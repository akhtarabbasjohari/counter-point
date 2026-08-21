# Phase 4 Requirements: Session Memory & Multi-Hop Querying

## 1. Executive Summary & Context
CounterPoint requires a continuous session memory and multi-hop reasoning engine. Product managers and strategists need to analyze live web research (competitor offerings, pricing, feature updates) against uploaded internal positioning documents (PDF/TXT) across multi-turn conversations without losing context.

## 2. Technical Scope & Requirements

### 2.1 Session Memory Manager
- **Storage Backend**: Utilize Django's session / cache framework (`django.core.cache`) to persist user session state across API calls.
- **Session Data**:
  - `session_id`: Unique UUID identifier per active user session.
  - `document_context`: Extracted text from uploaded PDF/TXT positioning documents.
  - `conversation_history`: Ordered list of user queries, tool execution summaries, and system responses.
  - `web_research_cache`: Cached web search results to reduce redundant external calls.
- **Lifetime & Isolation**: Configurable TTL (Time-To-Live) per session with strict tenant isolation.

### 2.2 Multi-Hop Synthesis Engine
- **Orchestration**: Python service leveraging the `groq` SDK for multi-hop competitive intelligence synthesis.
- **Execution Pipeline**:
  1. **Context Extraction**: Retrieve stored document context and recent conversation history from session memory.
  2. **Query Decomposition**: Analyze incoming query to identify required live web search parameters vs internal document references.
  3. **Tool Execution**: Execute web search tool queries as needed, logging every execution through the timestamped audit logger.
  4. **Multi-Hop Synthesis**: Synthesize internal document insights and live web research into a clear, structured competitive comparison.
- **Follow-up Support**: Process continuous multi-turn follow-up questions while maintaining prior research context.

### 2.3 Timestamped Audit Logging Integration
- Every tool execution (document context read, web search invocation, LLM synthesis pass) must emit a structured JSON audit log event:
  - `timestamp`: ISO 8601 string (`YYYY-MM-DDTHH:MM:SS.mmmZ`).
  - `tool_name`: `session_memory_lookup`, `web_search_execution`, or `multihop_synthesis`.
  - `input_params`: Sanitized input dictionary.
  - `execution_time_ms`: Execution duration in milliseconds.
  - `status`: `success` or `error`.

## 3. Key Technical Decisions
1. **Session Identification**: Pass `X-Session-ID` custom header or fallback to standard Django session cookie (`sessionid`).
2. **State Storage**: Use Django cache framework abstraction to allow memory backend for local dev and Redis for production deployment.
3. **Error Handling**: Graceful fallback when web search APIs fail or document context is missing, informing the user without breaking session history.
