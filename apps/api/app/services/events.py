from uuid import UUID

from app.core.security import ApiPrincipal
from app.schemas.domain import EventIngestRequest, EventIngestResponse
from app.services.store import DemoStore, demo_store


class EventIngestionService:
    def __init__(self, store: DemoStore = demo_store) -> None:
        self.store = store
        self._idempotency_cache: dict[tuple[UUID, str], list[UUID]] = {}

    async def ingest(
        self,
        payload: EventIngestRequest,
        principal: ApiPrincipal,
        idempotency_key: str | None = None,
    ) -> EventIngestResponse:
        effective_key = idempotency_key or payload.idempotency_key
        if effective_key:
            cache_key = (principal.organization_id, effective_key)
            if cache_key in self._idempotency_cache:
                return EventIngestResponse(
                    accepted=0,
                    duplicate=True,
                    idempotency_key=effective_key,
                    event_ids=self._idempotency_cache[cache_key],
                )

        event_ids: list[UUID] = []
        for event in payload.events:
            item = self.store.create(
                "events",
                {
                    **event.model_dump(),
                    "source": payload.source,
                    "idempotency_key": effective_key,
                },
                organization_id=principal.organization_id,
            )
            event_ids.append(item["id"])

        if effective_key:
            self._idempotency_cache[(principal.organization_id, effective_key)] = event_ids

        return EventIngestResponse(
            accepted=len(event_ids),
            duplicate=False,
            idempotency_key=effective_key,
            event_ids=event_ids,
        )


event_ingestion_service = EventIngestionService()
