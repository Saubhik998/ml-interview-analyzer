from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool
from app.schemas.evaluation_schema import EvaluationRequest, EvaluationResponse
from app.services.evaluation_service import evaluate_interview

# Create a FastAPI router for the /evaluate endpoint
router = APIRouter()

@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(request: EvaluationRequest):
    """
    Evaluate the candidate's interview based on job description, questions, and answers.
    
    This endpoint uses the Gemini model to analyze responses and generate a final evaluation report,
    including candidate fit score, strengths, improvement areas, and follow-up questions.
    """
    try:
        # Offload the blocking evaluation task to a thread pool for async compatibility
        return await run_in_threadpool(
            evaluate_interview, request.jd, request.questions, request.answers
        )
    except Exception as e:
        # Return a standardized 500 error if evaluation fails
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
