# Requirements Specification: Document Processing & Timestamped Tool Logger

**Feature**: Document Processing & Timestamped Tool Logger  
**Phase**: Phase 2 of CounterPoint Roadmap  
**Date**: 2026-08-18  

---

## 1. Context & Business Goals

CounterPoint enables product managers and strategists to compare live web research against internal positioning strategy documents. To achieve this, the system must ingest positioning documents (`.pdf` and `.txt`) and extract clean text for downstream AI synthesis. Additionally, to ensure transparency and auditability (as outlined in `specs/mission.md`), every internal tool execution (e.g., document parsing, web search) must be tracked via a timestamped audit logger recording execution metadata, parameters, and timings.

---

## 2. Technical Stack & Alignment

As defined in `specs/tech-stack.md`:
- **Backend Framework**: Django 5.x & Django REST Framework (DRF).
- **File Ingestion**: DRF `MultiPartParser` with payload size limits up to 10MB.
- **PDF Extraction**: `pdfplumber` (primary) or `pypdf` (fallback) for clean page-by-page text extraction.
- **TXT Extraction**: Native Python stream reader with standard UTF-8 decoding.
- **Audit Logging**: Python `logging` or custom utility module outputting ISO 8601 JSON-formatted log entries.

---

## 3. Detailed Scope & Requirements

### 3.1 Document Ingestion & Parsing
- **FR-2.1.1 File Upload API**: Provide a DRF endpoint (e.g., `POST /api/documents/upload/`) accepting multipart file payloads (`.pdf`, `.txt`).
- **FR-2.1.2 Validation**: Validate file extensions and enforce a maximum file size limit of 10MB. Reject unsupported MIME types or oversized files with clear HTTP 400 response payload errors.
- **FR-2.1.3 PDF Parsing Service**: Implement a service module that extracts clean text content from PDF pages, tracking page counts and character statistics.
- **FR-2.1.4 Text File Reader**: Implement a service module to safely decode UTF-8 text files with error handling for alternate encodings.
- **FR-2.1.5 Data Contract**: Return a standardized structured JSON payload containing document metadata (`filename`, `file_type`, `character_count`, `page_count`, `extracted_text`).

### 3.2 Timestamped Tool Audit Logger
- **FR-2.2.1 Audit Logger Module**: Create a dedicated logger service/wrapper for instrumenting tool calls across the application.
- **FR-2.2.2 Log Payload Schema**: Every log record must include:
  - `timestamp`: ISO 8601 UTC formatted string (e.g., `2026-08-18T14:45:00.000Z`)
  - `tool_name`: String identifier of the tool (e.g., `read_positioning_doc`, `pdf_parser`, `web_search`)
  - `input_params`: JSON object summarizing parameters passed to the tool
  - `execution_time_ms`: Execution duration in milliseconds
  - `status`: String status indicator (`SUCCESS` or `ERROR`)
  - `error_message`: Optional error details if `status` is `ERROR`
- **FR-2.2.3 Audit Log Retrieval API**: Provide an endpoint or utility method to inspect recent audit logs for debugging and frontend audit log rendering.

---

## 4. Key Architectural Decisions

1. **In-Memory Text Processing**: Uploaded documents are parsed synchronously in-memory (up to 10MB limit) for fast response times, avoiding unnecessary persistent disk footprint during early phases.
2. **Structured JSON Audit Logs**: Audit logs use ISO 8601 timestamps and JSON structure so the frontend UI (Phase 5) can consume and render real-time execution trails.
3. **Decoupled Parser Service**: Parsing logic is completely isolated from DRF view logic in a dedicated service layer (`api/services/document_parser.py`) for clean unit testing and reuse.
