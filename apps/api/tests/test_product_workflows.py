from datetime import UTC, datetime
from uuid import uuid4


def test_workspace_and_brand_pack_workflow(client):
    suffix = uuid4().hex[:8]
    organization = client.post(
        "/v1/organizations",
        json={"name": f"Acme Lift {suffix}", "slug": f"acme-lift-{suffix}"},
    )
    assert organization.status_code == 200
    assert organization.json()["slug"] == f"acme-lift-{suffix}"

    me = client.get("/v1/me")
    assert me.status_code == 200
    assert me.json()["organization"]["name"] == f"Acme Lift {suffix}"
    assert me.json()["organization"]["id"] == organization.json()["id"]
    assert me.json()["principal"]["organization_id"] == organization.json()["id"]

    brand_pack = client.post(
        "/v1/brand-packs",
        json={
            "name": f"Brand Pack {suffix}",
            "voice": "Evidence-led and direct.",
            "guardrails": {"claims_require_evidence": True},
            "prohibited_claims": ["guaranteed revenue"],
        },
    )
    assert brand_pack.status_code == 200
    brand_pack_body = brand_pack.json()
    assert brand_pack_body["name"] == f"Brand Pack {suffix}"
    assert brand_pack_body["organization_id"] == organization.json()["id"]

    brand_packs = client.get("/v1/brand-packs")
    assert brand_packs.status_code == 200
    assert any(item["id"] == brand_pack_body["id"] for item in brand_packs.json())

    evidence = client.post(
        "/v1/claim-evidence",
        json={
            "claim": f"Lift claim {suffix}",
            "evidence_url": "https://example.com/evidence",
            "source_name": "Evidence deck",
            "brand_pack_id": brand_pack_body["id"],
            "notes": "Approved test claim.",
        },
    )
    assert evidence.status_code == 200
    evidence_body = evidence.json()
    assert evidence_body["claim"] == f"Lift claim {suffix}"
    assert evidence_body["organization_id"] == organization.json()["id"]

    listed_evidence = client.get("/v1/claim-evidence")
    assert listed_evidence.status_code == 200
    assert any(item["id"] == evidence_body["id"] for item in listed_evidence.json())


def test_api_key_lifecycle(client):
    key = client.post(
        "/v1/api-keys",
        json={"name": "Events writer", "scopes": ["events:write"]},
    )
    assert key.status_code == 200
    key_body = key.json()
    assert key_body["raw_key"].startswith("clai_")

    listed = client.get("/v1/api-keys")
    assert listed.status_code == 200
    listed_key = next(item for item in listed.json() if item["id"] == key_body["id"])
    assert listed_key["raw_key"] is None

    deleted = client.delete(f"/v1/api-keys/{key_body['id']}")
    assert deleted.status_code == 204

    audit_logs = client.get("/v1/audit-logs")
    assert audit_logs.status_code == 200
    actions = [entry["action"] for entry in audit_logs.json()]
    assert "api_key.created" in actions
    assert "api_key.deleted" in actions


def test_bandit_lifecycle(client):
    created = client.post(
        "/v1/bandits",
        json={"name": "CTA allocation", "arms": ["control", "variant"]},
    )
    assert created.status_code == 200
    bandit = created.json()
    assert set(bandit["arms"]) == {"control", "variant"}

    decision = client.post(f"/v1/bandits/{bandit['id']}/decide")
    assert decision.status_code == 200
    assert decision.json()["chosen_arm"] in {"control", "variant"}

    updated = client.post(
        f"/v1/bandits/{bandit['id']}/update",
        json={"arm": "variant", "success": True},
    )
    assert updated.status_code == 200
    assert updated.json()["arms"]["variant"]["alpha"] == 2.0


