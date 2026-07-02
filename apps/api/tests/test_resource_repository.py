from uuid import uuid4
from pathlib import Path

from app.services.repositories import InMemoryResourceRepository, create_resource_repository
from app.services.resources import ResourceService
from app.services.store import DemoStore


def test_resource_repository_filters_by_organization_and_paginates():
    org_a = uuid4()
    org_b = uuid4()
    repository = InMemoryResourceRepository(DemoStore())

    first = repository.create("connectors", {"provider": "posthog", "display_name": "A1"}, org_a)
    repository.create("connectors", {"provider": "rudder", "display_name": "A2"}, org_a)
    repository.create("connectors", {"provider": "snowplow", "display_name": "B1"}, org_b)

    page = repository.list("connectors", org_a, limit=1, offset=0)
    assert page.total == 2
    assert page.limit == 1
    assert page.offset == 0
    assert page.items == [first]

    assert repository.get("connectors", first["id"], org_a) == first
    assert repository.get("connectors", first["id"], org_b) is None


def test_resource_service_uses_repository_contract():
    org_id = uuid4()
    service = ResourceService(InMemoryResourceRepository(DemoStore()))

    created = service.create("prompt_runs", {"provider": "mock"}, org_id)
    items, total = service.list("prompt_runs", org_id)

    assert total == 1
    assert items == [created]
    assert service.get("prompt_runs", created["id"], org_id) == created


def test_sqlalchemy_repository_is_lazy_and_covers_modular_resources():
    repo = Path(__file__).resolve().parents[1]
    source = (repo / "app" / "services" / "repositories.py").read_text()

    assert "class SQLAlchemyResourceRepository" in source
    assert '"connectors": "Connector"' in source
    assert '"prompt_runs": "PromptRun"' in source
    assert '"mmm_runs": "MmmRun"' in source
    assert '"uplift_runs": "UpliftRun"' in source
    assert "from sqlalchemy import" not in source.split("class SQLAlchemyResourceRepository")[0]


def test_repository_factory_defaults_to_memory_backend():
    repository = create_resource_repository("memory")

    assert isinstance(repository, InMemoryResourceRepository)


def test_repository_factory_has_lazy_sqlalchemy_backend():
    repo = Path(__file__).resolve().parents[1]
    source = (repo / "app" / "services" / "repositories.py").read_text()

    assert 'selected_backend == "sqlalchemy"' in source
    assert "from app.db.session import SessionLocal" in source
    assert source.index('selected_backend == "sqlalchemy"') < source.index("from app.db.session import SessionLocal")
