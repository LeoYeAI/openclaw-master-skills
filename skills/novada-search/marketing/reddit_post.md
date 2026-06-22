# Novada Search: Open-source multi-engine search SDK for AI agents

Built an alternative to Tavily that searches 9 engines simultaneously
(Google, Bing, Yahoo, DuckDuckGo, Yandex, YouTube, eBay, Walmart, Yelp).

What works today:
- **Multi-engine search**: Google + Bing in parallel, results merged and deduped
- **Vertical scenes**: news, academic, jobs, video, images — each auto-selects the best engines
- **Auto intent detection**: say "latest AI news" → auto-picks news scene
- **SDK + CLI + MCP Server + LangChain integration**

Coming in v1.1:
- Shopping price comparison (Google Shopping + eBay + Walmart)
- Local business search (Google Maps + Yelp)
- Research mode (search + extract + merge for RAG)

Quick start:

    pip install novada-search
    export NOVADA_API_KEY="your_key"

    from novada_search import NovadaSearch
    client = NovadaSearch()
    result = client.search("latest AI news", mode="auto")
    print(result["unified_results"][:3])

Free API key: https://novada.com
GitHub: https://github.com/NovadaLabs/novada-search
PyPI: https://pypi.org/project/novada-search/
