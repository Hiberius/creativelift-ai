from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB as PostgresJSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# JSONB on Postgres; generic JSON on other dialects so SQLite-backed tests can run.
JSONB = JSON().with_variant(PostgresJSONB(), "postgresql")


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    plan: Mapped[str] = mapped_column(String(40), default="open_source")
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    auth_provider: Mapped[str] = mapped_column(String(80), default="local")
    external_subject: Mapped[str | None] = mapped_column(String(240), nullable=True)


class Membership(Base, TimestampMixin):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("organization_id", "user_id", name="uq_membership_org_user"),)

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(40), nullable=False)


class ApiKey(Base, TimestampMixin):
    __tablename__ = "api_keys"
    __table_args__ = (Index("ix_api_keys_org_prefix", "organization_id", "prefix"),)

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    prefix: Mapped[str] = mapped_column(String(24), nullable=False)
    hashed_key: Mapped[str] = mapped_column(String(128), nullable=False)
    scopes: Mapped[list[str]] = mapped_column(JSONB, default=list)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class BrandPack(Base, TimestampMixin):
    __tablename__ = "brand_packs"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    voice: Mapped[str] = mapped_column(Text, default="")
    guardrails: Mapped[dict] = mapped_column(JSONB, default=dict)
    prohibited_claims: Mapped[list[str]] = mapped_column(JSONB, default=list)
    regulated_category: Mapped[bool] = mapped_column(Boolean, default=False)


class ApprovedClaim(Base, TimestampMixin):
    __tablename__ = "approved_claims"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    brand_pack_id: Mapped[UUID] = mapped_column(ForeignKey("brand_packs.id"), nullable=False)
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ClaimEvidence(Base, TimestampMixin):
    __tablename__ = "claim_evidence"
    __table_args__ = (Index("ix_claim_evidence_org_status", "organization_id", "status"),)

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    brand_pack_id: Mapped[UUID | None] = mapped_column(ForeignKey("brand_packs.id"), nullable=True)
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_name: Mapped[str] = mapped_column(String(180), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="approved")


