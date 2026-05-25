"""Sandbox test runner for ERPClaw modules.

Creates an isolated database, seeds the core schema, runs a module's tests
against it, checks GL invariants, and cleans up. Designed to work without
OpenClaw running — pure local Python tool.

Usage (programmatic):
    from erpclaw_os.sandbox import run_in_sandbox
    result = run_in_sandbox("/path/to/module")

Usage (CLI):
    python sandbox.py --module-path /path/to/module [--timeout 120] [--keep]
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Import gl_invariant_checker via importlib (parent dir has hyphen: erpclaw-os)
_checker_path = str(Path(__file__).resolve().parent / "gl_invariant_checker.py")
_checker_spec = importlib.util.spec_from_file_location(
    "gl_invariant_checker", _checker_path
)
_checker_mod = importlib.util.module_from_spec(_checker_spec)
_checker_spec.loader.exec_module(_checker_mod)
check_gl_invariants = _checker_mod.check_gl_invariants


def _find_project_root() -> Path:
    """Discover the project root by walking up from this file.

    Looks for the characteristic `src/erpclaw/scripts/erpclaw-setup/init_schema.py`.
    Falls back to a common relative path from the erpclaw-os directory.
    """
    # Start from this file's directory: src/erpclaw/scripts/erpclaw-os/
    current = Path(__file__).resolve().parent
    # Walk up: erpclaw-os -> scripts -> erpclaw -> src -> project root
    candidate = current.parent.parent.parent.parent
    if (candidate / "src" / "erpclaw" / "scripts" / "erpclaw-setup" / "init_schema.py").exists():
        return candidate
    # Fallback: walk up until we find the sentinel
    for parent in current.parents:
        sentinel = parent / "src" / "erpclaw" / "scripts" / "erpclaw-setup" / "init_schema.py"
        if sentinel.exists():
            return parent
    raise FileNotFoundError(
        "Cannot locate project root. Expected to find "
        "src/erpclaw/scripts/erpclaw-setup/init_schema.py"
    )


def _find_init_schema() -> str:
    """Return absolute path to core init_schema.py."""
    root = _find_project_root()
    path = root / "src" / "erpclaw" / "scripts" / "erpclaw-setup" / "init_schema.py"
    if not path.exists():
        raise FileNotFoundError(f"Core init_schema.py not found at {path}")
    return str(path)


def _find_module_init_db(module_path: str) -> str | None:
    """Return absolute path to the module's init_db.py, or None."""
    p = Path(module_path).resolve()
    init_db = p / "init_db.py"
    if init_db.exists():
        return str(init_db)
    return None


def _find_module_test_dir(module_path: str) -> str | None:
    """Return absolute path to the module's test directory, or None."""
    p = Path(module_path).resolve()
    # Standard location: scripts/tests/
    test_dir = p / "scripts" / "tests"
    if test_dir.is_dir():
        return str(test_dir)
    # Alternative: tests/ directly under module
    test_dir = p / "tests"
    if test_dir.is_dir():
        return str(test_dir)
    return None


def _parse_pytest_output(stdout: str, stderr: str) -> dict:
    """Parse pytest output to extract pass/fail counts.

    Pytest prints a summary line like:
        "5 passed, 2 failed in 1.23s"
        "3 passed in 0.45s"
        "1 failed in 0.12s"
        "no tests ran in 0.01s"
    """
    combined = stdout + "\n" + stderr

    passed = 0
    failed = 0
    errors = 0

    # Look for the summary line patterns
    m = re.search(r"(\d+)\s+passed", combined)
    if m:
        passed = int(m.group(1))

    m = re.search(r"(\d+)\s+failed", combined)
    if m:
        failed = int(m.group(1))

    m = re.search(r"(\d+)\s+error", combined)
    if m:
        errors = int(m.group(1))

    total = passed + failed + errors
    return {
        "tests_run": total,
        "tests_passed": passed,
        "tests_failed": failed,
        "tests_errored": errors,
    }


