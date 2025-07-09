from fastapi import APIRouter
from app.schemas.evaluation_schema import EvaluationRequest, EvaluationResponse
from app.services.evaluation_service import evaluate_interview

router = APIRouter()

@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate(request: EvaluationRequest):
    return evaluate_interview(request.jd, request.questions, request.answers)
