from typing import Any

from fastapi import APIRouter, Depends, Header

from app.api.deps import PaginationDep, PrincipalDep, RateLimitDep
from app.api.v1.endpoints._helpers import collection
from app.core.config import get_settings
from app.core.errors import ApiError
from app.core.security import ApiPrincipal, get_demo_organization_id, require_api_key
from app.schemas.common import CollectionResponse
from app.schemas.domain import EventIngestRequest, EventIngestResponse, EventRead
from app.services.events import event_ingestion_service
from app.services.resources import resource_service

router = APIRouter(prefix="/events", dependencies=[RateLimitDep])


async def event_ingest_principal(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> ApiPrincipal:
    settings = get_settings()
    if not x_api_key:
        if settings.environment == "production":
            raise ApiError(401, "missing_api_key", "Missing X-API-Key header")
        return ApiPrincipal(
            organization_id=get_demo_organization_id(),
            api_key_id=None,
            scopes={"events:write", "measurement:read", "admin:demo"},
            subject="demo-local-events",
        )
    return await require_api_key(x_api_key)


@router.post("/ingest")
async def ingest_events(
    payload: EventIngestRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    principal: ApiPrincipal = Depends(event_ingest_principal),
) -> dict[str, Any]:
    result = await event_ingestion_service.ingest(payload, principal, idempotency_key)
    deduplicated = len(payload.events) if result.duplicate else 0
    return {
        "data": result,
        "accepted": result.accepted,
        "deduplicated": deduplicated,
        "duplicate": result.duplicate,
        "idempotency_key": result.idempotency_key,
        "event_ids": result.event_ids,
    }


@router.get("", response_model=CollectionResponse[EventRead])
async def list_events(principal: PrincipalDep, pagination: PaginationDep) -> dict[str, object]:
    items, total = resource_service.list(
        "events",
        principal.organization_id,
        pagination.limit,
        pagination.offset,
    )
    return collection(items, total, pagination)
