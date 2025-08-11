import pytest
from unittest.mock import AsyncMock, patch
from starlette.websockets import WebSocketDisconnect

from app.routers import streaming_chat


class FakeWebSocket:
    def __init__(self):
        self.sent_texts = []
        self.accept_called = False
        self.closed = False
        self.close_code = None
        self.close_reason = None
        self.messages_to_receive = []
        self.receive_counter = 0

    async def accept(self):
        self.accept_called = True

    async def receive_text(self):
        # Simulate receiving sequential messages
        if self.receive_counter < len(self.messages_to_receive):
            msg = self.messages_to_receive[self.receive_counter]
            self.receive_counter += 1
            if isinstance(msg, Exception):
                raise msg
            return msg
        raise WebSocketDisconnect()

    async def send_text(self, text):
        self.sent_texts.append(text)

    async def close(self, code=None, reason=None):
        self.closed = True
        self.close_code = code
        self.close_reason = reason


@pytest.mark.asyncio
async def test_websocket_chat_normal_flow(monkeypatch):
    ws = FakeWebSocket()
    ws.messages_to_receive = ["Hello AI"]

    # Mock stream_conversation_responses to return two chunks
    async def fake_stream(prompt):
        yield "chunk1"
        yield "chunk2"

    monkeypatch.setattr(streaming_chat, "stream_conversation_responses", fake_stream)

    await streaming_chat.websocket_chat(ws)

    assert ws.accept_called
    assert ws.sent_texts == ["chunk1", "chunk2", "[END_OF_RESPONSE]"]


@pytest.mark.asyncio
async def test_websocket_chat_client_disconnect(monkeypatch):
    ws = FakeWebSocket()
    ws.messages_to_receive = [WebSocketDisconnect()]

    # The generator should never be called
    monkeypatch.setattr(streaming_chat, "stream_conversation_responses", AsyncMock())

    await streaming_chat.websocket_chat(ws)

    assert ws.accept_called
    # No messages sent
    assert ws.sent_texts == []


@pytest.mark.asyncio
async def test_websocket_chat_general_exception(monkeypatch):
    ws = FakeWebSocket()
    ws.messages_to_receive = ["This will fail"]

    # Force an exception inside the generator
    async def failing_stream(prompt):
        raise RuntimeError("LLM failed")

    monkeypatch.setattr(streaming_chat, "stream_conversation_responses", failing_stream)

    await streaming_chat.websocket_chat(ws)

    assert ws.accept_called
    assert ws.closed
    assert ws.close_code == 1011
    assert ws.close_reason == "Internal Server Error"
