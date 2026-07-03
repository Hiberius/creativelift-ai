from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.schemas.common import (
    ApprovalStatus,
    BrandPackCreate,
    BriefCreate,
    ClaimEvidenceCreate,
    CreativeTreatmentCreate,
    DemoScenarioRead,
    EventHealthRead,
    EventIn,
    EventIngestResponse,
    ExperimentCreate,
    ExperimentStatus,
    ExperimentVariantInput,
    OrganizationCreate,
)
from app.services.core_repositories import CoreRepository
from app.services.event_quality import capture_event_quality_snapshot, event_health_summary
from app.services.experiment_insights import build_experiment_insight
from app.services.measurement import experiment_result_from_events


def _scenario_events(*, experiment_id: str, control_id: str, treatment_id: str) -> list[EventIn]:
    timestamp = datetime.now(UTC)
    events: list[EventIn] = []
    for index in range(100):
        actor = f"demo-control-{index}"
        events.append(
            EventIn(
                event_name="impression",
                timestamp=timestamp,
                anonymous_id=actor,
                creative_treatment_id=control_id,
                experiment_id=experiment_id,
                variant_id="control",
                channel="paid_social",
                placement="feed",
            )
        )
        if index < 6:
            events.append(
                EventIn(
                    event_name="signup",
                    timestamp=timestamp,
                    anonymous_id=actor,
                    creative_treatment_id=control_id,
                    experiment_id=experiment_id,
                    variant_id="control",
                    channel="paid_social",
                    placement="feed",
                    value=80,
                    currency="USD",
                )
            )
    for index in range(100):
        actor = f"demo-treatment-{index}"
        events.append(
            EventIn(
                event_name="impression",
                timestamp=timestamp,
                anonymous_id=actor,
                creative_treatment_id=treatment_id,
                experiment_id=experiment_id,
                variant_id="ai_proof",
                channel="paid_social",
                placement="feed",
            )
        )
        if index < 18:
            events.append(
                EventIn(
                    event_name="signup",
                    timestamp=timestamp,
                    anonymous_id=actor,
                    creative_treatment_id=treatment_id,
                    experiment_id=experiment_id,
                    variant_id="ai_proof",
                    channel="paid_social",
                    placement="feed",
                    value=80,
                    currency="USD",
                )
            )
    return events


