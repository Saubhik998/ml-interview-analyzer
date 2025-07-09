from pydantic import BaseModel
from typing import List

class EvaluationRequest(BaseModel):
    jd: str
    questions: List[str]
    answers: List[str]

class EvaluationResponse(BaseModel):
    jd: str
    score: int
    questions: List[str]
    answers: List[str]
    strengths: List[str]
    improvements: List[str]
    followUps: List[str]
