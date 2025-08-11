import logging
from ..services import gemini_client

logger = logging.getLogger(__name__)

async def stream_conversation_responses(prompt: str):
    """
    Async generator that yields partial outputs from Gemini model as they are generated.
    Uses the shared gemini_client.generate_stream() which attempts SDK streaming and
    falls back to chunked synchronous generation when necessary.
    """
    try:
        async for chunk in gemini_client.generate_stream(prompt, chunk_size=32):
            yield chunk
    except Exception as e:
        logger.exception("Error while streaming conversation responses: %s", e)
        yield "[Error generating response]"
