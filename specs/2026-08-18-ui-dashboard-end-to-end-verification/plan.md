# Phase 5 Implementation Plan: UI Dashboard & End-to-End Verification

This plan breaks down the implementation and polish of the UI Dashboard and End-to-End verification into numbered task groups.

---

### Task Group 1: Core Design System & CSS Layout Refinement (`frontend/src/index.css`)
- [ ] Refine CSS design tokens (`--bg-primary`, `--accent-color`, `--status-success`, `--card-bg`, etc.).
- [ ] Polish responsive media query breakpoints (`@media (max-width: 1024px)`, `@media (max-width: 640px)`).
- [ ] Enhance sidebar drawer transitions, dropzone hover states, report card typography, and modal overlays.

---

### Task Group 2: Single-Page HTML Structure & DOM Components (`frontend/index.html`)
- [ ] Audit `index.html` structure for semantic HTML5 markup, accessibility labels, and unique IDs.
- [ ] Ensure dropzone, active document viewer, preset query chips, research timeline container, and audit log list elements are cleanly structured.
- [ ] Polish modal markup for JSON audit log inspection.

---

### Task Group 3: Event-Driven Client State & Controller (`frontend/src/main.js`, `frontend/src/api.js`)
- [ ] Connect `ApiClient` endpoints to UI event handlers (`fileInput`, `dropzone`, `queryForm`, `btnResetSession`, `btnClearDoc`).
- [ ] Implement automatic event-driven log refreshes following file uploads, search requests, and synthesis executions.
- [ ] Add interactive log inspector modal displaying formatted JSON payload and execution duration.
- [ ] Handle backend health status indicator and error boundary notifications.

---

### Task Group 4: Automated Testing & End-to-End Verification (`frontend/src/api.test.js`, Vitest, Django tests)
- [ ] Execute Vitest unit test suite `npx vitest run` for frontend API client interactions.
- [ ] Execute full Django backend test suite `python manage.py test api`.
- [ ] Verify full end-to-end user workflow (document upload -> competitor query -> multi-hop synthesis report -> audit log inspection -> session reset).
