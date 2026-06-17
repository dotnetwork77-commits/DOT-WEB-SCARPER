"""
search.py — Fetches and formats DuckDuckGo web search results.

Improvements over original:
- Smarter query cleaning (strips filler words for better retrieval)
- Returns up to 6 results instead of 4
- Includes source URLs for citations
- Truncates long snippets cleanly at sentence boundaries
- Adds a timestamp so the LLM knows results are fresh
- Graceful fallback if ddgs package name varies
"""

import re
from datetime import date


def _clean_query(query: str) -> str:
    filler = re.compile(
        r"^\s*(please\s+)?(can\s+you\s+)?(could\s+you\s+)?"
        r"(tell\s+me\s+)?(what\s+(is|are|was|were)\s+)?"
        r"(how\s+(do|does|did|can|to)\s+)?",
        re.IGNORECASE,
    )
    cleaned = filler.sub("", query).strip(" ?.,\n")
    return cleaned if len(cleaned) >= 5 else query.strip()


def _truncate(text: str, max_chars: int = 220) -> str:
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    last_period = truncated.rfind(". ")
    if last_period > max_chars // 2:
        return truncated[: last_period + 1]
    return truncated.rstrip() + "\u2026"


def fetch_results(query: str, max_results: int = 6) -> str:
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            try:
                from duckduckgo_search import DDGS
            except ImportError:
                print("Search error: neither 'ddgs' nor 'duckduckgo_search' is installed.")
                return ""

        search_query = _clean_query(query)
        today = date.today().isoformat()

        results = DDGS().text(search_query, max_results=max_results)
        if not results:
            return ""

        lines = [
            f"[Web Search Results \u2014 {today}]",
            f"Query: \"{search_query}\"",
            "",
        ]

        for i, r in enumerate(results, 1):
            title = r.get("title", "").strip()
            body  = _truncate(r.get("body", "").strip())
            url   = r.get("href", r.get("url", "")).strip()

            lines.append(f"{i}. {title}")
            if body:
                lines.append(f"   {body}")
            if url:
                lines.append(f"   Source: {url}")
            lines.append("")

        lines.append(
            "Note: Use the above results to inform your answer. "
            "Cite sources where relevant."
        )

        return "\n".join(lines)

    except Exception as e:
        print(f"Search error: {e}")
        return ""


if __name__ == "__main__":
    test_query = "what is the latest version of Python?"
    print(fetch_results(test_query))
