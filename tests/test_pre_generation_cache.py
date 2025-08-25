import pytest
from unittest.mock import AsyncMock, patch
from app.services import pre_generation_cache

async def clear_cache():
    async with pre_generation_cache._cache_lock:
        pre_generation_cache._pre_generated_questions.clear()

@pytest.mark.asyncio
async def test_make_session_key_trims_spaces():
    key = pre_generation_cache._make_session_key("   My JD   ")
    assert key == "My JD"

@pytest.mark.asyncio
async def test_store_and_get_pre_generated_question():
    await clear_cache()

    jd = "Test JD"
    question = "What is your experience?"

    await pre_generation_cache.store_pre_generated_question(jd, question)
    result = await pre_generation_cache.get_pre_generated_question(jd)
    assert result == question

    # After popping, it should be empty
    result2 = await pre_generation_cache.get_pre_generated_question(jd)
    assert result2 is None

@pytest.mark.asyncio
async def test_get_pre_generated_question_no_entry():
    await clear_cache()

    jd = "Non-existing JD"
    result = await pre_generation_cache.get_pre_generated_question(jd)
    assert result is None

@pytest.mark.asyncio
async def test_background_pre_generate_success(monkeypatch):
    await clear_cache()

    jd = "JD text"
    prev_q = "Prev question"
    answer = "Answer"

    fake_question = "Generated next question?"
    mock_generate = AsyncMock(return_value=fake_question)
    monkeypatch.setattr(pre_generation_cache.next_question_service, "generate_next_question", mock_generate)

    await pre_generation_cache.background_pre_generate(jd, prev_q, answer)

    stored = await pre_generation_cache.get_pre_generated_question(jd)
    assert stored == fake_question
    mock_generate.assert_awaited_once_with(jd, prev_q, answer)

@pytest.mark.asyncio
async def test_background_pre_generate_failure(monkeypatch):
    await clear_cache()

    jd = "JD text"
    prev_q = "Prev question"
    answer = "Answer"

    mock_generate = AsyncMock(side_effect=Exception("Boom"))
    monkeypatch.setattr(pre_generation_cache.next_question_service, "generate_next_question", mock_generate)

    with patch.object(pre_generation_cache.logger, "exception") as mock_log:
        await pre_generation_cache.background_pre_generate(jd, prev_q, answer)
        mock_log.assert_called_once()
