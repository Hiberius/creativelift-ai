from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from random import betavariate
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status

from app.api.v1.endpoints.connectors import router as modular_connectors_router
from app.api.v1.endpoints.measurement import router as modular_measurement_router
from app.api.v1.endpoints.prompt_runs import router as modular_prompt_runs_router
from app.core.rate_limit import rate_limiter
from app.core.security import Principal, get_principal, set_demo_organization_id
from app.schemas.common import (
    ApiKeyCreate,
    ApiKeyRead,
    ApprovalStatus,
    AuditLogRead,
    BanditCreate,
    BanditDecision,
    BanditUpdate,
    BrandPackCreate,
    BrandPackRead,
    BriefCreate,
    BriefRead,
    ClaimEvidenceCreate,
    ClaimEvidenceRead,
    CreativeTreatmentCreate,
    CreativeTreatmentRead,
    DemoScenarioRead,
    EventBatchIn,
    EventHealthRead,
    EventQualitySnapshotRead,
    EventIn,
    EventIngestResponse,
    ExperimentAssignment,
    ExperimentCreate,
    ExperimentInsightRead,
    ExperimentRead,
    ExperimentStatus,
    MeasurementAnalysisRead,
    MeasurementAnalyzeRequest,
    MeasurementCsvImportRead,
    MeasurementCsvImportRequest,
    MeasurementReportCreate,
    MeasurementReportRead,
    MeasurementReportSummaryRead,
    OrganizationCreate,
    OrganizationRead,
    ReviewDecision,
    RunCreate,
    RunRead,
    VariantGenerateRequest,
    GeneratedVariant,
)
from app.services.core_repositories import core_repository
from app.services.demo_scenario import create_demo_scenario
from app.services.event_quality import capture_event_quality_snapshot, event_health_summary
from app.services.experiment_insights import build_experiment_insight
from app.services.generator import provider_for
from app.services.measurement import analyze_observed_variants, demo_experiment_result, experiment_result_from_events
from app.services.measurement_reports import (
    clear_measurement_reports,
    create_measurement_report,
    export_measurement_reports,
    import_measurement_reports_from_csv,
    list_measurement_reports,
    summarize_measurement_reports,
)

router = APIRouter()

for modular_router in (
    modular_prompt_runs_router,
    modular_measurement_router,
    modular_connectors_router,
):
    router.include_router(modular_router)


def _record_audit(
    action: str,
    target_type: str,
    organization_id: UUID,
    target_id: str | None = None,
    **metadata: object,
) -> AuditLogRead:
    return core_repository.record_audit(action, target_type, organization_id, target_id, dict(metadata))


@router.post("/organizations", response_model=OrganizationRead, tags=["organizations"])
async def create_organization(payload: OrganizationCreate) -> OrganizationRead:
    item = core_repository.create_organization(payload)
    set_demo_organization_id(item.id)
    _record_audit("organization.created", "organization", item.id, str(item.id))
    return item


