"""Multi-provider embedding support for semantic search.

Providers are detected automatically in this order:
1. ollama (local server with nomic-embed-text)
2. sentence-transformers (pure Python)
3. fastembed (lightweight)
4. OpenAI API (cloud, needs OPENAI_API_KEY)
5. Gemini API (cloud, needs GEMINI_API_KEY)
6. BM25 (always available, keyword-based fallback)

Embedding Chain:
  A configurable fallback chain lets you define a priority list of providers.
  Palaia tries the first provider; if it fails (rate-limit, timeout, import error),
  it moves to the next. BM25 is always the last resort.
"""

from __future__ import annotations

import importlib.metadata as _importlib_metadata
import importlib.util
import math
import os
import re
import warnings
from collections import Counter
from typing import Protocol, runtime_checkable


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol for embedding providers."""

    name: str

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts. Returns list of vectors."""
        ...

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query text. Returns a vector."""
        ...


class OllamaProvider:
    """Embedding via local ollama server."""

    name = "ollama"
    default_model = "nomic-embed-text"

    def __init__(self, model: str | None = None, base_url: str = "http://localhost:11434"):
        self.model = model or self.default_model
        self.base_url = base_url
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import ollama as ollama_lib

                self._client = ollama_lib.Client(host=self.base_url)
            except ImportError:
                # Fall back to raw HTTP
                self._client = "http"
        return self._client

    def embed(self, texts: list[str]) -> list[list[float]]:
        client = self._get_client()
        if client == "http":
            return [self._embed_http(t) for t in texts]
        results = []
        for text in texts:
            resp = client.embed(model=self.model, input=text)
            # ollama returns {"embeddings": [[...]]}
            if isinstance(resp, dict) and "embeddings" in resp:
                results.append(resp["embeddings"][0])
            else:
                results.append(resp.embeddings[0] if hasattr(resp, "embeddings") else [])
        return results

    def embed_query(self, text: str) -> list[float]:
        return self.embed([text])[0]

    def _embed_http(self, text: str) -> list[float]:
        import json
        import urllib.request

        data = json.dumps({"model": self.model, "input": text}).encode()
        req = urllib.request.Request(
            f"{self.base_url}/api/embed",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        return result.get("embeddings", [[]])[0]


class SentenceTransformersProvider:
    """Embedding via sentence-transformers library."""

    name = "sentence-transformers"
    default_model = "all-MiniLM-L6-v2"

    def __init__(self, model: str | None = None):
        self.model_name = model or self.default_model
        self._model = None

    def _get_model(self):
        if self._model is None:
            import io
            import logging
            import os
            import sys

            # Suppress noisy HuggingFace / tokenizers / safetensors warnings
            os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
            os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
            os.environ.setdefault("HF_HUB_DISABLE_IMPLICIT_TOKEN", "1")
            os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
            for _logger_name in (
                "sentence_transformers",
                "transformers",
                "huggingface_hub",
                "torch",
                "safetensors",
            ):
                logging.getLogger(_logger_name).setLevel(logging.ERROR)

            # Redirect stderr during import + model load to suppress safetensors
            # LOAD REPORT and HF Hub auth warnings that bypass the logging framework
            _old_stderr = sys.stderr
            sys.stderr = io.StringIO()
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name)
            finally:
                sys.stderr = _old_stderr
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        model = self._get_model()
        embeddings = model.encode(texts, convert_to_numpy=True)
        return [e.tolist() for e in embeddings]

    def embed_query(self, text: str) -> list[float]:
        return self.embed([text])[0]


class FastEmbedProvider:
    """Embedding via fastembed library."""

    name = "fastembed"
    default_model = "BAAI/bge-small-en-v1.5"

    def __init__(self, model: str | None = None):
        self.model_name = model or self.default_model
        self._model = None

    def _get_model(self):
        if self._model is None:
            from fastembed import TextEmbedding

            self._model = TextEmbedding(model_name=self.model_name)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        model = self._get_model()
        embeddings = list(model.embed(texts))
        return [e.tolist() if hasattr(e, "tolist") else list(e) for e in embeddings]

    def embed_query(self, text: str) -> list[float]:
        return self.embed([text])[0]


class OpenAIProvider:
    """Embedding via OpenAI API."""

    name = "openai"
    default_model = "text-embedding-3-small"

    def __init__(self, model: str | None = None, api_key: str | None = None):
        self.model_name = model or self.default_model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                self._client = "http"
        return self._client

    def embed(self, texts: list[str]) -> list[list[float]]:
        client = self._get_client()
        if client == "http":
            return self._embed_http(texts)
        resp = client.embeddings.create(model=self.model_name, input=texts)
        return [d.embedding for d in resp.data]

    def embed_query(self, text: str) -> list[float]:
        return self.embed([text])[0]

    def _embed_http(self, texts: list[str]) -> list[list[float]]:
        import json
        import urllib.request

        data = json.dumps({"model": self.model_name, "input": texts}).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/embeddings",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        return [d["embedding"] for d in result["data"]]


class GeminiProvider:
    """Embedding via Google Gemini API."""

    name = "gemini"
    default_model = "gemini-embedding-exp-03-07"

    def __init__(self, model: str | None = None, api_key: str | None = None):
        self.model_name = model or self.default_model
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set")

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed texts via Gemini REST API."""
        import json
        import urllib.request

        results = []
        # Gemini embedContent accepts one text at a time; batch via batchEmbedContents
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:batchEmbedContents?key={self.api_key}"
        requests_body = [{"model": f"models/{self.model_name}", "content": {"parts": [{"text": t}]}} for t in texts]
        data = json.dumps({"requests": requests_body}).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        for emb in result.get("embeddings", []):
            results.append(emb.get("values", []))
        return results

    def embed_query(self, text: str) -> list[float]:
        return self.embed([text])[0]


