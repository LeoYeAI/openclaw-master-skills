#!/usr/bin/env python3
"""
Model Detector - Safe module for detecting local AI models

Security:
- No subprocess execution (removed)
- No HTTP requests (removed)
- Read-only operations only
"""

import json
import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ModelInfo:
    """Model information - read-only"""
    id: str
    name: str
    provider: str
    type: str
    cost_score: float = 0
    power_score: float = 50
    capabilities: List[str] = None
    # Optional cloud metadata (populated for providers that publish it)
    context_window: Optional[int] = None
    input_modalities: List[str] = None
    thinking: List[str] = None
    pricing_usd_per_million_tokens: Optional[dict] = None
    openai_base_url: Optional[str] = None
    anthropic_base_url: Optional[str] = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = ["chat"]


# Regional API endpoints for cloud providers that expose both an
# OpenAI-compatible and an Anthropic-compatible interface per region.
MINIMAX_ENDPOINTS = {
    "global_en": {
        "openai_base_url": "https://api.minimax.io/v1",
        "anthropic_base_url": "https://api.minimax.io/anthropic",
        "docs_root": "https://platform.minimax.io/docs",
    },
    "cn_zh": {
        "openai_base_url": "https://api.minimaxi.com/v1",
        "anthropic_base_url": "https://api.minimaxi.com/anthropic",
        "docs_root": "https://platform.minimaxi.com/docs",
    },
}


class ModelDetector:
    """
    Detect available AI models safely.

    Only reads from:
    - Ollama config files (read-only)
    - Environment variables (read-only)
    """

    def detect_local(self) -> List[ModelInfo]:
        """Detect local models from Ollama config"""
        models = []

        # Check Ollama models.json (read-only, safe)
        ollama_models = self._read_ollama_models()
        models.extend(ollama_models)

        return models

    def _read_ollama_models(self) -> List[ModelInfo]:
        """
        Read Ollama models from config file.
        Safe: read-only file operation.
        """
        models = []
        config_paths = [
            os.path.expanduser("~/.ollama/models.json"),
            "/usr/share/ollama/models.json",
        ]

        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r") as f:
                        data = json.load(f)
                        for model_name in data.keys():
                            # Estimate power score from name
                            power = 30
                            name_lower = model_name.lower()
                            if "70b" in name_lower:
                                power = 80
                            elif "34b" in name_lower or "33b" in name_lower:
                                power = 70
                            elif "14b" in name_lower or "13b" in name_lower:
                                power = 50
                            elif "8b" in name_lower or "7b" in name_lower:
                                power = 35
                            elif "3b" in name_lower or "2b" in name_lower:
                                power = 20

                            models.append(ModelInfo(
                                id=f"ollama:{model_name}",
                                name=model_name,
                                provider="Ollama",
                                type="local",
                                cost_score=0,
                                power_score=power,
                            ))
                    break  # Use first valid config
                except Exception:
                    pass

        return models

    def get_cloud_registry(self) -> List[ModelInfo]:
        """Return built-in cloud model registry (no external calls)"""
        return [
            ModelInfo("anthropic:claude-haiku-4", "Claude Haiku 4", "Anthropic", "cloud", 3, 60),
            ModelInfo("anthropic:claude-sonnet-4", "Claude Sonnet 4", "Anthropic", "cloud", 5, 80),
            ModelInfo("anthropic:claude-opus-4", "Claude Opus 4", "Anthropic", "cloud", 8, 95),
            ModelInfo("openai:gpt-4o-mini", "GPT-4o Mini", "OpenAI", "cloud", 1, 50),
            ModelInfo("openai:gpt-4o", "GPT-4o", "OpenAI", "cloud", 5, 85),
            ModelInfo(
                "minimax:MiniMax-M3", "MiniMax M3", "MiniMax", "cloud", 2, 90,
                capabilities=["chat", "vision"],
                context_window=1_000_000,
                input_modalities=["text", "image", "video"],
                thinking=["adaptive", "disabled"],
                pricing_usd_per_million_tokens={
                    "input": 0.6, "output": 2.4, "cache_read": 0.12, "cache_write": None,
                },
                openai_base_url=MINIMAX_ENDPOINTS["global_en"]["openai_base_url"],
                anthropic_base_url=MINIMAX_ENDPOINTS["global_en"]["anthropic_base_url"],
            ),
            ModelInfo(
                "minimax:MiniMax-M2.7", "MiniMax M2.7", "MiniMax", "cloud", 1, 70,
                capabilities=["chat"],
                context_window=204_800,
                input_modalities=["text"],
                thinking=["always_on"],
                pricing_usd_per_million_tokens={
                    "input": 0.3, "output": 1.2, "cache_read": 0.06, "cache_write": 0.375,
                },
                openai_base_url=MINIMAX_ENDPOINTS["global_en"]["openai_base_url"],
                anthropic_base_url=MINIMAX_ENDPOINTS["global_en"]["anthropic_base_url"],
            ),
        ]

    def get_cloud_endpoints(self) -> dict:
        """Return per-region API endpoints for multi-region cloud providers."""
        return {"MiniMax": MINIMAX_ENDPOINTS}

    def detect_all(self) -> List[ModelInfo]:
        """Detect all available models"""
        return self.detect_local() + self.get_cloud_registry()
