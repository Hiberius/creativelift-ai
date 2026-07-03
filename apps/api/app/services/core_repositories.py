from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Callable, Protocol
from uuid import UUID, uuid4

from app.core.config import get_settings
from app.core.security import generate_api_key
from app.schemas.common import (
    ApprovalStatus,
    ApiKeyCreate,
    ApiKeyRead,
    AuditLogRead,
    BanditCreate,
    BanditUpdate,
    BrandPackCreate,
    BrandPackRead,
    BriefCreate,
    BriefRead,
    ClaimEvidenceCreate,
    ClaimEvidenceRead,
    CreativeTreatmentCreate,
    CreativeTreatmentRead,
    EventIn,
    EventQualitySnapshotRead,
    ExperimentCreate,
    ExperimentRead,
    ExperimentStatus,
    ExperimentVariantInput,
    OrganizationCreate,
    OrganizationRead,
    RunCreate,
    RunRead,
)
from app.services.demo_store import DemoStore, store as demo_store

VALID_CORE_REPOSITORY_BACKENDS = {"memory", "sqlalchemy"}


@dataclass(frozen=True)
class UserAuthRecord:
    id: UUID
    email: str
    name: str
    hashed_password: str | None


@dataclass(frozen=True)
class UserSessionRecord:
    user_id: UUID
    organization_id: UUID
    expires_at: datetime


@dataclass(frozen=True)
class MeasurementSummaryStats:
    total_events: int
    conversion_events: int
    unique_actors: int
    revenue: float
    last_event_at: datetime | None
    running_experiments: int
    pending_review_creatives: int
    approved_creatives: int