def test_measurement_run_lifecycle(client):
    uplift = client.post("/v1/uplift/runs", json={"name": "Trial uplift", "config": {"segment": "trial"}})
    assert uplift.status_code == 200
    uplift_body = uplift.json()
    assert uplift_body["model_type"] == "two_model_baseline"
    assert uplift_body["result"]["note"]

    uplift_detail = client.get(f"/v1/uplift/runs/{uplift_body['id']}")
    assert uplift_detail.status_code == 200
    assert uplift_detail.json()["id"] == uplift_body["id"]

    mmm = client.post("/v1/mmms/runs", json={"name": "Weekly MMM", "config": {"weeks": 12}})
    assert mmm.status_code == 200
    mmm_body = mmm.json()
    assert mmm_body["model_type"] == "demo_linear_mmm"
    assert mmm_body["result"]["channels"]["paid_social"] == 0.42

    mmm_detail = client.get(f"/v1/mmms/runs/{mmm_body['id']}")
    assert mmm_detail.status_code == 200
    assert mmm_detail.json()["id"] == mmm_body["id"]


def test_one_click_demo_scenario_creates_measured_experiment(client):
    response = client.post("/v1/demo/scenario")

    assert response.status_code == 200
    scenario = response.json()
    assert scenario["organization"]["id"]
    assert scenario["experiment"]["status"] == "completed"
    assert scenario["ingestion"]["accepted"] == 224
    assert scenario["event_health"]["total_events"] == 224
    assert scenario["result"]["variants"]["control"]["visitors"] == 100
    assert scenario["result"]["variants"]["ai_proof"]["conversions"] == 18
    assert scenario["result"]["recommendation"] == "winner"
    assert scenario["insight"]["winning_variant_key"] == "ai_proof"
    assert scenario["results_url"].endswith("/results")

    me = client.get("/v1/me")
    assert me.status_code == 200
    assert me.json()["principal"]["organization_id"] == scenario["organization"]["id"]


def test_creative_treatment_review_workflow(client):
    suffix = uuid4().hex[:8]
    created = client.post(
        "/v1/creative-treatments",
        json={
            "name": f"Proof angle {suffix}",
            "objective": "Increase demo requests",
            "target_audience": "Growth teams",
            "channel": "paid_social",
            "angle": "proof",
            "hook": "Measure lift before scaling spend.",
            "cta": "Run a lift test",
        },
    )
    assert created.status_code == 200
    creative = created.json()
    assert creative["approval_status"] == "draft"

    detail = client.get(f"/v1/creative-treatments/{creative['id']}")
    assert detail.status_code == 200
    assert detail.json()["name"] == f"Proof angle {suffix}"

    approved = client.post(
        f"/v1/creative-treatments/{creative['id']}/approve",
        json={"notes": "Looks good."},
    )
    assert approved.status_code == 200
    assert approved.json()["approval_status"] == "approved"

    rejected = client.post(
        f"/v1/creative-treatments/{creative['id']}/reject",
        json={"notes": "Retesting rejection path."},
    )
    assert rejected.status_code == 200
    assert rejected.json()["approval_status"] == "rejected"


