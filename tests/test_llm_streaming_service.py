import pytest
from unittest.mock import AsyncMock
from app.services import gemini_client, llm_streaming_service


@pytest.mark.asyncio
async def test_stream_conversation_responses_success(monkeypatch):
    """Test that stream_conversation_responses yields chunks from gemini_client.generate_stream."""
    async def fake_generate_stream(prompt, chunk_size=32):
        yield "chunk1"
        yield "chunk2"

    monkeypatch.setattr(gemini_client, "generate_stream", fake_generate_stream)

    chunks = []
    async for chunk in llm_streaming_service.stream_conversation_responses("test prompt"):
        chunks.append(chunk)

    assert chunks == ["chunk1", "chunk2"]


@pytest.mark.asyncio
async def test_stream_conversation_responses_error(monkeypatch):
    """Test that stream_conversation_responses yields error text when generate_stream raises."""
    async def fake_generate_stream(prompt, chunk_size=32):
        raise RuntimeError("Boom!")

    monkeypatch.setattr(gemini_client, "generate_stream", fake_generate_stream)

    chunks = []
    async for chunk in llm_streaming_service.stream_conversation_responses("test prompt"):
        chunks.append(chunk)

    assert chunks == ["[Error generating response]"]
