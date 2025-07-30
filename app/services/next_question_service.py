import logging
import google.generativeai as genai
from ..config import GEMINI_KEY

# Configure API key globally before using the client
genai.configure(api_key=GEMINI_KEY)

# Initialize logger for the current module
logger = logging.getLogger(__name__)

# Create the GenerativeModel instance after configuration to interact with Gemini
client = genai.GenerativeModel(model_name="gemini-2.0-flash")

def generate_next_question(jd: str, previous_question: str, answer: str) -> str:
    """
    Uses Gemini to generate the next interview question based on:
    - the job description,
    - the previous question asked,
    - and the candidate's answer.

    Returns a single follow-up question in human-like, natural language.
    """
    # Compose a detailed prompt for the AI with interview context and instructions
    prompt = (
        f"You are an professional interviewer for the following job:\n\n"
        f"{jd}\n\n"
        f"The previous question was:\n\"{previous_question}\"\n\n"
        f"The candidate answered:\n\"{answer}\"\n\n"
        f"Based on the previous conversation, ask the next relevant interview question (question should be like the candidate can answer it by speaking only no need for question related to live coding or code sharing). "
        f"If the candidate's response is off-topic, irrelevant, or does not directly answer the question asked, respond with: 'That doesn’t answer my question. Can you explain how that’s relevant to this interview?' Then, immediately discard the response and pose a new, relevant interview question.\n\n"
        f"If the candidate indicates in any way that they don't know, are unsure, cannot answer, or do not wish to answer (for example, by saying 'I don't know', 'I'm not sure', 'I can't answer that', 'I prefer not to answer', etc.), smoothly move to a different, relevant topic based on the job description and ask a new question.\n"
        f"No extra explanation, no numbering, and be as human as possible."
    )


    # Fallback question in case of empty AI output
    fallback_default = "What challenges have you faced in your recent projects?"
    # Fallback question in case of an exception or error
    fallback_error = "Can you tell me more about your experience working in a team?"

    try:
        # Request the next question from Gemini using the crafted prompt
        response = client.generate_content(prompt)

        # Try to extract the primary text response from Gemini
        text = getattr(response, "text", None)
        if text:
            return text.strip()  # Return the next question, trimmed of whitespace

        # If the main text attribute is absent, check if there's a 'parts' structure (alternate format)
        if hasattr(response, "parts") and response.parts:
            part_text = getattr(response.parts[0], "text", None)
            if part_text:
                return part_text.strip()  # Return the part's text, trimmed of whitespace

        # If there is no valid answer, log a warning and return the default fallback
        logger.warning("Gemini returned empty or unexpected format. Using fallback default.")
        return fallback_default

    except Exception as e:
        # In case of any error, log the error and return the fallback error question
        logger.error("Error generating next question: %s", e)
        return fallback_error
