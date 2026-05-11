"""Template versioning module for CSV Documentation Generator

Handles template version tracking and compatibility checking.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


TEMPLATE_VERSION = "1.2.0"

COMPATIBILITY_RULES = {
    "1.0.0": {"min_generator": "1.0.0", "breaking": []},
    "1.1.0": {"min_generator": "1.1.0", "breaking": []},
    "1.2.0": {"min_generator": "1.2.0", "breaking": []},
}


@dataclass
class VersionInfo:
    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls, version: str) -> "VersionInfo":
        parts = version.split(".")
        return cls(
            major=int(parts[0]) if len(parts) > 0 else 0,
            minor=int(parts[1]) if len(parts) > 1 else 0,
            patch=int(parts[2]) if len(parts) > 2 else 0,
        )

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __ge__(self, other: "VersionInfo") -> bool:
        return (self.major, self.minor, self.patch) >= (
            other.major,
            other.minor,
            other.patch,
        )

    def __lt__(self, other: "VersionInfo") -> bool:
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )


@dataclass
class CompatibilityResult:
    compatible: bool
    current_version: str
    required_version: Optional[str]
    message: str


def get_template_version(db: Dict[str, Any]) -> Optional[str]:
    """Get template version from requirements database"""
    return db.get("template_version") or db.get("version")


def set_template_version(db: Dict[str, Any], version: str) -> Dict[str, Any]:
    """Set template version in requirements database"""
    db["template_version"] = version
    return db


def check_template_compatibility(
    db: Dict[str, Any], generator_version: str = TEMPLATE_VERSION
) -> CompatibilityResult:
    """Check if template version is compatible with generator

    Args:
        db: Requirements database
        generator_version: Current generator version

    Returns:
        CompatibilityResult with compatibility status and message
    """
    template_version = get_template_version(db)

    if not template_version:
        return CompatibilityResult(
            compatible=True,
            current_version=generator_version,
            required_version=None,
            message="No template version specified, assuming compatible",
        )

    template_v = VersionInfo.from_string(template_version)
    generator_v = VersionInfo.from_string(generator_version)

    if template_v > generator_v:
        return CompatibilityResult(
            compatible=False,
            current_version=generator_version,
            required_version=template_version,
            message=f"Template version {template_version} requires generator >= {template_version}. Current: {generator_version}",
        )

    for rule_version, rule in COMPATIBILITY_RULES.items():
        rule_v = VersionInfo.from_string(rule_version)
        if template_v >= rule_v:
            min_gen = VersionInfo.from_string(rule["min_generator"])
            if generator_v < min_gen:
                return CompatibilityResult(
                    compatible=False,
                    current_version=generator_version,
                    required_version=rule["min_generator"],
                    message=f"Template {template_version} requires generator >= {rule['min_generator']}. Current: {generator_version}",
                )

    return CompatibilityResult(
        compatible=True,
        current_version=generator_version,
        required_version=None,
        message=f"Template {template_version} is compatible with generator {generator_version}",
    )


def detect_template_version_from_file(file_path: Path) -> Optional[str]:
    """Detect template version from a template file

    Looks for version markers like:
    - <!-- template-version: 1.2.0 -->
    - {% set template_version = "1.2.0" %}
    - Version: 1.2.0 (in first 10 lines)
    """
    if not file_path.exists():
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [f.readline() for _ in range(10)]

        content = "".join(lines)

        patterns = [
            r"template-version:\s*(\d+\.\d+\.\d+)",
            r'template_version\s*=\s*["\'](\d+\.\d+\.\d+)["\']',
            r"version:\s*(\d+\.\d+\.\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)

    except Exception:
        pass

    return None


def migrate_template_if_needed(
    db: Dict[str, Any], target_version: str = TEMPLATE_VERSION
) -> Tuple[Dict[str, Any], bool]:
    """Migrate template data to current version if needed

    Returns:
        Tuple of (updated_db, was_migrated)
    """
    current_version = get_template_version(db)

    if not current_version:
        db = set_template_version(db, target_version)
        return db, True

    if current_version == target_version:
        return db, False

    migrated = False

    if VersionInfo.from_string(current_version) < VersionInfo.from_string("1.1.0"):
        if "gamp_category" not in db:
            db["gamp_category"] = None
        migrated = True

    if VersionInfo.from_string(current_version) < VersionInfo.from_string("1.2.0"):
        for req in db.get("requirements", []):
            if "risk_level" not in req:
                req["risk_level"] = None
        migrated = True

    db = set_template_version(db, target_version)
    return db, migrated


def load_requirements_with_version(
    path: Path,
) -> Tuple[Dict[str, Any], CompatibilityResult]:
    """Load requirements.json and check compatibility

    Returns:
        Tuple of (db, compatibility_result)
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            db = json.load(f)

        compatibility = check_template_compatibility(db)
        return db, compatibility

    except json.JSONDecodeError as e:
        return {}, CompatibilityResult(
            compatible=False,
            current_version=TEMPLATE_VERSION,
            required_version=None,
            message=f"Failed to parse requirements.json: {e}",
        )
    except Exception as e:
        return {}, CompatibilityResult(
            compatible=False,
            current_version=TEMPLATE_VERSION,
            required_version=None,
            message=f"Failed to load requirements.json: {e}",
        )
