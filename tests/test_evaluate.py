from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
import pytest

client = TestClient(app)

def test_evaluate_endpoint_success():
    payload = {
        "jd": "We are hiring a software engineer skilled in Python and web development.",
        "questions": [
            "What experience do you have with backend frameworks like Django or FastAPI?"
        ],
        "answers": [
            "I have used FastAPI in several projects including REST APIs and async apps."
        ]
    }

    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "strengths" in data
    assert "improvements" in data
    assert "followUps" in data

def test_evaluate_endpoint_missing_fields():
    # Missing "answers" field
    payload = {
        "jd": "We are hiring a Python developer.",
        "questions": ["What is your experience with Django?"]
    }

    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 422  

@patch("app.routers.evaluate.evaluate_interview")

def test_evaluate_endpoint_gemini_error(mock_eval):
    mock_eval.side_effect = Exception("Gemini service failed")

    payload = {
        "jd": "We are hiring a Python developer.",
        "questions": ["Tell me about your backend experience."],
        "answers": ["I have worked on multiple REST APIs using FastAPI."]
    }

    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 500
    assert response.json()["detail"] == "Evaluation failed: Gemini service failed"
