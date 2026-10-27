"""Unit test: positive sentiment classification."""
import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_litellm import ChatLiteLLM


@pytest.mark.usefixtures("add_agent_to_path")
@pytest.mark.asyncio
async def test_classify_positive_feedback():
    """classify_sentiment tool returns 'positive' for clearly positive feedback."""
    from agent import SentimentResult, _build_classifier_tool

    mock_llm = MagicMock(spec=ChatLiteLLM)
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(
        return_value=SentimentResult(
            sentiment="positive",
            confidence=0.95,
            reasoning="The review praises the product quality and fast delivery.",
        )
    )
    mock_llm.with_structured_output = MagicMock(return_value=mock_structured)

    classifier_tool = _build_classifier_tool(mock_llm)
    result_json = await classifier_tool.ainvoke(
        {"feedback_text": "Absolutely love this product! Fast delivery and great quality."}
    )
    result = json.loads(result_json)

    assert result["sentiment"] == "positive"
    assert isinstance(result["confidence"], float)
    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["reasoning"], str)
    assert len(result["reasoning"]) > 0
