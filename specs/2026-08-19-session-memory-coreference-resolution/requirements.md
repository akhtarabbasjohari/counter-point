# Phase 6 Specification: Multi-Turn Conversation Coreference Resolution & Entity Tracking

## Scope
Phase 6 introduces automated query disambiguation and entity coreference resolution for multi-turn research conversations in CounterPoint.

## Requirements & Problem Context
When a user asks a follow-up query such as:
- Turn 1: *"What is Salesforce's primary revenue driver?"*
- Turn 2: *"How does our strategy compare to that?"*

The system previously passed the raw query string (`"How does our strategy compare to that?"`) directly to `WebSearchService.search_competitor(query)`. Because the raw string contains un-resolved pronouns (`that`, `it`, `them`), live search failed or returned generic fallback results.

### Key Requirements
1. **`QueryRewriter` Service**:
   Implement `backend/api/services/query_rewriter.py` to rewrite multi-turn user queries using session conversation history before invoking search or LLM reasoning engines.
2. **Entity & Topic Resolution**:
   Extract active competitor entities (e.g. *Salesforce*, *HubSpot*, *Notion*, *ClickUp*, *Linear*) and primary topics from previous conversation turns.
3. **Pipeline Integration**:
   Integrate `QueryRewriter.resolve_query(query, history)` into `MultiHopSynthesisEngine` prior to `WebSearchService` execution so web searches are performed using explicit, standalone queries.
4. **Audit Logging**:
   Log `query_coreference_resolution` events with raw query, resolved standalone query, and resolution time in `AuditLogger`.
5. **Testing**:
   Verify coreference resolution logic and multi-turn flow with automated Django tests.