def test_experiment_lifecycle_and_results(client, api_headers):
    created = client.post(
        "/v1/experiments",
        json={
            "name": "Lifecycle smoke test",
            "hypothesis": "Treatment improves signup.",
            "primary_metric": "signup",
            "guardrail_metric": "cost_per_signup",
            "variants": [
                {
                    "key": "control",
                    "creative_treatment_id": "00000000-0000-0000-0000-000000000105",
                    "allocation": 0.5,
                    "is_control": True,
                },
                {
                    "key": "treatment",
                    "creative_treatment_id": "00000000-0000-0000-0000-000000000101",
                    "allocation": 0.5,
                },
            ],
            "channel": "paid_social",
        },
    )
    assert created.status_code == 200
    experiment = created.json()

    detail = client.get(f"/v1/experiments/{experiment['id']}")
    assert detail.status_code == 200
    assert detail.json()["name"] == "Lifecycle smoke test"

    started = client.post(f"/v1/experiments/{experiment['id']}/start")
    assert started.status_code == 200
    assert started.json()["status"] == "running"
    assert started.json()["starts_at"] is not None

    first_assignment = client.get(f"/v1/experiments/{experiment['id']}/assign?unit_id=anon-123")
    second_assignment = client.get(f"/v1/experiments/{experiment['id']}/assign?unit_id=anon-123")
    assert first_assignment.status_code == 200
    assert first_assignment.json() == second_assignment.json()
    assert first_assignment.json()["variant_key"] in {"control", "treatment"}

    timestamp = datetime.now(UTC).isoformat()
    events = []
    for index in range(10):
        events.append(
            {
                "event_name": "impression",
                "timestamp": timestamp,
                "anonymous_id": f"control-{index}",
                "creative_treatment_id": "00000000-0000-0000-0000-000000000105",
                "experiment_id": experiment["id"],
                "variant_id": "control",
            }
        )
    for index in range(1):
        events.append(
            {
                "event_name": "signup",
                "timestamp": timestamp,
                "anonymous_id": f"control-{index}",
                "creative_treatment_id": "00000000-0000-0000-0000-000000000105",
                "experiment_id": experiment["id"],
                "variant_id": "control",
            }
        )
    for index in range(10):
        events.append(
            {
                "event_name": "impression",
                "timestamp": timestamp,
                "anonymous_id": f"treatment-{index}",
                "creative_treatment_id": "00000000-0000-0000-0000-000000000101",
                "experiment_id": experiment["id"],
                "variant_id": "treatment",
            }
        )
    for index in range(4):
        events.append(
            {
                "event_name": "signup",
                "timestamp": timestamp,
                "anonymous_id": f"treatment-{index}",
                "creative_treatment_id": "00000000-0000-0000-0000-000000000101",
                "experiment_id": experiment["id"],
                "variant_id": "treatment",
                "value": 25.0,
                "currency": "USD",
            }
        )

    ingested = client.post("/v1/events/ingest", headers=api_headers, json={"events": events})
    assert ingested.status_code == 200
    assert ingested.json()["accepted"] == 25

    paused = client.post(f"/v1/experiments/{experiment['id']}/pause")
    assert paused.status_code == 200
    assert paused.json()["status"] == "paused"

    completed = client.post(f"/v1/experiments/{experiment['id']}/complete")
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
    assert completed.json()["ends_at"] is not None

    results = client.get(f"/v1/experiments/{experiment['id']}/results")
    assert results.status_code == 200
    body = results.json()
    assert body["variants"]["control"]["visitors"] == 10
    assert body["variants"]["control"]["conversions"] == 1
    assert body["variants"]["treatment"]["visitors"] == 10
    assert body["variants"]["treatment"]["conversions"] == 4
    assert body["variants"]["treatment"]["revenue"] == 100.0
    assert body["comparison"]["control_rate"] == 0.1
    assert body["comparison"]["treatment_rate"] == 0.4
    assert body["recommendation"] in {"winner", "loser", "inconclusive", "invalid_srm"}

    insights = client.get(f"/v1/experiments/{experiment['id']}/insights")
    assert insights.status_code == 200
    insight_body = insights.json()
    assert insight_body["experiment_id"] == experiment["id"]
    assert insight_body["recommendation"] == body["recommendation"]
    assert insight_body["decision_summary"]
    assert insight_body["recommended_action"]
    assert insight_body["evidence"]


def test_experiment_start_requires_control_and_treatment(client):
    created = client.post(
        "/v1/experiments",
        json={
            "name": "Invalid missing control",
            "hypothesis": "Both variants are treatments.",
            "primary_metric": "signup",
            "variants": [
                {
                    "key": "variant_a",
                    "creative_treatment_id": "00000000-0000-0000-0000-000000000101",
                    "allocation": 0.5,
                },
                {
                    "key": "variant_b",
                    "creative_treatment_id": "00000000-0000-0000-0000-000000000105",
                    "allocation": 0.5,
                },
            ],
        },
    )
    assert created.status_code == 200

    started = client.post(f"/v1/experiments/{created.json()['id']}/start")

    assert started.status_code == 409
    assert "control" in started.json()["error"]["message"]


