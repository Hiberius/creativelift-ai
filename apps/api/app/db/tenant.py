"""Request-scoped tenant context for Postgres Row-Level Security.

`get_principal` / `require_api_key` (and the auth endpoints during
registration) record the resolved organization here; a SQLAlchemy engine
event then sets the `app.organization_id` GUC at the start of every
Postgres transaction so the RLS policies from migration 0004 apply.
On SQLite (tests) and the in-memory backend this is a no-op.
"""

from __future__ import annotations

from contextvars import ContextVar
from uuid import UUID

current_organization_id: ContextVar[str | None] = ContextVar(
    "current_organization_id", default=None
)


def set_current_organization(organization_id: UUID | str | None) -> None:
    current_organization_id.set(str(organization_id) if organization_id else None)
