import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services import next_question_service


@pytest.mark.asyncio
async def test_generate_next_question_success(monkeypatch):
    async_mock = AsyncMock(return_value="What is your experience working in a team?")
    monkeypatch.setattr(next_question_service.gemini_client, "generate_text", async_mock)

    jd = "We want a backend engineer with API design experience."
    prev_q = "Tell me about a project you built with FastAPI."
    answer = "I built a real-time dashboard using FastAPI and WebSocket."

    result = await next_question_service.generate_next_question(jd, prev_q, answer)

    assert isinstance(result, str)
    assert result.startswith("What")


@pytest.mark.asyncio
async def test_generate_next_question_fallback_default(monkeypatch):
    # Simulate Gemini returning empty string
    async_mock = AsyncMock(return_value="")
    monkeypatch.setattr(next_question_service.gemini_client, "generate_text", async_mock)

    jd = "Hiring a backend engineer"
    prev_q = "Tell me about your experience with REST APIs"
    answer = "I designed multiple microservices with Express and Django"

    result = await next_question_service.generate_next_question(jd, prev_q, answer)
    assert result == "What challenges have you faced in your recent projects?"


@pytest.mark.asyncio
async def test_generate_next_question_error_handling(monkeypatch):
    # Simulate Gemini API failure
    async_mock = AsyncMock(side_effect=Exception("LLM failed"))
    monkeypatch.setattr(next_question_service.gemini_client, "generate_text", async_mock)

    jd = "Hiring a backend engineer"
    prev_q = "What frameworks have you used?"
    answer = "I’ve used Django, Flask, and FastAPI."

    result = await next_question_service.generate_next_question(jd, prev_q, answer)

    # Should return fallback error question
    assert result == "Can you tell me more about your experience working in a team?"


@pytest.mark.asyncio
async def test_generate_next_question_uses_cache(monkeypatch):
    """Test that cached question is used if available."""
    monkeypatch.setattr(
        next_question_service.pre_generation_cache,
        "get_pre_generated_question",
        AsyncMock(return_value="Cached question?")
    )
    jd = "Some JD"
    prev_q = "Previous question"
    answer = "Some answer"

    result = await next_question_service.generate_next_question(jd, prev_q, answer)
    assert result == "Cached question?"


@pytest.mark.asyncio
async def test_generate_next_question_none_response(monkeypatch):
    """Test fallback default is used if Gemini returns None."""
    monkeypatch.setattr(
        next_question_service.pre_generation_cache,
        "get_pre_generated_question",
        AsyncMock(return_value=None)
    )
    monkeypatch.setattr(
        next_question_service.gemini_client,
        "generate_text",
        AsyncMock(return_value=None)
    )

    jd = "Some JD"
    prev_q = "Previous question"
    answer = "Some answer"

    result = await next_question_service.generate_next_question(jd, prev_q, answer)
    assert result == "What challenges have you faced in your recent projects?"


@pytest.mark.asyncio
async def test_generate_next_question_stream(monkeypatch):
    """Test that streaming generator yields expected chunks."""
    async def mock_stream(prompt, chunk_size):
        for chunk in ["chunk1", "chunk2", "chunk3"]:
            yield chunk

    monkeypatch.setattr(
        next_question_service.gemini_client,
        "generate_stream",
        mock_stream
    )

    jd = "Some JD"
    prev_q = "Prev Q"
    answer = "Answer"

    chunks = []
    async for chunk in next_question_service.generate_next_question_stream(jd, prev_q, answer):
        chunks.append(chunk)

    assert chunks == ["chunk1", "chunk2", "chunk3"]
