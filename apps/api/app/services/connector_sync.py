"""Loads connector adapters from ``connectors/<provider>/src/adapter.py`` and
turns their normalized records into ingestable events.

Connectors live outside the ``apps/api`` package (see ``connectors/`` at the
repo root) and are not installed as a Python package, so adapters are loaded
by file path with :mod:`importlib`, mirroring the pattern already used by the
connector contract tests (``connectors/*/tests/test_contract.py``).
"""

from __future__ import annotations

import importlib.util
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any
from uuid import UUID

from app.core.errors import ApiError
from app.schemas.common import EventIn, EventName

CONNECTOR_IMPORT_TREATMENT_NAME = "Connector Import"

# Adapter class name per provider slug, matching connectors/<provider>/src/adapter.py.
_ADAPTER_CLASS_NAMES: dict[str, str] = {
    "google-ads": "GoogleAdsMetadataAdapter",
    "meta-ads": "MetaAdsMetadataAdapter",
    "hubspot": "HubSpotAdapter",
    "posthog": "PostHogAdapter",
    "rudder": "RudderAdapter",
    "snowplow": "SnowplowAdapter",
    "webhook-generic": "GenericWebhookAdapter",
}

# Providers may be referenced with either hyphens or underscores; normalize to
# the on-disk hyphenated directory name used under connectors/.
_PROVIDER_ALIASES: dict[str, str] = {
    "google_ads": "google-ads",
    "meta_ads": "meta-ads",
    "webhook_generic": "webhook-generic",
}

_EVENT_NAME_ALIASES: dict[str, EventName] = {
    "page_view": EventName.impression,
    "pageview": EventName.impression,
    "view": EventName.impression,
    "click": EventName.click,
    "session_start": EventName.session_start,
    "signup": EventName.signup,
    "sign_up": EventName.signup,
    "lead": EventName.lead,
    "purchase": EventName.purchase,
    "order_completed": EventName.purchase,
    "revenue": EventName.revenue,
}


