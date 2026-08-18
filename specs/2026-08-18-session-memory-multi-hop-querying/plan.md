# Phase 4 Implementation Plan: Session Memory & Multi-Hop Querying

This plan breaks down the implementation of Session Memory & Multi-Hop Querying into numbered task groups.

---

### Task Group 1: Session Memory Manager (`backend/api/session_manager.py`)
- [ ] Create `SessionManager` class utilizing `django.core.cache`.
- [ ] Implement `get_session(session_id)`, `create_session()`, `store_document_context(session_id, doc_text)`, `append_conversation(session_id, role, content)`, and `get_history(session_id)`.
- [ ] Write unit tests for `SessionManager` in `backend/api/tests/test_session_manager.py`.

---

### Task Group 2: Multi-Hop Reasoning & Synthesis Engine (`backend/api/synthesis_engine.py`)
- [ ] Implement `MultiHopSynthesisEngine` class integrating `groq` SDK and web search module.
- [ ] Add query decomposition logic to determine missing web research context vs document positioning context.
- [ ] Wire tool executions (web search, session memory lookup) through `TimestampedAuditLogger`.
- [ ] Support continuous follow-up synthesis by incorporating multi-turn conversation history.
- [ ] Write unit tests for synthesis engine in `backend/api/tests/test_synthesis_engine.py`.

---

### Task Group 3: REST API Endpoints & Serializers (`backend/api/views.py`, `backend/api/urls.py`)
- [ ] Build `MultiHopSynthesisView` DRF endpoint supporting `POST /api/synthesis/`.
- [ ] Create `SynthesisRequestSerializer` and `SynthesisResponseSerializer` accepting `session_id`, `query`, and returning synthesized insights + tool execution log traces.
- [ ] Ensure `X-Session-ID` header handling and automatic session key creation if missing.
- [ ] Connect session memory to document upload endpoint so uploaded document context attaches to active session.

---

### Task Group 4: Integration Testing & Verification
- [ ] Write comprehensive Django REST API integration tests in `backend/api/tests/test_synthesis_api.py`.
- [ ] Verify multi-turn follow-up queries retain prior research context across successive API requests.
- [ ] Confirm timestamped audit log events are recorded for every sub-tool execution during synthesis.
- [ ] Execute full Django test suite `python manage.py test api` to ensure zero regressions.
