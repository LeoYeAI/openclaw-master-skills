"""Hybrid search: BM25 + semantic embeddings (ADR-001)."""

from __future__ import annotations

import math
import re
from collections import Counter

from palaia.embeddings import (
    BM25Provider,
    _create_provider,
    _resolve_embedding_models,
    auto_detect_provider,
    cosine_similarity,
    detect_providers,
    get_provider_display_info,
)


def tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer."""
    text = text.lower()
    tokens = re.findall(r"\b\w+\b", text)
    return tokens


class BM25:
    """BM25 ranking algorithm — pure Python, zero dependencies."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus: list[tuple[str, list[str]]] = []  # (doc_id, tokens)
        self.doc_freqs: Counter = Counter()
        self.doc_lens: list[int] = []
        self.avg_dl: float = 0.0
        self.n_docs: int = 0

    def index(self, documents: list[tuple[str, str]]) -> None:
        """Index a list of (doc_id, text) tuples."""
        self.corpus = []
        self.doc_freqs = Counter()
        self.doc_lens = []

        for doc_id, text in documents:
            tokens = tokenize(text)
            self.corpus.append((doc_id, tokens))
            self.doc_lens.append(len(tokens))
            seen = set(tokens)
            for t in seen:
                self.doc_freqs[t] += 1

        self.n_docs = len(self.corpus)
        self.avg_dl = sum(self.doc_lens) / self.n_docs if self.n_docs else 1.0

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        """Search the index. Returns list of (doc_id, score) sorted desc."""
        query_tokens = tokenize(query)
        if not query_tokens or not self.corpus:
            return []

        scores = []
        for idx, (doc_id, doc_tokens) in enumerate(self.corpus):
            score = 0.0
            dl = self.doc_lens[idx]
            tf_map = Counter(doc_tokens)

            for qt in query_tokens:
                if qt not in tf_map:
                    continue
                tf = tf_map[qt]
                df = self.doc_freqs.get(qt, 0)
                idf = math.log((self.n_docs - df + 0.5) / (df + 0.5) + 1.0)
                tf_norm = (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * dl / self.avg_dl))
                score += idf * tf_norm

            if score > 0:
                scores.append((doc_id, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


def detect_search_tier() -> int:
    """Detect best available search tier.

    Returns:
        1: BM25 only
        2: Local embeddings (ollama, sentence-transformers, fastembed)
        3: API embeddings (OpenAI)
    """
    from palaia.embeddings import detect_providers

    providers = detect_providers()
    for p in providers:
        if p["available"]:
            if p["name"] == "openai":
                return 3
            elif p["name"] in ("ollama", "sentence-transformers", "fastembed"):
                return 2
    return 1


def _resolve_semantic_provider(config: dict):
    """Resolve the semantic embedding provider respecting embedding_chain config.

    Reads ``embedding_chain`` from *config*, iterates over its entries (skipping
    ``"bm25"``), and returns the first provider that can be instantiated.
    Falls back to ``auto_detect_provider()`` when the chain is absent, empty,
    contains only ``"bm25"``, or none of its semantic entries are available.
    """
    chain = config.get("embedding_chain")
    if chain and isinstance(chain, list):
        models = _resolve_embedding_models(config)
        available = {p["name"] for p in detect_providers() if p["available"]}
        for name in chain:
            if name == "bm25":
                continue
            if name not in available:
                continue
            try:
                return _create_provider(name, models.get(name))
            except (ImportError, ValueError):
                continue
    # No chain configured or no chain provider available → legacy fallback
    return auto_detect_provider(config)


class SearchEngine:
    """Unified hybrid search: BM25 + semantic embeddings."""

    def __init__(self, store, config: dict | None = None):
        self.store = store
        self.bm25 = BM25()
        self.config = config or store.config
        self._provider = None

    @property
    def provider(self):
        if self._provider is None:
            self._provider = _resolve_semantic_provider(self.config)
        return self._provider

    @property
    def has_embeddings(self) -> bool:
        return not isinstance(self.provider, BM25Provider)

    def build_index(self, include_cold: bool = False, agent: str | None = None) -> list[tuple[str, str, dict]]:
        """Build search index from store entries. Returns (doc_id, full_text, meta) list."""
        entries = self.store.all_entries(include_cold=include_cold, agent=agent)
        docs = []
        docs_with_meta = []
        for meta, body, tier in entries:
            doc_id = meta.get("id", "unknown")
            title = meta.get("title", "")
            tags = " ".join(meta.get("tags", []))
            full_text = f"{title} {tags} {body}"
            docs.append((doc_id, full_text))
            docs_with_meta.append((doc_id, full_text, meta))
        self.bm25.index(docs)
        return docs_with_meta

    def search(
        self,
        query: str,
        top_k: int = 10,
        include_cold: bool = False,
        project: str | None = None,
        agent: str | None = None,
        entry_type: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        assignee: str | None = None,
        instance: str | None = None,
        before: str | None = None,
        after: str | None = None,
        cross_project: bool = False,
    ) -> list[dict]:
        """Search memories using hybrid ranking (BM25 + embeddings when available).

        Structured filters (type, status, priority, assignee, instance) use exact match,
        not embeddings.

        Temporal filters (before, after) filter by entry created timestamp.
        cross_project=True ignores project filter and searches across all projects.
        """
        docs_with_meta = self.build_index(include_cold=include_cold, agent=agent)

        # Apply structured filters (exact match, pre-BM25)
        if project and not cross_project:
            docs_with_meta = [(did, text, meta) for did, text, meta in docs_with_meta if meta.get("project") == project]
        if entry_type:
            docs_with_meta = [
                (did, text, meta) for did, text, meta in docs_with_meta if meta.get("type", "memory") == entry_type
            ]
        if status:
            docs_with_meta = [(did, text, meta) for did, text, meta in docs_with_meta if meta.get("status") == status]
        if priority:
            docs_with_meta = [
                (did, text, meta) for did, text, meta in docs_with_meta if meta.get("priority") == priority
            ]
        if assignee:
            docs_with_meta = [
                (did, text, meta) for did, text, meta in docs_with_meta if meta.get("assignee") == assignee
            ]
        if instance:
            docs_with_meta = [
                (did, text, meta) for did, text, meta in docs_with_meta if meta.get("instance") == instance
            ]

        # Temporal filters (Issue #74)
        if before:
            docs_with_meta = [
                (did, text, meta) for did, text, meta in docs_with_meta if meta.get("created", "") < before
            ]
        if after:
            docs_with_meta = [
                (did, text, meta) for did, text, meta in docs_with_meta if meta.get("created", "") > after
            ]

        if project or entry_type or status or priority or assignee or instance or before or after:
            # Rebuild BM25 index with filtered docs
            self.bm25.index([(did, text) for did, text, meta in docs_with_meta])

        # BM25 scores
        bm25_results = self.bm25.search(query, top_k=top_k * 2)  # get more candidates for hybrid
        bm25_scores = {doc_id: score for doc_id, score in bm25_results}

        # Normalize BM25 scores to [0, 1]
        max_bm25 = max(bm25_scores.values()) if bm25_scores else 1.0
        bm25_norm = {k: v / max_bm25 for k, v in bm25_scores.items()} if max_bm25 > 0 else {}

        # Embedding scores (if available)
        embed_norm = {}
        if self.has_embeddings and docs_with_meta:
            try:
                query_vec = self.provider.embed_query(query)
                # Only embed BM25 candidates + a few extra for recall
                candidate_ids = set(bm25_scores.keys())
                texts_to_embed = []
                ids_to_embed = []
                for doc_id, full_text, meta in docs_with_meta:
                    # Check cache first
                    cached = self.store.embedding_cache.get_cached(doc_id)
                    if cached:
                        sim = cosine_similarity(query_vec, cached)
                        embed_norm[doc_id] = sim
                    elif doc_id in candidate_ids or len(texts_to_embed) < top_k:
                        texts_to_embed.append(full_text)
                        ids_to_embed.append(doc_id)

                if texts_to_embed:
                    vectors = self.provider.embed(texts_to_embed)
                    model_name = getattr(self.provider, "model_name", None) or getattr(
                        self.provider, "model", "unknown"
                    )
                    for doc_id, vec in zip(ids_to_embed, vectors):
                        self.store.embedding_cache.set_cached(doc_id, vec, model=model_name)
                        sim = cosine_similarity(query_vec, vec)
                        embed_norm[doc_id] = sim
            except Exception as e:
                # If embedding fails, fall back to BM25 only
                import warnings

                warnings.warn(f"Embedding search failed, using BM25 only: {e}")
                embed_norm = {}

        # Combine scores: hybrid ranking
        all_ids = set(bm25_norm.keys()) | set(embed_norm.keys())
        combined = {}
        for doc_id in all_ids:
            bm25_s = bm25_norm.get(doc_id, 0.0)
            embed_s = embed_norm.get(doc_id, 0.0)
            if embed_norm:
                # Weighted combination: 40% BM25 + 60% embedding
                combined[doc_id] = 0.4 * bm25_s + 0.6 * embed_s
            else:
                combined[doc_id] = bm25_s

        # Sort by combined score
        ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:top_k]

        # Build output
        output = []
        for doc_id, score in ranked:
            entry = self.store.read(doc_id)
            if entry:
                meta, body = entry
                result_entry = {
                    "id": doc_id,
                    "score": round(score, 4),
                    "type": meta.get("type", "memory"),
                    "scope": meta.get("scope", "team"),
                    "title": meta.get("title", ""),
                    "tags": meta.get("tags", []),
                    "body": body[:200] + ("..." if len(body) > 200 else ""),
                    "tier": self._get_tier(doc_id),
                    "decay_score": meta.get("decay_score", 0),
                }
                # Include task fields if present
                if meta.get("status"):
                    result_entry["status"] = meta["status"]
                if meta.get("priority"):
                    result_entry["priority"] = meta["priority"]
                if meta.get("assignee"):
                    result_entry["assignee"] = meta["assignee"]
                if meta.get("due_date"):
                    result_entry["due_date"] = meta["due_date"]
                if meta.get("instance"):
                    result_entry["instance"] = meta["instance"]
                if meta.get("project"):
                    result_entry["project"] = meta["project"]
                output.append(result_entry)
        return output

    def _get_tier(self, entry_id: str) -> str:
        """Determine which tier an entry is in."""
        for tier in ("hot", "warm", "cold"):
            if (self.store.root / tier / f"{entry_id}.md").exists():
                return tier
        return "unknown"

    def search_info(self) -> dict:
        """Get info about current search configuration."""
        provider = self.provider
        provider_display = get_provider_display_info(provider)
        has_embed = self.has_embeddings
        return {
            "provider": provider_display,
            "has_embeddings": has_embed,
            "bm25_active": True,
            "semantic_active": has_embed,
        }