@router.get("/me", tags=["auth"])
async def me(principal: Principal = Depends(get_principal)) -> dict:
    organization = core_repository.get_organization(principal.organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {
        "organization": organization,
        "principal": {
            "organization_id": principal.organization_id,
            "user_id": principal.user_id,
            "role": principal.role,
            "scopes": principal.scopes,
        },
    }


@router.post("/demo/scenario", response_model=DemoScenarioRead, tags=["demo"])
async def run_demo_scenario() -> DemoScenarioRead:
    scenario = create_demo_scenario(core_repository)
    set_demo_organization_id(scenario.organization.id)
    return scenario


@router.post("/demo/analyze", response_model=MeasurementAnalysisRead, tags=["demo", "measurement"])
async def analyze_demo_measurement(payload: MeasurementAnalyzeRequest) -> MeasurementAnalysisRead:
    return analyze_observed_variants(payload)


@router.post("/demo/reports", response_model=MeasurementReportRead, tags=["demo", "measurement"])
async def create_demo_measurement_report(payload: MeasurementReportCreate) -> MeasurementReportRead:
    return create_measurement_report(payload)


@router.get("/demo/reports", response_model=list[MeasurementReportRead], tags=["demo", "measurement"])
async def list_demo_measurement_reports(limit: int = Query(default=20, ge=1, le=100)) -> list[MeasurementReportRead]:
    return list_measurement_reports(limit)


@router.get("/demo/reports/summary", response_model=MeasurementReportSummaryRead, tags=["demo", "measurement"])
async def summarize_demo_measurement_reports(
    limit: int = Query(default=100, ge=1, le=100),
) -> MeasurementReportSummaryRead:
    return summarize_measurement_reports(limit)


@router.delete("/demo/reports", status_code=status.HTTP_204_NO_CONTENT, tags=["demo", "measurement"])
async def clear_demo_measurement_reports() -> Response:
    clear_measurement_reports()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/demo/reports/export", tags=["demo", "measurement"])
async def export_demo_measurement_reports(
    format: str = Query(default="csv", pattern="^(csv|json|markdown)$"),
    limit: int = Query(default=100, ge=1, le=100),
) -> Response:
    content, media_type, filename = export_measurement_reports(format, limit)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/demo/reports/import", response_model=MeasurementCsvImportRead, tags=["demo", "measurement"])
async def import_demo_measurement_reports(payload: MeasurementCsvImportRequest) -> MeasurementCsvImportRead:
    return import_measurement_reports_from_csv(payload)


@router.post("/brand-packs", response_model=BrandPackRead, tags=["brand packs"])
async def create_brand_pack(payload: BrandPackCreate, principal: Principal = Depends(get_principal)) -> BrandPackRead:
    item = core_repository.create_brand_pack(payload, principal.organization_id)
    _record_audit("brand_pack.created", "brand_pack", principal.organization_id, str(item.id))
    return item


@router.get("/brand-packs", response_model=list[BrandPackRead], tags=["brand packs"])
async def list_brand_packs(principal: Principal = Depends(get_principal)) -> list[BrandPackRead]:
    return core_repository.list_brand_packs(principal.organization_id)


@router.post("/claim-evidence", response_model=ClaimEvidenceRead, tags=["claim evidence"])
async def create_claim_evidence(
    payload: ClaimEvidenceCreate, principal: Principal = Depends(get_principal)
) -> ClaimEvidenceRead:
    item = core_repository.create_claim_evidence(payload, principal.organization_id)
    _record_audit("claim_evidence.created", "claim_evidence", principal.organization_id, str(item.id), claim=payload.claim)
    return item


@router.get("/claim-evidence", response_model=list[ClaimEvidenceRead], tags=["claim evidence"])
async def list_claim_evidence(principal: Principal = Depends(get_principal)) -> list[ClaimEvidenceRead]:
    return core_repository.list_claim_evidence(principal.organization_id)


@router.post("/briefs", response_model=BriefRead, tags=["briefs"])
async def create_brief(payload: BriefCreate, principal: Principal = Depends(get_principal)) -> BriefRead:
    item = core_repository.create_brief(payload, principal.organization_id)
    _record_audit("brief.created", "brief", principal.organization_id, str(item.id))
    return item


@router.get("/briefs", response_model=list[BriefRead], tags=["briefs"])
async def list_briefs(principal: Principal = Depends(get_principal)) -> list[BriefRead]:
    return core_repository.list_briefs(principal.organization_id)


@router.get("/briefs/{brief_id}", response_model=BriefRead, tags=["briefs"])
async def get_brief(brief_id: UUID, principal: Principal = Depends(get_principal)) -> BriefRead:
    item = core_repository.get_brief(brief_id, principal.organization_id)
    if not item:
        raise HTTPException(status_code=404, detail="Brief not found")
    return item


@router.post("/creative-treatments", response_model=CreativeTreatmentRead, tags=["creative treatments"])
async def create_creative(
    payload: CreativeTreatmentCreate, principal: Principal = Depends(get_principal)
) -> CreativeTreatmentRead:
    item = core_repository.create_creative_treatment(payload, principal.organization_id)
    _record_audit("creative_treatment.created", "creative_treatment", principal.organization_id, str(item.id))
    return item


@router.get("/creative-treatments", response_model=list[CreativeTreatmentRead], tags=["creative treatments"])
async def list_creatives(
    status_filter: ApprovalStatus | None = None,
    principal: Principal = Depends(get_principal),
) -> list[CreativeTreatmentRead]:
    return core_repository.list_creative_treatments(principal.organization_id, status_filter)


@router.get("/creative-treatments/{creative_id}", response_model=CreativeTreatmentRead, tags=["creative treatments"])
async def get_creative(creative_id: UUID, principal: Principal = Depends(get_principal)) -> CreativeTreatmentRead:
    item = core_repository.get_creative_treatment(creative_id, principal.organization_id)
    if not item:
        raise HTTPException(status_code=404, detail="Creative treatment not found")
    return item


def _set_approval(
    creative_id: UUID,
    status_value: ApprovalStatus,
    notes: str,
    organization_id: UUID,
    claim_evidence_urls: list[str] | None = None,
) -> CreativeTreatmentRead:
    existing = core_repository.get_creative_treatment(creative_id, organization_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Creative treatment not found")
    evidence_urls = claim_evidence_urls or []
    compliance_status = status_value.value
    metrics_snapshot = dict(existing.metrics_snapshot)
    if evidence_urls:
        metrics_snapshot["claim_evidence_urls"] = evidence_urls
    if status_value == ApprovalStatus.approved:
        brand_pack = (
            core_repository.get_brand_pack(existing.brand_pack_id, organization_id)
            if existing.brand_pack_id
            else None
        )
        requires_evidence = bool(brand_pack and brand_pack.guardrails.get("claims_require_evidence"))
        if requires_evidence and not evidence_urls and not existing.approved_claim_ids:
            compliance_status = "approved_needs_evidence"
    updated = existing.model_copy(
        update={
            "approval_status": status_value,
            "compliance_status": compliance_status,
            "metrics_snapshot": metrics_snapshot,
        }
    )
    saved = core_repository.update_creative_treatment(updated, organization_id)
    if not saved:
        raise HTTPException(status_code=404, detail="Creative treatment not found")
    _record_audit(
        f"creative_treatment.{status_value.value}",
        "creative_treatment",
        organization_id,
        str(creative_id),
        notes=notes,
        evidence_count=len(evidence_urls),
        compliance_status=compliance_status,
    )
    return saved


@router.post("/creative-treatments/{creative_id}/approve", response_model=CreativeTreatmentRead, tags=["approvals"])
async def approve_creative(
    creative_id: UUID,
    payload: ReviewDecision,
    principal: Principal = Depends(get_principal),
) -> CreativeTreatmentRead:
    return _set_approval(
        creative_id,
        ApprovalStatus.approved,
        payload.notes,
        principal.organization_id,
        payload.claim_evidence_urls,
    )


@router.post("/creative-treatments/{creative_id}/reject", response_model=CreativeTreatmentRead, tags=["approvals"])
async def reject_creative(
    creative_id: UUID,
    payload: ReviewDecision,
    principal: Principal = Depends(get_principal),
) -> CreativeTreatmentRead:
    return _set_approval(creative_id, ApprovalStatus.rejected, payload.notes, principal.organization_id)


@router.post("/variants/generate", response_model=list[GeneratedVariant], tags=["generation"])
async def generate_variants(
    payload: VariantGenerateRequest,
    principal: Principal = Depends(get_principal),
) -> list[GeneratedVariant]:
    provider = provider_for(payload.provider)
    variants = await provider.generate_variants(
        payload.brief, payload.brand_pack, payload.n, payload.temperature
    )
    _record_audit(
        "variants.generated",
        "prompt_run",
        principal.organization_id,
        provider=payload.provider,
        count=len(variants),
    )
    return variants


@router.post("/experiments", response_model=ExperimentRead, tags=["experiments"])
async def create_experiment(payload: ExperimentCreate, principal: Principal = Depends(get_principal)) -> ExperimentRead:
    item = core_repository.create_experiment(payload, principal.organization_id)
    _record_audit("experiment.created", "experiment", principal.organization_id, str(item.id))
    return item


@router.get("/experiments", response_model=list[ExperimentRead], tags=["experiments"])
async def list_experiments(principal: Principal = Depends(get_principal)) -> list[ExperimentRead]:
    return core_repository.list_experiments(principal.organization_id)


@router.get("/experiments/{experiment_id}", response_model=ExperimentRead, tags=["experiments"])
async def get_experiment(experiment_id: UUID, principal: Principal = Depends(get_principal)) -> ExperimentRead:
    experiment = core_repository.get_experiment(experiment_id, principal.organization_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment


@router.get("/experiments/{experiment_id}/assign", response_model=ExperimentAssignment, tags=["experiments"])
async def assign_experiment_variant(
    experiment_id: UUID,
    unit_id: str = Query(min_length=1, max_length=255),
    principal: Principal = Depends(get_principal),
) -> ExperimentAssignment:
    experiment = core_repository.get_experiment(experiment_id, principal.organization_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    bucket = int.from_bytes(sha256(f"{experiment_id}:{unit_id}".encode("utf-8")).digest()[:8], "big") / 2**64
    cumulative = 0.0
    selected = experiment.variants[-1]
    for variant in experiment.variants:
        cumulative += variant.allocation
        if bucket < cumulative:
            selected = variant
            break
    return ExperimentAssignment(
        experiment_id=experiment_id,
        unit_id=unit_id,
        variant_key=selected.key,
        creative_treatment_id=selected.creative_treatment_id,
        allocation=selected.allocation,
        is_control=selected.is_control,
    )


def _set_experiment_status(experiment_id: UUID, status_value: ExperimentStatus, organization_id: UUID) -> ExperimentRead:
    experiment = core_repository.get_experiment(experiment_id, organization_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if status_value == ExperimentStatus.running:
        _validate_experiment_launch(experiment)
    update: dict = {"status": status_value}
    if status_value == ExperimentStatus.running:
        update["starts_at"] = datetime.now(UTC)
    if status_value in {ExperimentStatus.completed, ExperimentStatus.invalidated}:
        update["ends_at"] = datetime.now(UTC)
    updated = experiment.model_copy(update=update)
    saved = core_repository.update_experiment(updated, organization_id)
    if not saved:
        raise HTTPException(status_code=404, detail="Experiment not found")
    _record_audit(f"experiment.{status_value.value}", "experiment", organization_id, str(experiment_id))
    return saved


def _validate_experiment_launch(experiment: ExperimentRead) -> None:
    if len(experiment.variants) < 2:
        raise HTTPException(status_code=409, detail="Experiment requires at least two variants before launch")
    if not any(variant.is_control for variant in experiment.variants):
        raise HTTPException(status_code=409, detail="Experiment requires one control variant before launch")
    if not any(not variant.is_control for variant in experiment.variants):
        raise HTTPException(status_code=409, detail="Experiment requires at least one treatment variant before launch")

    for variant in experiment.variants:
        if not variant.creative_treatment_id:
            raise HTTPException(
                status_code=409,
                detail=f"Variant {variant.key} requires a Creative Treatment before launch",
            )
        creative = core_repository.get_creative_treatment(variant.creative_treatment_id, experiment.organization_id)
        if not creative:
            raise HTTPException(
                status_code=409,
                detail=f"Variant {variant.key} references an unknown Creative Treatment",
            )
        if creative.approval_status != ApprovalStatus.approved:
            raise HTTPException(
                status_code=409,
                detail=f"Creative Treatment for variant {variant.key} must be approved before launch",
            )
        if creative.compliance_status == "approved_needs_evidence":
            raise HTTPException(
                status_code=409,
                detail=f"Creative Treatment for variant {variant.key} needs claim evidence before launch",
            )


@router.post("/experiments/{experiment_id}/start", response_model=ExperimentRead, tags=["experiments"])
async def start_experiment(experiment_id: UUID, principal: Principal = Depends(get_principal)) -> ExperimentRead:
    return _set_experiment_status(experiment_id, ExperimentStatus.running, principal.organization_id)


@router.post("/experiments/{experiment_id}/pause", response_model=ExperimentRead, tags=["experiments"])
async def pause_experiment(experiment_id: UUID, principal: Principal = Depends(get_principal)) -> ExperimentRead:
    return _set_experiment_status(experiment_id, ExperimentStatus.paused, principal.organization_id)


@router.post("/experiments/{experiment_id}/complete", response_model=ExperimentRead, tags=["experiments"])
async def complete_experiment(experiment_id: UUID, principal: Principal = Depends(get_principal)) -> ExperimentRead:
    return _set_experiment_status(experiment_id, ExperimentStatus.completed, principal.organization_id)


@router.get("/experiments/{experiment_id}/results", tags=["experiments", "measurement"])
async def experiment_results(experiment_id: UUID, principal: Principal = Depends(get_principal)) -> dict:
    experiment = core_repository.get_experiment(experiment_id, principal.organization_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    events = core_repository.list_events(principal.organization_id, limit=None)
    event_result = experiment_result_from_events(str(experiment_id), experiment.variants, events)
    return event_result or demo_experiment_result(str(experiment_id))


@router.get("/experiments/{experiment_id}/insights", response_model=ExperimentInsightRead, tags=["experiments", "measurement"])
async def experiment_insights(experiment_id: UUID, principal: Principal = Depends(get_principal)) -> ExperimentInsightRead:
    experiment = core_repository.get_experiment(experiment_id, principal.organization_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    events = core_repository.list_events(principal.organization_id, limit=None)
    event_result = experiment_result_from_events(str(experiment_id), experiment.variants, events)
    result = event_result or demo_experiment_result(str(experiment_id))
    return build_experiment_insight(experiment, result)


@router.post("/events/ingest", response_model=EventIngestResponse, tags=["events"])
async def ingest_events(
    payload: EventBatchIn,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    principal: Principal = Depends(get_principal),
) -> EventIngestResponse:
    rate_limiter.check(f"events:{principal.api_key_prefix or principal.organization_id}", 600, 60)
    accepted, deduped = core_repository.ingest_events(payload.events, principal.organization_id, idempotency_key)
    _record_audit("events.ingested", "event", principal.organization_id, count=len(payload.events))
    if accepted > 0:
        capture_event_quality_snapshot(core_repository, principal.organization_id)
    return EventIngestResponse(accepted=accepted, deduplicated=deduped, organization_id=principal.organization_id)


@router.get("/events", response_model=list[EventIn], tags=["events"])
async def list_events(
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    principal: Principal = Depends(get_principal),
) -> list[EventIn]:
    return core_repository.list_events(principal.organization_id, limit=limit, offset=offset)


@router.get("/events/health", response_model=EventHealthRead, tags=["events"])
async def event_health(principal: Principal = Depends(get_principal)) -> EventHealthRead:
    return EventHealthRead(**event_health_summary(core_repository.list_events(principal.organization_id, limit=None)))


@router.get("/events/health/history", response_model=list[EventQualitySnapshotRead], tags=["events"])
async def event_health_history(
    limit: int = Query(default=30, ge=1, le=200),
    principal: Principal = Depends(get_principal),
) -> list[EventQualitySnapshotRead]:
    return core_repository.list_event_quality_snapshots(principal.organization_id, limit=limit)


@router.post("/bandits", tags=["bandits"])
async def create_bandit(payload: BanditCreate, principal: Principal = Depends(get_principal)) -> dict:
    item = core_repository.create_bandit(payload, principal.organization_id)
    _record_audit("bandit.created", "bandit", principal.organization_id, str(item["id"]))
    return item


@router.post("/bandits/{bandit_id}/decide", response_model=BanditDecision, tags=["bandits"])
async def decide_bandit(bandit_id: UUID, principal: Principal = Depends(get_principal)) -> BanditDecision:
    bandit = core_repository.get_bandit(bandit_id, principal.organization_id)
    if not bandit:
        raise HTTPException(status_code=404, detail="Bandit not found")
    samples = {
        arm: betavariate(stats["alpha"], stats["beta"])
        for arm, stats in bandit["arms"].items()
    }
    return BanditDecision(chosen_arm=max(samples, key=samples.get), samples=samples)


@router.post("/bandits/{bandit_id}/update", tags=["bandits"])
async def update_bandit(
    bandit_id: UUID,
    payload: BanditUpdate,
    principal: Principal = Depends(get_principal),
) -> dict:
    bandit = core_repository.update_bandit_arm(bandit_id, payload, principal.organization_id)
    if not bandit:
        raise HTTPException(status_code=404, detail="Bandit or arm not found")
    return bandit


@router.post("/uplift/runs", response_model=RunRead, tags=["uplift"])
async def create_uplift_run(payload: RunCreate, principal: Principal = Depends(get_principal)) -> RunRead:
    return core_repository.create_uplift_run(payload, principal.organization_id)


@router.get("/uplift/runs/{run_id}", response_model=RunRead, tags=["uplift"])
async def get_uplift_run(run_id: UUID, principal: Principal = Depends(get_principal)) -> RunRead:
    item = core_repository.get_uplift_run(run_id, principal.organization_id)
    if not item:
        raise HTTPException(status_code=404, detail="Run not found")
    return item


@router.post("/mmms/runs", response_model=RunRead, tags=["mmm"])
async def create_mmm_run(payload: RunCreate, principal: Principal = Depends(get_principal)) -> RunRead:
    return core_repository.create_mmm_run(payload, principal.organization_id)


@router.get("/mmms/runs/{run_id}", response_model=RunRead, tags=["mmm"])
async def get_mmm_run(run_id: UUID, principal: Principal = Depends(get_principal)) -> RunRead:
    item = core_repository.get_mmm_run(run_id, principal.organization_id)
    if not item:
        raise HTTPException(status_code=404, detail="Run not found")
    return item


@router.get("/audit-logs", response_model=list[AuditLogRead], tags=["audit"])
async def audit_logs(principal: Principal = Depends(get_principal)) -> list[AuditLogRead]:
    return core_repository.list_audit_logs(principal.organization_id, limit=100)


@router.post("/api-keys", response_model=ApiKeyRead, tags=["api keys"])
async def create_api_key(payload: ApiKeyCreate, principal: Principal = Depends(get_principal)) -> ApiKeyRead:
    item = core_repository.create_api_key(payload, principal.organization_id)
    _record_audit("api_key.created", "api_key", principal.organization_id, str(item.id), prefix=item.prefix)
    return item


@router.get("/api-keys", response_model=list[ApiKeyRead], tags=["api keys"])
async def list_api_keys(principal: Principal = Depends(get_principal)) -> list[ApiKeyRead]:
    return core_repository.list_api_keys(principal.organization_id)


@router.delete("/api-keys/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["api keys"])
async def delete_api_key(api_key_id: UUID, principal: Principal = Depends(get_principal)) -> None:
    core_repository.delete_api_key(api_key_id, principal.organization_id)
    _record_audit("api_key.deleted", "api_key", principal.organization_id, str(api_key_id))