class Brief(Base, TimestampMixin):
    __tablename__ = "briefs"
    __table_args__ = (Index("ix_briefs_org_status", "organization_id", "status"),)

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    brand_pack_id: Mapped[UUID | None] = mapped_column(ForeignKey("brand_packs.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    objective: Mapped[str] = mapped_column(String(180), nullable=False)
    target_audience: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(String(80), nullable=False)
    primary_kpi: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="draft")
    body: Mapped[str] = mapped_column(Text, default="")


class CreativeTreatment(Base, TimestampMixin):
    __tablename__ = "creative_treatments"
    __table_args__ = (
        Index("ix_treatments_org_status", "organization_id", "approval_status"),
        Index("ix_treatments_org_channel", "organization_id", "channel"),
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    brief_id: Mapped[UUID | None] = mapped_column(ForeignKey("briefs.id"), nullable=True)
    brand_pack_id: Mapped[UUID | None] = mapped_column(ForeignKey("brand_packs.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    objective: Mapped[str] = mapped_column(String(180), nullable=False)
    target_audience: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(String(80), nullable=False)
    placement: Mapped[str] = mapped_column(String(120), default="")
    angle: Mapped[str] = mapped_column(String(160), default="")
    hook: Mapped[str] = mapped_column(Text, default="")
    cta: Mapped[str] = mapped_column(String(120), default="")
    offer: Mapped[str] = mapped_column(String(180), default="")
    copy: Mapped[str] = mapped_column(Text, default="")
    media_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=True)
    human_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    compliance_status: Mapped[str] = mapped_column(String(40), default="pending_review")
    approval_status: Mapped[str] = mapped_column(String(40), default="draft")
    approved_claim_ids: Mapped[list[str]] = mapped_column(JSONB, default=list)
    metrics_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict)
    versions: Mapped[list["CreativeVersion"]] = relationship()


class CreativeVersion(Base, TimestampMixin):
    __tablename__ = "creative_versions"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    creative_treatment_id: Mapped[UUID] = mapped_column(ForeignKey("creative_treatments.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    edited_by_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    change_note: Mapped[str] = mapped_column(Text, default="")


class PromptRun(Base, TimestampMixin):
    __tablename__ = "prompt_runs"
    __table_args__ = (Index("ix_prompt_runs_brief", "brief_id"),)

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    brief_id: Mapped[UUID | None] = mapped_column(ForeignKey("briefs.id"), nullable=True)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[dict] = mapped_column(JSONB, default=dict)
    response: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(40), default="succeeded")
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)


class ApprovalReview(Base, TimestampMixin):
    __tablename__ = "approval_reviews"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    creative_treatment_id: Mapped[UUID] = mapped_column(ForeignKey("creative_treatments.id"), nullable=False)
    reviewer_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="")
    claim_evidence_urls: Mapped[list[str]] = mapped_column(JSONB, default=list)


class Experiment(Base, TimestampMixin):
    __tablename__ = "experiments"
    __table_args__ = (Index("ix_experiments_org_status", "organization_id", "status"),)

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    hypothesis: Mapped[str] = mapped_column(Text, nullable=False)
    primary_metric: Mapped[str] = mapped_column(String(80), nullable=False)
    guardrail_metric: Mapped[str | None] = mapped_column(String(80), nullable=True)
    randomization_unit: Mapped[str] = mapped_column(String(80), default="anonymous_id")
    status: Mapped[str] = mapped_column(String(40), default="draft")
    channel: Mapped[str] = mapped_column(String(80), default="")
    decision_rule: Mapped[str] = mapped_column(Text, default="")
    minimum_detectable_effect: Mapped[float | None] = mapped_column(Float, nullable=True)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")


class ExperimentVariant(Base, TimestampMixin):
    __tablename__ = "experiment_variants"
    __table_args__ = (UniqueConstraint("experiment_id", "key", name="uq_experiment_variant_key"),)

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    experiment_id: Mapped[UUID] = mapped_column(ForeignKey("experiments.id"), nullable=False)
    creative_treatment_id: Mapped[UUID | None] = mapped_column(ForeignKey("creative_treatments.id"), nullable=True)
    key: Mapped[str] = mapped_column(String(80), nullable=False)
    allocation: Mapped[float] = mapped_column(Float, nullable=False)
    is_control: Mapped[bool] = mapped_column(Boolean, default=False)


class Event(Base, TimestampMixin):
    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_org_time", "organization_id", "timestamp"),
        Index("ix_events_treatment", "creative_treatment_id"),
        Index("ix_events_experiment_variant", "experiment_id", "variant_id"),
        UniqueConstraint("organization_id", "idempotency_key", name="uq_events_org_idempotency"),
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    event_name: Mapped[str] = mapped_column(String(80), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    anonymous_id: Mapped[str | None] = mapped_column(String(180), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(180), nullable=True)
    creative_treatment_id: Mapped[UUID] = mapped_column(ForeignKey("creative_treatments.id"), nullable=False)
    experiment_id: Mapped[UUID | None] = mapped_column(ForeignKey("experiments.id"), nullable=True)
    variant_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    channel: Mapped[str | None] = mapped_column(String(80), nullable=True)
    placement: Mapped[str | None] = mapped_column(String(120), nullable=True)
    value: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(180), nullable=True)
    properties: Mapped[dict] = mapped_column(JSONB, default=dict)


class ExperimentResult(Base, TimestampMixin):
    __tablename__ = "experiment_results"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    experiment_id: Mapped[UUID] = mapped_column(ForeignKey("experiments.id"), nullable=False)
    result: Mapped[dict] = mapped_column(JSONB, nullable=False)
    recommendation: Mapped[str] = mapped_column(String(40), nullable=False)


class Bandit(Base, TimestampMixin):
    __tablename__ = "bandits"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    policy: Mapped[str] = mapped_column(String(80), default="thompson_sampling")
    status: Mapped[str] = mapped_column(String(40), default="draft")


class BanditArm(Base, TimestampMixin):
    __tablename__ = "bandit_arms"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    bandit_id: Mapped[UUID] = mapped_column(ForeignKey("bandits.id"), nullable=False)
    creative_treatment_id: Mapped[UUID | None] = mapped_column(ForeignKey("creative_treatments.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    alpha: Mapped[float] = mapped_column(Float, default=1.0)
    beta: Mapped[float] = mapped_column(Float, default=1.0)


class MmmRun(Base, TimestampMixin):
    __tablename__ = "mmm_runs"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="queued")
    date_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    date_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    inputs: Mapped[dict] = mapped_column(JSONB, default=dict)
    outputs: Mapped[dict] = mapped_column(JSONB, default=dict)


class UpliftRun(Base, TimestampMixin):
    __tablename__ = "uplift_runs"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    experiment_id: Mapped[UUID | None] = mapped_column(ForeignKey("experiments.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="queued")
    inputs: Mapped[dict] = mapped_column(JSONB, default=dict)
    outputs: Mapped[dict] = mapped_column(JSONB, default=dict)


class Connector(Base, TimestampMixin):
    __tablename__ = "connectors"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(120), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="disconnected")
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_org_time", "organization_id", "created_at"),)

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    actor_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    target_type: Mapped[str] = mapped_column(String(120), nullable=False)
    target_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # "metadata" is reserved by the Declarative API; keep the DB column name unchanged.
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)


class EventQualitySnapshot(Base, TimestampMixin):
    __tablename__ = "event_quality_snapshots"
    __table_args__ = (Index("ix_event_quality_snapshots_org_captured", "organization_id", "captured_at"),)

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    total_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unique_actors: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    events_with_experiment: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    events_with_variant: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    conversion_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    revenue: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    experiment_coverage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    variant_coverage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    revenue_coverage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    warnings: Mapped[list] = mapped_column(JSONB, default=list)
