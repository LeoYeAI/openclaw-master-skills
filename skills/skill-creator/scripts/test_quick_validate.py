#!/usr/bin/env python3
import importlib.util
import tempfile
import textwrap
import unittest
from pathlib import Path
from typing import Callable, cast


MODULE_PATH = Path(__file__).with_name("quick_validate.py")
MODULE_SPEC = importlib.util.spec_from_file_location("quick_validate", MODULE_PATH)
if MODULE_SPEC is None or MODULE_SPEC.loader is None:
    raise RuntimeError(f"Unable to load quick_validate.py from {MODULE_PATH}")
QUICK_VALIDATE = importlib.util.module_from_spec(MODULE_SPEC)
_ = MODULE_SPEC.loader.exec_module(QUICK_VALIDATE)
validate_skill = cast(
    Callable[[str | Path], tuple[bool, str]], QUICK_VALIDATE.validate_skill
)


class ValidateSkillTests(unittest.TestCase):
    def make_skill(self, root: Path, frontmatter: str) -> Path:
        skill_dir = root / "demo-skill"
        skill_dir.mkdir()
        _ = (skill_dir / "SKILL.md").write_text(
            textwrap.dedent(frontmatter).strip() + "\n"
        )
        return skill_dir

    def test_allows_version_and_author_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = self.make_skill(
                Path(tmp),
                """
                ---
                name: demo-skill
                description: Demo skill for validation
                version: 1.0.0
                author: example.com/demo
                license: MIT
                ---
                """,
            )

            valid, message = validate_skill(skill_dir)

            self.assertTrue(valid)
            self.assertEqual(message, "Skill is valid!")

    def test_rejects_unexpected_frontmatter_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = self.make_skill(
                Path(tmp),
                """
                ---
                name: demo-skill
                description: Demo skill for validation
                unsupported: true
                ---
                """,
            )

            valid, message = validate_skill(skill_dir)

            self.assertFalse(valid)
            self.assertIn("unsupported", message)


if __name__ == "__main__":
    _ = unittest.main()
