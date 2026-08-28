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
        self.assertTrue(any(t in tool_names for t in ["langgraph_query_analysis", "query_coreference_resolution"]))

    def test_classify_intent_greetings(self):
        self.assertEqual(QueryRewriter.classify_intent("hi"), "GREETING")
        self.assertEqual(QueryRewriter.classify_intent("hello there!"), "GREETING")
        self.assertEqual(QueryRewriter.classify_intent("Good morning"), "GREETING")
        self.assertEqual(QueryRewriter.classify_intent("thanks"), "GREETING")

    def test_classify_intent_general_qa(self):
        self.assertEqual(QueryRewriter.classify_intent("what can you do?"), "GENERAL_QA")
        self.assertEqual(QueryRewriter.classify_intent("who are you"), "GENERAL_QA")
        self.assertEqual(QueryRewriter.classify_intent("how to use counterpoint"), "GENERAL_QA")

    def test_classify_intent_off_topic(self):
        self.assertEqual(QueryRewriter.classify_intent("what is the capital of France?"), "OFF_TOPIC")
        self.assertEqual(QueryRewriter.classify_intent("tell me a joke"), "OFF_TOPIC")
        self.assertEqual(QueryRewriter.classify_intent("solve 2+2"), "OFF_TOPIC")

    def test_classify_intent_competitor_research(self):
        self.assertEqual(QueryRewriter.classify_intent("Notion vs ClickUp pricing"), "COMPETITOR_RESEARCH")
        self.assertEqual(QueryRewriter.classify_intent("Salesforce features"), "COMPETITOR_RESEARCH")
        self.assertEqual(QueryRewriter.classify_intent("analyze positioning strategy document"), "COMPETITOR_RESEARCH")

