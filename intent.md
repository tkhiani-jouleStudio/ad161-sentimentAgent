# Feedback Sentiment Classifier Agent

AI agent that classifies feedback into positive, negative, or neutral sentiment with a confidence score and reasoning.

## Business challenge

Feedback classification currently takes 3 minutes per item and lacks structured output (sentiment label, confidence score, reasoning). A new AI agent must deliver accurate, grounded classifications (≥90% accuracy, no fabricated results) in under 1 second.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Classification accuracy | — | ≥ 90% | — | Feedback Sentiment Classification | user |
| Response time per classification | 3 minutes | ≤ 1 second | — | Feedback Sentiment Classification | user |

## Key Milestones

1. **Agent bootstrapped** — Python A2A agent project structure created and runnable locally.
2. **Sentiment classification working** — agent returns label (positive / negative / neutral), confidence score, and reasoning for a given feedback input.
3. **Accuracy gate passed** — evaluation confirms ≥ 90% accuracy on a representative test set with no hallucinated labels.
4. **Latency gate passed** — end-to-end response time verified ≤ 1 second under normal load.
5. **Agent deployed** — agent live on SAP BTP and accessible via A2A protocol.

## Business Architecture (RBA)

### End-to-End Process

Lead to Cash Standard B2B

### Process Hierarchy

```
Lead to Cash Standard B2B (E2E)
└── Market to Lead
    └── Customer Insight to Lead Development (BPS-368_015)
        └── Analyze and respond to customer insight
```

### Summary

Sentiment classification of customer feedback maps to the "Customer Insight to Lead Development" sub-process within the Market to Lead phase of Lead to Cash, enabling data-driven understanding of customer perception.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Gap? | Notes |
|------------------------|------------------------|------------|-------------------|--------------------|------|-------|
| Classify feedback as positive / negative / neutral | SAP AI Core – NLP APIs (Natural Language Processing, Text Classification) | — | — | — | Yes | No pre-built MCP server; custom agent with LLM call required |
| Return confidence score per classification | No standard asset | — | — | — | Yes | Custom agent logic needed |
| Return human-readable reasoning per classification | No standard asset | — | — | — | Yes | LLM-generated chain-of-thought, grounded (no fabrication) |
| Response time ≤ 1 second | SAP AI Core (LLM inference) | — | — | — | Maybe | Achievable with a fast model and a single-pass prompt; needs validation |
| Accuracy ≥ 90%, no fabricated results | No standard asset | — | — | — | Yes | Requires prompt engineering, structured output, and evaluation harness |

### Key findings

- No standard SAP product provides a ready-made sentiment classifier with confidence scores and reasoning out of the box.
- SAP AI Core provides the LLM inference runtime; the agent wraps it with a structured prompt.
- A single-pass LLM call with structured output (JSON) is the right architecture to hit the ≤ 1 second latency target.
- Accuracy ≥ 90% is achievable with a well-engineered prompt and a capable base model; an evaluation harness must validate this.
- No MCP servers were found for any of the discovered APIs; all integration is via direct LLM prompting within the agent.
- Grounding (no fabrication) is enforced by constraining the model to output only from a fixed label set and requiring a reasoning field.

## Recommendations

### Feedback Sentiment Classifier – Pro-code Python Agent

#### Executive Summary

Custom Python A2A agent on SAP BTP using LLM for fast, accurate sentiment classification.

#### Recommended Solution

Build a pro-code Python agent (A2A protocol) hosted on SAP BTP. The agent accepts a feedback text as input, constructs a structured prompt, calls an LLM via SAP AI Core in a single pass, and returns a JSON response containing `sentiment` (positive | negative | neutral), `confidence` (0–1 float), and `reasoning` (1–2 sentence explanation). Structured output mode constrains the model to the fixed label set, preventing fabrication.

#### Recommended solution category

AI Agent

#### Intent fit

95%
