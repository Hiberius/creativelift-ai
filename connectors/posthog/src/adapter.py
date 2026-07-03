from __future__ import annotations

from typing import Any

import httpx

DEFAULT_MAX_EVENTS = 100
DEFAULT_TIMEOUT_SECONDS = 10.0


class ConfigValidationError(ValueError):
    """Raised when a connector configuration fails schema validation."""


class PostHogAdapter:
    source = "posthog"

    def validate_config(self, config: dict) -> None:
        if not isinstance(config, dict):
            raise ConfigValidationError("config must be an object")
        project_api_key = config.get("project_api_key")
        if not isinstance(project_api_key, str) or not project_api_key.strip():
            raise ConfigValidationError("config.project_api_key is required and must be a non-empty string")
        host = config.get("host")
        if not isinstance(host, str) or not host.strip():
            raise ConfigValidationError("config.host is required and must be a non-empty string")
        project_id = config.get("project_id")
        if project_id is not None and not isinstance(project_id, str):
            raise ConfigValidationError("config.project_id must be a string when present")
        event_names = config.get("event_names")
        if event_names is not None:
            if not isinstance(event_names, list) or not all(isinstance(item, str) for item in event_names):
                raise ConfigValidationError("config.event_names must be an array of strings when present")
        allowed_fields = {"host", "project_api_key", "project_id", "event_names"}
        unknown_fields = set(config) - allowed_fields
        if unknown_fields:
            raise ConfigValidationError(f"config has unknown fields: {sorted(unknown_fields)}")

    def pull(
        self,
        config: dict,
        since: str | None = None,
        max_events: int = DEFAULT_MAX_EVENTS,
        client: httpx.Client | None = None,
    ) -> list[dict]:
        """Fetch raw events from the PostHog Events API.

        Uses the ``/api/projects/{project_id}/events`` endpoint (PostHog's REST API,
        authenticated with a personal/project API key as a bearer token) and follows
        the ``next`` pagination cursor until ``max_events`` is reached or the API
        stops returning a next page. See https://posthog.com/docs/api/events.
        """
        self.validate_config(config)
        host = (config.get("host") or "https://app.posthog.com").rstrip("/")
        project_id = config.get("project_id")
        if not project_id:
            raise ConfigValidationError("config.project_id is required to pull events")
        api_key = config["project_api_key"]
        event_names = config.get("event_names")

        headers = {"Authorization": f"Bearer {api_key}"}
        params: dict[str, Any] = {"limit": min(max_events, DEFAULT_MAX_EVENTS)}
        if since:
            params["after"] = since
        if event_names:
            params["event"] = event_names[0] if len(event_names) == 1 else event_names

        owns_client = client is None
        http_client = client or httpx.Client(timeout=DEFAULT_TIMEOUT_SECONDS)
        collected: list[dict] = []
        try:
            url = f"{host}/api/projects/{project_id}/events"
            request_params: dict[str, Any] | None = params
            while url and len(collected) < max_events:
                response = http_client.get(url, headers=headers, params=request_params)
                response.raise_for_status()
                body = response.json()
                results = body.get("results", [])
                remaining = max_events - len(collected)
                collected.extend(results[:remaining])
                url = body.get("next")
                request_params = None  # `next` is already a fully-qualified URL with query params
        finally:
            if owns_client:
                http_client.close()
        return collected

    def normalize(self, raw: dict) -> dict:
        return {
            "source": self.source,
            "record_type": "event",
            "external_id": raw.get("uuid") or raw.get("event"),
            "occurred_at": raw.get("timestamp"),
            "payload": raw,
        }
