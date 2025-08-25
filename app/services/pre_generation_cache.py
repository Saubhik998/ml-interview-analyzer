# app/services/pre_generation_cache.py
import asyncio
import logging
from collections import defaultdict
from typing import Optional
from . import next_question_service

logger = logging.getLogger(__name__)

# Simple in-memory cache keyed by session/job description
_pre_generated_questions = defaultdict(list)
_cache_lock = asyncio.Lock()

def _make_session_key(jd: str) -> str:
    """
    For now we key by JD text. In production, use session IDs or conversation IDs.
    """
    return jd.strip()

async def get_pre_generated_question(jd: str) -> Optional[str]:
    """Pop a pre-generated question from cache if available."""
    key = _make_session_key(jd)
    async with _cache_lock:
        if _pre_generated_questions[key]:
            return _pre_generated_questions[key].pop(0)
    return None

async def store_pre_generated_question(jd: str, question: str):
    """Store question in cache."""
    key = _make_session_key(jd)
    async with _cache_lock:
        _pre_generated_questions[key].append(question)

async def background_pre_generate(jd: str, prev_q: str, answer: str):
    """
    Background task to pre-generate the next question and store it.
    """
    try:
        logger.info("Background pre-generation started for JD: %s", jd[:40])
        next_q = await next_question_service.generate_next_question(jd, prev_q, answer)
        if next_q:
            await store_pre_generated_question(jd, next_q)
            logger.info("Background pre-generation complete and stored.")
    except Exception as e:
        logger.exception("Pre-generation failed: %s", e)