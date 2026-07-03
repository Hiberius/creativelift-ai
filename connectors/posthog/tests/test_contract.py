import httpx
import pytest

from connectors.posthog.src.adapter import ConfigValidationError, PostHogAdapter


def test_posthog_normalize() -> None:
    normalized = PostHogAdapter().normalize({"uuid": "evt_1", "timestamp": "2026-06-28T00:00:00Z"})
    assert normalized["source"] == "posthog"


def test_posthog_validate_config_accepts_minimal_config() -> None:
    PostHogAdapter().validate_config({"project_api_key": "phc_test", "host": "https://app.posthog.com"})


def test_posthog_validate_config_rejects_missing_required_fields() -> None:
    with pytest.raises(ConfigValidationError):
        PostHogAdapter().validate_config({"project_api_key": "phc_test"})


def test_posthog_validate_config_rejects_unknown_fields() -> None:
    with pytest.raises(ConfigValidationError):
        PostHogAdapter().validate_config(
            {"project_api_key": "phc_test", "host": "https://app.posthog.com", "unexpected": "nope"}
        )


def test_posthog_pull_fetches_events_with_no_network_calls() -> None:
    """Exercises pull() end-to-end (auth header, pagination via `next`, max_events cap)
    against a mocked httpx transport only — no real network access.
    """

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer phc_test"
        if "cursor" not in str(request.url):
            return httpx.Response(
                200,
                json={
                    "results": [{"uuid": "e1", "event": "purchase", "timestamp": "2026-06-28T00:00:00Z"}],
                    "next": "https://app.posthog.com/api/projects/123/events?cursor=abc",
                },
            )
        return httpx.Response(
            200,
            json={"results": [{"uuid": "e2", "event": "click", "timestamp": "2026-06-28T00:01:00Z"}], "next": None},
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    config = {"project_api_key": "phc_test", "host": "https://app.posthog.com", "project_id": "123"}

    results = PostHogAdapter().pull(config, max_events=10, client=client)

    assert [item["uuid"] for item in results] == ["e1", "e2"]


def test_posthog_pull_respects_max_events_cap() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "results": [
                    {"uuid": "e1", "event": "purchase", "timestamp": "2026-06-28T00:00:00Z"},
                    {"uuid": "e2", "event": "click", "timestamp": "2026-06-28T00:01:00Z"},
                ],
                "next": "https://app.posthog.com/api/projects/123/events?cursor=abc",
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    config = {"project_api_key": "phc_test", "host": "https://app.posthog.com", "project_id": "123"}

    results = PostHogAdapter().pull(config, max_events=1, client=client)

    assert len(results) == 1