def create_demo_scenario(repository: CoreRepository) -> DemoScenarioRead:
    suffix = uuid4().hex[:8]
    organization = repository.create_organization(
        OrganizationCreate(name=f"CreativeLift Demo {suffix}", slug=f"creativelift-demo-{suffix}")
    )
    from app.db.tenant import set_current_organization

    set_current_organization(organization.id)
    repository.record_audit("organization.created", "organization", organization.id, str(organization.id))

    brand_pack = repository.create_brand_pack(
        BrandPackCreate(
            name="Proof-led growth brand",
            voice="Evidence-led, specific, direct.",
            guardrails={"claims_require_evidence": True, "tone": "operator-grade"},
            prohibited_claims=["guaranteed revenue", "risk free growth"],
        ),
        organization.id,
    )
    repository.record_audit("brand_pack.created", "brand_pack", organization.id, str(brand_pack.id))

    claim_evidence = repository.create_claim_evidence(
        ClaimEvidenceCreate(
            brand_pack_id=brand_pack.id,
            claim="Measure incremental lift before scaling spend.",
            evidence_url="https://example.com/lift-methodology",
            source_name="CreativeLift demo methodology",
            notes="Seeded by the one-click demo scenario.",
        ),
        organization.id,
    )
    repository.record_audit(
        "claim_evidence.created",
        "claim_evidence",
        organization.id,
        str(claim_evidence.id),
        {"claim": claim_evidence.claim},
    )

    brief = repository.create_brief(
        BriefCreate(
            brand_pack_id=brand_pack.id,
            name="Meta proof angle lift test",
            objective="Increase qualified demo requests from paid social",
            target_audience="B2B SaaS growth teams comparing AI attribution tools",
            channel="paid_social",
            primary_kpi="signup",
            body="Compare a baseline product-control angle against a proof-led AI creative angle.",
        ),
        organization.id,
    )
    repository.record_audit("brief.created", "brief", organization.id, str(brief.id))

    control = repository.create_creative_treatment(
        CreativeTreatmentCreate(
            brief_id=brief.id,
            brand_pack_id=brand_pack.id,
            name="Control: platform ROAS angle",
            objective=brief.objective,
            target_audience=brief.target_audience,
            channel=brief.channel,
            placement="feed",
            angle="baseline",
            hook="Know which campaigns are working.",
            cta="Book a demo",
            body_copy="Connect your marketing data and inspect performance in one place.",
            ai_generated=False,
            human_edited=True,
        ),
        organization.id,
    )
    treatment = repository.create_creative_treatment(
        CreativeTreatmentCreate(
            brief_id=brief.id,
            brand_pack_id=brand_pack.id,
            name="Treatment: proof-led incrementality angle",
            objective=brief.objective,
            target_audience=brief.target_audience,
            channel=brief.channel,
            placement="feed",
            angle="proof",
            hook="Stop scaling creative before you know its incremental lift.",
            cta="Run a lift test",
            body_copy="CreativeLift ties AI creative, approval evidence, and experiment results into one decision trail.",
            ai_generated=True,
            human_edited=True,
        ),
        organization.id,
    )
    evidence_urls = [claim_evidence.evidence_url]
    control = control.model_copy(
        update={
            "approval_status": ApprovalStatus.approved,
            "compliance_status": "approved",
            "metrics_snapshot": {"claim_evidence_urls": evidence_urls},
        }
    )
    treatment = treatment.model_copy(
        update={
            "approval_status": ApprovalStatus.approved,
            "compliance_status": "approved",
            "metrics_snapshot": {"claim_evidence_urls": evidence_urls},
        }
    )
    repository.update_creative_treatment(control, organization.id)
    repository.update_creative_treatment(treatment, organization.id)
    repository.record_audit("creative_treatment.approved", "creative_treatment", organization.id, str(control.id))
    repository.record_audit("creative_treatment.approved", "creative_treatment", organization.id, str(treatment.id))

    experiment = repository.create_experiment(
        ExperimentCreate(
            name="Proof-led creative vs control",
            hypothesis="A proof-led incrementality angle will increase signup conversion against a baseline ROAS angle.",
            primary_metric="signup",
            guardrail_metric="cost_per_signup",
            variants=[
                ExperimentVariantInput(key="control", creative_treatment_id=control.id, allocation=0.5, is_control=True),
                ExperimentVariantInput(key="ai_proof", creative_treatment_id=treatment.id, allocation=0.5),
            ],
            channel="paid_social",
            decision_rule="95% confidence, valid SRM, positive signup lift",
            notes="Generated by one-click demo scenario.",
        ),
        organization.id,
    )
    experiment = experiment.model_copy(update={"status": ExperimentStatus.running, "starts_at": datetime.now(UTC)})
    repository.update_experiment(experiment, organization.id)
    repository.record_audit("experiment.running", "experiment", organization.id, str(experiment.id))

    events = _scenario_events(
        experiment_id=str(experiment.id),
        control_id=str(control.id),
        treatment_id=str(treatment.id),
    )
    accepted, deduplicated = repository.ingest_events(events, organization.id, f"demo-scenario-{suffix}")
    repository.record_audit("events.ingested", "event", organization.id, metadata={"count": accepted})
    capture_event_quality_snapshot(repository, organization.id)
    experiment = experiment.model_copy(update={"status": ExperimentStatus.completed, "ends_at": datetime.now(UTC)})
    repository.update_experiment(experiment, organization.id)
    repository.record_audit("experiment.completed", "experiment", organization.id, str(experiment.id))

    scenario_events = repository.list_events(organization.id, limit=None)
    result = experiment_result_from_events(str(experiment.id), experiment.variants, scenario_events)
    if result is None:
        raise RuntimeError("Demo scenario did not produce experiment results")
    insight = build_experiment_insight(experiment, result)
    event_health = EventHealthRead(**event_health_summary(scenario_events))

    return DemoScenarioRead(
        organization=organization,
        brand_pack=brand_pack,
        brief=brief,
        claim_evidence=claim_evidence,
        creatives=[control, treatment],
        experiment=experiment,
        ingestion=EventIngestResponse(accepted=accepted, deduplicated=deduplicated, organization_id=organization.id),
        event_health=event_health,
        result=result,
        insight=insight,
        results_url=f"/app/experiments/{experiment.id}/results",
    )
