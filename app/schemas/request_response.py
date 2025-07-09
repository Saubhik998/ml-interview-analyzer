from pydantic import BaseModel
from typing import List

class JDRequest(BaseModel):
    jd: str

class FirstQuestionResponse(BaseModel):
    questions: List[str]

class EvaluateRequest(BaseModel):
    transcript: str
    question: str

class EvaluateResponse(BaseModel):
    score: float
    feedback: str
