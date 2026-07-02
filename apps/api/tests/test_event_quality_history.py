"""Event quality history endpoint behavior on the default memory backend."""

from datetime import UTC, datetime
from uuid import uuid4


def _event_payload(actor: str, name: str = "purchase", value: float | None = 10.0) -> dict:
    payload = {
        "event_name": name,
        "timestamp": datetime.now(UTC).isoformat(),
        "anonymous_id": actor,
        "creative_treatment_id": str(uuid4()),
        "channel": "paid_social",
    }
    if value is not None:
        payload["value"] = value
        payload["currency"] = "USD"
    return payload


def test_ingest_records_quality_snapshots_in_history(client):
    first = client.post(
        "/v1/events/ingest",
        headers={"Idempotency-Key": f"evt_history_{uuid4().hex[:8]}"},
        json={"events": [_event_payload("anon_1")]},
    )
    assert first.status_code == 200
    assert first.json()["accepted"] == 1

    history = client.get("/v1/events/health/history")
    assert history.status_code == 200
    snapshots = history.json()
    assert len(snapshots) >= 1
    latest = snapshots[0]
    assert latest["total_events"] >= 1
    assert 0.0 <= latest["quality_score"] <= 1.0

    second = client.post(
        "/v1/events/ingest",
        headers={"Idempotency-Key": f"evt_history_{uuid4().hex[:8]}"},
        json={"events": [_event_payload("anon_2"), _event_payload("anon_3")]},
    )
    assert second.status_code == 200

    history = client.get("/v1/events/health/history").json()
    assert len(history) >= 2
    assert history[0]["total_events"] > history[1]["total_events"]
    captured = [snapshot["captured_at"] for snapshot in history]
    assert captured == sorted(captured, reverse=True)


def test_deduplicated_ingest_does_not_add_snapshot(client):
    idempotency_key = f"evt_dedup_{uuid4().hex[:8]}"
    payload = {"events": [_event_payload("anon_dedup")]}

    client.post("/v1/events/ingest", headers={"Idempotency-Key": idempotency_key}, json=payload)
    before = len(client.get("/v1/events/health/history").json())

    replay = client.post(
        "/v1/events/ingest", headers={"Idempotency-Key": idempotency_key}, json=payload
    )
    assert replay.json()["deduplicated"] == 1
    after = len(client.get("/v1/events/health/history").json())
    assert after == before


def test_history_respects_limit_query(client):
    for _ in range(3):
        client.post(
            "/v1/events/ingest",
            headers={"Idempotency-Key": f"evt_limit_{uuid4().hex[:8]}"},
            json={"events": [_event_payload(f"anon_{uuid4().hex[:6]}")]},
        )
    limited = client.get("/v1/events/health/history", params={"limit": 2})
    assert limited.status_code == 200
    assert len(limited.json()) == 2
