from fastapi import APIRouter, Query, status

from app.api.deps import PaginationDep, PrincipalDep, RateLimitDep
from app.api.v1.endpoints._helpers import collection, response, to_payload
from app.schemas.common import ApiResponse, CollectionResponse
from app.schemas.domain import MMMRunCreate, MMMRunRead, MeasurementSummary, UpliftRunCreate, UpliftRunRead
from app.services.measurement import measurement_service
from app.services.resources import resource_service

router = APIRouter(prefix="/measurement", dependencies=[RateLimitDep])


@router.get("/summary", response_model=ApiResponse[MeasurementSummary])
async def measurement_summary(
    principal: PrincipalDep,
    window: str = Query(default="last_7_days", max_length=80),
) -> dict[str, MeasurementSummary]:
    summary = await measurement_service.summary(principal.organization_id, window)
    return {"data": summary}


@router.post("/mmm-runs", response_model=ApiResponse[MMMRunRead], status_code=status.HTTP_201_CREATED)
async def create_mmm_run(principal: PrincipalDep, payload: MMMRunCreate) -> dict[str, object]:
    item = resource_service.create(
        "mmm_runs",
        {**to_payload(payload), "status": "queued", "outputs": {}},
        principal.organization_id,
    )
    return response(item)


@router.get("/mmm-runs", response_model=CollectionResponse[MMMRunRead])
async def list_mmm_runs(principal: PrincipalDep, pagination: PaginationDep) -> dict[str, object]:
    items, total = resource_service.list(
        "mmm_runs",
        principal.organization_id,
        pagination.limit,
        pagination.offset,
    )
    return collection(items, total, pagination)


@router.post("/uplift-runs", response_model=ApiResponse[UpliftRunRead], status_code=status.HTTP_201_CREATED)
async def create_uplift_run(principal: PrincipalDep, payload: UpliftRunCreate) -> dict[str, object]:
    item = resource_service.create(
        "uplift_runs",
        {**to_payload(payload), "status": "queued", "outputs": {}},
        principal.organization_id,
    )
    return response(item)


@router.get("/uplift-runs", response_model=CollectionResponse[UpliftRunRead])
async def list_uplift_runs(principal: PrincipalDep, pagination: PaginationDep) -> dict[str, object]:
    items, total = resource_service.list(
        "uplift_runs",
        principal.organization_id,
        pagination.limit,
        pagination.offset,
    )
    return collection(items, total, pagination)
