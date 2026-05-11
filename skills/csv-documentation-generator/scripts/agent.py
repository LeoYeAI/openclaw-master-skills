"""Agent detection module for CSV Documentation Generator

Simplified detection using environment variables and local config only.
Removed process scanning (psutil) and git config writing for security.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class AgentInfo:
    name: str
    mode: str
    confidence: float
    source: str


class AgentDetector:
    """Detect AI agent type and determine operating mode

    Detection priority:
    1. Environment variable (CSV_DOCS_MODE)
    2. Local config file (.csv-docs-config.json)
    3. Default: interactive
    """

    AGENT_ENV_VARS = {
        "OPENCLAW_MODE": "autonomous",
        "OPENCODE_MODE": "interactive",
        "CODEX_MODE": "interactive",
        "CURSOR_MODE": "interactive",
        "AGENT_MODE": None,
        "CSV_DOCS_MODE": None,
    }

    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path or Path.cwd()
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        config_path = self.project_path / ".csv-docs-config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _get_env_mode(self) -> Optional[str]:
        explicit_mode = os.getenv("CSV_DOCS_MODE")
        if explicit_mode:
            return explicit_mode

        for var, default_mode in self.AGENT_ENV_VARS.items():
            if var == "CSV_DOCS_MODE":
                continue
            value = os.getenv(var)
            if value:
                if default_mode:
                    return default_mode
                return value

        return None

    def _get_config_mode(self) -> Optional[str]:
        return self.config.get("agent", {}).get("default_mode")

    def detect(self) -> AgentInfo:
        if not self.config.get("agent", {}).get("auto_detect", True):
            mode = self._get_config_mode() or "interactive"
            return AgentInfo(
                name="Config",
                mode=mode,
                confidence=1.0,
                source="config (auto_detect=false)",
            )

        detected = self._get_env_mode()
        if detected:
            return AgentInfo(
                name="Environment",
                mode=detected,
                confidence=1.0,
                source="environment_variable",
            )

        detected = self._get_config_mode()
        if detected:
            return AgentInfo(
                name="Config",
                mode=detected,
                confidence=0.9,
                source="project_config",
            )

        return AgentInfo(
            name="Default",
            mode="interactive",
            confidence=1.0,
            source="default_fallback",
        )

    def set_mode(self, mode: str) -> bool:
        if mode not in ("interactive", "autonomous"):
            raise ValueError(
                f"Invalid mode: {mode}. Must be 'interactive' or 'autonomous'"
            )

        config_path = self.project_path / ".csv-docs-config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = {"agent": {}}

        config["agent"]["default_mode"] = mode
        config["agent"]["auto_detect"] = False

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True


def get_agent_mode(project_path: Optional[Path] = None) -> AgentInfo:
    """Convenience function to detect agent mode"""
    detector = AgentDetector(project_path)
    return detector.detect()


def set_agent_mode(
    mode: str, target: str = "config", project_path: Optional[Path] = None
) -> bool:
    """Convenience function to set agent mode"""
    detector = AgentDetector(project_path)
    return detector.set_mode(mode, target)
