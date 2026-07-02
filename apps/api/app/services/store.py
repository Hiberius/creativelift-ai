from collections import defaultdict
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


class DemoStore:
    def __init__(self) -> None:
        self._resources: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def create(
        self,
        resource: str,
        payload: dict[str, Any],
        organization_id: UUID | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        item = {
            "id": uuid4(),
            "created_at": now,
            "updated_at": now,
            **payload,
        }
        if organization_id and "organization_id" not in item:
            item["organization_id"] = organization_id
        self._resources[resource].append(item)
        return item

    def list(
        self,
        resource: str,
        organization_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        items = self._resources[resource]
        if organization_id:
            items = [item for item in items if item.get("organization_id") == organization_id]
        total = len(items)
        return items[offset : offset + limit], total

    def get(
        self,
        resource: str,
        resource_id: UUID,
        organization_id: UUID | None = None,
    ) -> dict[str, Any] | None:
        for item in self._resources[resource]:
            if item["id"] != resource_id:
                continue
            if organization_id and item.get("organization_id") != organization_id:
                continue
            return item
        return None


demo_store = DemoStore()
