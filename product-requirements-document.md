# Product Requirements Document (PRD)

**Title:** Feedback Sentiment Classifier Agent
**Date:** 2026-10-07
**Solution Category:** AI Agent

---

## Product Purpose & Value Proposition

**Elevator Pitch:**
Feedback sits unread or takes 3 minutes to manually classify. This agent returns an accurate sentiment label, a confidence score, and a plain-language reasoning in under 1 second — enabling teams to act on feedback at scale.

**Business Need:**
Manual or rule-based feedback classification is too slow (3 minutes per item) and does not provide structured, traceable outputs. Teams cannot act on feedback at the speed customers generate it.

**Expected Value:**
- Classification time reduced from 3 minutes to ≤ 1 second per item.
- Structured, grounded output (label + confidence + reasoning) replaces subjective manual assessment.
- ≥ 90% classification accuracy enables reliable downstream decisions.

**Product Objectives (Prioritized):**
1. Deliver accurate sentiment classification (positive / negative / neutral) at ≥ 90% accuracy.
2. Return a confidence score (0–1) and a brief reasoning for every classification.
3. Respond in ≤ 1 second end-to-end.
4. Never fabricate results — all outputs must be grounded in the input text.

---

## Business Metrics

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Classification accuracy | — | ≥ 90% | — | Feedback Sentiment Classification | user |
| Response time per classification | 3 minutes | ≤ 1 second | — | Feedback Sentiment Classification | user |

---

## Requirements

### Must-Have Requirements

**R1**: Sentiment Classification

- **Problem to Solve**: Users need to know whether a piece of feedback is positive, negative, or neutral without reading and judging it manually.
- **User Story**: As a CX analyst, I need the agent to classify any feedback text so that I can process large volumes quickly and consistently.
- **Acceptance Criteria**:
  - Given a feedback text input, when the agent is called, then it returns exactly one of: `positive`, `negative`, `neutral`.
  - The label is derived only from the input text — no external data is fabricated.
- **Maps to Objective**: 1, 4
- **Priority Rank**: 1

**R2**: Confidence Score

- **Problem to Solve**: A bare label gives no indication of how certain the classification is, making it hard to prioritise review effort.
- **User Story**: As a CX analyst, I need a confidence score alongside every label so that I can decide which items need human review.
- **Acceptance Criteria**:
  - Given a classification response, then a `confidence` field (float, 0.0–1.0) is always present.
- **Maps to Objective**: 2
- **Priority Rank**: 2

**R3**: Reasoning

- **Problem to Solve**: Without an explanation, analysts cannot verify or audit a classification decision.
- **User Story**: As a CX analyst, I need a short reasoning statement so that I can understand and validate the classification.
- **Acceptance Criteria**:
  - Given a classification response, then a `reasoning` field (1–2 sentences) is always present.
  - The reasoning references content from the input text; it does not introduce external claims.
- **Maps to Objective**: 2, 4
- **Priority Rank**: 3

**R4**: Latency ≤ 1 Second

- **Problem to Solve**: The current 3-minute classification time blocks real-time and batch feedback workflows.
- **User Story**: As a CX analyst, I need each classification to complete within 1 second so that feedback can be processed in near real-time.
- **Acceptance Criteria**:
  - Given a standard feedback input (up to 500 words), when the agent processes it, then the end-to-end response is returned in ≤ 1 second under normal load.
- **Maps to Objective**: 3
- **Priority Rank**: 4

**R5**: Accuracy ≥ 90% (No Fabrication)

- **Problem to Solve**: Inaccurate or hallucinated classifications erode trust and produce wrong business decisions.
- **User Story**: As a CX analyst, I need the agent to be correct at least 90% of the time and never invent information so that I can rely on its output.
- **Acceptance Criteria**:
  - An evaluation harness validates ≥ 90% accuracy on a representative labelled test set before deployment.
  - Structured output mode constrains the model to the fixed label set, preventing label hallucination.
- **Maps to Objective**: 1, 4
- **Priority Rank**: 5

---

## Solution Architecture

**Architecture Overview:**
A Python A2A agent hosted on SAP BTP Cloud Foundry. The agent receives a feedback text, constructs a single structured prompt, calls an LLM via SAP AI Core (Generative AI Hub), and returns a JSON response. No multi-step reasoning loop is needed — a single pass satisfies both the latency and accuracy requirements.

