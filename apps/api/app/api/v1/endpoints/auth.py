"""Human login: registration, session-cookie auth, logout.

Passwords are hashed with stdlib scrypt; sessions are stored server-side by
token hash so they can be revoked. API-key auth (Authorization / X-API-Key)
remains the path for machines and SDKs.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Cookie, Response

from app.core.config import settings
from app.core.errors import ApiError
from app.core.rate_limit import rate_limiter
from app.core.security import (
    SESSION_COOKIE_NAME,
    generate_session_token,
    hash_password,
    hash_session_token,
    is_production,
    resolve_session_principal,
    verify_password,
)
from app.schemas.common import (
    AuthSessionRead,
    LoginRequest,
    OrganizationCreate,
    RegisterRequest,
    UserRead,
)
from app.db.tenant import set_current_organization
from app.services.core_repositories import core_repository

router = APIRouter(prefix="/auth", tags=["auth"])


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "org"


def _start_session(response: Response, user_id, organization_id) -> datetime:
    raw_token, token_hash = generate_session_token()
    expires_at = datetime.now(UTC) + timedelta(hours=settings.session_ttl_hours)
    core_repository.create_user_session(user_id, organization_id, token_hash, expires_at)
    response.set_cookie(
        SESSION_COOKIE_NAME,
        raw_token,
        httponly=True,
        samesite="lax",
        secure=is_production(),
        max_age=settings.session_ttl_hours * 3600,
        path="/",
    )
    return expires_at


def _session_read(user, organization, role: str, expires_at: datetime) -> AuthSessionRead:
    return AuthSessionRead(
        user=UserRead(id=user.id, email=user.email, name=user.name),
        organization=organization,
        role=role,
        expires_at=expires_at,
    )


@router.post("/register", response_model=AuthSessionRead)
async def register(payload: RegisterRequest, response: Response) -> AuthSessionRead:
    rate_limiter.check(f"auth-register:{payload.email.lower()}", 5, 60)
    if core_repository.get_user_by_email(payload.email) is not None:
        raise ApiError(409, "email_taken", "An account with this email already exists")

    slug = payload.organization_slug or f"{_slugify(payload.organization_name)}-{uuid4().hex[:6]}"
    try:
        organization = core_repository.create_organization(
            OrganizationCreate(name=payload.organization_name, slug=slug)
        )
    except ValueError as exc:
        raise ApiError(409, "slug_taken", "This organization slug is already in use") from exc

    try:
        user = core_repository.create_user(payload.email, payload.name, hash_password(payload.password))
    except ValueError as exc:
        raise ApiError(409, "email_taken", "An account with this email already exists") from exc

    core_repository.create_membership(user.id, organization.id, "owner")
    set_current_organization(organization.id)
    expires_at = _start_session(response, user.id, organization.id)
    core_repository.record_audit("user.registered", "user", organization.id, str(user.id))
    return _session_read(user, organization, "owner", expires_at)


@router.post("/login", response_model=AuthSessionRead)
async def login(payload: LoginRequest, response: Response) -> AuthSessionRead:
    rate_limiter.check(f"auth-login:{payload.email.lower()}", 10, 60)
    user = core_repository.get_user_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise ApiError(401, "invalid_credentials", "Invalid email or password")

    membership = core_repository.get_primary_membership(user.id)
    if membership is None:
        raise ApiError(403, "no_membership", "This account does not belong to any organization")
    organization_id, role = membership
    organization = core_repository.get_organization(organization_id)
    if organization is None:
        raise ApiError(403, "no_membership", "This account's organization no longer exists")

    set_current_organization(organization_id)
    expires_at = _start_session(response, user.id, organization_id)
    core_repository.record_audit("user.logged_in", "user", organization_id, str(user.id))
    return _session_read(user, organization, role, expires_at)


@router.post("/logout")
async def logout(
    response: Response,
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> dict[str, str]:
    if session_token:
        core_repository.revoke_user_session(hash_session_token(session_token))
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return {"status": "logged_out"}


@router.get("/session", response_model=AuthSessionRead)
async def current_session(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> AuthSessionRead:
    if not session_token:
        raise ApiError(401, "no_session", "Not logged in")
    principal = resolve_session_principal(session_token)
    if principal is None or principal.user_id is None:
        raise ApiError(401, "no_session", "Session expired or revoked")
    user = core_repository.get_user(principal.user_id)
    organization = core_repository.get_organization(principal.organization_id)
    if user is None or organization is None:
        raise ApiError(401, "no_session", "Session expired or revoked")
    record = core_repository.get_active_user_session(hash_session_token(session_token))
    return _session_read(user, organization, principal.role, record.expires_at)
