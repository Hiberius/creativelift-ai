import httpx

from app.core.config import Settings
from app.core.errors import ApiError
from app.services.ai.base import GenerationRequest, GenerationResponse


class OpenAICompatibleProvider:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        if not self.settings.openai_api_key:
            raise ApiError(
                503,
                "ai_provider_unconfigured",
                "OpenAI-compatible provider is missing an API key",
            )

        model = request.model or self.settings.openai_model
        async with httpx.AsyncClient(base_url=self.settings.openai_base_url, timeout=30) as client:
            response = await client.post(
                "/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are CreativeLift AI, a marketing measurement assistant.",
                        },
                        {"role": "user", "content": request.prompt},
                    ],
                    "temperature": 0.4,
                },
            )
        if response.status_code >= 400:
            raise ApiError(502, "ai_provider_error", "AI provider request failed")

        body = response.json()
        choice = body["choices"][0]["message"]["content"]
        usage = body.get("usage", {})
        return GenerationResponse(
            provider="openai-compatible",
            model=model,
            content=choice,
            raw=body,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
        )
