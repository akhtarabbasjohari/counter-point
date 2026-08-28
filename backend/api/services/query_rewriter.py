import os
import re
import time
import logging
from django.conf import settings
from .audit_logger import AuditLogger

logger = logging.getLogger(__name__)

KNOWN_ENTITIES = [
    'Salesforce', 'HubSpot', 'Notion', 'ClickUp', 'Linear', 
    'Asana', 'Monday.com', 'Oracle', 'Microsoft Dynamics', 'SAP',
    'Datadog', 'Snowflake', 'Stripe', 'Figma', 'Slack', 'Zoom',
    'Jira', 'Confluence', 'Trello', 'Zendesk', 'Intercom', 'Databricks',
    'Workday', 'ServiceNow', 'GitHub', 'GitLab', 'Postman', 'Sentry'
]

PRONOUN_PATTERNS = [
    r'\bthat\b', r'\bit\b', r'\bthem\b', r'\bthis\b', r'\btheir\b', r'\bthese\b', r'\bthose\b'
]

class QueryRewriter:

    @staticmethod
    def classify_intent(query):
        """
        Classifies incoming query intent into one of:
        - GREETING: Greetings, pleasantries, single-word hellos/thanks/goodbyes.
        - GENERAL_QA: Questions asking about CounterPoint's identity, capabilities, or usage.
        - OFF_TOPIC: Questions completely unrelated to software, business software, or competitive strategy.
        - COMPETITOR_RESEARCH: Authentic competitive intelligence, pricing, positioning, or document contrast requests.
        """
        if not query or not str(query).strip():
            return "GREETING"

        clean_query = str(query).strip().lower()
        words = clean_query.split()

        # 1. Check GREETING
        greeting_pattern = r'^(hi|hello|hey|greetings|howdy|sup|good\s+(morning|afternoon|evening)|thank\s+you|thanks|bye|goodbye|hi\s+there|hello\s+there)[\s!\.,?]*$'
        if re.match(greeting_pattern, clean_query):
            return "GREETING"

        if len(words) <= 3 and any(w in {"hi", "hello", "hey", "greetings", "howdy", "sup", "thanks"} for w in words):
            # Verify if there is a specific competitor name attached e.g. "hi salesforce"
            if not any(entity.lower() in clean_query for entity in KNOWN_ENTITIES):
                return "GREETING"

        # 2. Check GENERAL_QA
        general_qa_phrases = [
            "counterpoint", "what can you do", "who are you", "what is this", "how to use",
            "how does this work", "help me use", "what are your features", "how do i upload",
            "what is your purpose", "how do you work", "what do you do"
        ]
        if any(phrase in clean_query for phrase in general_qa_phrases):
            return "GENERAL_QA"

        # 3. Check COMPETITOR_RESEARCH - Known Entities
        for entity in KNOWN_ENTITIES:
            if re.search(r'\b' + re.escape(entity) + r'\b', clean_query, re.IGNORECASE):
                return "COMPETITOR_RESEARCH"

        # 4. Check COMPETITOR_RESEARCH - Domain Keywords
        competitor_keywords = {
            "pricing", "price", "cost", "competitor", "competitors", "versus", "vs",
            "features", "positioning", "market", "alternative", "alternatives", "strategy",
            "gap", "contrast", "saas", "tier", "subscription", "crm", "erp", "software",
            "platform", "product", "analytics", "document", "pdf", "txt", "upload",
            "analysis", "compare", "comparison", "offering", "offerings", "benchmark",
            "vendor", "tool", "integration", "enterprise", "smb", "onboarding"
        }
        if any(w in competitor_keywords for w in words):
            return "COMPETITOR_RESEARCH"

        # 5. Check OFF_TOPIC indicators
        off_topic_indicators = [
            "capital of", "weather", "tell me a joke", "write a poem", "solve",
            "recipe", "who won", "movie", "song", "president", "distance to", "translate"
        ]
        if any(ind in clean_query for ind in off_topic_indicators):
            return "OFF_TOPIC"

        # Check proper noun / capitalization in original query (e.g. company names outside KNOWN_ENTITIES)
        capitalized_words = re.findall(r'\b[A-Z][a-zA-Z0-9\.\-]{2,}\b', str(query))
        ignored_caps = {"What", "How", "Why", "When", "Who", "Where", "Can", "Could", "Should", "Would", "Tell", "Give", "Show", "Is", "Are", "The", "This", "That", "Please", "France", "Germany", "Paris", "London"}
        meaningful_caps = [c for c in capitalized_words if c not in ignored_caps]
        if len(meaningful_caps) > 0:
            return "COMPETITOR_RESEARCH"

        if len(words) <= 4 and not any(w in competitor_keywords for w in words):
            return "OFF_TOPIC"

        return "COMPETITOR_RESEARCH"

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
        ignored_terms = {
            'CounterPoint', 'Executive', 'Summary', 'Live', 'Market', 'Intelligence',
            'Internal', 'Positioning', 'Alignment', 'Strategic', 'Recommendations',
            'Section', 'File', 'Document', 'User', 'Assistant', 'Query', 'Topic',
            'Pricing', 'Features', 'Offerings', 'Compare', 'What', 'How', 'Does', 'Which',
            'Overview', 'Analysis', 'Report', 'SaaS', 'API', 'SMBs', 'Tiered',
            'You', 'They', 'Them', 'Their', 'These', 'Those', 'This', 'That', 'Your', 'Our', 'We'
        }
        for msg in reversed(conversation_history):
            content = msg.get('content', '')
            # 1. Check known entities list
            for entity in KNOWN_ENTITIES:
                if re.search(r'\b' + re.escape(entity) + r'\b', content, re.IGNORECASE):
                    return entity

            # 2. Dynamic proper-noun extraction fallback for entities outside KNOWN_ENTITIES
            candidates = re.findall(r'\b[A-Z][a-zA-Z0-9\.\-]{2,}\b', content)
            for candidate in candidates:
                if candidate not in ignored_terms and len(candidate) > 2:
                    return candidate
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
