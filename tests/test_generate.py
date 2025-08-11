from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock
import pytest

client = TestClient(app)


@pytest.mark.asyncio
async def test_generate_endpoint_success(monkeypatch):
    """Test successful generation with mocked generate_first_question."""
    mock_question = "What experience do you have with React and TypeScript?"
    mock_generate = AsyncMock(return_value=mock_question)

    # Patch the service method to return mock_question
    monkeypatch.setattr(
        "app.routers.generate.generate_first_question",
        mock_generate
    )

    payload = {
        "jd": "We are looking for a frontend developer experienced in React and TypeScript."
    }

    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data == {"questions": [mock_question]}
    mock_generate.assert_awaited_once_with(payload["jd"])


def test_generate_endpoint_missing_jd():
    """Test validation error when JD is missing."""
    payload = {}  # JD field missing
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 422  # Unprocessable Entity


@patch("app.routers.generate.generate_first_question")
def test_generate_endpoint_service_error(mock_generate):
    """Test error handling when generate_first_question raises exception."""
    mock_generate.side_effect = Exception("LLM service failed")

    payload = {
        "jd": "We need a backend engineer with Node.js and MongoDB skills."
    }

    response = client.post("/api/generate", json=payload)
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error: Question generation failed."
