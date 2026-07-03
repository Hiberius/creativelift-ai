from __future__ import annotations

import json
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import PaginationDep, PrincipalDep, RateLimitDep
from app.api.v1.endpoints._helpers import collection, response, to_payload
from app.core.errors import ApiError
from app.core.security import ApiPrincipal
from app.schemas.common import ApiResponse, CollectionResponse
from app.schemas.domain import ConnectorCreate, ConnectorRead, ConnectorSyncRequest, ConnectorSyncResponse
from app.services.connector_sync import (
    get_or_create_connector_import_treatment,
    load_adapter,
    normalized_records_to_events,
)
from app.services.core_repositories import core_repository
from app.services.event_quality import capture_event_quality_snapshot
from app.services.resources import resource_service

router = APIRouter(prefix="/connectors", dependencies=[RateLimitDep])

_EVENTS_WRITE_SCOPE = "events:write"


def _require_events_write(principal: ApiPrincipal) -> None:
    if _EVENTS_WRITE_SCOPE not in principal.scopes and "admin:demo" not in principal.scopes:
        raise ApiError(403, "forbidden", f"API key is missing the required scope: {_EVENTS_WRITE_SCOPE}")


def _parse_connector_id(connector_id: str) -> UUID:
    try:
        return UUID(connector_id)
    except ValueError as exc:
        raise ApiError(400, "invalid_connector_id", "connector_id must be a valid UUID") from exc


def _sync_idempotency_key(connector_id: str, raw_records: list[dict[str, Any]]) -> str | None:
    """Derive a stable idempotency key from the connector and the exact set of
    raw records being synced, so replaying the same sync request dedupes
    instead of double-ingesting.
    """
    if not raw_records:
        return None
    canonical = json.dumps(raw_records, sort_keys=True, default=str)
    digest = sha256(canonical.encode("utf-8")).hexdigest()
    return f"connector-sync:{connector_id}:{digest}"


@router.post("", response_model=ApiResponse[ConnectorRead], status_code=status.HTTP_201_CREATED)
async def create_connector(principal: PrincipalDep, payload: ConnectorCreate) -> dict[str, object]:
    item = resource_service.create(
        "connectors",
        {**to_payload(payload), "status": "disconnected", "last_sync_at": None},
        principal.organization_id,
    )
    return response(item)


@router.get("", response_model=CollectionResponse[ConnectorRead])
async def list_connectors(principal: PrincipalDep, pagination: PaginationDep) -> dict[str, object]:
    items, total = resource_service.list(
        "connectors",
        principal.organization_id,
        pagination.limit,
        pagination.offset,
    )
    return collection(items, total, pagination)


@router.post("/{connector_id}/sync", response_model=ApiResponse[ConnectorSyncResponse])
async def sync_connector(
    principal: PrincipalDep,
    connector_id: str,
    payload: ConnectorSyncRequest,
) -> dict[str, object]:
    """Sync a connector.

    Push mode (default when ``events`` is supplied): raw provider payloads are
    normalized via the connector's adapter and ingested.
    Pull mode (``events`` omitted): the connector's adapter fetches records
    itself using the connector's stored config. Only providers whose adapter
    implements ``pull`` support this (currently PostHog).
    """
    _require_events_write(principal)

    connector_uuid = _parse_connector_id(connector_id)
    connector = resource_service.get("connectors", connector_uuid, principal.organization_id)
    if connector is None:
        raise ApiError(404, "connector_not_found", f"No connector found with id {connector_id}")

    provider = connector["provider"]
    adapter = load_adapter(provider, mapping=payload.mapping)

    if payload.events is not None:
        mode = "push"
        raw_records = payload.events
    else:
        mode = "pull"
        try:
            raw_records = adapter.pull(connector.get("config", {}), since=payload.since, max_events=payload.max_events)
        except NotImplementedError as exc:
            raise ApiError(400, "connector_pull_unsupported", str(exc)) from exc

    normalized_records = [adapter.normalize(raw_record) for raw_record in raw_records]
    creative_treatment_id = get_or_create_connector_import_treatment(
        core_repository, principal.organization_id, provider
    )
    batch = normalized_records_to_events(normalized_records, creative_treatment_id)

    idempotency_key = _sync_idempotency_key(connector_id, raw_records)
    accepted, deduplicated = core_repository.ingest_events(batch.events, principal.organization_id, idempotency_key)
    if accepted > 0:
        capture_event_quality_snapshot(core_repository, principal.organization_id)

    resource_service.update(
        "connectors",
        connector_uuid,
        {"status": "connected", "last_sync_at": datetime.now(UTC)},
        principal.organization_id,
    )

    return response(
        to_payload(
            ConnectorSyncResponse(
                accepted=accepted,
                deduplicated=deduplicated,
                skipped=batch.skipped,
                provider=provider,
                mode=mode,
            )
        )
    )
