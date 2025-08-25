import logging
from ..services import gemini_client
import json
import re
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def _build_schema_example():
    """
    Returns a JSON string showing the exact output structure
    we expect from the AI model during evaluation.

    This example acts as an explicit format guide for the LLM,
    ensuring we receive a valid, parseable response.
    """
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
    Evaluate a candidate's interview performance using an AI model.

    Args:
        jd (str): The job description text.
        questions (list[str]): List of interview questions asked.
        answers (list[str]): List of candidate's corresponding answers.

    Returns:
        dict: Parsed evaluation result containing:
            - jd: The job description
            - score: A numeric performance score (0–100)
            - questions: The original questions
            - answers: The original answers
            - strengths: Identified strengths from the answers
            - improvements: Areas the candidate could improve
            - followUps: Recommendations for next round / further questions

    Process:
    1. Build a strict schema example for the AI to follow.
    2. Craft a prompt combining the schema, job description, Q/A data.
    3. Ask the Gemini LLM to generate the evaluation.
    4. Clean the raw output (strip markdown fences, fix trailing commas).
    5. Parse the cleaned output into JSON.
    6. Return the parsed evaluation dictionary.

    Raises:
        HTTPException: If AI output is malformed JSON or any error occurs.
    """
    schema_example = _build_schema_example()

    # Build the AI prompt, embedding the schema and interview data
    prompt = f"""
You are an AI assistant. Given a job description, a list of questions, and candidate answers, return _strictly valid_ JSON matching this schema exactly (no markdown fences, no extra fields). 
In "strengths" describe the candidate's positive attributes based on correct answers provided, in "improvements" list areas for development, 
and in "followUps" recommend whether to proceed to the next round and suggest follow-up questions. 
Score should reflect the quality of the answers.

{schema_example}

Job Description:
{jd}

Questions: {json.dumps(questions)}

Answers:   {json.dumps(answers)}
"""

    try:
        # Ask the Gemini model to generate the evaluation
        raw_text = await gemini_client.generate_text(prompt)
        raw_text = raw_text.strip()

        # --- Cleanup stage: ensure valid JSON before parsing ---
        # Remove ```json or ``` fences that LLM might add
        cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", raw_text)
        # Remove trailing commas before closing braces/brackets (common JSON error)
        cleaned = re.sub(r",\s*}(?=\s*$)", "}", cleaned)
        cleaned = re.sub(r",\s*](?=\s*$)", "]", cleaned)

        # Attempt to parse the AI's JSON output
        evaluation = json.loads(cleaned)
        logger.info("Successfully parsed Gemini evaluation response.")
        return evaluation

    except json.JSONDecodeError as e:
        # The AI returned invalid JSON
        logger.error("Invalid JSON from Gemini: %s", e)
        logger.debug("Raw response: %s", raw_text if 'raw_text' in locals() else "N/A")
        raise HTTPException(status_code=502, detail="AI evaluation returned malformed JSON.")

    except Exception as e:
        # Unexpected errors (network issues, model errors, etc.)
        logger.exception("Evaluation error")
        raise HTTPException(status_code=500, detail="Failed to generate AI evaluation.")
