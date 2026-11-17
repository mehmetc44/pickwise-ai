from typing import Any
import httpx

from config import settings


def web_search(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """
    Tavily API kullanarak internette arama yapar.
    Katalogda doğrudan yazmayan cihaz/traktör/model uyumluluk bilgilerini ve
    teknik spesifikasyonları (örn. voltaj, soket tipi, uyumlu parça türü) öğrenmek için kullanılır.
    """
    if not settings.TAVILY_API_KEY:
        return [{"error": "TAVILY_API_KEY tanımlı değil."}]

    payload = {
        "api_key": settings.TAVILY_API_KEY,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
    }
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post("https://api.tavily.com/search", json=payload)
            resp.raise_for_status()
            results = resp.json().get("results", [])

        return [
            {
                "title": r.get("title"),
                "url": r.get("url"),
                "content": r.get("content"),
            }
            for r in results
        ]
    except Exception as exc:
        return [{"error": f"Web araması başarısız: {exc}"}]

