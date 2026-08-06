#!/usr/bin/env python3
"""Unit tests for MiniMax model integration in ai-model-router-v2."""

import os
import sys
import json
import tempfile
import unittest

# Add skill source to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skill"))

from modules.detector import ModelDetector, ModelInfo
from core.router import RouterCore, Model, RouteResult


class TestMiniMaxCloudRegistry(unittest.TestCase):
    """Test MiniMax models in cloud registry."""

    def setUp(self):
        self.detector = ModelDetector()
        self.registry = self.detector.get_cloud_registry()

    def test_registry_contains_minimax_models(self):
        """MiniMax models should be present in the cloud registry."""
        minimax_models = [m for m in self.registry if m.provider == "MiniMax"]
        self.assertEqual(len(minimax_models), 4)

    def test_minimax_m27_in_registry(self):
        """MiniMax M2.7 should be in the registry with correct attributes."""
        m27 = next((m for m in self.registry if m.id == "minimax:MiniMax-M2.7"), None)
        self.assertIsNotNone(m27)
        self.assertEqual(m27.name, "MiniMax M2.7")
        self.assertEqual(m27.provider, "MiniMax")
        self.assertEqual(m27.type, "cloud")
        self.assertEqual(m27.power_score, 85)
        self.assertEqual(m27.cost_score, 3)

    def test_minimax_m27_highspeed_in_registry(self):
        """MiniMax M2.7 Highspeed should be in the registry."""
        m27hs = next((m for m in self.registry if m.id == "minimax:MiniMax-M2.7-highspeed"), None)
        self.assertIsNotNone(m27hs)
        self.assertEqual(m27hs.name, "MiniMax M2.7 Highspeed")
        self.assertEqual(m27hs.power_score, 75)
        self.assertEqual(m27hs.cost_score, 2)

    def test_minimax_m25_in_registry(self):
        """MiniMax M2.5 should be in the registry."""
        m25 = next((m for m in self.registry if m.id == "minimax:MiniMax-M2.5"), None)
        self.assertIsNotNone(m25)
        self.assertEqual(m25.name, "MiniMax M2.5")
        self.assertEqual(m25.power_score, 70)
        self.assertEqual(m25.cost_score, 2)

    def test_minimax_m25_highspeed_in_registry(self):
        """MiniMax M2.5 Highspeed should be in the registry."""
        m25hs = next((m for m in self.registry if m.id == "minimax:MiniMax-M2.5-highspeed"), None)
        self.assertIsNotNone(m25hs)
        self.assertEqual(m25hs.name, "MiniMax M2.5 Highspeed")
        self.assertEqual(m25hs.power_score, 60)
        self.assertEqual(m25hs.cost_score, 1)

    def test_minimax_models_are_cloud_type(self):
        """All MiniMax models should be cloud type."""
        minimax_models = [m for m in self.registry if m.provider == "MiniMax"]
        for m in minimax_models:
            self.assertEqual(m.type, "cloud")

    def test_minimax_m27_capabilities(self):
        """MiniMax M2.7 should have chat, vision, and tools capabilities."""
        m27 = next((m for m in self.registry if m.id == "minimax:MiniMax-M2.7"), None)
        self.assertIn("chat", m27.capabilities)
        self.assertIn("vision", m27.capabilities)
        self.assertIn("tools", m27.capabilities)

    def test_minimax_m25_capabilities(self):
        """MiniMax M2.5 should have chat and tools capabilities."""
        m25 = next((m for m in self.registry if m.id == "minimax:MiniMax-M2.5"), None)
        self.assertIn("chat", m25.capabilities)
        self.assertIn("tools", m25.capabilities)
        self.assertNotIn("vision", m25.capabilities)

    def test_total_cloud_models_count(self):
        """Registry should have 9 cloud models total (5 original + 4 MiniMax)."""
        self.assertEqual(len(self.registry), 9)

    def test_minimax_power_scores_ordered(self):
        """MiniMax M2.7 should have higher power than M2.5 variants."""
        minimax_models = {m.id: m for m in self.registry if m.provider == "MiniMax"}
        self.assertGreater(
            minimax_models["minimax:MiniMax-M2.7"].power_score,
            minimax_models["minimax:MiniMax-M2.7-highspeed"].power_score,
        )
        self.assertGreater(
            minimax_models["minimax:MiniMax-M2.7-highspeed"].power_score,
            minimax_models["minimax:MiniMax-M2.5"].power_score,
        )
        self.assertGreater(
            minimax_models["minimax:MiniMax-M2.5"].power_score,
            minimax_models["minimax:MiniMax-M2.5-highspeed"].power_score,
        )

    def test_minimax_cost_scores_reasonable(self):
        """MiniMax highspeed variants should be cheaper than standard."""
        minimax_models = {m.id: m for m in self.registry if m.provider == "MiniMax"}
        self.assertGreaterEqual(
            minimax_models["minimax:MiniMax-M2.7"].cost_score,
            minimax_models["minimax:MiniMax-M2.7-highspeed"].cost_score,
        )
        self.assertGreaterEqual(
            minimax_models["minimax:MiniMax-M2.5"].cost_score,
            minimax_models["minimax:MiniMax-M2.5-highspeed"].cost_score,
        )


