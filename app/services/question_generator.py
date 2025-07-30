import logging
import google.generativeai as genai
from ..config import GEMINI_KEY

# Configure Gemini API with your API key
genai.configure(api_key=GEMINI_KEY)

# Initialize the generative model once, globally,
# so it can be reused on each function call efficiently
model = genai.GenerativeModel("gemini-2.0-flash")

# Set up logger for this module (good for monitoring & debugging)
logger = logging.getLogger(__name__)

def generate_first_question(jd: str) -> str:
    """
    Generate the very first technical interview question for a candidate
    based only on the given job description.
    
    - The question should focus purely on technical knowledge relevant to the JD.
    - It should NOT be about the candidate's past experience or projects.
    - Each invocation should ideally vary the question ("everytime a new question").
    - The output must be just the question (no numbering, formatting, or explanation).
    
    Args:
        jd (str): The job description text.
    Returns:
        str: The first technical interview question generated.
    Raises:
        RuntimeError: If Gemini fails to generate a question.
    """
    # Compose a detailed, instruction-driven prompt for Gemini
    prompt = f"""
You are a professional interviewer.

Analyse the following job description select all the skills and knowledge areas required , ask the **first** interview question to a candidate, make sure you ask the question keeping all the skills and knowledge areas from the job description in mind just based on technical knowledge no previous experience and projects and everytime a new question make sure you keep the question short like not very short but also not very long.

Only return the question. No numbering. No formatting. No extra explanation.

Job Description:
\"\"\"{jd}\"\"\"
"""
    try:
        # Request Gemini to generate a question using the crafted prompt
        response = model.generate_content(prompt)
        # Strip extra whitespace from Gemini's response and return
        return response.text.strip()

    except Exception as e:
        # Log detailed error info for debugging
        logger.error("Error generating first question: %s", e)
        # Raise a generic exception to the calling context
        raise RuntimeError("Failed to generate first question")
