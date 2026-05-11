"""Standards Reader for AI Agent Code Annotation Standards

This module provides a unified interface to read the Central Standards Registry
(standards/code-annotations.json) for code annotation conventions.

Skill-agnostic: can be used by any skill without coupling.
Uses {baseDir} relative path to locate standards file within skill directory.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any


class StandardsReader:
    """
    Reads and provides access to the Central Standards Registry.

    The standards file is located at:
        {skill_root}/standards/code-annotations.json

    If the file doesn't exist, built-in defaults are used.
    """

    def __init__(self, standards_path: Optional[str] = None):
        """
        Initialize StandardsReader.

        Args:
            standards_path: Optional custom path to standards file.
                          Defaults to {skill_root}/standards/code-annotations.json
        """
        if standards_path:
            self.standards_path = Path(standards_path)
        else:
            self.standards_path = self._get_default_standards_path()
        self._standards = None
        self._loaded = False

    def _get_default_standards_path(self) -> Path:
        """
        Get the default standards path within the skill directory.
        Uses Path(__file__).parent.parent to locate skill root.
        """
        skill_root = Path(__file__).parent.parent
        return skill_root / "standards" / "code-annotations.json"

    @property
    def standards(self) -> Dict[str, Any]:
        """Lazy load standards from file."""
        if not self._loaded:
            self._load()
        return self._standards or {}

    def _load(self) -> None:
        """Load standards from file, using defaults if not found."""
        self._loaded = True

        if self.standards_path.exists():
            try:
                with open(self.standards_path, "r", encoding="utf-8") as f:
                    self._standards = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(
                    f"Warning: Failed to load standards from {self.standards_path}: {e}"
                )
                self._standards = self._get_defaults()
        else:
            print(f"Info: Standards file not found at {self.standards_path}")
            print(f"      Using built-in defaults.")
            self._standards = self._get_defaults()

    def _get_defaults(self) -> Dict[str, Any]:
        """Return built-in default standards."""
        return {
            "version": "1.0",
            "description": "Built-in defaults (standards file not found)",
            "standards": {
                "requirement_markers": {
                    "enabled": True,
                    "patterns": [
                        {"style": "python", "pattern": "# @REQ {id} - {description}"},
                        {"style": "cpp", "pattern": "// @REQ {id} - {description}"},
                    ],
                },
                "test_markers": {
                    "enabled": True,
                    "patterns": [
                        {
                            "style": "python",
                            "pattern": "# @TEST[{type-id}] - {description}",
                        },
                        {
                            "style": "cpp",
                            "pattern": "// @TEST[{type-id}] - {description}",
                        },
                    ],
                },
                "risk_markers": {
                    "enabled": True,
                    "pattern": "// @RISK [{H|M|L}]",
                    "levels": {
                        "H": {"name": "High Risk"},
                        "M": {"name": "Medium Risk"},
                        "L": {"name": "Low Risk"},
                    },
                },
                "modules": {},
            },
            "configurable": True,
            "enforcement": "advisory",
        }

    def is_enabled(self, marker_type: str) -> bool:
        """
        Check if a marker type is enabled.

        Args:
            marker_type: One of 'requirement_markers', 'test_markers',
                        'design_markers', 'risk_markers'

        Returns:
            True if enabled, False otherwise
        """
        standards = self.standards.get("standards", {})
        marker = standards.get(marker_type, {})
        return marker.get("enabled", False)

    def get_requirement_patterns(self) -> List[Dict[str, str]]:
        """Get all requirement marker patterns."""
        if not self.is_enabled("requirement_markers"):
            return []

        standards = self.standards.get("standards", {})
        patterns = standards.get("requirement_markers", {}).get("patterns", [])
        return patterns

    def get_test_patterns(self) -> List[Dict[str, str]]:
        """Get all test marker patterns."""
        if not self.is_enabled("test_markers"):
            return []

        standards = self.standards.get("standards", {})
        patterns = standards.get("test_markers", {}).get("patterns", [])
        return patterns

    def get_design_patterns(self) -> List[Dict[str, str]]:
        """Get all design specification marker patterns (FS, TS)."""
        if not self.is_enabled("design_markers"):
            return []

        standards = self.standards.get("standards", {})
        patterns = standards.get("design_markers", {}).get("patterns", [])
        return patterns

    def get_risk_pattern(self) -> str:
        """Get the risk marker pattern."""
        if not self.is_enabled("risk_markers"):
            return ""

        standards = self.standards.get("standards", {})
        return standards.get("risk_markers", {}).get("pattern", "// @RISK [H/M/L]")

    def get_risk_levels(self) -> Dict[str, Dict[str, str]]:
        """Get risk level definitions."""
        if not self.is_enabled("risk_markers"):
            return {}

        standards = self.standards.get("standards", {})
        return standards.get("risk_markers", {}).get("levels", {})

    def get_modules(self) -> Dict[str, Dict[str, str]]:
        """Get module definitions."""
        standards = self.standards.get("standards", {})
        return standards.get("modules", {})

    def get_module_info(self, module_id: str) -> Optional[Dict[str, str]]:
        """Get information about a specific module."""
        modules = self.get_modules()
        return modules.get(module_id)

    def get_test_prefix(self, module_id: str) -> str:
        """Get the test prefix for a module."""
        module = self.get_module_info(module_id)
        if module:
            return module.get("test_prefix", module_id.upper()[:2])
        return module_id.upper()[:2]

    def should_enforce(self) -> bool:
        """Check if standards should be strictly enforced."""
        return self.standards.get("enforcement", "advisory") == "strict"

    def is_configurable(self) -> bool:
        """Check if standards are configurable."""
        return self.standards.get("configurable", True)

    def get_version(self) -> str:
        """Get the standards version."""
        return self.standards.get("version", "unknown")

    def get_purpose(self) -> str:
        """Get the purpose description."""
        return self.standards.get("purpose", "")

    def get_style_pattern(self, marker_type: str, style: str) -> Optional[str]:
        """
        Get pattern for a specific marker type and code style.

        Args:
            marker_type: One of 'requirement_markers', 'test_markers', 'design_markers'
            style: Code style (e.g., 'python', 'cpp', 'javascript')

        Returns:
            Pattern string or None if not found
        """
        if marker_type == "requirement_markers":
            patterns = self.get_requirement_patterns()
        elif marker_type == "test_markers":
            patterns = self.get_test_patterns()
        elif marker_type == "design_markers":
            patterns = self.get_design_patterns()
        else:
            return None

        for p in patterns:
            if p.get("style") == style:
                return p.get("pattern")
        return None

    def format_requirement_marker(
        self, req_id: str, description: str, style: str = "python"
    ) -> str:
        """
        Format a requirement marker string.

        Args:
            req_id: Requirement ID (e.g., 'URS-001')
            description: Requirement description
            style: Code style (default: 'python')

        Returns:
            Formatted marker string
        """
        pattern = self.get_style_pattern("requirement_markers", style)
        if not pattern:
            pattern = "# @REQ {id} - {description}"

        return pattern.replace("{id}", req_id).replace("{description}", description)

    def format_test_marker(
        self, test_id: str, description: str, style: str = "python"
    ) -> str:
        """
        Format a test marker string.

        Args:
            test_id: Test case ID (e.g., 'OQ-UM-001')
            description: Test description
            style: Code style (default: 'python')

        Returns:
            Formatted marker string
        """
        pattern = self.get_style_pattern("test_markers", style)
        if not pattern:
            pattern = "# @TEST[{type-id}] - {description}"

        return pattern.replace("{type-id}", test_id).replace(
            "{description}", description
        )

    def format_risk_marker(self, level: str) -> str:
        """
        Format a risk marker string.

        Args:
            level: Risk level ('H', 'M', or 'L')

        Returns:
            Formatted marker string
        """
        pattern = self.get_risk_pattern()
        return pattern.replace("{H|M|L}", level)

    def get_required_for_skills(self) -> List[str]:
        """Get list of skills that require these standards."""
        standards = self.standards.get("standards", {})
        req_markers = standards.get("requirement_markers", {})
        return req_markers.get("required_for_skills", [])

    def to_dict(self) -> Dict[str, Any]:
        """Return the full standards dictionary."""
        return self.standards.copy()

    def get_system_prompt_rules(self) -> str:
        """
        Get the standards formatted as rules text for system prompt.

        Returns:
            Multi-line string suitable for adding to system prompt
        """
        rules = [
            "Code Annotation Rules (for GxP traceability):",
            "- When writing code that implements requirements, add @REQ markers: # @REQ URS-xxx - description",
            "- When writing test cases, add @TEST markers: # @TEST[OQ-UM-xxx] - description",
            "- Mark high-risk code sections with @RISK H (security, compliance, audit trail related)",
            "- Mark medium-risk code with @RISK M",
            "- Mark low-risk code with @RISK L",
        ]
        return "\n".join(rules)


def get_reader() -> StandardsReader:
    """Convenience function to get a StandardsReader instance."""
    return StandardsReader()


if __name__ == "__main__":
    reader = StandardsReader()
    print(f"Standards Version: {reader.get_version()}")
    print(f"Standards Path: {reader.standards_path}")
    print(f"Configurable: {reader.is_configurable()}")
    print(f"Enforcement: {'strict' if reader.should_enforce() else 'advisory'}")
    print(f"\nRequirement Patterns:")
    for p in reader.get_requirement_patterns():
        print(f"  {p.get('style')}: {p.get('pattern')}")
    print(f"\nModules:")
    for mod_id, mod_info in reader.get_modules().items():
        print(f"  {mod_id}: {mod_info.get('name')} ({mod_info.get('test_prefix')})")
    print(f"\n--- System Prompt Rules ---")
    print(reader.get_system_prompt_rules())
