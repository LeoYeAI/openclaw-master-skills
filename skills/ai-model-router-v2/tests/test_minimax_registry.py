#!/usr/bin/env python3
"""Offline registry and routing-output tests; this skill has no inference client."""

import io
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skill"))

from core.router import RouterCore, main  # noqa: E402
from modules.detector import ModelDetector, MINIMAX_ENDPOINTS  # noqa: E402


class TestMiniMaxRegistry(unittest.TestCase):
    def setUp(self):
        self.detector = ModelDetector()
        registry = self.detector.get_cloud_registry()
        self.by_id = {m.id: m for m in registry}
        self.minimax = [m for m in registry if m.provider == "MiniMax"]

    def test_current_models_registered_flash_first(self):
        self.assertEqual(
            [m.id for m in self.minimax],
            ["minimax:MiniMax-M3.1-Flash", "minimax:MiniMax-M3"],
        )
        for model in self.minimax:
            self.assertEqual(model.type, "cloud")
            self.assertEqual(model.capabilities, ["chat", "vision"])
            self.assertEqual(model.input_modalities, ["text", "image", "video"])
            self.assertEqual(model.context_window, 1_000_000)
            self.assertEqual(model.openai_base_url, "https://api.minimax.io/v1")
            self.assertEqual(model.anthropic_base_url, "https://api.minimax.io/anthropic")

    def test_flash_parameters(self):
        model = self.by_id["minimax:MiniMax-M3.1-Flash"]
        self.assertEqual(model.max_output_tokens, 524_288)
        self.assertEqual(model.thinking, ["adaptive"])
        self.assertEqual(model.reasoning_efforts, ["low", "medium", "high", "xhigh", "max"])
        self.assertEqual(
            model.pricing_usd_per_million_tokens,
            {"input": 0.15, "output": 0.6, "cache_read": 0.015, "cache_write": None},
        )
        self.assertIsNone(model.pricing_tiers_usd_per_million_tokens)

    def test_m3_parameters(self):
        model = self.by_id["minimax:MiniMax-M3"]
        self.assertEqual(model.thinking, ["adaptive", "disabled"])
        self.assertIsNone(model.reasoning_efforts)
        self.assertEqual(
            model.pricing_usd_per_million_tokens,
            {"input": 0.3, "output": 1.2, "cache_read": 0.06, "cache_write": None},
        )
        self.assertEqual(model.pricing_tiers_usd_per_million_tokens, {
            "<=512k": {"input": 0.3, "output": 1.2, "cache_read": 0.06},
            ">512k": {"input": 0.6, "output": 2.4, "cache_read": 0.12},
        })

    def test_regional_endpoints(self):
        endpoints = self.detector.get_cloud_endpoints()["MiniMax"]
        self.assertEqual(endpoints, MINIMAX_ENDPOINTS)
        for region, host in (("global_en", "api.minimax.io"), ("cn_zh", "api.minimaxi.com")):
            with self.subTest(region=region):
                self.assertEqual(endpoints[region]["openai_base_url"], f"https://{host}/v1")
                self.assertEqual(endpoints[region]["anthropic_base_url"], f"https://{host}/anthropic")


