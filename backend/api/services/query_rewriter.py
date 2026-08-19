import os
import re
import time
import logging
from django.conf import settings
from .audit_logger import AuditLogger

logger = logging.getLogger(__name__)

KNOWN_ENTITIES = [
    'Salesforce', 'HubSpot', 'Notion', 'ClickUp', 'Linear', 
    'Asana', 'Monday.com', 'Oracle', 'Microsoft Dynamics', 'SAP'
]

PRONOUN_PATTERNS = [
    r'\bthat\b', r'\bit\b', r'\bthem\b', r'\bthis\b', r'\btheir\b', r'\bthese\b', r'\bthose\b'
]

class QueryRewriter:

    @staticmethod
    def resolve_query(query, conversation_history=None, session_id="global"):
        start_time = time.time()
        raw_query = query.strip()
        resolved_query = raw_query
        is_rewritten = False

        if not conversation_history or len(conversation_history) == 0:
            return raw_query

        # Check if query contains any ambiguous pronouns or relative terms
        has_pronoun = any(re.search(pattern, raw_query, re.IGNORECASE) for pattern in PRONOUN_PATTERNS)
        
        # Extract recent competitor entities from history
        recent_entity = QueryRewriter._extract_recent_entity(conversation_history)

        if has_pronoun or (recent_entity and len(raw_query.split()) < 7):
            api_key = getattr(settings, 'GROQ_API_KEY', '') or os.getenv('GROQ_API_KEY', '')
            if api_key and api_key.startswith('gsk_'):
                try:
                    resolved_query = QueryRewriter._rewrite_with_llm(api_key, raw_query, conversation_history)
                    if resolved_query and resolved_query != raw_query and not resolved_query.startswith("<think>"):
                        is_rewritten = True
                except Exception as e:
                    logger.warning(f"LLM query rewriter encountered issue: {e}. Using rule-based coreference fallback.")

            if not is_rewritten and recent_entity:
                resolved_query = QueryRewriter._rewrite_with_rules(raw_query, recent_entity)
                is_rewritten = True

        execution_time_ms = (time.time() - start_time) * 1000

        if is_rewritten:
            AuditLogger.log_tool_execution(
                tool_name="query_coreference_resolution",
                input_params={
                    "raw_query": raw_query,
                    "recent_entity": recent_entity,
                    "history_turns": len(conversation_history)
                },
                execution_time_ms=execution_time_ms,
                status="success",
                result_summary=f"Resolved '{raw_query}' -> '{resolved_query}'",
                session_id=session_id
            )

        return resolved_query

    @staticmethod
    def _extract_recent_entity(conversation_history):
        for msg in reversed(conversation_history):
            content = msg.get('content', '')
            for entity in KNOWN_ENTITIES:
                if re.search(r'\b' + re.escape(entity) + r'\b', content, re.IGNORECASE):
                    return entity
        return None

    @staticmethod
    def _rewrite_with_rules(raw_query, entity):
        # Substitute vague pronouns with explicit entity name cleanly
        rewritten = raw_query
        for pattern in PRONOUN_PATTERNS:
            rewritten = re.sub(pattern, f"{entity}", rewritten, flags=re.IGNORECASE)
        if entity.lower() not in rewritten.lower():
            rewritten = f"Compare CounterPoint strategy with {entity} pricing and market positioning"
        return rewritten

    @staticmethod
    def _rewrite_with_llm(api_key, raw_query, conversation_history):
        from groq import Groq
        client = Groq(api_key=api_key)
        
        history_summary = "\n".join([
            f"{m.get('role', 'user').capitalize()}: {m.get('content', '')[:300]}"
            for m in conversation_history[-4:]
        ])

        system_prompt = (
            "You are a search query disambiguation assistant.\n"
            "Given recent conversation history and a user follow-up query, rewrite the follow-up into a single standalone explicit search query string.\n"
            "Replace ambiguous pronouns (like 'that', 'it', 'them', 'their') with the specific competitor or topic name from the conversation history.\n"
            "DO NOT include thinking tags like <think> or reasoning. Return ONLY the rewritten search query string."
        )

        user_prompt = f"CONVERSATION HISTORY:\n{history_summary}\n\nFOLLOW-UP QUERY: {raw_query}\n\nREWRITTEN STANDALONE QUERY:"

        models_to_try = ["qwen/qwen3.6-27b", "openai/gpt-oss-20b", "openai/gpt-oss-120b"]
        for model_name in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=60
                )
                result = response.choices[0].message.content.strip().strip('"\'')
                if "<think>" in result:
                    result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()
                if result:
                    return result
            except Exception:
                continue

        return raw_query
