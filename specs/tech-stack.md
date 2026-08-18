# CounterPoint - Tech Stack Architecture

## 1. Overview
CounterPoint is built using a lightweight Node.js/TypeScript architecture designed for rapid LLM inference, clean document processing, and transparent tool execution tracking.

## 2. Core Technologies

### Backend Infrastructure
- **Runtime**: Node.js (v18+)
- **Language**: TypeScript (`tsconfig.json` configured for ES2022 / NodeNext)
- **Framework**: Express.js (`express`) for REST API endpoints and session management
- **File Upload**: `multer` for multipart form handling (PDF/TXT uploads)

### Frontend Interface
- **Tooling**: Vite for fast local development and lightweight bundling
- **UI Paradigm**: HTML5 + Vanilla CSS design system (custom tokens, responsive flex/grid layouts, dynamic micro-interactions, no heavy CSS frameworks)
- **Client Logic**: TypeScript / Vanilla JS for streaming responses, handling doc uploads, and updating live research logs

### AI & Reasoning Engine
- **LLM Provider**: Groq API (High-throughput inference for multi-hop reasoning and prompt synthesis)
- **Web Search Module**: Custom REST integration with web search provider (e.g. Tavily / Serper / DuckDuckGo API) for fetching live competitor news, pricing, and feature pages

### Document Processing
- **PDF Parser**: `pdf-parse` for extracting structured text from uploaded PDF positioning documents
- **TXT Reader**: Native Node.js stream and string decoding for text files

### Logging & Audit System
- **Logger**: Custom timestamped JSON/structured log module (`Winston` or lightweight custom logger)
- **Log Fields**: `timestamp` (ISO string), `tool_name` (`web_search`, `read_positioning_doc`), `input_params`, `execution_time_ms`, `status`

### State & Session Management
- **Session Memory**: In-memory session store tracking active document context, previous search results, and conversation history per user session
