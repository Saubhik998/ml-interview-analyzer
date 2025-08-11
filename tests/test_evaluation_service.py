import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from app.services import evaluation_service


@pytest.mark.asyncio
async def test_evaluate_interview_success(monkeypatch):
    fake_json = """
    {
      "jd": "Looking for a Python developer",
      "score": 85,
      "questions": ["What is your experience with Python?"],
      "answers": ["I have worked with Python for 3 years."],
      "strengths": ["Strong Python skills"],
      "improvements": ["Needs more experience with Django"],
      "followUps": ["Can you describe a Python project you led?"]
    }
    """

    async_mock = AsyncMock(return_value=fake_json)
    monkeypatch.setattr(evaluation_service.gemini_client, "generate_text", async_mock)

    jd = "Looking for a Python developer"
    questions = ["What is your experience with Python?"]
    answers = ["I have worked with Python for 3 years."]

    result = await evaluation_service.evaluate_interview(jd, questions, answers)

    assert result["score"] == 85
    assert "strengths" in result
    assert isinstance(result["strengths"], list)


@pytest.mark.asyncio
async def test_evaluate_interview_invalid_json(monkeypatch):
    async_mock = AsyncMock(return_value="Not a JSON response")
    monkeypatch.setattr(evaluation_service.gemini_client, "generate_text", async_mock)

    jd = "Test JD"
    questions = ["Q1"]
    answers = ["A1"]

    with pytest.raises(HTTPException) as exc_info:
        await evaluation_service.evaluate_interview(jd, questions, answers)

    assert exc_info.value.status_code == 502
    assert "malformed json" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_evaluate_interview_gemini_failure(monkeypatch):
    async_mock = AsyncMock(side_effect=Exception("Gemini is down"))
    monkeypatch.setattr(evaluation_service.gemini_client, "generate_text", async_mock)

    jd = "Test JD"
    questions = ["Q1"]
    answers = ["A1"]

    with pytest.raises(HTTPException) as exc_info:
        await evaluation_service.evaluate_interview(jd, questions, answers)

    assert exc_info.value.status_code == 500
    assert "failed to generate ai evaluation" in exc_info.value.detail.lower()
