import pytest
from unittest.mock import patch, MagicMock
from app.services.next_question_service import generate_next_question

@patch("app.services.next_question_service.client.generate_content")
def test_generate_next_question_success(mock_generate):
    mock_resp = MagicMock()
    mock_resp.text = "What is your experience working in a team?"
    mock_generate.return_value = mock_resp

    jd = "We want a backend engineer with API design experience."
    prev_q = "Tell me about a project you built with FastAPI."
    answer = "I built a real-time dashboard using FastAPI and WebSocket."

    result = generate_next_question(jd, prev_q, answer)

    assert isinstance(result, str)
    assert result.startswith("What")

@patch("app.services.next_question_service.client.generate_content")
def test_generate_next_question_parts_fallback(mock_generate):
    # Simulate response with no `.text`, but valid `.parts[0].text`
    mock_resp = MagicMock()
    mock_resp.text = None
    mock_resp.parts = [MagicMock(text="How do you handle API versioning?")]
    mock_generate.return_value = mock_resp

    jd = "Hiring a backend engineer"
    prev_q = "Tell me about your experience with REST APIs"
    answer = "I designed multiple microservices with Express and Django"

    result = generate_next_question(jd, prev_q, answer)
    assert result == "How do you handle API versioning?"

@patch("app.services.next_question_service.client.generate_content")
def test_generate_next_question_error_handling(mock_generate):
    # Simulate Gemini API failure
    mock_generate.side_effect = Exception("LLM failed")

    jd = "Hiring a backend engineer"
    prev_q = "What frameworks have you used?"
    answer = "I’ve used Django, Flask, and FastAPI."

    result = generate_next_question(jd, prev_q, answer)

    # Should return fallback question
    assert result == "Can you tell me more about your experience working in a team?"
