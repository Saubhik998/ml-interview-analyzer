from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from pydantic import BaseModel
import json
from ..services import next_question_service, pre_generation_cache

router = APIRouter()

class NextQuestionRequest(BaseModel):
    jd: str
    previous_question: str
    answer: str

class NextQuestionResponse(BaseModel):
    next_question: str

@router.post("/next-question", response_model=NextQuestionResponse)
async def get_next_question(request: NextQuestionRequest, background_tasks: BackgroundTasks):
    """
    Returns the next interview question, and schedules pre-generation for the following question.
    """
    try:
        question = await next_question_service.generate_next_question(
            request.jd, request.previous_question, request.answer
        )

        # Schedule background pre-generation for next question (use current question as previous)
        # We don't yet have the candidate's future answer, so pass empty string as placeholder.
        background_tasks.add_task(
            pre_generation_cache.background_pre_generate,
            request.jd,
            question,
            ""  # No answer available for the following question
        )

        return NextQuestionResponse(next_question=question)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: Could not generate next question."
        )

@router.websocket("/ws/next-question")
async def websocket_next_question(websocket: WebSocket):
    """
    WebSocket endpoint that streams next question or returns cached question instantly.
    Client sends JSON:
    { "jd": "...", "previous_question": "...", "answer": "..." }
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                jd = payload["jd"]
                previous_question = payload["previous_question"]
                answer = payload["answer"]
            except Exception:
                await websocket.send_text("[Error] Invalid payload format.")
                continue

            # Try to obtain cached pre-generated question
            cached = await pre_generation_cache.get_pre_generated_question(jd)
            if cached:
                # send cached question immediately
                await websocket.send_text(cached)
                await websocket.send_text("[END_OF_RESPONSE]")
                # Kick off background pre-generation for the next question
                # use the cached question as 'previous' for the next generation
                asyncio.create_task(pre_generation_cache.background_pre_generate(jd, cached, ""))
                continue

            # No cached question available — stream live generation
            try:
                async for chunk in next_question_service.generate_next_question_stream(jd, previous_question, answer):
                    await websocket.send_text(chunk)
                await websocket.send_text("[END_OF_RESPONSE]")
            except Exception as e:
                await websocket.send_text(f"[Error] {str(e)}")

            # Schedule background pre-generation for next question
            asyncio.create_task(pre_generation_cache.background_pre_generate(jd, previous_question, ""))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(f"[Error] {str(e)}")
        except Exception:
            pass
        await websocket.close(code=1011, reason="Internal Server Error")
