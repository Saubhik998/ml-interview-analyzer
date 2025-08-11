import logging
from ..services import gemini_client

logger = logging.getLogger(__name__)

async def generate_first_question(jd: str) -> str:
    """
    Generate the very first technical interview question for a candidate
    based only on the given job description.

    Prompt content is intentionally preserved exactly.
    """
    prompt = f"""
You are a professional interviewer.

Analyze the following job description and identify all required technical skills. Create the first interview question that primarily tests the candidate's technical knowledge, including backend, frontend, architecture, security, performance, and testing aspects. You may integrate non-technical or leadership elements only as they relate directly to the technical execution. The question should be theoretical, focused, and concise—long enough to be clear but not overwhelming. Avoid asking about prior experience or projects. Provide only the question, no explanations or skill lists. Generate a new and unique question each time.

Only return the question. No numbering. No formatting. No extra explanation.

Job Description:
\"\"\"{jd}\"\"\" 
"""
    try:
        text = await gemini_client.generate_text(prompt)
        return text.strip()
    except Exception as e:
        logger.error("Error generating first question: %s", e)
        raise RuntimeError("Failed to generate first question")
