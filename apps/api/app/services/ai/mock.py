from app.services.ai.base import GenerationRequest, GenerationResponse


class MockAIProvider:
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        treatment = (
            "Creative angle: lead with measurable lift, pair the approved claim with a "
            "channel-native proof point, and reserve a clear holdout for incrementality."
        )
        return GenerationResponse(
            provider="mock",
            model=request.model or "mock-creative-lift",
            content=treatment,
            raw={
                "variables": request.variables,
                "safety": {"policy_review": "not_applicable_mock"},
            },
            input_tokens=max(1, len(request.prompt.split())),
            output_tokens=len(treatment.split()),
        )
