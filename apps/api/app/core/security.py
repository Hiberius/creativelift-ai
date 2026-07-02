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


DEFAULT_SERVICE_SCOPES = ("events:write", "experiments:read", "creatives:read", "measurement:read")
_DEV_ENVIRONMENTS = {"development", "dev", "local", "test", "ci"}


def is_production() -> bool:
    return settings.app_env.lower() not in _DEV_ENVIRONMENTS


def _resolve_api_key(raw_key: str):
    """Look up a presented API key against the repository by its HMAC hash."""
    from app.services.core_repositories import core_repository

    return core_repository.get_api_key_by_hash(hash_api_key(raw_key))


def get_principal(authorization: str | None = Header(default=None)) -> Principal:
    if authorization is None:
        if is_production():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required: send 'Authorization: Bearer <api-key>'",
            )
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
    record = _resolve_api_key(token)
    if record is not None:
        return Principal(
            organization_id=record.organization_id,
            user_id=None,
            role="service",
            scopes=tuple(record.scopes) or DEFAULT_SERVICE_SCOPES,
            api_key_prefix=record.prefix,
        )
    if not is_production() and token == settings.demo_api_key:
        return Principal(
            organization_id=get_demo_organization_id(),
            user_id=None,
            role="service",
            scopes=DEFAULT_SERVICE_SCOPES,
            api_key_prefix="demo",
        )
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or revoked API key")


def require_role(principal: Principal, allowed: set[str]) -> None:
    if principal.role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")


def require_scope(principal: Principal, scope: str) -> None:
    if "demo:*" in principal.scopes or scope in principal.scopes:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"API key is missing the required scope: {scope}",
    )


async def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> ApiPrincipal:
    if not x_api_key:
        raise ApiError(401, "missing_api_key", "Missing X-API-Key header")
    record = _resolve_api_key(x_api_key)
    if record is not None:
        return ApiPrincipal(
            organization_id=record.organization_id,
            api_key_id=record.id,
            scopes=set(record.scopes) or set(DEFAULT_SERVICE_SCOPES),
            subject=f"api-key:{record.prefix}",
        )
    if not is_production() and x_api_key == settings.demo_api_key:
        return ApiPrincipal(
            organization_id=get_demo_organization_id(),
            api_key_id=None,
            scopes={"events:write", "measurement:read", "admin:demo"},
            subject="demo-api-key",
        )
    raise ApiError(401, "invalid_api_key", "Invalid or revoked API key")
