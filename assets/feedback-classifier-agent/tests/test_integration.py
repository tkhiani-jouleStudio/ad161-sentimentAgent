"""Integration test: end-to-end agent flow with mocked LLM."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage


@pytest.mark.usefixtures("add_agent_to_path")
@pytest.mark.asyncio
async def test_agent_invoke_returns_classification_response():
    """Full agent invoke with mocked LLM returns a valid completed response."""
    from agent import SampleAgent

    mock_graph = MagicMock()
    mock_graph.ainvoke = AsyncMock(
        return_value={
            "messages": [
                AIMessage(
                    content='**Sentiment:** positive\n**Confidence:** 0.95\n**Reasoning:** The feedback expresses satisfaction with delivery speed and product quality.'
                )
            ]
        }
    )

    agent = SampleAgent()
    with patch.object(agent, "_create_graph", return_value=mock_graph):
        response = await agent.invoke(
            query="Classify this feedback: The package arrived early and the product exceeded my expectations!",
            context_id="test-context-001",
            tools=[],
        )

    assert response.status == "completed"
    assert response.message is not None
    assert len(response.message) > 0


@pytest.mark.usefixtures("add_agent_to_path")
@pytest.mark.asyncio
async def test_agent_stream_yields_completion():
    """Agent stream yields a final is_task_complete=True chunk."""
    from agent import SampleAgent

    mock_graph = MagicMock()
    mock_graph.ainvoke = AsyncMock(
        return_value={
            "messages": [
                AIMessage(content="Sentiment: negative | Confidence: 0.88 | Reasoning: References poor service.")
            ]
        }
    )

    agent = SampleAgent()
    chunks = []
    with patch.object(agent, "_create_graph", return_value=mock_graph):
        async for chunk in agent.stream(
            query="Rate this: The support team was unhelpful and rude.",
            context_id="test-context-002",
            tools=[],
        ):
            chunks.append(chunk)

    assert any(c["is_task_complete"] for c in chunks), (
        "At least one chunk must have is_task_complete=True"
    )
    final = next(c for c in chunks if c["is_task_complete"])
    assert "content" in final
    assert len(final["content"]) > 0
