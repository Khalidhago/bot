"""Abstract AI provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatMessage:
    role: str  # "user" | "assistant" | "system"
    content: str


@dataclass
class AIResponse:
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    finish_reason: str = "stop"
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseAIProvider(ABC):
    """Abstract interface for all AI providers."""

    name: str = "base"

    @abstractmethod
    async def complete(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AIResponse:
        """Return a complete (non-streaming) response."""

    @abstractmethod
    async def stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """Yield response tokens one at a time."""

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return embedding vectors for a list of texts."""

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the provider has a valid API key configured."""
