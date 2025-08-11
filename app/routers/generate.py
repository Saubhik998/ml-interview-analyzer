from fastapi import APIRouter, HTTPException
from ..schemas.request_response import JDRequest, FirstQuestionResponse
from ..services.question_generator import generate_first_question

router = APIRouter()

@router.post("/generate", response_model=FirstQuestionResponse)
async def generate(req: JDRequest):
    """
    Generate the first interview question based on the provided job description (JD).
    """
    try:
        question = await generate_first_question(req.jd)
        return {"questions": [question]}
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error: Question generation failed.")
