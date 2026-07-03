from __future__ import annotations

from collections import Counter
from typing import Any
from uuid import UUID

from app.services.measurement import CONVERSION_EVENT_NAMES


def capture_event_quality_snapshot(repository: Any, organization_id: UUID) -> Any:
    """Compute the current event health and persist it as a trend snapshot.

    Uses the repository's aggregate rollup (a handful of SQL aggregates on
    the persistent backend) instead of loading every event into memory.
    """
    summary = repository.compute_event_health(organization_id)
    return repository.record_event_quality_snapshot(summary, organization_id)


def _event_name_value(event_name: Any) -> str:
    return str(getattr(event_name, "value", event_name))


def event_health_summary(events: list[Any]) -> dict:
    total_events = len(events)
    if total_events == 0:
        return {
            "total_events": 0,
            "unique_actors": 0,
            "events_with_experiment": 0,
            "events_with_variant": 0,
            "conversion_events": 0,
            "revenue": 0.0,
            "last_event_at": None,
            "event_counts": {},
            "channel_counts": {},
            "experiment_coverage": 0.0,
            "variant_coverage": 0.0,
            "revenue_coverage": 0.0,
            "quality_score": 0.0,
            "warnings": ["No events have been ingested yet."],
        }

    event_counts: Counter[str] = Counter()
    channel_counts: Counter[str] = Counter()
    actors: set[str] = set()
    events_with_identity = 0
    events_with_experiment = 0
    events_with_variant = 0
    conversion_events = 0
    valued_conversion_events = 0
    revenue = 0.0

    for event in events:
        event_name = _event_name_value(event.event_name)
        event_counts[event_name] += 1
        channel_counts[event.channel or "unknown"] += 1
        actor = event.user_id or event.anonymous_id
        if actor:
            events_with_identity += 1
            actors.add(str(actor))
        if event.experiment_id:
            events_with_experiment += 1
        if event.variant_id:
            events_with_variant += 1
        if event_name in CONVERSION_EVENT_NAMES:
            conversion_events += 1
            if event.value is not None:
                valued_conversion_events += 1
                revenue += float(event.value)

    return summarize_event_aggregates(
        total_events=total_events,
        unique_actors=len(actors),
        events_with_identity=events_with_identity,
        events_with_experiment=events_with_experiment,
        events_with_variant=events_with_variant,
        conversion_events=conversion_events,
        valued_conversion_events=valued_conversion_events,
        revenue=revenue,
        last_event_at=max(event.timestamp for event in events),
        event_counts=dict(event_counts),
        channel_counts=dict(channel_counts),
    )


def summarize_event_aggregates(
    *,
    total_events: int,
    unique_actors: int,
    events_with_identity: int,
    events_with_experiment: int,
    events_with_variant: int,
    conversion_events: int,
    valued_conversion_events: int,
    revenue: float,
    last_event_at: Any,
    event_counts: dict[str, int] | None = None,
    channel_counts: dict[str, int] | None = None,
) -> dict:
    """Shared health math for both the in-memory path and the SQL rollup."""
    experiment_coverage = events_with_experiment / total_events
    variant_coverage = events_with_variant / total_events
    revenue_coverage = valued_conversion_events / conversion_events if conversion_events else 1.0
    identity_coverage = events_with_identity / total_events
    quality_score = round(
        (identity_coverage + experiment_coverage + variant_coverage + revenue_coverage) / 4,
        3,
    )
    warnings: list[str] = []
    if experiment_coverage < 0.8:
        warnings.append("Most events are not attached to experiments.")
    if variant_coverage < 0.8:
        warnings.append("Most events are missing variant IDs.")
    if conversion_events and revenue_coverage < 0.5:
        warnings.append("Most conversion events do not carry revenue value.")

    return {
        "total_events": total_events,
        "unique_actors": unique_actors,
        "events_with_experiment": events_with_experiment,
        "events_with_variant": events_with_variant,
        "conversion_events": conversion_events,
        "revenue": revenue,
        "last_event_at": last_event_at,
        "event_counts": event_counts or {},
        "channel_counts": channel_counts or {},
        "experiment_coverage": experiment_coverage,
        "variant_coverage": variant_coverage,
        "revenue_coverage": revenue_coverage,
        "quality_score": quality_score,
        "warnings": warnings,
    }
