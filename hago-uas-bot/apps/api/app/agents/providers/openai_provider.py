"""OpenAI provider implementation."""

from __future__ import annotations

from collections.abc import AsyncGenerator

import openai

from app.agents.providers.base_provider import AIResponse, BaseAIProvider, ChatMessage
from app.core.config import get_settings
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIProvider(BaseAIProvider):
    name = "openai"

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.OPENAI_API_KEY
        self._default_model = settings.OPENAI_DEFAULT_MODEL
        self._embedding_model = settings.OPENAI_EMBEDDING_MODEL
        if self._api_key:
            self._client = openai.AsyncOpenAI(api_key=self._api_key)
        else:
            self._client = None

    @property
    def is_available(self) -> bool:
        return bool(self._api_key and self._client)

    def _to_openai_messages(
        self, messages: list[ChatMessage]
    ) -> list[dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in messages]

    async def complete(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AIResponse:
        if not self._client:
            raise AIProviderError("OpenAI API key not configured.")
        try:
            response = await self._client.chat.completions.create(
                model=model or self._default_model,
                messages=self._to_openai_messages(messages),
                temperature=temperature,
                max_tokens=max_tokens,
            )
            choice = response.choices[0]
            usage = response.usage
            return AIResponse(
                content=choice.message.content or "",
                model=response.model,
                prompt_tokens=usage.prompt_tokens if usage else 0,
                completion_tokens=usage.completion_tokens if usage else 0,
                total_tokens=usage.total_tokens if usage else 0,
                finish_reason=choice.finish_reason or "stop",
            )
        except openai.OpenAIError as exc:
            logger.error("openai_error", error=str(exc))
            raise AIProviderError(f"OpenAI error: {exc}") from exc

    async def stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        if not self._client:
            raise AIProviderError("OpenAI API key not configured.")
        try:
            async with self._client.chat.completions.stream(
                model=model or self._default_model,
                messages=self._to_openai_messages(messages),
                temperature=temperature,
                max_tokens=max_tokens,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except openai.OpenAIError as exc:
            logger.error("openai_stream_error", error=str(exc))
            raise AIProviderError(f"OpenAI streaming error: {exc}") from exc

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not self._client:
            raise AIProviderError("OpenAI API key not configured.")
        try:
            response = await self._client.embeddings.create(
                model=self._embedding_model,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except openai.OpenAIError as exc:
            logger.error("openai_embed_error", error=str(exc))
            raise AIProviderError(f"OpenAI embedding error: {exc}") from exc
