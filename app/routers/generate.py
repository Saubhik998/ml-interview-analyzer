from fastapi import APIRouter, HTTPException
from ..schemas.request_response import JDRequest, FirstQuestionResponse
from ..services.question_generator import generate_first_question

# Create an API router for grouping question-generation-related endpoints
router = APIRouter()

@router.post("/generate", response_model=FirstQuestionResponse)
async def generate(req: JDRequest):
    """
    Generate the first interview question based on the provided job description (JD).
    
    - Accepts: A job description (JD) in the request body.
    - Returns: A list containing a single first interview question.
    - Used as the starting point of the interview process.
    """
    try:
        # Call the question generator service to produce a relevant first question.
        question = await generate_first_question(req.jd)

        # Wrap the single question in a list (as defined in the response schema)
        return {"questions": [question]}

    except Exception:
        # Any unexpected errors (LLM/API failure, service issue, etc.)
        # are returned as a generic 500 Internal Server Error response.
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: Question generation failed."
        )
