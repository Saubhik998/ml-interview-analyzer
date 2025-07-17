import logging
import google.generativeai as genai
from ..config import GEMINI_KEY

# Configure API key globally before using the client
genai.configure(api_key=GEMINI_KEY)

# Initialize logger
logger = logging.getLogger(__name__)

# Create the GenerativeModel instance after configuration
client = genai.GenerativeModel(model_name="gemini-2.0-flash")

def generate_next_question(jd: str, previous_question: str, answer: str) -> str:
    """
    Uses Gemini to generate the next interview question based on:
    - the job description,
    - the previous question asked,
    - and the candidate's answer.

    Returns a single follow-up question in human-like, natural language.
    """
    prompt = (
        f"You are an interviewer for the following job:\n\n"
        f"{jd}\n\n"
        f"The previous question was:\n\"{previous_question}\"\n\n"
        f"The candidate answered:\n\"{answer}\"\n\n"
        f"Based on this answer, ask the next relevant interview question. "
        f"No extra explanation, no numbering, and be as human as possible."
    )

    fallback_default = "What challenges have you faced in your recent projects?"
    fallback_error = "Can you tell me more about your experience working in a team?"

    try:
        response = client.generate_content(prompt)

        text = getattr(response, "text", None)
        if text:
            return text.strip()

        if hasattr(response, "parts") and response.parts:
            part_text = getattr(response.parts[0], "text", None)
            if part_text:
                return part_text.strip()

        logger.warning("Gemini returned empty or unexpected format. Using fallback default.")
        return fallback_default

    except Exception as e:
        logger.error("Error generating next question: %s", e)
        return fallback_error
