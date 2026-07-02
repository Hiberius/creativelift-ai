from __future__ import annotations

from typing import Any

import httpx


class CreativeLiftClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000") -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def ingest(self, events: list[dict[str, Any]], idempotency_key: str | None = None) -> dict[str, Any]:
        headers = {"X-API-Key": self.api_key}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        response = httpx.post(
            f"{self.base_url}/v1/events/ingest",
            headers=headers,
            json={"events": events},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def assign(self, experiment_id: str, unit_id: str) -> dict[str, Any]:
        response = httpx.get(
            f"{self.base_url}/v1/experiments/{experiment_id}/assign",
            headers={"X-API-Key": self.api_key},
            params={"unit_id": unit_id},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def event_health(self) -> dict[str, Any]:
        response = httpx.get(
            f"{self.base_url}/v1/events/health",
            headers={"X-API-Key": self.api_key},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def experiment_insight(self, experiment_id: str) -> dict[str, Any]:
        response = httpx.get(
            f"{self.base_url}/v1/experiments/{experiment_id}/insights",
            headers={"X-API-Key": self.api_key},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
