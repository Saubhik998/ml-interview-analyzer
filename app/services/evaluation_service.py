import logging
from ..services import gemini_client
import json
import re
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def _build_schema_example():
    return json.dumps({
        "jd": "...",
        "score": "<number between 0 and 100>",
        "questions": ["..."],
        "answers": ["..."],
        "strengths": ["..."],
        "improvements": ["..."],
        "followUps": ["..."]
    }, indent=2)

async def evaluate_interview(jd: str, questions: list[str], answers: list[str]) -> dict:
    """
    Async evaluation using your original prompt. Returns parsed JSON.
    """
    schema_example = _build_schema_example()

    prompt = f"""
You are an AI assistant. Given a job description, a list of questions, and candidate answers, return _strictly valid_ JSON matching this schema exactly (no markdown fences, no extra fields): Like fo Strengths talk about the candidate's strengths, improvements talk about areas they can improve, and followUps are to schedule to next round of interview or not and what to ask the candidate in the next round.
Give the score based on the responses the candidate gives.
{schema_example}

Job Description:
{jd}

Questions: {json.dumps(questions)}

Answers:   {json.dumps(answers)}
"""

    try:
        raw_text = await gemini_client.generate_text(prompt)
        raw_text = raw_text.strip()

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
        logger.debug("Raw response: %s", raw_text if 'raw_text' in locals() else "N/A")
        raise HTTPException(status_code=502, detail="AI evaluation returned malformed JSON.")
    except Exception as e:
        logger.exception("Evaluation error")
        raise HTTPException(status_code=500, detail="Failed to generate AI evaluation.")
