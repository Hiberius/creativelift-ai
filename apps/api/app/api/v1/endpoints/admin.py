from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import PaginationDep, PrincipalDep, RateLimitDep
from app.api.v1.endpoints._helpers import collection, response, to_payload
from app.schemas.common import ApiResponse, CollectionResponse
from app.schemas.domain import (
    APIKeyCreate,
    APIKeyRead,
    AuditLogRead,
    MembershipCreate,
    MembershipRead,
    OrganizationCreate,
    OrganizationRead,
    UserCreate,
    UserRead,
)
from app.services.resources import resource_service

router = APIRouter(responses={401: {"description": "Unauthorized"}})


@router.post(
    "/organizations",
    response_model=ApiResponse[OrganizationRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RateLimitDep],
)
async def create_organization(payload: OrganizationCreate) -> dict[str, object]:
    item = resource_service.create("organizations", to_payload(payload))
    return response(item)


@router.get(
    "/organizations",
    response_model=CollectionResponse[OrganizationRead],
    dependencies=[RateLimitDep],
)
async def list_organizations(pagination: PaginationDep) -> dict[str, object]:
    items, total = resource_service.list("organizations", limit=pagination.limit, offset=pagination.offset)
    return collection(items, total, pagination)


@router.post(
    "/users",
    response_model=ApiResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RateLimitDep],
)
async def create_user(payload: UserCreate) -> dict[str, object]:
    item = resource_service.create("users", {**to_payload(payload), "is_active": True})
    return response(item)


@router.get("/users", response_model=CollectionResponse[UserRead], dependencies=[RateLimitDep])
async def list_users(pagination: PaginationDep) -> dict[str, object]:
    items, total = resource_service.list("users", limit=pagination.limit, offset=pagination.offset)
    return collection(items, total, pagination)


@router.post(
    "/memberships",
    response_model=ApiResponse[MembershipRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RateLimitDep],
)
async def create_membership(payload: MembershipCreate) -> dict[str, object]:
    data = {**to_payload(payload), "status": "active"}
    item = resource_service.create("memberships", data, organization_id=payload.organization_id)
    return response(item)


@router.get("/memberships", response_model=CollectionResponse[MembershipRead], dependencies=[RateLimitDep])
async def list_memberships(
    principal: PrincipalDep,
    pagination: PaginationDep,
) -> dict[str, object]:
    items, total = resource_service.list(
        "memberships",
        organization_id=principal.organization_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return collection(items, total, pagination)


@router.post(
    "/api-keys",
    response_model=ApiResponse[APIKeyRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RateLimitDep],
)
async def create_api_key(principal: PrincipalDep, payload: APIKeyCreate) -> dict[str, object]:
    item = resource_service.create(
        "api_keys",
        {
            **to_payload(payload),
            "key_hash": f"sha256:demo:{payload.name}",
            "last_used_at": None,
            "revoked_at": None,
        },
        organization_id=principal.organization_id,
    )
    return response(item)


@router.get("/api-keys", response_model=CollectionResponse[APIKeyRead], dependencies=[RateLimitDep])
async def list_api_keys(principal: PrincipalDep, pagination: PaginationDep) -> dict[str, object]:
    items, total = resource_service.list(
        "api_keys",
        organization_id=principal.organization_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return collection(items, total, pagination)


@router.get("/audit-logs", response_model=CollectionResponse[AuditLogRead], dependencies=[RateLimitDep])
async def list_audit_logs(principal: PrincipalDep, pagination: PaginationDep) -> dict[str, object]:
    items, total = resource_service.list(
        "audit_logs",
        organization_id=principal.organization_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return collection(items, total, pagination)


@router.post(
    "/audit-logs/demo",
    response_model=ApiResponse[AuditLogRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RateLimitDep],
)
async def create_demo_audit_log(principal: PrincipalDep, resource_id: UUID | None = None) -> dict[str, object]:
    item = resource_service.create(
        "audit_logs",
        {
            "actor_user_id": None,
            "action": "demo.audit.created",
            "resource_type": "demo",
            "resource_id": resource_id,
            "metadata_json": {"source": "api-scaffold"},
        },
        organization_id=principal.organization_id,
    )
    return response(item)
