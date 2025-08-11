from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock
import pytest

client = TestClient(app)


@pytest.mark.asyncio
async def test_evaluate_endpoint_success(monkeypatch):
    """Test successful evaluation with mocked evaluate_interview."""
    mock_response = {
        "jd": "We are hiring a software engineer skilled in Python and web development.",
        "questions": [
            "What experience do you have with backend frameworks like Django or FastAPI?"
        ],
        "answers": [
            "I have used FastAPI in several projects including REST APIs and async apps."
        ],
        "score": 85,
        "strengths": ["Strong Python knowledge", "Good FastAPI experience"],
        "improvements": ["Could improve on testing strategies"],
        "followUps": ["Tell me about a challenging bug you fixed."]
    }
    mock_eval = AsyncMock(return_value=mock_response)
    monkeypatch.setattr(
        "app.routers.evaluate.evaluate_interview",
        mock_eval
    )

    payload = {
        "jd": mock_response["jd"],
        "questions": mock_response["questions"],
        "answers": mock_response["answers"]
    }

    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data == mock_response
    mock_eval.assert_awaited_once_with(
        payload["jd"], payload["questions"], payload["answers"]
    )


def test_evaluate_endpoint_missing_fields():
    """Test missing fields validation."""
    # Missing "answers" field
    payload = {
        "jd": "We are hiring a Python developer.",
        "questions": ["What is your experience with Django?"]
    }

    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 422  # Unprocessable Entity


@patch("app.routers.evaluate.evaluate_interview")
def test_evaluate_endpoint_gemini_error(mock_eval):
    """Test exception handling when evaluate_interview fails."""
    mock_eval.side_effect = Exception("Gemini service failed")

    payload = {
        "jd": "We are hiring a Python developer.",
        "questions": ["Tell me about your backend experience."],
        "answers": ["I have worked on multiple REST APIs using FastAPI."]
    }

    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 500
    assert response.json()["detail"] == "Evaluation failed: Gemini service failed"
