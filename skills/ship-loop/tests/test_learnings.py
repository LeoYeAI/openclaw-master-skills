import tempfile
from pathlib import Path

import pytest

from shiploop.learnings import (
    LearningsEngine,
    _compute_error_signature,
    _extract_keywords,
    _extract_tags,
    _keyword_score,
    Learning,
)


@pytest.fixture
def learnings_path():
    with tempfile.NamedTemporaryFile(suffix=".yml", delete=False) as f:
        path = Path(f.name)
    path.unlink()
    yield path
    path.unlink(missing_ok=True)


@pytest.fixture
def engine(learnings_path):
    return LearningsEngine(learnings_path)


class TestKeywordExtraction:
    def test_filters_stop_words(self):
        keywords = _extract_keywords("this is the error from build")
        assert "this" not in keywords
        assert "the" not in keywords
        assert "error" in keywords
        assert "build" in keywords

    def test_filters_short_words(self):
        keywords = _extract_keywords("a an ok fix the module")
        assert "ok" not in keywords
        assert "an" not in keywords
        assert "fix" in keywords
        assert "module" in keywords

    def test_extracts_underscored_identifiers(self):
        keywords = _extract_keywords("import_error in theme_toggle component")
        assert "import_error" in keywords
        assert "theme_toggle" in keywords
        assert "component" in keywords

    def test_empty_input(self):
        keywords = _extract_keywords("")
        assert keywords == set()


class TestKeywordScoring:
    def test_exact_tag_match_scores_higher(self):
        learning_with_tags = Learning(
            id="L001", date="2026-01-01", segment="seg",
            failure="build failed", root_cause="missing import",
            fix="added import", tags=["build", "import"],
        )
        learning_no_tags = Learning(
            id="L002", date="2026-01-01", segment="seg",
            failure="build failed", root_cause="missing import",
            fix="added import", tags=[],
        )
        query_keywords = {"build", "import"}
        score_with = _keyword_score(query_keywords, learning_with_tags)
        score_without = _keyword_score(query_keywords, learning_no_tags)
        assert score_with > score_without

    def test_no_overlap_returns_zero(self):
        learning = Learning(
            id="L001", date="2026-01-01", segment="seg",
            failure="timeout on deploy", root_cause="slow server",
            fix="increased timeout", tags=["timeout"],
        )
        query_keywords = {"authentication", "password", "login"}
        assert _keyword_score(query_keywords, learning) == 0.0


class TestSearch:
    def test_returns_top_n_sorted_by_relevance(self, engine):
        engine.record(segment="s1", failure="build error import", root_cause="missing", fix="added", tags=["build"])
        engine.record(segment="s2", failure="lint warning", root_cause="unused var", fix="removed", tags=["lint"])
        engine.record(segment="s3", failure="build failed import module", root_cause="wrong path", fix="fixed path", tags=["build", "import"])

        results = engine.search("build import error", max_results=2)
        assert len(results) == 2
        names = [r.segment for r in results]
        assert "s3" in names

    def test_empty_learnings(self, learnings_path):
        engine = LearningsEngine(learnings_path)
        results = engine.search("anything")
        assert results == []


class TestFormatForPrompt:
    def test_output_format(self, engine):
        engine.record(segment="seg-1", failure="build failed", root_cause="bad import", fix="fixed import")
        learnings = engine.search("build")
        output = engine.format_for_prompt(learnings)
        assert "## Relevant Lessons from Past Runs" in output
        assert "L001" in output
        assert "build failed" in output
        assert "Use these lessons" in output

    def test_empty_returns_empty_string(self, engine):
        assert engine.format_for_prompt([]) == ""


class TestRecord:
    def test_creates_sequential_ids(self, engine):
        l1 = engine.record(segment="s1", failure="err1", root_cause="r1", fix="f1")
        l2 = engine.record(segment="s2", failure="err2", root_cause="r2", fix="f2")
        l3 = engine.record(segment="s3", failure="err3", root_cause="r3", fix="f3")
        assert l1.id == "L001"
        assert l2.id == "L002"
        assert l3.id == "L003"

    def test_persists_to_file(self, learnings_path):
        engine1 = LearningsEngine(learnings_path)
        engine1.record(segment="s", failure="f", root_cause="r", fix="x")
        engine2 = LearningsEngine(learnings_path)
        assert len(engine2.learnings) == 1
        assert engine2.learnings[0].id == "L001"


class TestErrorSignature:
    def test_same_first_five_lines_same_signature(self):
        error_a = "line1\nline2\nline3\nline4\nline5\nextra_a"
        error_b = "line1\nline2\nline3\nline4\nline5\nextra_b"
        assert _compute_error_signature(error_a) == _compute_error_signature(error_b)

    def test_different_lines_different_signature(self):
        error_a = "error: module not found"
        error_b = "error: syntax error"
        assert _compute_error_signature(error_a) != _compute_error_signature(error_b)

    def test_empty_input(self):
        sig = _compute_error_signature("")
        assert isinstance(sig, str)
        assert len(sig) > 0


class TestEmptyLearningsFile:
    def test_handles_nonexistent_file(self):
        engine = LearningsEngine(Path("/tmp/nonexistent-learnings-xyz.yml"))
        assert engine.learnings == []

    def test_handles_empty_file(self, learnings_path):
        learnings_path.write_text("")
        engine = LearningsEngine(learnings_path)
        assert engine.learnings == []

    def test_handles_invalid_yaml(self, learnings_path):
        learnings_path.write_text(": : invalid yaml {{{}}")
        engine = LearningsEngine(learnings_path)
        assert engine.learnings == []
