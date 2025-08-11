import pytest
from unittest.mock import AsyncMock
from app.services import question_generator


@pytest.mark.asyncio
async def test_generate_first_question_success(monkeypatch):
    async_mock = AsyncMock(return_value="What programming languages are you most comfortable with?")
    monkeypatch.setattr(question_generator.gemini_client, "generate_text", async_mock)

    jd = "Hiring a full-stack engineer with React and Node.js experience"
    result = await question_generator.generate_first_question(jd)

    assert isinstance(result, str)
    assert result.endswith("?")


@pytest.mark.asyncio
async def test_generate_first_question_invalid_response(monkeypatch):
    # Gemini responds with non-question text
    async_mock = AsyncMock(return_value="This is not a question")
    monkeypatch.setattr(question_generator.gemini_client, "generate_text", async_mock)

    jd = "Hiring a full-stack engineer"
    result = await question_generator.generate_first_question(jd)

    # Should still return a string
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_generate_first_question_gemini_failure(monkeypatch):
    # Simulate Gemini API failure
    async_mock = AsyncMock(side_effect=Exception("Gemini timeout"))
    monkeypatch.setattr(question_generator.gemini_client, "generate_text", async_mock)

    jd = "Hiring a backend engineer"

    with pytest.raises(RuntimeError, match="Failed to generate first question"):
        await question_generator.generate_first_question(jd)
