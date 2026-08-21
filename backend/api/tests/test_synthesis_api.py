from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from api.services.session_manager import SessionManager
from api.services.audit_logger import AuditLogger

class SynthesisAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.session_id = "test_custom_session_99"
        SessionManager.clear_session(self.session_id)

    def test_synthesis_endpoint_canonical_and_custom_header(self):
        headers = {'HTTP_X_SESSION_ID': self.session_id}
        payload = {
            'query': 'What is Notion offering?',
            'execute_web_search': False
        }

        response = self.client.post('/api/synthesis/', payload, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["session_id"], self.session_id)
        self.assertIn("synthesis", data)
        self.assertIn("recent_audit_logs", data)

    def test_multi_turn_conversation_persistence(self):
        headers = {'HTTP_X_SESSION_ID': self.session_id}

        # 1. Turn 1
        res1 = self.client.post('/api/query/', {'query': 'Turn 1 query', 'execute_web_search': False}, format='json', **headers)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        # 2. Turn 2 (Follow-up)
        res2 = self.client.post('/api/query/', {'query': 'Turn 2 follow-up query', 'execute_web_search': False}, format='json', **headers)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)

        # Verify history in session
        history = SessionManager.get_conversation_history(self.session_id)
        self.assertEqual(len(history), 4)  # 2 user questions + 2 assistant responses
        self.assertEqual(history[0]["content"], "Turn 1 query")
        self.assertEqual(history[2]["content"], "Turn 2 follow-up query")

    def test_document_context_attached_to_session_synthesis(self):
        headers = {'HTTP_X_SESSION_ID': self.session_id}

        # 1. Upload positioning file
        file_content = b"CounterPoint Strategy: High throughput LLM competitive synthesis engine."
        uploaded_file = SimpleUploadedFile("counterpoint_strategy.txt", file_content, content_type="text/plain")

        upload_res = self.client.post('/api/upload/', {'file': uploaded_file}, format='multipart', **headers)
        self.assertEqual(upload_res.status_code, status.HTTP_201_CREATED)

        # 2. Execute synthesis query
        synth_res = self.client.post('/api/synthesis/', {'query': 'Explain key features', 'execute_web_search': False}, format='json', **headers)
        self.assertEqual(synth_res.status_code, status.HTTP_200_OK)
        self.assertTrue(synth_res.json()["document_context_used"])
        self.assertEqual(synth_res.json()["document_name"], "counterpoint_strategy.txt")

    def test_session_reset_endpoint(self):
        headers = {'HTTP_X_SESSION_ID': self.session_id}
        self.client.post('/api/query/', {'query': 'Pre-reset query', 'execute_web_search': False}, format='json', **headers)

        reset_res = self.client.post('/api/session/reset/', {}, format='json', **headers)
        self.assertEqual(reset_res.status_code, status.HTTP_200_OK)

        history = SessionManager.get_conversation_history(self.session_id)
        self.assertEqual(history, [])
