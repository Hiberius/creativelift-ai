"""End-to-end API workflow against the SQLAlchemy backend on SQLite.

Swaps the CoreRepositoryProxy delegate and the resource service repository,
runs the product workflow through the real FastAPI routes, then restores the
default memory backend.
"""

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.sqlalchemy


@pytest.fixture
def sqlalchemy_client():
    pytest.importorskip("sqlalchemy")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from app.core.security import reset_demo_organization_id
    from app.db.models import Base
    from app.main import create_app
    from app.services.core_repositories import SQLAlchemyCoreRepository, core_repository
    from app.services.repositories import SQLAlchemyResourceRepository, create_resource_repository
    from app.services.resources import resource_service

    engine = create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    previous_resource_repository = resource_service.repository
    core_repository.use(SQLAlchemyCoreRepository(factory))
    resource_service.repository = SQLAlchemyResourceRepository(factory)
    reset_demo_organization_id()
    try:
        with TestClient(create_app()) as client:
            yield client
    finally:
        core_repository.reset()
        resource_service.repository = previous_resource_repository or create_resource_repository()
        reset_demo_organization_id()


def _event_payload(creative_id: str, actor: str, name: str, value: float | None = None) -> dict:
    payload = {
        "event_name": name,
        "timestamp": datetime.now(UTC).isoformat(),
        "anonymous_id": actor,
        "creative_treatment_id": creative_id,
        "channel": "paid_social",
    }
    if value is not None:
        payload["value"] = value
        payload["currency"] = "USD"
    return payload


def test_product_workflow_persists_through_sqlalchemy_backend(sqlalchemy_client):
    client = sqlalchemy_client

    organization = client.post(
        "/v1/organizations", json={"name": "Persist Co", "slug": "persist-co"}
    )
    assert organization.status_code == 200, organization.text
    organization_id = organization.json()["id"]

    brand_pack = client.post("/v1/brand-packs", json={"name": "Persist Pack", "voice": "direct"})
    assert brand_pack.status_code == 200, brand_pack.text

    creative = client.post(
        "/v1/creative-treatments",
        json={
            "name": "Persist Creative",
            "objective": "conversion",
            "target_audience": "founders",
            "channel": "paid_social",
        },
    )
    assert creative.status_code == 200, creative.text
    creative_id = creative.json()["id"]

    approved = client.post(
        f"/v1/creative-treatments/{creative_id}/approve",
        json={"notes": "ship it"},
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["approval_status"] == "approved"

    ingest = client.post(
        "/v1/events/ingest",
        headers={"Idempotency-Key": "evt_sqla_1"},
        json={
            "events": [
                _event_payload(creative_id, "anon_1", "impression"),
                _event_payload(creative_id, "anon_1", "purchase", value=99.0),
            ]
        },
    )
    assert ingest.status_code == 200, ingest.text
    assert ingest.json()["accepted"] == 2

    replay = client.post(
        "/v1/events/ingest",
        headers={"Idempotency-Key": "evt_sqla_1"},
        json={"events": [_event_payload(creative_id, "anon_1", "impression")]},
    )
    assert replay.status_code == 200
    assert replay.json()["deduplicated"] == 1

    health = client.get("/v1/events/health")
    assert health.status_code == 200
    assert health.json()["total_events"] == 2

    history = client.get("/v1/events/health/history")
    assert history.status_code == 200
    snapshots = history.json()
    assert len(snapshots) == 1
    assert snapshots[0]["total_events"] == 2
    assert snapshots[0]["organization_id"] == organization_id

    api_headers = {"X-API-Key": "dev-api-key"}
    summary = client.get("/v1/measurement/summary", headers=api_headers)
    assert summary.status_code == 200
    cards = {card["metric"]: card["value"] for card in summary.json()["data"]["cards"]}
    assert cards["impressions"] == 2
    assert cards["conversion_rate"] == pytest.approx(1.0)

    connector = client.post(
        "/v1/connectors",
        headers=api_headers,
        json={"provider": "posthog", "display_name": "PostHog"},
    )
    assert connector.status_code == 201, connector.text
    connectors = client.get("/v1/connectors", headers=api_headers)
    assert connectors.status_code == 200
    assert connectors.json()["meta"]["total"] == 1

    audit = client.get("/v1/audit-logs")
    assert audit.status_code == 200
    actions = {entry["action"] for entry in audit.json()}
    assert {"organization.created", "creative_treatment.approved", "events.ingested"} <= actions
