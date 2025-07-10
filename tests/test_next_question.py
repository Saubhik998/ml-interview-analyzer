from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_next_question_endpoint():
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
