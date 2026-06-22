"""LangChain integration for Novada Search."""

from typing import Optional

try:
    from langchain_core.tools import BaseTool
except Exception as exc:  # pragma: no cover
    raise ImportError("Install langchain-core: pip install langchain-core") from exc

from pydantic import BaseModel, Field
from novada_search import NovadaSearch


class NovadaSearchInput(BaseModel):
    query: str = Field(description="Search query")
    scene: Optional[str] = Field(default=None, description="Vertical scene")
    mode: Optional[str] = Field(default=None, description="auto or multi")
    max_results: int = Field(default=5, description="Maximum results")


class NovadaSearchTool(BaseTool):
    name: str = "novada_search"
    description: str = "Search the web with Novada multi-engine search."
    args_schema: type = NovadaSearchInput
    client: NovadaSearch = None

    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(**kwargs)
        self.client = NovadaSearch(api_key=api_key)

    def _run(self, query: str, scene: str = None, mode: str = None, max_results: int = 5) -> str:
        import json

        result = self.client.search(
            query=query,
            scene=scene,
            mode=mode,
            max_results=max_results,
            format="agent-json",
        )
        summary = {
            "query": result.get("query"),
            "engines_used": result.get("engines_used"),
            "results": [],
        }
        for r in result.get("unified_results", result.get("organic_results", []))[:max_results]:
            summary["results"].append(
                {
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "snippet": (r.get("snippet") or "")[:200],
                    "score": r.get("score"),
                }
            )
        return json.dumps(summary, ensure_ascii=False)
