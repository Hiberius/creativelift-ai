from fastapi import APIRouter, status

from app.api.deps import PaginationDep, PrincipalDep, RateLimitDep
from app.api.v1.endpoints._helpers import collection, response, to_payload
from app.schemas.common import ApiResponse, CollectionResponse
from app.schemas.domain import BriefCreate, BriefRead
from app.services.resources import resource_service

router = APIRouter(prefix="/briefs", dependencies=[RateLimitDep])


@router.post("", response_model=ApiResponse[BriefRead], status_code=status.HTTP_201_CREATED)
async def create_brief(principal: PrincipalDep, payload: BriefCreate) -> dict[str, object]:
    item = resource_service.create("briefs", to_payload(payload), principal.organization_id)
    return response(item)


@router.get("", response_model=CollectionResponse[BriefRead])
async def list_briefs(principal: PrincipalDep, pagination: PaginationDep) -> dict[str, object]:
    items, total = resource_service.list(
        "briefs",
        principal.organization_id,
        pagination.limit,
        pagination.offset,
    )
    return collection(items, total, pagination)