**Key Components:**
- **Python A2A Agent**: Accepts requests (A2A protocol), runs the classification prompt, returns structured JSON.
- **SAP AI Core / Generative AI Hub**: Provides LLM inference with structured output mode to enforce the fixed label schema.
- **Evaluation Harness**: Offline test suite validating accuracy ≥ 90% before each release.

**Integration Points:**
- Callers interact with the agent via the A2A protocol endpoint.
- The agent calls SAP AI Core inference endpoint (outbound, synchronous).

### Agent Extensibility & Instrumentation

**Agent Extensibility:**
- The agent exposes a single classification skill today; additional skills (e.g., topic tagging, urgency scoring) can be added as new tools without changing the core agent loop.
- The system prompt and label set are configurable via environment variables to support domain-specific tuning.

**Business Step Instrumentation:**
- Each milestone below maps to a structured log statement emitted at runtime.
- Log pattern: `[MILESTONE_ID].[achieved|missed]: [description]`
- Instrumentation enables production monitoring, SLA alerting, and debugging of agent behaviour.

### Automation & Agent Behaviour

**Automation Level:** Autonomous agent (single-pass, no human approval required per classification)

**Actions the system performs without human approval:**
- Classifying feedback text and returning label, confidence, and reasoning.

**Actions that require human review or approval:**
- None for routine classifications. Items with confidence < 0.6 should be flagged for optional human review by the calling system.

**Model or engine used:** Fast LLM (e.g., GPT-4o-mini or equivalent) via SAP Generative AI Hub, with structured output / JSON mode enabled.

**Knowledge & data sources accessed:**
- Input feedback text only. No external knowledge base or retrieval step.

**Guardrails & fail-safes:**
- Structured output mode constrains the model to the allowed label set (`positive`, `negative`, `neutral`) — prevents label fabrication.
- Reasoning field must reference the input text; the prompt explicitly forbids introducing external claims.
- If the LLM call fails or times out, the agent returns a structured error (no silent failure).
- Confidence < 0.6 is surfaced to callers as a low-confidence signal.

---

## Milestones

### M1: Agent Bootstrapped

- **Description**: Python A2A agent project is created, dependencies installed, and the server starts locally.
- **Achieved when**: The agent process starts and responds to a health-check request.
- **Log on achievement**: `M1.achieved: agent bootstrapped and health-check passed`
- **Log on miss**: `M1.missed: agent failed to start or health-check unresponsive`

### M2: Sentiment Classification Working

- **Description**: The agent classifies a feedback input and returns a valid JSON response with `sentiment`, `confidence`, and `reasoning`.
- **Achieved when**: A test input returns a correctly structured JSON response with all three fields populated.
- **Log on achievement**: `M2.achieved: classification returned valid structured response`
- **Log on miss**: `M2.missed: classification response missing required fields or malformed`

### M3: Accuracy Gate Passed

- **Description**: Evaluation harness confirms ≥ 90% accuracy on the labelled test set with no fabricated labels.
- **Achieved when**: Eval run reports accuracy ≥ 0.90 and all responses use only allowed label values.
- **Log on achievement**: `M3.achieved: accuracy eval passed — score above 90% threshold`
- **Log on miss**: `M3.missed: accuracy eval failed — score below 90% threshold`

### M4: Latency Gate Passed

- **Description**: End-to-end response time is verified to be ≤ 1 second under normal load.
- **Achieved when**: Latency test confirms p95 response time ≤ 1000 ms for inputs up to 500 words.
- **Log on achievement**: `M4.achieved: latency gate passed — p95 within 1-second target`
- **Log on miss**: `M4.missed: latency gate failed — p95 exceeds 1-second target`

### M5: Agent Deployed

- **Description**: Agent is live on SAP BTP and accessible via the A2A protocol endpoint.
- **Achieved when**: Deployment succeeds and a live classification request returns a valid response from the production endpoint.
- **Log on achievement**: `M5.achieved: agent deployed and live endpoint validated`
- **Log on miss**: `M5.missed: deployment failed or live endpoint unreachable`
