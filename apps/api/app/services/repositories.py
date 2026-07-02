from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol
from uuid import UUID

from app.core.config import get_settings
from app.services.store import DemoStore, demo_store


RESOURCE_MODEL_NAMES = {
    "connectors": "Connector",
    "prompt_runs": "PromptRun",
    "mmm_runs": "MmmRun",
    "uplift_runs": "UpliftRun",
}

VALID_RESOURCE_REPOSITORY_BACKENDS = {"memory", "sqlalchemy"}


@dataclass(frozen=True)
class CollectionPage:
    items: list[dict[str, Any]]
    total: int
    limit: int
    offset: int


class ResourceRepository(Protocol):
    def create(
        self,
        resource: str,
        payload: dict[str, Any],
        organization_id: UUID | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    def list(
        self,
        resource: str,
        organization_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> CollectionPage:
        raise NotImplementedError

    def get(
        self,
        resource: str,
        resource_id: UUID,
        organization_id: UUID | None = None,
    ) -> dict[str, Any] | None:
        raise NotImplementedError


class InMemoryResourceRepository:
    def __init__(self, store: DemoStore = demo_store) -> None:
        self.store = store

    def create(
        self,
        resource: str,
        payload: dict[str, Any],
        organization_id: UUID | None = None,
    ) -> dict[str, Any]:
        return self.store.create(resource, payload, organization_id)

    def list(
        self,
        resource: str,
        organization_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> CollectionPage:
        items, total = self.store.list(resource, organization_id, limit, offset)
        return CollectionPage(items=items, total=total, limit=limit, offset=offset)

    def get(
        self,
        resource: str,
        resource_id: UUID,
        organization_id: UUID | None = None,
    ) -> dict[str, Any] | None:
        return self.store.get(resource, resource_id, organization_id)


class SQLAlchemyResourceRepository:
    def __init__(self, session_factory: Callable[[], Any]) -> None:
        self.session_factory = session_factory

    def create(
        self,
        resource: str,
        payload: dict[str, Any],
        organization_id: UUID | None = None,
    ) -> dict[str, Any]:
        model = self._model_for(resource)
        item = model(**self._tenant_payload(payload, organization_id))
        with self.session_factory() as session:
            session.add(item)
            session.commit()
            session.refresh(item)
            return self._to_payload(item)

    def list(
        self,
        resource: str,
        organization_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> CollectionPage:
        from sqlalchemy import func, select

        model = self._model_for(resource)
        filters = self._tenant_filters(model, organization_id)
        with self.session_factory() as session:
            total = session.scalar(select(func.count()).select_from(model).where(*filters)) or 0
            statement = select(model).where(*filters).offset(offset).limit(limit)
            if hasattr(model, "created_at"):
                statement = statement.order_by(model.created_at.desc())
            items = [self._to_payload(item) for item in session.scalars(statement).all()]
            return CollectionPage(items=items, total=total, limit=limit, offset=offset)

    def get(
        self,
        resource: str,
        resource_id: UUID,
        organization_id: UUID | None = None,
    ) -> dict[str, Any] | None:
        model = self._model_for(resource)
        with self.session_factory() as session:
            item = session.get(model, resource_id)
            if item is None:
                return None
            if organization_id is not None and getattr(item, "organization_id", None) != organization_id:
                return None
            return self._to_payload(item)

    def _model_for(self, resource: str) -> type[Any]:
        from app.db import models

        model_name = RESOURCE_MODEL_NAMES.get(resource)
        if model_name is None:
            raise ValueError(f"No SQLAlchemy model registered for resource: {resource}")
        return getattr(models, model_name)

    def _tenant_payload(self, payload: dict[str, Any], organization_id: UUID | None) -> dict[str, Any]:
        if organization_id is None or "organization_id" in payload:
            return payload
        return {**payload, "organization_id": organization_id}

    def _tenant_filters(self, model: type[Any], organization_id: UUID | None) -> list[Any]:
        if organization_id is None or not hasattr(model, "organization_id"):
            return []
        return [model.organization_id == organization_id]

    def _to_payload(self, item: Any) -> dict[str, Any]:
        return {column.name: getattr(item, column.name) for column in item.__table__.columns}


def create_resource_repository(backend: str | None = None) -> ResourceRepository:
    selected_backend = backend or get_settings().resource_repository_backend
    if selected_backend == "memory":
        return InMemoryResourceRepository()
    if selected_backend == "sqlalchemy":
        from app.db.session import SessionLocal

        return SQLAlchemyResourceRepository(SessionLocal)
    raise ValueError(
        f"Unknown RESOURCE_REPOSITORY_BACKEND={selected_backend!r}; "
        f"expected one of {sorted(VALID_RESOURCE_REPOSITORY_BACKENDS)}"
    )
