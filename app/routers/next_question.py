from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from pydantic import BaseModel
import json
import asyncio
from ..services import next_question_service, pre_generation_cache

# Create router instance for question progression endpoints
router = APIRouter()

# ------------------------------
# Request & Response Models
# ------------------------------

class NextQuestionRequest(BaseModel):
    jd: str                   # Job description
    previous_question: str    # The last question asked
    answer: str               # Candidate's answer to the previous question

class NextQuestionResponse(BaseModel):
    next_question: str        # The next question to ask

# ------------------------------
# REST Endpoint: Get Next Question
# ------------------------------

@router.post("/next-question", response_model=NextQuestionResponse)
async def get_next_question(request: NextQuestionRequest, background_tasks: BackgroundTasks):
    """
    REST endpoint:
    - Generates the next interview question based on the JD, previous question, and answer.
    - Schedules a background task to pre-generate the *following* question 
      so it can be served instantly later.
    """
    try:
        # Generate the next interview question using the service layer.
        question = await next_question_service.generate_next_question(
            request.jd, request.previous_question, request.answer
        )

        # Background pre-generation:
        # We use the *current* question as 'previous' and leave the answer empty,
        # because the candidate hasn't answered it yet.
        background_tasks.add_task(
            pre_generation_cache.background_pre_generate,
            request.jd,
            question,
            ""  # Placeholder for answer
        )

        # Return the generated next question to the client.
        return NextQuestionResponse(next_question=question)

    except Exception:
        # Catch any error and return a generic 500 without leaking details.
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: Could not generate next question."
        )

# ------------------------------
# WebSocket Endpoint: Stream Next Question
# ------------------------------

@router.websocket("/ws/next-question")
async def websocket_next_question(websocket: WebSocket):
    """
    WebSocket endpoint for streaming the next interview question.

    Client sends JSON payload:
    {
      "jd": "...", 
      "previous_question": "...", 
      "answer": "..."
    }

    Server behavior:
    - If a cached pre-generated question is available, send it instantly.
    - Otherwise, stream a live generated question chunk-by-chunk.
    - After sending, schedule background pre-generation for the following question.
    """
    await websocket.accept()
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                jd = payload["jd"]
                previous_question = payload["previous_question"]
                answer = payload["answer"]
            except Exception:
                # Invalid payload format
                await websocket.send_text("[Error] Invalid payload format.")
                continue

            # 1️⃣ Try to serve a cached question first
            cached = await pre_generation_cache.get_pre_generated_question(jd)
            if cached:
                await websocket.send_text(cached)
                await websocket.send_text("[END_OF_RESPONSE]")

                # Pre-generate the *next* question in the background
                asyncio.create_task(
                    pre_generation_cache.background_pre_generate(jd, cached, "")
                )
                continue

            # 2️⃣ No cache — generate question live and stream it
            try:
                async for chunk in next_question_service.generate_next_question_stream(
                    jd, previous_question, answer
                ):
                    await websocket.send_text(chunk)
                await websocket.send_text("[END_OF_RESPONSE]")
            except Exception as e:
                await websocket.send_text(f"[Error] {str(e)}")

            # 3️⃣ Schedule background pre-generation for the *following* question
            asyncio.create_task(
                pre_generation_cache.background_pre_generate(jd, previous_question, "")
            )

    except WebSocketDisconnect:
        # Client disconnected — just exit the loop quietly
        pass
    except Exception as e:
        # Any unexpected error during connection handling
        try:
            await websocket.send_text(f"[Error] {str(e)}")
        except Exception:
            pass
        await websocket.close(code=1011, reason="Internal Server Error")
