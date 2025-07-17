from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel
from ..services import next_question_service

# Create a FastAPI router for next-question generation
router = APIRouter()

# Request schema for generating the next interview question
class NextQuestionRequest(BaseModel):
    jd: str                    # Job description
    previous_question: str     # Previous question asked to the candidate
    answer: str                # Candidate's answer to the previous question

# Response schema containing the next generated question
class NextQuestionResponse(BaseModel):
    next_question: str

@router.post("/next-question", response_model=NextQuestionResponse)
async def get_next_question(request: NextQuestionRequest):
    """
    Generate the next interview question dynamically based on:
    - Job Description (JD)
    - Previous Question
    - Candidate's Answer

    Returns a follow-up question to make the interview more contextual and adaptive.
    """
    try:
        # Run the next-question generator in a thread pool 
        question = await run_in_threadpool(
            next_question_service.generate_next_question,
            request.jd,
            request.previous_question,
            request.answer
        )
        # Wrap the result in the response schema
        return NextQuestionResponse(next_question=question)
    except Exception:
        # handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: Could not generate next question."
        )
