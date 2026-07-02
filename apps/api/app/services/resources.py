from typing import Any
from uuid import UUID

from app.services.repositories import ResourceRepository, create_resource_repository


class ResourceService:
    def __init__(self, repository: ResourceRepository | None = None) -> None:
        self.repository = repository or create_resource_repository()

    def create(
        self,
        resource: str,
        payload: dict[str, Any],
        organization_id: UUID | None = None,
    ) -> dict[str, Any]:
        return self.repository.create(resource, payload, organization_id)

    def list(
        self,
        resource: str,
        organization_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        page = self.repository.list(resource, organization_id, limit, offset)
        return page.items, page.total

    def get(
        self,
        resource: str,
        resource_id: UUID,
        organization_id: UUID | None = None,
    ) -> dict[str, Any] | None:
        return self.repository.get(resource, resource_id, organization_id)


resource_service = ResourceService()
