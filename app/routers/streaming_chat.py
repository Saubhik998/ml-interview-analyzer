import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.llm_streaming_service import stream_conversation_responses

# Create an API router for chat-related WebSocket endpoints
router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time AI conversational streaming.

    Flow:
    1. Accepts a WebSocket connection from the client.
    2. Listens for incoming text messages from the user.
    3. For each message, builds a prompt to send to the LLM.
    4. Streams back the LLM's partial responses chunk-by-chunk to the client.
    5. Sends a special "[END_OF_RESPONSE]" marker when a complete answer is finished.

    This allows the user to see the AI's reply in real time as it is generated.
    """
    await websocket.accept()
    try:
        while True:
            # Receive the user's input from the WebSocket connection
            data = await websocket.receive_text()

            # Create a system-friendly prompt to instruct the AI to act like an interviewer
            prompt = (
                "You are a helpful interviewer AI. Respond conversationally:\n"
                f"User: {data}\n"
                "AI:"
            )

            logger.debug("Received prompt for streaming chat.")

            # Stream the AI's response in chunks and send them back to the client
            async for chunk in stream_conversation_responses(prompt):
                await websocket.send_text(chunk)

            # Indicate to the client that the AI's response is complete
            await websocket.send_text("[END_OF_RESPONSE]")

    except WebSocketDisconnect:
        # Client disconnected normally — no error, just log it
        logger.info("Client disconnected from WebSocket chat")

    except Exception as e:
        # Log unexpected errors for debugging
        logger.error(f"WebSocket error: {e}")
        try:
            # Try to close connection with an error code
            await websocket.close(code=1011, reason="Internal Server Error")
        except Exception:
            # Closing the socket failed — usually safe to ignore
            logger.debug("WebSocket close failed.")
