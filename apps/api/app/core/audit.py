from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class AuditEvent:
    action: str
    organization_id: UUID
    actor_id: UUID | None = None
    resource_type: str | None = None
    resource_id: UUID | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class AuditLogger:
    async def record(self, event: AuditEvent) -> None:
        logger.info(
            "audit.event",
            extra={
                "_action": event.action,
                "_organization_id": str(event.organization_id),
                "_actor_id": str(event.actor_id) if event.actor_id else None,
                "_resource_type": event.resource_type,
                "_resource_id": str(event.resource_id) if event.resource_id else None,
                "_metadata": event.metadata,
                "_occurred_at": event.occurred_at.isoformat(),
            },
        )


audit_logger = AuditLogger()
