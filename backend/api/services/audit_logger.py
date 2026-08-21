import datetime
import logging
import threading
import time

logger = logging.getLogger('counterpoint.audit')
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] AUDIT [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# In-memory session log storage with thread lock
SESSION_AUDIT_LOGS = {}
LOG_LOCK = threading.Lock()

class AuditLogger:
    @staticmethod
    def get_logs(session_id="global"):
        with LOG_LOCK:
            return list(SESSION_AUDIT_LOGS.get(session_id, []))

    @staticmethod
    def clear_logs(session_id="global"):
        with LOG_LOCK:
            if session_id in SESSION_AUDIT_LOGS:
                SESSION_AUDIT_LOGS[session_id] = []

    @staticmethod
    def log_tool_execution(tool_name, input_params, execution_time_ms, status="SUCCESS", result_summary="", error_message=None, session_id="global"):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Sanitize input params to avoid leaking full document contents in brief log view
        sanitized_params = {}
        for k, v in (input_params or {}).items():
            if isinstance(v, str) and len(v) > 200:
                sanitized_params[k] = v[:200] + "... (truncated)"
            else:
                sanitized_params[k] = v

        status_str = status.upper() if isinstance(status, str) else "SUCCESS"
        if status_str == "ERROR" and not error_message:
            error_message = str(result_summary)

        entry = {
            "timestamp": timestamp,
            "tool_name": tool_name,
            "input_params": sanitized_params,
            "execution_time_ms": round(execution_time_ms, 2),
            "status": status_str,
            "result_summary": str(result_summary)[:300] if result_summary else "",
            "error_message": error_message
        }

        with LOG_LOCK:
            if session_id not in SESSION_AUDIT_LOGS:
                SESSION_AUDIT_LOGS[session_id] = []

            SESSION_AUDIT_LOGS[session_id].insert(0, entry)  # latest first
            
            # Keep maximum 100 log entries per session
            if len(SESSION_AUDIT_LOGS[session_id]) > 100:
                SESSION_AUDIT_LOGS[session_id] = SESSION_AUDIT_LOGS[session_id][:100]

        logger.info(f"Tool: {tool_name} | Status: {status_str} | Duration: {entry['execution_time_ms']}ms | Params: {sanitized_params}")
        return entry


class audit_tool:
    """Decorator / Context manager to measure execution time and record audit log."""
    def __init__(self, tool_name, get_session_id=None):
        self.tool_name = tool_name
        self.get_session_id = get_session_id

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            session_id = kwargs.get('session_id', 'global')
            status = "success"
            result_summary = ""
            try:
                result = func(*args, **kwargs)
                if isinstance(result, dict) and "summary" in result:
                    result_summary = result["summary"]
                elif isinstance(result, str):
                    result_summary = result[:200]
                else:
                    result_summary = str(result)[:200]
                return result
            except Exception as e:
                status = "error"
                result_summary = str(e)
                raise e
            finally:
                elapsed_ms = (time.time() - start_time) * 1000
                input_params = {k: v for k, v in kwargs.items() if k != 'session_id'}
                AuditLogger.log_tool_execution(
                    tool_name=self.tool_name,
                    input_params=input_params,
                    execution_time_ms=elapsed_ms,
                    status=status,
                    result_summary=result_summary,
                    session_id=session_id
                )
        return wrapper
