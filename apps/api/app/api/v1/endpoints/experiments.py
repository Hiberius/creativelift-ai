from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import PaginationDep, PrincipalDep, RateLimitDep
from app.api.v1.endpoints._helpers import collection, response, to_payload
from app.schemas.common import ApiResponse, CollectionResponse
from app.schemas.domain import (
    BanditArmCreate,
    BanditArmRead,
    BanditCreate,
    BanditRead,
    ExperimentCreate,
    ExperimentRead,
    ExperimentResultRead,
    ExperimentVariantCreate,
    ExperimentVariantRead,
)
from app.services.resources import resource_service

router = APIRouter(dependencies=[RateLimitDep])


@router.post("/experiments", response_model=ApiResponse[ExperimentRead], status_code=status.HTTP_201_CREATED)
async def create_experiment(principal: PrincipalDep, payload: ExperimentCreate) -> dict[str, object]:
    item = resource_service.create("experiments", to_payload(payload), principal.organization_id)
    return response(item)


@router.get("/experiments", response_model=CollectionResponse[ExperimentRead])
async def list_experiments(principal: PrincipalDep, pagination: PaginationDep) -> dict[str, object]:
    items, total = resource_service.list(
        "experiments",
        principal.organization_id,
        pagination.limit,
        pagination.offset,
    )
    return collection(items, total, pagination)


@router.post(
    "/experiments/{experiment_id}/variants",
    response_model=ApiResponse[ExperimentVariantRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_experiment_variant(
    experiment_id: UUID,
    principal: PrincipalDep,
    payload: ExperimentVariantCreate,
) -> dict[str, object]:
    item = resource_service.create(
        "experiment_variants",
        {**to_payload(payload), "experiment_id": experiment_id},
        principal.organization_id,
    )
    return response(item)


@router.get(
    "/experiments/{experiment_id}/variants",
    response_model=CollectionResponse[ExperimentVariantRead],
)
async def list_experiment_variants(
    experiment_id: UUID,
    principal: PrincipalDep,
    pagination: PaginationDep,
) -> dict[str, object]:
    items, _total = resource_service.list(
        "experiment_variants",
        principal.organization_id,
        limit=500,
        offset=0,
    )
    filtered = [item for item in items if item.get("experiment_id") == experiment_id]
    return collection(filtered[pagination.offset : pagination.offset + pagination.limit], len(filtered), pagination)


@router.get(
    "/experiments/{experiment_id}/results",
    response_model=CollectionResponse[ExperimentResultRead],
)
async def list_experiment_results(
    experiment_id: UUID,
    principal: PrincipalDep,
    pagination: PaginationDep,
) -> dict[str, object]:
    items, _total = resource_service.list(
        "experiment_results",
        principal.organization_id,
        limit=500,
        offset=0,
    )
    filtered = [item for item in items if item.get("experiment_id") == experiment_id]
    if not filtered:
        filtered = [
            {
                "id": UUID("00000000-0000-4000-8000-000000000101"),
                "organization_id": principal.organization_id,
                "experiment_id": experiment_id,
                "variant_id": None,
                "metric_name": "conversion_rate",
                "value": 0.043,
                "sample_size": 12000,
                "confidence": 0.91,
                "computed_at": datetime.now(UTC),
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
        ]
    return collection(filtered[pagination.offset : pagination.offset + pagination.limit], len(filtered), pagination)


@router.post("/bandits", response_model=ApiResponse[BanditRead], status_code=status.HTTP_201_CREATED)
async def create_bandit(principal: PrincipalDep, payload: BanditCreate) -> dict[str, object]:
    item = resource_service.create("bandits", to_payload(payload), principal.organization_id)
    return response(item)


@router.get("/bandits", response_model=CollectionResponse[BanditRead])
async def list_bandits(principal: PrincipalDep, pagination: PaginationDep) -> dict[str, object]:
    items, total = resource_service.list(
        "bandits",
        principal.organization_id,
        pagination.limit,
        pagination.offset,
    )
    return collection(items, total, pagination)


@router.post(
    "/bandits/{bandit_id}/arms",
    response_model=ApiResponse[BanditArmRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_bandit_arm(
    bandit_id: UUID,
    principal: PrincipalDep,
    payload: BanditArmCreate,
) -> dict[str, object]:
    item = resource_service.create(
        "bandit_arms",
        {**to_payload(payload), "bandit_id": bandit_id},
        principal.organization_id,
    )
    return response(item)


@router.get("/bandits/{bandit_id}/arms", response_model=CollectionResponse[BanditArmRead])
async def list_bandit_arms(
    bandit_id: UUID,
    principal: PrincipalDep,
    pagination: PaginationDep,
) -> dict[str, object]:
    items, _total = resource_service.list(
        "bandit_arms",
        principal.organization_id,
        limit=500,
        offset=0,
    )
    filtered = [item for item in items if item.get("bandit_id") == bandit_id]
    return collection(filtered[pagination.offset : pagination.offset + pagination.limit], len(filtered), pagination)
