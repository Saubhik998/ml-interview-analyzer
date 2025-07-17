import logging
import google.generativeai as genai
from ..config import GEMINI_KEY

# Configure Gemini API with your API key
genai.configure(api_key=GEMINI_KEY)

# Initialize the generative model once, globally
model = genai.GenerativeModel("gemini-2.0-flash")

# Set up logger
logger = logging.getLogger(__name__)

def generate_first_question(jd: str) -> str:
    prompt = f"""
You are an expert technical interviewer.

Based on the following job description, ask the **first** interview question to a candidate.

Only return the question. No numbering. No formatting. No extra explanation.

Job Description:
\"\"\"{jd}\"\"\"
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        logger.error("Error generating first question: %s", e)
        raise RuntimeError("Failed to generate first question")
