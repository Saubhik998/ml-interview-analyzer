import logging
import google.generativeai as genai
from ..config import GEMINI_KEY
import json
import re

# Configure Gemini
genai.configure(api_key=GEMINI_KEY)

# Initialize logger
logger = logging.getLogger(__name__)

# Load model
model = genai.GenerativeModel("gemini-1.5-flash")

def evaluate_interview(jd: str, questions: list[str], answers: list[str]) -> dict:

    prompt = f"""
    Based on the following job description, questions, and candidate answers, evaluate the candidate and return a JSON in this exact format:

    {{
      "jd": string,
      "score": integer (0-100),
      "questions": list of strings,
      "answers": list of strings,
      "strengths": list of strings,
      "improvements": list of strings,
      "followUps": list of strings
    }}

    Job Description:
    {jd}

    Questions:
    {json.dumps(questions)}

    Answers:
    {json.dumps(answers)}
    """

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Remove any ```json or markdown wrappers
        clean_json = re.sub(r"^```json|```$", "", raw_text, flags=re.MULTILINE).strip()

        # Parse JSON
        evaluation = json.loads(clean_json)

        logger.info("Successfully parsed Gemini evaluation response.")
        return evaluation

    except json.JSONDecodeError as e:
        logger.error("JSON decode error in Gemini response: %s", e)
        logger.debug("Raw response text: %s", raw_text)
        raise ValueError("Gemini response is not valid JSON.")

    except Exception as e:
        logger.error("Failed to generate evaluation from Gemini: %s", e)
        raise RuntimeError("Failed to generate evaluation from Gemini.")
