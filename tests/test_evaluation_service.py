import pytest
from unittest.mock import patch, MagicMock
from app.services.evaluation_service import evaluate_interview

@patch("app.services.evaluation_service.model.generate_content")
def test_evaluate_interview_success(mock_generate):
    # Valid Gemini response
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
    mock_resp = MagicMock()
    mock_resp.text = fake_json
    mock_generate.return_value = mock_resp

    jd = "Looking for a Python developer"
    questions = ["What is your experience with Python?"]
    answers = ["I have worked with Python for 3 years."]

    result = evaluate_interview(jd, questions, answers)

    assert result["score"] == 85
    assert "strengths" in result
    assert isinstance(result["strengths"], list)

@patch("app.services.evaluation_service.model.generate_content")
def test_evaluate_interview_invalid_json(mock_generate):
    # Gemini returns malformed JSON
    mock_resp = MagicMock()
    mock_resp.text = "Not a JSON response"
    mock_generate.return_value = mock_resp

    jd = "Test JD"
    questions = ["Q1"]
    answers = ["A1"]

    with pytest.raises(ValueError, match="Gemini response is not valid JSON"):
        evaluate_interview(jd, questions, answers)

@patch("app.services.evaluation_service.model.generate_content")
def test_evaluate_interview_gemini_failure(mock_generate):
    # Gemini raises an internal error
    mock_generate.side_effect = Exception("Gemini is down")

    jd = "Test JD"
    questions = ["Q1"]
    answers = ["A1"]

    with pytest.raises(RuntimeError, match="Failed to generate evaluation from Gemini"):
        evaluate_interview(jd, questions, answers)
