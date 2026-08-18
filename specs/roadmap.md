# CounterPoint - Implementation Roadmap

This roadmap breaks down the implementation of CounterPoint into 5 small, incremental phases of work.

---

## Phase 1: Project Setup & Specs Constitution
- [x] Create project specifications in `specs/` (`mission.md`, `tech-stack.md`, `roadmap.md`).
- [ ] Initialize Express.js backend structure with TypeScript and environment config handling (`.env`).
- [ ] Setup initial Vite frontend build pipeline and base CSS tokens.

## Phase 2: Document Processing & Timestamped Tool Logger
- [ ] Implement file upload middleware (`multer`) supporting `.pdf` and `.txt` files.
- [ ] Build document parsing service using `pdf-parse` for PDFs and UTF-8 stream reader for text files.
- [ ] Implement timestamped audit logger module to track every tool execution (tool name, input arguments, execution timestamp, and status).
- [ ] Write unit tests for document parsing and logger modules.

## Phase 3: Web Search & Groq Reasoning Engine
- [ ] Integrate Groq API client with environment-configured API keys.
- [ ] Build live web search tool wrapper (fetching current offerings, pricing, and updates).
- [ ] Implement prompt strategy for competitor analysis that invokes web search and parses results.
- [ ] Wire web search execution through the timestamped tool logger.

## Phase 4: Session Memory & Multi-Hop Querying
- [ ] Create in-memory session manager to store uploaded document context and past conversation turns.
- [ ] Implement multi-hop synthesis engine combining internal positioning document context with live web research findings.
- [ ] Support continuous follow-up questions without losing prior research state.
- [ ] Verify multi-hop research accuracy with test queries.

## Phase 5: UI Dashboard & End-to-End Verification
- [ ] Build clean, responsive single-page web UI:
  - Competitor search input & document upload dropzone
  - Findings summary display panel (offerings, pricing, gap analysis)
  - Real-time timestamped audit log viewer
  - Interactive multi-turn chat / Q&A section
- [ ] Connect frontend to Express API endpoints.
- [ ] Perform full end-to-end user workflow testing and polish visual design.
