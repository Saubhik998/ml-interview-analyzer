from fastapi import FastAPI
from .routers import generate, evaluate, next_question, streaming_chat
from .services.gemini_client import warmup_model

app = FastAPI(
    title="AI Interview API",
    description="Generates questions, evaluates answers, and handles interview logic using Gemini",
    version="1.0.0"
)

app.include_router(generate.router, prefix="/api", tags=["Question Generator"])
app.include_router(evaluate.router, prefix="/api", tags=["Evaluation"])
app.include_router(next_question.router, prefix="/api", tags=["Follow-Up Question"])
# streaming_chat router contains WebSocket endpoints
app.include_router(streaming_chat.router)

@app.on_event("startup")
async def on_startup():
    # Warm up the shared Gemini model to reduce first-request latency
    await warmup_model()

@app.get("/", tags=["Root"])
async def root():
    return {"ok": True}

@app.get("/healthz", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
