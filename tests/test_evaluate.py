from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_evaluate_endpoint():
    payload = {
        "jd": "We are hiring a software engineer skilled in Python and web development.",
        "questions": [
            "What experience do you have with backend frameworks like Django or FastAPI?"
        ],
        "answers": [
            "I have used FastAPI in several projects including REST APIs and async apps."
        ]
    }

    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "strengths" in data
    assert "improvements" in data
    assert "followUps" in data
