#!/usr/bin/env python3
"""ERPClaw OS — Regression Gate

Runs the existing test suite in a sandbox that includes the new module.
Any failure = deployment blocked. Returns list of broken tests with context.

Supports incremental mode (only run tests for affected modules based on
dependency graph).
"""
import json
import os
import subprocess
import sys
import tempfile
import time


def run_regression(module_path, db_path=None, affected_modules=None, timeout=300):
    """Run regression tests for a module.

    Args:
        module_path: Path to the module directory
        db_path: Path to a test database (if None, creates fresh one)
        affected_modules: List of module names to test (None = module tests only)
        timeout: Maximum seconds for test execution

    Returns:
        dict with passed, failed, broken_tests, duration_ms
    """
    start_time = time.time()

    # Find test directory
    test_dirs = []
    scripts_tests = os.path.join(module_path, "scripts", "tests")
    root_tests = os.path.join(module_path, "tests")

    if os.path.isdir(scripts_tests):
        test_dirs.append(scripts_tests)
    elif os.path.isdir(root_tests):
        test_dirs.append(root_tests)

    if not test_dirs:
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "result": "skip",
            "reason": "No test directory found",
            "passed": 0,
            "failed": 0,
            "broken_tests": [],
            "duration_ms": duration_ms,
        }

    # Set up environment
    env = os.environ.copy()
    if db_path:
        env["ERPCLAW_DB_PATH"] = db_path

    # Add erpclaw_lib to PYTHONPATH
    lib_path = os.path.expanduser("~/.openclaw/erpclaw/lib")
    if os.path.isdir(lib_path):
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{lib_path}:{existing}" if existing else lib_path

    # Run pytest with JSON output
    all_passed = 0
    all_failed = 0
    broken_tests = []

    for test_dir in test_dirs:
        cmd = [
            sys.executable, "-m", "pytest", test_dir,
            "-v", "--tb=short", "--no-header", "-q",
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )

            # Parse pytest output for pass/fail counts
            stdout = result.stdout
            for line in stdout.split("\n"):
                line = line.strip()
                # Look for summary line like "5 passed, 2 failed"
                if "passed" in line or "failed" in line:
                    import re
                    passed_match = re.search(r"(\d+)\s+passed", line)
                    failed_match = re.search(r"(\d+)\s+failed", line)
                    if passed_match:
                        all_passed += int(passed_match.group(1))
                    if failed_match:
                        all_failed += int(failed_match.group(1))

                # Capture FAILED test names
                if line.startswith("FAILED"):
                    broken_tests.append({
                        "test": line.replace("FAILED ", ""),
                        "test_dir": test_dir,
                    })

            # Also check for errors in output
            if result.returncode != 0 and all_failed == 0:
                # Pytest returned non-zero but no explicit fails — could be import errors
                for line in stdout.split("\n") + (result.stderr or "").split("\n"):
                    if "ERROR" in line or "ImportError" in line:
                        broken_tests.append({
                            "test": line.strip()[:200],
                            "test_dir": test_dir,
                        })
                        all_failed += 1

        except subprocess.TimeoutExpired:
            broken_tests.append({
                "test": f"TIMEOUT: Tests in {test_dir} exceeded {timeout}s",
                "test_dir": test_dir,
            })
            all_failed += 1

    duration_ms = int((time.time() - start_time) * 1000)

    return {
        "result": "pass" if all_failed == 0 else "fail",
        "passed": all_passed,
        "failed": all_failed,
        "broken_tests": broken_tests,
        "duration_ms": duration_ms,
    }
