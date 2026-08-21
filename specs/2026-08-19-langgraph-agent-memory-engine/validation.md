# Phase 7 Validation & Acceptance Criteria

## 1. Automated Test Suite Validation
- All Django backend unit/integration tests pass cleanly (`venv\Scripts\python manage.py test api`).
- All Vitest frontend tests pass cleanly (`npx vitest run`).

## 2. Stateful Agent Memory & Graph Transition Verification
- Multi-turn conversation state is maintained inside LangGraph `MemorySaver` checkpoints per `session_id`.
- Given free-form unexpected follow-up queries (e.g. *"How do we stack up against them?"* or *"What about their enterprise plan?"*):
  - `QueryAnalysisNode` identifies active entities from graph state without relying on hardcoded static rules.
  - `WebResearchNode` executes web search for the explicit entity stored in state.
  - Audit log records node transition steps: `langgraph_query_analysis` -> `langgraph_state_lookup` -> `langgraph_web_research` -> `langgraph_synthesis`.
