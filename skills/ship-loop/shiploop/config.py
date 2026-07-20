from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator


class SegmentStatus(str, Enum):
    PENDING = "pending"
    CODING = "coding"
    PREFLIGHT = "preflight"
    SHIPPING = "shipping"
    VERIFYING = "verifying"
    REPAIRING = "repairing"
    EXPERIMENTING = "experimenting"
    SHIPPED = "shipped"
    FAILED = "failed"

    # Aliases for crash recovery detection
    @classmethod
    def active_states(cls) -> set[SegmentStatus]:
        return {cls.CODING, cls.PREFLIGHT, cls.SHIPPING, cls.VERIFYING, cls.REPAIRING, cls.EXPERIMENTING}


class BranchStrategy(str, Enum):
    DIRECT = "direct-to-main"
    PER_SEGMENT = "per-segment"
    PR = "pr"


class SegmentConfig(BaseModel):
    name: str
    status: SegmentStatus = SegmentStatus.PENDING
    prompt: str
    depends_on: list[str] = []
    commit: str | None = None
    deploy_url: str | None = None
    tag: str | None = None
    # TODO: touched_paths is reserved for future parallel execution (not yet implemented)
    touched_paths: list[str] = []


class BudgetConfig(BaseModel):
    max_usd_per_segment: float = 10.0
    max_usd_per_run: float = 50.0
    max_tokens_per_segment: int = 500_000
    halt_on_breach: bool = True
    optimization_budget_usd: float = 5.0
    model_pricing: dict[str, dict[str, float]] = {}


class RepairConfig(BaseModel):
    max_attempts: int = 3


class OptimizationConfig(BaseModel):
    enabled: bool = True
    max_experiments: int = 2
    min_repair_attempts: int = 1
    min_repair_diff_lines: int = 5
    budget_usd: float = 5.0


class MetaConfig(BaseModel):
    enabled: bool = True
    experiments: int = 3


class TimeoutsConfig(BaseModel):
    agent: int = 900
    deploy: int = 300
    preflight: int = 300


class ReflectionConfig(BaseModel):
    enabled: bool = True
    auto_run: bool = True
    history_depth: int = 10


class PreflightConfig(BaseModel):
    build: str | None = None
    lint: str | None = None
    test: str | None = None


class DeployConfig(BaseModel):
    provider: str = "vercel"
    routes: list[str] = ["/"]
    marker: str | None = None
    health_endpoint: str | None = None
    deploy_header: str | None = None
    script: str | None = None
    timeout: int = 300


AGENT_PRESETS: dict[str, str] = {
    "claude-code": "claude --print --permission-mode bypassPermissions",
    "codex": "codex --quiet",
    "aider": "aider --yes-always --no-git",
}


class ShipLoopConfig(BaseModel):
    project: str
    repo: str
    site: str
    platform: str = "vercel"
    branch_strategy: BranchStrategy = Field(default=BranchStrategy.PR, alias="branch")
    mode: str = "solo"
    agent: str | None = None
    agent_command: str = ""
    preflight: PreflightConfig = PreflightConfig()
    deploy: DeployConfig = Field(default_factory=DeployConfig)
    repair: RepairConfig = RepairConfig()
    meta: MetaConfig = MetaConfig()
    optimization: OptimizationConfig = OptimizationConfig()
    budget: BudgetConfig = BudgetConfig()
    timeouts: TimeoutsConfig = TimeoutsConfig()
    reflection: ReflectionConfig = ReflectionConfig()
    router: dict[str, str] = {}
    blocked_patterns: list[str] = []
    segments: list[SegmentConfig]

    model_config = {"populate_by_name": True}

    @field_validator("repo")
    @classmethod
    def resolve_repo_path(cls, v: str) -> str:
        expanded = Path(v).expanduser().resolve()
        return str(expanded)

    @model_validator(mode="before")
    @classmethod
    def migrate_verify_to_deploy(cls, data: dict[str, Any]) -> dict[str, Any]:
        if "verify" in data and "deploy" not in data:
            verify = data.pop("verify")
            data["deploy"] = verify
        if "branch" not in data and "branch_strategy" in data:
            data["branch"] = data.pop("branch_strategy")
        return data

    @model_validator(mode="after")
    def resolve_agent_preset(self) -> ShipLoopConfig:
        if self.agent_command:
            return self
        if self.agent and self.agent in AGENT_PRESETS:
            self.agent_command = AGENT_PRESETS[self.agent]
        elif self.agent:
            raise ValueError(
                f"Unknown agent preset '{self.agent}'. "
                f"Available: {', '.join(AGENT_PRESETS)}. "
                f"Or set agent_command directly."
            )
        if not self.agent_command:
            raise ValueError("Either 'agent' or 'agent_command' must be set")
        return self


def load_config(config_path: Path) -> ShipLoopConfig:
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    raw = yaml.safe_load(config_path.read_text())
    if not raw:
        raise ValueError(f"Empty config file: {config_path}")
    return ShipLoopConfig.model_validate(raw)


def save_config(config: ShipLoopConfig, config_path: Path) -> None:
    data = _config_to_serializable(config)
    content = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    tmp_path = config_path.with_suffix(".yml.tmp")
    tmp_path.write_text(content)
    os.replace(str(tmp_path), str(config_path))


def _config_to_serializable(config: ShipLoopConfig) -> dict[str, Any]:
    data = config.model_dump(by_alias=True)
    data["branch"] = config.branch_strategy.value
    for seg in data.get("segments", []):
        seg["status"] = seg["status"].value if hasattr(seg["status"], "value") else seg["status"]
    # Drop None values for cleaner YAML
    return _strip_none(data)


def _strip_none(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_none(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_none(item) for item in obj]
    return obj
