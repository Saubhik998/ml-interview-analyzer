import pytest
from unittest.mock import patch, MagicMock
from app.services.evaluation_service import evaluate_interview

@patch("app.services.evaluation_service.model.generate_content")
def test_evaluate_interview(mock_generate):
    # Prepare fake Gemini output (as a JSON string inside a code block)
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
