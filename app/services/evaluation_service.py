import logging
import google.generativeai as genai
from ..config import GEMINI_KEY
import json
import re
from fastapi import HTTPException

# Configure Gemini
genai.configure(api_key=GEMINI_KEY)

# Initialize logger
logger = logging.getLogger(__name__)

# Load model
model = genai.GenerativeModel("gemini-1.5-flash")

def evaluate_interview(jd: str, questions: list[str], answers: list[str]) -> dict:
    # Example schema with concrete JSON to guide output
    schema_example = json.dumps({
        "jd": "...",
        "score": 0,
        "questions": ["..."],
        "answers": ["..."],
        "strengths": ["..."],
        "improvements": ["..."],
        "followUps": ["..."]
    }, indent=2)

    prompt = f"""
You are an AI assistant. Given a job description, a list of questions, and candidate answers, return _strictly valid_ JSON matching this schema exactly (no markdown fences, no extra fields):

{schema_example}

Job Description:
{jd}

Questions: {json.dumps(questions)}

Answers:   {json.dumps(answers)}
"""

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Strip markdown fences and code blocks
        cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", raw_text)
        # Remove trailing commas before closing braces/brackets
        cleaned = re.sub(r",\s*}(?=\s*$)", "}", cleaned)
        cleaned = re.sub(r",\s*](?=\s*$)", "]", cleaned)

        evaluation = json.loads(cleaned)
        logger.info("Successfully parsed Gemini evaluation response.")
        return evaluation

    except json.JSONDecodeError as e:
        logger.error("Invalid JSON from Gemini: %s", e)
        logger.debug("Raw response: %s", raw_text)
        raise HTTPException(status_code=502, detail="AI evaluation returned malformed JSON.")
    except Exception as e:
        logger.exception("Evaluation error")
        raise HTTPException(status_code=500, detail="Failed to generate AI evaluation.")
