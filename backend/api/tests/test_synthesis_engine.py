from django.test import TestCase
from api.services.synthesis_engine import MultiHopSynthesisEngine
from api.services.session_manager import SessionManager
from api.services.audit_logger import AuditLogger

class MultiHopSynthesisEngineTests(TestCase):
    def setUp(self):
        self.session_id = "synthesis_test_session"
        SessionManager.clear_session(self.session_id)

    def test_synthesis_without_doc_and_no_web(self):
        result = MultiHopSynthesisEngine.execute_synthesis(
            query="What is CounterPoint?",
            execute_web_search=False,
            session_id=self.session_id
        )

        self.assertEqual(result["query"], "What is CounterPoint?")
        self.assertIn("synthesis", result)
        self.assertFalse(result["document_context_used"])
        self.assertIsNone(result["document_name"])

        # Verify conversation history updated
        history = SessionManager.get_conversation_history(self.session_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["content"], "What is CounterPoint?")

    def test_synthesis_with_document_context(self):
        SessionManager.set_active_document(self.session_id, {
            "file_name": "internal_strategy.txt",
            "text": "CounterPoint is an automated competitive intelligence assistant.",
            "word_count": 8
        })

        result = MultiHopSynthesisEngine.execute_synthesis(
            query="Summarize our positioning advantage",
            execute_web_search=False,
            session_id=self.session_id
        )

        self.assertTrue(result["document_context_used"])
        self.assertEqual(result["document_name"], "internal_strategy.txt")

    def test_audit_logs_recorded(self):
        MultiHopSynthesisEngine.execute_synthesis(
            query="Audit log trace query",
            execute_web_search=False,
            session_id=self.session_id
        )

        logs = AuditLogger.get_logs(self.session_id)
        tool_names = [l["tool_name"] for l in logs]
        self.assertIn("session_memory_lookup", tool_names)
        self.assertIn("groq_reasoning_synthesis", tool_names)
        self.assertIn("multihop_synthesis_complete", tool_names)
