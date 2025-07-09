from fastapi import APIRouter
from pydantic import BaseModel
from ..services import next_question_service

router = APIRouter()

class NextQuestionRequest(BaseModel):
    jd: str
    previous_question: str
    answer: str

class NextQuestionResponse(BaseModel):
    next_question: str

@router.post("/next-question", response_model=NextQuestionResponse)
def get_next_question(request: NextQuestionRequest):
    question = next_question_service.generate_next_question(
        jd=request.jd,
        previous_question=request.previous_question,
        answer=request.answer
    )
    return NextQuestionResponse(next_question=question)
    