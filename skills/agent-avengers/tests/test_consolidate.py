#!/usr/bin/env python3
"""Tests for consolidate.py"""

import json
import os
import sys
import tempfile
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from consolidate import (
    collect_outputs,
    validate_outputs,
    generate_summary,
)


class TestCollectOutputs:
    """Test collecting agent output files"""
    
    def test_collect_existing_outputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mission_path = Path(tmpdir)
            outputs_dir = mission_path / "outputs"
            outputs_dir.mkdir()
            
            # Create sample output files
            (outputs_dir / "agent_01.md").write_text("# Agent 1 Output\nResult A")
            (outputs_dir / "agent_02.md").write_text("# Agent 2 Output\nResult B")
            
            plan = {
                "commands": [
                    {"agent_id": "agent_01"},
                    {"agent_id": "agent_02"}
                ]
            }
            
            results = collect_outputs(mission_path, plan)
            
            assert len(results) == 2
            assert results[0]["status"] == "completed"
            assert results[1]["status"] == "completed"
            assert "Result A" in results[0]["content"]
    
    def test_handle_missing_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mission_path = Path(tmpdir)
            outputs_dir = mission_path / "outputs"
            outputs_dir.mkdir()
            
            plan = {
                "commands": [
                    {"agent_id": "missing_agent"}
                ]
            }
            
            results = collect_outputs(mission_path, plan)
            
            assert len(results) == 1
            assert results[0]["status"] == "missing"
            assert results[0]["content"] is None


class TestValidateOutputs:
    """Test output validation"""
    
    def test_all_completed(self):
        results = [
            {"agent_id": "a1", "status": "completed", "size": 100},
            {"agent_id": "a2", "status": "completed", "size": 200}
        ]
        
        validation = validate_outputs(results)
        
        assert validation["total"] == 2
        assert validation["completed"] == 2
        assert validation["missing"] == 0
        assert validation["success"] is True
    
    def test_some_missing(self):
        results = [
            {"agent_id": "a1", "status": "completed", "size": 100},
            {"agent_id": "a2", "status": "missing", "size": 0}
        ]
        
        validation = validate_outputs(results)
        
        assert validation["completed"] == 1
        assert validation["missing"] == 1
        assert validation["success"] is False
        assert len(validation["issues"]) == 1
    
    def test_empty_outputs(self):
        results = [
            {"agent_id": "a1", "status": "completed", "size": 0}
        ]
        
        validation = validate_outputs(results)
        
        assert validation["empty"] == 1
        assert validation["success"] is False


class TestGenerateSummary:
    """Test summary generation"""
    
    def test_summary_structure(self):
        mission = {
            "id": "test_123",
            "task": "Test mission",
            "created_at": "2026-02-06T12:00:00"
        }
        
        results = [
            {
                "agent_id": "agent_01",
                "status": "completed",
                "content": "Research findings here",
                "size": 50
            }
        ]
        
        validation = {
            "total": 1,
            "completed": 1,
            "missing": 0,
            "empty": 0,
            "success": True,
            "issues": []
        }
        
        summary = generate_summary(mission, results, validation)
        
        assert "test_123" in summary
        assert "Test mission" in summary
        assert "Research findings here" in summary
        assert "✅ 성공" in summary
    
    def test_summary_with_issues(self):
        mission = {
            "id": "test_456",
            "task": "Failed mission",
            "created_at": "2026-02-06T12:00:00"
        }
        
        results = [
            {"agent_id": "a1", "status": "missing", "content": None, "size": 0}
        ]
        
        validation = {
            "total": 1,
            "completed": 0,
            "missing": 1,
            "empty": 0,
            "success": False,
            "issues": ["누락: a1"]
        }
        
        summary = generate_summary(mission, results, validation)
        
        assert "⚠️ 일부 실패" in summary
        assert "누락: a1" in summary


class TestConsolidateIntegration:
    """Integration tests for consolidation"""
    
    def test_full_consolidation_workflow(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mission_path = Path(tmpdir)
            outputs_dir = mission_path / "outputs"
            outputs_dir.mkdir()
            
            # Create mission file
            mission = {
                "id": "integration_test",
                "task": "Test consolidation workflow",
                "created_at": "2026-02-06T12:00:00",
                "agents": [
                    {"id": "agent_01", "type": "researcher"},
                    {"id": "agent_02", "type": "analyst"}
                ]
            }
            (mission_path / "mission.json").write_text(json.dumps(mission))
            
            # Create plan
            plan = {
                "commands": [
                    {"agent_id": "agent_01"},
                    {"agent_id": "agent_02"}
                ]
            }
            
            # Create output files
            (outputs_dir / "agent_01.md").write_text("# Research\nFound important data about X.")
            (outputs_dir / "agent_02.md").write_text("# Analysis\nData shows trend Y.")
            
            # Collect outputs
            results = collect_outputs(mission_path, plan)
            assert len(results) == 2
            
            # Validate
            validation = validate_outputs(results)
            assert validation["success"] is True
            
            # Generate summary
            summary = generate_summary(mission, results, validation)
            
            assert "integration_test" in summary
            assert "Found important data" in summary
            assert "Data shows trend" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
