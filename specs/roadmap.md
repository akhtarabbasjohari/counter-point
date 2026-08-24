# CounterPoint - Implementation Roadmap

This roadmap breaks down the implementation of CounterPoint into 5 small, incremental phases of work using Python / Django REST Framework (DRF) for the backend and Vite / Vanilla CSS for the frontend.

---

## Phase 1: Project Setup & Specs Constitution
- [x] Create project specifications in `specs/` (`mission.md`, `tech-stack.md`, `roadmap.md`).
- [x] Initialize Python virtual environment (`venv`), Django project (`counterpoint`), and DRF app (`api`).
- [x] Configure `django-cors-headers`, environment variables (`python-dotenv`), and `requirements.txt`.
- [x] Setup initial Vite frontend structure, base CSS design tokens, and Vitest test runner.

## Phase 2: Document Processing & Timestamped Tool Logger
- [x] Implement DRF file upload view & serializer supporting `.pdf` and `.txt` files using `MultiPartParser`.
- [x] Build document parsing service using `pdfplumber` / `pypdf` for PDFs and UTF-8 stream reader for text files.
- [x] Implement timestamped audit logger module (Python `logging` or custom middleware) tracking tool name, parameters, execution timestamp, and status.
- [x] Write Django unit tests for document parsing and tool logger components.

## Phase 3: Web Search & Groq Reasoning Engine
- [x] Integrate official `groq` Python SDK with environment-configured API keys.
- [x] Build Python web search module (fetching current offerings, pricing, and recent competitor news).
- [x] Implement prompt strategy for competitor analysis that triggers web search tool execution.
- [x] Wire web search execution through the timestamped audit logger.

## Phase 4: Session Memory & Multi-Hop Querying
- [x] Implement session manager using Django sessions / cache framework to store document context and conversation history.
- [x] Build multi-hop synthesis engine in Python combining internal positioning document context with live web research findings.
- [x] Support continuous follow-up questions without losing prior research state.
- [x] Verify multi-hop research accuracy with test queries.

## Phase 5: UI Dashboard & End-to-End Verification
- [x] Build clean, responsive single-page web UI (Vite + Vanilla CSS/HTML):
  - Competitor search input & document upload dropzone
  - Findings summary display panel (offerings, pricing, gap analysis)
  - Real-time timestamped audit log viewer
  - Interactive multi-turn chat / Q&A section
- [x] Connect frontend to Django REST Framework API endpoints.
- [x] Perform full end-to-end user workflow testing and polish visual design.

## Phase 6: Multi-Turn Conversation Coreference Resolution & Entity Tracking
- [x] Implement `QueryRewriter` service (`backend/api/services/query_rewriter.py`) to resolve multi-turn pronouns (`that`, `it`, `them`) into explicit standalone queries before search.
- [x] Wire `QueryRewriter` into `MultiHopSynthesisEngine` prior to `WebSearchService` invocation.
- [x] Update `SessionManager` to track active competitor entities and conversation topic history.
- [x] Add Django unit/integration tests for multi-turn coreference resolution.

## Phase 7: Stateful Agent Memory Architecture & LangGraph Graph Engine
- [x] Install and configure `langgraph` and `langchain-core` Python dependencies.
- [x] Build `AgentMemoryState` graph state class maintaining dynamic context (`messages`, `active_entities`, `document_context`, `resolved_topic`).
- [x] Construct multi-node `StateGraph` execution pipeline (`QueryAnalysis` -> `StateMemoryLookup` -> `WebResearch` -> `StrategySynthesis`) with `MemorySaver` checkpointer.
- [x] Integrate `LangGraphEngine` into Django REST API synthesis endpoints replacing rigid static rule-based query handling.
- [x] Write Django backend unit and integration tests verifying graph state persistence and multi-turn state transitions across session turns.

## Phase 8: Security Hardening, Data Integrity & Architectural Refinement
- [x] **Security Hardening**:
  - Enforce mandatory `SECRET_KEY` configuration in production and set `DEBUG=False` by default in `settings.py` and `.env.example`.
  - Restrict default `ALLOWED_HOSTS` and `CORS_ALLOW_ALL_ORIGINS` setting to explicit environment origins.
  - Fix Stored XSS vulnerability in frontend markdown renderer (`parseMarkdownToHTML`) by HTML-escaping raw text content before applying markdown transformations and sanitizing link URLs.
  - Document single-tenant scope and lack of default multi-tenant auth in `README.md`.
- [x] **Data Integrity & Search Correctness**:
  - Remove fabricated synthetic search fallback (`_fallback_search`) in `WebSearchService` to ensure all research findings reflect authentic live web signals.
- [x] **Cache & Memory Leak Isolation**:
  - Incorporate `session_id` and document text hash into `GroqReasoningEngine` synthesis cache key to prevent cross-session context leaks.
  - Fix `AuditLogger` memory leak in `clear_logs()` by deleting session keys (`pop`) and setting a maximum session cap.
  - Document `MemorySaver` single-process checkpointer scope in `LangGraphEngine`.
- [x] **Audit & Routing Optimization**:
  - Consolidate duplicate audit log calls in `LangGraphEngine` (`langgraph_state_lookup` and `langgraph_execution_complete`).
  - Consolidate session ID resolution logic inside `SessionManager.get_or_create_session_id`.
  - Expand entity dictionary and add dynamic proper-noun extraction fallback in `QueryRewriter`.
  - Streamline API URL routing to use canonical trailing slashes.



