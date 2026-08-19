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
- [ ] Implement `QueryRewriter` service (`backend/api/services/query_rewriter.py`) to resolve multi-turn pronouns (`that`, `it`, `them`) into explicit standalone queries before search.
- [ ] Wire `QueryRewriter` into `MultiHopSynthesisEngine` prior to `WebSearchService` invocation.
- [ ] Update `SessionManager` to track active competitor entities and conversation topic history.
- [ ] Add Django unit/integration tests for multi-turn coreference resolution.

