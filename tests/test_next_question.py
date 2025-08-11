import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_next_question_endpoint_success(monkeypatch):
    mock_question = "What is your experience with cloud platforms?"
    mock_generate = AsyncMock(return_value=mock_question)
    monkeypatch.setattr(
        "app.routers.next_question.next_question_service.generate_next_question",
        mock_generate
    )

    payload = {
        "jd": "We're hiring a machine learning engineer with experience in deep learning.",
        "previous_question": "Tell me about your experience with neural networks.",
        "answer": "I've implemented CNNs and RNNs for computer vision and NLP projects."
    }

    response = client.post("/api/next-question", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["next_question"] == mock_question

    # Allow for multiple awaits due to background task execution
    assert mock_generate.await_count >= 1
    first_call_args = mock_generate.await_args_list[0].args
    assert first_call_args[0] == payload["jd"]
    assert first_call_args[1] == payload["previous_question"]
    assert first_call_args[2] == payload["answer"]


def test_next_question_endpoint_missing_fields():
    payload = {
        "jd": "We need an ML engineer."  # Missing previous_question and answer
    }

    response = client.post("/api/next-question", json=payload)
    assert response.status_code == 422  # Validation error


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


@pytest.mark.asyncio
async def test_websocket_next_question_with_cache(monkeypatch):
    async def mock_get_cache(jd):
        return "Cached Question"

    monkeypatch.setattr(
        "app.routers.next_question.pre_generation_cache.get_pre_generated_question",
        mock_get_cache
    )

    with client.websocket_connect("/api/ws/next-question") as websocket:
        payload = {
            "jd": "Test JD",
            "previous_question": "Prev Q",
            "answer": "Some answer"
        }
        websocket.send_json(payload)
        msg1 = websocket.receive_text()
        msg2 = websocket.receive_text()
        assert msg1 == "Cached Question"
        assert msg2 == "[END_OF_RESPONSE]"


@pytest.mark.asyncio
async def test_websocket_next_question_invalid_payload():
    with client.websocket_connect("/api/ws/next-question") as websocket:
        websocket.send_text("invalid json")
        msg = websocket.receive_text()
        assert msg == "[Error] Invalid payload format."


@pytest.mark.asyncio
async def test_websocket_next_question_no_cache_streaming(monkeypatch):
    async def mock_get_cache(jd):
        return None

    async def mock_stream(jd, prev_q, ans):
        yield "Streamed chunk 1"
        yield "Streamed chunk 2"

    monkeypatch.setattr(
        "app.routers.next_question.pre_generation_cache.get_pre_generated_question",
        mock_get_cache
    )
    monkeypatch.setattr(
        "app.routers.next_question.next_question_service.generate_next_question_stream",
        mock_stream
    )

    with client.websocket_connect("/api/ws/next-question") as websocket:
        payload = {
            "jd": "Test JD",
            "previous_question": "Prev Q",
            "answer": "Some answer"
        }
        websocket.send_json(payload)
        chunks = []
        chunks.append(websocket.receive_text())
        chunks.append(websocket.receive_text())
        chunks.append(websocket.receive_text())
        assert chunks[0] == "Streamed chunk 1"
        assert chunks[1] == "Streamed chunk 2"
        assert chunks[2] == "[END_OF_RESPONSE]"
