from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from app.schemas.common import (
    ApprovalStatus,
    ApiKeyCreate,
    BanditCreate,
    BanditUpdate,
    BrandPackCreate,
    BriefCreate,
    ClaimEvidenceCreate,
    CreativeTreatmentCreate,
    EventIn,
    ExperimentCreate,
    ExperimentStatus,
    ExperimentVariantInput,
    OrganizationCreate,
    RunCreate,
)
from app.services.core_repositories import InMemoryCoreRepository, create_core_repository
from app.services.demo_store import DemoStore


def test_core_repository_creates_and_gets_organizations() -> None:
    repository = InMemoryCoreRepository(DemoStore())
    created = repository.create_organization(OrganizationCreate(name="Acme Lift", slug="acme-lift"))

    assert created.name == "Acme Lift"
    assert repository.get_organization(created.id) == created
    assert repository.get_organization(uuid4()) is None


def test_core_repository_brand_packs_and_briefs_filter_by_organization() -> None:
    repository = InMemoryCoreRepository(DemoStore())
    org_a = uuid4()
    org_b = uuid4()

    brand_pack = repository.create_brand_pack(
        BrandPackCreate(
            name="Org A brand",
            voice="Evidence-led.",
            guardrails={"claims_require_evidence": True},
            prohibited_claims=["guaranteed revenue"],
        ),
        org_a,
    )
    repository.create_brand_pack(BrandPackCreate(name="Org B brand"), org_b)
    brief = repository.create_brief(
        BriefCreate(
            name="Org A brief",
            objective="Increase demo requests",
            target_audience="Growth teams",
            channel="paid_social",
            primary_kpi="signup",
            brand_pack_id=brand_pack.id,
        ),
        org_a,
    )
    repository.create_brief(
        BriefCreate(
            name="Org B brief",
            objective="Increase activation",
            target_audience="Trial users",
            channel="email",
            primary_kpi="activation",
        ),
        org_b,
    )

    assert repository.list_brand_packs(org_a) == [brand_pack]
    assert repository.list_briefs(org_a) == [brief]
    assert repository.get_brief(brief.id, org_a) == brief
    assert repository.get_brief(brief.id, org_b) is None


def test_core_repository_api_keys_and_audit_logs_filter_by_organization() -> None:
    repository = InMemoryCoreRepository(DemoStore())
    org_a = uuid4()
    org_b = uuid4()

    created = repository.create_api_key(ApiKeyCreate(name="Events writer", scopes=["events:write"]), org_a)
    repository.create_api_key(ApiKeyCreate(name="Other writer", scopes=["events:write"]), org_b)
    audit = repository.record_audit(
        "api_key.created",
        "api_key",
        org_a,
        str(created.id),
        {"prefix": created.prefix},
    )
    repository.record_audit("api_key.created", "api_key", org_b)

    listed = repository.list_api_keys(org_a)
    deleted = repository.delete_api_key(created.id, org_a)

    assert created.raw_key and created.raw_key.startswith("clai_")
    assert len(listed) == 1
    assert listed[0].id == created.id
    assert listed[0].raw_key is None
    assert repository.list_audit_logs(org_a) == [audit]
    assert deleted is True
    assert repository.list_api_keys(org_a) == []


def test_core_repository_claim_evidence_filters_by_organization() -> None:
    repository = InMemoryCoreRepository(DemoStore())
    org_a = uuid4()
    org_b = uuid4()

    created = repository.create_claim_evidence(
        ClaimEvidenceCreate(
            claim="Measure lift before scaling spend.",
            evidence_url="https://example.com/a",
            source_name="Source A",
        ),
        org_a,
    )
    repository.create_claim_evidence(
        ClaimEvidenceCreate(
            claim="Unsupported for org A.",
            evidence_url="https://example.com/b",
            source_name="Source B",
        ),
        org_b,
    )

    assert repository.list_claim_evidence(org_a) == [created]


def test_core_repository_creative_treatments_filter_and_update_by_organization() -> None:
    repository = InMemoryCoreRepository(DemoStore())
    org_a = uuid4()
    org_b = uuid4()

    created = repository.create_creative_treatment(
        CreativeTreatmentCreate(
            name="Proof angle",
            objective="Increase demo requests",
            target_audience="Growth teams",
            channel="paid_social",
            body_copy="Measure lift before scaling spend.",
        ),
        org_a,
    )
    repository.create_creative_treatment(
        CreativeTreatmentCreate(
            name="Other org angle",
            objective="Increase activation",
            target_audience="Trial users",
            channel="email",
        ),
        org_b,
    )
    approved = created.model_copy(update={"approval_status": ApprovalStatus.approved})

    saved = repository.update_creative_treatment(approved, org_a)

    assert saved == approved
    assert repository.list_creative_treatments(org_a, ApprovalStatus.approved) == [approved]
    assert repository.get_creative_treatment(created.id, org_a) == approved
    assert repository.get_creative_treatment(created.id, org_b) is None


