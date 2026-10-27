"""Unit test: negative sentiment classification."""
import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_litellm import ChatLiteLLM


@pytest.mark.usefixtures("add_agent_to_path")
@pytest.mark.asyncio
async def test_classify_negative_feedback():
    """classify_sentiment tool returns 'negative' for clearly negative feedback."""
    from agent import SentimentResult, _build_classifier_tool

    mock_llm = MagicMock(spec=ChatLiteLLM)
    mock_structured = MagicMock()
    mock_structured.ainvoke = AsyncMock(
        return_value=SentimentResult(
            sentiment="negative",
            confidence=0.91,
            reasoning="The review mentions late delivery and damaged packaging.",
        )
    )
    mock_llm.with_structured_output = MagicMock(return_value=mock_structured)

    classifier_tool = _build_classifier_tool(mock_llm)
    result_json = await classifier_tool.ainvoke(
        {"feedback_text": "Delivery was very late and packaging was completely damaged."}
    )
    result = json.loads(result_json)

    assert result["sentiment"] == "negative"
    assert isinstance(result["confidence"], float)
    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["reasoning"], str)
    assert len(result["reasoning"]) > 0
