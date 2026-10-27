"""Unit test: structured output schema enforcement."""
import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_litellm import ChatLiteLLM


@pytest.mark.usefixtures("add_agent_to_path")
@pytest.mark.asyncio
async def test_response_has_all_required_fields():
    """classify_sentiment always returns sentiment, confidence, and reasoning."""
    from agent import SentimentResult, _build_classifier_tool

    mock_llm = MagicMock(spec=ChatLiteLLM)
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(
        return_value=SentimentResult(
            sentiment="positive",
            confidence=0.85,
            reasoning="The feedback is enthusiastic about the product.",
        )
    )
    mock_llm.with_structured_output = MagicMock(return_value=mock_structured)

    classifier_tool = _build_classifier_tool(mock_llm)
    result_json = await classifier_tool.ainvoke({"feedback_text": "Great product!"})
    result = json.loads(result_json)

    assert "sentiment" in result, "Response must include 'sentiment' field"
    assert "confidence" in result, "Response must include 'confidence' field"
    assert "reasoning" in result, "Response must include 'reasoning' field"
    assert result["sentiment"] in ("positive", "negative", "neutral"), (
        "sentiment must be one of: positive, negative, neutral"
    )
    assert isinstance(result["confidence"], float), "confidence must be a float"
    assert 0.0 <= result["confidence"] <= 1.0, "confidence must be between 0.0 and 1.0"
    assert isinstance(result["reasoning"], str), "reasoning must be a string"


@pytest.mark.usefixtures("add_agent_to_path")
def test_sentiment_result_rejects_invalid_label():
    """SentimentResult raises validation error for invalid sentiment label."""
    from agent import SentimentResult
    import pydantic

    with pytest.raises((pydantic.ValidationError, ValueError)):
        SentimentResult(sentiment="unknown", confidence=0.5, reasoning="test")


@pytest.mark.usefixtures("add_agent_to_path")
def test_sentiment_result_rejects_out_of_range_confidence():
    """SentimentResult raises validation error when confidence is out of range."""
    from agent import SentimentResult
    import pydantic

    with pytest.raises((pydantic.ValidationError, ValueError)):
        SentimentResult(sentiment="positive", confidence=1.5, reasoning="test")