class TestMiniMaxRouterFallback(unittest.TestCase):
    """Test MiniMax in router fallback models."""

    def test_fallback_includes_minimax(self):
        """Router fallback models should include MiniMax M2.7."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "models.json")
            # Write a config that will trigger fallback path by importing from detector
            router = RouterCore(config_path=config_path)
            minimax_models = [m for m in router.models if m.provider == "MiniMax"]
            self.assertGreater(len(minimax_models), 0)

    def test_minimax_model_lookup_by_id(self):
        """Router should find MiniMax models by ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "models.json")
            router = RouterCore(config_path=config_path)
            m = router.get_model("minimax:MiniMax-M2.7")
            self.assertIsNotNone(m)
            self.assertEqual(m.name, "MiniMax M2.7")


class TestMiniMaxRouting(unittest.TestCase):
    """Test routing decisions involving MiniMax models."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        config_path = os.path.join(self.tmpdir, "models.json")
        # Configure MiniMax as secondary (cloud) model
        config = {
            "primary_model": {"id": "ollama:llama3:8b"},
            "secondary_model": {"id": "minimax:MiniMax-M2.7"},
            "models": [
                {"id": "ollama:llama3:8b", "name": "Llama 3 8B", "provider": "Ollama",
                 "type": "local", "cost_score": 0, "power_score": 35},
                {"id": "minimax:MiniMax-M2.7", "name": "MiniMax M2.7", "provider": "MiniMax",
                 "type": "cloud", "cost_score": 3, "power_score": 85,
                 "requires_api_key": True, "api_key_env": "MINIMAX_API_KEY"},
            ]
        }
        with open(config_path, "w") as f:
            json.dump(config, f)
        self.router = RouterCore(config_path=config_path)

    def test_simple_task_routes_to_primary(self):
        """Simple tasks should route to primary (local) model."""
        result = self.router.route("What is Python?")
        self.assertEqual(result.model_type, "primary")
        self.assertEqual(result.model_id, "ollama:llama3:8b")

    def test_complex_task_routes_to_minimax(self):
        """Complex tasks should route to MiniMax (secondary)."""
        result = self.router.route("Design a scalable microservices architecture for an e-commerce platform")
        self.assertEqual(result.model_type, "secondary")
        self.assertEqual(result.model_id, "minimax:MiniMax-M2.7")
        self.assertEqual(result.model_name, "MiniMax M2.7")

    def test_force_secondary_routes_to_minimax(self):
        """Force secondary should route to MiniMax."""
        result = self.router.route("Hello", force="secondary")
        self.assertEqual(result.model_id, "minimax:MiniMax-M2.7")
        self.assertEqual(result.reason, "forced")

    def test_privacy_routes_to_primary_not_minimax(self):
        """Privacy-sensitive data should route to local, not MiniMax cloud."""
        result = self.router.route("My API key is sk-1234567890abcdef")
        self.assertEqual(result.model_type, "primary")
        self.assertEqual(result.model_id, "ollama:llama3:8b")
        self.assertGreater(len(result.privacy_detected), 0)

    def test_route_result_has_correct_fields(self):
        """Route result for MiniMax should contain all expected fields."""
        result = self.router.route("Design a comprehensive end-to-end system", force="secondary")
        self.assertIsInstance(result, RouteResult)
        self.assertEqual(result.model_id, "minimax:MiniMax-M2.7")
        self.assertEqual(result.model_name, "MiniMax M2.7")
        self.assertIsInstance(result.confidence, float)


class TestModelInfoDataclass(unittest.TestCase):
    """Test ModelInfo dataclass for MiniMax models."""

    def test_minimax_model_info_defaults(self):
        """ModelInfo should have correct defaults for capabilities."""
        m = ModelInfo("minimax:test", "Test", "MiniMax", "cloud")
        self.assertEqual(m.capabilities, ["chat"])

    def test_minimax_model_info_custom_capabilities(self):
        """ModelInfo should accept custom capabilities."""
        m = ModelInfo("minimax:test", "Test", "MiniMax", "cloud",
                      capabilities=["chat", "vision", "tools"])
        self.assertEqual(m.capabilities, ["chat", "vision", "tools"])


class TestDetectAll(unittest.TestCase):
    """Test detect_all includes MiniMax models."""

    def test_detect_all_includes_minimax(self):
        """detect_all should include MiniMax models from cloud registry."""
        detector = ModelDetector()
        all_models = detector.detect_all()
        minimax_models = [m for m in all_models if m.provider == "MiniMax"]
        self.assertEqual(len(minimax_models), 4)

    def test_detect_all_minimax_ids(self):
        """detect_all should have all 4 MiniMax model IDs."""
        detector = ModelDetector()
        all_models = detector.detect_all()
        minimax_ids = {m.id for m in all_models if m.provider == "MiniMax"}
        expected = {
            "minimax:MiniMax-M2.7",
            "minimax:MiniMax-M2.7-highspeed",
            "minimax:MiniMax-M2.5",
            "minimax:MiniMax-M2.5-highspeed",
        }
        self.assertEqual(minimax_ids, expected)


if __name__ == "__main__":
    unittest.main()
