# Specification: feedback-classifier-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read `product-requirements-document.md` and `intent.md` at the project root for full context.
- [x] Bootstrap agent code in `assets/feedback-classifier-agent/` using instructions from the sap-agent-bootstrap section. (invoke from inside `assets/feedback-classifier-agent/`, use copy commands — do NOT create files manually)
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

No runtime skill is needed — the classification logic is a single-pass LLM call with no branching workflow or external reference material. All instructions fit in the system prompt.

---

## Project-Specific Tasks

### System Prompt

- [x] Open `assets/feedback-classifier-agent/app/agent.py` and write a `get_system_prompt()` function (or equivalent `@prompt_section`) with the following instructions:
  - You are a feedback sentiment classifier. Given a feedback text, classify it as exactly one of: `positive`, `negative`, `neutral`.
  - Return a JSON object with three fields: `sentiment` (string: "positive" | "negative" | "neutral"), `confidence` (float 0.0–1.0), `reasoning` (string, 1–2 sentences referencing content from the input text).
  - IMPORTANT: Base the classification strictly on the input text. Do NOT fabricate, invent, or introduce information not present in the input.
  - If confidence is below 0.6, still return the best classification but set `confidence` accordingly — do NOT refuse to classify.
  - Never return a label outside the allowed set. Never omit any of the three fields.

### Classification Tool / Agent Input

- [x] The agent accepts a single input: `feedback_text` (string) — the raw feedback to be classified.
- [x] Implement a `classify_feedback` function (or tool) that:
  1. Takes `feedback_text` as input.
  2. Constructs the LLM prompt using the system prompt above and the user's `feedback_text`.
  3. Calls the LLM via SAP AI Core (LiteLLM) using **structured output / JSON mode** to enforce the fixed response schema.
  4. Returns the parsed JSON response: `{ sentiment, confidence, reasoning }`.
- [x] Enable structured output mode (JSON mode) on the LLM call to prevent label hallucination. The model must be constrained to return only the defined JSON schema.

### Response Schema Enforcement

- [x] Define a Pydantic model (or equivalent) for the structured output:
  ```
  class SentimentResult(BaseModel):
      sentiment: Literal["positive", "negative", "neutral"]
      confidence: float  # 0.0 – 1.0
      reasoning: str
  ```
- [x] Wire the Pydantic model into the LLM call as the `response_format` / `with_structured_output` parameter so the model is forced to conform to the schema.

### Performance (Latency ≤ 1 second)

- [x] Use a fast LLM model (e.g. `gpt-4o-mini` or equivalent via SAP AI Core Generative AI Hub) — single-pass, no multi-step reasoning loop.
- [x] Do NOT add retrieval steps, vector store lookups, or multi-agent sub-calls — all classification happens in one LLM call.

### No-Fabrication Guardrail

- [x] The system prompt must explicitly state: "Base your classification strictly on the input text. Do NOT fabricate or introduce information not present in the input."
- [x] The `reasoning` field must reference actual phrases or themes from the input text — enforce this in the system prompt instructions.

---

## Business Instrumentation

- [x] Implement business step instrumentation for each milestone defined in `product-requirements-document.md`:
  - **M1** — Agent bootstrapped: `M1.achieved: agent bootstrapped and health-check passed` / `M1.missed: agent failed to start or health-check unresponsive`
  - **M2** — Classification working: `M2.achieved: classification returned valid structured response` / `M2.missed: classification response missing required fields or malformed`
  - **M3** — Accuracy gate passed: `M3.achieved: accuracy eval passed — score above 90% threshold` / `M3.missed: accuracy eval failed — score below 90% threshold`
  - **M4** — Latency gate passed: `M4.achieved: latency gate passed — p95 within 1-second target` / `M4.missed: latency gate failed — p95 exceeds 1-second target`
  - **M5** — Agent deployed: `M5.achieved: agent deployed and live endpoint validated` / `M5.missed: deployment failed or live endpoint unreachable`
- [x] Use pattern `[MILESTONE_ID].[achieved|missed]: [description]` for all log statements.
- [x] Add OpenTelemetry spans for each business step using the **decorator or context-manager** form on plain async methods (NOT inside `stream()` async generators).
- [x] Extract classification logic into a plain async helper (e.g. `_run_classification()`) and instrument that method; call it from `stream()` and yield results outside any span context.
- [x] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`.

---

## MCP Tool Integration

No external SAP API integrations are required — the agent calls SAP AI Core directly via LiteLLM. Skip all MCP server creation and wiring tasks. Do NOT add any `requires` entries to `asset.yaml`.

No `mcp-mock.json` generation is needed (no MCP tools to mock).

---

## Testing

- [x] `conftest.py` only sets `IBD_TESTING=true`.
- [x] Mock all LLM calls (ChatLiteLLM / AI Core) — tests must run fully offline with no real AI Core credentials.
- [x] Write unit tests in `assets/feedback-classifier-agent/tests/`:
  - `test_classify_positive.py` — input with clearly positive feedback → asserts `sentiment == "positive"`, `confidence` is a float, `reasoning` is non-empty string.
  - `test_classify_negative.py` — input with clearly negative feedback → asserts `sentiment == "negative"`.
  - `test_classify_neutral.py` — input with neutral feedback → asserts `sentiment == "neutral"`.
  - `test_schema_enforcement.py` — asserts that the LLM response is always parsed into `SentimentResult` with all three fields present and valid types.
  - `test_no_fabrication.py` — asserts that the system prompt contains the no-fabrication guardrail instruction.
- [x] Write one integration test `test_integration.py` exercising the full agent flow: mock LLM returns a valid JSON sentiment response → agent returns structured `{ sentiment, confidence, reasoning }`.
- [x] Run `pytest` from `assets/feedback-classifier-agent/` (no args). Fix any failures immediately.
- [x] If coverage < 70%, add targeted tests until threshold is met.
- [x] Run `pytest` again (no args) to generate final `test_report.json`.
- [x] Verify `test_report.json` exists in `assets/feedback-classifier-agent/`.
