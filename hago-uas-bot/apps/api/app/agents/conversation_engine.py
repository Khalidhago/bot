"""Conversation engine — builds context, calls AI, streams responses."""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

from app.agents.ai_router import AIRouter, TaskType
from app.agents.providers.base_provider import ChatMessage
from app.core.logging import get_logger
from app.uav.prompt_library import get_system_prompt

logger = get_logger(__name__)

MAX_HISTORY_MESSAGES = 20


class ConversationEngine:
    """Orchestrates context building, RAG injection, and AI invocation."""

    def __init__(self, router: AIRouter | None = None) -> None:
        self._router = router or AIRouter()

    def _build_messages(
        self,
        user_message: str,
        mode: str,
        history: list[ChatMessage],
        rag_context: str | None,
    ) -> list[ChatMessage]:
        system_prompt = get_system_prompt(mode)
        if rag_context:
            system_prompt += (
                f"\n\n## Retrieved Knowledge\n\nUse the following verified technical "
                f"information to ground your answer:\n\n{rag_context}"
            )

        messages: list[ChatMessage] = [
            ChatMessage(role="system", content=system_prompt)
        ]
        # Keep only the most recent history to stay within the context window
        messages.extend(history[-MAX_HISTORY_MESSAGES:])
        messages.append(ChatMessage(role="user", content=user_message))
        return messages

    async def complete(
        self,
        user_message: str,
        mode: str = "general",
        history: list[ChatMessage] | None = None,
        rag_context: str | None = None,
    ) -> tuple[str, str, int]:
        """Return (response_text, model_name, total_tokens)."""
        task = self._router.classify_task(user_message)
        provider, model = self._router.get_provider(task)
        messages = self._build_messages(
            user_message, mode, history or [], rag_context
        )
        response = await provider.complete(messages, model=model)
        return response.content, response.model, response.total_tokens

    async def stream(
        self,
        user_message: str,
        mode: str = "general",
        history: list[ChatMessage] | None = None,
        rag_context: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Yield response tokens."""
        task = self._router.classify_task(user_message)
        provider, model = self._router.get_provider(task)
        messages = self._build_messages(
            user_message, mode, history or [], rag_context
        )
        async for token in provider.stream(messages, model=model):
            yield token
