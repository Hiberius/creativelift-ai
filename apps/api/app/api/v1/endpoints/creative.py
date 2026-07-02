from fastapi import APIRouter, status

from app.api.deps import PaginationDep, PrincipalDep, RateLimitDep
from app.api.v1.endpoints._helpers import collection, response, to_payload
from app.schemas.common import ApiResponse, CollectionResponse
from app.schemas.domain import (
    ApprovalReviewCreate,
    ApprovalReviewRead,
    CreativeTreatmentCreate,
    CreativeTreatmentRead,
    CreativeVersionCreate,
    CreativeVersionRead,
)
from app.services.resources import resource_service

router = APIRouter(dependencies=[RateLimitDep])


@router.post(
    "/creative-treatments",
    response_model=ApiResponse[CreativeTreatmentRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_creative_treatment(
    principal: PrincipalDep,
    payload: CreativeTreatmentCreate,
) -> dict[str, object]:
    item = resource_service.create("creative_treatments", to_payload(payload), principal.organization_id)
    return response(item)


@router.get("/creative-treatments", response_model=CollectionResponse[CreativeTreatmentRead])
async def list_creative_treatments(
    principal: PrincipalDep,
    pagination: PaginationDep,
) -> dict[str, object]:
    items, total = resource_service.list(
        "creative_treatments",
        principal.organization_id,
        pagination.limit,
        pagination.offset,
    )
    return collection(items, total, pagination)


@router.post(
    "/creative-versions",
    response_model=ApiResponse[CreativeVersionRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_creative_version(
    principal: PrincipalDep,
    payload: CreativeVersionCreate,
) -> dict[str, object]:
    item = resource_service.create("creative_versions", to_payload(payload), principal.organization_id)
    return response(item)


@router.get("/creative-versions", response_model=CollectionResponse[CreativeVersionRead])
async def list_creative_versions(
    principal: PrincipalDep,
    pagination: PaginationDep,
) -> dict[str, object]:
    items, total = resource_service.list(
        "creative_versions",
        principal.organization_id,
        pagination.limit,
        pagination.offset,
    )
    return collection(items, total, pagination)


@router.post(
    "/approval-reviews",
    response_model=ApiResponse[ApprovalReviewRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_approval_review(
    principal: PrincipalDep,
    payload: ApprovalReviewCreate,
) -> dict[str, object]:
    item = resource_service.create("approval_reviews", to_payload(payload), principal.organization_id)
    return response(item)


@router.get("/approval-reviews", response_model=CollectionResponse[ApprovalReviewRead])
async def list_approval_reviews(
    principal: PrincipalDep,
    pagination: PaginationDep,
) -> dict[str, object]:
    items, total = resource_service.list(
        "approval_reviews",
        principal.organization_id,
        pagination.limit,
        pagination.offset,
    )
    return collection(items, total, pagination)
