# Validation Specification: Document Processing & Timestamped Tool Logger

**Feature**: Document Processing & Timestamped Tool Logger  
**Phase**: Phase 2  
**Date**: 2026-08-18  

---

## 1. Success Criteria

To consider Phase 2 complete and ready for merging into `main` / `replanning`, all of the following criteria must pass cleanly:

### 1.1 Automated Testing
- **Django Unit Tests**: All unit tests in `api/tests/` pass with 0 errors or failures.
- **Coverage**:
  - `document_parser.py`: PDF extraction, TXT decoding, size validation, invalid file type errors.
  - `audit_logger.py`: Log entry creation, ISO 8601 formatting, duration tracking in ms, error capture, `@audit_tool` decorator execution.
  - `views.py` & `serializers.py`: Multipart upload endpoint returns HTTP 200 with structured JSON on success and HTTP 400 on invalid files.

### 1.2 Endpoint & Audit Trail Verification
- **File Upload Endpoint (`POST /api/documents/upload/`)**:
  - Uploading a sample `.txt` file returns `200 OK` with extracted text payload and metadata.
  - Uploading a sample `.pdf` file returns `200 OK` with page-by-page text payload and page count.
  - Uploading an unsupported file format (e.g. `.png`, `.exe`) returns `400 Bad Request`.
  - Uploading a file larger than 10MB returns `400 Bad Request`.
- **Audit Logs Endpoint (`GET /api/audit-logs/`)**:
  - Immediately following document upload, an audit log entry for `document_upload` is present.
  - Audit log entries validate strictly against the JSON schema:
    ```json
    {
      "timestamp": "2026-08-18T14:45:00.000000Z",
      "tool_name": "document_upload",
      "input_params": { "filename": "positioning_strategy.pdf", "file_size": 1048576 },
      "execution_time_ms": 42.5,
      "status": "SUCCESS",
      "error_message": null
    }
    ```

---

## 2. Verification Commands

Run the following commands to validate the implementation before merging:

```bash
# Activate virtual environment (Windows pwsh)
.\venv\Scripts\Activate.ps1

# Run backend unit & integration tests
python manage.py test api

# Run test suite with verbose output
python manage.py test api -v 2
```

---

## 3. Definition of Done (DoD)

- [ ] New branch created: `feature/2026-08-18-doc-processing-audit-logger`
- [ ] Specification files committed under `specs/2026-08-18-doc-processing-audit-logger/`:
  - [x] `requirements.md`
  - [x] `plan.md`
  - [x] `validation.md`
- [ ] Backend implementation complete and verified with Django test runner.
- [ ] No regression in Phase 1 setup.
