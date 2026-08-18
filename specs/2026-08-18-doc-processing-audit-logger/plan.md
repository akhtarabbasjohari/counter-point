# Implementation Plan: Document Processing & Timestamped Tool Logger

**Feature**: Document Processing & Timestamped Tool Logger  
**Phase**: Phase 2  
**Date**: 2026-08-18  

---

## Task Groups

### Task Group 1: Core Document Parsing Service
- [ ] Install/verify document parsing dependencies (`pdfplumber` / `pypdf`) in the backend virtual environment.
- [ ] Create `api/services/document_parser.py` module.
- [ ] Implement PDF parsing function `parse_pdf_document(file_obj)` that extracts page text, page counts, and total characters using `pdfplumber`.
- [ ] Implement TXT parsing function `parse_txt_document(file_obj)` with UTF-8 decoding and fallback handling.
- [ ] Implement main entry point `parse_document(file_obj, filename)` that routes processing based on file extension and validates size (<10MB).
- [ ] Write unit tests for `document_parser.py` covering standard text files, valid PDFs, empty files, and unsupported formats.

### Task Group 2: Timestamped Tool Audit Logger Module
- [ ] Create `api/services/audit_logger.py` module.
- [ ] Implement `AuditLogger` class / logger utility wrapper.
- [ ] Implement `log_tool_execution(tool_name, input_params, execution_time_ms, status, error_message=None)` producing ISO 8601 UTC JSON entries.
- [ ] Provide thread-safe in-memory log buffer / file logger for retrieving recent audit entries.
- [ ] Create a Python context manager / decorator `@audit_tool(tool_name)` to automatically record start/end time, parameters, status, and execution duration.
- [ ] Write unit tests for `audit_logger.py` verifying JSON schema, ISO 8601 formatting, duration calculation, and error logging.

### Task Group 3: DRF Endpoints, Serializers & Integration Tests
- [ ] Create `DocumentUploadSerializer` in `api/serializers.py` enforcing `.pdf`/`.txt` file extension constraints and 10MB file size limit.
- [ ] Create `DocumentUploadView` in `api/views.py` using `MultiPartParser`, invoking `parse_document`, and decorating execution with `@audit_tool("document_upload")`.
- [ ] Create `AuditLogListView` in `api/views.py` returning recent audit log records.
- [ ] Wire API routes in `api/urls.py` (`/api/documents/upload/` and `/api/audit-logs/`).
- [ ] Write Django REST Framework integration tests (`api/tests/test_views.py`) testing end-to-end multipart upload requests, response formatting, and audit log generation.
