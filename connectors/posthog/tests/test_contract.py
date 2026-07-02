from connectors.posthog.src.adapter import PostHogAdapter


def test_posthog_normalize() -> None:
    normalized = PostHogAdapter().normalize({"uuid": "evt_1", "timestamp": "2026-06-28T00:00:00Z"})
    assert normalized["source"] == "posthog"
