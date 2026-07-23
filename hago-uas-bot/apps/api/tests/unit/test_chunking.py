"""Tests for RAG chunking."""

from __future__ import annotations

from app.rag.chunking import chunk_text


class TestChunking:
    def test_short_text_single_chunk(self) -> None:
        text = "Hello world"
        chunks = chunk_text(text, chunk_size=512, overlap=64)
        assert len(chunks) == 1
        assert chunks[0].content == text
        assert chunks[0].chunk_index == 0

    def test_long_text_multiple_chunks(self) -> None:
        word = "word "
        text = word * 600  # ~3000 chars → should produce >1 chunk with chunk_size=512
        chunks = chunk_text(text, chunk_size=512, overlap=64)
        assert len(chunks) > 1

    def test_chunks_have_overlap(self) -> None:
        text = "A" * 3000
        chunks = chunk_text(text, chunk_size=100, overlap=20)
        # Each chunk except the last should end beyond where the next starts
        for i in range(len(chunks) - 1):
            start_a = chunks[i].metadata["char_start"]
            end_a = chunks[i].metadata["char_end"]
            start_b = chunks[i + 1].metadata["char_start"]
            # b starts before a ends (overlap)
            assert start_b < end_a

    def test_empty_text_returns_no_chunks(self) -> None:
        chunks = chunk_text("   ", chunk_size=512, overlap=64)
        assert chunks == []

    def test_chunk_indices_sequential(self) -> None:
        text = "x" * 5000
        chunks = chunk_text(text, chunk_size=200, overlap=20)
        indices = [c.chunk_index for c in chunks]
        assert indices == list(range(len(chunks)))
