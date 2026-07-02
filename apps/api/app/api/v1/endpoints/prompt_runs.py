from fastapi import APIRouter, status

from app.api.deps import PaginationDep, PrincipalDep, RateLimitDep
from app.api.v1.endpoints._helpers import collection, response, to_payload
from app.schemas.common import ApiResponse, CollectionResponse
from app.schemas.domain import PromptRunCreate, PromptRunRead
from app.services.ai import GenerationRequest, get_ai_provider
from app.services.resources import resource_service

router = APIRouter(prefix="/prompt-runs", dependencies=[RateLimitDep])


@router.post("", response_model=ApiResponse[PromptRunRead], status_code=status.HTTP_201_CREATED)
async def create_prompt_run(principal: PrincipalDep, payload: PromptRunCreate) -> dict[str, object]:
    provider = get_ai_provider()
    generation = await provider.generate(
        GenerationRequest(
            prompt=payload.prompt,
            variables=payload.variables,
            model=payload.model,
        )
    )
    item = resource_service.create(
        "prompt_runs",
        {
            **to_payload(payload),
            "provider": payload.provider or generation.provider,
            "model": payload.model or generation.model,
            "response": {"content": generation.content, "raw": generation.raw},
            "status": "succeeded",
            "input_tokens": generation.input_tokens,
            "output_tokens": generation.output_tokens,
        },
        principal.organization_id,
    )
    return response(item)


@router.get("", response_model=CollectionResponse[PromptRunRead])
async def list_prompt_runs(principal: PrincipalDep, pagination: PaginationDep) -> dict[str, object]:
    items, total = resource_service.list(
        "prompt_runs",
        principal.organization_id,
        pagination.limit,
        pagination.offset,
    )
    return collection(items, total, pagination)