class ConnectorSyncError(ApiError):
    """Raised for connector-sync-specific failures, mapped to a 4xx response."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(status_code, code, message)


def _repo_root() -> Path:
    """Walk up from this file until a directory containing ``connectors/`` is found."""
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / "connectors").is_dir():
            return candidate
    raise ConnectorSyncError(
        500,
        "connectors_not_found",
        "Could not locate the connectors/ directory relative to the API package. "
        "This deployment likely does not bundle the connectors/ source tree.",
    )


def normalize_provider_slug(provider: str) -> str:
    slug = provider.strip().lower()
    slug = _PROVIDER_ALIASES.get(slug, slug)
    slug = slug.replace("_", "-")
    return slug


@lru_cache(maxsize=None)
def _load_adapter_module(provider_slug: str) -> ModuleType:
    adapter_path = _repo_root() / "connectors" / provider_slug / "src" / "adapter.py"
    if not adapter_path.is_file():
        raise ConnectorSyncError(
            404,
            "connector_provider_not_found",
            f"No adapter found for provider '{provider_slug}' at {adapter_path}",
        )
    module_name = f"connectors.{provider_slug.replace('-', '_')}.adapter"
    spec = importlib.util.spec_from_file_location(module_name, adapter_path)
    if spec is None or spec.loader is None:
        raise ConnectorSyncError(
            500,
            "connector_adapter_load_failed",
            f"Could not load adapter module for provider '{provider_slug}'",
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_adapter(provider: str, mapping: dict[str, Any] | None = None) -> Any:
    """Instantiate the adapter class for ``provider``.

    ``mapping`` is forwarded to adapters that require constructor arguments
    (currently only ``webhook-generic``, which needs a field mapping).
    """
    provider_slug = normalize_provider_slug(provider)
    class_name = _ADAPTER_CLASS_NAMES.get(provider_slug)
    if class_name is None:
        raise ConnectorSyncError(
            400,
            "unknown_connector_provider",
            f"Unknown connector provider '{provider}'. Known providers: "
            f"{sorted(_ADAPTER_CLASS_NAMES)}",
        )
    module = _load_adapter_module(provider_slug)
    adapter_class = getattr(module, class_name, None)
    if adapter_class is None:
        raise ConnectorSyncError(
            500,
            "connector_adapter_load_failed",
            f"Adapter module for '{provider_slug}' does not define {class_name}",
        )
    if provider_slug == "webhook-generic":
        return adapter_class(mapping or {})
    return adapter_class()


def _coerce_event_name(raw_name: Any) -> EventName:
    if raw_name is None:
        return EventName.custom_conversion
    text = str(raw_name).strip().lower()
    text = re.sub(r"[\s-]+", "_", text)
    if text in EventName.__members__:
        return EventName(text)
    if text in _EVENT_NAME_ALIASES:
        return _EVENT_NAME_ALIASES[text]
    return EventName.custom_conversion


def _coerce_timestamp(raw_timestamp: Any) -> datetime:
    if isinstance(raw_timestamp, datetime):
        return raw_timestamp if raw_timestamp.tzinfo else raw_timestamp.replace(tzinfo=UTC)
    if isinstance(raw_timestamp, str) and raw_timestamp:
        text = raw_timestamp.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return datetime.now(UTC)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    return datetime.now(UTC)


@dataclass(frozen=True)
class NormalizedBatch:
    events: list[EventIn]
    skipped: int


def normalized_records_to_events(
    normalized_records: list[dict[str, Any]],
    creative_treatment_id: UUID,
) -> NormalizedBatch:
    """Map connector-normalized records (per connectors/shared-contract.md) onto
    :class:`EventIn`, the schema the core ingest pipeline accepts.

    Records that cannot be mapped to a valid event (missing both an
    anonymous/user identity) are dropped and counted as ``skipped`` rather than
    raising, so one malformed record does not fail an entire sync batch.
    """
    events: list[EventIn] = []
    skipped = 0
    for record in normalized_records:
        payload = record.get("payload") if isinstance(record.get("payload"), dict) else {}
        anonymous_id = payload.get("anonymous_id") or record.get("anonymous_id")
        user_id = payload.get("user_id") or record.get("user_id")
        if not anonymous_id and not user_id:
            # Fall back to the record's external_id as an anonymous identity so a
            # single connector record still produces a countable event; only drop
            # records with no identity signal at all.
            external_id = record.get("external_id")
            if external_id:
                anonymous_id = f"{record.get('source', 'connector')}:{external_id}"
            else:
                skipped += 1
                continue
        event_name_source = payload.get("event_name") or record.get("record_type")
        try:
            event = EventIn(
                event_name=_coerce_event_name(event_name_source),
                timestamp=_coerce_timestamp(record.get("occurred_at")),
                anonymous_id=str(anonymous_id) if anonymous_id else None,
                user_id=str(user_id) if user_id else None,
                creative_treatment_id=creative_treatment_id,
                channel=record.get("source"),
                properties=payload if isinstance(payload, dict) else {},
            )
        except ValueError:
            skipped += 1
            continue
        events.append(event)
    return NormalizedBatch(events=events, skipped=skipped)


def get_or_create_connector_import_treatment(repository: Any, organization_id: UUID, provider: str) -> UUID:
    """Return the placeholder creative treatment used to satisfy the required
    ``Event.creative_treatment_id`` foreign key for connector-sourced events
    that are not tied to a specific CreativeLift creative treatment.

    One placeholder is reused per organization+provider rather than created on
    every sync call.
    """
    from app.schemas.common import CreativeTreatmentCreate

    treatment_name = f"{CONNECTOR_IMPORT_TREATMENT_NAME}: {provider}"
    existing = repository.list_creative_treatments(organization_id)
    for treatment in existing:
        if treatment.name == treatment_name:
            return treatment.id
    created = repository.create_creative_treatment(
        CreativeTreatmentCreate(
            name=treatment_name,
            objective="connector_import",
            target_audience="n/a",
            channel=provider,
        ),
        organization_id,
    )
    return created.id
