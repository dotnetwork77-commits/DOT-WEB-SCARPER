from duckduckgo_search import DDGS

def fetch_results(query):
    """Fetch web search results from DuckDuckGo and format them."""
    try:
        results = DDGS().text(query, max_results=4)
        formatted = "Web Search Results:\n"
        for r in results:
            formatted += r['title'] + ': ' + r['body'] + '\n\n'
        return formatted
    except Exception as e:
        print(f"Error fetching search results: {e}")
        return ""

if __name__ == "__main__":
    test_query = "Python web search library"
    print(fetch_results(test_query))