from fastapi import FastAPI
from .routers import generate, evaluate, next_question  # new router added

app = FastAPI()

# Route for generating initial questions from JD
app.include_router(generate.router, prefix="/api")

# Route for evaluating the final report
app.include_router(evaluate.router, prefix="/api")

# Route for generating the next question based on the user's last answer
app.include_router(next_question.router, prefix="/api")

@app.get("/")
async def root():
    return {"ok": True}
