import time
import logging
from .session_manager import SessionManager
from .query_rewriter import QueryRewriter
from .web_search import WebSearchService
from .groq_engine import GroqReasoningEngine
from .audit_logger import AuditLogger

logger = logging.getLogger(__name__)

class MultiHopSynthesisEngine:
    """
    Orchestrates continuous multi-turn synthesis by retrieving session memory (positioning doc + context),
    resolving multi-turn coreference ambiguities, executing targeted live web research tools,
    and running Groq LLM synthesis.
    """

    @classmethod
    def execute_synthesis(cls, query, execute_web_search=True, session_id="global"):
        start_time = time.time()
        
        # 1. Audit Log: Memory Lookup
        memory_start = time.time()
        document_context = SessionManager.get_active_document(session_id)
        conversation_history = SessionManager.get_conversation_history(session_id)
        memory_duration = (time.time() - memory_start) * 1000

        AuditLogger.log_tool_execution(
            tool_name="session_memory_lookup",
            input_params={"session_id": session_id},
            execution_time_ms=memory_duration,
            status="success",
            result_summary=f"Retrieved doc: {document_context.get('file_name') if document_context else 'None'}, history: {len(conversation_history)} items",
            session_id=session_id
        )

        # 2. Coreference Resolution & Disambiguation
        search_query = QueryRewriter.resolve_query(
            query=query,
            conversation_history=conversation_history,
            session_id=session_id
        )

        # 3. Tool Execution: Web Search using Resolved Standalone Query
        web_results = None
        if execute_web_search:
            web_results = WebSearchService.search_competitor(query=search_query, max_results=5, session_id=session_id)

        # 4. Reasoning & Synthesis: Groq LLM Engine
        synthesis_response = GroqReasoningEngine.synthesize_counterpoint(
            query=search_query,
            document_context=document_context,
            web_results=web_results,
            conversation_history=conversation_history,
            session_id=session_id
        )

        # 5. Update Conversation Memory
        SessionManager.append_conversation_message(session_id, "user", query)
        SessionManager.append_conversation_message(session_id, "assistant", synthesis_response["synthesis"])

        total_execution_time_ms = (time.time() - start_time) * 1000

        AuditLogger.log_tool_execution(
            tool_name="multihop_synthesis_complete",
            input_params={
                "query": query,
                "resolved_query": search_query,
                "session_id": session_id,
                "execute_web_search": execute_web_search
            },
            execution_time_ms=total_execution_time_ms,
            status="success",
            result_summary=f"Multi-hop synthesis finished in {round(total_execution_time_ms, 2)}ms",
            session_id=session_id
        )

        return {
            "query": query,
            "resolved_query": search_query,
            "synthesis": synthesis_response["synthesis"],
            "model_used": synthesis_response["model"],
            "execution_time_ms": round(total_execution_time_ms, 2),
            "document_context_used": bool(document_context),
            "document_name": document_context.get("file_name") if document_context else None,
            "web_sources": web_results.get("results", []) if web_results else [],
            "recent_audit_logs": AuditLogger.get_logs(session_id)[:10]
        }
