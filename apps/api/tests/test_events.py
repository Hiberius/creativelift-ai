from datetime import UTC, datetime
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas.common import EventIn


def test_event_requires_identity() -> None:
    with pytest.raises(ValidationError):
        EventIn(
            event_name="click",
            timestamp=datetime.now(UTC),
            creative_treatment_id=UUID("00000000-0000-0000-0000-000000000101"),
        )


def test_ingest_accepts_batch_and_deduplicates_idempotency_key() -> None:
    client = TestClient(app)
    payload = {
        "events": [
            {
                "event_name": "purchase",
                "timestamp": "2026-06-28T10:00:00Z",
                "anonymous_id": "anon_test",
                "creative_treatment_id": "00000000-0000-0000-0000-000000000101",
                "value": 99.0,
                "currency": "USD",
            }
        ]
    }
    first = client.post("/v1/events/ingest", json=payload, headers={"Idempotency-Key": "pytest-event-1"})
    second = client.post("/v1/events/ingest", json=payload, headers={"Idempotency-Key": "pytest-event-1"})
    assert first.status_code == 200
    assert first.json()["accepted"] == 1
    assert second.status_code == 200
    assert second.json()["deduplicated"] == 1
