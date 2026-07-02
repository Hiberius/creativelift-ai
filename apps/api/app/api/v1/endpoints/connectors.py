from fastapi import APIRouter, status

from app.api.deps import PaginationDep, PrincipalDep, RateLimitDep
from app.api.v1.endpoints._helpers import collection, response, to_payload
from app.schemas.common import ApiResponse, CollectionResponse
from app.schemas.domain import ConnectorCreate, ConnectorRead
from app.services.resources import resource_service

router = APIRouter(prefix="/connectors", dependencies=[RateLimitDep])


@router.post("", response_model=ApiResponse[ConnectorRead], status_code=status.HTTP_201_CREATED)
async def create_connector(principal: PrincipalDep, payload: ConnectorCreate) -> dict[str, object]:
    item = resource_service.create(
        "connectors",
        {**to_payload(payload), "status": "disconnected", "last_sync_at": None},
        principal.organization_id,
    )
    return response(item)


@router.get("", response_model=CollectionResponse[ConnectorRead])
async def list_connectors(principal: PrincipalDep, pagination: PaginationDep) -> dict[str, object]:
    items, total = resource_service.list(
        "connectors",
        principal.organization_id,
        pagination.limit,
        pagination.offset,
    )
    return collection(items, total, pagination)
