import logging
from ..services import gemini_client

logger = logging.getLogger(__name__)

async def stream_conversation_responses(prompt: str):
    """
    Stream AI-generated conversation responses in real-time.

    This function is an **async generator**, meaning it produces chunks of text
    over time instead of waiting for the entire AI response to complete.  
    It's useful for live chat or interview scenarios where immediate partial
    feedback improves the user experience.

    Args:
        prompt (str): The text prompt to send to the AI model.

    Yields:
        str: A chunk (partial segment) of the AI's generated response.

    Process:
    1. Call `gemini_client.generate_stream()` with the given prompt.
    2. Stream partial text chunks as they are produced by the AI.
    3. If streaming fails, catch the exception and yield a fallback error message.

    Notes:
        - `chunk_size=32` means the model will stream up to 32 characters
          per chunk before yielding.
        - `generate_stream()` internally handles fallback logic:
            * Uses SDK's native streaming if available.
            * Falls back to chunked generation if streaming is unsupported.
        - This function should be consumed using `async for`.

    Example:
        async for part in stream_conversation_responses("Hello AI!"):
            print(part, end="", flush=True)
    """
    try:
        # Stream partial output chunks from the Gemini client
        async for chunk in gemini_client.generate_stream(prompt, chunk_size=32):
            yield chunk

    except Exception as e:
        # Log unexpected errors and yield an error message back to the client
        logger.exception("Error while streaming conversation responses: %s", e)
        yield "[Error generating response]"
