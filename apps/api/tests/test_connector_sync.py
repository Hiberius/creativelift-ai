"""Coverage for the connector sync endpoint (POST /v1/connectors/{id}/sync)
and the connector adapter loader/event-mapping helpers behind it.
"""

from __future__ import annotations

from datetime import UTC, datetime

import httpx
import pytest

from app.services import connector_sync


def _create_connector(client, api_headers, provider="webhook-generic", display_name="My Webhook"):
    response = client.post(
        "/v1/connectors",
        headers=api_headers,
        json={"provider": provider, "display_name": display_name, "config": {}},
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]


def _webhook_event(event_type: str, ts: str | None = None) -> dict:
    return {
        "id": f"evt-{event_type}",
        "type": event_type,
        "ts": ts or datetime.now(UTC).isoformat(),
        "anonymous_id": "anon-connector-1",
    }


def test_sync_push_ingests_webhook_events(client, api_headers):
    connector = _create_connector(client, api_headers)

    response = client.post(
        f"/v1/connectors/{connector['id']}/sync",
        headers=api_headers,
        json={
            "mapping": {"event_name_path": "type", "timestamp_path": "ts"},
            "events": [_webhook_event("purchase"), _webhook_event("click")],
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()["data"]
    assert body["accepted"] == 2
    assert body["deduplicated"] == 0
    assert body["provider"] == "webhook-generic"
    assert body["mode"] == "push"

    updated = client.get("/v1/connectors", headers=api_headers).json()["data"]
    synced = next(item for item in updated if item["id"] == connector["id"])
    assert synced["status"] == "connected"
    assert synced["last_sync_at"] is not None


def test_sync_push_replay_deduplicates(client, api_headers):
    connector = _create_connector(client, api_headers)
    body = {
        "mapping": {"event_name_path": "type", "timestamp_path": "ts"},
        "events": [_webhook_event("purchase", ts="2026-06-28T00:00:00Z")],
    }

    first = client.post(f"/v1/connectors/{connector['id']}/sync", headers=api_headers, json=body)
    assert first.status_code == 200, first.text
    assert first.json()["data"]["accepted"] == 1

    second = client.post(f"/v1/connectors/{connector['id']}/sync", headers=api_headers, json=body)
    assert second.status_code == 200, second.text
    second_data = second.json()["data"]
    assert second_data["accepted"] == 0
    assert second_data["deduplicated"] == 1


def test_sync_unknown_connector_returns_404(client, api_headers):
    response = client.post(
        "/v1/connectors/00000000-0000-0000-0000-000000000999/sync",
        headers=api_headers,
        json={"events": [_webhook_event("purchase")]},
    )
    assert response.status_code == 404


def test_sync_invalid_connector_id_returns_400(client, api_headers):
    response = client.post(
        "/v1/connectors/not-a-uuid/sync",
        headers=api_headers,
        json={"events": [_webhook_event("purchase")]},
    )
    assert response.status_code == 400


def test_sync_requires_events_write_scope(client):
    create_response = client.post(
        "/v1/api-keys",
        json={"name": "connector-sync-reader", "scopes": ["measurement:read"]},
    )
    assert create_response.status_code == 200, create_response.text
    reader_key = create_response.json()["raw_key"]

    writer_headers = {"X-API-Key": "dev-api-key"}
    connector = _create_connector(client, writer_headers)

    response = client.post(
        f"/v1/connectors/{connector['id']}/sync",
        headers={"X-API-Key": reader_key},
        json={"events": [_webhook_event("purchase")]},
    )
    assert response.status_code == 403


def test_sync_pull_mode_fetches_and_ingests_posthog_events(client, api_headers, monkeypatch):
    connector_response = client.post(
        "/v1/connectors",
        headers=api_headers,
        json={
            "provider": "posthog",
            "display_name": "PostHog Prod",
            "config": {
                "project_api_key": "phc_test_key",
                "host": "https://app.posthog.com",
                "project_id": "123",
            },
        },
    )
    assert connector_response.status_code == 201, connector_response.text
    connector = connector_response.json()["data"]

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer phc_test_key"
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "uuid": "posthog-evt-1",
                        "event": "purchase",
                        "timestamp": "2026-06-28T00:00:00Z",
                        "distinct_id": "user-42",
                    }
                ],
                "next": None,
            },
        )

    original_client = httpx.Client

    def fake_client(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", fake_client)

    response = client.post(
        f"/v1/connectors/{connector['id']}/sync",
        headers=api_headers,
        json={},
    )
    assert response.status_code == 200, response.text
    body = response.json()["data"]
    assert body["mode"] == "pull"
    assert body["provider"] == "posthog"
    assert body["accepted"] == 1


def test_sync_unknown_provider_returns_4xx(client, api_headers):
    connector = _create_connector(client, api_headers, provider="does-not-exist", display_name="Bogus")

    response = client.post(
        f"/v1/connectors/{connector['id']}/sync",
        headers=api_headers,
        json={"events": [_webhook_event("purchase")]},
    )
    assert 400 <= response.status_code < 500


def test_normalized_records_to_events_falls_back_to_external_id_identity():
    from uuid import uuid4

    record = {
        "source": "webhook_generic",
        "record_type": "event",
        "external_id": "evt-no-identity",
        "occurred_at": "2026-06-28T00:00:00Z",
        "payload": {"event_name": "purchase", "anonymous_id": None, "user_id": None, "properties": {}},
    }
    batch = connector_sync.normalized_records_to_events([record], uuid4())
    assert batch.skipped == 0
    assert len(batch.events) == 1
    assert batch.events[0].anonymous_id == "webhook_generic:evt-no-identity"


def test_normalized_records_to_events_skips_records_without_any_identity():
    from uuid import uuid4

    record = {
        "source": "webhook_generic",
        "record_type": "event",
        "external_id": None,
        "occurred_at": "2026-06-28T00:00:00Z",
        "payload": {"event_name": "purchase", "anonymous_id": None, "user_id": None, "properties": {}},
    }
    batch = connector_sync.normalized_records_to_events([record], uuid4())
    assert batch.skipped == 1
    assert len(batch.events) == 0


def test_load_adapter_raises_for_unknown_provider():
    with pytest.raises(connector_sync.ConnectorSyncError):
        connector_sync.load_adapter("totally-unknown-provider")


@pytest.mark.parametrize(
    "provider",
    ["google-ads", "meta-ads", "hubspot", "posthog", "rudder", "snowplow", "webhook-generic"],
)
def test_load_adapter_loads_every_known_provider(provider):
    mapping = {"event_name_path": "type", "timestamp_path": "ts"} if provider == "webhook-generic" else None
    adapter = connector_sync.load_adapter(provider, mapping=mapping)
    assert hasattr(adapter, "normalize")
    assert hasattr(adapter, "validate_config")
