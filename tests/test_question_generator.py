import pytest
from unittest.mock import patch, MagicMock
from app.services.question_generator import generate_first_question

@patch("app.services.question_generator.model.generate_content")
def test_generate_first_question_success(mock_generate):
    mock_resp = MagicMock()
    mock_resp.text = "What programming languages are you most comfortable with?"
    mock_generate.return_value = mock_resp

    jd = "Hiring a full-stack engineer with React and Node.js experience"
    result = generate_first_question(jd)

    assert isinstance(result, str)
    assert result.endswith("?")

@patch("app.services.question_generator.model.generate_content")
def test_generate_first_question_invalid_response(mock_generate):
    # Gemini responds with non-question text
    mock_resp = MagicMock()
    mock_resp.text = "This is not a question"
    mock_generate.return_value = mock_resp

    jd = "Hiring a full-stack engineer"
    
    result = generate_first_question(jd)
    # Fallback logic still returns string, so assert it handles non-question gracefully
    assert isinstance(result, str)
    assert len(result) > 0

@patch("app.services.question_generator.model.generate_content")
def test_generate_first_question_gemini_failure(mock_generate):
    # Simulate Gemini API failure
    mock_generate.side_effect = Exception("Gemini timeout")

    jd = "Hiring a backend engineer"

    with pytest.raises(RuntimeError, match="Failed to generate first question"):
        generate_first_question(jd)
