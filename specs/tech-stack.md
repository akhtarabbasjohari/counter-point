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

### Security & Infrastructure Hardening
- **Environment Security**: Strict `SECRET_KEY` validation (prevents starting server in production with insecure fallback keys), `DEBUG=False` by default, and explicit `ALLOWED_HOSTS` configuration
- **Cross-Site Scripting (XSS) Protection**: Mandatory HTML escaping of raw markdown content before rendering DOM nodes in `parseMarkdownToHTML`, accompanied by protocol sanitization for hyperlink URLs
- **Single-Tenant Scope**: Transparent session context handling (`X-Session-ID`) with documented recommendations for multi-tenant gateway authentication

### AI & Reasoning Engine
- **LLM Provider**: `groq` Python SDK (High-throughput inference for multi-hop reasoning, prompt synthesis, and tool orchestration)
- **Stateful Agent Memory Engine**: `langgraph` (`StateGraph` + `MemorySaver`) managing dynamic multi-turn conversation graph state, active entities, intent tracking, and research node execution without relying on rigid static rules
- **Intent Classification & Adaptive Routing**: Dynamic intent classification node inside LangGraph categorizing inputs into `GREETING`, `OFF_TOPIC`, `GENERAL_QA`, and `COMPETITOR_RESEARCH` to prevent unnecessary web search calls and suppress rigid competitor table structures for conversational inputs
- **Anti-Hallucination Guardrail Architecture**: Zero-hallucination policy eliminating hardcoded synthetic pricing grids (`$5-$15/mo`) and forcing explicit fallback statements ("No pricing data found in sources") whenever live search signals or LLM inference yield incomplete market information
- **Coreference Resolution Engine**: `QueryRewriter` service (`backend/api/services/query_rewriter.py`) utilizing session memory context and dynamic proper-noun extraction to resolve ambiguous multi-turn follow-up queries before web search execution
- **Web Search Module**: Authentic DuckDuckGo (`ddgs`) live search integration for real-time market data without synthetic search hallucination

### State, Caching & Session Management
- **Stateful Graph Memory**: LangGraph `MemorySaver` checkpointer persisting stateful graph snapshots per session (single-process development scope)
- **Session-Isolated Cache**: Session-specific, document-content-hashed MD5 synthesis cache key in `GroqReasoningEngine` to eliminate cross-session data leaks
- **Session Audit Logger**: Thread-safe in-memory audit log manager (`AuditLogger`) with automatic session cleanup and maximum session caps to prevent memory leaks

