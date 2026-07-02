from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel, Field

from app.core.rate_limit import enforce_rate_limit
from app.core.security import ApiPrincipal, require_api_key

PrincipalDep = Annotated[ApiPrincipal, Depends(require_api_key)]
RateLimitDep = Depends(enforce_rate_limit)


class PaginationParams(BaseModel):
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


def pagination(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset)


PaginationDep = Annotated[PaginationParams, Depends(pagination)]
