from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.core.security import DEMO_ORG_ID, DEMO_USER_ID, generate_api_key
from app.schemas.common import (
    ApiKeyRead,
    ApprovalStatus,
    AuditLogRead,
    BrandPackRead,
    BriefRead,
    ClaimEvidenceRead,
    CreativeTreatmentRead,
    EventIn,
    EventQualitySnapshotRead,
    ExperimentRead,
    ExperimentStatus,
    ExperimentVariantInput,
    OrganizationRead,
    RunRead,
)


def _u(suffix: int) -> UUID:
    return UUID(f"00000000-0000-0000-0000-{suffix:012d}")


class DemoStore:
    def __init__(self) -> None:
        self.organization = OrganizationRead(
            id=DEMO_ORG_ID, name="Growth Lab Inc.", slug="growth-lab", plan="open_source"
        )
        self.organizations: dict[UUID, OrganizationRead] = {self.organization.id: self.organization}
        self.brand_packs: dict[UUID, BrandPackRead] = {
            _u(11): BrandPackRead(
                id=_u(11),
                organization_id=DEMO_ORG_ID,
                name="Growth Lab Core",
                voice="Clear, evidence-led, direct, never hype-only.",
                guardrails={"claims_require_evidence": True, "tone": "premium technical"},
                prohibited_claims=["guaranteed revenue", "risk free growth"],
            )
        }
        self.claim_evidence: dict[UUID, ClaimEvidenceRead] = {
            _u(31): ClaimEvidenceRead(
                id=_u(31),
                organization_id=DEMO_ORG_ID,
                brand_pack_id=_u(11),
                claim="Measure incremental lift before scaling spend.",
                evidence_url="https://example.com/lift-methodology",
                source_name="Internal methodology",
                notes="Approved for demo proof-led creative angles.",
                status="approved",
                created_at=datetime.now(UTC),
            )
        }
        self.briefs: dict[UUID, BriefRead] = {
            _u(21): BriefRead(
                id=_u(21),
                organization_id=DEMO_ORG_ID,
                brand_pack_id=_u(11),
                name="Meta prospecting AI video test",
                objective="Increase qualified demo requests from paid social",
                target_audience="US B2B SaaS growth leaders at 50-500 employee companies",
                channel="paid_social",
                primary_kpi="signup",
                body="Compare proof-led AI-generated hooks against static control creative.",
            ),
            _u(22): BriefRead(
                id=_u(22),
                organization_id=DEMO_ORG_ID,
                brand_pack_id=_u(11),
                name="Lifecycle email subject line lift",
                objective="Improve activation from trial users",
                target_audience="Trial users who imported ad accounts but did not launch a test",
                channel="email",
                primary_kpi="activation",
            ),
            _u(23): BriefRead(
                id=_u(23),
                organization_id=DEMO_ORG_ID,
                brand_pack_id=_u(11),
                name="Landing page hero angle test",
                objective="Lift visitor-to-demo conversion",
                target_audience="Marketing teams comparing AI attribution tools",
                channel="landing_page",
                primary_kpi="demo_request",
            ),
        }
        self.creatives: dict[UUID, CreativeTreatmentRead] = {}
        for idx in range(12):
            cid = _u(101 + idx)
            channel = ["paid_social", "email", "landing_page"][idx % 3]
            status = [
                ApprovalStatus.approved,
                ApprovalStatus.pending_review,
                ApprovalStatus.draft,
                ApprovalStatus.rejected,
            ][idx % 4]
            self.creatives[cid] = CreativeTreatmentRead(
                id=cid,
                organization_id=DEMO_ORG_ID,
                brief_id=_u(21 + (idx % 3)),
                brand_pack_id=_u(11),
                name=f"AI treatment {idx + 1}: prompt-to-profit angle",
                objective="Drive incremental conversion lift",
                target_audience="US growth teams",
                channel=channel,
                placement="meta_feed" if channel == "paid_social" else channel,
                angle=["proof", "speed", "governance", "open_source"][idx % 4],
                hook="Stop trusting platform ROAS blindly.",
                cta="Run a lift test",
                offer="Open-source local demo",
                body_copy="Track the chain from generated prompt to incremental revenue.",
                ai_generated=True,
                human_edited=idx % 2 == 0,
                approval_status=status,
                compliance_status="approved" if status == ApprovalStatus.approved else "pending_review",
                metrics_snapshot={
                    "spend": 7500 + idx * 1200,
                    "revenue": 14200 + idx * 2400,
                    "lift": round(0.04 + idx * 0.013, 3),
                    "conversions": 80 + idx * 14,
                },
            )
        self.experiments: dict[UUID, ExperimentRead] = {
            _u(201): ExperimentRead(
                id=_u(201),
                organization_id=DEMO_ORG_ID,
                name="AI video vs static control",
                hypothesis="Proof-led generated video creates higher signup conversion than static control.",
                primary_metric="signup",
                guardrail_metric="cost_per_signup",
                variants=[
                    ExperimentVariantInput(key="control", creative_treatment_id=_u(105), allocation=0.5, is_control=True),
                    ExperimentVariantInput(key="ai_video", creative_treatment_id=_u(101), allocation=0.5),
                ],
                channel="paid_social",
                status=ExperimentStatus.running,
            ),
            _u(202): ExperimentRead(
                id=_u(202),
                organization_id=DEMO_ORG_ID,
                name="Email subject line urgency test",
                hypothesis="Measurement-first urgency improves activation without unsubscribes.",
                primary_metric="activation",
                guardrail_metric="unsubscribe",
                variants=[
                    ExperimentVariantInput(key="control", creative_treatment_id=_u(105), allocation=0.5, is_control=True),
                    ExperimentVariantInput(key="measurement_angle", creative_treatment_id=_u(101), allocation=0.5),
                ],
                channel="email",
                status=ExperimentStatus.running,
            ),
        }
        self.events: list[EventIn] = []
        self.event_organization_ids: list[UUID] = []
        self.idempotency_keys: set[str] = set()
        self.audit_logs: list[AuditLogRead] = []
        self.event_quality_snapshots: list[EventQualitySnapshotRead] = []
        self.api_keys: dict[UUID, ApiKeyRead] = {}
        self.bandits: dict[UUID, dict] = {}
        self.runs: dict[UUID, RunRead] = {}

    def audit(self, action: str, target_type: str, target_id: str | None = None, **metadata: object) -> None:
        self.audit_logs.append(
            AuditLogRead(
                id=uuid4(),
                organization_id=DEMO_ORG_ID,
                action=action,
                target_type=target_type,
                target_id=target_id,
                metadata=metadata,
                created_at=datetime.now(UTC),
            )
        )

    def create_api_key(self, name: str, scopes: list[str]) -> ApiKeyRead:
        raw, prefix, _hashed = generate_api_key()
        api_key = ApiKeyRead(
            id=uuid4(),
            organization_id=DEMO_ORG_ID,
            name=name,
            prefix=prefix,
            scopes=scopes,
            raw_key=raw,
            created_at=datetime.now(UTC),
        )
        self.api_keys[api_key.id] = api_key
        self.audit("api_key.created", "api_key", str(api_key.id), prefix=prefix)
        return api_key


store = DemoStore()
