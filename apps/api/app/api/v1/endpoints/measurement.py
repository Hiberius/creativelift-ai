from typing import Any

from fastapi import APIRouter, Query, status
from mmm_service import run_demo_mmm
from uplift_service import score_segment_uplift

from app.api.deps import PaginationDep, PrincipalDep, RateLimitDep
from app.api.v1.endpoints._helpers import collection, response, to_payload
from app.schemas.common import ApiResponse, CollectionResponse
from app.schemas.domain import MMMRunCreate, MMMRunRead, MeasurementSummary, UpliftRunCreate, UpliftRunRead
from app.services.measurement import measurement_service
from app.services.resources import resource_service

router = APIRouter(prefix="/measurement", dependencies=[RateLimitDep])


def _is_row_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(row, dict) for row in value)


def _execute_mmm_run(inputs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Run the MMM service synchronously; never raises for bad inputs."""
    weekly_rows = inputs.get("weekly_rows")
    if not _is_row_list(weekly_rows):
        return "failed", {
            "error": "inputs.weekly_rows must be a non-empty list of weekly spend row objects."
        }
    try:
        outputs = run_demo_mmm(weekly_rows)
    except (TypeError, ValueError) as exc:
        return "failed", {"error": f"MMM computation failed: {exc}"}
    if not outputs.get("channels"):
        return "failed", {
            "error": "No spend channels found: each weekly row needs at least one '<channel>_spend' key."
        }
    return "succeeded", outputs


def _execute_uplift_run(inputs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Run the uplift service synchronously; never raises for bad inputs."""
    rows = inputs.get("rows")
    if not _is_row_list(rows):
        return "failed", {
            "error": "inputs.rows must be a non-empty list of observation row objects."
        }
    segment_key = inputs.get("segment_key", "segment")
    if not isinstance(segment_key, str) or not segment_key:
        return "failed", {"error": "inputs.segment_key must be a non-empty string when provided."}
    try:
        segments = score_segment_uplift(rows, segment_key)
    except (TypeError, ValueError) as exc:
        return "failed", {"error": f"Uplift computation failed: {exc}"}
    return "succeeded", {"model_type": "segment_baseline", "segments": segments}


@router.get("/summary", response_model=ApiResponse[MeasurementSummary])
async def measurement_summary(
    principal: PrincipalDep,
    window: str = Query(default="last_7_days", max_length=80),
) -> dict[str, MeasurementSummary]:
    summary = await measurement_service.summary(principal.organization_id, window)
    return {"data": summary}


@router.post("/mmm-runs", response_model=ApiResponse[MMMRunRead], status_code=status.HTTP_201_CREATED)
async def create_mmm_run(principal: PrincipalDep, payload: MMMRunCreate) -> dict[str, object]:
    run_status, outputs = _execute_mmm_run(payload.inputs)
    item = resource_service.create(
        "mmm_runs",
        {**to_payload(payload), "status": run_status, "outputs": outputs},
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
    run_status, outputs = _execute_uplift_run(payload.inputs)
    item = resource_service.create(
        "uplift_runs",
        {**to_payload(payload), "status": run_status, "outputs": outputs},
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
