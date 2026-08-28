# Phase 9 Validation & Acceptance Criteria

## Acceptance Criteria

### 1. Intent Classification Accuracy
- Inputs like `"hi"`, `"hello"`, `"hey"` must be classified as `GREETING`.
- Inputs like `"what is this?"`, `"how do I use CounterPoint?"`, `"help"` must be classified as `GENERAL_QA`.
- Inputs like `"what is the distance to the moon?"`, `"tell me a joke"` must be classified as `OFF_TOPIC`.
- Inputs like `"compare Notion vs ClickUp"`, `"HubSpot pricing"`, `"Salesforce enterprise features"` must be classified as `COMPETITOR_RESEARCH`.

### 2. Zero Unnecessary Search Executions
- Queries classified as `GREETING`, `GENERAL_QA`, or `OFF_TOPIC` must bypass the `WebSearchService.search_competitor` execution node, recording 0 web search calls in audit logs.

### 3. Adaptive Response Formatting
- `GREETING` inputs must return a concise, helpful conversational greeting introducing CounterPoint's purpose, without 4-section Markdown headers or tabular pricing layouts.
- `GENERAL_QA` inputs must provide direct guidance on uploading positioning documents and asking competitor research queries.
- `OFF_TOPIC` inputs must politely clarify CounterPoint's focus on competitive software research.
- `COMPETITOR_RESEARCH` inputs must present strategic matrices with structured tables, but only containing verified data.

### 4. Zero Hallucination Guarantee
- Neither Groq LLM outputs nor rule-based fallback outputs may present hardcoded fake pricing numbers (`$5-$15/mo`) or synthetic competitor metrics when actual research data is missing.
- When pricing data is not present in live web search snippets or document excerpts, the output must explicitly state: *"No verified external pricing data found in sources"*.

### 5. Automated Verification
- Run `python manage.py test api` -> All Django API tests pass cleanly with 100% success rate.
- Run `npx vitest run` in `frontend/` -> All Vitest UI component tests pass cleanly.
