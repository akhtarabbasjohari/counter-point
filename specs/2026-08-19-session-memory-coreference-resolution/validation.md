# Phase 6 Validation & Acceptance Criteria

## 1. Automated Test Suite Validation
- All 24+ Django backend unit/integration tests pass cleanly (`venv\Scripts\python manage.py test api`).
- All 10 Vitest frontend tests pass cleanly (`npx vitest run`).

## 2. Multi-Turn Coreference Resolution Criteria
- Given Turn 1: *"What is Salesforce's primary revenue driver?"*
- Given Turn 2: *"How does our strategy compare to that?"*
- Expected Result:
  - `QueryRewriter` resolves Turn 2 into an explicit query string containing `Salesforce` (e.g. *"Compare CounterPoint strategy with Salesforce revenue & positioning"*).
  - `WebSearchService` executes web search for `Salesforce`, NOT for the raw string `"How does our strategy compare to that?"`.
  - Audit log shows `query_coreference_resolution` status `SUCCESS` with parameter `resolved_query`.