def test_core_repository_experiments_filter_and_update_by_organization() -> None:
    repository = InMemoryCoreRepository(DemoStore())
    org_a = uuid4()
    org_b = uuid4()
    control_id = UUID("00000000-0000-0000-0000-000000000105")
    treatment_id = UUID("00000000-0000-0000-0000-000000000101")

    created = repository.create_experiment(
        ExperimentCreate(
            name="Signup lift",
            hypothesis="Treatment improves signup.",
            primary_metric="signup",
            guardrail_metric="cost_per_signup",
            variants=[
                ExperimentVariantInput(
                    key="control",
                    creative_treatment_id=control_id,
                    allocation=0.5,
                    is_control=True,
                ),
                ExperimentVariantInput(
                    key="treatment",
                    creative_treatment_id=treatment_id,
                    allocation=0.5,
                ),
            ],
            channel="paid_social",
        ),
        org_a,
    )
    repository.create_experiment(
        ExperimentCreate(
            name="Other org test",
            hypothesis="Email improves activation.",
            primary_metric="activation",
            variants=[
                ExperimentVariantInput(key="control", allocation=0.5, is_control=True),
                ExperimentVariantInput(key="treatment", allocation=0.5),
            ],
            channel="email",
        ),
        org_b,
    )
    running = created.model_copy(update={"status": ExperimentStatus.running, "starts_at": datetime.now(UTC)})

    saved = repository.update_experiment(running, org_a)

    assert saved == running
    assert repository.list_experiments(org_a) == [running]
    assert repository.get_experiment(created.id, org_a) == running
    assert repository.get_experiment(created.id, org_b) is None


def test_core_repository_bandits_filter_and_update_by_organization() -> None:
    repository = InMemoryCoreRepository(DemoStore())
    org_a = uuid4()
    org_b = uuid4()

    created = repository.create_bandit(BanditCreate(name="CTA bandit", arms=["control", "variant"]), org_a)
    repository.create_bandit(BanditCreate(name="Other bandit", arms=["control", "variant"]), org_b)

    updated = repository.update_bandit_arm(created["id"], BanditUpdate(arm="variant", success=True), org_a)

    assert updated is not None
    assert updated["arms"]["variant"]["alpha"] == 2.0
    assert updated["arms"]["variant"]["beta"] == 1.0
    assert repository.get_bandit(created["id"], org_a) == updated
    assert repository.get_bandit(created["id"], org_b) is None
    assert repository.update_bandit_arm(created["id"], BanditUpdate(arm="missing", success=True), org_a) is None


def test_core_repository_measurement_runs_filter_by_organization() -> None:
    repository = InMemoryCoreRepository(DemoStore())
    org_a = uuid4()
    org_b = uuid4()

    uplift = repository.create_uplift_run(RunCreate(name="Uplift demo", config={"segment": "trial"}), org_a)
    mmm = repository.create_mmm_run(RunCreate(name="MMM demo", config={"weeks": 12}), org_a)
    repository.create_uplift_run(RunCreate(name="Other uplift"), org_b)
    repository.create_mmm_run(RunCreate(name="Other MMM"), org_b)

    assert repository.get_uplift_run(uplift.id, org_a) == uplift
    assert repository.get_uplift_run(uplift.id, org_b) is None
    assert repository.get_mmm_run(mmm.id, org_a) == mmm
    assert repository.get_mmm_run(mmm.id, org_b) is None
    assert uplift.result["note"]
    assert mmm.result["channels"]["paid_social"] == 0.42


def test_core_repository_event_ingestion_deduplicates_batch_idempotency_key() -> None:
    repository = InMemoryCoreRepository(DemoStore())
    org_id = uuid4()
    other_org_id = uuid4()
    event = EventIn(
        event_name="purchase",
        timestamp=datetime.now(UTC),
        anonymous_id="anon-core-repo",
        creative_treatment_id=UUID("00000000-0000-0000-0000-000000000101"),
        value=49,
        currency="USD",
    )

    accepted, deduplicated = repository.ingest_events([event], org_id, "evt-core-repo")
    second_accepted, second_deduplicated = repository.ingest_events([event], org_id, "evt-core-repo")
    other_accepted, other_deduplicated = repository.ingest_events(
        [event.model_copy(update={"anonymous_id": "anon-other-org-same-key"})],
        other_org_id,
        "evt-core-repo",
    )
    repository.ingest_events(
        [event.model_copy(update={"anonymous_id": "anon-other-org"})],
        other_org_id,
        "evt-other-org",
    )

    assert (accepted, deduplicated) == (1, 0)
    assert (second_accepted, second_deduplicated) == (0, 1)
    assert (other_accepted, other_deduplicated) == (1, 0)
    assert [item.anonymous_id for item in repository.list_events(org_id)] == ["anon-core-repo"]


def test_core_repository_factory_and_sqlalchemy_backend_are_lazy() -> None:
    repository = create_core_repository("memory")
    source = (Path(__file__).resolve().parents[1] / "app" / "services" / "core_repositories.py").read_text()

    assert isinstance(repository, InMemoryCoreRepository)
    assert "class SQLAlchemyCoreRepository" in source
    assert 'selected_backend == "sqlalchemy"' in source
    assert "from sqlalchemy import" not in source.split("class SQLAlchemyCoreRepository")[0]
    assert source.index('selected_backend == "sqlalchemy"') < source.index("from app.db.session import SessionLocal")
