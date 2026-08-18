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
- **Client Logic**: Vanilla JS / TypeScript for sending API requests, handling doc uploads, rendering findings, and displaying live audit logs

### AI & Reasoning Engine
- **LLM Provider**: `groq` Python SDK (High-throughput inference for multi-hop reasoning, prompt synthesis, and tool orchestration)
- **Web Search Module**: Custom Python search integration using web search APIs (e.g., Tavily / Serper / DuckDuckGo) for fetching live competitor offerings, pricing, and news updates

### Document Processing
- **PDF Parser**: `pdfplumber` (or `pypdf`) for extracting structured text from uploaded PDF positioning documents
- **TXT Reader**: Native Python file handling and UTF-8 stream decoding

### Logging & Audit System
- **Logger**: Custom Python timestamped JSON audit log module (leveraging Python's standard `logging` library or custom middleware)
- **Log Fields**: `timestamp` (ISO 8601 string), `tool_name` (`web_search`, `read_positioning_doc`), `input_params`, `execution_time_ms`, `status`

### State & Session Management
- **Session Memory**: Django Session / Cache framework (`django.core.cache`) or in-memory session state tracking active document context, previous search results, and chat history per user session
