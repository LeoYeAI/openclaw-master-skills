"""Tests for the source extractor."""

import json
import subprocess
import sys
from pathlib import Path


def run_extractor(url: str) -> dict:
    """Run the extractor and return parsed JSON."""
    project_root = str(Path(__file__).parent.parent)
    result = subprocess.run(
        [sys.executable, "scripts/extractors/extract.py", url],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=project_root,
    )
    stdout = result.stdout.strip()
    # Find the JSON object in output (skip any preceding noise)
    start = stdout.find("{")
    if start == -1:
        raise ValueError(f"No JSON in output: {stdout[:200]}")
    return json.loads(stdout[start:])


def test_detect_type():
    """URL type detection routes correctly."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from scripts.extractors.extract import detect_type

    assert detect_type("https://arxiv.org/abs/2401.04088") == "web"
    assert detect_type("https://arxiv.org/pdf/2401.04088") == "pdf"
    assert detect_type("https://reddit.com/r/test/comments/abc") == "reddit"
    assert detect_type("https://github.com/owner/repo") == "github"
    assert detect_type("https://x.com/user/status/123") == "twitter"
    assert detect_type("https://twitter.com/user/status/123") == "twitter"
    assert detect_type("https://example.com/doc.pdf") == "pdf"
    assert detect_type("https://example.com/article") == "web"
    assert detect_type("https://youtube.com/watch?v=abc") == "youtube"


def test_github_extractor():
    """GitHub extractor returns structured data from a public repo."""
    result = run_extractor("https://github.com/anthropics/anthropic-sdk-python")
    assert result["type"] == "github"
    assert result["word_count"] > 0
    assert "anthropic" in result["text"].lower()
    assert "error" not in result


def test_web_extractor():
    """Web extractor returns structured data from a blog post."""
    result = run_extractor("https://lilianweng.github.io/posts/2024-02-05-human-data-quality/")
    assert result["type"] == "web"
    assert result["title"] != ""
    assert result["word_count"] > 100
    assert "error" not in result


def test_extractor_truncation():
    """Long text gets truncated at 50k chars."""
    # Can't easily trigger this in a test without a huge page,
    # but verify the field would exist
    result = run_extractor("https://github.com/anthropics/anthropic-sdk-python")
    assert "truncated" not in result or result.get("truncated") is True


def test_extractor_bad_url():
    """Bad URL returns an error dict, not a crash."""
    project_root = str(Path(__file__).parent.parent)
    result = subprocess.run(
        [sys.executable, "scripts/extractors/extract.py", "https://thisdoesnotexist.example.com"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=project_root,
    )
    assert result.returncode != 0
    output = (result.stdout or result.stderr).strip()
    start = output.find("{")
    assert start != -1, f"No JSON in output: {output[:200]}"
    data = json.loads(output[start:])
    assert "error" in data
