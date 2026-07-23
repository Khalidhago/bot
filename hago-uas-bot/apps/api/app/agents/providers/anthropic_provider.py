"""Anthropic provider implementation."""

from __future__ import annotations

from collections.abc import AsyncGenerator

import anthropic

from app.agents.providers.base_provider import AIResponse, BaseAIProvider, ChatMessage
from app.core.config import get_settings
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnthropicProvider(BaseAIProvider):
    name = "anthropic"

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.ANTHROPIC_API_KEY
        self._default_model = settings.ANTHROPIC_DEFAULT_MODEL
        if self._api_key:
            self._client = anthropic.AsyncAnthropic(api_key=self._api_key)
        else:
            self._client = None

    @property
    def is_available(self) -> bool:
        return bool(self._api_key and self._client)

    def _split_messages(
        self, messages: list[ChatMessage]
    ) -> tuple[str, list[dict[str, str]]]:
        """Separate system prompt from conversation messages."""
        system_parts: list[str] = []
        conversation: list[dict[str, str]] = []
        for msg in messages:
            if msg.role == "system":
                system_parts.append(msg.content)
            else:
                conversation.append({"role": msg.role, "content": msg.content})
        return "\n\n".join(system_parts), conversation

    async def complete(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AIResponse:
        if not self._client:
            raise AIProviderError("Anthropic API key not configured.")
        try:
            system, conversation = self._split_messages(messages)
            response = await self._client.messages.create(
                model=model or self._default_model,
                system=system or anthropic.NOT_GIVEN,
                messages=conversation,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = "".join(
                block.text for block in response.content if hasattr(block, "text")
            )
            return AIResponse(
                content=content,
                model=response.model,
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                finish_reason=response.stop_reason or "stop",
            )
        except anthropic.AnthropicError as exc:
            logger.error("anthropic_error", error=str(exc))
            raise AIProviderError(f"Anthropic error: {exc}") from exc

    async def stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        if not self._client:
            raise AIProviderError("Anthropic API key not configured.")
        try:
            system, conversation = self._split_messages(messages)
            async with self._client.messages.stream(
                model=model or self._default_model,
                system=system or anthropic.NOT_GIVEN,
                messages=conversation,
                temperature=temperature,
                max_tokens=max_tokens,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except anthropic.AnthropicError as exc:
            logger.error("anthropic_stream_error", error=str(exc))
            raise AIProviderError(f"Anthropic streaming error: {exc}") from exc

    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise AIProviderError(
            "Anthropic does not provide an embedding API. Use OpenAI embeddings."
        )
