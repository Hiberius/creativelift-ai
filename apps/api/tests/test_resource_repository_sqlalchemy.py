"""Functional tests for SQLAlchemyResourceRepository on in-memory SQLite."""

from uuid import uuid4

import pytest

pytestmark = pytest.mark.sqlalchemy


@pytest.fixture
def sqlite_resource_repository():
    pytest.importorskip("sqlalchemy")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from app.db.models import Base
    from app.services.repositories import SQLAlchemyResourceRepository

    engine = create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    return SQLAlchemyResourceRepository(sessionmaker(bind=engine))


def test_connector_create_list_get_with_tenancy(sqlite_resource_repository):
    repository = sqlite_resource_repository
    organization_id = uuid4()
    other_organization_id = uuid4()

    created = repository.create(
        "connectors",
        {"provider": "posthog", "display_name": "PostHog", "status": "disconnected", "config": {}},
        organization_id,
    )
    assert created["organization_id"] == organization_id
    assert created["provider"] == "posthog"

    page = repository.list("connectors", organization_id)
    assert page.total == 1
    assert page.items[0]["id"] == created["id"]

    assert repository.list("connectors", other_organization_id).total == 0
    assert repository.get("connectors", created["id"], organization_id) is not None
    assert repository.get("connectors", created["id"], other_organization_id) is None


def test_prompt_run_and_measurement_runs_roundtrip(sqlite_resource_repository):
    repository = sqlite_resource_repository
    organization_id = uuid4()

    prompt_run = repository.create(
        "prompt_runs",
        {
            "provider": "mock",
            "model": "mock-large",
            "prompt": "write a hook",
            "variables": {"angle": "speed"},
            "response": {"text": "Ship faster."},
            "status": "succeeded",
            "input_tokens": 12,
            "output_tokens": 40,
        },
        organization_id,
    )
    assert prompt_run["variables"] == {"angle": "speed"}

    mmm_run = repository.create(
        "mmm_runs",
        {"name": "Q3 MMM", "status": "queued", "inputs": {}, "outputs": {}},
        organization_id,
    )
    uplift_run = repository.create(
        "uplift_runs",
        {"name": "Churn uplift", "status": "queued", "inputs": {}, "outputs": {}},
        organization_id,
    )

    for resource, created in (
        ("prompt_runs", prompt_run),
        ("mmm_runs", mmm_run),
        ("uplift_runs", uplift_run),
    ):
        page = repository.list(resource, organization_id)
        assert page.total == 1
        assert page.items[0]["id"] == created["id"]


def test_list_pagination_returns_total(sqlite_resource_repository):
    repository = sqlite_resource_repository
    organization_id = uuid4()

    for index in range(3):
        repository.create(
            "connectors",
            {"provider": f"provider-{index}", "display_name": f"Provider {index}", "config": {}},
            organization_id,
        )

    page = repository.list("connectors", organization_id, limit=2, offset=0)
    assert page.total == 3
    assert len(page.items) == 2
    tail = repository.list("connectors", organization_id, limit=2, offset=2)
    assert tail.total == 3
    assert len(tail.items) == 1
