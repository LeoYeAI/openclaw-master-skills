#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTTP client for llama-server (OpenAI-compatible API)."""

from __future__ import annotations

from typing import Dict, List

DEFAULT_SERVER = "http://127.0.0.1:8080"


class ContextOverflowError(RuntimeError):
    """Raised when the request exceeds or fills the model's context window.

    Covers both cases:
    - Prompt alone exceeds context (HTTP 400, exceed_context_size_error)
    - Prompt fits but output is truncated (finish_reason: "length")
    """

    def __init__(self, message: str, *, prompt_tokens: int = 0, ctx_size: int = 0):
        super().__init__(message)
        self.prompt_tokens = prompt_tokens
        self.ctx_size = ctx_size


def _load_requests():
    """Import requests lazily so tests can import command modules without it."""
    try:
        import requests
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The 'requests' package is required to talk to llama-server. "
            "Run via has-text/has_text_entry.py or install requests first."
        ) from exc
    return requests


class HaSClient:
    """Thin wrapper around llama-server's OpenAI-compatible API."""

    def __init__(self, server_url: str = DEFAULT_SERVER):
        self.base_url = server_url.rstrip("/")
        self._requests = _load_requests()
        self._session = self._requests.Session()

    # ------------------------------------------------------------------
    # Chat completions
    # ------------------------------------------------------------------

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send a chat completion request and return the assistant reply.

        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."}

        Returns:
            The model's response text.

        Raises:
            RuntimeError: If the server is unreachable or returns an error.
            ContextOverflowError: If the prompt exceeds context or output
                is truncated due to context exhaustion.
        """
        url = f"{self.base_url}/v1/chat/completions"
        payload = {"messages": messages}
        try:
            resp = self._session.post(url, json=payload, timeout=120)
        except self._requests.ConnectionError:
            raise RuntimeError(
                f"Cannot connect to llama-server at {self.base_url}\n"
                f"Please start llama-server first:\n"
                f"  llama-server -m has_text_model.gguf -ngl 999 -c 8192 -fa on -ctk q8_0 -ctv q8_0 --port 8080\n"
                f"For parallel scan/seek, add --parallel N (or -np N) and scale -c to 8192 * N "
                f"so each slot keeps the full 8K context budget."
            )

        # Detect prompt overflow (HTTP 400 with exceed_context_size_error)
        if resp.status_code == 400:
            try:
                err = resp.json().get("error", {})
            except Exception:
                err = {}
            if err.get("type") == "exceed_context_size_error":
                raise ContextOverflowError(
                    f"Prompt ({err.get('n_prompt_tokens', '?')} tokens) exceeds "
                    f"context window ({err.get('n_ctx', '?')} tokens)",
                    prompt_tokens=err.get("n_prompt_tokens", 0),
                    ctx_size=err.get("n_ctx", 0),
                )

        try:
            resp.raise_for_status()
        except self._requests.HTTPError as e:
            raise RuntimeError(
                f"llama-server returned {e.response.status_code}: {e.response.text}"
            ) from e

        data = resp.json()
        choice = data["choices"][0]

        # Detect output truncation (finish_reason: "length")
        if choice.get("finish_reason") == "length":
            usage = data.get("usage", {})
            raise ContextOverflowError(
                f"Output truncated: context full "
                f"(prompt {usage.get('prompt_tokens', '?')} + "
                f"completion {usage.get('completion_tokens', '?')} = "
                f"{usage.get('total_tokens', '?')} tokens)",
                prompt_tokens=usage.get("prompt_tokens", 0),
                ctx_size=usage.get("total_tokens", 0),
            )

        return choice["message"]["content"]

    # ------------------------------------------------------------------
    # Tokenize (for chunking)
    # ------------------------------------------------------------------

    def tokenize(self, text: str) -> List[int]:
        """Tokenize text using llama-server's /tokenize endpoint.

        Args:
            text: Text to tokenize.

        Returns:
            List of token IDs.
        """
        url = f"{self.base_url}/tokenize"
        try:
            resp = self._session.post(url, json={"content": text}, timeout=30)
            resp.raise_for_status()
        except self._requests.ConnectionError:
            raise RuntimeError(
                f"Cannot connect to llama-server at {self.base_url} for tokenization.\n"
                f"Token counting requires a running llama-server."
            )
        except self._requests.HTTPError as e:
            raise RuntimeError(
                f"llama-server tokenize returned {e.response.status_code}: {e.response.text}"
            ) from e

        data = resp.json()
        return data.get("tokens", [])

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string.

        Args:
            text: Text to count tokens for.

        Returns:
            Number of tokens.
        """
        return len(self.tokenize(text))

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def health(self) -> bool:
        """Check if llama-server is reachable."""
        try:
            resp = self._session.get(f"{self.base_url}/health", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
