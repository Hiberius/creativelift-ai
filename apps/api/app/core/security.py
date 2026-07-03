from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from uuid import UUID

from fastapi import Cookie, Header, HTTPException, status

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


def hash_password(password: str) -> str:
    """Memory-hard scrypt hash (stdlib only, keeps the quickstart dependency-free)."""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt$16384$8$1${salt.hex()}${digest.hex()}"


def verify_password(password: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    try:
        scheme, n, r, parallelism, salt_hex, digest_hex = hashed.split("$")
        if scheme != "scrypt":
            return False
        candidate = hashlib.scrypt(
            password.encode("utf-8"),
            salt=bytes.fromhex(salt_hex),
            n=int(n),
            r=int(r),
            p=int(parallelism),
        )
        return hmac.compare_digest(candidate.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def generate_session_token() -> tuple[str, str]:
    """Returns (raw_token_for_cookie, sha256_hash_for_storage)."""
    raw = secrets.token_urlsafe(32)
    return raw, hash_session_token(raw)


def hash_session_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def resolve_session_principal(raw_token: str) -> Principal | None:
    """Resolve a session cookie into a user Principal, or None if invalid."""
    from app.db.tenant import set_current_organization
    from app.services.core_repositories import core_repository

    record = core_repository.get_active_user_session(hash_session_token(raw_token))
    if record is None:
        return None
    role = core_repository.get_membership_role(record.user_id, record.organization_id) or "viewer"
    set_current_organization(record.organization_id)
    return Principal(
        organization_id=record.organization_id,
        user_id=record.user_id,
        role=role,
        scopes=("user:*",),
        api_key_prefix=None,
    )


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


SESSION_COOKIE_NAME = "creativelift_session"
DEFAULT_SERVICE_SCOPES = ("events:write", "experiments:read", "creatives:read", "measurement:read")
_DEV_ENVIRONMENTS = {"development", "dev", "local", "test", "ci"}


def is_production() -> bool:
    return settings.app_env.lower() not in _DEV_ENVIRONMENTS


def _resolve_api_key(raw_key: str):
    """Look up a presented API key against the repository by its HMAC hash."""
    from app.services.core_repositories import core_repository

    return core_repository.get_api_key_by_hash(hash_api_key(raw_key))


async def get_principal(
    authorization: str | None = Header(default=None),
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> Principal:
    if session_token:
        principal = resolve_session_principal(session_token)
        if principal is not None:
            return principal
        # Stale/revoked cookie: fall through to the other auth schemes.
    if authorization is None:
        if is_production():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required: send 'Authorization: Bearer <api-key>'",
            )
        from app.db.tenant import set_current_organization

        set_current_organization(get_demo_organization_id())
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
        from app.db.tenant import set_current_organization

        set_current_organization(record.organization_id)
        return Principal(
            organization_id=record.organization_id,
            user_id=None,
            role="service",
            scopes=tuple(record.scopes) or DEFAULT_SERVICE_SCOPES,
            api_key_prefix=record.prefix,
        )
    if not is_production() and token == settings.demo_api_key:
        from app.db.tenant import set_current_organization

        set_current_organization(get_demo_organization_id())
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
    if "demo:*" in principal.scopes or "user:*" in principal.scopes or scope in principal.scopes:
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
        from app.db.tenant import set_current_organization

        set_current_organization(record.organization_id)
        return ApiPrincipal(
            organization_id=record.organization_id,
            api_key_id=record.id,
            scopes=set(record.scopes) or set(DEFAULT_SERVICE_SCOPES),
            subject=f"api-key:{record.prefix}",
        )
    if not is_production() and x_api_key == settings.demo_api_key:
        from app.db.tenant import set_current_organization

        set_current_organization(get_demo_organization_id())
        return ApiPrincipal(
            organization_id=get_demo_organization_id(),
            api_key_id=None,
            scopes={"events:write", "measurement:read", "admin:demo"},
            subject="demo-api-key",
        )
    raise ApiError(401, "invalid_api_key", "Invalid or revoked API key")
