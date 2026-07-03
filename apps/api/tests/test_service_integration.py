"""Integration tests proving the API really calls the standalone statistical services.

Covers: synchronous MMM and uplift runs (services/mmm-service, services/uplift-service),
Thompson sampling decisions through bandit_service, and the always-valid sequential
block computed by experiment_engine in the demo analyze endpoint.
"""

from bandit_service import ThompsonBandit


def test_mmm_run_computes_outputs_synchronously(client, api_headers):
    response = client.post(
        "/v1/measurement/mmm-runs",
        headers=api_headers,
        json={
            "name": "Q1 spend mix",
            "inputs": {
                "weekly_rows": [
                    {"week": "2026-01-01", "paid_social_spend": 100, "search_spend": 50},
                    {"week": "2026-01-08", "paid_social_spend": 100, "search_spend": 150},
                ]
            },
        },
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["status"] == "succeeded"
    assert set(data["outputs"]["channels"]) == {"paid_social", "search"}
    assert abs(sum(data["outputs"]["channels"].values()) - 1.0) < 1e-9


def test_mmm_run_with_missing_inputs_fails_cleanly(client, api_headers):
    response = client.post(
        "/v1/measurement/mmm-runs",
        headers=api_headers,
        json={"name": "No data", "inputs": {}},
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["status"] == "failed"
    assert "weekly_rows" in data["outputs"]["error"]


def test_uplift_run_scores_segments_synchronously(client, api_headers):
    response = client.post(
        "/v1/measurement/uplift-runs",
        headers=api_headers,
        json={
            "name": "Segment uplift",
            "inputs": {
                "rows": [
                    {"segment": "saas", "treated": True, "outcome": 1},
                    {"segment": "saas", "treated": False, "outcome": 0},
                    {"segment": "dtc", "treated": True, "outcome": 0},
                    {"segment": "dtc", "treated": False, "outcome": 1},
                ]
            },
        },
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["status"] == "succeeded"
    segments = data["outputs"]["segments"]
    assert segments[0]["segment"] == "saas"
    assert segments[0]["uplift"] > 0
    assert data["outputs"]["model_type"] == "segment_baseline"


def test_uplift_run_with_invalid_rows_fails_cleanly(client, api_headers):
    response = client.post(
        "/v1/measurement/uplift-runs",
        headers=api_headers,
        json={"name": "Broken", "inputs": {"rows": "not-a-list"}},
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["status"] == "failed"
    assert "rows" in data["outputs"]["error"]


def test_bandit_decide_uses_bandit_service(client, monkeypatch):
    created = client.post(
        "/v1/bandits",
        json={"name": "CTA allocation", "arms": ["control", "variant"]},
    )
    assert created.status_code == 200
    bandit = created.json()

    def fake_decide(self):
        return "variant", {"control": 0.1, "variant": 0.9}

    monkeypatch.setattr(ThompsonBandit, "decide", fake_decide)

    decision = client.post(f"/v1/bandits/{bandit['id']}/decide")

    assert decision.status_code == 200
    body = decision.json()
    assert body["chosen_arm"] == "variant"
    assert body["samples"] == {"control": 0.1, "variant": 0.9}


def test_demo_analyze_includes_sequential_block(client):
    response = client.post(
        "/v1/demo/analyze",
        json={
            "name": "Sequential smoke test",
            "minimum_detectable_effect": 0.02,
            "control": {
                "key": "control",
                "visitors": 10_000,
                "conversions": 700,
                "revenue": 90_000,
                "allocation": 0.5,
            },
            "treatment": {
                "key": "treatment",
                "visitors": 10_000,
                "conversions": 1_300,
                "revenue": 180_000,
                "allocation": 0.5,
            },
        },
    )

    assert response.status_code == 200
    sequential = response.json()["sequential"]
    assert sequential["method"] == "msprt_normal_mixture"
    assert 0.0 <= sequential["always_valid_p_value"] <= 1.0
    assert sequential["can_stop"] is True
    assert sequential["decision"] == "stop"
