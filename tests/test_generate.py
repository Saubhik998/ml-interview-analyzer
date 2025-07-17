from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
import pytest

client = TestClient(app)

def test_generate_endpoint_success():
    payload = {
        "jd": "We are looking for a frontend developer experienced in React and TypeScript."
    }

    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert isinstance(data["questions"], list)
    assert len(data["questions"]) > 0

def test_generate_endpoint_missing_jd():
    payload = {}  # JD field is missing
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 422  # Validation error

@patch("app.routers.generate.generate_first_question")
def test_generate_endpoint_service_error(mock_generate):
    def raise_exception(*args, **kwargs):
        raise Exception("LLM service failed")

    mock_generate.side_effect = raise_exception

    payload = {
        "jd": "We need a backend engineer with Node.js and MongoDB skills."
    }

    response = client.post("/api/generate", json=payload)
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error: Question generation failed."

