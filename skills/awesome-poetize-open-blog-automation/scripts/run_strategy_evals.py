#!/usr/bin/env python3
"""Run local strategy-layer evaluations for the Poetize blog automation skill."""

from __future__ import annotations

import json
from types import SimpleNamespace

import manage_blog
from blog_strategy import StrategyValidationError, apply_article_strategy, apply_ops_strategy


class EvalFailure(Exception):
    """Raised when an eval case fails."""


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise EvalFailure(message)


def expect_strategy_error(fn, contains: str) -> None:
    try:
        fn()
    except StrategyValidationError as exc:
        rendered = exc.render()
        assert_true(contains in rendered, f"Expected error to contain '{contains}', got: {rendered}")
        return
    raise EvalFailure("Expected StrategyValidationError but the call succeeded.")


def expect_die_signal(fn, contains: str) -> None:
    class DieSignal(Exception):
        pass

    original_die = manage_blog.die

    def fake_die(message: str, code: int = 1) -> None:
        raise DieSignal(message)

    manage_blog.die = fake_die
    try:
        try:
            fn()
        except DieSignal as exc:
            assert_true(contains in str(exc), f"Expected die message to contain '{contains}', got: {exc}")
            return
        raise EvalFailure("Expected command to stop with a die signal.")
    finally:
        manage_blog.die = original_die


def run_article_eval_suite() -> None:
    free_brief = {
        "taskType": "create_article",
        "primaryGoal": "asset_maintenance",
        "targetAudience": "Personal blog readers",
        "publishIntent": "public",
        "reasoning": "This article improves the long-term blog library.",
        "selectedAngle": "Practical maintenance guide",
        "alternativesConsidered": ["Wide beginner overview", "Compact tactical checklist"],
    }
    free_payload = {"title": "Example", "content": "Body", "payType": 4, "payAmount": 19.9}
    result = apply_article_strategy(free_brief, free_payload, is_update=False, cli_publish=False, cli_draft=False)
    assert_true(result["payType"] == 0, "Free-default article should force payType=0.")
    assert_true(result["viewStatus"] is True, "Public brief should produce viewStatus=true.")

    draft_brief = dict(free_brief)
    draft_brief["publishIntent"] = "draft"
    draft_result = apply_article_strategy(draft_brief, {"title": "Example", "content": "Body"}, is_update=False, cli_publish=False, cli_draft=False)
    assert_true(draft_result["viewStatus"] is False, "Draft brief should force viewStatus=false.")
    assert_true(bool(draft_result.get("password")), "Draft brief should auto-fill a password.")
    assert_true(bool(draft_result.get("tips")), "Draft brief should auto-fill preview tips.")

    bad_alternatives = dict(free_brief)
    bad_alternatives["alternativesConsidered"] = ["Only one option"]
    expect_strategy_error(
        lambda: apply_article_strategy(bad_alternatives, {"title": "Example", "content": "Body"}, is_update=False, cli_publish=False, cli_draft=False),
        "alternativesConsidered",
    )

    invalid_paid = dict(free_brief)
    invalid_paid["monetizationIntent"] = "paid_explicit"
    invalid_paid["whyPaid"] = "Try to monetize."
    expect_strategy_error(
        lambda: apply_article_strategy(invalid_paid, {"title": "Example", "content": "Body", "payType": 4}, is_update=False, cli_publish=False, cli_draft=False),
        "primaryGoal",
    )

    valid_paid = dict(invalid_paid)
    valid_paid["primaryGoal"] = "conversion"
    paid_result = apply_article_strategy(valid_paid, {"title": "Example", "content": "Body", "payType": 4}, is_update=False, cli_publish=False, cli_draft=False)
    assert_true(paid_result["payType"] == 4, "Explicit paid article should retain payType when conversion goal is set.")


def run_ops_eval_suite() -> None:
    update_brief = {
        "taskType": "update_article",
        "primaryGoal": "asset_maintenance",
        "reasoning": "Refresh the existing article.",
        "expectedOutcome": "The post stays accurate and useful.",
    }
    expect_strategy_error(
        lambda: apply_ops_strategy(update_brief, {"id": 12, "viewStatus": False}, expected_task_type="update_article"),
        "hide-article",
    )

    expect_strategy_error(
        lambda: apply_ops_strategy(update_brief, {"id": 12, "payType": 4}, expected_task_type="update_article"),
        "paywall",
    )

    hide_brief = {
        "taskType": "hide_article",
        "primaryGoal": "asset_maintenance",
        "reasoning": "Take the post down from public view.",
        "expectedOutcome": "The article is no longer public but remains recoverable.",
    }
    hidden = apply_ops_strategy(hide_brief, {"id": 12}, expected_task_type="hide_article")
    assert_true(hidden["viewStatus"] is False, "hide_article should force viewStatus=false.")


def run_taxonomy_eval_suite() -> None:
    fake_args = SimpleNamespace(base_url="https://example.com", api_key="test")

    original_fetch_categories = manage_blog.fetch_categories
    manage_blog.fetch_categories = lambda args: [
        {"id": 1, "sortName": "AI实践"},
        {"id": 2, "sortName": "AI工具"},
    ]
    try:
        expect_die_signal(lambda: manage_blog.resolve_sort_id(fake_args, None, "AI"), "Closest matches")
    finally:
        manage_blog.fetch_categories = original_fetch_categories


def main() -> None:
    suites = [
        ("article", run_article_eval_suite),
        ("ops", run_ops_eval_suite),
        ("taxonomy", run_taxonomy_eval_suite),
    ]

    results: list[dict[str, str]] = []
    for name, suite in suites:
        try:
            suite()
            results.append({"suite": name, "status": "passed"})
        except Exception as exc:  # noqa: BLE001
            results.append({"suite": name, "status": "failed", "message": str(exc)})

    failed = [item for item in results if item["status"] != "passed"]
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
