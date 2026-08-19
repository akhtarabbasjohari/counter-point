from django.test import TestCase
from api.services.query_rewriter import QueryRewriter
from api.services.synthesis_engine import MultiHopSynthesisEngine
from api.services.session_manager import SessionManager
from api.services.audit_logger import AuditLogger

class QueryRewriterTests(TestCase):
    def setUp(self):
        self.session_id = "rewriter_test_session"
        SessionManager.clear_session(self.session_id)

    def test_query_rewrite_without_history(self):
        query = "What is Salesforce primary revenue driver?"
        resolved = QueryRewriter.resolve_query(query, conversation_history=[], session_id=self.session_id)
        self.assertEqual(resolved, query)

    def test_query_rewrite_with_pronoun_followup(self):
        history = [
            {"role": "user", "content": "What is Salesforce primary revenue driver?"},
            {"role": "assistant", "content": "Salesforce primary revenue driver is Sales Cloud and Service Cloud SaaS subscriptions."}
        ]
        query = "How does our strategy compare to that?"
        resolved = QueryRewriter.resolve_query(query, conversation_history=history, session_id=self.session_id)
        
        # Verify that 'that' was replaced by 'Salesforce' or Salesforce is included in the resolved query
        self.assertIn("Salesforce", resolved)
        self.assertNotEqual(resolved, query)

    def test_synthesis_engine_invokes_query_rewriter(self):
        SessionManager.append_conversation_message(self.session_id, "user", "Tell me about HubSpot pricing tiers.")
        SessionManager.append_conversation_message(self.session_id, "assistant", "HubSpot offers Free, Starter, Professional, and Enterprise tiers.")

        result = MultiHopSynthesisEngine.execute_synthesis(
            query="How does our strategy compare to that?",
            execute_web_search=False,
            session_id=self.session_id
        )

        self.assertEqual(result["query"], "How does our strategy compare to that?")
        self.assertIn("HubSpot", result["resolved_query"])

        logs = AuditLogger.get_logs(self.session_id)
        tool_names = [l["tool_name"] for l in logs]
        self.assertIn("query_coreference_resolution", tool_names)
