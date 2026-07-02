from importlib import reload

import app.services.measurement_reports as measurement_reports
from app.services.measurement_reports import clear_measurement_reports


def test_health_and_measurement_summary_smoke(client, api_headers):
    health = client.get("/healthz")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    response = client.get("/v1/measurement/summary", headers=api_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["window"] == "last_7_days"
    assert {card["metric"] for card in body["data"]["cards"]} >= {
        "impressions",
        "conversion_rate",
        "incremental_lift",
    }


def test_demo_analyze_endpoint_returns_measurement_decision(client):
    response = client.post(
        "/v1/demo/analyze",
        json={
            "name": "Signup page test",
            "minimum_detectable_effect": 0.02,
            "control": {
                "key": "control",
                "label": "Current page",
                "visitors": 1000,
                "conversions": 70,
                "revenue": 9000,
                "allocation": 0.5,
            },
            "treatment": {
                "key": "ai_proof",
                "label": "AI proof page",
                "visitors": 1000,
                "conversions": 120,
                "revenue": 18_000,
                "allocation": 0.5,
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["recommendation"] == "winner"
    assert body["variants"]["ai_proof"]["conversion_rate"] == 0.12
    assert body["comparison"]["p_value"] < 0.05
    assert body["sample_size"]["remaining_treatment"] >= 0


def test_demo_report_endpoint_saves_and_lists_measurement_decisions(client):
    clear_measurement_reports()
    payload = {
        "source": "manual",
        "notes": "Keep for decision review",
        "request": {
            "name": "Saved report test",
            "minimum_detectable_effect": 0.02,
            "control": {
                "key": "control",
                "label": "Current page",
                "visitors": 1000,
                "conversions": 70,
                "revenue": 9000,
                "allocation": 0.5,
            },
            "treatment": {
                "key": "treatment",
                "label": "Proof page",
                "visitors": 1000,
                "conversions": 120,
                "revenue": 18_000,
                "allocation": 0.5,
            },
        },
    }

    created = client.post("/v1/demo/reports", json=payload)
    listed = client.get("/v1/demo/reports")

    assert created.status_code == 200
    created_body = created.json()
    assert created_body["analysis"]["recommendation"] == "winner"
    assert created_body["notes"] == "Keep for decision review"
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == created_body["id"]

    clear_measurement_reports()


def test_demo_report_import_endpoint_accepts_csv_and_returns_row_errors(client):
    clear_measurement_reports()
    csv_text = "\n".join(
        [
            "name,control_visitors,control_conversions,treatment_visitors,treatment_conversions,control_revenue,treatment_revenue,mde,notes",
            "Homepage proof,1000,70,1000,120,9000,18000,2,Winner candidate",
            "Email subject,900,90,900,72,4000,3100,1.5,Loser candidate",
            "Broken row,10,12,10,1,0,0,2,Invalid conversions",
        ]
    )

    imported = client.post(
        "/v1/demo/reports/import",
        json={"csv_text": csv_text, "source": "csv-upload", "save_reports": True},
    )
    listed = client.get("/v1/demo/reports")

    assert imported.status_code == 200
    body = imported.json()
    assert body["accepted"] == 2
    assert body["rejected"] == 1
    assert body["reports"][0]["analysis"]["name"] == "Homepage proof"
    assert body["reports"][0]["analysis"]["recommendation"] == "winner"
    assert "conversions cannot exceed visitors" in body["errors"][0]["message"]
    assert listed.status_code == 200
    assert len(listed.json()) == 2

    clear_measurement_reports()


def test_demo_report_export_and_clear_endpoints(client):
    clear_measurement_reports()
    payload = {
        "source": "manual",
        "notes": "Export this",
        "request": {
            "name": "Export report test",
            "minimum_detectable_effect": 0.02,
            "control": {
                "key": "control",
                "label": "Current page",
                "visitors": 1000,
                "conversions": 70,
                "revenue": 9000,
                "allocation": 0.5,
            },
            "treatment": {
                "key": "treatment",
                "label": "Proof page",
                "visitors": 1000,
                "conversions": 120,
                "revenue": 18_000,
                "allocation": 0.5,
            },
        },
    }
    created = client.post("/v1/demo/reports", json=payload)

    csv_export = client.get("/v1/demo/reports/export?format=csv")
    json_export = client.get("/v1/demo/reports/export?format=json")
    markdown_export = client.get("/v1/demo/reports/export?format=markdown")
    cleared = client.delete("/v1/demo/reports")
    listed = client.get("/v1/demo/reports")

    assert created.status_code == 200
    assert csv_export.status_code == 200
    assert "text/csv" in csv_export.headers["content-type"]
    assert "Export report test" in csv_export.text
    assert json_export.status_code == 200
    assert json_export.json()[0]["analysis"]["name"] == "Export report test"
    assert markdown_export.status_code == 200
    assert "# CreativeLift AI Measurement Reports" in markdown_export.text
    assert cleared.status_code == 204
    assert listed.json() == []


def test_demo_reports_survive_service_reload(client):
    clear_measurement_reports()
    payload = {
        "source": "manual",
        "request": {
            "name": "Persistent report test",
            "control": {
                "key": "control",
                "visitors": 1000,
                "conversions": 70,
                "allocation": 0.5,
            },
            "treatment": {
                "key": "treatment",
                "visitors": 1000,
                "conversions": 120,
                "allocation": 0.5,
            },
        },
    }
    created = client.post("/v1/demo/reports", json=payload)

    reloaded_reports = reload(measurement_reports).list_measurement_reports()

    assert created.status_code == 200
    assert reloaded_reports[0].analysis.name == "Persistent report test"
    reload(measurement_reports).clear_measurement_reports()


def test_demo_report_summary_endpoint_aggregates_saved_decisions(client):
    clear_measurement_reports()
    csv_text = "\n".join(
        [
            "name,control_visitors,control_conversions,treatment_visitors,treatment_conversions",
            "Winner,1000,70,1000,120",
            "Loser,1000,120,1000,70",
        ]
    )
    imported = client.post(
        "/v1/demo/reports/import",
        json={"csv_text": csv_text, "source": "summary-test", "save_reports": True},
    )
    summary = client.get("/v1/demo/reports/summary")

    assert imported.status_code == 200
    assert summary.status_code == 200
    body = summary.json()
    assert body["total"] == 2
    assert body["winners"] == 1
    assert body["losers"] == 1
    assert body["best_report_name"] == "Winner"
    assert body["average_relative_lift"] is not None

    clear_measurement_reports()
