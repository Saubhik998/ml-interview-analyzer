from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from ..schemas.request_response import JDRequest, FirstQuestionResponse
from ..services.question_generator import generate_first_question

# Create a FastAPI router instance for question generation
router = APIRouter()

@router.post("/generate", response_model=FirstQuestionResponse)
async def generate(req: JDRequest):
    """
    Generate the first interview question based on the provided job description (JD).
    
    Uses an LLM to analyze the JD and generate a relevant, role-specific question.
    """
    try:
        # Run the blocking question generation function in a separate thread for async compatibility
        question = await run_in_threadpool(generate_first_question, req.jd)
        
        # Return the question inside a standardized response format
        return {
            "questions": [question]
        }
    except Exception:
        # Return a 500 error if the generation fails unexpectedly
        raise HTTPException(status_code=500, detail="Internal Server Error: Question generation failed.")
