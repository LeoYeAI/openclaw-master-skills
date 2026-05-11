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
from typing import List


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

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = ["chat"]


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
        ]

    def detect_all(self) -> List[ModelInfo]:
        """Detect all available models"""
        return self.detect_local() + self.get_cloud_registry()
