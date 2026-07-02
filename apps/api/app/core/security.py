from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from uuid import UUID

from fastapi import Header, HTTPException, status

from app.core.config import settings
from app.core.errors import ApiError


@dataclass(frozen=True)
class Principal:
    organization_id: UUID
    user_id: UUID | None
    role: str
    scopes: tuple[str, ...]
    api_key_prefix: str | None = None


@dataclass(frozen=True)
class ApiPrincipal:
    organization_id: UUID
    api_key_id: UUID | None
    scopes: set[str]
    subject: str


DEMO_ORG_ID = UUID("00000000-0000-0000-0000-000000000001")
DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000002")
_demo_organization_id = DEMO_ORG_ID


def get_demo_organization_id() -> UUID:
    return _demo_organization_id


def set_demo_organization_id(organization_id: UUID) -> None:
    global _demo_organization_id
    _demo_organization_id = organization_id


def reset_demo_organization_id() -> None:
    set_demo_organization_id(DEMO_ORG_ID)


def generate_api_key() -> tuple[str, str, str]:
    raw = f"clai_{secrets.token_urlsafe(32)}"
    prefix = raw[:12]
    return raw, prefix, hash_api_key(raw)


def hash_api_key(raw: str) -> str:
    digest = hmac.new(
        settings.api_key_pepper.encode("utf-8"),
        raw.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return digest


def get_principal(authorization: str | None = Header(default=None)) -> Principal:
    if authorization is None:
        return Principal(
            organization_id=get_demo_organization_id(),
            user_id=DEMO_USER_ID,
            role="owner",
            scopes=("demo:*",),
            api_key_prefix="demo",
        )
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth header")
    # MVP scaffold: resolve real hashed API keys against Postgres in the repository layer.
    return Principal(
        organization_id=get_demo_organization_id(),
        user_id=None,
        role="service",
        scopes=("events:write", "experiments:read", "creatives:read"),
        api_key_prefix=token[:12],
    )


def require_role(principal: Principal, allowed: set[str]) -> None:
    if principal.role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")


async def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> ApiPrincipal:
    if not x_api_key:
        raise ApiError(401, "missing_api_key", "Missing X-API-Key header")
    if x_api_key != settings.demo_api_key:
        raise ApiError(401, "invalid_api_key", "Invalid API key")
    return ApiPrincipal(
        organization_id=get_demo_organization_id(),
        api_key_id=None,
        scopes={"events:write", "measurement:read", "admin:demo"},
        subject="demo-api-key",
    )
