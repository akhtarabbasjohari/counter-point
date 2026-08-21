import time
import logging
from .session_manager import SessionManager
from .langgraph_memory_engine import LangGraphEngine
from .audit_logger import AuditLogger

logger = logging.getLogger(__name__)

class MultiHopSynthesisEngine:
    """
    Orchestrates continuous multi-turn synthesis using the LangGraph stateful agent memory engine.
    Applies graph state checkpoints (`MemorySaver`), dynamic entity resolution, targeted web research,
    and Groq LLM synthesis.
    """

    @classmethod
    def execute_synthesis(cls, query, execute_web_search=True, session_id="global"):
        # Route execution through LangGraph stateful memory pipeline
        return LangGraphEngine.execute_graph_synthesis(
            query=query,
            session_id=session_id,
            execute_web_search=execute_web_search
        )
