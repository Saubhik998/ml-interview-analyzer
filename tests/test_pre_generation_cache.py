import pytest
from unittest.mock import AsyncMock, patch
from app.services import pre_generation_cache


@pytest.mark.asyncio
async def test_make_session_key_trims_spaces():
    key = pre_generation_cache._make_session_key("   My JD   ")
    assert key == "My JD"


@pytest.mark.asyncio
async def test_store_and_get_pre_generated_question():
    jd = "Test JD"
    question = "What is your experience?"
    
    # Ensure cache is empty
    await pre_generation_cache.store_pre_generated_question(jd, question)
    result = await pre_generation_cache.get_pre_generated_question(jd)
    assert result == question

    # After popping, it should be empty
    result2 = await pre_generation_cache.get_pre_generated_question(jd)
    assert result2 is None


@pytest.mark.asyncio
async def test_get_pre_generated_question_no_entry():
    jd = "Non-existing JD"
    result = await pre_generation_cache.get_pre_generated_question(jd)
    assert result is None


@pytest.mark.asyncio
async def test_background_pre_generate_success(monkeypatch):
    jd = "JD text"
    prev_q = "Prev question"
    answer = "Answer"

    fake_question = "Generated next question?"
    mock_generate = AsyncMock(return_value=fake_question)
    monkeypatch.setattr(pre_generation_cache.next_question_service, "generate_next_question", mock_generate)

    # Clear cache before
    pre_generation_cache._pre_generated_questions.clear()

    await pre_generation_cache.background_pre_generate(jd, prev_q, answer)

    # The generated question should be stored
    stored = await pre_generation_cache.get_pre_generated_question(jd)
    assert stored == fake_question
    mock_generate.assert_awaited_once_with(jd, prev_q, answer)


@pytest.mark.asyncio
async def test_background_pre_generate_failure(monkeypatch):
    jd = "JD text"
    prev_q = "Prev question"
    answer = "Answer"

    # Force generate_next_question to raise
    mock_generate = AsyncMock(side_effect=Exception("Boom"))
    monkeypatch.setattr(pre_generation_cache.next_question_service, "generate_next_question", mock_generate)

    with patch.object(pre_generation_cache.logger, "exception") as mock_log:
        await pre_generation_cache.background_pre_generate(jd, prev_q, answer)
        mock_log.assert_called_once()