class BM25Provider:
    """Keyword-based search provider. Always available, no vectors."""

    name = "bm25"

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus: list[tuple[str, list[str]]] = []
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
            tokens = _tokenize(text)
            self.corpus.append((doc_id, tokens))
            self.doc_lens.append(len(tokens))
            seen = set(tokens)
            for t in seen:
                self.doc_freqs[t] += 1

        self.n_docs = len(self.corpus)
        self.avg_dl = sum(self.doc_lens) / self.n_docs if self.n_docs else 1.0

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        """Search the index. Returns list of (doc_id, score) sorted desc."""
        query_tokens = _tokenize(query)
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

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Not applicable for BM25. Raises NotImplementedError."""
        raise NotImplementedError("BM25 does not produce embedding vectors")

    def embed_query(self, text: str) -> list[float]:
        """Not applicable for BM25. Raises NotImplementedError."""
        raise NotImplementedError("BM25 does not produce embedding vectors")


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer."""
    text = text.lower()
    return re.findall(r"\b\w+\b", text)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _check_ollama_available(base_url: str = "http://localhost:11434") -> tuple[bool, str | None, list[str]]:
    """Check if ollama server is running and which models are available.

    Returns: (server_running, version_or_none, list_of_models)
    """
    import json
    import urllib.request

    try:
        req = urllib.request.Request(f"{base_url}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
        models = [m.get("name", "").split(":")[0] for m in data.get("models", [])]
        return True, None, models
    except Exception:
        return False, None, []


def _check_openai_key() -> str | None:
    """Check for OpenAI API key in env or openclaw auth."""
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key
    # Check openclaw auth profiles
    auth_dir = os.path.expanduser("~/.openclaw")
    for candidate in ["auth.json", "config.json"]:
        path = os.path.join(auth_dir, candidate)
        if os.path.exists(path):
            try:
                import json

                with open(path) as f:
                    data = json.load(f)
                # Look for openai key in various formats
                if isinstance(data, dict):
                    if "openai_api_key" in data:
                        return data["openai_api_key"]
                    for profile in data.values():
                        if isinstance(profile, dict) and "openai_api_key" in profile:
                            return profile["openai_api_key"]
            except (OSError, ValueError):
                pass
    return None


def _check_gemini_key() -> str | None:
    """Check for Gemini API key in env."""
    return os.environ.get("GEMINI_API_KEY")


def _check_voyage_key() -> str | None:
    """Check for Voyage API key in env."""
    return os.environ.get("VOYAGE_API_KEY")


def detect_providers() -> list[dict]:
    """Detect all available embedding providers.

    Returns list of dicts with keys: name, available, version, models, install_hint
    """
    providers = []

    # 1. ollama
    server_running, version, models = _check_ollama_available()
    has_nomic = "nomic-embed-text" in models if models else False
    providers.append(
        {
            "name": "ollama",
            "available": server_running and has_nomic,
            "server_running": server_running,
            "models": models,
            "has_nomic": has_nomic,
            "version": version,
            "install_hint": None
            if server_running
            else "curl -fsSL https://ollama.com/install.sh | sh && ollama pull nomic-embed-text",
        }
    )

    # 2. sentence-transformers
    st_spec = importlib.util.find_spec("sentence_transformers")
    st_version = None
    if st_spec:
        try:
            # already imported as _importlib_metadata
            st_version = _importlib_metadata.version("sentence-transformers")
        except Exception:
            st_version = "installed"
    providers.append(
        {
            "name": "sentence-transformers",
            "available": st_spec is not None,
            "version": st_version,
            "install_hint": 'pip install "palaia[sentence-transformers]"' if not st_spec else None,
        }
    )

    # 3. fastembed
    fe_spec = importlib.util.find_spec("fastembed")
    fe_version = None
    if fe_spec:
        try:
            # already imported as _importlib_metadata
            fe_version = _importlib_metadata.version("fastembed")
        except Exception:
            fe_version = "installed"
    providers.append(
        {
            "name": "fastembed",
            "available": fe_spec is not None,
            "version": fe_version,
            "install_hint": 'pip install "palaia[fastembed]"' if not fe_spec else None,
        }
    )

    # 4. OpenAI
    openai_key = _check_openai_key()
    providers.append(
        {
            "name": "openai",
            "available": openai_key is not None,
            "version": None,
            "install_hint": None if openai_key else "Set OPENAI_API_KEY environment variable",
        }
    )

    # 5. Gemini
    gemini_key = _check_gemini_key()
    providers.append(
        {
            "name": "gemini",
            "available": gemini_key is not None,
            "version": None,
            "install_hint": None if gemini_key else "Set GEMINI_API_KEY environment variable",
        }
    )

    # 6. Voyage
    voyage_key = _check_voyage_key()
    providers.append(
        {
            "name": "voyage",
            "available": voyage_key is not None,
            "version": None,
            "install_hint": None if voyage_key else "Set VOYAGE_API_KEY environment variable",
        }
    )

    return providers


class EmbeddingChain:
    """Tries providers in order. Falls back on error."""

    def __init__(self, chain: list[str], models: dict[str, str] | None = None):
        self.chain_names = chain
        self.providers: list[EmbeddingProvider] = []
        self.models = models or {}
        self._last_error: str | None = None
        self._active_provider: str | None = None
        self._fallback_reason: str | None = None
        for name in chain:
            if name == "bm25":
                continue  # BM25 is always the implicit last resort
            try:
                provider = _create_provider(name, self.models.get(name))
                self.providers.append(provider)
            except (ImportError, ValueError):
                continue  # skip unavailable

    @property
    def name(self) -> str:
        """Display name for the chain."""
        return " → ".join(self.chain_names)

    @property
    def active_provider_name(self) -> str | None:
        """Name of the currently active (last successful) provider."""
        return self._active_provider

    @property
    def fallback_reason(self) -> str | None:
        """Reason why we fell back from the primary provider."""
        return self._fallback_reason

    def embed_query(self, text: str) -> tuple[list[float], str]:
        """Returns (vector, provider_name). Tries each provider in order."""
        self._fallback_reason = None
        primary_name = self.providers[0].name if self.providers else None
        for provider in self.providers:
            try:
                vector = provider.embed_query(text)
                self._active_provider = provider.name
                if provider.name != primary_name:
                    self._fallback_reason = self._last_error
                return vector, provider.name
            except Exception as e:
                self._last_error = f"{provider.name}: {e}"
                warnings.warn(f"{provider.name} failed: {e}, trying next...")
                continue
        # All failed → BM25 (return empty vector)
        self._active_provider = "bm25"
        if primary_name:
            self._fallback_reason = self._last_error
        return [], "bm25"

    def embed(self, texts: list[str]) -> tuple[list[list[float]], str]:
        """Batch embed. Returns (vectors, provider_name)."""
        self._fallback_reason = None
        primary_name = self.providers[0].name if self.providers else None
        for provider in self.providers:
            try:
                vectors = provider.embed(texts)
                self._active_provider = provider.name
                if provider.name != primary_name:
                    self._fallback_reason = self._last_error
                return vectors, provider.name
            except Exception as e:
                self._last_error = f"{provider.name}: {e}"
                warnings.warn(f"{provider.name} failed: {e}, trying next...")
                continue
        self._active_provider = "bm25"
        if primary_name:
            self._fallback_reason = self._last_error
        return [], "bm25"

    def provider_status(self) -> list[dict]:
        """Get status info for each provider in the chain."""
        detected = {p["name"]: p for p in detect_providers()}
        statuses = []
        for name in self.chain_names:
            if name == "bm25":
                statuses.append(
                    {
                        "name": "bm25",
                        "model": None,
                        "available": True,
                        "status": "always available",
                    }
                )
                continue
            info = detected.get(name, {})
            model = self.models.get(name)
            # Get default model from provider class
            if not model:
                defaults = {
                    "openai": OpenAIProvider.default_model,
                    "sentence-transformers": SentenceTransformersProvider.default_model,
                    "fastembed": FastEmbedProvider.default_model,
                    "ollama": OllamaProvider.default_model,
                    "gemini": GeminiProvider.default_model,
                }
                model = defaults.get(name)
            available = info.get("available", False)
            if name in ("openai", "gemini"):
                status = "API key found" if available else "no key found"
            elif name == "ollama":
                if info.get("server_running"):
                    status = "server running" if available else "model not pulled"
                else:
                    status = "server not running"
            else:
                status = "installed" if available else "not installed"
            statuses.append(
                {
                    "name": name,
                    "model": model,
                    "available": available,
                    "status": status,
                }
            )
        return statuses


def _resolve_embedding_models(config: dict) -> dict[str, str]:
    """Extract per-provider model overrides from config.

    Supports both:
      - embedding_model: "text-embedding-3-large"  (old format, applies to active provider)
      - embedding_model: {"openai": "text-embedding-3-large", ...}  (new format)
    """
    raw = config.get("embedding_model", "")
    if isinstance(raw, dict):
        return raw
    # Old format: single string → no per-provider mapping
    return {}


def _resolve_single_model(config: dict) -> str | None:
    """Get single model string for backward compat."""
    raw = config.get("embedding_model", "")
    if isinstance(raw, str) and raw:
        return raw
    return None


def build_embedding_chain(config: dict) -> EmbeddingChain:
    """Build an EmbeddingChain from config.

    Supports:
      - embedding_chain: ["openai", "sentence-transformers", "bm25"]
      - embedding_provider: "auto" (legacy, auto-detect)
      - embedding_provider: "sentence-transformers" (legacy, single provider)

    embedding_chain takes precedence over embedding_provider.
    """
    models = _resolve_embedding_models(config)
    single_model = _resolve_single_model(config)

    # New format: explicit chain
    chain = config.get("embedding_chain")
    if chain and isinstance(chain, list):
        # Ensure bm25 is always at the end
        if "bm25" not in chain:
            chain = chain + ["bm25"]
        return EmbeddingChain(chain, models)

    # Legacy format: embedding_provider
    provider_name = config.get("embedding_provider", "auto")

    if provider_name == "none":
        return EmbeddingChain(["bm25"], models)

    if provider_name != "auto":
        # Single explicit provider + bm25 fallback
        chain_list = [provider_name, "bm25"]
        # If single_model is set, map it to this provider
        if single_model and provider_name not in models:
            models[provider_name] = single_model
        return EmbeddingChain(chain_list, models)

    # Auto-detect: build chain from available providers
    detected = detect_providers()
    chain_list = []
    for p in detected:
        if p["available"] and p["name"] != "voyage":
            chain_list.append(p["name"])
    chain_list.append("bm25")
    if single_model:
        # Apply single model to first provider if no per-provider config
        if chain_list and chain_list[0] not in models:
            models[chain_list[0]] = single_model
    return EmbeddingChain(chain_list, models)


def auto_detect_provider(config: dict | None = None) -> EmbeddingProvider | BM25Provider:
    """Auto-detect the best available embedding provider.

    Order: ollama → sentence-transformers → fastembed → openai → bm25

    Args:
        config: Optional config dict with embedding_provider and embedding_model keys.

    Returns:
        An embedding provider instance.

    Note: For new code, prefer build_embedding_chain() which supports fallback chains.
    """
    config = config or {}
    provider_name = config.get("embedding_provider", "auto")
    model = config.get("embedding_model", "") or None
    # Handle dict-style embedding_model for backward compat
    if isinstance(model, dict):
        model = None

    if provider_name == "none":
        return BM25Provider()

    if provider_name != "auto":
        # Explicit provider requested
        return _create_provider(provider_name, model)

    # Auto-detect
    providers = detect_providers()
    for p in providers:
        if p["available"] and p["name"] != "voyage":  # voyage is not a provider we implement
            return _create_provider(p["name"], model)

    # Fallback
    return BM25Provider()


def _create_provider(name: str, model: str | None = None) -> EmbeddingProvider | BM25Provider:
    """Create a provider by name."""
    if name == "ollama":
        return OllamaProvider(model=model)
    elif name == "sentence-transformers":
        return SentenceTransformersProvider(model=model)
    elif name == "fastembed":
        return FastEmbedProvider(model=model)
    elif name == "openai":
        return OpenAIProvider(model=model)
    elif name == "gemini":
        return GeminiProvider(model=model)
    elif name == "bm25" or name == "none":
        return BM25Provider()
    else:
        raise ValueError(f"Unknown embedding provider: {name}")


def _repair_fastembed_cache_if_needed(model_name: str) -> None:
    """Check fastembed cache integrity and delete corrupted cache for re-download.

    Corrupted caches (e.g. broken symlinks from container/volume issues) cause
    cryptic ONNX runtime errors. This pre-check in warmup ensures a clean state.
    """
    import shutil
    from pathlib import Path

    model_short = model_name.split("/")[-1] if "/" in model_name else model_name
    cache_dir_name = f"models--qdrant--{model_short}-onnx-q"
    import tempfile

    cache_dir = Path(tempfile.gettempdir()) / "fastembed_cache" / cache_dir_name

    if not cache_dir.exists():
        return  # No cache yet — will be downloaded fresh

    # Check for ONNX files
    onnx_files = list(cache_dir.rglob("model_optimized.onnx")) + list(cache_dir.rglob("model.onnx"))

    corrupted = False
    if not onnx_files:
        corrupted = True
    else:
        for f in onnx_files:
            if f.is_symlink() and not f.resolve().exists():
                corrupted = True
                break
            if not f.is_file():
                corrupted = True
                break

    if corrupted:
        print(f"  [palaia] Corrupted fastembed cache detected — removing {cache_dir} for re-download")
        try:
            shutil.rmtree(cache_dir)
        except OSError as e:
            print(f"  [palaia] Warning: could not remove corrupted cache: {e}")


def warmup_providers(config: dict) -> list[dict]:
    """Pre-download and load embedding models for all providers in the chain.

    Returns a list of dicts with keys: name, status, message.
    status is one of: ready, skipped, action_needed, error.
    """
    import os

    models = _resolve_embedding_models(config)

    # Determine which providers to warm up
    chain = config.get("embedding_chain")
    if chain and isinstance(chain, list):
        provider_names = [p for p in chain if p != "bm25"]
    else:
        provider_name = config.get("embedding_provider", "auto")
        if provider_name in ("none", "auto"):
            # For auto, detect what's available
            if provider_name == "auto":
                detected = detect_providers()
                provider_names = [
                    p["name"] for p in detected if p["available"] and p["name"] not in ("voyage", "openai", "gemini")
                ]
            else:
                provider_names = []
        else:
            provider_names = [provider_name]

    if not provider_names:
        return []

    results = []
    for name in provider_names:
        model_override = models.get(name)
        try:
            if name == "sentence-transformers":
                model_name = model_override or SentenceTransformersProvider.default_model
                provider = SentenceTransformersProvider(model=model_name)
                provider._get_model()  # triggers download + load
                # Try to find cache path
                cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
                results.append(
                    {
                        "name": name,
                        "status": "ready",
                        "message": f"Model loaded: {model_name} (cached at {cache_dir})",
                    }
                )
            elif name == "ollama":
                model_name = model_override or OllamaProvider.default_model
                server_running, _, available_models = _check_ollama_available()
                if not server_running:
                    results.append(
                        {
                            "name": name,
                            "status": "action_needed",
                            "message": "Ollama server not running. Start with: ollama serve",
                        }
                    )
                elif model_name not in available_models and model_name.split(":")[0] not in available_models:
                    results.append(
                        {
                            "name": name,
                            "status": "action_needed",
                            "message": f"Model '{model_name}' not pulled. Run: ollama pull {model_name}",
                        }
                    )
                else:
                    results.append(
                        {
                            "name": name,
                            "status": "ready",
                            "message": f"Model available: {model_name}",
                        }
                    )
            elif name == "fastembed":
                model_name = model_override or FastEmbedProvider.default_model
                # Pre-check: verify cache integrity before loading
                _repair_fastembed_cache_if_needed(model_name)
                provider = FastEmbedProvider(model=model_name)
                provider._get_model()  # triggers download
                results.append(
                    {
                        "name": name,
                        "status": "ready",
                        "message": f"Model loaded: {model_name}",
                    }
                )
            elif name == "openai":
                # Cloud provider — no model to download
                key = _check_openai_key()
                if key:
                    results.append(
                        {
                            "name": name,
                            "status": "skipped",
                            "message": "Cloud provider — no local model to pre-load. API key found.",
                        }
                    )
                else:
                    results.append(
                        {
                            "name": name,
                            "status": "action_needed",
                            "message": "No API key found. Set OPENAI_API_KEY environment variable.",
                        }
                    )
            elif name == "gemini":
                # Cloud provider — no model to download
                key = _check_gemini_key()
                if key:
                    model_name = model_override or GeminiProvider.default_model
                    results.append(
                        {
                            "name": name,
                            "status": "skipped",
                            "message": f"Cloud provider — no local model to pre-load. API key found. Model: {model_name}",
                        }
                    )
                else:
                    results.append(
                        {
                            "name": name,
                            "status": "action_needed",
                            "message": "No API key found. Set GEMINI_API_KEY environment variable.",
                        }
                    )
            else:
                results.append(
                    {
                        "name": name,
                        "status": "skipped",
                        "message": f"Unknown provider '{name}', skipping.",
                    }
                )
        except ImportError as e:
            results.append(
                {
                    "name": name,
                    "status": "error",
                    "message": f"Not installed: {e}",
                }
            )
        except Exception as e:
            results.append(
                {
                    "name": name,
                    "status": "error",
                    "message": str(e),
                }
            )

    return results


def get_provider_display_info(provider: EmbeddingProvider | BM25Provider) -> str:
    """Get a human-readable display string for a provider."""
    if isinstance(provider, BM25Provider):
        return "BM25 (keyword search)"
    name = getattr(provider, "name", "unknown")
    model = getattr(provider, "model_name", None) or getattr(provider, "model", None) or "default"
    return f"{name} ({model})"
