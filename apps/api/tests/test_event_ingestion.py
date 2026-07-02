from datetime import UTC, datetime
from uuid import uuid4


def test_event_ingestion_accepts_valid_event_and_idempotency(client, api_headers):
    idempotency_key = f"pytest-{uuid4()}"
    anonymous_id = f"anon-{uuid4()}"
    payload = {
        "events": [
            {
                "event_name": "purchase",
                "timestamp": datetime.now(UTC).isoformat(),
                "anonymous_id": anonymous_id,
                "creative_treatment_id": "00000000-0000-0000-0000-000000000101",
                "value": 49.0,
                "currency": "USD",
                "properties": {"campaign": "spring-lift"},
            }
        ],
    }

    first = client.post(
        "/v1/events/ingest",
        headers={**api_headers, "Idempotency-Key": idempotency_key},
        json=payload,
    )
    assert first.status_code == 200
    first_body = first.json()
    assert first_body["accepted"] == 1

    second = client.post(
        "/v1/events/ingest",
        headers={**api_headers, "Idempotency-Key": idempotency_key},
        json=payload,
    )
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["accepted"] == 0
    assert second_body["deduplicated"] == 1

    listed = client.get("/v1/events?limit=50")
    assert listed.status_code == 200
    assert any(event["anonymous_id"] == anonymous_id for event in listed.json())

    health = client.get("/v1/events/health")
    assert health.status_code == 200
    health_body = health.json()
    assert health_body["total_events"] >= 1
    assert health_body["conversion_events"] >= 1
    assert health_body["event_counts"]["purchase"] >= 1


def test_event_ingestion_requires_user_or_anonymous_id(client, api_headers):
    response = client.post(
        "/v1/events/ingest",
        headers=api_headers,
        json={
            "events": [
                {
                    "event_name": "impression",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "creative_treatment_id": "00000000-0000-0000-0000-000000000101",
                }
            ],
        },
    )

    assert response.status_code == 422
