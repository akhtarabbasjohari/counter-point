import io
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status

class CounterPointAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

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
        self.assertEqual(response.json()["document"]["file_name"], "strategy.txt")

    def test_invalid_document_upload(self):
        file_content = b"Invalid executable content"
        uploaded_file = SimpleUploadedFile("script.exe", file_content, content_type="application/octet-stream")

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