def run_in_sandbox(
    module_path: str,
    timeout: int = 120,
    keep_on_success: bool = False,
) -> dict:
    """Run a module's tests in an isolated sandbox environment.

    Steps:
    1. Create a temporary directory with a fresh SQLite DB
    2. Run core init_schema.py to create foundation tables
    3. Run the module's init_db.py to create its tables (on top of core)
    4. Run the module's tests via pytest
    5. Run GL invariant checks on the resulting DB
    6. Clean up the temp directory (unless tests failed or keep_on_success)

    Args:
        module_path: Absolute path to the module directory (e.g., src/legalclaw).
        timeout: Maximum seconds for the test run (default 120).
        keep_on_success: If True, preserve sandbox dir even on success.

    Returns:
        {
            "result": "pass" | "fail" | "error",
            "tests_run": int,
            "tests_passed": int,
            "tests_failed": int,
            "tests_errored": int,
            "gl_invariants": {...},
            "duration_ms": int,
            "sandbox_path": str,
            "error": str (only on error),
        }
    """
    start_time = time.monotonic()
    sandbox_dir = tempfile.mkdtemp(prefix="erpclaw_sandbox_")
    db_path = os.path.join(sandbox_dir, "sandbox.sqlite")

    result = {
        "result": "error",
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "tests_errored": 0,
        "gl_invariants": {"result": "skip", "checks": [], "violations": []},
        "duration_ms": 0,
        "sandbox_path": sandbox_dir,
    }

    cleanup = True

    try:
        module_path = str(Path(module_path).resolve())

        # --- Step 1: Seed core schema ---
        init_schema_path = _find_init_schema()
        proc = subprocess.run(
            [sys.executable, init_schema_path, "--db-path", db_path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.path.dirname(init_schema_path),
        )
        if proc.returncode != 0:
            result["error"] = f"Core init_schema.py failed: {proc.stderr}"
            cleanup = False
            return result

        # --- Step 2: Run module's init_db.py ---
        init_db_path = _find_module_init_db(module_path)
        if init_db_path:
            # Module init_db.py typically takes db_path as first positional arg
            # or via --db-path flag. Try positional arg first (most common pattern).
            proc = subprocess.run(
                [sys.executable, init_db_path, db_path],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=os.path.dirname(init_db_path),
            )
            if proc.returncode != 0:
                # Retry with --db-path flag
                proc = subprocess.run(
                    [sys.executable, init_db_path, "--db-path", db_path],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=os.path.dirname(init_db_path),
                )
                if proc.returncode != 0:
                    result["error"] = (
                        f"Module init_db.py failed: {proc.stderr or proc.stdout}"
                    )
                    cleanup = False
                    return result

        # --- Step 3: Run module's tests ---
        test_dir = _find_module_test_dir(module_path)
        if not test_dir:
            result["error"] = f"No test directory found in {module_path}"
            cleanup = False
            return result

        # Build environment: pass sandbox DB path via ERPCLAW_DB_PATH
        test_env = os.environ.copy()
        test_env["ERPCLAW_DB_PATH"] = db_path
        # Ensure erpclaw_lib is importable
        erpclaw_lib = os.path.expanduser("~/.openclaw/erpclaw/lib")
        if "PYTHONPATH" in test_env:
            test_env["PYTHONPATH"] = erpclaw_lib + os.pathsep + test_env["PYTHONPATH"]
        else:
            test_env["PYTHONPATH"] = erpclaw_lib

        proc = subprocess.run(
            [sys.executable, "-m", "pytest", test_dir, "-q", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=test_env,
            cwd=module_path,
        )

        test_results = _parse_pytest_output(proc.stdout, proc.stderr)
        result.update(test_results)

        # --- Step 4: GL invariant checks ---
        gl_result = check_gl_invariants(db_path)
        result["gl_invariants"] = gl_result

        # --- Determine overall result ---
        tests_ok = test_results["tests_failed"] == 0 and test_results["tests_errored"] == 0
        gl_ok = gl_result["result"] in ("pass", "skip")

        if test_results["tests_run"] == 0:
            result["result"] = "error"
            result["error"] = "No tests were collected or run"
            cleanup = False
        elif tests_ok and gl_ok:
            result["result"] = "pass"
        else:
            result["result"] = "fail"
            cleanup = False  # preserve for debugging

    except subprocess.TimeoutExpired:
        result["result"] = "error"
        result["error"] = f"Sandbox timed out after {timeout}s"
        cleanup = False
    except FileNotFoundError as e:
        result["result"] = "error"
        result["error"] = str(e)
        cleanup = False
    except Exception as e:
        result["result"] = "error"
        result["error"] = f"{type(e).__name__}: {e}"
        cleanup = False
    finally:
        elapsed = time.monotonic() - start_time
        result["duration_ms"] = int(elapsed * 1000)

        # Clean up unless we need to preserve for debugging
        if cleanup and not keep_on_success:
            try:
                shutil.rmtree(sandbox_dir, ignore_errors=True)
                result["sandbox_path"] = "(cleaned up)"
            except Exception:
                pass

    return result


def main():
    """CLI entry point for the sandbox runner."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run module tests in an isolated sandbox"
    )
    parser.add_argument(
        "--module-path",
        required=True,
        help="Path to the module directory to test",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Maximum seconds for the test run (default: 120)",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep the sandbox directory even on success",
    )
    args = parser.parse_args()

    result = run_in_sandbox(
        module_path=args.module_path,
        timeout=args.timeout,
        keep_on_success=args.keep,
    )

    print(json.dumps(result, indent=2))
    sys.exit(0 if result["result"] == "pass" else 1)


if __name__ == "__main__":
    main()
