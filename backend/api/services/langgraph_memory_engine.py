import time
import logging
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .session_manager import SessionManager
from .query_rewriter import QueryRewriter
from .web_search import WebSearchService
from .groq_engine import GroqReasoningEngine
from .audit_logger import AuditLogger

logger = logging.getLogger(__name__)

class AgentMemoryState(TypedDict):
    session_id: str
    raw_query: str
    resolved_query: str
    active_entities: List[str]
    messages: List[Dict[str, Any]]
    document_context: Optional[Dict[str, Any]]
    web_research_results: Optional[Dict[str, Any]]
    final_synthesis: str
    model_used: str
    execute_web_search: bool

class LangGraphEngine:
    _compiled_app = None
    _checkpointer = MemorySaver()

    @classmethod
    def get_app(cls):
        if cls._compiled_app is None:
            builder = StateGraph(AgentMemoryState)

            builder.add_node("query_analysis", cls._query_analysis_node)
            builder.add_node("state_memory_lookup", cls._state_memory_lookup_node)
            builder.add_node("web_research", cls._web_research_node)
            builder.add_node("strategy_synthesis", cls._strategy_synthesis_node)

            builder.add_edge(START, "query_analysis")
            builder.add_edge("query_analysis", "state_memory_lookup")
            builder.add_edge("state_memory_lookup", "web_research")
            builder.add_edge("web_research", "strategy_synthesis")
            builder.add_edge("strategy_synthesis", END)

            cls._compiled_app = builder.compile(checkpointer=cls._checkpointer)
        return cls._compiled_app

    @staticmethod
    def _query_analysis_node(state: AgentMemoryState) -> Dict[str, Any]:
        start = time.time()
        session_id = state.get("session_id", "global")
        raw_query = state.get("raw_query", "")
        history = state.get("messages", [])

        resolved_query = QueryRewriter.resolve_query(raw_query, conversation_history=history, session_id=session_id)

        extracted_entity = QueryRewriter._extract_recent_entity(history) if history else None
        active_entities = list(state.get("active_entities", []))
        if extracted_entity and extracted_entity not in active_entities:
            active_entities.append(extracted_entity)

        duration = (time.time() - start) * 1000
        AuditLogger.log_tool_execution(
            tool_name="langgraph_query_analysis",
            input_params={"raw_query": raw_query, "active_entities": active_entities},
            execution_time_ms=duration,
            status="success",
            result_summary=f"Analyzed query into resolved topic: '{resolved_query}'",
            session_id=session_id
        )

        return {
            "resolved_query": resolved_query,
            "active_entities": active_entities
        }

    @staticmethod
    def _state_memory_lookup_node(state: AgentMemoryState) -> Dict[str, Any]:
        start = time.time()
        session_id = state.get("session_id", "global")
        doc_context = SessionManager.get_active_document(session_id)
        history = SessionManager.get_conversation_history(session_id)
        duration = (time.time() - start) * 1000

        AuditLogger.log_tool_execution(
            tool_name="langgraph_state_lookup",
            input_params={"session_id": session_id, "has_doc": bool(doc_context), "history_count": len(history)},
            execution_time_ms=duration,
            status="success",
            result_summary=f"Graph memory state checkpoint synced (doc: {doc_context.get('file_name') if doc_context else 'None'})",
            session_id=session_id
        )
        return {
            "document_context": doc_context,
            "messages": history
        }

    @staticmethod
    def _web_research_node(state: AgentMemoryState) -> Dict[str, Any]:
        start = time.time()
        session_id = state.get("session_id", "global")
        execute_web = state.get("execute_web_search", True)
        web_results = None

        if execute_web:
            search_topic = state.get("resolved_query", state.get("raw_query"))
            web_results = WebSearchService.search_competitor(query=search_topic, max_results=5, session_id=session_id)

        duration = (time.time() - start) * 1000

        AuditLogger.log_tool_execution(
            tool_name="langgraph_web_research",
            input_params={"execute_web_search": execute_web},
            execution_time_ms=duration,
            status="success",
            result_summary=f"Retrieved {len(web_results.get('results', [])) if web_results else 0} web sources",
            session_id=session_id
        )
        return {"web_research_results": web_results}

    @staticmethod
    def _strategy_synthesis_node(state: AgentMemoryState) -> Dict[str, Any]:
        start = time.time()
        session_id = state.get("session_id", "global")
        query = state.get("resolved_query", state.get("raw_query"))
        doc_context = state.get("document_context")
        web_results = state.get("web_research_results")
        history = state.get("messages", [])

        synthesis_response = GroqReasoningEngine.synthesize_counterpoint(
            query=query,
            document_context=doc_context,
            web_results=web_results,
            conversation_history=history,
            session_id=session_id
        )

        duration = (time.time() - start) * 1000
        AuditLogger.log_tool_execution(
            tool_name="langgraph_synthesis",
            input_params={"model": synthesis_response["model"]},
            execution_time_ms=duration,
            status="success",
            result_summary=f"Synthesized counterpoint using {synthesis_response['model']}",
            session_id=session_id
        )

        return {
            "final_synthesis": synthesis_response["synthesis"],
            "model_used": synthesis_response["model"]
        }

    @classmethod
    def execute_graph_synthesis(cls, query: str, session_id: str = "global", execute_web_search: bool = True) -> Dict[str, Any]:
        start_time = time.time()
        app = cls.get_app()

        document_context = SessionManager.get_active_document(session_id)
        conversation_history = SessionManager.get_conversation_history(session_id)

        initial_state: AgentMemoryState = {
            "session_id": session_id,
            "raw_query": query,
            "resolved_query": query,
            "active_entities": [],
            "messages": conversation_history,
            "document_context": document_context,
            "web_research_results": None,
            "final_synthesis": "",
            "model_used": "",
            "execute_web_search": execute_web_search
        }

        config = {"configurable": {"thread_id": session_id}}
        final_state = app.invoke(initial_state, config=config)

        # Update Session Memory
        SessionManager.append_conversation_message(session_id, "user", query)
        SessionManager.append_conversation_message(session_id, "assistant", final_state["final_synthesis"])

        total_duration = (time.time() - start_time) * 1000

        AuditLogger.log_tool_execution(
            tool_name="langgraph_execution_complete",
            input_params={"session_id": session_id, "raw_query": query},
            execution_time_ms=total_duration,
            status="success",
            result_summary=f"LangGraph stateful memory pipeline finished in {round(total_duration, 2)}ms",
            session_id=session_id
        )

        return {
            "query": query,
            "resolved_query": final_state["resolved_query"],
            "synthesis": final_state["final_synthesis"],
            "model_used": final_state["model_used"],
            "execution_time_ms": round(total_duration, 2),
            "document_context_used": bool(document_context),
            "document_name": document_context.get("file_name") if document_context else None,
            "web_sources": final_state.get("web_research_results", {}).get("results", []) if final_state.get("web_research_results") else [],
            "recent_audit_logs": AuditLogger.get_logs(session_id)[:10]
        }
