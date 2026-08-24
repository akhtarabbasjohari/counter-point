import uuid
import logging
from django.core.cache import cache
from .audit_logger import AuditLogger

logger = logging.getLogger(__name__)

SESSION_TIMEOUT_SECONDS = 86400  # 24 hours

class SessionManager:
    """
    Manages continuous session state (document context, conversation history, search cache)
    backed by Django's cache framework (`django.core.cache`).
    """

    @staticmethod
    def _cache_key(session_id):
        return f"cp_session:{session_id}"

    @classmethod
    def get_or_create_session_id(cls, request=None, header_session_id=None):
        """
        Extract session_id from header (X-Session-ID), request body, request.session, or generate a new UUID.
        """
        session_id = header_session_id
        if not session_id and request:
            # 1. Custom Header
            session_id = request.headers.get('X-Session-ID') or (getattr(request, 'META', {}).get('HTTP_X_SESSION_ID') if hasattr(request, 'META') else None)
            # 2. JSON Body Parameter
            if not session_id and hasattr(request, 'data') and isinstance(request.data, dict):
                session_id = request.data.get('session_id')
            # 3. Standard Django Session
            if not session_id and hasattr(request, 'session'):
                if not request.session.session_key:
                    request.session.create()
                session_id = request.session.session_key

        if not session_id:
            session_id = str(uuid.uuid4())

        return session_id

    @classmethod
    def get_session_data(cls, session_id):
        key = cls._cache_key(session_id)
        data = cache.get(key)
        if data is None:
            data = {
                "active_document": None,
                "conversation_history": [],
                "created_at": uuid.uuid4().hex
            }
            cache.set(key, data, SESSION_TIMEOUT_SECONDS)
        return data

    @classmethod
    def save_session_data(cls, session_id, data):
        key = cls._cache_key(session_id)
        cache.set(key, data, SESSION_TIMEOUT_SECONDS)

    @classmethod
    def set_active_document(cls, session_id, document_data):
        """
        Store uploaded positioning document metadata & text into session memory.
        """
        session = cls.get_session_data(session_id)
        session["active_document"] = document_data
        cls.save_session_data(session_id, session)

        AuditLogger.log_tool_execution(
            tool_name="session_memory_set_document",
            input_params={"file_name": document_data.get("file_name") if document_data else None},
            execution_time_ms=1.0,
            status="success",
            result_summary="Active document set in session memory cache",
            session_id=session_id
        )
        return session["active_document"]

    @classmethod
    def get_active_document(cls, session_id):
        session = cls.get_session_data(session_id)
        return session.get("active_document")

    @classmethod
    def clear_active_document(cls, session_id):
        session = cls.get_session_data(session_id)
        doc_name = session.get("active_document", {}).get("file_name") if session.get("active_document") else None
        session["active_document"] = None
        cls.save_session_data(session_id, session)

        AuditLogger.log_tool_execution(
            tool_name="session_memory_clear_document",
            input_params={"cleared_doc": doc_name},
            execution_time_ms=1.0,
            status="success",
            result_summary="Active document cleared from session memory cache",
            session_id=session_id
        )

    @classmethod
    def append_conversation_message(cls, session_id, role, content):
        """
        Append user/assistant message to continuous conversation history.
        """
        session = cls.get_session_data(session_id)
        history = session.get("conversation_history", [])
        history.append({
            "role": role,
            "content": content
        })
        # Limit conversation history to last 20 messages
        if len(history) > 20:
            history = history[-20:]
        session["conversation_history"] = history
        cls.save_session_data(session_id, session)
        return history

    @classmethod
    def get_conversation_history(cls, session_id):
        session = cls.get_session_data(session_id)
        return session.get("conversation_history", [])

    @classmethod
    def clear_session(cls, session_id):
        key = cls._cache_key(session_id)
        cache.delete(key)
        AuditLogger.clear_logs(session_id)
        AuditLogger.log_tool_execution(
            tool_name="session_memory_reset",
            input_params={"session_id": session_id},
            execution_time_ms=1.0,
            status="success",
            result_summary="Session memory cache and logs cleared",
            session_id=session_id
        )
