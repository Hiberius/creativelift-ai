"""Behavioral parity tests for InMemory and SQLAlchemy core repositories.

The memory variant always runs; the sqlalchemy variant runs on an in-memory
SQLite database and is skipped when sqlalchemy is not installed, so the
no-dependency quickstart stays intact.
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.schemas.common import (
    ApiKeyCreate,
    ApprovalStatus,
    BrandPackCreate,
    BriefCreate,
    CreativeTreatmentCreate,
    EventIn,
    ExperimentCreate,
    ExperimentStatus,
    ExperimentVariantInput,
    OrganizationCreate,
)


def _memory_repository():
    from app.services.core_repositories import InMemoryCoreRepository
    from app.services.demo_store import DemoStore

    return InMemoryCoreRepository(DemoStore())


def _sqlite_repository():
    pytest.importorskip("sqlalchemy")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from app.db.models import Base
    from app.services.core_repositories import SQLAlchemyCoreRepository

    engine = create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    return SQLAlchemyCoreRepository(sessionmaker(bind=engine))


@pytest.fixture(params=["memory", pytest.param("sqlalchemy", marks=pytest.mark.sqlalchemy)])
def any_core_repository(request):
    if request.param == "memory":
        return _memory_repository()
    return _sqlite_repository()


def _create_organization(repository, slug_suffix: str = "a"):
    return repository.create_organization(
        OrganizationCreate(name="Parity Org", slug=f"parity-org-{slug_suffix}")
    )


def _event(creative_id, experiment_id=None, variant_id=None, name="purchase", value=None, actor="anon_1"):
    return EventIn(
        event_name=name,
        timestamp=datetime.now(UTC),
        anonymous_id=actor,
        creative_treatment_id=creative_id,
        experiment_id=experiment_id,
        variant_id=variant_id,
        channel="paid_social",
        value=value,
        currency="USD" if value is not None else None,
    )


def test_core_entities_roundtrip_scoped_by_organization(any_core_repository):
    repository = any_core_repository
    organization = _create_organization(repository)

    brand_pack = repository.create_brand_pack(
        BrandPackCreate(name="Parity Pack", voice="direct"), organization.id
    )
    assert brand_pack.organization_id == organization.id

    brief = repository.create_brief(
        BriefCreate(
            name="Parity Brief",
            objective="conversion",
            target_audience="smb founders",
            channel="email",
            primary_kpi="signup_rate",
            brand_pack_id=brand_pack.id,
        ),
        organization.id,
    )
    assert brief.organization_id == organization.id

    creative = repository.create_creative_treatment(
        CreativeTreatmentCreate(
            name="Parity Creative",
            objective="conversion",
            target_audience="smb founders",
            channel="email",
            brief_id=brief.id,
            brand_pack_id=brand_pack.id,
        ),
        organization.id,
    )
    assert creative.organization_id == organization.id

    approved = repository.update_creative_treatment(
        creative.model_copy(update={"approval_status": ApprovalStatus.approved}),
        organization.id,
    )
    assert approved is not None
    assert approved.approval_status == ApprovalStatus.approved

    scoped = repository.list_creative_treatments(organization.id)
    assert [item.id for item in scoped] == [creative.id]

    other_org = _create_organization(repository, slug_suffix="b")
    assert repository.list_creative_treatments(other_org.id) == []
    assert repository.get_creative_treatment(creative.id, other_org.id) is None


def test_latest_organization_id_tracks_most_recent(any_core_repository):
    repository = any_core_repository
    first = _create_organization(repository, slug_suffix="first")
    assert repository.latest_organization_id() == first.id
    second = _create_organization(repository, slug_suffix="second")
    assert repository.latest_organization_id() == second.id


def test_event_ingest_idempotency_parity(any_core_repository):
    repository = any_core_repository
    organization = _create_organization(repository)
    other_org = _create_organization(repository, slug_suffix="b")
    creative_id = uuid4()

    events = [_event(creative_id), _event(creative_id, actor="anon_2")]
    assert repository.ingest_events(events, organization.id, "evt_batch_1") == (2, 0)
    assert repository.ingest_events(events, organization.id, "evt_batch_1") == (0, 2)
    assert repository.ingest_events(events, other_org.id, "evt_batch_1") == (2, 0)

    assert len(repository.list_events(organization.id, limit=None)) == 2


def test_api_key_hashing_parity(any_core_repository):
    repository = any_core_repository
    organization = _create_organization(repository)

    api_key = repository.create_api_key(ApiKeyCreate(name="parity-key"), organization.id)
    assert api_key.raw_key
    assert api_key.raw_key.startswith("clai_")
    assert api_key.prefix == api_key.raw_key[:12]

    listed = repository.list_api_keys(organization.id)
    assert [item.id for item in listed] == [api_key.id]

    if hasattr(repository, "session_factory"):
        from sqlalchemy import select

        from app.db.models import ApiKey

        with repository.session_factory() as session:
            stored = session.scalars(select(ApiKey).where(ApiKey.id == api_key.id)).one()
        assert stored.hashed_key
        assert stored.hashed_key != api_key.raw_key
        assert api_key.raw_key not in stored.hashed_key


def test_event_quality_snapshot_roundtrip(any_core_repository):
    repository = any_core_repository
    organization = _create_organization(repository)
    other_org = _create_organization(repository, slug_suffix="b")

    first = repository.record_event_quality_snapshot(
        {"total_events": 1, "quality_score": 0.5, "warnings": ["low coverage"]},
        organization.id,
    )
    second = repository.record_event_quality_snapshot(
        {"total_events": 3, "quality_score": 0.75, "revenue": 42.5},
        organization.id,
    )

    snapshots = repository.list_event_quality_snapshots(organization.id)
    assert [item.id for item in snapshots] == [second.id, first.id]
    assert snapshots[0].total_events == 3
    assert snapshots[0].revenue == pytest.approx(42.5)
    assert snapshots[1].warnings == ["low coverage"]

    assert repository.list_event_quality_snapshots(other_org.id) == []
    assert len(repository.list_event_quality_snapshots(organization.id, limit=1)) == 1


def test_measurement_summary_stats_parity(any_core_repository):
    repository = any_core_repository
    organization = _create_organization(repository)
    creative_id = uuid4()

    events = [
        _event(creative_id, name="impression", actor="anon_1"),
        _event(creative_id, name="purchase", value=100.0, actor="anon_1"),
        _event(creative_id, name="purchase", value=50.0, actor="anon_2"),
    ]
    assert repository.ingest_events(events, organization.id, "evt_stats_1") == (3, 0)

    experiment = repository.create_experiment(
        ExperimentCreate(
            name="Parity Experiment",
            hypothesis="treatment wins",
            primary_metric="conversion_rate",
            variants=[
                ExperimentVariantInput(key="control", allocation=0.5, is_control=True),
                ExperimentVariantInput(key="treatment", allocation=0.5),
            ],
        ),
        organization.id,
    )
    repository.update_experiment(
        experiment.model_copy(update={"status": ExperimentStatus.running}),
        organization.id,
    )

    stats = repository.measurement_summary_stats(organization.id)
    assert stats.total_events == 3
    assert stats.conversion_events == 2
    assert stats.unique_actors == 2
    assert stats.revenue == pytest.approx(150.0)
    assert stats.last_event_at is not None
    assert stats.running_experiments == 1

    future = datetime.now(UTC) + timedelta(days=1)
    empty_window = repository.measurement_summary_stats(organization.id, since=future)
    assert empty_window.total_events == 0
    assert empty_window.conversion_events == 0
    assert empty_window.revenue == pytest.approx(0.0)
    # Non-event counters are window-independent.
    assert empty_window.running_experiments == 1
