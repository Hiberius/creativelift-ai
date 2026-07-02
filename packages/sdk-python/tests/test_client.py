from creativelift.client import CreativeLiftClient


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


def test_python_sdk_sends_x_api_key_and_idempotency_key(monkeypatch):
    call: dict = {}

    def fake_post(url, headers, json, timeout):
        call.update({"url": url, "headers": headers, "json": json, "timeout": timeout})
        return FakeResponse({"accepted": 1})

    monkeypatch.setattr("creativelift.client.httpx.post", fake_post)

    client = CreativeLiftClient("dev-api-key", base_url="http://localhost:8000/")
    response = client.ingest(
        [
            {
                "event_name": "purchase",
                "timestamp": "2026-06-28T10:00:00Z",
                "anonymous_id": "anon-test",
                "creative_treatment_id": "00000000-0000-0000-0000-000000000101",
            }
        ],
        idempotency_key="evt-test",
    )

    assert response == {"accepted": 1}
    assert call["url"] == "http://localhost:8000/v1/events/ingest"
    assert call["headers"]["X-API-Key"] == "dev-api-key"
    assert call["headers"]["Idempotency-Key"] == "evt-test"
    assert "Authorization" not in call["headers"]
    assert call["json"]["events"][0]["event_name"] == "purchase"


def test_python_sdk_assigns_experiment_unit(monkeypatch):
    call: dict = {}

    def fake_get(url, headers, params, timeout):
        call.update({"url": url, "headers": headers, "params": params, "timeout": timeout})
        return FakeResponse({"variant_key": "control", "unit_id": "anon-test"})

    monkeypatch.setattr("creativelift.client.httpx.get", fake_get)

    client = CreativeLiftClient("dev-api-key", base_url="http://localhost:8000/")
    response = client.assign("exp-123", "anon-test")

    assert response["variant_key"] == "control"
    assert call["url"] == "http://localhost:8000/v1/experiments/exp-123/assign"
    assert call["headers"]["X-API-Key"] == "dev-api-key"
    assert call["params"] == {"unit_id": "anon-test"}


def test_python_sdk_reads_event_health(monkeypatch):
    call: dict = {}

    def fake_get(url, headers, timeout):
        call.update({"url": url, "headers": headers, "timeout": timeout})
        return FakeResponse({"total_events": 3, "quality_score": 1.0})

    monkeypatch.setattr("creativelift.client.httpx.get", fake_get)

    client = CreativeLiftClient("dev-api-key", base_url="http://localhost:8000/")
    response = client.event_health()

    assert response["total_events"] == 3
    assert call["url"] == "http://localhost:8000/v1/events/health"
    assert call["headers"]["X-API-Key"] == "dev-api-key"


def test_python_sdk_reads_experiment_insight(monkeypatch):
    call: dict = {}

    def fake_get(url, headers, timeout):
        call.update({"url": url, "headers": headers, "timeout": timeout})
        return FakeResponse({"recommendation": "winner", "decision_summary": "Treatment wins."})

    monkeypatch.setattr("creativelift.client.httpx.get", fake_get)

    client = CreativeLiftClient("dev-api-key", base_url="http://localhost:8000/")
    response = client.experiment_insight("exp-123")

    assert response["recommendation"] == "winner"
    assert call["url"] == "http://localhost:8000/v1/experiments/exp-123/insights"
    assert call["headers"]["X-API-Key"] == "dev-api-key"
