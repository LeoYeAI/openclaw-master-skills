import tempfile
from pathlib import Path

import pytest
import yaml

from shiploop.config import (
    BranchStrategy,
    SegmentStatus,
    ShipLoopConfig,
    load_config,
    save_config,
)


@pytest.fixture
def minimal_config_data():
    return {
        "project": "TestProject",
        "repo": "/tmp/test-repo",
        "site": "https://example.com",
        "agent_command": "echo test",
        "segments": [
            {"name": "seg-1", "prompt": "Do something"},
        ],
    }


@pytest.fixture
def full_config_data():
    return {
        "project": "FullProject",
        "repo": "/tmp/test-repo",
        "site": "https://example.com",
        "platform": "vercel",
        "branch": "pr",
        "mode": "solo",
        "agent_command": "claude --print",
        "preflight": {
            "build": "npm run build",
            "lint": "npm run lint",
            "test": "npm test",
        },
        "deploy": {
            "provider": "vercel",
            "routes": ["/", "/api/health"],
            "marker": "data-version",
            "timeout": 600,
        },
        "repair": {"max_attempts": 5},
        "meta": {"enabled": True, "experiments": 4},
        "budget": {
            "max_usd_per_segment": 15.0,
            "max_usd_per_run": 100.0,
        },
        "blocked_patterns": ["*.pem", "secret.txt"],
        "segments": [
            {"name": "dark-mode", "prompt": "Add dark mode", "depends_on": []},
            {"name": "auth", "prompt": "Add auth", "depends_on": ["dark-mode"]},
        ],
    }


def test_load_minimal_config(minimal_config_data):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(minimal_config_data, f)
        config_path = Path(f.name)

    config = load_config(config_path)
    assert config.project == "TestProject"
    assert config.branch_strategy == BranchStrategy.PR
    assert len(config.segments) == 1
    assert config.segments[0].name == "seg-1"
    assert config.segments[0].status == SegmentStatus.PENDING
    assert config.repair.max_attempts == 3
    assert config.meta.enabled is True

    config_path.unlink()


def test_load_full_config(full_config_data):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(full_config_data, f)
        config_path = Path(f.name)

    config = load_config(config_path)
    assert config.project == "FullProject"
    assert config.branch_strategy == BranchStrategy.PR
    assert config.repair.max_attempts == 5
    assert config.meta.experiments == 4
    assert config.deploy.timeout == 600
    assert len(config.segments) == 2
    assert config.segments[1].depends_on == ["dark-mode"]
    assert config.budget.max_usd_per_segment == 15.0

    config_path.unlink()


def test_save_and_reload_config(full_config_data):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(full_config_data, f)
        config_path = Path(f.name)

    config = load_config(config_path)
    config.segments[0].status = SegmentStatus.SHIPPED
    config.segments[0].commit = "abc123"

    save_config(config, config_path)
    reloaded = load_config(config_path)

    assert reloaded.segments[0].status == SegmentStatus.SHIPPED
    assert reloaded.segments[0].commit == "abc123"
    assert reloaded.segments[1].status == SegmentStatus.PENDING

    config_path.unlink()


def test_segment_status_active_states():
    active = SegmentStatus.active_states()
    assert SegmentStatus.CODING in active
    assert SegmentStatus.REPAIRING in active
    assert SegmentStatus.PENDING not in active
    assert SegmentStatus.SHIPPED not in active
    assert SegmentStatus.FAILED not in active


def test_missing_config_file():
    with pytest.raises(FileNotFoundError):
        load_config(Path("/nonexistent/SHIPLOOP.yml"))


def test_empty_config_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write("")
        config_path = Path(f.name)

    with pytest.raises(ValueError, match="Empty config"):
        load_config(config_path)

    config_path.unlink()


def test_verify_to_deploy_migration():
    data = {
        "project": "Test",
        "repo": "/tmp/test",
        "site": "https://example.com",
        "agent_command": "echo test",
        "verify": {
            "routes": ["/", "/health"],
            "marker": "v1",
        },
        "segments": [{"name": "s1", "prompt": "p1"}],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(data, f)
        config_path = Path(f.name)

    config = load_config(config_path)
    assert config.deploy.routes == ["/", "/health"]
    assert config.deploy.marker == "v1"

    config_path.unlink()
