# Phase 9 Implementation Plan: Dynamic Intent Classification & Zero-Hallucination Agent Guardrails

## Task Group 1: Query Intent Classifier & Intent State Schema
- Task 1.1: Expand `AgentMemoryState` in `backend/api/services/langgraph_memory_engine.py` to include `intent: str` field (`GREETING`, `OFF_TOPIC`, `GENERAL_QA`, `COMPETITOR_RESEARCH`).
- Task 1.2: Build Intent Classification helper method in `backend/api/services/query_rewriter.py` (`QueryRewriter.classify_intent(query)`) using light rule matching for greetings/general questions and entity/keyword analysis for competitive research topics.
- Task 1.3: Update `_query_analysis_node` in `LangGraphEngine` to populate `intent` in state and log `langgraph_query_analysis` with intent classification status.

## Task Group 2: Conditional Graph Execution & Adaptive Web Search Routing
- Task 2.1: Update `_web_research_node` in `LangGraphEngine` to inspect `intent`.
- Task 2.2: Skip `WebSearchService.search_competitor` calls when `intent` is `GREETING`, `OFF_TOPIC`, or `GENERAL_QA`, preventing redundant web traffic and conserving resources.
- Task 2.3: Ensure `execute_web_search` state flag defaults to `False` for non-competitor intents.

## Task Group 3: Adaptive System Prompting & Adaptive Synthesis Engine
- Task 3.1: Refactor `GroqReasoningEngine.synthesize_counterpoint` to accept `intent` parameter.
- Task 3.2: Create adaptive system prompts tailored to query intent:
  - `GREETING`: Concise, friendly greeting introducing CounterPoint as a strategic competitive intelligence assistant.
  - `GENERAL_QA`: Clear explanation of features (positioning doc contrast, web search intelligence, multi-turn Q&A).
  - `OFF_TOPIC`: Polite refusal explaining CounterPoint's focused domain (competitive intelligence) and inviting a software competitor query.
  - `COMPETITOR_RESEARCH`: Full 4-section Markdown competitive intelligence analysis.
- Task 3.3: Inject zero-hallucination guardrail instruction into the `COMPETITOR_RESEARCH` system prompt: *"Do NOT invent pricing models, entry tiers, or competitor features. If live web research findings or document context lack pricing data, state explicitly: 'No verified external pricing data found in sources'."*

## Task Group 4: Zero-Hallucination Rule-Based Fallback Engine Overhaul
- Task 4.1: Overhaul `GroqReasoningEngine._generate_fallback_synthesis` to eliminate static fake pricing tables (`| Entry Pricing | Self-serve low tier ($5-$15/mo) |`) and arbitrary synthetic feature benchmarks.
- Task 4.2: Tailor rule-based fallback responses by `intent`:
  - `GREETING` fallback: Clean welcome response without competitive tables.
  - `GENERAL_QA` fallback: Clean usage guide without competitive tables.
  - `OFF_TOPIC` fallback: Clean scope clarification response.
  - `COMPETITOR_RESEARCH` fallback: Transparent summary stating exact web sources found (or zero sources found) and document context extracted, explicitly marking missing fields as "Data not found in search results" rather than hallucinating metrics.

## Task Group 5: Backend API Endpoint & LangGraph Integration
- Task 5.1: Update `MultiHopSynthesisEngine` and DRF `SynthesisAPIView` (`backend/api/views.py`) to handle intent-aware responses cleanly and pass intent metadata in response payloads.
- Task 5.2: Ensure audit logs in `AuditLogger` record the classified `intent` alongside model execution duration.

## Task Group 6: Automated Test Suite Verification
- Task 6.1: Add comprehensive unit tests in `backend/api/tests/test_query_rewriter.py` for intent classification (`GREETING`, `OFF_TOPIC`, `GENERAL_QA`, `COMPETITOR_RESEARCH`).
- Task 6.2: Add unit tests in `backend/api/tests/test_synthesis_engine.py` and `test_langgraph_memory.py` validating that greetings and off-topic queries do NOT produce 4-section matrices or fake pricing tables.
- Task 6.3: Run full Django test suite (`python manage.py test api`) and Vitest frontend test suite (`npx vitest run`) to verify zero regressions.
