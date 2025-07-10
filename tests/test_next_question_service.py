import pytest
from unittest.mock import patch, MagicMock
from app.services.next_question_service import generate_next_question

@patch("app.services.next_question_service.client.generate_content")
def test_generate_next_question(mock_generate):
    mock_resp = MagicMock()
    mock_resp.text = "What is your experience working in a team?"
    mock_generate.return_value = mock_resp

    jd = "We want a backend engineer with API design experience."
    prev_q = "Tell me about a project you built with FastAPI."
    answer = "I built a real-time dashboard using FastAPI and WebSocket."

    result = generate_next_question(jd, prev_q, answer)

    assert isinstance(result, str)
    assert result.startswith("What")
