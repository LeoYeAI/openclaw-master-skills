#!/usr/bin/env python3
"""Shared strategy validation for the Poetize blog automation skill."""

from __future__ import annotations

import json
import uuid
from typing import Any

ARTICLE_CREATE_TASK_TYPES = {"create_article", "repurpose_article"}
ARTICLE_UPDATE_TASK_TYPES = {"refresh_article"}
OPS_TASK_TYPES = {"update_article", "hide_article"}
PRIMARY_GOALS = {"asset_maintenance", "seo_growth", "brand_expression", "conversion"}
PUBLISH_INTENTS = {"draft", "public"}
MONETIZATION_INTENTS = {"free_default", "paid_explicit"}


class StrategyValidationError(Exception):
    """Structured validation error for strategy-layer failures."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def render(self) -> str:
        payload = {
            "error": "strategy_validation_failed",
            "message": self.message,
            "details": self.details,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)


def load_json_object(path: str, *, label: str) -> dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise StrategyValidationError(
            f"{label} does not exist.",
            details={"path": path},
        ) from exc
    except json.JSONDecodeError as exc:
        raise StrategyValidationError(
            f"{label} is not valid JSON.",
            details={"path": path, "reason": str(exc)},
        ) from exc

    if not isinstance(data, dict):
        raise StrategyValidationError(
            f"{label} must contain a JSON object.",
            details={"path": path},
        )
    return data


def ensure_article_brief(
    brief: dict[str, Any],
    *,
    is_update: bool,
    cli_publish: bool,
    cli_draft: bool,
) -> dict[str, Any]:
    task_type = _require_enum(
        brief,
        "taskType",
        ARTICLE_UPDATE_TASK_TYPES if is_update else ARTICLE_CREATE_TASK_TYPES,
    )
    primary_goal = _require_enum(brief, "primaryGoal", PRIMARY_GOALS)
    target_audience = _require_non_empty_string(brief, "targetAudience")
    publish_intent = _require_enum(brief, "publishIntent", PUBLISH_INTENTS)
    reasoning = _require_non_empty_string(brief, "reasoning")
    selected_angle = _require_non_empty_string(brief, "selectedAngle")
    alternatives = _require_string_list(brief, "alternativesConsidered", min_items=2, max_items=3)

    if selected_angle in alternatives:
        raise StrategyValidationError(
            "selectedAngle must be the final choice and cannot be duplicated in alternativesConsidered.",
            details={"selectedAngle": selected_angle, "alternativesConsidered": alternatives},
        )

    monetization_intent = brief.get("monetizationIntent", "free_default")
    if monetization_intent not in MONETIZATION_INTENTS:
        raise StrategyValidationError(
            "monetizationIntent must be one of the supported values.",
            details={"field": "monetizationIntent", "allowed": sorted(MONETIZATION_INTENTS)},
        )

    why_paid: str | None = None
    if monetization_intent == "paid_explicit":
        why_paid = _require_non_empty_string(brief, "whyPaid")
        if primary_goal != "conversion":
            raise StrategyValidationError(
                "Paid publishing is only allowed when primaryGoal is conversion.",
                details={"primaryGoal": primary_goal, "monetizationIntent": monetization_intent},
            )

    if cli_publish and publish_intent == "draft":
        raise StrategyValidationError(
            "CLI flags conflict with brief publishIntent.",
            details={"flag": "--publish", "publishIntent": publish_intent},
        )
    if cli_draft and publish_intent == "public":
        raise StrategyValidationError(
            "CLI flags conflict with brief publishIntent.",
            details={"flag": "--draft", "publishIntent": publish_intent},
        )

    normalized = {
        "taskType": task_type,
        "primaryGoal": primary_goal,
        "targetAudience": target_audience,
        "publishIntent": publish_intent,
        "reasoning": reasoning,
        "selectedAngle": selected_angle,
        "alternativesConsidered": alternatives,
        "monetizationIntent": monetization_intent,
    }
    if why_paid:
        normalized["whyPaid"] = why_paid
    return normalized


def apply_article_strategy(
    brief: dict[str, Any],
    payload: dict[str, Any],
    *,
    is_update: bool,
    cli_publish: bool,
    cli_draft: bool,
) -> dict[str, Any]:
    normalized = ensure_article_brief(
        brief,
        is_update=is_update,
        cli_publish=cli_publish,
        cli_draft=cli_draft,
    )

    adjusted = dict(payload)
    publish_intent = normalized["publishIntent"]
    adjusted["viewStatus"] = publish_intent == "public"

    if adjusted["viewStatus"]:
        adjusted.pop("password", None)
        adjusted.pop("tips", None)
    else:
        if not _has_text(adjusted.get("password")):
            adjusted["password"] = f"draft-{uuid.uuid4().hex[:8]}"
        if not _has_text(adjusted.get("tips")):
            adjusted["tips"] = "Strategy brief requested a draft/private article."

    monetization_intent = normalized["monetizationIntent"]
    pay_type = adjusted.get("payType")
    if monetization_intent != "paid_explicit":
        adjusted["payType"] = 0
        adjusted.pop("payAmount", None)
        adjusted.pop("freePercent", None)
    else:
        if not isinstance(pay_type, int) or pay_type <= 0:
            raise StrategyValidationError(
                "Paid publishing requires payType > 0.",
                details={"payType": pay_type, "taskType": normalized["taskType"]},
            )

    if normalized["primaryGoal"] != "conversion" and isinstance(adjusted.get("payType"), int) and adjusted["payType"] > 0:
        raise StrategyValidationError(
            "payType > 0 is only allowed when primaryGoal is conversion.",
            details={"primaryGoal": normalized["primaryGoal"], "payType": adjusted["payType"]},
        )

    return {key: value for key, value in adjusted.items() if value is not None}


def ensure_ops_brief(brief: dict[str, Any], *, expected_task_type: str) -> dict[str, Any]:
    if expected_task_type not in OPS_TASK_TYPES:
        raise StrategyValidationError(
            "Unsupported ops task type.",
            details={"expectedTaskType": expected_task_type},
        )

    task_type = _require_enum(brief, "taskType", {expected_task_type})
    primary_goal = _require_enum(brief, "primaryGoal", PRIMARY_GOALS)
    reasoning = _require_non_empty_string(brief, "reasoning")
    expected_outcome = _require_non_empty_string(brief, "expectedOutcome")

    return {
        "taskType": task_type,
        "primaryGoal": primary_goal,
        "reasoning": reasoning,
        "expectedOutcome": expected_outcome,
    }


def apply_ops_strategy(
    brief: dict[str, Any],
    payload: dict[str, Any],
    *,
    expected_task_type: str,
) -> dict[str, Any]:
    normalized = ensure_ops_brief(brief, expected_task_type=expected_task_type)
    adjusted = dict(payload)

    if expected_task_type == "hide_article":
        adjusted["viewStatus"] = False
        if not _has_text(adjusted.get("password")):
            adjusted["password"] = f"hidden-{adjusted.get('id', 'article')}"
        if not _has_text(adjusted.get("tips")):
            adjusted["tips"] = "Article hidden by strategy brief."
        return {key: value for key, value in adjusted.items() if value is not None}

    if adjusted.get("viewStatus") is False:
        raise StrategyValidationError(
            "Use hide-article instead of update-article for takedown behavior.",
            details={"taskType": normalized["taskType"]},
        )

    pay_type = adjusted.get("payType")
    if normalized["primaryGoal"] != "conversion" and isinstance(pay_type, int) and pay_type > 0:
        raise StrategyValidationError(
            "update-article cannot introduce a paywall unless primaryGoal is conversion.",
            details={"primaryGoal": normalized["primaryGoal"], "payType": pay_type},
        )

    return {key: value for key, value in adjusted.items() if value is not None}


def _require_non_empty_string(source: dict[str, Any], key: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value.strip():
        raise StrategyValidationError(
            f"{key} must be a non-empty string.",
            details={"field": key},
        )
    return value.strip()


def _require_enum(source: dict[str, Any], key: str, allowed: set[str]) -> str:
    value = source.get(key)
    if not isinstance(value, str) or value not in allowed:
        raise StrategyValidationError(
            f"{key} must be one of the supported values.",
            details={"field": key, "allowed": sorted(allowed)},
        )
    return value


def _require_string_list(
    source: dict[str, Any],
    key: str,
    *,
    min_items: int,
    max_items: int,
) -> list[str]:
    value = source.get(key)
    if not isinstance(value, list):
        raise StrategyValidationError(
            f"{key} must be a list of strings.",
            details={"field": key},
        )

    cleaned: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise StrategyValidationError(
                f"{key} must contain only non-empty strings.",
                details={"field": key},
            )
        normalized = item.strip()
        if normalized in seen:
            continue
        seen.add(normalized)
        cleaned.append(normalized)

    if len(cleaned) < min_items or len(cleaned) > max_items:
        raise StrategyValidationError(
            f"{key} must contain between {min_items} and {max_items} unique items.",
            details={"field": key, "count": len(cleaned)},
        )
    return cleaned


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
