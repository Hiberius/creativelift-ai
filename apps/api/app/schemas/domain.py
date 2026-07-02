from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class TimestampedRead(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TenantRead(TimestampedRead):
    organization_id: UUID


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")
    plan: str = "starter"
    settings: dict[str, Any] = Field(default_factory=dict)


class OrganizationRead(TimestampedRead):
    name: str
    slug: str
    plan: str
    settings: dict[str, Any]


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    full_name: str = Field(min_length=1, max_length=200)


class UserRead(TimestampedRead):
    email: str
    full_name: str
    is_active: bool


class MembershipCreate(BaseModel):
    organization_id: UUID
    user_id: UUID
    role: Literal["owner", "admin", "member", "viewer"] = "member"


class MembershipRead(TenantRead):
    user_id: UUID
    role: str
    status: str


class APIKeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    scopes: dict[str, Any] = Field(default_factory=lambda: {"events:write": True})
    expires_at: datetime | None = None


class APIKeyRead(TenantRead):
    name: str
    scopes: dict[str, Any]
    last_used_at: datetime | None
    expires_at: datetime | None
    revoked_at: datetime | None


class BrandPackCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")
    voice_guidelines: str = ""
    visual_guidelines: dict[str, Any] = Field(default_factory=dict)
    forbidden_claims: dict[str, Any] = Field(default_factory=dict)


class BrandPackRead(TenantRead):
    name: str
    slug: str
    voice_guidelines: str
    visual_guidelines: dict[str, Any]
    forbidden_claims: dict[str, Any]


class ApprovedClaimCreate(BaseModel):
    brand_pack_id: UUID | None = None
    claim_text: str = Field(min_length=1, max_length=500)
    evidence_url: str | None = Field(default=None, max_length=1000)
    status: Literal["approved", "pending", "retired"] = "approved"


class ApprovedClaimRead(TenantRead):
    brand_pack_id: UUID | None
    claim_text: str
    evidence_url: str | None
    status: str


class BriefCreate(BaseModel):
    brand_pack_id: UUID | None = None
    title: str = Field(min_length=1, max_length=240)
    objective: str = ""
    audience: str = ""
    channel: str = "paid_social"
    constraints: dict[str, Any] = Field(default_factory=dict)
    status: Literal["draft", "ready", "archived"] = "draft"


class BriefRead(TenantRead):
    brand_pack_id: UUID | None
    title: str
    objective: str
    audience: str
    channel: str
    constraints: dict[str, Any]
    status: str


class CreativeTreatmentCreate(BaseModel):
    brief_id: UUID
    name: str = Field(min_length=1, max_length=200)
    channel: str = "paid_social"
    hypothesis: str = ""
    content: dict[str, Any] = Field(default_factory=dict)
    status: Literal["draft", "ready", "archived"] = "draft"


class CreativeTreatmentRead(TenantRead):
    brief_id: UUID
    name: str
    channel: str
    hypothesis: str
    content: dict[str, Any]
    status: str


class CreativeVersionCreate(BaseModel):
    treatment_id: UUID
    version_label: str = "v1"
    asset_uri: str | None = Field(default=None, max_length=1000)
    payload: dict[str, Any] = Field(default_factory=dict)
    status: Literal["draft", "in_review", "approved", "rejected", "archived"] = "draft"


class CreativeVersionRead(TenantRead):
    treatment_id: UUID
    version_label: str
    asset_uri: str | None
    payload: dict[str, Any]
    status: str


class PromptRunCreate(BaseModel):
    brief_id: UUID | None = None
    prompt: str = Field(min_length=1)
    provider: str | None = None
    model: str | None = None
    variables: dict[str, Any] = Field(default_factory=dict)


class PromptRunRead(TenantRead):
    brief_id: UUID | None
    provider: str
    model: str
    prompt: str
    response: dict[str, Any]
    status: str
    input_tokens: int
    output_tokens: int


class ApprovalReviewCreate(BaseModel):
    creative_version_id: UUID
    reviewer_user_id: UUID | None = None
    status: Literal["pending", "approved", "changes_requested", "rejected"] = "pending"
    notes: str | None = None
    policy_findings: dict[str, Any] = Field(default_factory=dict)


class ApprovalReviewRead(TenantRead):
    creative_version_id: UUID
    reviewer_user_id: UUID | None
    status: str
    notes: str | None
    policy_findings: dict[str, Any]


class ExperimentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=220)
    hypothesis: str = ""
    primary_metric: str = "conversion_rate"
    status: Literal["draft", "running", "paused", "completed", "archived"] = "draft"
    starts_at: datetime | None = None
    ends_at: datetime | None = None


