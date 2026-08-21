# Phase 6 Implementation Plan: Multi-Turn Conversation Coreference Resolution

## Task Group 1: `QueryRewriter` Coreference Resolution Module
- Task 1.1: Create `backend/api/services/query_rewriter.py` with `QueryRewriter.resolve_query(query, conversation_history, session_id)`.
- Task 1.2: Implement regex and fast entity extraction to detect competitor entities (*Salesforce*, *HubSpot*, *Notion*, *ClickUp*, *Linear*, *Asana*, *Monday.com*) from chat history.
- Task 1.3: Implement lightweight Groq LLM / fallback coreference resolver to convert vague queries into explicit standalone search queries.
- Task 1.4: Add audit log trace `query_coreference_resolution` in `AuditLogger`.

## Task Group 2: Integration into `MultiHopSynthesisEngine`
- Task 2.1: Update `MultiHopSynthesisEngine.execute_synthesis()` in `backend/api/services/synthesis_engine.py`.
- Task 2.2: Invoke `QueryRewriter.resolve_query()` before triggering `WebSearchService.search_competitor()`.
- Task 2.3: Pass the resolved standalone query to `WebSearchService` while retaining the original query for UI chat display.

## Task Group 3: Comprehensive Django Backend Tests & Verification
- Task 3.1: Add unit tests in `backend/api/tests.py` testing `QueryRewriter` with multi-turn conversation payloads.
- Task 3.2: Add integration tests verifying multi-hop synthesis for pronoun follow-ups (`"How does our strategy compare to that?"`).
- Task 3.3: Execute full Django test suite (`python manage.py test api`) and Vitest client suite (`npx vitest run`).
