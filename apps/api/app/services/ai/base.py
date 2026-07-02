from typing import Any, Protocol

from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    prompt: str
    variables: dict[str, Any] = Field(default_factory=dict)
    model: str | None = None


class GenerationResponse(BaseModel):
    provider: str
    model: str
    content: str
    raw: dict[str, Any] = Field(default_factory=dict)
    input_tokens: int = 0
    output_tokens: int = 0


class AIProvider(Protocol):
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        ...