class TestRoutingOutput(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.directory.cleanup)
        self.home = Path(self.directory.name)
        self.config = self.home / ".model-router" / "models.json"
        self.config.parent.mkdir()

    def run_cli(self, *args):
        output = io.StringIO()
        with patch.dict(os.environ, {"HOME": str(self.home)}), \
                patch.object(sys, "argv", ["router.py", *args]), \
                patch("sys.stdout", output), \
                patch.object(ModelDetector, "detect_local", return_value=[]):
            main()
        return output.getvalue()

    def save_models(self, primary, secondary):
        data = {
            "primary_model": {"id": primary},
            "secondary_model": {"id": secondary},
            "models": [
                {"id": model_id, "name": model_id, "provider": "MiniMax", "type": "cloud"}
                for model_id in (primary, secondary)
            ],
        }
        self.config.write_text(json.dumps(data))
        return self.config.read_bytes()

    def test_fresh_cli_catalog_has_only_current_minimax_choices(self):
        choices = [line.split()[0] for line in self.run_cli("--list").splitlines()]
        self.assertEqual([x for x in choices if x.startswith("minimax:")], [
            "minimax:MiniMax-M3.1-Flash", "minimax:MiniMax-M3",
        ])
        self.assertEqual(len(choices), 7)

    def test_standalone_cli_loads_catalog_without_pythonpath(self):
        router_path = Path(__file__).resolve().parents[1] / "skill" / "core" / "router.py"
        result = subprocess.run(
            [sys.executable, str(router_path), "--list"],
            cwd=self.home,
            env={"HOME": str(self.home), "PYTHONDONTWRITEBYTECODE": "1"},
            capture_output=True, text=True, check=True, timeout=10,
        )
        choices = [line.split()[0] for line in result.stdout.splitlines()]
        self.assertEqual([x for x in choices if x.startswith("minimax:")], [
            "minimax:MiniMax-M3.1-Flash", "minimax:MiniMax-M3",
        ])

    def test_standalone_cli_preserves_saved_legacy_selection(self):
        original = self.save_models("minimax:MiniMax-M2.7", "minimax:MiniMax-M3.1-Flash")
        router_path = Path(__file__).resolve().parents[1] / "skill" / "core" / "router.py"
        result = subprocess.run(
            [sys.executable, str(router_path), "--json", "--force", "primary", "Hello"],
            cwd=self.home,
            env={"HOME": str(self.home), "PYTHONDONTWRITEBYTECODE": "1"},
            capture_output=True, text=True, check=True, timeout=10,
        )
        self.assertEqual(json.loads(result.stdout)["model_id"], "minimax:MiniMax-M2.7")
        self.assertEqual(self.config.read_bytes(), original)

    def test_registry_output_keeps_metadata(self):
        with patch.object(ModelDetector, "detect_local", return_value=[]):
            router = RouterCore(self.config)
        models = json.loads(json.dumps(router.list_models()))
        flash = next(model for model in models if model["id"] == "minimax:MiniMax-M3.1-Flash")
        self.assertEqual(flash["max_output_tokens"], 524_288)
        self.assertEqual(flash["thinking"], ["adaptive"])
        self.assertEqual(flash["input_modalities"], ["text", "image", "video"])

    def test_flash_and_m3_cli_route_without_changing_saved_config(self):
        original = self.save_models("minimax:MiniMax-M3.1-Flash", "minimax:MiniMax-M3")
        for task, expected in (("Hello", "minimax:MiniMax-M3.1-Flash"),
                               ("Design architecture", "minimax:MiniMax-M3")):
            with self.subTest(task=task):
                result = json.loads(self.run_cli("--json", task))
                self.assertEqual(result["model_id"], expected)
                self.assertEqual(self.config.read_bytes(), original)

    def test_saved_legacy_and_custom_ids_are_not_reset(self):
        for model_id in ("minimax:MiniMax-M2.7", "minimax:MiniMax-M2.5", "minimax:custom-model"):
            with self.subTest(model_id=model_id):
                original = self.save_models(model_id, "minimax:MiniMax-M3.1-Flash")
                result = json.loads(self.run_cli("--json", "--force", "primary", "Hello"))
                self.assertEqual(result["model_id"], model_id)
                self.assertIn(model_id, self.run_cli("--list"))
                self.assertEqual(self.config.read_bytes(), original)

    def test_history_survives_registry_refresh_and_route(self):
        self.save_models("minimax:MiniMax-M3.1-Flash", "minimax:MiniMax-M3")
        history = {
            "conversation": {
                "id": "conversation", "started_at": "2026-10-20", "transitions": 0,
                "last_model": "minimax:MiniMax-M2.7",
                "messages": [{"role": "assistant", "content": "Previous response",
                              "model": "minimax:MiniMax-M2.7", "type": "primary"}],
            },
        }
        contexts = self.config.parent / "contexts.json"
        contexts.write_text(json.dumps(history))
        original = contexts.read_bytes()
        router = RouterCore(self.config)
        result = router.route("Design architecture", conversation_id="conversation")
        self.assertEqual(result.model_id, "minimax:MiniMax-M3")
        self.assertEqual(result.previous_model, "minimax:MiniMax-M2.7")
        self.assertTrue(result.is_switch)
        self.assertEqual(router.get_conversation("conversation")["messages"],
                         history["conversation"]["messages"])
        self.assertEqual(contexts.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
