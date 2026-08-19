# Phase 7 Specification: Stateful Agent Memory Architecture & LangGraph Graph Engine

## Scope
Phase 7 introduces a stateful agent memory engine leveraging **LangGraph** (`StateGraph` + `MemorySaver`) to replace rigid static rule-based query handling with dynamic graph state persistence.

## Background & Problem Statement
In previous iterations, query coreference resolution relied on static regex pattern matching and micro-LLM prompts. However, real-world user queries are highly unexpected, free-form, and do not always follow predefined keyword rules.

To build a robust agent, CounterPoint requires a **Stateful Graph Memory Architecture** where:
- State transitions track dynamic conversation state, active entities, intent context, positioning document context, and multi-turn research findings.
- Memory checkpoints (`MemorySaver`) persist graph states across turns per session.
- Flexible graph nodes process user input adaptively regardless of prompt phrasing.

## Key Requirements
1. **LangGraph Dependency Setup**:
   Add `langgraph` and `langchain-core` to `backend/requirements.txt` and install in `venv`.
2. **`AgentMemoryState` Definition**:
   Define `TypedDict` state schema representing:
   - `messages`: List of conversation messages (User / Assistant / System).
   - `active_entities`: Tracked competitor entities (*Salesforce*, *HubSpot*, *Notion*, etc.).
   - `document_context`: Active positioning document text and metadata.
   - `resolved_topic`: Current explicit research topic.
   - `web_research_results`: External web search signals.
   - `final_synthesis`: Generated Markdown counter-point analysis report.
3. **Multi-Node `StateGraph` Construction**:
   Implement 4 primary execution nodes in `backend/api/services/langgraph_memory_engine.py`:
   - `QueryAnalysisNode`: Analyzes incoming prompt and updates intent/entity state.
   - `StateMemoryLookupNode`: Merges session document context and conversation memory checkpoints.
   - `WebResearchNode`: Triggers targeted web search when external signals are required.
   - `StrategySynthesisNode`: Generates final competitive synthesis using Groq LLM.
4. **State Checkpointing (`MemorySaver`)**:
   Use `MemorySaver` to save state checkpoints per `session_id` thread configuration (`configurable: {"thread_id": session_id}`).
5. **API Integration**:
   Connect `LangGraphEngine` to Django REST API endpoints while preserving existing response payload contracts.
