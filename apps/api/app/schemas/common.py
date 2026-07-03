from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

T = TypeVar("T")


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ApiResponse(BaseModel, Generic[T]):
    data: T


class CollectionMeta(BaseModel):
    total: int
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class CollectionResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: CollectionMeta


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str
    code: str


class ErrorBody(BaseModel):
    code: str
    message: str
    request_id: str | None = None
    details: list[ErrorDetail] | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody


class Role(StrEnum):
    owner = "owner"
    admin = "admin"
    marketer = "marketer"
    analyst = "analyst"
    viewer = "viewer"
    service = "service"


class ApprovalStatus(StrEnum):
    draft = "draft"
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"
    archived = "archived"


class ExperimentStatus(StrEnum):
    draft = "draft"
    running = "running"
    paused = "paused"
    completed = "completed"
    invalidated = "invalidated"


class EventName(StrEnum):
    impression = "impression"
    click = "click"
    session_start = "session_start"
    signup = "signup"
    lead = "lead"
    purchase = "purchase"
    revenue = "revenue"
    custom_conversion = "custom_conversion"


class RegisterRequest(APIModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    name: str = Field(min_length=1, max_length=180)
    password: str = Field(min_length=8, max_length=200)
    organization_name: str = Field(min_length=1, max_length=180)
    organization_slug: str | None = Field(default=None, min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")


class LoginRequest(APIModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=200)


class UserRead(APIModel):
    id: UUID
    email: str
    name: str


class AuthSessionRead(APIModel):
    user: UserRead
    organization: "OrganizationRead"
    role: str
    expires_at: datetime


class OrganizationCreate(APIModel):
    name: str = Field(min_length=1, max_length=180)
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")


class OrganizationRead(APIModel):
    id: UUID
    name: str
    slug: str
    plan: str = "open_source"


class BrandPackCreate(APIModel):
    name: str
    voice: str = ""
    guardrails: dict[str, Any] = Field(default_factory=dict)
    prohibited_claims: list[str] = Field(default_factory=list)
    regulated_category: bool = False


class BrandPackRead(BrandPackCreate):
    id: UUID
    organization_id: UUID


class ClaimEvidenceCreate(APIModel):
    claim: str = Field(min_length=1, max_length=260)
    evidence_url: str = Field(min_length=1, max_length=500)
    source_name: str = Field(default="", max_length=180)
    notes: str = ""
    brand_pack_id: UUID | None = None
    status: str = "approved"


class ClaimEvidenceRead(ClaimEvidenceCreate):
    id: UUID
    organization_id: UUID
    created_at: datetime


class BriefCreate(APIModel):
    name: str
    objective: str
    target_audience: str
    channel: str
    primary_kpi: str
    brand_pack_id: UUID | None = None
    body: str = ""


class BriefRead(BriefCreate):
    id: UUID
    organization_id: UUID
    status: str = "draft"


class CreativeTreatmentCreate(APIModel):
    brief_id: UUID | None = None
    brand_pack_id: UUID | None = None
    name: str
    objective: str
    target_audience: str
    channel: str
    placement: str = ""
    angle: str = ""
    hook: str = ""
    cta: str = ""
    offer: str = ""
    body_copy: str = ""
    media_metadata: dict[str, Any] = Field(default_factory=dict)
    ai_generated: bool = True
    human_edited: bool = False
    approved_claim_ids: list[str] = Field(default_factory=list)


class CreativeTreatmentRead(CreativeTreatmentCreate):
    id: UUID
    organization_id: UUID
    compliance_status: str = "pending_review"
    approval_status: ApprovalStatus = ApprovalStatus.draft
    metrics_snapshot: dict[str, Any] = Field(default_factory=dict)


class ReviewDecision(APIModel):
    notes: str = ""
    claim_evidence_urls: list[str] = Field(default_factory=list)


class VariantGenerateRequest(APIModel):
    brief: BriefCreate
    brand_pack: BrandPackCreate | None = None
    n: int = Field(default=3, ge=1, le=12)
    provider: str = "mock"
    temperature: float = Field(default=0.7, ge=0, le=2)


class GeneratedVariant(APIModel):
    variant_id: str
    headline: str
    primary_text: str
    landing_page_hero: str
    email_subject: str
    cta: str
    angle: str
    hypothesis: str
    prompt_lineage: dict[str, Any]


class ExperimentVariantInput(APIModel):
    key: str
    creative_treatment_id: UUID | None = None
    allocation: float = Field(gt=0, le=1)
    is_control: bool = False


class ExperimentCreate(APIModel):
    name: str
    hypothesis: str
    primary_metric: str
    guardrail_metric: str | None = None
    variants: list[ExperimentVariantInput]
    randomization_unit: str = "anonymous_id"
    channel: str = ""
    decision_rule: str = "95% confidence, no SRM, positive guardrails"
    minimum_detectable_effect: float | None = None
    notes: str = ""

    @model_validator(mode="after")
    def allocations_sum(self) -> "ExperimentCreate":
        total = sum(variant.allocation for variant in self.variants)
        if not 0.99 <= total <= 1.01:
            raise ValueError("Experiment variant allocations must sum to 1.0")
        return self


class ExperimentRead(ExperimentCreate):
    id: UUID
    organization_id: UUID
    status: ExperimentStatus = ExperimentStatus.draft
    starts_at: datetime | None = None
    ends_at: datetime | None = None


class ExperimentAssignment(APIModel):
    experiment_id: UUID
    unit_id: str
    variant_key: str
    creative_treatment_id: UUID | None = None
    allocation: float
    is_control: bool = False


class ExperimentInsightRead(APIModel):
    experiment_id: UUID
    recommendation: str
    winning_variant_key: str | None = None
    decision_summary: str
    recommended_action: str
    confidence_note: str
    evidence: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class MeasurementVariantInput(APIModel):
    key: str = Field(min_length=1, max_length=80, pattern=r"^[a-zA-Z0-9_-]+$")
    label: str = Field(default="", max_length=120)
    visitors: int = Field(ge=0, le=100_000_000)
    conversions: int = Field(ge=0, le=100_000_000)
    revenue: float = Field(default=0.0, ge=0)
    allocation: float = Field(default=0.5, gt=0, le=1)

    @model_validator(mode="after")
    def conversions_cannot_exceed_visitors(self) -> "MeasurementVariantInput":
        if self.conversions > self.visitors:
            raise ValueError("conversions cannot exceed visitors")
        return self


class MeasurementAnalyzeRequest(APIModel):
    name: str = Field(default="Untitled experiment", min_length=1, max_length=160)
    primary_metric: str = Field(default="conversion_rate", max_length=80)
    minimum_detectable_effect: float | None = Field(default=0.01, gt=0, le=1)
    control: MeasurementVariantInput
    treatment: MeasurementVariantInput

    @model_validator(mode="after")
    def variant_keys_must_differ(self) -> "MeasurementAnalyzeRequest":
        if self.control.key == self.treatment.key:
            raise ValueError("control and treatment keys must differ")
        return self


class MeasurementAnalysisRead(APIModel):
    name: str
    primary_metric: str
    variants: dict[str, Any]
    comparison: dict[str, Any]
    srm: dict[str, Any]
    sample_size: dict[str, Any]
    # Additive optional field: always-valid sequential test (mSPRT) block.
    sequential: dict[str, Any] | None = None
    recommendation: str
    decision_summary: str
    recommended_action: str
    next_steps: list[str] = Field(default_factory=list)


class MeasurementReportCreate(APIModel):
    source: str = Field(default="manual", min_length=1, max_length=80)
    notes: str = Field(default="", max_length=500)
    request: MeasurementAnalyzeRequest


class MeasurementReportRead(APIModel):
    id: UUID
    created_at: datetime
    source: str
    notes: str = ""
    request: MeasurementAnalyzeRequest
    analysis: MeasurementAnalysisRead


class MeasurementCsvImportRequest(APIModel):
    csv_text: str = Field(min_length=1, max_length=200_000)
    source: str = Field(default="csv", min_length=1, max_length=80)
    save_reports: bool = True
    default_minimum_detectable_effect: float | None = Field(default=0.01, gt=0, le=1)


class MeasurementCsvImportError(APIModel):
    row_number: int
    message: str


class MeasurementCsvImportRead(APIModel):
    accepted: int
    rejected: int
    reports: list[MeasurementReportRead] = Field(default_factory=list)
    errors: list[MeasurementCsvImportError] = Field(default_factory=list)
    required_columns: list[str] = Field(default_factory=list)


class MeasurementReportSummaryRead(APIModel):
    total: int
    winners: int
    losers: int
    inconclusive: int
    invalid_srm: int
    needs_more_data: int
    average_relative_lift: float | None = None
    best_report_id: UUID | None = None
    best_report_name: str | None = None
    best_relative_lift: float | None = None


class EventIn(APIModel):
    event_name: EventName
    timestamp: datetime
    anonymous_id: str | None = None
    user_id: str | None = None
    creative_treatment_id: UUID
    experiment_id: UUID | None = None
    variant_id: str | None = None
    channel: str | None = None
    placement: str | None = None
    value: float | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    properties: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def identity_present(self) -> "EventIn":
        if not self.anonymous_id and not self.user_id:
            raise ValueError("anonymous_id or user_id is required")
        return self


class EventBatchIn(APIModel):
    events: list[EventIn] = Field(min_length=1, max_length=500)


class EventIngestResponse(APIModel):
    accepted: int
    deduplicated: int = 0
    organization_id: UUID


class EventHealthRead(APIModel):
    total_events: int
    unique_actors: int
    events_with_experiment: int
    events_with_variant: int
    conversion_events: int
    revenue: float
    last_event_at: datetime | None = None
    event_counts: dict[str, int] = Field(default_factory=dict)
    channel_counts: dict[str, int] = Field(default_factory=dict)
    experiment_coverage: float
    variant_coverage: float
    revenue_coverage: float
    quality_score: float
    warnings: list[str] = Field(default_factory=list)


class EventQualitySnapshotRead(APIModel):
    id: UUID
    organization_id: UUID
    captured_at: datetime
    total_events: int
    unique_actors: int
    events_with_experiment: int
    events_with_variant: int
    conversion_events: int
    revenue: float
    experiment_coverage: float
    variant_coverage: float
    revenue_coverage: float
    quality_score: float
    warnings: list[str] = Field(default_factory=list)


class DemoScenarioRead(APIModel):
    organization: OrganizationRead
    brand_pack: BrandPackRead
    brief: BriefRead
    claim_evidence: ClaimEvidenceRead
    creatives: list[CreativeTreatmentRead]
    experiment: ExperimentRead
    ingestion: EventIngestResponse
    event_health: EventHealthRead
    result: dict[str, Any]
    insight: ExperimentInsightRead
    results_url: str


class ApiKeyCreate(APIModel):
    name: str
    scopes: list[str] = Field(default_factory=lambda: ["events:write"])


class ApiKeyRead(APIModel):
    id: UUID
    organization_id: UUID
    name: str
    prefix: str
    scopes: list[str]
    created_at: datetime
    raw_key: str | None = None


class BanditCreate(APIModel):
    name: str
    arms: list[str] = Field(min_length=2)


class BanditDecision(APIModel):
    chosen_arm: str
    samples: dict[str, float]


class BanditUpdate(APIModel):
    arm: str
    success: bool


class RunCreate(APIModel):
    name: str = "demo run"
    config: dict[str, Any] = Field(default_factory=dict)


class RunRead(APIModel):
    id: UUID
    organization_id: UUID
    status: str
    model_type: str
    config: dict[str, Any]
    result: dict[str, Any]


class AuditLogRead(APIModel):
    id: UUID
    organization_id: UUID
    action: str
    target_type: str
    target_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
