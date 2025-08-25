import logging
from ..services import gemini_client, pre_generation_cache

logger = logging.getLogger(__name__)


def _build_prompt(jd: str, previous_question: str, answer: str) -> str:
    """
    Build the exact prompt sent to the LLM.

    IMPORTANT: This function returns the prompt text verbatim. Do not alter
    the wording unless you intentionally want to change the model's behavior.
    """
    return (
        f"You are an professional interviewer for the following job:\n\n"
        f"{jd}\n\n"
        f"The previous question was:\n\"{previous_question}\"\n\n"
        f"The candidate answered:\n\"{answer}\"\n\n"

        f"Based on the previous conversation, Ask the next relevant interview question that can be answered verbally (no coding or screen sharing required). Only ask about skills and topics present in the job description. "

        f"Do not evaluate or judge whether the candidate's answer is correct or incorrect. Only ensure that the response is on-topic, relevant to the question, and aligned with the skills or topics in the job description."

        f"If the candidate's response is off-topic, consists of unrelated jargon just ignore the previous response and ask a new, relevant question based only on the job description."

        f"If the candidate tries to shift the conversation to skills or topics not included in the job description, politely steer the conversation back. Then proceed with a relevant question according to jd.\n"

        f"If the candidate is unable or unwilling to answer (for example, says, I don't know, I'm not sure, etc.), smoothly switch to another relevant topic from the job description and ask a new question."

        f"Do not include any extra explanation, numbering, or filler phrases such as \"That's a good overview,\" \"Thanks for that,\" or \"That's a good example.\"Directly ask the next relevant interview question without any commentary or acknowledgments of the candidate's previous answers"

        f"Keep the tone conversational and engaging. Make sure the question is clear, concise, and easy to understand. Avoid complex or technical jargon that might confuse the candidate."
    )


async def generate_next_question(jd: str, previous_question: str, answer: str) -> str:
    """
    Return the next interview question (string).

    Behavior:
      1. Check pre_generation_cache for a cached question (fast path).
      2. If none, build the prompt and call gemini_client.generate_text().
      3. If the LLM returns an empty string, use `fallback_default`.
      4. On any exception, return `fallback_error`.

    This function intentionally returns raw strings from the LLM or the fallbacks.
    """
    # 1) Try cache first — very low latency if available
    cached_q = await pre_generation_cache.get_pre_generated_question(jd)
    if cached_q:
        logger.info("Using pre-generated question from cache.")
        return cached_q

    # 2) Build prompt and call model
    prompt = _build_prompt(jd, previous_question, answer)
    fallback_default = "What challenges have you faced in your recent projects?"
    fallback_error = "Can you tell me more about your experience working in a team?"

    try:
        text = await gemini_client.generate_text(prompt)
        if text:
            # Trim whitespace and return
            return text.strip()

        # Treat empty/None as unexpected; use a safe default
        logger.warning("Gemini returned empty or unexpected format. Using fallback default.")
        return fallback_default

    except Exception as e:
        # Log the error and return a safe fallback (do not raise here)
        logger.error("Error generating next question: %s", e)
        return fallback_error


async def generate_next_question_stream(jd: str, previous_question: str, answer: str):
    """
    Async generator that yields chunks of the next question as they're generated.

    Consumers should use `async for chunk in generate_next_question_stream(...)`.
    Each `chunk` is a partial string produced by gemini_client.generate_stream.
    """
    prompt = _build_prompt(jd, previous_question, answer)
    async for chunk in gemini_client.generate_stream(prompt, chunk_size=64):
        yield chunk
