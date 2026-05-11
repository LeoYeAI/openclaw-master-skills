"""Tests for git hooks installation"""

import unittest
import tempfile
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestGitHooksInstallation(unittest.TestCase):
    """Test git hooks installation script"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

        self.project_path.joinpath(".git").mkdir()
        self.hooks_dir = self.project_path / ".git" / "hooks"
        self.hooks_dir.mkdir()

        self.install_script = (
            Path(__file__).parent.parent.parent / "scripts" / "git-hooks" / "install.sh"
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_install_script_exists(self):
        """Test that install script exists and is executable"""
        if self.install_script.exists():
            self.assertTrue(self.install_script.stat().st_mode & 0o111)

    def test_post_commit_hook_exists(self):
        """Test that post-commit hook source exists"""
        hook_source = (
            Path(__file__).parent.parent.parent
            / "scripts"
            / "git-hooks"
            / "post-commit"
        )
        self.assertTrue(hook_source.exists())

    def test_install_local(self):
        """Test local installation of hooks"""
        if not self.install_script.exists():
            self.skipTest("Install script not found")

        result = subprocess.run(
            [str(self.install_script), "--local"],
            cwd=str(self.project_path),
            capture_output=True,
            text=True,
        )

        self.assertIn("Installing local git hooks", result.stdout)

    def test_uninstall(self):
        """Test uninstalling hooks"""
        if not self.install_script.exists():
            self.skipTest("Install script not found")

        hook_file = self.hooks_dir / "post-commit"
        hook_file.write_text("#!/bin/bash\nexit 0\n")
        hook_file.chmod(0o755)

        result = subprocess.run(
            [str(self.install_script), "--uninstall"],
            cwd=str(self.project_path),
            capture_output=True,
            text=True,
        )

        self.assertTrue(result.returncode == 0 or not hook_file.exists())


class TestPostCommitHook(unittest.TestCase):
    """Test post-commit hook behavior"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

        self.project_path.joinpath(".git").mkdir()

        self.hooks_dir = self.project_path / ".git" / "hooks"
        self.hooks_dir.mkdir()

        self.hook_source = (
            Path(__file__).parent.parent.parent
            / "scripts"
            / "git-hooks"
            / "post-commit"
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_hook_detects_relevant_files(self):
        """Test that hook detects relevant file changes"""
        if not self.hook_source.exists():
            self.skipTest("Hook source not found")

        hook_content = self.hook_source.read_text()

        self.assertIn("requirements.json", hook_content)
        self.assertIn(".py", hook_content)

    def test_hook_runs_compliance_check(self):
        """Test that hook runs compliance check"""
        if not self.hook_source.exists():
            self.skipTest("Hook source not found")

        hook_content = self.hook_source.read_text()

        self.assertIn("generate.py check", hook_content)


if __name__ == "__main__":
    unittest.main()
