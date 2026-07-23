"""Embedding generation via AI provider."""

from __future__ import annotations

from app.agents.ai_router import AIRouter
from app.core.logging import get_logger

logger = get_logger(__name__)

_BATCH_SIZE = 100


async def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts, batching as needed."""
    router = AIRouter()
    provider = router.get_embedding_provider()

    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), _BATCH_SIZE):
        batch = texts[i : i + _BATCH_SIZE]
        logger.debug("embedding_batch", start=i, size=len(batch))
        embeddings = await provider.embed(batch)
        all_embeddings.extend(embeddings)

    return all_embeddings
