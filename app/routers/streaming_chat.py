import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.llm_streaming_service import stream_conversation_responses

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint to handle real-time conversational streaming with LLM.
    Receives text messages, sends partial streamed responses back.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            prompt = f"You are a helpful interviewer AI. Respond conversationally:\nUser: {data}\nAI:"
            logger.debug("Received prompt for streaming chat.")
            async for chunk in stream_conversation_responses(prompt):
                await websocket.send_text(chunk)
            await websocket.send_text("[END_OF_RESPONSE]")
    except WebSocketDisconnect:
        logger.info("Client disconnected from WebSocket chat")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal Server Error")
        except Exception:
            logger.debug("Websocket close failed.")
