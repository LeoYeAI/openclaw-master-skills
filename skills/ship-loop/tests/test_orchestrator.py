import tempfile
from pathlib import Path

import pytest
import yaml

from shiploop.config import SegmentStatus, load_config, save_config
from shiploop.orchestrator import Orchestrator


@pytest.fixture
def config_path():
    data = {
        "project": "TestProject",
        "repo": "/tmp/test-repo",
        "site": "https://example.com",
        "agent_command": "echo test",
        "segments": [
            {"name": "seg-1", "prompt": "Build feature 1", "depends_on": []},
            {"name": "seg-2", "prompt": "Build feature 2", "depends_on": ["seg-1"]},
            {"name": "seg-3", "prompt": "Build feature 3", "depends_on": ["seg-1"]},
            {"name": "seg-4", "prompt": "Build feature 4", "depends_on": ["seg-2", "seg-3"]},
        ],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(data, f)
        path = Path(f.name)
    yield path
    path.unlink(missing_ok=True)


class TestOrchestrator:
    def test_find_eligible_initial(self, config_path):
        orch = Orchestrator(config_path)
        eligible = orch._find_eligible_segments()
        assert eligible == [0]  # Only seg-1 has no deps

    def test_find_eligible_after_first_shipped(self, config_path):
        orch = Orchestrator(config_path)
        orch.config.segments[0].status = SegmentStatus.SHIPPED
        orch._checkpoint()

        eligible = orch._find_eligible_segments()
        assert sorted(eligible) == [1, 2]  # seg-2 and seg-3 both depend only on seg-1

    def test_find_eligible_all_shipped(self, config_path):
        orch = Orchestrator(config_path)
        for seg in orch.config.segments:
            seg.status = SegmentStatus.SHIPPED
        orch._checkpoint()

        eligible = orch._find_eligible_segments()
        assert eligible == []

    def test_dag_with_multiple_deps(self, config_path):
        orch = Orchestrator(config_path)
        orch.config.segments[0].status = SegmentStatus.SHIPPED
        orch.config.segments[1].status = SegmentStatus.SHIPPED
        orch._checkpoint()

        eligible = orch._find_eligible_segments()
        # seg-3 is eligible (depends on seg-1 which is shipped)
        # seg-4 is NOT eligible (depends on seg-2 AND seg-3, seg-3 is still pending)
        assert 2 in eligible
        assert 3 not in eligible

    def test_dag_all_deps_met(self, config_path):
        orch = Orchestrator(config_path)
        for seg in orch.config.segments[:3]:
            seg.status = SegmentStatus.SHIPPED
        orch._checkpoint()

        eligible = orch._find_eligible_segments()
        assert eligible == [3]

    def test_crash_recovery(self, config_path):
        orch = Orchestrator(config_path)
        orch.config.segments[0].status = SegmentStatus.CODING
        orch.config.segments[1].status = SegmentStatus.REPAIRING
        save_config(orch.config, config_path)

        orch2 = Orchestrator(config_path)
        recovered = orch2._recover_crashed_segments()
        assert set(recovered) == {"seg-1", "seg-2"}
        assert orch2.config.segments[0].status == SegmentStatus.FAILED
        assert orch2.config.segments[1].status == SegmentStatus.FAILED

    def test_reset_segment(self, config_path):
        orch = Orchestrator(config_path)
        orch.config.segments[0].status = SegmentStatus.FAILED
        orch.config.segments[0].commit = "abc123"
        orch._checkpoint()

        assert orch.reset_segment("seg-1") is True
        reloaded = load_config(config_path)
        assert reloaded.segments[0].status == SegmentStatus.PENDING
        assert reloaded.segments[0].commit is None

    def test_reset_nonexistent_segment(self, config_path):
        orch = Orchestrator(config_path)
        assert orch.reset_segment("does-not-exist") is False

    def test_get_status(self, config_path):
        orch = Orchestrator(config_path)
        orch.config.segments[0].status = SegmentStatus.SHIPPED
        orch.config.segments[0].commit = "abc123"

        statuses = orch.get_status()
        assert len(statuses) == 4
        assert statuses[0]["status"] == "shipped"
        assert statuses[0]["commit"] == "abc123"
        assert statuses[1]["depends_on"] == ["seg-1"]

    def test_checkpoint_persists(self, config_path):
        orch = Orchestrator(config_path)
        orch._set_segment_status(orch.config.segments[0], SegmentStatus.CODING)

        reloaded = load_config(config_path)
        assert reloaded.segments[0].status == SegmentStatus.CODING
