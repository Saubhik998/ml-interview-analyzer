from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_endpoint():
    payload = {
        "jd": "We are looking for a frontend developer experienced in React and TypeScript."
    }

    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert isinstance(data["questions"], list)
    assert len(data["questions"]) > 0
