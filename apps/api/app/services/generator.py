from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from uuid import uuid4

from app.core.config import settings
from app.schemas.common import BrandPackCreate, BriefCreate, GeneratedVariant


class CreativeGeneratorProvider(ABC):
    @abstractmethod
    async def generate_variants(
        self, brief: BriefCreate, brand_pack: BrandPackCreate | None, n: int, temperature: float
    ) -> list[GeneratedVariant]:
        raise NotImplementedError


class MockCreativeGeneratorProvider(CreativeGeneratorProvider):
    async def generate_variants(
        self, brief: BriefCreate, brand_pack: BrandPackCreate | None, n: int, temperature: float
    ) -> list[GeneratedVariant]:
        angles = ["proof-led", "speed-to-learning", "governance", "incrementality", "open-source"]
        variants: list[GeneratedVariant] = []
        for idx in range(n):
            angle = angles[idx % len(angles)]
            variant_id = f"mock_{uuid4().hex[:10]}"
            variants.append(
                GeneratedVariant(
                    variant_id=variant_id,
                    headline=f"Measure {brief.channel} creative lift with {angle} clarity",
                    primary_text=(
                        f"CreativeLift AI connects {brief.name.lower()} from prompt lineage to "
                        f"{brief.primary_kpi} impact, so teams can promote what truly lifts revenue."
                    ),
                    landing_page_hero=f"Turn every {brief.channel} idea into a measurable treatment.",
                    email_subject=f"Which AI creative lifted {brief.primary_kpi}?",
                    cta="Run a lift test",
                    angle=angle,
                    hypothesis=(
                        f"A {angle} message will improve {brief.primary_kpi} among "
                        f"{brief.target_audience} versus the current control."
                    ),
                    prompt_lineage={
                        "provider": "mock",
                        "model": "mock-creative-lift-v0",
                        "temperature": temperature,
                        "timestamp": datetime.now(UTC).isoformat(),
                        "system_prompt": "Generate measurable marketing creative variants with compliance metadata.",
                        "prompt": brief.model_dump(),
                        "brand_pack": brand_pack.model_dump() if brand_pack else None,
                    },
                )
            )
        return variants


_VARIANT_FIELDS = ("headline", "primary_text", "landing_page_hero", "email_subject", "cta", "angle", "hypothesis")

_GENERATION_SYSTEM_PROMPT = (
    "You are CreativeLift AI, a marketing measurement copywriter. "
    "Every variant you produce will be A/B tested for incremental revenue lift, "
    "so each one must take a genuinely different persuasion angle. "
    "Respect the brand voice and never invent factual claims. "
    "Respond with a JSON array only - no prose, no markdown fences. Each item must "
    "have exactly these string fields: headline, primary_text, landing_page_hero, "
    "email_subject, cta, angle, hypothesis."
)


def _generation_prompt(brief: BriefCreate, brand_pack: BrandPackCreate | None, n: int) -> str:
    parts = [
        f"Generate {n} distinct marketing creative variants as a JSON array.",
        f"Brief: {brief.name}. Objective: {brief.objective}. Channel: {brief.channel}.",
        f"Target audience: {brief.target_audience}. Primary KPI: {brief.primary_kpi}.",
    ]
    if brief.body:
        parts.append(f"Notes: {brief.body}")
    if brand_pack is not None:
        parts.append(f"Brand voice: {brand_pack.voice}")
        if brand_pack.prohibited_claims:
            parts.append("Never use these claims: " + "; ".join(brand_pack.prohibited_claims))
    return "\n".join(parts)


def _parse_variants_json(content: str) -> list[dict]:
    import json

    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("provider response does not contain a JSON array")
    items = json.loads(text[start : end + 1])
    if not isinstance(items, list) or not items:
        raise ValueError("provider response is not a non-empty JSON array")
    return items


class OpenAICompatibleProvider(CreativeGeneratorProvider):
    async def generate_variants(
        self, brief: BriefCreate, brand_pack: BrandPackCreate | None, n: int, temperature: float
    ) -> list[GeneratedVariant]:
        from app.core.errors import ApiError
        from app.services.ai.base import GenerationRequest
        from app.services.ai.openai_compatible import OpenAICompatibleProvider as ChatProvider

        if not settings.openai_api_key:
            raise ApiError(
                503,
                "ai_provider_unconfigured",
                "OPENAI_COMPATIBLE_API_KEY is not configured; use provider='mock' locally",
            )

        prompt = _generation_prompt(brief, brand_pack, n)
        response = await ChatProvider(settings).generate(
            GenerationRequest(prompt=f"{_GENERATION_SYSTEM_PROMPT}\n\n{prompt}")
        )
        try:
            items = _parse_variants_json(response.content)
        except (ValueError, KeyError, TypeError) as exc:
            raise ApiError(
                502,
                "ai_provider_bad_response",
                f"Could not parse variants from the AI provider response: {exc}",
            ) from exc

        variants: list[GeneratedVariant] = []
        for item in items[:n]:
            fields = {name: str(item.get(name, "")).strip() for name in _VARIANT_FIELDS}
            if not fields["headline"] or not fields["primary_text"]:
                continue
            variants.append(
                GeneratedVariant(
                    variant_id=f"gen_{uuid4().hex[:10]}",
                    **fields,
                    prompt_lineage={
                        "provider": "openai-compatible",
                        "model": response.model,
                        "temperature": temperature,
                        "timestamp": datetime.now(UTC).isoformat(),
                        "system_prompt": _GENERATION_SYSTEM_PROMPT,
                        "prompt": brief.model_dump(),
                        "brand_pack": brand_pack.model_dump() if brand_pack else None,
                        "input_tokens": response.input_tokens,
                        "output_tokens": response.output_tokens,
                    },
                )
            )
        if not variants:
            raise ApiError(
                502,
                "ai_provider_bad_response",
                "The AI provider returned no usable variants",
            )
        return variants


def provider_for(name: str) -> CreativeGeneratorProvider:
    if name == "mock":
        return MockCreativeGeneratorProvider()
    if name in {"openai", "openai-compatible"}:
        return OpenAICompatibleProvider()
    raise ValueError(f"Unknown generator provider: {name}")
