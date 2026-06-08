#!/usr/bin/env python3
"""
Content Planner — Daily content recommendation engine.

Reads profile, goals, and content calendar configuration to generate
daily content recommendations with content mix compliance tracking.

Designed to be called by an AI agent as part of the daily PDCA loop.

Usage:
    from content_planner import ContentPlanner

    planner = ContentPlanner(
        profile_path="config/profile.json",
        goals_path="config/goals.json",
        calendar_path="config/content-calendar.json"
    )
    recommendation = planner.generate_daily_plan(day_of_week="tuesday")
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional


CONTENT_PILLARS = {
    "value": {
        "label": "Technical Depth / Value",
        "description": "Tips, insights, tutorials, how-tos",
        "default_target_pct": 40,
        "formats": ["technical insight", "tutorial", "tool comparison", "code snippet"],
    },
    "opinion": {
        "label": "Industry Pulse / Opinion",
        "description": "Contrarian takes, hot takes, predictions, trend analysis",
        "default_target_pct": 25,
        "formats": ["contrarian take", "prediction", "rapid reaction", "industry analysis"],
    },
    "story": {
        "label": "Builder's Journey / Story",
        "description": "Build-in-public, decisions, lessons, failures",
        "default_target_pct": 25,
        "formats": ["build update", "lesson learned", "decision story", "milestone"],
    },
    "engagement": {
        "label": "Community Value / Engagement",
        "description": "Questions, polls, resource shares, community highlights",
        "default_target_pct": 10,
        "formats": ["question", "poll", "resource list", "community highlight"],
    },
}

CONTENT_FORMULAS = [
    {
        "name": "Claim + Evidence + CTA",
        "template": "[Bold claim] → [Evidence/example] → [Discussion prompt]",
        "best_for": ["value", "opinion"],
    },
    {
        "name": "Story + Lesson + Takeaway",
        "template": "[Brief narrative] → [What happened] → [Actionable insight]",
        "best_for": ["story"],
    },
    {
        "name": "Question + Context + Invitation",
        "template": "[Thoughtful question] → [Why asking] → [Invite perspectives]",
        "best_for": ["engagement"],
    },
    {
        "name": "List + Value + CTA",
        "template": "[N items] → [Brief explanation each] → [Bookmark/follow prompt]",
        "best_for": ["value", "engagement"],
    },
    {
        "name": "Reaction + Analysis + Prediction",
        "template": "[News reference] → [Your analysis] → [What happens next]",
        "best_for": ["opinion"],
    },
]

WEEKLY_THEMES = {
    "monday": "Industry Pulse",
    "tuesday": "Technical Depth",
    "wednesday": "Builder's Journey",
    "thursday": "Community Value",
    "friday": "Personal Touch + Recap",
    "saturday": "Light Engagement",
    "sunday": "Review + Planning",
}

PRODUCT_INTEGRATION_TIERS = {
    1: {"label": "Background Presence", "description": "Bio/profile does the work, no explicit mention"},
    2: {"label": "Contextual Reference", "description": "Product as example within broader insight"},
    3: {"label": "Direct Promotion", "description": "Product is the subject: launch, milestone, demo"},
}


class ContentPlanner:
    """Generates daily content recommendations based on configuration and history."""

    def __init__(
        self,
        profile_path: str = "config/profile.json",
        goals_path: str = "config/goals.json",
        calendar_path: str = "config/content-calendar.json",
    ):
        self.profile = self._load_json(profile_path, {})
        self.goals = self._load_json(goals_path, {})
        self.calendar = self._load_json(calendar_path, {})
        self.content_mix_targets = self._get_content_mix_targets()

    def _load_json(self, path: str, default: Dict) -> Dict:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return default

    def _get_content_mix_targets(self) -> Dict[str, int]:
        mix = self.goals.get("content_mix", {})
        return {
            "value": mix.get("value_tweets_pct", 40),
            "opinion": mix.get("opinion_tweets_pct", 25),
            "story": mix.get("story_tweets_pct", 25),
            "engagement": mix.get("engagement_tweets_pct", 10),
        }

    def generate_daily_plan(
        self,
        day_of_week: Optional[str] = None,
        week_history: Optional[Dict[str, int]] = None,
        trending_topics: Optional[List[str]] = None,
    ) -> Dict:
        """
        Generate content recommendations for today.

        Args:
            day_of_week: e.g. "tuesday". Auto-detected if None.
            week_history: Content pillar counts so far this week,
                          e.g. {"value": 5, "opinion": 3, "story": 2, "engagement": 1}
            trending_topics: Current trending topics to potentially react to.

        Returns:
            Daily content plan with recommendations.
        """
        if day_of_week is None:
            day_of_week = datetime.now().strftime("%A").lower()

        theme = WEEKLY_THEMES.get(day_of_week, "General")
        compliance = self._check_mix_compliance(week_history or {})
        is_thread_day = self._is_thread_day(day_of_week)

        recommendations = []

        priority_pillar = compliance.get("most_underrepresented")
        if priority_pillar:
            rec = self._generate_recommendation(
                pillar=priority_pillar,
                reason=f"Underrepresented this week ({compliance['actual'].get(priority_pillar, 0)}% vs {self.content_mix_targets.get(priority_pillar, 0)}% target)",
                trending_topics=trending_topics,
            )
            recommendations.append(rec)

        theme_pillar = self._theme_to_pillar(theme)
        if theme_pillar and theme_pillar != priority_pillar:
            rec = self._generate_recommendation(
                pillar=theme_pillar,
                reason=f"Today's theme: {theme}",
                trending_topics=trending_topics,
            )
            recommendations.append(rec)

        if len(recommendations) < 2:
            filler_pillar = "value" if "value" not in [r["pillar"] for r in recommendations] else "opinion"
            rec = self._generate_recommendation(
                pillar=filler_pillar,
                reason="Fill daily post quota",
                trending_topics=trending_topics,
            )
            recommendations.append(rec)

        for i, rec in enumerate(recommendations):
            rec["product_integration"] = self._suggest_integration_tier(i, len(recommendations))

        plan = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "day_of_week": day_of_week,
            "theme": theme,
            "is_thread_day": is_thread_day,
            "content_mix_compliance": compliance,
            "recommendations": recommendations,
            "engagement_targets": self._get_engagement_targets(),
        }

        if is_thread_day:
            plan["thread_note"] = (
                "Thread day! Post your prepared thread during Window A "
                "(08:00-10:00 in target audience timezone). "
                "Include visuals in 60-70% of thread tweets."
            )

        if trending_topics:
            plan["trending_topics"] = trending_topics
            plan["trending_note"] = (
                "Consider a rapid-reaction tweet to a trending topic. "
                "Post within 2 hours of breaking for maximum algorithmic boost."
            )

        return plan

    def _check_mix_compliance(self, week_history: Dict[str, int]) -> Dict:
        total = sum(week_history.values()) or 1
        actual = {k: round(week_history.get(k, 0) / total * 100, 1) for k in self.content_mix_targets}

        deviations = {}
        for pillar, target in self.content_mix_targets.items():
            deviations[pillar] = actual.get(pillar, 0) - target

        most_under = min(deviations, key=deviations.get) if deviations else None

        return {
            "actual": actual,
            "target": self.content_mix_targets,
            "deviations": deviations,
            "most_underrepresented": most_under if deviations.get(most_under, 0) < -5 else None,
            "status": "ON_TRACK" if all(abs(v) <= 10 for v in deviations.values()) else "NEEDS_ADJUSTMENT",
        }

    def _generate_recommendation(
        self,
        pillar: str,
        reason: str,
        trending_topics: Optional[List[str]] = None,
    ) -> Dict:
        pillar_info = CONTENT_PILLARS.get(pillar, CONTENT_PILLARS["value"])
        matching_formulas = [f for f in CONTENT_FORMULAS if pillar in f["best_for"]]

        rec = {
            "pillar": pillar,
            "pillar_label": pillar_info["label"],
            "reason": reason,
            "suggested_formats": pillar_info["formats"],
            "suggested_formula": matching_formulas[0]["name"] if matching_formulas else None,
            "formula_template": matching_formulas[0]["template"] if matching_formulas else None,
            "multimodal_suggestion": self._suggest_visual(pillar),
        }

        if trending_topics and pillar in ("opinion", "value"):
            rec["trending_angle"] = (
                f"Consider reacting to: {trending_topics[0]}"
                if trending_topics else None
            )

        return rec

    def _suggest_visual(self, pillar: str) -> str:
        visual_map = {
            "value": "Code screenshot, diagram, or terminal output",
            "opinion": "Data visualization or comparison diagram",
            "story": "Dashboard screenshot, product screenshot, or workspace photo",
            "engagement": "Poll (built-in X feature) or comparison table image",
        }
        return visual_map.get(pillar, "Consider adding a relevant image")

    def _suggest_integration_tier(self, index: int, total: int) -> Dict:
        if index == 0:
            return PRODUCT_INTEGRATION_TIERS[1]
        elif index == total - 1 and total > 2:
            return PRODUCT_INTEGRATION_TIERS[2]
        return PRODUCT_INTEGRATION_TIERS[1]

    def _is_thread_day(self, day_of_week: str) -> bool:
        cal_day = self.calendar.get("weekly_rhythm", {}).get(day_of_week, {})
        return cal_day.get("thread_day", day_of_week in ("tuesday", "thursday"))

    def _theme_to_pillar(self, theme: str) -> Optional[str]:
        mapping = {
            "Industry Pulse": "opinion",
            "Technical Depth": "value",
            "Builder's Journey": "story",
            "Community Value": "engagement",
            "Personal Touch + Recap": "story",
            "Light Engagement": "engagement",
        }
        return mapping.get(theme)

    def _get_engagement_targets(self) -> Dict:
        targets = self.goals.get("targets", {}).get("1_month", {})
        return {
            "daily_replies_target": targets.get("daily_replies", 10),
            "core_circle_engagement": "Reply to 10-15 accounts before posting",
            "reply_quality_minimum": "Level C (thoughtful question) or above",
            "community_posting": "Post in 1-2 X Communities if relevant",
        }


if __name__ == "__main__":
    planner = ContentPlanner()
    plan = planner.generate_daily_plan()
    print(json.dumps(plan, indent=2, ensure_ascii=False))
