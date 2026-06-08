#!/usr/bin/env python3
"""
Analytics Reporter — Performance analytics and reporting engine.

Generates performance reports using validated X data. Computes metrics,
compares against benchmarks, identifies top/bottom performers, and
produces structured reports for weekly and monthly reviews.

Designed to be called by an AI agent as part of the review cycle.

Usage:
    from analytics_reporter import AnalyticsReporter

    reporter = AnalyticsReporter(goals_path="config/goals.json")
    report = reporter.generate_report(validated_tweets)
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple


ENGAGEMENT_BENCHMARKS = {
    "early": {"good": 2.0, "great": 5.0, "exceptional": 10.0},
    "growth": {"good": 1.0, "great": 2.5, "exceptional": 5.0},
    "established": {"good": 0.5, "great": 1.5, "exceptional": 3.0},
    "authority": {"good": 0.3, "great": 1.0, "exceptional": 2.0},
}

IMPRESSIONS_BENCHMARKS = {
    "early": {"low": 50, "average": 200, "high": 1000},
    "growth": {"low": 500, "average": 2000, "high": 20000},
    "established": {"low": 2000, "average": 10000, "high": 100000},
    "authority": {"low": 5000, "average": 20000, "high": 200000},
}


class AnalyticsReporter:
    """Generates performance reports from validated X data."""

    def __init__(self, goals_path: str = "config/goals.json"):
        self.goals = self._load_json(goals_path, {})
        self.growth_stage = self.goals.get("growth_stage", "early")

    def _load_json(self, path: str, default: Dict) -> Dict:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return default

    def generate_report(
        self,
        validated_tweets: List[Dict],
        period_label: str = "Report Period",
        previous_period_metrics: Optional[Dict] = None,
    ) -> Dict:
        """
        Generate a comprehensive performance report.

        Args:
            validated_tweets: List of validated tweet objects with metrics.
            period_label: Human-readable label for the report period.
            previous_period_metrics: Previous period summary for comparison.

        Returns:
            Structured performance report.
        """
        if not validated_tweets:
            return {
                "period": period_label,
                "generated_at": datetime.now().isoformat(),
                "status": "NO_DATA",
                "message": "No validated tweets to analyze",
            }

        metrics = self._compute_metrics(validated_tweets)
        top_performers = self._find_top_performers(validated_tweets, n=3)
        bottom_performers = self._find_bottom_performers(validated_tweets, n=3)
        content_breakdown = self._analyze_content_types(validated_tweets)
        timing_analysis = self._analyze_posting_times(validated_tweets)
        benchmark_comparison = self._compare_benchmarks(metrics)

        report = {
            "period": period_label,
            "generated_at": datetime.now().isoformat(),
            "growth_stage": self.growth_stage,
            "summary": metrics,
            "benchmark_comparison": benchmark_comparison,
            "top_performers": top_performers,
            "bottom_performers": bottom_performers,
            "content_type_breakdown": content_breakdown,
            "timing_analysis": timing_analysis,
            "recommendations": self._generate_recommendations(
                metrics, top_performers, bottom_performers, content_breakdown
            ),
        }

        if previous_period_metrics:
            report["period_comparison"] = self._compare_periods(metrics, previous_period_metrics)

        goal_targets = self.goals.get("targets", {}).get("1_month", {})
        if goal_targets:
            report["goal_progress"] = self._assess_goal_progress(metrics, goal_targets)

        return report

    def _compute_metrics(self, tweets: List[Dict]) -> Dict:
        total_impressions = 0
        total_likes = 0
        total_retweets = 0
        total_replies = 0
        total_quotes = 0
        total_bookmarks = 0
        complete_count = 0

        for tweet in tweets:
            m = tweet.get("metrics", {})
            impressions = m.get("impressionCount")
            if impressions is None:
                continue

            complete_count += 1
            total_impressions += impressions
            total_likes += m.get("likeCount") or 0
            total_retweets += m.get("retweetCount") or 0
            total_replies += m.get("replyCount") or 0
            total_quotes += m.get("quoteCount") or 0
            total_bookmarks += m.get("bookmarkCount") or 0

        total_engagement = total_likes + total_retweets + total_replies + total_quotes

        return {
            "total_tweets": len(tweets),
            "tweets_with_complete_data": complete_count,
            "total_impressions": total_impressions,
            "total_engagement": total_engagement,
            "avg_impressions_per_tweet": (
                round(total_impressions / complete_count, 1) if complete_count else None
            ),
            "avg_engagement_per_tweet": (
                round(total_engagement / complete_count, 2) if complete_count else None
            ),
            "engagement_rate_pct": (
                round(total_engagement / total_impressions * 100, 2)
                if total_impressions > 0 else None
            ),
            "engagement_breakdown": {
                "likes": total_likes,
                "retweets": total_retweets,
                "replies": total_replies,
                "quotes": total_quotes,
                "bookmarks": total_bookmarks,
            },
            "engagement_quality": {
                "reply_ratio": (
                    round(total_replies / total_engagement * 100, 1)
                    if total_engagement > 0 else None
                ),
                "bookmark_ratio": (
                    round(total_bookmarks / total_engagement * 100, 1)
                    if total_engagement > 0 else None
                ),
                "note": "Higher reply and bookmark ratios indicate deeper engagement",
            },
        }

    def _find_top_performers(self, tweets: List[Dict], n: int = 3) -> List[Dict]:
        scored = []
        for tweet in tweets:
            m = tweet.get("metrics", {})
            impressions = m.get("impressionCount")
            if not impressions:
                continue
            engagement = sum(
                m.get(k, 0) or 0
                for k in ["likeCount", "retweetCount", "replyCount", "quoteCount"]
            )
            er = engagement / impressions * 100 if impressions > 0 else 0
            scored.append({
                "id": tweet.get("id"),
                "text_preview": tweet.get("text", "")[:120],
                "impressions": impressions,
                "engagement": engagement,
                "engagement_rate_pct": round(er, 2),
                "likes": m.get("likeCount", 0),
                "replies": m.get("replyCount", 0),
                "bookmarks": m.get("bookmarkCount", 0),
                "created_at": tweet.get("createdAt"),
            })

        scored.sort(key=lambda x: x["engagement_rate_pct"], reverse=True)
        return scored[:n]

    def _find_bottom_performers(self, tweets: List[Dict], n: int = 3) -> List[Dict]:
        scored = []
        for tweet in tweets:
            m = tweet.get("metrics", {})
            impressions = m.get("impressionCount")
            if not impressions:
                continue
            engagement = sum(
                m.get(k, 0) or 0
                for k in ["likeCount", "retweetCount", "replyCount", "quoteCount"]
            )
            er = engagement / impressions * 100 if impressions > 0 else 0
            scored.append({
                "id": tweet.get("id"),
                "text_preview": tweet.get("text", "")[:120],
                "impressions": impressions,
                "engagement": engagement,
                "engagement_rate_pct": round(er, 2),
                "created_at": tweet.get("createdAt"),
            })

        scored.sort(key=lambda x: x["engagement_rate_pct"])
        return scored[:n]

    def _analyze_content_types(self, tweets: List[Dict]) -> Dict:
        """Analyze performance by content type (requires type tagging in tweet data)."""
        return {
            "note": "Content type analysis requires tweets to be tagged with pillar types during posting. "
                    "Use the daily review template to track content types manually until automated tagging is available.",
            "total_tweets": len(tweets),
        }

    def _analyze_posting_times(self, tweets: List[Dict]) -> Dict:
        """Analyze performance by posting time."""
        hour_buckets: Dict[int, List[Dict]] = {}

        for tweet in tweets:
            created_at = tweet.get("createdAt")
            if not created_at:
                continue
            try:
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                hour = dt.hour
            except (ValueError, AttributeError):
                continue

            if hour not in hour_buckets:
                hour_buckets[hour] = []

            m = tweet.get("metrics", {})
            impressions = m.get("impressionCount", 0) or 0
            engagement = sum(
                m.get(k, 0) or 0
                for k in ["likeCount", "retweetCount", "replyCount", "quoteCount"]
            )
            hour_buckets[hour].append({"impressions": impressions, "engagement": engagement})

        time_performance = {}
        for hour, posts in sorted(hour_buckets.items()):
            avg_imp = sum(p["impressions"] for p in posts) / len(posts) if posts else 0
            avg_eng = sum(p["engagement"] for p in posts) / len(posts) if posts else 0
            time_performance[f"{hour:02d}:00 UTC"] = {
                "post_count": len(posts),
                "avg_impressions": round(avg_imp, 1),
                "avg_engagement": round(avg_eng, 2),
            }

        return {
            "by_hour_utc": time_performance,
            "note": "Times are in UTC. Convert to your audience's timezone for actionable insights.",
        }

    def _compare_benchmarks(self, metrics: Dict) -> Dict:
        er = metrics.get("engagement_rate_pct")
        avg_imp = metrics.get("avg_impressions_per_tweet")

        er_bench = ENGAGEMENT_BENCHMARKS.get(self.growth_stage, ENGAGEMENT_BENCHMARKS["early"])
        imp_bench = IMPRESSIONS_BENCHMARKS.get(self.growth_stage, IMPRESSIONS_BENCHMARKS["early"])

        er_rating = "N/A"
        if er is not None:
            if er >= er_bench["exceptional"]:
                er_rating = "EXCEPTIONAL"
            elif er >= er_bench["great"]:
                er_rating = "GREAT"
            elif er >= er_bench["good"]:
                er_rating = "GOOD"
            else:
                er_rating = "BELOW_BENCHMARK"

        imp_rating = "N/A"
        if avg_imp is not None:
            if avg_imp >= imp_bench["high"]:
                imp_rating = "HIGH"
            elif avg_imp >= imp_bench["average"]:
                imp_rating = "AVERAGE"
            elif avg_imp >= imp_bench["low"]:
                imp_rating = "LOW"
            else:
                imp_rating = "BELOW_BENCHMARK"

        return {
            "growth_stage": self.growth_stage,
            "engagement_rate": {
                "actual": er,
                "benchmarks": er_bench,
                "rating": er_rating,
            },
            "impressions": {
                "actual": avg_imp,
                "benchmarks": imp_bench,
                "rating": imp_rating,
            },
        }

    def _compare_periods(self, current: Dict, previous: Dict) -> Dict:
        def pct_change(curr, prev):
            if prev and prev > 0 and curr is not None:
                return round((curr - prev) / prev * 100, 1)
            return None

        return {
            "impressions_change_pct": pct_change(
                current.get("total_impressions"), previous.get("total_impressions")
            ),
            "engagement_rate_change": (
                round(
                    (current.get("engagement_rate_pct") or 0) - (previous.get("engagement_rate_pct") or 0),
                    2,
                )
            ),
            "avg_impressions_change_pct": pct_change(
                current.get("avg_impressions_per_tweet"), previous.get("avg_impressions_per_tweet")
            ),
        }

    def _assess_goal_progress(self, metrics: Dict, targets: Dict) -> Dict:
        progress = {}

        er = metrics.get("engagement_rate_pct")
        er_target = targets.get("avg_engagement_rate_pct")
        if er is not None and er_target:
            progress["engagement_rate"] = {
                "actual": er,
                "target": er_target,
                "status": "ON_TRACK" if er >= er_target else "BEHIND",
            }

        avg_imp = metrics.get("avg_impressions_per_tweet")
        imp_target = targets.get("avg_impressions_per_tweet")
        if avg_imp is not None and imp_target:
            progress["avg_impressions"] = {
                "actual": avg_imp,
                "target": imp_target,
                "status": "ON_TRACK" if avg_imp >= imp_target else "BEHIND",
            }

        return progress

    def _generate_recommendations(
        self,
        metrics: Dict,
        top_performers: List[Dict],
        bottom_performers: List[Dict],
        content_breakdown: Dict,
    ) -> List[str]:
        recs = []

        er = metrics.get("engagement_rate_pct")
        if er is not None and er < 1.0:
            recs.append(
                "Engagement rate is below 1%. Focus on content that generates replies "
                "(questions, contrarian takes) rather than passive likes."
            )

        reply_ratio = metrics.get("engagement_quality", {}).get("reply_ratio")
        if reply_ratio is not None and reply_ratio < 20:
            recs.append(
                "Reply ratio is low. Add discussion prompts and open-ended questions "
                "to your posts. Replies have the highest algorithm weight."
            )

        if top_performers:
            best = top_performers[0]
            recs.append(
                f"Your top performer had {best['engagement_rate_pct']}% ER. "
                f"Analyze what made it work and create similar content."
            )

        if bottom_performers:
            worst = bottom_performers[0]
            if worst["engagement_rate_pct"] == 0:
                recs.append(
                    "You have posts with 0% engagement. Review posting time and content quality. "
                    "Consider if the topic matched your audience's interests."
                )

        return recs


if __name__ == "__main__":
    reporter = AnalyticsReporter()
    print("Analytics Reporter v1.0")
    print("=" * 40)
    print()
    print("This module generates performance reports from validated X data.")
    print("It is designed to be called by an AI agent during review cycles.")
    print()
    print("Usage:")
    print("  from analytics_reporter import AnalyticsReporter")
    print()
    print("  reporter = AnalyticsReporter(goals_path='config/goals.json')")
    print("  report = reporter.generate_report(validated_tweets)")
    print()
    print("See SKILL.md for full integration details.")
