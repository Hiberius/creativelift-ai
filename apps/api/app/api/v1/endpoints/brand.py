from fastapi import APIRouter, status

from app.api.deps import PaginationDep, PrincipalDep, RateLimitDep
from app.api.v1.endpoints._helpers import collection, response, to_payload
from app.schemas.common import ApiResponse, CollectionResponse
from app.schemas.domain import (
    ApprovedClaimCreate,
    ApprovedClaimRead,
    BrandPackCreate,
    BrandPackRead,
)
from app.services.resources import resource_service

router = APIRouter(dependencies=[RateLimitDep])


@router.post("/brand-packs", response_model=ApiResponse[BrandPackRead], status_code=status.HTTP_201_CREATED)
async def create_brand_pack(principal: PrincipalDep, payload: BrandPackCreate) -> dict[str, object]:
    item = resource_service.create("brand_packs", to_payload(payload), principal.organization_id)
    return response(item)


@router.get("/brand-packs", response_model=CollectionResponse[BrandPackRead])
async def list_brand_packs(principal: PrincipalDep, pagination: PaginationDep) -> dict[str, object]:
    items, total = resource_service.list(
        "brand_packs",
        principal.organization_id,
        pagination.limit,
        pagination.offset,
    )
    return collection(items, total, pagination)


@router.post(
    "/approved-claims",
    response_model=ApiResponse[ApprovedClaimRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_approved_claim(
    principal: PrincipalDep,
    payload: ApprovedClaimCreate,
) -> dict[str, object]:
    item = resource_service.create("approved_claims", to_payload(payload), principal.organization_id)
    return response(item)


@router.get("/approved-claims", response_model=CollectionResponse[ApprovedClaimRead])
async def list_approved_claims(principal: PrincipalDep, pagination: PaginationDep) -> dict[str, object]:
    items, total = resource_service.list(
        "approved_claims",
        principal.organization_id,
        pagination.limit,
        pagination.offset,
    )
    return collection(items, total, pagination)
