from django.test import TestCase
from api.services.langgraph_memory_engine import LangGraphEngine
from api.services.session_manager import SessionManager
from api.services.audit_logger import AuditLogger

class LangGraphMemoryEngineTests(TestCase):
    def setUp(self):
        self.session_id = "langgraph_test_session"
        SessionManager.clear_session(self.session_id)

    def test_langgraph_state_transition_and_execution(self):
        result = LangGraphEngine.execute_graph_synthesis(
            query="What is Salesforce's primary revenue driver?",
            session_id=self.session_id,
            execute_web_search=False
        )

        self.assertEqual(result["query"], "What is Salesforce's primary revenue driver?")
        self.assertIn("synthesis", result)
        self.assertIn("resolved_query", result)

        # Check audit log entries for LangGraph nodes
        logs = AuditLogger.get_logs(self.session_id)
        tool_names = [l["tool_name"] for l in logs]
        self.assertIn("langgraph_query_analysis", tool_names)
        self.assertIn("langgraph_state_lookup", tool_names)
        self.assertIn("langgraph_synthesis", tool_names)

    def test_langgraph_multi_turn_memory(self):
        # Turn 1
        LangGraphEngine.execute_graph_synthesis(
            query="Tell me about Notion pricing.",
            session_id=self.session_id,
            execute_web_search=False
        )

        # Turn 2: Relative pronoun follow-up
        result_turn2 = LangGraphEngine.execute_graph_synthesis(
            query="How does our strategy compare to that?",
            session_id=self.session_id,
            execute_web_search=False
        )

        self.assertIn("Notion", result_turn2["resolved_query"])

        history = SessionManager.get_conversation_history(self.session_id)
        self.assertEqual(len(history), 4) # 2 user + 2 assistant messages

    def test_greeting_intent_does_not_hallucinate_matrices(self):
        result = LangGraphEngine.execute_graph_synthesis(
            query="hi",
            session_id=self.session_id,
            execute_web_search=True
        )

        self.assertEqual(result["intent"], "GREETING")
        self.assertIn("Hello", result["synthesis"])
        # Ensure it does NOT contain synthetic pricing tables or matrix headers
        self.assertNotIn("Self-serve low tier ($5-$15/mo)", result["synthesis"])
        self.assertNotIn("### 1. Executive Summary", result["synthesis"])

    def test_off_topic_intent_does_not_hallucinate_pricing(self):
        result = LangGraphEngine.execute_graph_synthesis(
            query="what is the capital of France?",
            session_id=self.session_id,
            execute_web_search=True
        )

        self.assertEqual(result["intent"], "OFF_TOPIC")
        self.assertIn("software competitive intelligence", result["synthesis"])
        self.assertNotIn("Self-serve low tier ($5-$15/mo)", result["synthesis"])
        self.assertNotIn("### 1. Executive Summary", result["synthesis"])

    def test_competitor_research_zero_hallucination_fallback(self):
        result = LangGraphEngine.execute_graph_synthesis(
            query="Salesforce enterprise tier pricing",
            session_id=self.session_id,
            execute_web_search=False
        )

        self.assertEqual(result["intent"], "COMPETITOR_RESEARCH")
        self.assertNotIn("Self-serve low tier ($5-$15/mo)", result["synthesis"])
        self.assertIn("No verified external pricing data found", result["synthesis"])

