"""Unit test: no-fabrication guardrail in system prompt."""

import pytest


@pytest.mark.usefixtures("add_agent_to_path")
def test_system_prompt_contains_no_fabrication_guardrail():
    """System prompt must explicitly instruct against fabrication."""
    from agent import get_system_prompt

    prompt = get_system_prompt()

    assert "fabricate" in prompt.lower() or "invent" in prompt.lower(), (
        "System prompt must contain anti-fabrication instruction"
    )


@pytest.mark.usefixtures("add_agent_to_path")
def test_system_prompt_references_input_text():
    """System prompt must instruct the agent to base reasoning on input text."""
    from agent import get_system_prompt

    prompt = get_system_prompt()

    assert "input text" in prompt.lower() or "input" in prompt.lower(), (
        "System prompt must reference grounding in the input text"
    )


@pytest.mark.usefixtures("add_agent_to_path")
def test_system_prompt_defines_allowed_labels():
    """System prompt must mention the allowed sentiment labels."""
    from agent import get_system_prompt

    prompt = get_system_prompt()

    for label in ("positive", "negative", "neutral"):
        assert label in prompt.lower(), (
            f"System prompt must reference allowed label '{label}'"
        )
