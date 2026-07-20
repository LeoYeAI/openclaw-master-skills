from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import yaml

from shiploop.cli import main


@pytest.fixture
def config_path():
    data = {
        "project": "CLITest",
        "repo": "/tmp/test-repo",
        "site": "https://example.com",
        "agent_command": "echo test",
        "segments": [{"name": "seg-1", "prompt": "Do something"}],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(data, f)
        path = Path(f.name)
    yield str(path)
    path.unlink(missing_ok=True)


class TestCLIBasics:
    def test_no_command_prints_help(self, capsys):
        ret = main([])
        assert ret == 0

    def test_version_flag(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0

    def test_missing_config(self):
        ret = main(["-c", "/nonexistent/SHIPLOOP.yml", "status"])
        assert ret == 1


class TestStatusCommand:
    def test_status_shows_segments(self, config_path, capsys):
        ret = main(["-c", config_path, "status"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "seg-1" in captured.out
        assert "pending" in captured.out


class TestResetCommand:
    def test_reset_nonexistent_segment(self, config_path, capsys):
        ret = main(["-c", config_path, "reset", "nonexistent"])
        assert ret == 1

    def test_reset_existing_segment(self, config_path, capsys):
        ret = main(["-c", config_path, "reset", "seg-1"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "Reset" in captured.out


class TestDryRunFlag:
    def test_dry_run_parses(self, config_path):
        with patch("shiploop.cli.Orchestrator") as mock_orch:
            mock_instance = MagicMock()
            mock_orch.return_value = mock_instance
            mock_instance.run = AsyncMock(return_value=True)
            ret = main(["-c", config_path, "run", "--dry-run"])
        assert ret == 0
        mock_instance.run.assert_called_once_with(dry_run=True)


class TestBudgetCommand:
    def test_budget_shows_summary(self, config_path, capsys):
        ret = main(["-c", config_path, "budget"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "Budget Summary" in captured.out