def test_experiment_start_requires_approved_creatives(client):
    created = client.post(
        "/v1/experiments",
        json={
            "name": "Invalid rejected creative",
            "hypothesis": "Rejected creative should not launch.",
            "primary_metric": "signup",
            "variants": [
                {
                    "key": "control",
                    "creative_treatment_id": "00000000-0000-0000-0000-000000000104",
                    "allocation": 0.5,
                    "is_control": True,
                },
                {
                    "key": "treatment",
                    "creative_treatment_id": "00000000-0000-0000-0000-000000000101",
                    "allocation": 0.5,
                },
            ],
        },
    )
    assert created.status_code == 200

    started = client.post(f"/v1/experiments/{created.json()['id']}/start")

    assert started.status_code == 409
    assert "approved" in started.json()["error"]["message"]


def test_launch_blocks_claim_evidence_gap(client):
    created = client.post(
        "/v1/creative-treatments",
        json={
            "brand_pack_id": "00000000-0000-0000-0000-000000000011",
            "name": "Evidence gated claim",
            "objective": "Increase demo requests",
            "target_audience": "Growth teams",
            "channel": "paid_social",
            "angle": "proof",
            "hook": "Measure lift before scaling spend.",
            "cta": "Run a lift test",
        },
    )
    assert created.status_code == 200
    creative_id = created.json()["id"]

    approved_without_evidence = client.post(
        f"/v1/creative-treatments/{creative_id}/approve",
        json={"notes": "Approved but missing evidence."},
    )
    assert approved_without_evidence.status_code == 200
    assert approved_without_evidence.json()["compliance_status"] == "approved_needs_evidence"

    experiment = client.post(
        "/v1/experiments",
        json={
            "name": "Evidence policy launch",
            "hypothesis": "Evidence-gated proof angle improves signup.",
            "primary_metric": "signup",
            "variants": [
                {
                    "key": "control",
                    "creative_treatment_id": "00000000-0000-0000-0000-000000000105",
                    "allocation": 0.5,
                    "is_control": True,
                },
                {
                    "key": "treatment",
                    "creative_treatment_id": creative_id,
                    "allocation": 0.5,
                },
            ],
        },
    )
    assert experiment.status_code == 200

    blocked = client.post(f"/v1/experiments/{experiment.json()['id']}/start")
    assert blocked.status_code == 409
    assert "claim evidence" in blocked.json()["error"]["message"]

    approved_with_evidence = client.post(
        f"/v1/creative-treatments/{creative_id}/approve",
        json={"notes": "Evidence attached.", "claim_evidence_urls": ["https://example.com/evidence"]},
    )
    assert approved_with_evidence.status_code == 200
    assert approved_with_evidence.json()["compliance_status"] == "approved"

    started = client.post(f"/v1/experiments/{experiment.json()['id']}/start")
    assert started.status_code == 200
    assert started.json()["status"] == "running"


def test_connector_registry_workflow(client, api_headers):
    suffix = uuid4().hex[:8]
    created = client.post(
        "/v1/connectors",
        headers=api_headers,
        json={
            "provider": "posthog",
            "display_name": f"PostHog {suffix}",
            "config": {"mode": "test"},
        },
    )
    assert created.status_code == 201
    connector = created.json()["data"]
    assert connector["status"] == "disconnected"

    listed = client.get("/v1/connectors", headers=api_headers)
    assert listed.status_code == 200
    body = listed.json()
    assert body["meta"]["total"] >= 1
    assert any(item["id"] == connector["id"] for item in body["data"])
