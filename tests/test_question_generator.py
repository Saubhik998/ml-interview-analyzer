import pytest
from unittest.mock import patch, MagicMock
from app.services.question_generator import generate_first_question

@patch("app.services.question_generator.model.generate_content")
def test_generate_first_question(mock_generate):
    mock_resp = MagicMock()
    mock_resp.text = "What programming languages are you most comfortable with?"
    mock_generate.return_value = mock_resp

    jd = "Hiring a full-stack engineer with React and Node.js experience"
    result = generate_first_question(jd)

    assert isinstance(result, str)
    assert result.endswith("?")
