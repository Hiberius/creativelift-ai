"""OpenAI-compatible variant generation: config guard, parsing, lineage."""

import dataclasses
import json

import app.services.generator as generator_module
from app.services.ai.base import GenerationResponse


def _brief_payload():
    return {
        "name": "Paid social hook test",
        "objective": "Increase demo requests",
        "target_audience": "B2B growth leads",
        "channel": "paid_social",
        "primary_kpi": "signup",
    }


def test_openai_provider_without_key_returns_503(client):
    response = client.post(
        "/v1/variants/generate",
        json={"brief": _brief_payload(), "provider": "openai", "n": 2},
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "ai_provider_unconfigured"


def test_openai_provider_parses_variants_from_chat_response(client, monkeypatch):
    configured = dataclasses.replace(generator_module.settings, openai_api_key="test-key")
    monkeypatch.setattr(generator_module, "settings", configured)

    content = json.dumps(
        [
            {
                "headline": "Stop guessing which ad works",
                "primary_text": "Measure incremental lift per creative.",
                "landing_page_hero": "From prompt to profit.",
                "email_subject": "Your winning creative, proven",
                "cta": "Run a lift test",
                "angle": "proof",
                "hypothesis": "Proof-led hooks lift signups.",
            },
            {
                "headline": "Your ROAS is lying to you",
                "primary_text": "Only lift tests reveal real winners.",
                "landing_page_hero": "Causal measurement for AI creative.",
                "email_subject": "The truth about your creatives",
                "cta": "See the lift",
                "angle": "contrarian",
                "hypothesis": "Contrarian hooks drive curiosity clicks that convert.",
            },
        ]
    )

    async def fake_generate(self, request):
        return GenerationResponse(
            provider="openai-compatible",
            model="gpt-4o-mini",
            content=f"```json\n{content}\n```",
            raw={},
            input_tokens=120,
            output_tokens=340,
        )

    from app.services.ai.openai_compatible import OpenAICompatibleProvider as ChatProvider

    monkeypatch.setattr(ChatProvider, "generate", fake_generate)

    response = client.post(
        "/v1/variants/generate",
        json={"brief": _brief_payload(), "provider": "openai", "n": 2},
    )
    assert response.status_code == 200, response.text
    variants = response.json()
    assert len(variants) == 2
    assert variants[0]["headline"] == "Stop guessing which ad works"
    assert variants[0]["prompt_lineage"]["provider"] == "openai-compatible"
    assert variants[0]["prompt_lineage"]["model"] == "gpt-4o-mini"
    assert variants[0]["prompt_lineage"]["output_tokens"] == 340


def test_openai_provider_rejects_unparseable_response(client, monkeypatch):
    configured = dataclasses.replace(generator_module.settings, openai_api_key="test-key")
    monkeypatch.setattr(generator_module, "settings", configured)

    async def fake_generate(self, request):
        return GenerationResponse(
            provider="openai-compatible",
            model="gpt-4o-mini",
            content="Sorry, I cannot help with that.",
            raw={},
            input_tokens=10,
            output_tokens=10,
        )

    from app.services.ai.openai_compatible import OpenAICompatibleProvider as ChatProvider

    monkeypatch.setattr(ChatProvider, "generate", fake_generate)

    response = client.post(
        "/v1/variants/generate",
        json={"brief": _brief_payload(), "provider": "openai", "n": 2},
    )
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "ai_provider_bad_response"
