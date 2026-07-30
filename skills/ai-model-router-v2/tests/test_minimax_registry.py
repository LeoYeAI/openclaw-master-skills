#!/usr/bin/env python3
"""Unit tests for the MiniMax cloud provider entries in ai-model-router-v2.

These tests only inspect the built-in registry; they make no network calls.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skill"))

from modules.detector import ModelDetector, MINIMAX_ENDPOINTS  # noqa: E402


class TestMiniMaxRegistry(unittest.TestCase):
    def setUp(self):
        self.detector = ModelDetector()
        registry = self.detector.get_cloud_registry()
        self.by_id = {m.id: m for m in registry}
        self.minimax = [m for m in registry if m.provider == "MiniMax"]

    def test_provider_present(self):
        """The cloud registry exposes the MiniMax provider."""
        self.assertGreater(len(self.minimax), 0)
        for m in self.minimax:
            self.assertEqual(m.type, "cloud")

    def test_current_models_registered(self):
        """Both currently offered text models are registered."""
        self.assertIn("minimax:MiniMax-M3", self.by_id)
        self.assertIn("minimax:MiniMax-M2.7", self.by_id)

    def test_m3_parameters(self):
        m = self.by_id["minimax:MiniMax-M3"]
        self.assertEqual(m.name, "MiniMax M3")
        self.assertEqual(m.context_window, 1_000_000)
        self.assertEqual(m.input_modalities, ["text", "image", "video"])
        self.assertEqual(m.thinking, ["adaptive", "disabled"])
        self.assertEqual(
            m.pricing_usd_per_million_tokens,
            {"input": 0.6, "output": 2.4, "cache_read": 0.12, "cache_write": None},
        )
        self.assertEqual(m.openai_base_url, "https://api.minimax.io/v1")
        self.assertEqual(m.anthropic_base_url, "https://api.minimax.io/anthropic")

    def test_m27_parameters(self):
        m = self.by_id["minimax:MiniMax-M2.7"]
        self.assertEqual(m.name, "MiniMax M2.7")
        self.assertEqual(m.context_window, 204_800)
        self.assertEqual(m.input_modalities, ["text"])
        self.assertEqual(m.thinking, ["always_on"])
        self.assertEqual(
            m.pricing_usd_per_million_tokens,
            {"input": 0.3, "output": 1.2, "cache_read": 0.06, "cache_write": 0.375},
        )

    def test_regional_endpoints(self):
        """Global and CN regions expose OpenAI- and Anthropic-compatible URLs."""
        endpoints = self.detector.get_cloud_endpoints()["MiniMax"]
        self.assertEqual(endpoints, MINIMAX_ENDPOINTS)
        self.assertEqual(
            endpoints["global_en"]["openai_base_url"], "https://api.minimax.io/v1"
        )
        self.assertEqual(
            endpoints["global_en"]["anthropic_base_url"],
            "https://api.minimax.io/anthropic",
        )
        self.assertEqual(
            endpoints["cn_zh"]["openai_base_url"], "https://api.minimaxi.com/v1"
        )
        self.assertEqual(
            endpoints["cn_zh"]["anthropic_base_url"],
            "https://api.minimaxi.com/anthropic",
        )


if __name__ == "__main__":
    unittest.main()
