# Phase 5 Requirements: UI Dashboard & End-to-End Verification

## 1. Context & Executive Summary
CounterPoint requires a production-grade, highly responsive single-page web dashboard built with HTML5, Vanilla CSS, and JavaScript (Vite). Product managers and strategists need an intuitive interface to upload internal strategy documents, execute competitor search queries, review multi-hop competitive intelligence reports, and inspect live timestamped tool audit logs.

## 2. Scope & Key Decisions

### 2.1 User Interface Architecture
- **Layout Model**: Fluid single-page workspace consisting of:
  - **Header Bar**: Application branding, system active model tag, session reset control, and backend health status indicator.
  - **Collapsible Sidebar Drawer**: Houses the PDF/TXT document upload dropzone, active document context card, and real-time audit log list view.
  - **Central Main Stage**: Houses quick preset query chips, research query input bar, web search toggle switch, and multi-turn research findings timeline.
- **Design Tokens & Aesthetics**: Custom CSS variables for color tokens, typographic scale (Inter / sans-serif), elevation shadows, fluid spacing, and smooth transition micro-animations without heavy external CSS frameworks.
- **Responsive Breakpoints**:
  - Desktop (`> 1024px`): Two-column layout with fixed sidebar and wide main timeline.
  - Tablet (`640px - 1024px`): Adaptable sidebar drawer and fluid card elements.
  - Mobile (`< 640px`): Collapsible sidebar drawer with toggle button, single-column stacked view, touch-friendly touch targets.

### 2.2 Functional Requirements
- **Document Management**: Drag-and-drop file upload dropzone supporting PDF/TXT files, active document preview badge, word count stats, and one-click clear context button.
- **Competitor Querying & Synthesis**: Interactive search input with preset query chips (e.g. Notion, Linear, Enterprise Pricing), web search toggle checkbox, loading state indicator, and structured report cards.
- **Audit Log Inspection**: Live timestamped log feed recording tool executions (`session_memory_lookup`, `web_search_execution`, `groq_reasoning_synthesis`). Clickable log rows open an interactive detail modal displaying raw JSON parameters and timing metrics.
- **Session Reset**: One-click session reset clearing active document context, conversation timeline, and log traces.

### 2.3 Integration & API Connection
- Asynchronous API client (`src/api.js`) connecting to DRF endpoints (`/api/health/`, `/api/upload/`, `/api/documents/`, `/api/synthesis/`, `/api/logs/`, `/api/session/reset/`) with host fallback resolution.