class CoreRepository(Protocol):
    def create_organization(self, payload: OrganizationCreate) -> OrganizationRead:
        raise NotImplementedError

    def get_organization(self, organization_id: UUID) -> OrganizationRead | None:
        raise NotImplementedError

    def latest_organization_id(self) -> UUID | None:
        raise NotImplementedError

    def create_user(self, email: str, name: str, hashed_password: str) -> UserAuthRecord:
        raise NotImplementedError

    def get_user_by_email(self, email: str) -> UserAuthRecord | None:
        raise NotImplementedError

    def get_user(self, user_id: UUID) -> UserAuthRecord | None:
        raise NotImplementedError

    def create_membership(self, user_id: UUID, organization_id: UUID, role: str) -> None:
        raise NotImplementedError

    def get_membership_role(self, user_id: UUID, organization_id: UUID) -> str | None:
        raise NotImplementedError

    def get_primary_membership(self, user_id: UUID) -> tuple[UUID, str] | None:
        raise NotImplementedError

    def create_user_session(
        self, user_id: UUID, organization_id: UUID, token_hash: str, expires_at: datetime
    ) -> None:
        raise NotImplementedError

    def get_active_user_session(self, token_hash: str) -> UserSessionRecord | None:
        raise NotImplementedError

    def revoke_user_session(self, token_hash: str) -> bool:
        raise NotImplementedError

    def record_audit(
        self,
        action: str,
        target_type: str,
        organization_id: UUID,
        target_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLogRead:
        raise NotImplementedError

    def list_audit_logs(self, organization_id: UUID | None = None, limit: int = 100) -> list[AuditLogRead]:
        raise NotImplementedError

    def create_api_key(self, payload: ApiKeyCreate, organization_id: UUID) -> ApiKeyRead:
        raise NotImplementedError

    def list_api_keys(self, organization_id: UUID | None = None) -> list[ApiKeyRead]:
        raise NotImplementedError

    def delete_api_key(self, api_key_id: UUID, organization_id: UUID | None = None) -> bool:
        raise NotImplementedError

    def get_api_key_by_hash(self, hashed_key: str) -> ApiKeyRead | None:
        raise NotImplementedError

    def create_brand_pack(self, payload: BrandPackCreate, organization_id: UUID) -> BrandPackRead:
        raise NotImplementedError

    def list_brand_packs(self, organization_id: UUID | None = None) -> list[BrandPackRead]:
        raise NotImplementedError

    def get_brand_pack(self, brand_pack_id: UUID, organization_id: UUID | None = None) -> BrandPackRead | None:
        raise NotImplementedError

    def create_brief(self, payload: BriefCreate, organization_id: UUID) -> BriefRead:
        raise NotImplementedError

    def list_briefs(self, organization_id: UUID | None = None) -> list[BriefRead]:
        raise NotImplementedError

    def get_brief(self, brief_id: UUID, organization_id: UUID | None = None) -> BriefRead | None:
        raise NotImplementedError

    def create_creative_treatment(
        self, payload: CreativeTreatmentCreate, organization_id: UUID
    ) -> CreativeTreatmentRead:
        raise NotImplementedError

    def list_creative_treatments(
        self,
        organization_id: UUID | None = None,
        status_filter: ApprovalStatus | None = None,
    ) -> list[CreativeTreatmentRead]:
        raise NotImplementedError

    def get_creative_treatment(
        self, creative_treatment_id: UUID, organization_id: UUID | None = None
    ) -> CreativeTreatmentRead | None:
        raise NotImplementedError

    def update_creative_treatment(
        self, creative_treatment: CreativeTreatmentRead, organization_id: UUID | None = None
    ) -> CreativeTreatmentRead | None:
        raise NotImplementedError

    def create_experiment(self, payload: ExperimentCreate, organization_id: UUID) -> ExperimentRead:
        raise NotImplementedError

    def list_experiments(self, organization_id: UUID | None = None) -> list[ExperimentRead]:
        raise NotImplementedError

    def get_experiment(self, experiment_id: UUID, organization_id: UUID | None = None) -> ExperimentRead | None:
        raise NotImplementedError

    def update_experiment(self, experiment: ExperimentRead, organization_id: UUID | None = None) -> ExperimentRead | None:
        raise NotImplementedError

    def create_bandit(self, payload: BanditCreate, organization_id: UUID) -> dict[str, Any]:
        raise NotImplementedError

    def get_bandit(self, bandit_id: UUID, organization_id: UUID | None = None) -> dict[str, Any] | None:
        raise NotImplementedError

    def update_bandit_arm(
        self, bandit_id: UUID, payload: BanditUpdate, organization_id: UUID | None = None
    ) -> dict[str, Any] | None:
        raise NotImplementedError

    def create_uplift_run(self, payload: RunCreate, organization_id: UUID) -> RunRead:
        raise NotImplementedError

    def get_uplift_run(self, run_id: UUID, organization_id: UUID | None = None) -> RunRead | None:
        raise NotImplementedError

    def create_mmm_run(self, payload: RunCreate, organization_id: UUID) -> RunRead:
        raise NotImplementedError

    def get_mmm_run(self, run_id: UUID, organization_id: UUID | None = None) -> RunRead | None:
        raise NotImplementedError

    def create_claim_evidence(self, payload: ClaimEvidenceCreate, organization_id: UUID) -> ClaimEvidenceRead:
        raise NotImplementedError

    def list_claim_evidence(self, organization_id: UUID | None = None) -> list[ClaimEvidenceRead]:
        raise NotImplementedError

    def ingest_events(
        self,
        events: list[EventIn],
        organization_id: UUID,
        idempotency_key: str | None = None,
    ) -> tuple[int, int]:
        raise NotImplementedError

    def list_events(
        self,
        organization_id: UUID | None = None,
        limit: int | None = 25,
        offset: int = 0,
    ) -> list[EventIn]:
        raise NotImplementedError

    def record_event_quality_snapshot(
        self,
        summary: dict[str, Any],
        organization_id: UUID,
    ) -> EventQualitySnapshotRead:
        raise NotImplementedError

    def list_event_quality_snapshots(
        self,
        organization_id: UUID | None = None,
        limit: int = 30,
    ) -> list[EventQualitySnapshotRead]:
        raise NotImplementedError

    def measurement_summary_stats(
        self,
        organization_id: UUID,
        since: datetime | None = None,
    ) -> MeasurementSummaryStats:
        raise NotImplementedError

    def compute_event_health(self, organization_id: UUID) -> dict[str, Any]:
        raise NotImplementedError


class InMemoryCoreRepository:
    def __init__(self, store: DemoStore = demo_store) -> None:
        self.store = store

    def create_organization(self, payload: OrganizationCreate) -> OrganizationRead:
        item = OrganizationRead(id=uuid4(), **payload.model_dump())
        self.store.organizations[item.id] = item
        self.store.organization = item
        return item

    def get_organization(self, organization_id: UUID) -> OrganizationRead | None:
        return self.store.organizations.get(organization_id)

    def latest_organization_id(self) -> UUID | None:
        latest = None
        for organization_id in self.store.organizations:
            latest = organization_id
        return latest

    def create_user(self, email: str, name: str, hashed_password: str) -> UserAuthRecord:
        normalized = email.strip().lower()
        if normalized in self.store.users_by_email:
            raise ValueError("email already registered")
        record = UserAuthRecord(id=uuid4(), email=normalized, name=name, hashed_password=hashed_password)
        self.store.users_by_email[normalized] = record
        self.store.users_by_id[record.id] = record
        return record

    def get_user_by_email(self, email: str) -> UserAuthRecord | None:
        return self.store.users_by_email.get(email.strip().lower())

    def get_user(self, user_id: UUID) -> UserAuthRecord | None:
        return self.store.users_by_id.get(user_id)

    def create_membership(self, user_id: UUID, organization_id: UUID, role: str) -> None:
        self.store.memberships.append((user_id, organization_id, role))

    def get_membership_role(self, user_id: UUID, organization_id: UUID) -> str | None:
        for member_id, member_org, role in self.store.memberships:
            if member_id == user_id and member_org == organization_id:
                return role
        return None

    def get_primary_membership(self, user_id: UUID) -> tuple[UUID, str] | None:
        for member_id, member_org, role in self.store.memberships:
            if member_id == user_id:
                return member_org, role
        return None

    def create_user_session(
        self, user_id: UUID, organization_id: UUID, token_hash: str, expires_at: datetime
    ) -> None:
        self.store.user_sessions[token_hash] = UserSessionRecord(
            user_id=user_id, organization_id=organization_id, expires_at=expires_at
        )

    def get_active_user_session(self, token_hash: str) -> UserSessionRecord | None:
        record = self.store.user_sessions.get(token_hash)
        if record is None:
            return None
        expires_at = record.expires_at if record.expires_at.tzinfo else record.expires_at.replace(tzinfo=UTC)
        if expires_at <= datetime.now(UTC):
            return None
        return record

    def revoke_user_session(self, token_hash: str) -> bool:
        return self.store.user_sessions.pop(token_hash, None) is not None

    def record_audit(
        self,
        action: str,
        target_type: str,
        organization_id: UUID,
        target_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLogRead:
        item = AuditLogRead(
            id=uuid4(),
            organization_id=organization_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            metadata=metadata or {},
            created_at=datetime.now(UTC),
        )
        self.store.audit_logs.append(item)
        return item

    def list_audit_logs(self, organization_id: UUID | None = None, limit: int = 100) -> list[AuditLogRead]:
        items = list(reversed(self.store.audit_logs))
        if organization_id is not None:
            items = [item for item in items if item.organization_id == organization_id]
        return items[:limit]

    def create_api_key(self, payload: ApiKeyCreate, organization_id: UUID) -> ApiKeyRead:
        raw, prefix, hashed = generate_api_key()
        item = ApiKeyRead(
            id=uuid4(),
            organization_id=organization_id,
            name=payload.name,
            prefix=prefix,
            scopes=payload.scopes,
            raw_key=raw,
            created_at=datetime.now(UTC),
        )
        self.store.api_keys[item.id] = item
        self.store.api_key_hashes[hashed] = item.id
        return item

    def list_api_keys(self, organization_id: UUID | None = None) -> list[ApiKeyRead]:
        items = list(self.store.api_keys.values())
        if organization_id is not None:
            items = [item for item in items if item.organization_id == organization_id]
        return [item.model_copy(update={"raw_key": None}) for item in items]

    def delete_api_key(self, api_key_id: UUID, organization_id: UUID | None = None) -> bool:
        item = self.store.api_keys.get(api_key_id)
        if item is None:
            return False
        if organization_id is not None and item.organization_id != organization_id:
            return False
        self.store.api_keys.pop(api_key_id)
        self.store.api_key_hashes = {
            hashed: key_id
            for hashed, key_id in self.store.api_key_hashes.items()
            if key_id != api_key_id
        }
        return True

    def get_api_key_by_hash(self, hashed_key: str) -> ApiKeyRead | None:
        api_key_id = self.store.api_key_hashes.get(hashed_key)
        if api_key_id is None:
            return None
        item = self.store.api_keys.get(api_key_id)
        if item is None:
            return None
        return item.model_copy(update={"raw_key": None})

    def create_brand_pack(self, payload: BrandPackCreate, organization_id: UUID) -> BrandPackRead:
        item = BrandPackRead(id=uuid4(), organization_id=organization_id, **payload.model_dump())
        self.store.brand_packs[item.id] = item
        return item

    def list_brand_packs(self, organization_id: UUID | None = None) -> list[BrandPackRead]:
        items = list(self.store.brand_packs.values())
        if organization_id is not None:
            items = [item for item in items if item.organization_id == organization_id]
        return items

    def get_brand_pack(self, brand_pack_id: UUID, organization_id: UUID | None = None) -> BrandPackRead | None:
        item = self.store.brand_packs.get(brand_pack_id)
        if item is None:
            return None
        if organization_id is not None and item.organization_id != organization_id:
            return None
        return item

    def create_brief(self, payload: BriefCreate, organization_id: UUID) -> BriefRead:
        item = BriefRead(id=uuid4(), organization_id=organization_id, status="draft", **payload.model_dump())
        self.store.briefs[item.id] = item
        return item

    def list_briefs(self, organization_id: UUID | None = None) -> list[BriefRead]:
        items = list(self.store.briefs.values())
        if organization_id is not None:
            items = [item for item in items if item.organization_id == organization_id]
        return items

    def get_brief(self, brief_id: UUID, organization_id: UUID | None = None) -> BriefRead | None:
        item = self.store.briefs.get(brief_id)
        if item is None:
            return None
        if organization_id is not None and item.organization_id != organization_id:
            return None
        return item

    def create_creative_treatment(
        self, payload: CreativeTreatmentCreate, organization_id: UUID
    ) -> CreativeTreatmentRead:
        item = CreativeTreatmentRead(
            id=uuid4(),
            organization_id=organization_id,
            approval_status=ApprovalStatus.draft,
            compliance_status="pending_review",
            metrics_snapshot={},
            **payload.model_dump(),
        )
        self.store.creatives[item.id] = item
        return item

    def list_creative_treatments(
        self,
        organization_id: UUID | None = None,
        status_filter: ApprovalStatus | None = None,
    ) -> list[CreativeTreatmentRead]:
        items = list(self.store.creatives.values())
        if organization_id is not None:
            items = [item for item in items if item.organization_id == organization_id]
        if status_filter:
            items = [item for item in items if item.approval_status == status_filter]
        return items

    def get_creative_treatment(
        self, creative_treatment_id: UUID, organization_id: UUID | None = None
    ) -> CreativeTreatmentRead | None:
        item = self.store.creatives.get(creative_treatment_id)
        if item is None:
            return None
        if organization_id is not None and item.organization_id != organization_id:
            return None
        return item

    def update_creative_treatment(
        self, creative_treatment: CreativeTreatmentRead, organization_id: UUID | None = None
    ) -> CreativeTreatmentRead | None:
        if organization_id is not None and creative_treatment.organization_id != organization_id:
            return None
        if creative_treatment.id not in self.store.creatives:
            return None
        self.store.creatives[creative_treatment.id] = creative_treatment
        return creative_treatment

    def create_experiment(self, payload: ExperimentCreate, organization_id: UUID) -> ExperimentRead:
        item = ExperimentRead(
            id=uuid4(),
            organization_id=organization_id,
            status=ExperimentStatus.draft,
            starts_at=None,
            ends_at=None,
            **payload.model_dump(),
        )
        self.store.experiments[item.id] = item
        return item

    def list_experiments(self, organization_id: UUID | None = None) -> list[ExperimentRead]:
        items = list(self.store.experiments.values())
        if organization_id is not None:
            items = [item for item in items if item.organization_id == organization_id]
        return items

    def get_experiment(self, experiment_id: UUID, organization_id: UUID | None = None) -> ExperimentRead | None:
        item = self.store.experiments.get(experiment_id)
        if item is None:
            return None
        if organization_id is not None and item.organization_id != organization_id:
            return None
        return item

    def update_experiment(self, experiment: ExperimentRead, organization_id: UUID | None = None) -> ExperimentRead | None:
        if organization_id is not None and experiment.organization_id != organization_id:
            return None
        if experiment.id not in self.store.experiments:
            return None
        self.store.experiments[experiment.id] = experiment
        return experiment

    def create_bandit(self, payload: BanditCreate, organization_id: UUID) -> dict[str, Any]:
        bandit_id = uuid4()
        item = {
            "id": bandit_id,
            "organization_id": organization_id,
            "name": payload.name,
            "arms": {arm: {"alpha": 1.0, "beta": 1.0} for arm in payload.arms},
        }
        self.store.bandits[bandit_id] = item
        return item

    def get_bandit(self, bandit_id: UUID, organization_id: UUID | None = None) -> dict[str, Any] | None:
        item = self.store.bandits.get(bandit_id)
        if item is None:
            return None
        if organization_id is not None and item["organization_id"] != organization_id:
            return None
        return item

    def update_bandit_arm(
        self, bandit_id: UUID, payload: BanditUpdate, organization_id: UUID | None = None
    ) -> dict[str, Any] | None:
        item = self.get_bandit(bandit_id, organization_id)
        if item is None or payload.arm not in item["arms"]:
            return None
        if payload.success:
            item["arms"][payload.arm]["alpha"] += 1
        else:
            item["arms"][payload.arm]["beta"] += 1
        return item

    def create_uplift_run(self, payload: RunCreate, organization_id: UUID) -> RunRead:
        item = RunRead(
            id=uuid4(),
            organization_id=organization_id,
            status="completed_demo",
            model_type="two_model_baseline",
            config=payload.config,
            result={"auuc": None, "qini": None, "note": "Scaffold ready for EconML/CausalML adapters."},
        )
        self.store.runs[item.id] = item
        return item

    def get_uplift_run(self, run_id: UUID, organization_id: UUID | None = None) -> RunRead | None:
        item = self.store.runs.get(run_id)
        if item is None or item.model_type != "two_model_baseline":
            return None
        if organization_id is not None and item.organization_id != organization_id:
            return None
        return item

    def create_mmm_run(self, payload: RunCreate, organization_id: UUID) -> RunRead:
        item = RunRead(
            id=uuid4(),
            organization_id=organization_id,
            status="completed_demo",
            model_type="demo_linear_mmm",
            config=payload.config,
            result={
                "channels": {"paid_social": 0.42, "search": 0.31, "email": 0.12},
                "calibration_note": "Use incrementality tests as priors in future PyMC-Marketing/Meridian adapter.",
            },
        )
        self.store.runs[item.id] = item
        return item

    def get_mmm_run(self, run_id: UUID, organization_id: UUID | None = None) -> RunRead | None:
        item = self.store.runs.get(run_id)
        if item is None or item.model_type != "demo_linear_mmm":
            return None
        if organization_id is not None and item.organization_id != organization_id:
            return None
        return item

    def create_claim_evidence(self, payload: ClaimEvidenceCreate, organization_id: UUID) -> ClaimEvidenceRead:
        item = ClaimEvidenceRead(
            id=uuid4(),
            organization_id=organization_id,
            created_at=datetime.now(UTC),
            **payload.model_dump(),
        )
        self.store.claim_evidence[item.id] = item
        return item

    def list_claim_evidence(self, organization_id: UUID | None = None) -> list[ClaimEvidenceRead]:
        items = list(self.store.claim_evidence.values())
        if organization_id is not None:
            items = [item for item in items if item.organization_id == organization_id]
        return items

    def ingest_events(
        self,
        events: list[EventIn],
        organization_id: UUID,
        idempotency_key: str | None = None,
    ) -> tuple[int, int]:
        if idempotency_key:
            scoped_idempotency_key = f"{organization_id}:{idempotency_key}"
            if scoped_idempotency_key in self.store.idempotency_keys:
                return 0, len(events)
            self.store.idempotency_keys.add(scoped_idempotency_key)
        self.store.events.extend(events)
        self.store.event_organization_ids.extend([organization_id] * len(events))
        return len(events), 0

    def list_events(
        self,
        organization_id: UUID | None = None,
        limit: int | None = 25,
        offset: int = 0,
    ) -> list[EventIn]:
        pairs = list(zip(self.store.events, self.store.event_organization_ids, strict=False))
        if organization_id is not None:
            pairs = [pair for pair in pairs if pair[1] == organization_id]
        items = [event for event, _org_id in reversed(pairs)]
        if limit is None:
            return items[offset:]
        return items[offset : offset + limit]

    def record_event_quality_snapshot(
        self,
        summary: dict[str, Any],
        organization_id: UUID,
    ) -> EventQualitySnapshotRead:
        item = EventQualitySnapshotRead(
            id=uuid4(),
            organization_id=organization_id,
            captured_at=datetime.now(UTC),
            total_events=summary.get("total_events", 0),
            unique_actors=summary.get("unique_actors", 0),
            events_with_experiment=summary.get("events_with_experiment", 0),
            events_with_variant=summary.get("events_with_variant", 0),
            conversion_events=summary.get("conversion_events", 0),
            revenue=summary.get("revenue", 0.0),
            experiment_coverage=summary.get("experiment_coverage", 0.0),
            variant_coverage=summary.get("variant_coverage", 0.0),
            revenue_coverage=summary.get("revenue_coverage", 0.0),
            quality_score=summary.get("quality_score", 0.0),
            warnings=list(summary.get("warnings", [])),
        )
        self.store.event_quality_snapshots.append(item)
        return item

    def list_event_quality_snapshots(
        self,
        organization_id: UUID | None = None,
        limit: int = 30,
    ) -> list[EventQualitySnapshotRead]:
        items = list(reversed(self.store.event_quality_snapshots))
        if organization_id is not None:
            items = [item for item in items if item.organization_id == organization_id]
        return items[:limit]

    def measurement_summary_stats(
        self,
        organization_id: UUID,
        since: datetime | None = None,
    ) -> MeasurementSummaryStats:
        from app.services.measurement import CONVERSION_EVENT_NAMES

        total_events = 0
        conversion_events = 0
        revenue = 0.0
        actors: set[str] = set()
        last_event_at: datetime | None = None
        pairs = zip(self.store.events, self.store.event_organization_ids, strict=False)
        for event, event_organization_id in pairs:
            if event_organization_id != organization_id:
                continue
            if since is not None and event.timestamp < since:
                continue
            total_events += 1
            if last_event_at is None or event.timestamp > last_event_at:
                last_event_at = event.timestamp
            actor = event.user_id or event.anonymous_id
            if actor:
                actors.add(str(actor))
            event_name = str(getattr(event.event_name, "value", event.event_name))
            if event_name in CONVERSION_EVENT_NAMES:
                conversion_events += 1
                revenue += float(event.value or 0.0)

        running_experiments = sum(
            1
            for item in self.store.experiments.values()
            if item.organization_id == organization_id and item.status == ExperimentStatus.running
        )
        pending_review_creatives = 0
        approved_creatives = 0
        for item in self.store.creatives.values():
            if item.organization_id != organization_id:
                continue
            if item.approval_status in (ApprovalStatus.draft, ApprovalStatus.pending_review):
                pending_review_creatives += 1
            elif item.approval_status == ApprovalStatus.approved:
                approved_creatives += 1

        return MeasurementSummaryStats(
            total_events=total_events,
            conversion_events=conversion_events,
            unique_actors=len(actors),
            revenue=revenue,
            last_event_at=last_event_at,
            running_experiments=running_experiments,
            pending_review_creatives=pending_review_creatives,
            approved_creatives=approved_creatives,
        )

    def compute_event_health(self, organization_id: UUID) -> dict[str, Any]:
        from app.services.event_quality import event_health_summary

        return event_health_summary(self.list_events(organization_id, limit=None))


class SQLAlchemyCoreRepository:
    def __init__(self, session_factory: Callable[[], Any]) -> None:
        self.session_factory = session_factory

    def create_organization(self, payload: OrganizationCreate) -> OrganizationRead:
        from app.db.models import Organization

        # Client-side timestamp: microsecond precision on every dialect, so
        # latest_organization_id() stays deterministic (SQLite CURRENT_TIMESTAMP
        # only has second precision).
        item = Organization(**payload.model_dump(), created_at=datetime.now(UTC))
        with self.session_factory() as session:
            session.add(item)
            session.commit()
            session.refresh(item)
            return self._organization_to_schema(item)

    def get_organization(self, organization_id: UUID) -> OrganizationRead | None:
        from sqlalchemy import select
        from app.db.models import Organization

        with self.session_factory() as session:
            item = session.scalar(select(Organization).where(Organization.id == organization_id))
            return self._organization_to_schema(item) if item is not None else None

    def latest_organization_id(self) -> UUID | None:
        from sqlalchemy import select
        from app.db.models import Organization

        with self.session_factory() as session:
            return session.scalar(
                select(Organization.id).order_by(Organization.created_at.desc()).limit(1)
            )

    def create_user(self, email: str, name: str, hashed_password: str) -> UserAuthRecord:
        from sqlalchemy.exc import IntegrityError

        from app.db.models import User

        item = User(email=email.strip().lower(), name=name, hashed_password=hashed_password)
        with self.session_factory() as session:
            session.add(item)
            try:
                session.commit()
            except IntegrityError as exc:
                session.rollback()
                raise ValueError("email already registered") from exc
            session.refresh(item)
            return UserAuthRecord(id=item.id, email=item.email, name=item.name, hashed_password=item.hashed_password)

    def get_user_by_email(self, email: str) -> UserAuthRecord | None:
        from sqlalchemy import select

        from app.db.models import User

        with self.session_factory() as session:
            item = session.scalar(select(User).where(User.email == email.strip().lower()))
            if item is None:
                return None
            return UserAuthRecord(id=item.id, email=item.email, name=item.name, hashed_password=item.hashed_password)

    def get_user(self, user_id: UUID) -> UserAuthRecord | None:
        from app.db.models import User

        with self.session_factory() as session:
            item = session.get(User, user_id)
            if item is None:
                return None
            return UserAuthRecord(id=item.id, email=item.email, name=item.name, hashed_password=item.hashed_password)

    def create_membership(self, user_id: UUID, organization_id: UUID, role: str) -> None:
        from app.db.models import Membership

        with self.session_factory() as session:
            session.add(Membership(user_id=user_id, organization_id=organization_id, role=role))
            session.commit()

    def get_membership_role(self, user_id: UUID, organization_id: UUID) -> str | None:
        from sqlalchemy import select

        from app.db.models import Membership

        with self.session_factory() as session:
            return session.scalar(
                select(Membership.role).where(
                    Membership.user_id == user_id,
                    Membership.organization_id == organization_id,
                )
            )

    def get_primary_membership(self, user_id: UUID) -> tuple[UUID, str] | None:
        from sqlalchemy import select

        from app.db.models import Membership

        with self.session_factory() as session:
            row = session.execute(
                select(Membership.organization_id, Membership.role)
                .where(Membership.user_id == user_id)
                .order_by(Membership.created_at.asc())
                .limit(1)
            ).first()
            return (row[0], row[1]) if row is not None else None

    def create_user_session(
        self, user_id: UUID, organization_id: UUID, token_hash: str, expires_at: datetime
    ) -> None:
        from app.db.models import UserSession

        with self.session_factory() as session:
            session.add(
                UserSession(
                    user_id=user_id,
                    organization_id=organization_id,
                    token_hash=token_hash,
                    expires_at=expires_at,
                )
            )
            session.commit()

    def get_active_user_session(self, token_hash: str) -> UserSessionRecord | None:
        from sqlalchemy import select

        from app.db.models import UserSession

        with self.session_factory() as session:
            item = session.scalar(
                select(UserSession).where(
                    UserSession.token_hash == token_hash,
                    UserSession.revoked_at.is_(None),
                )
            )
            if item is None:
                return None
            expires_at = item.expires_at if item.expires_at.tzinfo else item.expires_at.replace(tzinfo=UTC)
            if expires_at <= datetime.now(UTC):
                return None
            return UserSessionRecord(
                user_id=item.user_id, organization_id=item.organization_id, expires_at=expires_at
            )

    def revoke_user_session(self, token_hash: str) -> bool:
        from sqlalchemy import select

        from app.db.models import UserSession

        with self.session_factory() as session:
            item = session.scalar(select(UserSession).where(UserSession.token_hash == token_hash))
            if item is None or item.revoked_at is not None:
                return False
            item.revoked_at = datetime.now(UTC)
            session.commit()
            return True

    def record_audit(
        self,
        action: str,
        target_type: str,
        organization_id: UUID,
        target_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLogRead:
        from app.db.models import AuditLog

        item = AuditLog(
            organization_id=organization_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            metadata_=metadata or {},
        )
        with self.session_factory() as session:
            session.add(item)
            session.commit()
            session.refresh(item)
            return self._audit_log_to_schema(item)

    def list_audit_logs(self, organization_id: UUID | None = None, limit: int = 100) -> list[AuditLogRead]:
        from sqlalchemy import select
        from app.db.models import AuditLog

        statement = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        if organization_id is not None:
            statement = statement.where(AuditLog.organization_id == organization_id)
        with self.session_factory() as session:
            return [self._audit_log_to_schema(item) for item in session.scalars(statement).all()]

    def create_api_key(self, payload: ApiKeyCreate, organization_id: UUID) -> ApiKeyRead:
        from app.db.models import ApiKey

        raw, prefix, hashed = generate_api_key()
        item = ApiKey(
            organization_id=organization_id,
            name=payload.name,
            prefix=prefix,
            hashed_key=hashed,
            scopes=payload.scopes,
        )
        with self.session_factory() as session:
            session.add(item)
            session.commit()
            session.refresh(item)
            return self._api_key_to_schema(item, raw_key=raw)

    def list_api_keys(self, organization_id: UUID | None = None) -> list[ApiKeyRead]:
        from sqlalchemy import select
        from app.db.models import ApiKey

        statement = select(ApiKey).where(ApiKey.revoked_at.is_(None)).order_by(ApiKey.created_at.desc())
        if organization_id is not None:
            statement = statement.where(ApiKey.organization_id == organization_id)
        with self.session_factory() as session:
            return [self._api_key_to_schema(item, raw_key=None) for item in session.scalars(statement).all()]

    def delete_api_key(self, api_key_id: UUID, organization_id: UUID | None = None) -> bool:
        from sqlalchemy import select
        from app.db.models import ApiKey

        statement = select(ApiKey).where(ApiKey.id == api_key_id)
        if organization_id is not None:
            statement = statement.where(ApiKey.organization_id == organization_id)
        with self.session_factory() as session:
            item = session.scalar(statement)
            if item is None:
                return False
            item.revoked_at = datetime.now(UTC)
            session.commit()
            return True

    def get_api_key_by_hash(self, hashed_key: str) -> ApiKeyRead | None:
        from sqlalchemy import select
        from app.db.models import ApiKey

        statement = select(ApiKey).where(
            ApiKey.hashed_key == hashed_key,
            ApiKey.revoked_at.is_(None),
        )
        with self.session_factory() as session:
            item = session.scalar(statement)
            return self._api_key_to_schema(item, raw_key=None) if item is not None else None

    def create_brand_pack(self, payload: BrandPackCreate, organization_id: UUID) -> BrandPackRead:
        from app.db.models import BrandPack

        item = BrandPack(organization_id=organization_id, **payload.model_dump())
        with self.session_factory() as session:
            session.add(item)
            session.commit()
            session.refresh(item)
            return self._brand_pack_to_schema(item)

    def list_brand_packs(self, organization_id: UUID | None = None) -> list[BrandPackRead]:
        from sqlalchemy import select
        from app.db.models import BrandPack

        statement = select(BrandPack).order_by(BrandPack.created_at.desc())
        if organization_id is not None:
            statement = statement.where(BrandPack.organization_id == organization_id)
        with self.session_factory() as session:
            return [self._brand_pack_to_schema(item) for item in session.scalars(statement).all()]

    def get_brand_pack(self, brand_pack_id: UUID, organization_id: UUID | None = None) -> BrandPackRead | None:
        from sqlalchemy import select
        from app.db.models import BrandPack

        statement = select(BrandPack).where(BrandPack.id == brand_pack_id)
        if organization_id is not None:
            statement = statement.where(BrandPack.organization_id == organization_id)
        with self.session_factory() as session:
            item = session.scalar(statement)
            return self._brand_pack_to_schema(item) if item is not None else None

    def create_brief(self, payload: BriefCreate, organization_id: UUID) -> BriefRead:
        from app.db.models import Brief

        item = Brief(organization_id=organization_id, status="draft", **payload.model_dump())
        with self.session_factory() as session:
            session.add(item)
            session.commit()
            session.refresh(item)
            return self._brief_to_schema(item)

    def list_briefs(self, organization_id: UUID | None = None) -> list[BriefRead]:
        from sqlalchemy import select
        from app.db.models import Brief

        statement = select(Brief).order_by(Brief.created_at.desc())
        if organization_id is not None:
            statement = statement.where(Brief.organization_id == organization_id)
        with self.session_factory() as session:
            return [self._brief_to_schema(item) for item in session.scalars(statement).all()]

    def get_brief(self, brief_id: UUID, organization_id: UUID | None = None) -> BriefRead | None:
        from sqlalchemy import select
        from app.db.models import Brief

        statement = select(Brief).where(Brief.id == brief_id)
        if organization_id is not None:
            statement = statement.where(Brief.organization_id == organization_id)
        with self.session_factory() as session:
            item = session.scalar(statement)
            return self._brief_to_schema(item) if item is not None else None

    def create_creative_treatment(
        self, payload: CreativeTreatmentCreate, organization_id: UUID
    ) -> CreativeTreatmentRead:
        from app.db.models import CreativeTreatment

        data = payload.model_dump()
        body_copy = data.pop("body_copy")
        item = CreativeTreatment(
            organization_id=organization_id,
            approval_status=ApprovalStatus.draft.value,
            compliance_status="pending_review",
            metrics_snapshot={},
            copy=body_copy,
            **data,
        )
        with self.session_factory() as session:
            session.add(item)
            session.commit()
            session.refresh(item)
            return self._creative_treatment_to_schema(item)

    def list_creative_treatments(
        self,
        organization_id: UUID | None = None,
        status_filter: ApprovalStatus | None = None,
    ) -> list[CreativeTreatmentRead]:
        from sqlalchemy import select
        from app.db.models import CreativeTreatment

        statement = select(CreativeTreatment).order_by(CreativeTreatment.created_at.desc())
        if organization_id is not None:
            statement = statement.where(CreativeTreatment.organization_id == organization_id)
        if status_filter:
            statement = statement.where(CreativeTreatment.approval_status == status_filter.value)
        with self.session_factory() as session:
            return [self._creative_treatment_to_schema(item) for item in session.scalars(statement).all()]

    def get_creative_treatment(
        self, creative_treatment_id: UUID, organization_id: UUID | None = None
    ) -> CreativeTreatmentRead | None:
        from sqlalchemy import select
        from app.db.models import CreativeTreatment

        statement = select(CreativeTreatment).where(CreativeTreatment.id == creative_treatment_id)
        if organization_id is not None:
            statement = statement.where(CreativeTreatment.organization_id == organization_id)
        with self.session_factory() as session:
            item = session.scalar(statement)
            return self._creative_treatment_to_schema(item) if item is not None else None

    def update_creative_treatment(
        self, creative_treatment: CreativeTreatmentRead, organization_id: UUID | None = None
    ) -> CreativeTreatmentRead | None:
        from sqlalchemy import select
        from app.db.models import CreativeTreatment

        statement = select(CreativeTreatment).where(CreativeTreatment.id == creative_treatment.id)
        if organization_id is not None:
            statement = statement.where(CreativeTreatment.organization_id == organization_id)
        with self.session_factory() as session:
            item = session.scalar(statement)
            if item is None:
                return None
            item.brief_id = creative_treatment.brief_id
            item.brand_pack_id = creative_treatment.brand_pack_id
            item.name = creative_treatment.name
            item.objective = creative_treatment.objective
            item.target_audience = creative_treatment.target_audience
            item.channel = creative_treatment.channel
            item.placement = creative_treatment.placement
            item.angle = creative_treatment.angle
            item.hook = creative_treatment.hook
            item.cta = creative_treatment.cta
            item.offer = creative_treatment.offer
            item.copy = creative_treatment.body_copy
            item.media_metadata = creative_treatment.media_metadata
            item.ai_generated = creative_treatment.ai_generated
            item.human_edited = creative_treatment.human_edited
            item.compliance_status = creative_treatment.compliance_status
            item.approval_status = creative_treatment.approval_status.value
            item.approved_claim_ids = creative_treatment.approved_claim_ids
            item.metrics_snapshot = creative_treatment.metrics_snapshot
            session.commit()
            session.refresh(item)
            return self._creative_treatment_to_schema(item)

    def create_experiment(self, payload: ExperimentCreate, organization_id: UUID) -> ExperimentRead:
        from app.db.models import Experiment, ExperimentVariant

        data = payload.model_dump()
        variants = data.pop("variants")
        item = Experiment(
            organization_id=organization_id,
            status=ExperimentStatus.draft.value,
            starts_at=None,
            ends_at=None,
            **data,
        )
        with self.session_factory() as session:
            session.add(item)
            session.flush()
            for variant in variants:
                session.add(
                    ExperimentVariant(
                        organization_id=organization_id,
                        experiment_id=item.id,
                        **variant,
                    )
                )
            session.commit()
            session.refresh(item)
            return self._experiment_to_schema(session, item)

    def list_experiments(self, organization_id: UUID | None = None) -> list[ExperimentRead]:
        from sqlalchemy import select
        from app.db.models import Experiment

        statement = select(Experiment).order_by(Experiment.created_at.desc())
        if organization_id is not None:
            statement = statement.where(Experiment.organization_id == organization_id)
        with self.session_factory() as session:
            return [self._experiment_to_schema(session, item) for item in session.scalars(statement).all()]

    def get_experiment(self, experiment_id: UUID, organization_id: UUID | None = None) -> ExperimentRead | None:
        from sqlalchemy import select
        from app.db.models import Experiment

        statement = select(Experiment).where(Experiment.id == experiment_id)
        if organization_id is not None:
            statement = statement.where(Experiment.organization_id == organization_id)
        with self.session_factory() as session:
            item = session.scalar(statement)
            return self._experiment_to_schema(session, item) if item is not None else None

    def update_experiment(self, experiment: ExperimentRead, organization_id: UUID | None = None) -> ExperimentRead | None:
        from sqlalchemy import select
        from app.db.models import Experiment

        statement = select(Experiment).where(Experiment.id == experiment.id)
        if organization_id is not None:
            statement = statement.where(Experiment.organization_id == organization_id)
        with self.session_factory() as session:
            item = session.scalar(statement)
            if item is None:
                return None
            item.name = experiment.name
            item.hypothesis = experiment.hypothesis
            item.primary_metric = experiment.primary_metric
            item.guardrail_metric = experiment.guardrail_metric
            item.randomization_unit = experiment.randomization_unit
            item.status = experiment.status.value
            item.channel = experiment.channel
            item.decision_rule = experiment.decision_rule
            item.minimum_detectable_effect = experiment.minimum_detectable_effect
            item.starts_at = experiment.starts_at
            item.ends_at = experiment.ends_at
            item.notes = experiment.notes
            session.commit()
            session.refresh(item)
            return self._experiment_to_schema(session, item)

    def create_bandit(self, payload: BanditCreate, organization_id: UUID) -> dict[str, Any]:
        from app.db.models import Bandit, BanditArm

        item = Bandit(organization_id=organization_id, name=payload.name, status="running")
        with self.session_factory() as session:
            session.add(item)
            session.flush()
            for arm in payload.arms:
                session.add(
                    BanditArm(
                        organization_id=organization_id,
                        bandit_id=item.id,
                        name=arm,
                        alpha=1.0,
                        beta=1.0,
                    )
                )
            session.commit()
            session.refresh(item)
            return self._bandit_to_dict(session, item)

    def get_bandit(self, bandit_id: UUID, organization_id: UUID | None = None) -> dict[str, Any] | None:
        from sqlalchemy import select
        from app.db.models import Bandit

        statement = select(Bandit).where(Bandit.id == bandit_id)
        if organization_id is not None:
            statement = statement.where(Bandit.organization_id == organization_id)
        with self.session_factory() as session:
            item = session.scalar(statement)
            return self._bandit_to_dict(session, item) if item is not None else None

    def update_bandit_arm(
        self, bandit_id: UUID, payload: BanditUpdate, organization_id: UUID | None = None
    ) -> dict[str, Any] | None:
        from sqlalchemy import select
        from app.db.models import Bandit, BanditArm

        bandit_statement = select(Bandit).where(Bandit.id == bandit_id)
        if organization_id is not None:
            bandit_statement = bandit_statement.where(Bandit.organization_id == organization_id)
        with self.session_factory() as session:
            bandit = session.scalar(bandit_statement)
            if bandit is None:
                return None
            arm = session.scalar(
                select(BanditArm).where(
                    BanditArm.bandit_id == bandit_id,
                    BanditArm.name == payload.arm,
                )
            )
            if arm is None:
                return None
            if payload.success:
                arm.alpha += 1
            else:
                arm.beta += 1
            session.commit()
            session.refresh(bandit)
            return self._bandit_to_dict(session, bandit)

    def create_uplift_run(self, payload: RunCreate, organization_id: UUID) -> RunRead:
        from app.db.models import UpliftRun

        result = {"auuc": None, "qini": None, "note": "Scaffold ready for EconML/CausalML adapters."}
        item = UpliftRun(
            organization_id=organization_id,
            name=payload.name,
            status="completed_demo",
            inputs=payload.config,
            outputs=result,
        )
        with self.session_factory() as session:
            session.add(item)
            session.commit()
            session.refresh(item)
            return self._uplift_run_to_schema(item)

    def get_uplift_run(self, run_id: UUID, organization_id: UUID | None = None) -> RunRead | None:
        from sqlalchemy import select
        from app.db.models import UpliftRun

        statement = select(UpliftRun).where(UpliftRun.id == run_id)
        if organization_id is not None:
            statement = statement.where(UpliftRun.organization_id == organization_id)
        with self.session_factory() as session:
            item = session.scalar(statement)
            return self._uplift_run_to_schema(item) if item is not None else None

    def create_mmm_run(self, payload: RunCreate, organization_id: UUID) -> RunRead:
        from app.db.models import MmmRun

        result = {
            "channels": {"paid_social": 0.42, "search": 0.31, "email": 0.12},
            "calibration_note": "Use incrementality tests as priors in future PyMC-Marketing/Meridian adapter.",
        }
        item = MmmRun(
            organization_id=organization_id,
            name=payload.name,
            status="completed_demo",
            inputs=payload.config,
            outputs=result,
        )
        with self.session_factory() as session:
            session.add(item)
            session.commit()
            session.refresh(item)
            return self._mmm_run_to_schema(item)

    def get_mmm_run(self, run_id: UUID, organization_id: UUID | None = None) -> RunRead | None:
        from sqlalchemy import select
        from app.db.models import MmmRun

        statement = select(MmmRun).where(MmmRun.id == run_id)
        if organization_id is not None:
            statement = statement.where(MmmRun.organization_id == organization_id)
        with self.session_factory() as session:
            item = session.scalar(statement)
            return self._mmm_run_to_schema(item) if item is not None else None

    def _bandit_to_dict(self, session: Any, item: Any) -> dict[str, Any]:
        from sqlalchemy import select
        from app.db.models import BanditArm

        arms = session.scalars(
            select(BanditArm)
            .where(BanditArm.bandit_id == item.id)
            .order_by(BanditArm.name.asc())
        ).all()
        return {
            "id": item.id,
            "organization_id": item.organization_id,
            "name": item.name,
            "arms": {arm.name: {"alpha": arm.alpha, "beta": arm.beta} for arm in arms},
        }

    def _uplift_run_to_schema(self, item: Any) -> RunRead:
        return RunRead(
            id=item.id,
            organization_id=item.organization_id,
            status=item.status,
            model_type="two_model_baseline",
            config=item.inputs or {},
            result=item.outputs or {},
        )

    def _mmm_run_to_schema(self, item: Any) -> RunRead:
        return RunRead(
            id=item.id,
            organization_id=item.organization_id,
            status=item.status,
            model_type="demo_linear_mmm",
            config=item.inputs or {},
            result=item.outputs or {},
        )

    def _organization_to_schema(self, item: Any) -> OrganizationRead:
        return OrganizationRead(
            id=item.id,
            name=item.name,
            slug=item.slug,
            plan=item.plan,
        )

    def _api_key_to_schema(self, item: Any, raw_key: str | None = None) -> ApiKeyRead:
        return ApiKeyRead(
            id=item.id,
            organization_id=item.organization_id,
            name=item.name,
            prefix=item.prefix,
            scopes=item.scopes or [],
            raw_key=raw_key,
            created_at=item.created_at,
        )

    def _audit_log_to_schema(self, item: Any) -> AuditLogRead:
        return AuditLogRead(
            id=item.id,
            organization_id=item.organization_id,
            action=item.action,
            target_type=item.target_type,
            target_id=item.target_id,
            metadata=item.metadata_ or {},
            created_at=item.created_at,
        )

    def create_claim_evidence(self, payload: ClaimEvidenceCreate, organization_id: UUID) -> ClaimEvidenceRead:
        from app.db.models import ClaimEvidence

        item = ClaimEvidence(organization_id=organization_id, **payload.model_dump())
        with self.session_factory() as session:
            session.add(item)
            session.commit()
            session.refresh(item)
            return self._claim_evidence_to_schema(item)

    def list_claim_evidence(self, organization_id: UUID | None = None) -> list[ClaimEvidenceRead]:
        from sqlalchemy import select
        from app.db.models import ClaimEvidence

        statement = select(ClaimEvidence).order_by(ClaimEvidence.created_at.desc())
        if organization_id is not None:
            statement = statement.where(ClaimEvidence.organization_id == organization_id)
        with self.session_factory() as session:
            return [self._claim_evidence_to_schema(item) for item in session.scalars(statement).all()]

    def ingest_events(
        self,
        events: list[EventIn],
        organization_id: UUID,
        idempotency_key: str | None = None,
    ) -> tuple[int, int]:
        from sqlalchemy import select
        from sqlalchemy.exc import IntegrityError

        from app.db.models import Event

        with self.session_factory() as session:
            if idempotency_key:
                existing = session.scalar(
                    select(Event.id).where(
                        Event.organization_id == organization_id,
                        Event.idempotency_key == idempotency_key,
                    )
                )
                if existing is not None:
                    return 0, len(events)
            for index, event in enumerate(events):
                session.add(
                    Event(
                        organization_id=organization_id,
                        idempotency_key=idempotency_key if index == 0 else None,
                        **event.model_dump(),
                    )
                )
            try:
                session.commit()
            except IntegrityError:
                # Concurrent replay of the same idempotency key: the unique
                # constraint uq_events_org_idempotency wins over the
                # check-then-insert race above.
                session.rollback()
                return 0, len(events)
            return len(events), 0

    def _brand_pack_to_schema(self, item: Any) -> BrandPackRead:
        return BrandPackRead(
            id=item.id,
            organization_id=item.organization_id,
            name=item.name,
            voice=item.voice,
            guardrails=item.guardrails or {},
            prohibited_claims=item.prohibited_claims or [],
            regulated_category=item.regulated_category,
        )

    def _brief_to_schema(self, item: Any) -> BriefRead:
        return BriefRead(
            id=item.id,
            organization_id=item.organization_id,
            brand_pack_id=item.brand_pack_id,
            name=item.name,
            objective=item.objective,
            target_audience=item.target_audience,
            channel=item.channel,
            primary_kpi=item.primary_kpi,
            body=item.body,
            status=item.status,
        )

    def _creative_treatment_to_schema(self, item: Any) -> CreativeTreatmentRead:
        return CreativeTreatmentRead(
            id=item.id,
            organization_id=item.organization_id,
            brief_id=item.brief_id,
            brand_pack_id=item.brand_pack_id,
            name=item.name,
            objective=item.objective,
            target_audience=item.target_audience,
            channel=item.channel,
            placement=item.placement,
            angle=item.angle,
            hook=item.hook,
            cta=item.cta,
            offer=item.offer,
            body_copy=item.copy,
            media_metadata=item.media_metadata or {},
            ai_generated=item.ai_generated,
            human_edited=item.human_edited,
            approved_claim_ids=item.approved_claim_ids or [],
            compliance_status=item.compliance_status,
            approval_status=ApprovalStatus(item.approval_status),
            metrics_snapshot=item.metrics_snapshot or {},
        )

    def _experiment_to_schema(self, session: Any, item: Any) -> ExperimentRead:
        from sqlalchemy import select
        from app.db.models import ExperimentVariant

        variants = session.scalars(
            select(ExperimentVariant)
            .where(ExperimentVariant.experiment_id == item.id)
            .order_by(ExperimentVariant.created_at.asc(), ExperimentVariant.key.asc())
        ).all()
        return ExperimentRead(
            id=item.id,
            organization_id=item.organization_id,
            name=item.name,
            hypothesis=item.hypothesis,
            primary_metric=item.primary_metric,
            guardrail_metric=item.guardrail_metric,
            variants=[
                ExperimentVariantInput(
                    key=variant.key,
                    creative_treatment_id=variant.creative_treatment_id,
                    allocation=variant.allocation,
                    is_control=variant.is_control,
                )
                for variant in variants
            ],
            randomization_unit=item.randomization_unit,
            channel=item.channel,
            decision_rule=item.decision_rule,
            minimum_detectable_effect=item.minimum_detectable_effect,
            notes=item.notes,
            status=ExperimentStatus(item.status),
            starts_at=item.starts_at,
            ends_at=item.ends_at,
        )

    def list_events(
        self,
        organization_id: UUID | None = None,
        limit: int | None = 25,
        offset: int = 0,
    ) -> list[EventIn]:
        from sqlalchemy import select
        from app.db.models import Event

        statement = select(Event).order_by(Event.timestamp.desc())
        if organization_id is not None:
            statement = statement.where(Event.organization_id == organization_id)
        statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        with self.session_factory() as session:
            return [self._event_to_schema(item) for item in session.scalars(statement).all()]

    def record_event_quality_snapshot(
        self,
        summary: dict[str, Any],
        organization_id: UUID,
    ) -> EventQualitySnapshotRead:
        from app.db.models import EventQualitySnapshot

        item = EventQualitySnapshot(
            organization_id=organization_id,
            captured_at=datetime.now(UTC),
            total_events=summary.get("total_events", 0),
            unique_actors=summary.get("unique_actors", 0),
            events_with_experiment=summary.get("events_with_experiment", 0),
            events_with_variant=summary.get("events_with_variant", 0),
            conversion_events=summary.get("conversion_events", 0),
            revenue=summary.get("revenue", 0.0),
            experiment_coverage=summary.get("experiment_coverage", 0.0),
            variant_coverage=summary.get("variant_coverage", 0.0),
            revenue_coverage=summary.get("revenue_coverage", 0.0),
            quality_score=summary.get("quality_score", 0.0),
            warnings=list(summary.get("warnings", [])),
        )
        with self.session_factory() as session:
            session.add(item)
            session.commit()
            session.refresh(item)
            return self._event_quality_snapshot_to_schema(item)

    def list_event_quality_snapshots(
        self,
        organization_id: UUID | None = None,
        limit: int = 30,
    ) -> list[EventQualitySnapshotRead]:
        from sqlalchemy import select

        from app.db.models import EventQualitySnapshot

        statement = (
            select(EventQualitySnapshot)
            .order_by(EventQualitySnapshot.captured_at.desc())
            .limit(limit)
        )
        if organization_id is not None:
            statement = statement.where(EventQualitySnapshot.organization_id == organization_id)
        with self.session_factory() as session:
            return [self._event_quality_snapshot_to_schema(item) for item in session.scalars(statement).all()]

    def measurement_summary_stats(
        self,
        organization_id: UUID,
        since: datetime | None = None,
    ) -> MeasurementSummaryStats:
        from sqlalchemy import func, select

        from app.db.models import CreativeTreatment, Event, Experiment
        from app.services.measurement import CONVERSION_EVENT_NAMES

        event_conditions = [Event.organization_id == organization_id]
        if since is not None:
            event_conditions.append(Event.timestamp >= since)

        totals_statement = select(
            func.count(Event.id),
            func.count(func.distinct(func.coalesce(Event.user_id, Event.anonymous_id))),
            func.max(Event.timestamp),
        ).where(*event_conditions)
        conversions_statement = select(
            func.count(Event.id),
            func.coalesce(func.sum(Event.value), 0),
        ).where(*event_conditions, Event.event_name.in_(sorted(CONVERSION_EVENT_NAMES)))
        experiments_statement = select(func.count(Experiment.id)).where(
            Experiment.organization_id == organization_id,
            Experiment.status == "running",
        )
        creatives_statement = (
            select(CreativeTreatment.approval_status, func.count(CreativeTreatment.id))
            .where(CreativeTreatment.organization_id == organization_id)
            .group_by(CreativeTreatment.approval_status)
        )

        with self.session_factory() as session:
            total_events, unique_actors, last_event_at = session.execute(totals_statement).one()
            conversion_events, conversion_revenue = session.execute(conversions_statement).one()
            running_experiments = session.scalar(experiments_statement) or 0
            approval_counts = {status: count for status, count in session.execute(creatives_statement).all()}

        if isinstance(conversion_revenue, Decimal):
            conversion_revenue = float(conversion_revenue)
        pending_review_creatives = int(approval_counts.get("draft", 0)) + int(approval_counts.get("pending_review", 0))
        return MeasurementSummaryStats(
            total_events=int(total_events or 0),
            conversion_events=int(conversion_events or 0),
            unique_actors=int(unique_actors or 0),
            revenue=float(conversion_revenue or 0.0),
            last_event_at=last_event_at,
            running_experiments=int(running_experiments),
            pending_review_creatives=pending_review_creatives,
            approved_creatives=int(approval_counts.get("approved", 0)),
        )

    def compute_event_health(self, organization_id: UUID) -> dict[str, Any]:
        from sqlalchemy import case, func, select

        from app.db.models import Event
        from app.services.event_quality import summarize_event_aggregates
        from app.services.measurement import CONVERSION_EVENT_NAMES

        conversion_names = sorted(CONVERSION_EVENT_NAMES)
        is_conversion = Event.event_name.in_(conversion_names)
        statement = select(
            func.count(Event.id),
            func.count(func.distinct(func.coalesce(Event.user_id, Event.anonymous_id))),
            func.count(func.coalesce(Event.user_id, Event.anonymous_id)),
            func.count(Event.experiment_id),
            func.count(Event.variant_id),
            func.coalesce(func.sum(case((is_conversion, 1), else_=0)), 0),
            func.coalesce(
                func.sum(case(((is_conversion) & (Event.value.isnot(None)), 1), else_=0)), 0
            ),
            func.coalesce(func.sum(case((is_conversion, Event.value), else_=0)), 0),
            func.max(Event.timestamp),
        ).where(Event.organization_id == organization_id)

        with self.session_factory() as session:
            (
                total_events,
                unique_actors,
                events_with_identity,
                events_with_experiment,
                events_with_variant,
                conversion_events,
                valued_conversion_events,
                revenue,
                last_event_at,
            ) = session.execute(statement).one()

        if not total_events:
            from app.services.event_quality import event_health_summary

            return event_health_summary([])
        if isinstance(revenue, Decimal):
            revenue = float(revenue)
        return summarize_event_aggregates(
            total_events=int(total_events),
            unique_actors=int(unique_actors),
            events_with_identity=int(events_with_identity),
            events_with_experiment=int(events_with_experiment),
            events_with_variant=int(events_with_variant),
            conversion_events=int(conversion_events),
            valued_conversion_events=int(valued_conversion_events),
            revenue=float(revenue or 0.0),
            last_event_at=last_event_at,
        )

    def _event_quality_snapshot_to_schema(self, item: Any) -> EventQualitySnapshotRead:
        revenue = item.revenue
        if isinstance(revenue, Decimal):
            revenue = float(revenue)
        return EventQualitySnapshotRead(
            id=item.id,
            organization_id=item.organization_id,
            captured_at=item.captured_at,
            total_events=item.total_events,
            unique_actors=item.unique_actors,
            events_with_experiment=item.events_with_experiment,
            events_with_variant=item.events_with_variant,
            conversion_events=item.conversion_events,
            revenue=revenue,
            experiment_coverage=item.experiment_coverage,
            variant_coverage=item.variant_coverage,
            revenue_coverage=item.revenue_coverage,
            quality_score=item.quality_score,
            warnings=item.warnings or [],
        )

    def _claim_evidence_to_schema(self, item: Any) -> ClaimEvidenceRead:
        return ClaimEvidenceRead(
            id=item.id,
            organization_id=item.organization_id,
            brand_pack_id=item.brand_pack_id,
            claim=item.claim,
            evidence_url=item.evidence_url,
            source_name=item.source_name,
            notes=item.notes,
            status=item.status,
            created_at=item.created_at,
        )

    def _event_to_schema(self, item: Any) -> EventIn:
        value = item.value
        if isinstance(value, Decimal):
            value = float(value)
        return EventIn(
            event_name=item.event_name,
            timestamp=item.timestamp,
            anonymous_id=item.anonymous_id,
            user_id=item.user_id,
            creative_treatment_id=item.creative_treatment_id,
            experiment_id=item.experiment_id,
            variant_id=item.variant_id,
            channel=item.channel,
            placement=item.placement,
            value=value,
            currency=item.currency,
            properties=item.properties or {},
        )


def create_core_repository(backend: str | None = None) -> CoreRepository:
    selected_backend = backend or get_settings().resource_repository_backend
    if selected_backend == "memory":
        return InMemoryCoreRepository()
    if selected_backend == "sqlalchemy":
        from app.db.session import SessionLocal

        return SQLAlchemyCoreRepository(SessionLocal)
    raise ValueError(
        f"Unknown RESOURCE_REPOSITORY_BACKEND={selected_backend!r}; "
        f"expected one of {sorted(VALID_CORE_REPOSITORY_BACKENDS)}"
    )


class CoreRepositoryProxy:
    """Delegates every call to the active CoreRepository backend.

    Routers import ``core_repository`` by name at import time, so this proxy
    is the seam that lets tests and runtime profiles swap the backend without
    touching call sites. ``use()`` swaps the delegate; ``reset()`` rebuilds it
    from the configured ``RESOURCE_REPOSITORY_BACKEND``.
    """

    def __init__(self, delegate: CoreRepository) -> None:
        self._delegate = delegate

    def use(self, repository: CoreRepository) -> None:
        self._delegate = repository

    def reset(self) -> None:
        self._delegate = create_core_repository()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._delegate, name)


core_repository = CoreRepositoryProxy(create_core_repository())
