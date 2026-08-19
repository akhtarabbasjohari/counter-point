# Phase 7 Implementation Plan: Stateful Agent Memory Architecture & LangGraph Graph Engine

## Task Group 1: Dependency Setup & Graph State Schema
- Task 1.1: Add `langgraph` and `langchain-core` to `backend/requirements.txt` and install in `venv`.
- Task 1.2: Create `backend/api/services/langgraph_memory_engine.py`.
- Task 1.3: Define `AgentMemoryState(TypedDict)` containing `messages`, `active_entities`, `document_context`, `resolved_topic`, `web_research_results`, and `final_synthesis`.

## Task Group 2: Multi-Node `StateGraph` Pipeline & `MemorySaver`
- Task 2.1: Implement `QueryAnalysisNode` to extract entities and resolve intent dynamically.
- Task 2.2: Implement `StateMemoryLookupNode` to load active positioning doc context and conversation checkpoints.
- Task 2.3: Implement `WebResearchNode` to execute live web search signals via `WebSearchService`.
- Task 2.4: Implement `StrategySynthesisNode` to run Groq reasoning synthesis over the state graph.
- Task 2.5: Compile `StateGraph` with `MemorySaver` checkpointer and thread-based `configurable: {"thread_id": session_id}` checkpointing.

## Task Group 3: Django API Integration & Workflow Wiring
- Task 3.1: Wire `LangGraphEngine.run_synthesis()` into `MultiHopSynthesisEngine` and Django REST Framework `SynthesisAPIView`.
- Task 3.2: Record audit logs for graph node transitions (`langgraph_query_analysis`, `langgraph_state_lookup`, `langgraph_web_research`, `langgraph_synthesis`).

## Task Group 4: Unit & Integration Testing
- Task 4.1: Write unit tests in `backend/api/tests/test_langgraph_memory.py` validating state transitions and entity memory persistence.
- Task 4.2: Execute full backend test suite (`python manage.py test api`) and Vitest client suite (`npx vitest run`).
