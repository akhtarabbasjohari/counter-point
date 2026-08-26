import time
import logging
from .audit_logger import AuditLogger

logger = logging.getLogger(__name__)

DISALLOWED_DOMAINS = [
    'youtube.com',
    'youtu.be',
    'facebook.com',
    'instagram.com',
    'tiktok.com',
    'accounts.google.com',
    'play.google.com',
    'vimeo.com'
]

class WebSearchService:
    @staticmethod
    def search_competitor(query, max_results=5, session_id="global"):
        start_time = time.time()
        status = "success"
        results = []

        # Deduplicate search keywords
        clean_query = query.strip()
        add_keywords = [kw for kw in ["pricing", "features", "offerings"] if kw not in clean_query.lower()]
        search_query = f"{clean_query} {' '.join(add_keywords)}".strip()

        try:
            results = WebSearchService._execute_ddg_search(search_query, max_results=max_results)
            if len(results) < 2:
                # Try raw query if initial search returned sparse results
                secondary_results = WebSearchService._execute_ddg_search(clean_query, max_results=max_results)
                for item in secondary_results:
                    if not any(r['url'] == item['url'] for r in results):
                        results.append(item)
        except Exception as e:
            logger.warning(f"DuckDuckGo search encountered an issue: {e}.")

        if not results:
            logger.info(f"Live search returned no results for '{query}'.")

        results = results[:max_results]
        execution_time_ms = (time.time() - start_time) * 1000
        
        AuditLogger.log_tool_execution(
            tool_name="web_search",
            input_params={
                "query": query,
                "search_query": search_query,
                "max_results": max_results
            },
            execution_time_ms=execution_time_ms,
            status=status,
            result_summary=f"Retrieved {len(results)} web intelligence signals for '{query}'",
            session_id=session_id
        )

        return {
            "query": query,
            "result_count": len(results),
            "results": results
        }

    @staticmethod
    def _execute_ddg_search(query, max_results=5):
        formatted_results = []
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                ddg_results = list(ddgs.text(query, max_results=max_results * 2))
                for item in ddg_results:
                    url = item.get("href", "")
                    # Filter out video/social noise domains
                    if any(domain in url.lower() for domain in DISALLOWED_DOMAINS):
                        continue

                    formatted_results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("body", ""),
                        "url": url,
                        "source": "DuckDuckGo Web Search"
                    })
                    if len(formatted_results) >= max_results:
                        break
        except Exception as e:
            logger.error(f"DDGS search error: {e}")
            raise e
        return formatted_results
