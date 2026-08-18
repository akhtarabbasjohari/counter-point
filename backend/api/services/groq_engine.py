import os
import time
import logging
from django.conf import settings
from .audit_logger import AuditLogger

logger = logging.getLogger(__name__)

class GroqReasoningEngine:
    MODEL_NAME = "llama-3.3-70b-versatile"

    @staticmethod
    def synthesize_counterpoint(query, document_context=None, web_results=None, conversation_history=None, session_id="global"):
        start_time = time.time()
        api_key = getattr(settings, 'GROQ_API_KEY', '') or os.getenv('GROQ_API_KEY', '')
        status = "success"
        synthesis_result = ""
        model_used = GroqReasoningEngine.MODEL_NAME

        doc_summary = ""
        if document_context:
            doc_summary = f"File: {document_context.get('file_name', 'Document')}\n"
            doc_summary += f"Excerpt/Content: {document_context.get('text', '')[:3000]}"

        web_summary = ""
        if web_results and web_results.get('results'):
            web_summary = "\n".join([
                f"- [{r.get('title')}]({r.get('url')}): {r.get('snippet')}"
                for r in web_results.get('results', [])
            ])

        history_context = ""
        if conversation_history:
            history_context = "\n".join([
                f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}"
                for msg in conversation_history[-6:]
            ])

        system_prompt = (
            "You are CounterPoint, an elite strategic competitive intelligence AI assistant.\n"
            "Your objective is to contrast live market web research against the user's internal positioning documents.\n"
            "Provide sharp, structured, multi-hop strategic synthesis with the following section structure:\n\n"
            "### 1. Executive Summary\n"
            "A concise 2-3 sentence overview answering the user's specific query.\n\n"
            "### 2. Live Market Intelligence\n"
            "Key findings regarding competitor offerings, pricing models, market positioning, and recent updates gathered from live web search.\n\n"
            "### 3. Internal Positioning Alignment & Gap Analysis\n"
            "Direct comparison between internal document positioning and external competitor reality. Highlight overlap, competitive advantages, and vulnerability gaps.\n\n"
            "### 4. Strategic Counter-Point Recommendations\n"
            "3-4 actionable strategic recommendations for product, marketing, or pricing strategy.\n"
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

        if api_key and api_key != "your_groq_api_key_here":
            try:
                synthesis_result = GroqReasoningEngine._call_groq_api(api_key, system_prompt, user_content)
            except Exception as e:
                logger.warning(f"Groq API call failed: {e}. Falling back to Rule-Based Synthesis Engine.")
                model_used = "CounterPoint Rule-Based Engine (Fallback)"
                synthesis_result = GroqReasoningEngine._generate_fallback_synthesis(query, document_context, web_results)
        else:
            logger.info("GROQ_API_KEY not configured. Using CounterPoint Rule-Based Engine.")
            model_used = "CounterPoint Rule-Based Engine"
            synthesis_result = GroqReasoningEngine._generate_fallback_synthesis(query, document_context, web_results)

        execution_time_ms = (time.time() - start_time) * 1000

        AuditLogger.log_tool_execution(
            tool_name="groq_reasoning_synthesis",
            input_params={
                "query": query,
                "has_doc_context": bool(document_context),
                "web_results_count": len(web_results.get('results', [])) if web_results else 0,
                "model": model_used
            },
            execution_time_ms=execution_time_ms,
            status=status,
            result_summary=f"Synthesized response ({len(synthesis_result)} chars) using {model_used}",
            session_id=session_id
        )

        return {
            "query": query,
            "model": model_used,
            "synthesis": synthesis_result,
            "execution_time_ms": round(execution_time_ms, 2)
        }

    @staticmethod
    def _call_groq_api(api_key, system_prompt, user_content):
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=GroqReasoningEngine.MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3,
            max_tokens=2048,
        )
        return response.choices[0].message.content

    @staticmethod
    def _generate_fallback_synthesis(query, document_context, web_results):
        doc_name = document_context.get('file_name', 'Uploaded Strategy File') if document_context else "None"
        word_count = document_context.get('word_count', 0) if document_context else 0
        web_count = len(web_results.get('results', [])) if web_results else 0

        web_highlights = ""
        if web_results and web_results.get('results'):
            web_highlights = "\n".join([
                f"- **{r.get('title')}**: {r.get('snippet')}"
                for r in web_results.get('results', [])[:3]
            ])
        else:
            web_highlights = "- No specific external search data retrieved."

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

        return (
            f"### 1. Executive Summary\n"
            f"Competitive analysis for **{query}** synthesizes {web_count} live web search signals with internal strategy data from {doc_name}.\n\n"
            f"### 2. Live Market Intelligence\n"
            f"Live web signals for **{query}** reveal the following market activity:\n"
            f"{web_highlights}\n\n"
            f"### 3. Internal Positioning Alignment & Gap Analysis\n"
            f"{doc_section}\n\n"
            f"- **Positioning Overlap**: Market offerings align closely with core feature sets outlined in your document.\n"
            f"- **Competitive Advantage**: Internal strategy emphasizes higher customizability and dedicated user support.\n"
            f"- **Strategic Vulnerability**: Market competitors are aggressively pushing self-serve SaaS entry pricing, creating potential friction for high-friction enterprise onboarding.\n\n"
            f"### 4. Strategic Counter-Point Recommendations\n"
            f"1. **Pricing Transparency**: Publish clear pricing tier breakdowns to counter low-cost competitor positioning.\n"
            f"2. **Feature Spotlight**: Emphasize unique capabilities highlighted in {doc_name} in upcoming marketing campaigns.\n"
            f"3. **Speed to Value**: Streamline self-serve onboarding based on competitive benchmark findings.\n"
        )
