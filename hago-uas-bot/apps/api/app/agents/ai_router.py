"""AI Router — selects the appropriate provider and model for each task type."""

from __future__ import annotations

from enum import Enum

from app.agents.providers.anthropic_provider import AnthropicProvider
from app.agents.providers.base_provider import BaseAIProvider
from app.agents.providers.openai_provider import OpenAIProvider
from app.core.config import get_settings
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


class TaskType(str, Enum):
    GENERAL = "general"
    TECHNICAL = "technical"
    CODE = "code"
    LOG_ANALYSIS = "log_analysis"
    DOCUMENT = "document"
    VISION = "vision"


class AIRouter:
    """Select the best available provider and model for a given task."""

    def __init__(self) -> None:
        settings = get_settings()
        self._providers: dict[str, BaseAIProvider] = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
        }
        self._priority = settings.AI_PROVIDER_PRIORITY

    def _model_map(self, provider: str, task: TaskType) -> str:
        settings = get_settings()
        if provider == "openai":
            return {
                TaskType.GENERAL: settings.OPENAI_DEFAULT_MODEL,
                TaskType.TECHNICAL: settings.OPENAI_TECHNICAL_MODEL,
                TaskType.CODE: settings.OPENAI_TECHNICAL_MODEL,
                TaskType.LOG_ANALYSIS: settings.OPENAI_TECHNICAL_MODEL,
                TaskType.DOCUMENT: settings.OPENAI_DEFAULT_MODEL,
                TaskType.VISION: settings.OPENAI_TECHNICAL_MODEL,
            }[task]
        if provider == "anthropic":
            return {
                TaskType.GENERAL: settings.ANTHROPIC_DEFAULT_MODEL,
                TaskType.TECHNICAL: settings.ANTHROPIC_TECHNICAL_MODEL,
                TaskType.CODE: settings.ANTHROPIC_TECHNICAL_MODEL,
                TaskType.LOG_ANALYSIS: settings.ANTHROPIC_TECHNICAL_MODEL,
                TaskType.DOCUMENT: settings.ANTHROPIC_DEFAULT_MODEL,
                TaskType.VISION: settings.ANTHROPIC_TECHNICAL_MODEL,
            }[task]
        return ""

    def get_provider(self, task: TaskType = TaskType.GENERAL) -> tuple[BaseAIProvider, str]:
        """Return (provider, model_name) for the given task type."""
        for name in self._priority:
            provider = self._providers.get(name)
            if provider and provider.is_available:
                model = self._model_map(name, task)
                logger.debug("ai_router_selected", provider=name, model=model, task=task)
                return provider, model
        raise AIProviderError(
            "No AI provider is available. Configure OPENAI_API_KEY or ANTHROPIC_API_KEY."
        )

    def get_embedding_provider(self) -> BaseAIProvider:
        """Return the provider used for embeddings (always OpenAI for now)."""
        openai_provider = self._providers.get("openai")
        if openai_provider and openai_provider.is_available:
            return openai_provider
        raise AIProviderError(
            "Embedding provider (OpenAI) is not available. "
            "Set OPENAI_API_KEY to enable RAG."
        )

    def classify_task(self, message: str) -> TaskType:
        """Heuristic domain classification — full ML classifier in v2."""
        lower = message.lower()
        if any(kw in lower for kw in ("log", "ulog", "dataflash", "telemetry", "flight data")):
            return TaskType.LOG_ANALYSIS
        if any(kw in lower for kw in ("code", "script", "implement", "write a", "example", "snippet")):
            return TaskType.CODE
        if any(kw in lower for kw in ("px4", "ardupilot", "mavlink", "mavsdk", "ros2", "ros 2",
                                       "parameter", "firmware", "esc", "flight controller")):
            return TaskType.TECHNICAL
        if any(kw in lower for kw in ("document", "pdf", "manual", "specification")):
            return TaskType.DOCUMENT
        return TaskType.GENERAL
