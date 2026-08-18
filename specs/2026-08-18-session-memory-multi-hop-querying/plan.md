# Phase 4 Implementation Plan: Session Memory & Multi-Hop Querying

This plan breaks down the implementation of Session Memory & Multi-Hop Querying into numbered task groups.

---

### Task Group 1: Session Memory Manager (`backend/api/session_manager.py`)
- [x] Create `SessionManager` class utilizing `django.core.cache`.
- [x] Implement `get_session(session_id)`, `create_session()`, `store_document_context(session_id, doc_text)`, `append_conversation(session_id, role, content)`, and `get_history(session_id)`.
- [x] Write unit tests for `SessionManager` in `backend/api/tests/test_session_manager.py`.

---

### Task Group 2: Multi-Hop Reasoning & Synthesis Engine (`backend/api/synthesis_engine.py`)
- [x] Implement `MultiHopSynthesisEngine` class integrating `groq` SDK and web search module.
- [x] Add query decomposition logic to determine missing web research context vs document positioning context.
- [x] Wire tool executions (web search, session memory lookup) through `TimestampedAuditLogger`.
- [x] Support continuous follow-up synthesis by incorporating multi-turn conversation history.
- [x] Write unit tests for synthesis engine in `backend/api/tests/test_synthesis_engine.py`.

---

### Task Group 3: REST API Endpoints & Serializers (`backend/api/views.py`, `backend/api/urls.py`)
- [x] Build `MultiHopSynthesisView` DRF endpoint supporting `POST /api/synthesis/`.
- [x] Create `SynthesisRequestSerializer` and `SynthesisResponseSerializer` accepting `session_id`, `query`, and returning synthesized insights + tool execution log traces.
- [x] Ensure `X-Session-ID` header handling and automatic session key creation if missing.
- [x] Connect session memory to document upload endpoint so uploaded document context attaches to active session.

---

### Task Group 4: Integration Testing & Verification
- [x] Write comprehensive Django REST API integration tests in `backend/api/tests/test_synthesis_api.py`.
- [x] Verify multi-turn follow-up queries retain prior research context across successive API requests.
- [x] Confirm timestamped audit log events are recorded for every sub-tool execution during synthesis.
- [x] Execute full Django test suite `python manage.py test api` to ensure zero regressions.
