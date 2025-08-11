from fastapi import APIRouter, HTTPException
from app.schemas.evaluation_schema import EvaluationRequest, EvaluationResponse
from app.services.evaluation_service import evaluate_interview

router = APIRouter()

@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(request: EvaluationRequest):
    """
    Evaluate the candidate's interview based on job description, questions, and answers.
    """
    try:
        return await evaluate_interview(request.jd, request.questions, request.answers)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
