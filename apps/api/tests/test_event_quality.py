from datetime import UTC, datetime
from types import SimpleNamespace

from app.services.event_quality import event_health_summary


def test_event_health_summary_scores_coverage_and_revenue() -> None:
    events = [
        SimpleNamespace(
            event_name="impression",
            timestamp=datetime(2026, 6, 28, 10, 0, tzinfo=UTC),
            anonymous_id="anon-1",
            user_id=None,
            experiment_id="00000000-0000-0000-0000-000000000201",
            variant_id="control",
            channel="paid_social",
            value=None,
        ),
        SimpleNamespace(
            event_name="purchase",
            timestamp=datetime(2026, 6, 28, 10, 1, tzinfo=UTC),
            anonymous_id="anon-1",
            user_id=None,
            experiment_id="00000000-0000-0000-0000-000000000201",
            variant_id="control",
            channel="paid_social",
            value=49.0,
        ),
    ]

    summary = event_health_summary(events)

    assert summary["total_events"] == 2
    assert summary["unique_actors"] == 1
    assert summary["events_with_experiment"] == 2
    assert summary["events_with_variant"] == 2
    assert summary["conversion_events"] == 1
    assert summary["revenue"] == 49.0
    assert summary["event_counts"] == {"impression": 1, "purchase": 1}
    assert summary["channel_counts"] == {"paid_social": 2}
    assert summary["quality_score"] == 1.0
    assert summary["warnings"] == []


def test_event_health_summary_empty_state() -> None:
    summary = event_health_summary([])

    assert summary["total_events"] == 0
    assert summary["quality_score"] == 0.0
    assert summary["warnings"]
