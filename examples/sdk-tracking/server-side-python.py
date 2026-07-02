from __future__ import annotations

from datetime import UTC, datetime
from os import getenv

from creativelift.client import CreativeLiftClient


client = CreativeLiftClient(
    api_key=getenv("CREATIVELIFT_API_KEY", "dev-api-key"),
    base_url=getenv("CREATIVELIFT_API_URL", "http://localhost:8000"),
)


def track_signup(
    *,
    experiment_id: str,
    variant_key: str,
    creative_treatment_id: str,
    anonymous_id: str,
    value: float = 0.0,
) -> dict:
    return client.ingest(
        [
            {
                "event_name": "signup",
                "timestamp": datetime.now(UTC).isoformat(),
                "anonymous_id": anonymous_id,
                "experiment_id": experiment_id,
                "variant_id": variant_key,
                "creative_treatment_id": creative_treatment_id,
                "channel": "landing_page",
                "placement": "signup_form",
                "value": value,
                "currency": "USD",
                "properties": {"source": "server_side_example"},
            }
        ],
        idempotency_key=f"signup_{anonymous_id}_{experiment_id}",
    )


def read_event_health() -> dict:
    return client.event_health()


if __name__ == "__main__":
    print(read_event_health())
