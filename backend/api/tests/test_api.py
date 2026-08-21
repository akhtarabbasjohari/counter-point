import io
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status

from api.services.document_parser import DocumentParserService
from api.services.audit_logger import AuditLogger, audit_tool

class CounterPointAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        AuditLogger.clear_logs("global")

    def test_health_check(self):
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "ok", "app": "counterpoint"})

    def test_txt_document_upload(self):
        file_content = b"CounterPoint positioning strategy file content. Target market: Enterprise and SMBs."
        uploaded_file = SimpleUploadedFile("strategy.txt", file_content, content_type="text/plain")

        response = self.client.post('/api/upload/', {'file': uploaded_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("document", response.json())
        doc = response.json()["document"]
        self.assertEqual(doc["file_name"], "strategy.txt")
        self.assertEqual(doc["page_count"], 1)

    def test_canonical_upload_and_audit_logs_endpoints(self):
        file_content = b"Canonical route test strategy positioning doc."
        uploaded_file = SimpleUploadedFile("canonical_strategy.txt", file_content, content_type="text/plain")

        # Test canonical upload endpoint
        response = self.client.post('/api/documents/upload/', {'file': uploaded_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test canonical audit logs endpoint
        log_res = self.client.get('/api/audit-logs/')
        self.assertEqual(log_res.status_code, status.HTTP_200_OK)
        self.assertGreater(log_res.json()["log_count"], 0)

        # Validate audit log JSON schema fields
        log_entry = log_res.json()["logs"][0]
        self.assertIn("timestamp", log_entry)
        self.assertIn("tool_name", log_entry)
        self.assertIn("input_params", log_entry)
        self.assertIn("execution_time_ms", log_entry)
        self.assertIn("status", log_entry)
        self.assertIn("error_message", log_entry)

    def test_invalid_document_upload(self):
        file_content = b"Invalid executable content"
        uploaded_file = SimpleUploadedFile("script.exe", file_content, content_type="application/octet-stream")

        response = self.client.post('/api/upload/', {'file': uploaded_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_oversized_file_upload(self):
        # Create virtual >10MB file buffer
        large_content = b"A" * (10 * 1024 * 1024 + 1024)
        uploaded_file = SimpleUploadedFile("large_doc.txt", large_content, content_type="text/plain")

        response = self.client.post('/api/upload/', {'file': uploaded_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_document_detail_and_clear(self):
        # 1. Check initially empty
        res = self.client.get('/api/documents/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNone(res.json()["active_document"])

        # 2. Upload document
        file_content = b"Positioning document test text."
        uploaded_file = SimpleUploadedFile("positioning.txt", file_content, content_type="text/plain")
        self.client.post('/api/upload/', {'file': uploaded_file}, format='multipart')

        # 3. Check document detail
        res2 = self.client.get('/api/documents/')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(res2.json()["active_document"])
        self.assertEqual(res2.json()["active_document"]["file_name"], "positioning.txt")

        # 4. Delete document
        res3 = self.client.delete('/api/documents/')
        self.assertEqual(res3.status_code, status.HTTP_200_OK)

        # 5. Verify cleared
        res4 = self.client.get('/api/documents/')
        self.assertIsNone(res4.json()["active_document"])

    def test_web_search(self):
        response = self.client.post('/api/search/', {'query': 'Notion'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.json())

    def test_multihop_query(self):
        response = self.client.post('/api/query/', {'query': 'Compare Notion vs counterpoint positioning', 'execute_web_search': False}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("synthesis", data)
        self.assertIn("model_used", data)
        self.assertIn("execution_time_ms", data)

    def test_audit_logs(self):
        # Perform an action to create log
        self.client.post('/api/search/', {'query': 'Linear'}, format='json')

        response = self.client.get('/api/logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.json()["log_count"], 0)

    def test_session_reset(self):
        response = self.client.post('/api/session/reset/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UnitServiceTests(TestCase):
    def setUp(self):
        AuditLogger.clear_logs("test_session")

    def test_document_parser_txt(self):
        uploaded_file = SimpleUploadedFile("test.txt", b"Hello CounterPoint text document parsing.", content_type="text/plain")
        result = DocumentParserService.parse_uploaded_file(uploaded_file, session_id="test_session")
        self.assertEqual(result["file_name"], "test.txt")
        self.assertEqual(result["file_type"], "text")
        self.assertEqual(result["character_count"], 41)
        self.assertEqual(result["page_count"], 1)

    def test_document_parser_invalid_format(self):
        uploaded_file = SimpleUploadedFile("test.bin", b"\x00\x01\x02\x03", content_type="application/octet-stream")
        with self.assertRaises(ValueError):
            DocumentParserService.parse_uploaded_file(uploaded_file, session_id="test_session")

    def test_audit_logger_direct_and_decorator(self):
        AuditLogger.log_tool_execution(
            tool_name="test_tool",
            input_params={"param1": "val1"},
            execution_time_ms=15.5,
            status="SUCCESS",
            result_summary="Completed successfully",
            session_id="test_session"
        )
        logs = AuditLogger.get_logs("test_session")
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["tool_name"], "test_tool")
        self.assertEqual(logs[0]["status"], "SUCCESS")

        @audit_tool("decorated_tool")
        def dummy_action(session_id="test_session"):
            return "ok"

        dummy_action(session_id="test_session")
        updated_logs = AuditLogger.get_logs("test_session")
        self.assertEqual(len(updated_logs), 2)
        self.assertEqual(updated_logs[0]["tool_name"], "decorated_tool")
