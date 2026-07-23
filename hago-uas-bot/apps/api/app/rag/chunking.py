"""Document chunking strategies."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    content: str
    chunk_index: int
    metadata: dict


def chunk_text(
    text: str,
    chunk_size: int = 512,
    overlap: int = 64,
) -> list[Chunk]:
    """Split text into overlapping token-aware chunks.

    Uses a simple character-based approximation (4 chars ≈ 1 token).
    A proper tokenizer can be substituted without changing the interface.
    """
    char_size = chunk_size * 4
    char_overlap = overlap * 4
    step = max(char_size - char_overlap, 1)

    chunks: list[Chunk] = []
    start = 0
    index = 0
    while start < len(text):
        end = min(start + char_size, len(text))
        chunk_text_str = text[start:end].strip()
        if chunk_text_str:
            chunks.append(
                Chunk(
                    content=chunk_text_str,
                    chunk_index=index,
                    metadata={"char_start": start, "char_end": end},
                )
            )
            index += 1
        start += step

    return chunks
