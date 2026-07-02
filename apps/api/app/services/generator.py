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


class OpenAICompatibleProvider(CreativeGeneratorProvider):
    async def generate_variants(
        self, brief: BriefCreate, brand_pack: BrandPackCreate | None, n: int, temperature: float
    ) -> list[GeneratedVariant]:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_COMPATIBLE_API_KEY is not configured; use provider='mock' locally")
        # Scaffold: wire an OpenAI-compatible chat/completions client here.
        raise NotImplementedError(
            "OpenAI-compatible provider scaffold is ready for a client implementation"
        )


def provider_for(name: str) -> CreativeGeneratorProvider:
    if name == "mock":
        return MockCreativeGeneratorProvider()
    if name in {"openai", "openai-compatible"}:
        return OpenAICompatibleProvider()
    raise ValueError(f"Unknown generator provider: {name}")
