from typing import Any

from app.api.deps import PaginationParams


def to_payload(model: Any) -> dict[str, Any]:
    return model.model_dump(mode="python", exclude_none=True)


def response(item: dict[str, Any]) -> dict[str, Any]:
    return {"data": item}


def collection(
    items: list[dict[str, Any]],
    total: int,
    pagination: PaginationParams,
) -> dict[str, Any]:
    return {
        "data": items,
        "meta": {
            "total": total,
            "limit": pagination.limit,
            "offset": pagination.offset,
        },
    }