class ExperimentRead(TenantRead):
    name: str
    hypothesis: str
    primary_metric: str
    status: str
    starts_at: datetime | None
    ends_at: datetime | None


class ExperimentVariantCreate(BaseModel):
    creative_version_id: UUID | None = None
    name: str = Field(min_length=1, max_length=160)
    allocation: float = Field(default=0.5, ge=0.0, le=1.0)
    is_control: bool = False


class ExperimentVariantRead(TenantRead):
    experiment_id: UUID
    creative_version_id: UUID | None
    name: str
    allocation: float
    is_control: bool


class EventIngestItem(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    event_name: str = Field(min_length=1, max_length=160)
    event_type: Literal["impression", "click", "conversion", "view", "custom"] = "custom"
    occurred_at: datetime = Field(validation_alias=AliasChoices("occurred_at", "timestamp"))
    external_event_id: str | None = Field(default=None, max_length=255)
    user_id: str | None = Field(default=None, max_length=255)
    anonymous_id: str | None = Field(default=None, max_length=255)
    experiment_id: UUID | None = None
    variant_id: UUID | None = None
    value: float | None = Field(default=None, ge=0)
    properties: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_actor_identity(self) -> "EventIngestItem":
        if not self.user_id and not self.anonymous_id:
            raise ValueError("Either user_id or anonymous_id is required")
        return self


class EventIngestRequest(BaseModel):
    source: str = Field(default="web", max_length=80)
    idempotency_key: str | None = Field(default=None, max_length=255)
    events: list[EventIngestItem] = Field(min_length=1, max_length=500)


class EventRead(TenantRead):
    event_name: str
    event_type: str
    source: str
    external_event_id: str | None
    idempotency_key: str | None
    user_id: str | None
    anonymous_id: str | None
    experiment_id: UUID | None
    variant_id: UUID | None
    occurred_at: datetime
    value: float | None
    properties: dict[str, Any]


class EventIngestResponse(BaseModel):
    accepted: int
    duplicate: bool = False
    idempotency_key: str | None = None
    event_ids: list[UUID] = Field(default_factory=list)


class ExperimentResultRead(TenantRead):
    experiment_id: UUID
    variant_id: UUID | None
    metric_name: str
    value: float
    sample_size: int
    confidence: float | None
    computed_at: datetime


class BanditCreate(BaseModel):
    experiment_id: UUID | None = None
    name: str = Field(min_length=1, max_length=200)
    policy: str = "thompson_sampling"
    status: Literal["draft", "running", "paused", "completed"] = "draft"
    parameters: dict[str, Any] = Field(default_factory=dict)


class BanditRead(TenantRead):
    experiment_id: UUID | None
    name: str
    policy: str
    status: str
    parameters: dict[str, Any]


class BanditArmCreate(BaseModel):
    variant_id: UUID | None = None
    name: str = Field(min_length=1, max_length=160)
    pulls: int = Field(default=0, ge=0)
    rewards: float = Field(default=0.0, ge=0)
    allocation: float = Field(default=0.0, ge=0.0, le=1.0)


class BanditArmRead(TenantRead):
    bandit_id: UUID
    variant_id: UUID | None
    name: str
    pulls: int
    rewards: float
    allocation: float


class MMMRunCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    date_start: datetime | None = None
    date_end: datetime | None = None
    inputs: dict[str, Any] = Field(default_factory=dict)


class MMMRunRead(TenantRead):
    name: str
    status: str
    date_start: datetime | None
    date_end: datetime | None
    inputs: dict[str, Any]
    outputs: dict[str, Any]


class UpliftRunCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    experiment_id: UUID | None = None
    inputs: dict[str, Any] = Field(default_factory=dict)


class UpliftRunRead(TenantRead):
    name: str
    status: str
    experiment_id: UUID | None
    inputs: dict[str, Any]
    outputs: dict[str, Any]


class ConnectorCreate(BaseModel):
    provider: str = Field(min_length=1, max_length=120)
    display_name: str = Field(min_length=1, max_length=200)
    config: dict[str, Any] = Field(default_factory=dict)


class ConnectorRead(TenantRead):
    provider: str
    display_name: str
    status: str
    config: dict[str, Any]
    last_sync_at: datetime | None


class AuditLogRead(TenantRead):
    actor_user_id: UUID | None
    action: str
    resource_type: str | None
    resource_id: UUID | None
    metadata_json: dict[str, Any]


class MetricCard(BaseModel):
    metric: str
    value: float
    delta: float | None = None
    unit: str = "count"


class MeasurementSummary(BaseModel):
    organization_id: UUID
    window: str
    cards: list[MetricCard]
    notes: list[str] = Field(default_factory=list)
