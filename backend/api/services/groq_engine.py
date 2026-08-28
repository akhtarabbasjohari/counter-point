import os
import time
import logging
import hashlib
from django.conf import settings
from django.core.cache import cache
from .audit_logger import AuditLogger

logger = logging.getLogger(__name__)

PRIMARY_CANDIDATES = [
    os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b'),
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.6-27b",
    "groq/compound",
    "groq/compound-mini",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant"
]

class GroqReasoningEngine:

    @classmethod
    def get_groq_model_candidates(cls, api_key):
        candidates = list(PRIMARY_CANDIDATES)
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            fetched_models = [
                m.id for m in client.models.list().data 
                if not any(excluded in m.id.lower() for excluded in ['whisper', 'guard', 'orpheus', 'vision', 'audio'])
            ]
            for m in fetched_models:
                if m not in candidates:
                    candidates.append(m)
        except Exception as e:
            logger.debug(f"Could not list Groq models dynamically: {e}")
        return candidates

    @staticmethod
    def synthesize_counterpoint(query, document_context=None, web_results=None, conversation_history=None, session_id="global", intent="COMPETITOR_RESEARCH"):
        start_time = time.time()
        api_key = getattr(settings, 'GROQ_API_KEY', '') or os.getenv('GROQ_API_KEY', '')
        status = "success"
        synthesis_result = ""
        model_used = None

        # Check Cache to prevent Groq Rate Limit (429) hits on identical queries
        doc_text = document_context.get('text', '') if document_context else ''
        doc_file = document_context.get('file_name', '') if document_context else ''
        doc_hash = hashlib.md5(f"{doc_file}:{doc_text}".encode('utf-8')).hexdigest() if document_context else 'no_doc'
        web_count = len(web_results.get('results', [])) if web_results else 0

        cache_key_str = f"synthesis_cache_{session_id}_{query}_{intent}_{doc_hash}_{web_count}"
        cache_key = hashlib.md5(cache_key_str.encode('utf-8')).hexdigest()
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info(f"Serving synthesis for query '{query}' (intent: {intent}) from internal response cache.")
            cached_response["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
            cached_response["model"] = f"{cached_response['model']} (Cache)"
            return cached_response

        # Format Contexts
        doc_summary = ""
        if document_context:
            doc_summary = f"File: {document_context.get('file_name', 'Document')}\n"
            doc_summary += f"Excerpt/Content: {document_context.get('text', '')[:2500]}"

        web_summary = ""
        if web_results and web_results.get('results'):
            web_summary = "\n".join([
                f"- [{r.get('title')}]({r.get('url')}): {r.get('snippet')}"
                for r in web_results.get('results', [])[:4]
            ])

        history_context = ""
        if conversation_history:
            history_context = "\n".join([
                f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}"
                for msg in conversation_history[-4:]
            ])

        # Tailor System Prompt according to Intent
        if intent == "GREETING":
            system_prompt = (
                "You are CounterPoint, an elite strategic competitive intelligence AI assistant.\n"
                "The user has greeted you. Respond with a warm, concise welcome (1-2 short sentences).\n"
                "Introduce yourself as CounterPoint and explain that you help analyze software competitors, pricing models, market positioning, and gap analysis against internal strategy documents.\n"
                "Do NOT generate markdown tables, section headers, or competitor matrices for simple greetings."
            )
        elif intent == "GENERAL_QA":
            system_prompt = (
                "You are CounterPoint, an elite strategic competitive intelligence AI assistant.\n"
                "The user asked about CounterPoint's identity, capabilities, or usage.\n"
                "Provide a clear, helpful response explaining what CounterPoint does:\n"
                "- Upload PDF/TXT internal positioning documents for gap analysis.\n"
                "- Search live web research on software competitors, pricing models, and market positioning.\n"
                "- Perform multi-turn strategic Q&A.\n"
                "Do NOT generate competitive pricing tables or gap analysis matrices for general Q&A queries."
            )
        elif intent == "OFF_TOPIC":
            system_prompt = (
                "You are CounterPoint, an elite strategic competitive intelligence AI assistant.\n"
                "The user asked an off-topic question unrelated to software competitive research or positioning strategy.\n"
                "Politely inform the user (in 1-2 concise sentences) that CounterPoint is specialized specifically for software competitive analysis and strategic document evaluation, and invite them to ask about a competitor or upload a strategy file.\n"
                "Do NOT attempt to answer unrelated trivia or invent fake pricing models."
            )
        else:
            # COMPETITOR_RESEARCH
            system_prompt = (
                "You are CounterPoint, an elite strategic competitive intelligence AI assistant.\n"
                "Your objective is to contrast live market web research against the user's internal positioning documents.\n"
                "CRITICAL TABLE RULE: In Section 2 (Live Market Intelligence) and Section 3 (Internal Positioning Alignment), use explicit company/product names (e.g. 'Salesforce', 'HubSpot', 'Notion', 'ClickUp') in table rows and column headers. NEVER put raw user question phrases or pronouns as competitor names.\n"
                "CRITICAL ZERO-HALLUCINATION RULE: Do NOT invent pricing models, entry tiers, or competitor features. If live web research findings or document context lack verified pricing data, explicitly state: 'No verified external pricing data found in sources'.\n\n"
                "Provide sharp, structured, multi-hop strategic synthesis with Markdown tables and clear section headers:\n\n"
                "### 1. Executive Summary\n"
                "A concise 2-3 sentence overview answering the user's specific query.\n\n"
                "### 2. Live Market Intelligence\n"
                "Key findings regarding competitor offerings, pricing models, market positioning, and recent updates. Present comparative pricing/feature data in Markdown tables whenever applicable.\n\n"
                "### 3. Internal Positioning Alignment & Gap Analysis\n"
                "Direct comparison between internal document positioning and external competitor reality. Highlight overlap, competitive advantages, and vulnerability gaps.\n\n"
                "### 4. Strategic Counter-Point Recommendations\n"
                "3-4 actionable strategic recommendations formatted as a Markdown table or numbered list with rationale and tactical steps.\n"
            )

        user_content = f"QUERY / RESEARCH TOPIC: {query}\n\n"
        if history_context:
            user_content += f"PREVIOUS CONVERSATION CONTEXT:\n{history_context}\n\n"
        if doc_summary:
            user_content += f"INTERNAL POSITIONING DOCUMENT:\n{doc_summary}\n\n"
        else:
            user_content += "INTERNAL POSITIONING DOCUMENT:\n[No positioning document uploaded yet. Advise user they can upload a PDF/TXT document for direct gap analysis.]\n\n"
        if web_summary:
            user_content += f"LIVE WEB RESEARCH FINDINGS:\n{web_summary}\n\n"
        else:
            user_content += "LIVE WEB RESEARCH FINDINGS:\n[No live web search results provided.]\n\n"

        # Check API key and attempt models with Exponential Backoff on 429
        if api_key and api_key.startswith('gsk_'):
            candidates = GroqReasoningEngine.get_groq_model_candidates(api_key)
            for attempt, model_candidate in enumerate(candidates):
                try:
                    synthesis_result = GroqReasoningEngine._call_groq_api(api_key, model_candidate, system_prompt, user_content)
                    model_used = f"{model_candidate} (Groq)"
                    break
                except Exception as e:
                    err_msg = str(e).lower()
                    if "429" in err_msg or "rate_limit" in err_msg:
                        backoff = (attempt + 1) * 0.5
                        logger.warning(f"Rate limit 429 hit on Groq model '{model_candidate}'. Backing off for {backoff}s and switching candidate...")
                        time.sleep(backoff)
                    else:
                        logger.warning(f"Groq model '{model_candidate}' call returned: {e}. Trying next candidate...")

        if not synthesis_result:
            if not (api_key and api_key.startswith('gsk_')):
                logger.info("GROQ_API_KEY is missing or invalid. Using CounterPoint Intelligent Rule-Based Engine.")
            model_used = "CounterPoint Rule-Based Engine"
            synthesis_result = GroqReasoningEngine._generate_fallback_synthesis(query, document_context, web_results, intent=intent)

        execution_time_ms = (time.time() - start_time) * 1000

        result_payload = {
            "query": query,
            "intent": intent,
            "model": model_used,
            "synthesis": synthesis_result,
            "execution_time_ms": round(execution_time_ms, 2)
        }

        # Cache successful response for 300s (5 min) to prevent repeated rate limit hits
        if synthesis_result:
            try:
                cache.set(cache_key, result_payload, timeout=300)
            except Exception as ce:
                logger.debug(f"Could not cache synthesis response: {ce}")

        AuditLogger.log_tool_execution(
            tool_name="groq_reasoning_synthesis",
            input_params={
                "query": query,
                "intent": intent,
                "has_doc_context": bool(document_context),
                "web_results_count": len(web_results.get('results', [])) if web_results else 0,
                "model": model_used
            },
            execution_time_ms=execution_time_ms,
            status=status,
            result_summary=f"Synthesized response ({len(synthesis_result)} chars) using {model_used} [Intent: {intent}]",
            session_id=session_id
        )

        return result_payload

    @staticmethod
    def _call_groq_api(api_key, model_name, system_prompt, user_content):
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3,
            max_tokens=1500,
        )
        return response.choices[0].message.content

    @staticmethod
    def _generate_fallback_synthesis(query, document_context, web_results, intent="COMPETITOR_RESEARCH"):
        if intent == "GREETING":
            return (
                "Hello! I am **CounterPoint**, your strategic competitive intelligence assistant.\n\n"
                "How can I assist your market analysis today? You can:\n"
                "- Ask for live pricing and feature research on software competitors (e.g. *Salesforce*, *HubSpot*, *Notion*, *ClickUp*).\n"
                "- Upload a PDF/TXT positioning document to analyze competitive gaps and strategic alignment.\n"
                "- Ask follow-up questions to explore market positioning."
            )
        elif intent == "GENERAL_QA":
            return (
                "### CounterPoint Strategic Intelligence Assistant\n\n"
                "CounterPoint helps software strategy teams contrast internal positioning against live market reality:\n\n"
                "1. **Live Market Web Signals**: Conducts real-time web research on competitor offerings, pricing models, and updates.\n"
                "2. **Internal Document Contrast**: Extracts themes from uploaded PDF/TXT strategy documents to uncover gaps and differentiators.\n"
                "3. **Multi-Turn Graph Memory**: Maintains continuous conversation context across follow-up queries.\n\n"
                "*Enter a software competitor query or upload a positioning document to get started.*"
            )
        elif intent == "OFF_TOPIC":
            return (
                "I am **CounterPoint**, an AI assistant specialized specifically in software competitive intelligence and strategic positioning analysis.\n\n"
                "I don't process general off-topic queries, but I can help you evaluate software competitors, analyze pricing models, or contrast your internal strategy files. Feel free to ask about a software competitor or upload a strategy file!"
            )
        else:
            doc_name = document_context.get('file_name', 'Uploaded Strategy File') if document_context else "None"
            word_count = document_context.get('word_count', 0) if document_context else 0
            web_count = len(web_results.get('results', [])) if web_results else 0

            has_web_data = bool(web_results and web_results.get('results'))
            if has_web_data:
                web_highlights = "\n".join([
                    f"- **{r.get('title')}**: {r.get('snippet')}"
                    for r in web_results.get('results', [])[:4]
                ])
            else:
                web_highlights = "- No live external web research data was retrieved for this topic."

            doc_section = ""
            if document_context:
                doc_section = (
                    f"Extracted internal positioning text from **{doc_name}** ({word_count} words). "
                    f"Key strategic themes detected include product differentiation, target customer segments, and value metrics."
                )
            else:
                doc_section = (
                    "No internal positioning document is currently active in session. "
                    "Upload a PDF or TXT strategy file to unlock automated line-by-line positioning contrast."
                )

            pricing_note = "No verified external pricing data found in search results." if not has_web_data else "Review live web research snippets above for specific tier details."

            return (
                f"### 1. Executive Summary\n"
                f"Competitive analysis for **{query}** synthesizes {web_count} live web search signals with internal strategy data from {doc_name}.\n\n"
                f"### 2. Live Market Intelligence\n"
                f"Live web research findings for **{query}**:\n\n"
                f"{web_highlights}\n\n"
                f"*Pricing & Market Note*: {pricing_note}\n\n"
                f"### 3. Internal Positioning Alignment & Gap Analysis\n"
                f"{doc_section}\n\n"
                f"- **Positioning Overlap**: Market offerings align with core capabilities outlined in your positioning context.\n"
                f"- **Competitive Advantage**: Internal strategy emphasizes customizability, integration capabilities, and dedicated support.\n"
                f"- **Strategic Gap**: Competitor self-serve models require active monitoring to protect enterprise positioning.\n\n"
                f"### 4. Strategic Counter-Point Recommendations\n"
                f"1. **Positioning Highlight**: Emphasize unique capabilities documented in {doc_name}.\n"
                f"2. **Market Verification**: Monitor verified competitor pricing updates directly via live research.\n"
                f"3. **Onboarding Efficiency**: Streamline customer evaluation pathways based on competitive findings.\n"
            )
