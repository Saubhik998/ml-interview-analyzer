from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)

def test_next_question_endpoint_success():
    payload = {
        "jd": "We're hiring a machine learning engineer with experience in deep learning.",
        "previous_question": "Tell me about your experience with neural networks.",
        "answer": "I've implemented CNNs and RNNs for computer vision and NLP projects."
    }

    response = client.post("/api/next-question", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "next_question" in data
    assert isinstance(data["next_question"], str)

def test_next_question_endpoint_missing_fields():
    payload = {
        "jd": "We need an ML engineer."  # Missing previous_question and answer
    }

    response = client.post("/api/next-question", json=payload)
    assert response.status_code == 422  # Unprocessable Entity due to validation error

@patch("app.routers.next_question.next_question_service.generate_next_question")
def test_next_question_endpoint_service_error(mock_generate):
    mock_generate.side_effect = Exception("Gemini API error")

    payload = {
        "jd": "We're hiring a data scientist.",
        "previous_question": "What experience do you have with data pipelines?",
        "answer": "I've built ETL workflows using Airflow and Spark."
    }

    response = client.post("/api/next-question", json=payload)
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error: Could not generate next question."
