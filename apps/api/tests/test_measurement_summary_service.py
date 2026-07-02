"""MeasurementService.summary: demo fallback vs repository-computed cards."""

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.schemas.common import EventIn, OrganizationCreate
from app.services.core_repositories import InMemoryCoreRepository
from app.services.demo_store import DemoStore
from app.services.measurement import MeasurementService

EXPECTED_METRICS = {"impressions", "conversion_rate", "incremental_lift", "creative_fatigue_index"}


@pytest.fixture
def repository():
    return InMemoryCoreRepository(DemoStore())


@pytest.fixture
def organization(repository):
    return repository.create_organization(OrganizationCreate(name="Summary Co", slug="summary-co"))


def _event(name: str, actor: str, value: float | None = None) -> EventIn:
    return EventIn(
        event_name=name,
        timestamp=datetime.now(UTC),
        anonymous_id=actor,
        creative_treatment_id=uuid4(),
        channel="paid_social",
        value=value,
        currency="USD" if value is not None else None,
    )


def test_summary_without_events_returns_demo_cards(repository, organization):
    service = MeasurementService(repository)

    summary = asyncio.run(service.summary(organization.id))

    assert summary.window == "last_7_days"
    assert {card.metric for card in summary.cards} == EXPECTED_METRICS
    cards = {card.metric: card for card in summary.cards}
    assert cards["impressions"].value == 128_420
    assert cards["conversion_rate"].value == pytest.approx(0.043)
    assert any("Demo values" in note for note in summary.notes)


def test_summary_with_events_computes_cards_with_same_shape(repository, organization):
    service = MeasurementService(repository)
    events = [
        _event("impression", "anon_1"),
        _event("impression", "anon_2"),
        _event("purchase", "anon_1", value=80.0),
    ]
    assert repository.ingest_events(events, organization.id, "evt_summary_1") == (3, 0)

    summary = asyncio.run(service.summary(organization.id))

    assert {card.metric for card in summary.cards} == EXPECTED_METRICS
    cards = {card.metric: card for card in summary.cards}
    assert cards["impressions"].value == 3
    assert cards["conversion_rate"].value == pytest.approx(0.5)
    assert cards["conversion_rate"].unit == "ratio"
    assert cards["incremental_lift"].unit == "ratio"
    assert any("Computed from 3 repository events" in note for note in summary.notes)


def test_summary_window_filters_events(repository, organization):
    service = MeasurementService(repository)
    old_event = _event("purchase", "anon_old", value=10.0).model_copy(
        update={"timestamp": datetime(2020, 1, 1, tzinfo=UTC)}
    )
    repository.ingest_events([old_event], organization.id, "evt_summary_old")

    summary = asyncio.run(service.summary(organization.id, window="last_7_days"))

    # The only event is outside the window, so the demo fallback is served.
    cards = {card.metric: card for card in summary.cards}
    assert cards["impressions"].value == 128_420
