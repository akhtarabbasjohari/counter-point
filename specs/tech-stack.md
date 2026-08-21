# CounterPoint - Tech Stack Architecture

## 1. Overview
CounterPoint is built using a robust Python / Django REST Framework (DRF) backend paired with a lightweight Vite / Vanilla CSS frontend, designed for fast LLM inference, clean document parsing, and transparent tool execution tracking.

## 2. Core Technologies

### Backend Infrastructure
- **Runtime & Language**: Python (v3.11+)
- **Framework**: Django (v5.x) & Django REST Framework (DRF) for REST API endpoints, serializers, and request handling
- **CORS Management**: `django-cors-headers` for seamless cross-origin requests from the frontend client
- **File Upload & Parsing**: DRF `MultiPartParser` with `pdfplumber` / `pypdf` for PDF text extraction and standard Python UTF-8 decoding for TXT files
- **Package Management**: `requirements.txt` / Virtual Environment (`venv`)

### Frontend Interface
- **Tooling**: Vite for fast local development and lightweight bundling
- **UI Paradigm**: HTML5 + Vanilla CSS design system (custom design tokens, responsive flex/grid layouts, dynamic micro-interactions, no heavy CSS frameworks)
- **Responsive Architecture**: Mobile-first fluid CSS grid/flexbox layout with dynamic media query breakpoints (`@media (max-width: 1024px)`, `@media (max-width: 640px)`), adaptable sidebar drawer, and fluid touch controls for desktop, tablet, and mobile devices
- **Client Logic**: Vanilla JS / TypeScript for sending API requests, handling doc uploads, rendering findings, and displaying live audit logs
- **Testing & Validation**: Vitest for Vite-native unit and integration test validation (`npm run test`)

### AI & Reasoning Engine
- **LLM Provider**: `groq` Python SDK (High-throughput inference for multi-hop reasoning, prompt synthesis, and tool orchestration)
- **Stateful Agent Memory Engine**: `langgraph` (`StateGraph` + `MemorySaver`) managing dynamic multi-turn conversation graph state, active entities, intent tracking, and research node execution without relying on rigid static rules
- **Coreference Resolution Engine**: `QueryRewriter` service (`backend/api/services/query_rewriter.py`) utilizing session memory context to resolve ambiguous multi-turn follow-up queries (e.g. *"How does our strategy compare to that?"* -> *"Compare CounterPoint strategy with Salesforce revenue & positioning"*) before web search execution
- **Web Search Module**: Custom Python search integration using web search APIs (e.g., Tavily / Serper / DuckDuckGo) for fetching live competitor offerings, pricing, and news updates


### Document Processing
- **PDF Parser**: `pdfplumber` (or `pypdf`) for extracting structured text from uploaded PDF positioning documents
- **TXT Reader**: Native Python file handling and UTF-8 stream decoding

### Logging & Audit System
- **Logger**: Custom Python timestamped JSON audit log module (leveraging Python's standard `logging` library or custom middleware)
- **Log Fields**: `timestamp` (ISO 8601 string), `tool_name` (`web_search`, `read_positioning_doc`), `input_params`, `execution_time_ms`, `status`

### State & Session Management
- **Stateful Graph Memory**: LangGraph `MemorySaver` checkpointer persisting stateful graph snapshots per session, tracking conversation history, extracted entities, active document context, and intent state across arbitrary free-form user queries
- **Session Memory**: Django Session / Cache framework (`django.core.cache`) or in-memory session state tracking active document context, previous search results, and chat history per user session

