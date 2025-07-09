from fastapi import APIRouter
from ..schemas.request_response import JDRequest, FirstQuestionResponse
from ..services.question_generator import generate_first_question

router = APIRouter()

@router.post("/generate")
async def generate(req: JDRequest):
    question = generate_first_question(req.jd)
    return {
        "questions": [question]  
    }
