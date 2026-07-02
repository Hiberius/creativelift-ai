"""Real API-key authentication: hashed lookup, revocation, scopes, production mode."""

import dataclasses

import pytest

import app.core.security as security
import app.main as main_module


def _create_key(client, scopes=None):
    payload = {"name": "auth-test-key"}
    if scopes is not None:
        payload["scopes"] = scopes
    response = client.post("/v1/api-keys", json=payload)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["raw_key"], "raw key must be returned exactly once at creation"
    return body


def _event_payload():
    from datetime import UTC, datetime
    from uuid import uuid4

    return {
        "events": [
            {
                "event_name": "purchase",
                "timestamp": datetime.now(UTC).isoformat(),
                "anonymous_id": "anon_auth",
                "creative_treatment_id": str(uuid4()),
                "value": 10.0,
                "currency": "USD",
            }
        ]
    }


def test_bearer_auth_resolves_real_key_to_its_organization(client):
    key = _create_key(client)

    me = client.get("/v1/me", headers={"Authorization": f"Bearer {key['raw_key']}"})
    assert me.status_code == 200, me.text
    body = me.json()
    assert body["principal"]["organization_id"] == key["organization_id"]

    listed = client.get("/v1/api-keys").json()
    assert all(item.get("raw_key") in (None, "") for item in listed), "raw keys must never be listed"


def test_x_api_key_accepts_real_key_on_measurement_routes(client):
    key = _create_key(client, scopes=["measurement:read"])
    response = client.get("/v1/measurement/summary", headers={"X-API-Key": key["raw_key"]})
    assert response.status_code == 200, response.text


def test_invalid_bearer_token_is_rejected(client):
    response = client.get("/v1/me", headers={"Authorization": "Bearer clai_not_a_real_key"})
    assert response.status_code == 401


def test_revoked_key_stops_working(client):
    key = _create_key(client)
    headers = {"Authorization": f"Bearer {key['raw_key']}"}
    assert client.get("/v1/me", headers=headers).status_code == 200

    deleted = client.delete(f"/v1/api-keys/{key['id']}")
    assert deleted.status_code in (200, 204), deleted.text

    assert client.get("/v1/me", headers=headers).status_code == 401


def test_ingest_requires_events_write_scope(client):
    read_only = _create_key(client, scopes=["measurement:read"])
    denied = client.post(
        "/v1/events/ingest",
        headers={"Authorization": f"Bearer {read_only['raw_key']}"},
        json=_event_payload(),
    )
    assert denied.status_code == 403, denied.text

    writer = _create_key(client, scopes=["events:write"])
    allowed = client.post(
        "/v1/events/ingest",
        headers={"Authorization": f"Bearer {writer['raw_key']}"},
        json=_event_payload(),
    )
    assert allowed.status_code == 200, allowed.text
    assert allowed.json()["accepted"] == 1


def test_production_mode_rejects_anonymous_and_demo_credentials(client, monkeypatch):
    production_settings = dataclasses.replace(security.settings, app_env="production")
    monkeypatch.setattr(security, "settings", production_settings)

    anonymous = client.get("/v1/me")
    assert anonymous.status_code == 401

    demo_bearer = client.get("/v1/me", headers={"Authorization": "Bearer dev-api-key"})
    assert demo_bearer.status_code == 401

    demo_key = client.get("/v1/measurement/summary", headers={"X-API-Key": "dev-api-key"})
    assert demo_key.status_code == 401


def test_real_keys_keep_working_in_production_mode(client, monkeypatch):
    key = _create_key(client)
    production_settings = dataclasses.replace(security.settings, app_env="production")
    monkeypatch.setattr(security, "settings", production_settings)

    me = client.get("/v1/me", headers={"Authorization": f"Bearer {key['raw_key']}"})
    assert me.status_code == 200


def test_boot_refuses_production_with_dev_pepper(monkeypatch):
    production_settings = dataclasses.replace(security.settings, app_env="production")
    monkeypatch.setattr(security, "settings", production_settings)
    monkeypatch.setattr(main_module, "settings", production_settings)

    with pytest.raises(RuntimeError, match="API_KEY_PEPPER"):
        main_module.create_app()


def test_security_headers_present(client):
    response = client.get("/healthz")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"

    demo = client.get("/demo")
    assert "content-security-policy" in demo.headers
