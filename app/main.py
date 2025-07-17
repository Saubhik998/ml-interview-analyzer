from fastapi import FastAPI
from .routers import generate, evaluate, next_question  # your routers

app = FastAPI(
    title="AI Interview API",
    description="Generates questions, evaluates answers, and handles interview logic using Gemini",
    version="1.0.0"
)

# Include routers
app.include_router(generate.router, prefix="/api", tags=["Question Generator"])
app.include_router(evaluate.router, prefix="/api", tags=["Evaluation"])
app.include_router(next_question.router, prefix="/api", tags=["Follow-Up Question"])

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {"ok": True}

# Health check endpoint 
@app.get("/healthz", tags=["Health"], summary="Health Check", description="Simple health check endpoint.")
async def health_check():
    return {"status": "healthy"}
