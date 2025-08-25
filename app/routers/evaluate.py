from fastapi import APIRouter, HTTPException
from app.schemas.evaluation_schema import EvaluationRequest, EvaluationResponse
from app.services.evaluation_service import evaluate_interview

# Create a router instance for grouping evaluation-related endpoints
router = APIRouter()

@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(request: EvaluationRequest):
    """
    Evaluate the candidate's interview based on:
      - Job description (jd)
      - List of interview questions
      - Candidate's answers
    Returns a structured evaluation score and feedback.
    """
    try:
        # Pass the provided job description, questions, and answers
        # to the evaluation service for processing.
        # The service handles the actual scoring/analysis logic.
        return await evaluate_interview(request.jd, request.questions, request.answers)

    except HTTPException:
        # If the service already raised an HTTPException (e.g., bad request),
        # re-raise it without modification so FastAPI can handle it as-is.
        raise

    except Exception as e:
        # Catch any unexpected errors and return a generic server error
        # so internal details are not leaked to the client.
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}"
        )
