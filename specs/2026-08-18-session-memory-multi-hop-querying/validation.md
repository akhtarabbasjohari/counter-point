# Phase 4 Validation & Merge Criteria: Session Memory & Multi-Hop Querying

## 1. Success Criteria

### 1.1 Session Memory Persistence
- [ ] Active document context remains attached to the session ID across multiple API calls.
- [ ] Multi-turn conversation history correctly records previous user prompts and synthesized answers.
- [ ] Session TTL and cache expiry prevent memory leaks while isolating distinct session keys.

### 1.2 Multi-Hop Synthesis Engine
- [ ] Synthesis engine successfully retrieves both uploaded internal positioning context and live web search findings.
- [ ] Follow-up queries (e.g. "How does their pricing compare to our enterprise plan?") correctly reference prior document context and search results.
- [ ] Groq LLM prompts return structured, accurate competitive intelligence insights.

### 1.3 Audit Log Verification
- [ ] All underlying tool calls (`session_memory_lookup`, `web_search_execution`, `multihop_synthesis`) produce ISO 8601 timestamped JSON audit log entries.

## 2. Automated Test Execution Commands

```bash
# Navigate to backend directory
cd backend

# Run all Django unit and integration tests
python manage.py test api

# Run specific Phase 4 test suites
python manage.py test api.tests.test_session_manager
python manage.py test api.tests.test_synthesis_engine
python manage.py test api.tests.test_synthesis_api
```

## 3. Merge Readiness Checklist
- [ ] All Django tests pass with 100% success rate.
- [ ] Code meets project style guidelines and contains proper docstrings.
- [ ] Feature branch `feature/2026-08-18-session-memory-multi-hop-querying` is ready to merge into `main`.
