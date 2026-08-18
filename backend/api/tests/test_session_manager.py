from django.test import TestCase
from api.services.session_manager import SessionManager
from api.services.audit_logger import AuditLogger

class SessionManagerTests(TestCase):
    def setUp(self):
        self.session_id = "test_session_123"
        SessionManager.clear_session(self.session_id)

    def test_session_data_initialization(self):
        data = SessionManager.get_session_data(self.session_id)
        self.assertIsNone(data["active_document"])
        self.assertEqual(data["conversation_history"], [])

    def test_active_document_management(self):
        doc_data = {
            "file_name": "test_strategy.pdf",
            "file_type": "pdf",
            "word_count": 120,
            "text": "Positioning strategy text content for testing session memory."
        }

        # 1. Set active document
        SessionManager.set_active_document(self.session_id, doc_data)
        retrieved_doc = SessionManager.get_active_document(self.session_id)
        self.assertIsNotNone(retrieved_doc)
        self.assertEqual(retrieved_doc["file_name"], "test_strategy.pdf")

        # 2. Clear active document
        SessionManager.clear_active_document(self.session_id)
        self.assertIsNone(SessionManager.get_active_document(self.session_id))

    def test_conversation_history_append_and_retrieve(self):
        SessionManager.append_conversation_message(self.session_id, "user", "What is Notion's pricing?")
        SessionManager.append_conversation_message(self.session_id, "assistant", "Notion pricing starts at $8/mo.")

        history = SessionManager.get_conversation_history(self.session_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "What is Notion's pricing?")
        self.assertEqual(history[1]["role"], "assistant")

    def test_session_reset(self):
        SessionManager.set_active_document(self.session_id, {"file_name": "doc.txt"})
        SessionManager.append_conversation_message(self.session_id, "user", "Hello")

        SessionManager.clear_session(self.session_id)
        data = SessionManager.get_session_data(self.session_id)
        self.assertIsNone(data["active_document"])
        self.assertEqual(data["conversation_history"], [])
