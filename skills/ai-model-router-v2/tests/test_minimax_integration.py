#!/usr/bin/env python3
"""Integration tests for MiniMax model routing in ai-model-router-v2.

These tests verify end-to-end routing behavior when MiniMax is configured
as a cloud provider. They do NOT make live API calls to MiniMax.
"""

import os
import sys
import json
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skill"))

from core.router import RouterCore
from modules.detector import ModelDetector


class TestMiniMaxEndToEndRouting(unittest.TestCase):
    """Integration tests for MiniMax routing with full config lifecycle."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmpdir, "models.json")

    def _create_router_with_minimax_secondary(self):
        """Create a router with MiniMax M2.7 as secondary model."""
        config = {
            "primary_model": {"id": "ollama:llama3:8b"},
            "secondary_model": {"id": "minimax:MiniMax-M2.7"},
            "models": [
                {"id": "ollama:llama3:8b", "name": "Llama 3 8B", "provider": "Ollama",
                 "type": "local", "cost_score": 0, "power_score": 35},
                {"id": "minimax:MiniMax-M2.7", "name": "MiniMax M2.7", "provider": "MiniMax",
                 "type": "cloud", "cost_score": 3, "power_score": 85,
                 "requires_api_key": True, "api_key_env": "MINIMAX_API_KEY",
                 "capabilities": ["chat", "vision", "tools"]},
                {"id": "minimax:MiniMax-M2.5-highspeed", "name": "MiniMax M2.5 Highspeed",
                 "provider": "MiniMax", "type": "cloud", "cost_score": 1, "power_score": 60,
                 "requires_api_key": True, "api_key_env": "MINIMAX_API_KEY",
                 "capabilities": ["chat", "tools"]},
            ]
        }
        with open(self.config_path, "w") as f:
            json.dump(config, f)
        return RouterCore(config_path=self.config_path)

    def test_complex_task_routing_to_minimax(self):
        """Complex tasks should be routed to MiniMax M2.7 when configured as secondary."""
        router = self._create_router_with_minimax_secondary()
        tasks = [
            "Design a scalable microservices architecture",
            "Implement a comprehensive end-to-end testing framework",
            "Analyze and optimize the database query performance",
        ]
        for task in tasks:
            result = router.route(task)
            self.assertEqual(result.model_id, "minimax:MiniMax-M2.7",
                             f"Task '{task}' should route to MiniMax M2.7")

    def test_simple_task_stays_local(self):
        """Simple tasks should stay on local model, not MiniMax."""
        router = self._create_router_with_minimax_secondary()
        tasks = [
            "What is a for loop?",
            "Show me a Python syntax example",
            "What is HTTP?",
        ]
        for task in tasks:
            result = router.route(task)
            self.assertEqual(result.model_id, "ollama:llama3:8b",
                             f"Task '{task}' should stay on local model")

    def test_model_list_includes_minimax(self):
        """list_models should include MiniMax models."""
        router = self._create_router_with_minimax_secondary()
        models = router.list_models()
        minimax_models = [m for m in models if m["provider"] == "MiniMax"]
        self.assertEqual(len(minimax_models), 2)
        model_ids = {m["id"] for m in minimax_models}
        self.assertIn("minimax:MiniMax-M2.7", model_ids)
        self.assertIn("minimax:MiniMax-M2.5-highspeed", model_ids)

    def test_auto_detect_includes_minimax_in_registry(self):
        """Auto-detect mode should discover MiniMax models from cloud registry."""
        # No config file => auto-detect mode
        no_config_path = os.path.join(self.tmpdir, "nonexistent.json")
        router = RouterCore(config_path=no_config_path)
        minimax_models = [m for m in router.models if m.provider == "MiniMax"]
        self.assertGreater(len(minimax_models), 0,
                           "Auto-detect should include MiniMax from cloud registry")

    def test_status_with_minimax_secondary(self):
        """Router status should reflect MiniMax as secondary."""
        router = self._create_router_with_minimax_secondary()
        status = router.get_status()
        self.assertEqual(status["secondary_id"], "minimax:MiniMax-M2.7")

    def test_privacy_override_prevents_minimax(self):
        """Privacy-sensitive content should never route to MiniMax cloud."""
        router = self._create_router_with_minimax_secondary()
        sensitive_tasks = [
            "password=hunter2secretword",
            "Use API key sk-abcdefghijklmnop1234",
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9abcdef",
        ]
        for task in sensitive_tasks:
            result = router.route(task)
            self.assertEqual(result.model_id, "ollama:llama3:8b",
                             f"Sensitive task should not route to MiniMax: {task}")
            self.assertGreater(len(result.privacy_detected), 0)


if __name__ == "__main__":
    unittest.main()
