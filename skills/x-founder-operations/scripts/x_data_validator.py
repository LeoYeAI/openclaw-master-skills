#!/usr/bin/env python3
"""
X Data Validator — Complete validation workflow for X analytics data.

Core Principle: Data verifiable, anomalies flagged, NEVER guess to fill gaps.

Validation Layers:
1. Fetch timeline → Get tweet list
2. Fetch details → Get metrics per tweet
3. Cross-validate → ID, author, timestamp consistency
4. Sanity check → Reasonable data (likes ≤ impressions)
5. Report → Mark anomalies, never guess

Usage:
    This module is designed to be used by an AI agent, not executed directly.
    The agent calls tool APIs and passes results through the validator.

    from x_data_validator import XDataValidator, generate_execution_plan

    validator = XDataValidator("@handle")
    plan = generate_execution_plan("@handle")
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any


class XDataValidator:
    """Validates X data integrity through a 5-layer pipeline."""

    def __init__(self, username: str):
        self.username = username
        self.validation_report = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "validation_version": "3.0",
            "principles": [
                "Data verifiable: every data point has source and validation record",
                "Anomalies flagged: any anomaly recorded in validation report",
                "NEVER guess to fill gaps: missing data marked as null"
            ],
            "checks": [],
            "errors": [],
            "warnings": [],
            "data_quality_score": 100,
            "tweets_analyzed": 0,
            "tweets_valid": 0,
            "tweets_invalid": 0
        }
        self.timeline_cache: Dict[str, Dict] = {}

    def validate_timeline_data(self, timeline_data: Dict) -> Tuple[Optional[List[Dict]], List[Dict]]:
        """
        Layer 1: Validate timeline data structure and content.

        Returns: (valid_tweets_list, validation_checks)
        """
        checks = []

        if not timeline_data:
            checks.append({
                "step": "timeline_fetch",
                "status": "FAILED",
                "message": "Timeline data is None or empty",
                "action": "STOP — cannot proceed without timeline data",
                "severity": "CRITICAL"
            })
            self._log_error("Timeline fetch failed — no data", {})
            return None, checks

        if not timeline_data.get("ok"):
            error = timeline_data.get("error", "unknown")
            checks.append({
                "step": "timeline_api_status",
                "status": "FAILED",
                "message": f"API returned error: {error}",
                "action": "STOP — API error, cannot trust data",
                "severity": "CRITICAL"
            })
            self._log_error(f"Timeline API error: {error}", timeline_data)
            return None, checks

        tweets = timeline_data.get("tweets", [])

        if not tweets:
            checks.append({
                "step": "timeline_content",
                "status": "WARNING",
                "message": "Timeline exists but contains no tweets",
                "action": "CONTINUE — may be new account or no recent posts",
                "severity": "WARNING"
            })
            return [], checks

        valid_tweets = []
        invalid_tweets = []

        for i, tweet in enumerate(tweets):
            tweet_id = tweet.get("id")

            if not tweet_id:
                invalid_tweets.append({
                    "index": i,
                    "reason": "Missing tweet ID",
                    "available_fields": list(tweet.keys())
                })
                self._log_warning(f"Tweet[{i}] missing ID", {"fields": list(tweet.keys())})
                continue

            self.timeline_cache[tweet_id] = {
                "text_preview": tweet.get("text", "")[:100],
                "createdAt": tweet.get("createdAt"),
                "authorId": tweet.get("authorId")
            }
            valid_tweets.append(tweet)

        checks.append({
            "step": "timeline_validation",
            "status": "OK" if not invalid_tweets else "PARTIAL",
            "message": f"Timeline validated: {len(valid_tweets)}/{len(tweets)} tweets valid",
            "details": {
                "total": len(tweets),
                "valid": len(valid_tweets),
                "invalid": len(invalid_tweets),
                "invalid_details": invalid_tweets if invalid_tweets else None
            },
            "action": "CONTINUE" if valid_tweets else "STOP — no valid tweets"
        })

        self.validation_report["tweets_analyzed"] = len(tweets)
        return valid_tweets, checks

    def validate_tweet_details(self, tweet_data: Dict, original_tweet: Dict) -> Tuple[Optional[Dict], List[Dict]]:
        """
        Layers 2-4: Validate tweet details, cross-validate, and sanity check.

        Returns: (validated_tweet_data, validation_checks)
        """
        checks = []
        tweet_id = original_tweet.get("id")

        if not tweet_data:
            checks.append({
                "step": "tweet_details_fetch",
                "status": "FAILED",
                "tweet_id": tweet_id,
                "message": "Tweet details data is None or empty",
                "action": "SKIP — cannot validate without data",
                "severity": "ERROR"
            })
            self._log_error(f"Tweet {tweet_id} details fetch failed", {})
            return None, checks

        if not tweet_data.get("ok"):
            error = tweet_data.get("error", "unknown")
            checks.append({
                "step": "tweet_api_status",
                "status": "FAILED",
                "tweet_id": tweet_id,
                "message": f"API returned error: {error}",
                "action": "SKIP — API error for this tweet",
                "severity": "ERROR"
            })
            self._log_error(f"Tweet {tweet_id} API error: {error}", tweet_data)
            return None, checks

        tweet = tweet_data.get("tweet")
        if not tweet:
            checks.append({
                "step": "tweet_data_structure",
                "status": "FAILED",
                "tweet_id": tweet_id,
                "message": "API returned ok=True but tweet data is missing",
                "action": "SKIP — missing tweet data",
                "severity": "ERROR"
            })
            self._log_error(f"Tweet {tweet_id} missing data despite ok=True", tweet_data)
            return None, checks

        # --- Cross-validation (Layer 3) ---

        returned_id = tweet.get("id")
        if returned_id != tweet_id:
            checks.append({
                "step": "cross_validation_id",
                "status": "CRITICAL_ERROR",
                "tweet_id": tweet_id,
                "message": f"ID MISMATCH! Requested: {tweet_id}, Returned: {returned_id}",
                "action": "SKIP — data integrity compromised",
                "severity": "CRITICAL"
            })
            self._log_error("ID mismatch", {"requested": tweet_id, "returned": returned_id})
            return None, checks

        timeline_author = self.timeline_cache.get(tweet_id, {}).get("authorId")
        details_author = tweet.get("authorId")
        if timeline_author and details_author and timeline_author != details_author:
            checks.append({
                "step": "cross_validation_author",
                "status": "ERROR",
                "tweet_id": tweet_id,
                "message": "Author ID mismatch between timeline and details",
                "severity": "ERROR"
            })
            self._log_error(f"Author mismatch for tweet {tweet_id}", {
                "timeline": timeline_author, "details": details_author
            })

        timeline_time = self.timeline_cache.get(tweet_id, {}).get("createdAt")
        details_time = tweet.get("createdAt")
        if timeline_time and details_time and timeline_time != details_time:
            checks.append({
                "step": "cross_validation_timestamp",
                "status": "WARNING",
                "tweet_id": tweet_id,
                "message": "Timestamp mismatch between timeline and details",
                "severity": "WARNING"
            })
            self._log_warning(f"Timestamp mismatch for tweet {tweet_id}", {
                "timeline": timeline_time, "details": details_time
            })

        # --- Metrics completeness ---

        metrics = tweet.get("metrics", {})
        required_metrics = ["likeCount", "retweetCount", "replyCount", "quoteCount", "impressionCount"]
        missing_metrics = [m for m in required_metrics if m not in metrics]

        if missing_metrics:
            checks.append({
                "step": "metrics_completeness",
                "status": "WARNING",
                "tweet_id": tweet_id,
                "message": f"Missing metrics fields: {missing_metrics}",
                "severity": "WARNING"
            })
            self._log_warning(f"Tweet {tweet_id} missing metrics", {"missing": missing_metrics})
            for m in missing_metrics:
                metrics[m] = None

        # --- Sanity checks (Layer 4) ---

        likes = metrics.get("likeCount")
        retweets = metrics.get("retweetCount")
        impressions = metrics.get("impressionCount")

        if likes is not None and impressions is not None and likes > impressions:
            checks.append({
                "step": "sanity_check_likes",
                "status": "ERROR",
                "tweet_id": tweet_id,
                "message": f"IMPOSSIBLE: Likes ({likes}) > Impressions ({impressions})",
                "action": "FLAG_ANOMALY — data error detected but not modified",
                "severity": "ERROR"
            })
            self._log_error("Data anomaly: likes > impressions", {
                "tweet_id": tweet_id, "likes": likes, "impressions": impressions
            })

        if retweets is not None and impressions is not None and retweets > impressions:
            checks.append({
                "step": "sanity_check_retweets",
                "status": "ERROR",
                "tweet_id": tweet_id,
                "message": f"IMPOSSIBLE: Retweets ({retweets}) > Impressions ({impressions})",
                "severity": "ERROR"
            })
            self._log_error("Data anomaly: retweets > impressions", {
                "tweet_id": tweet_id, "retweets": retweets, "impressions": impressions
            })

        for metric_name in required_metrics:
            value = metrics.get(metric_name)
            if value is not None and value < 0:
                checks.append({
                    "step": f"sanity_check_{metric_name}",
                    "status": "ERROR",
                    "tweet_id": tweet_id,
                    "message": f"IMPOSSIBLE: {metric_name} is negative ({value})",
                    "severity": "ERROR"
                })
                self._log_error(f"Negative value for {metric_name}", {
                    "tweet_id": tweet_id, "value": value
                })

        checks.append({
            "step": "tweet_validation_complete",
            "status": "OK",
            "tweet_id": tweet_id,
            "message": "Tweet data validated successfully",
            "has_warnings": any(c.get("severity") == "WARNING" for c in checks),
            "has_errors": any(c.get("severity") == "ERROR" for c in checks)
        })

        return tweet, checks

    def calculate_metrics(self, validated_tweets: List[Dict]) -> Dict:
        """Layer 5: Calculate summary metrics from complete data only."""
        if not validated_tweets:
            return {
                "total_tweets": 0,
                "complete_data": 0,
                "incomplete_data": 0,
                "note": "No validated tweets to analyze"
            }

        complete_tweets = []
        incomplete_tweets = []
        total_engagement = 0
        total_impressions = 0

        required = ["likeCount", "retweetCount", "replyCount", "quoteCount", "impressionCount"]

        for tweet in validated_tweets:
            metrics = tweet.get("metrics", {})
            is_complete = all(metrics.get(m) is not None for m in required)

            if is_complete:
                complete_tweets.append(tweet)
                total_engagement += sum(metrics[m] for m in required if m != "impressionCount")
                total_impressions += metrics["impressionCount"]
            else:
                incomplete_tweets.append({
                    "id": tweet.get("id"),
                    "missing_metrics": [m for m in required if metrics.get(m) is None]
                })

        summary = {
            "total_tweets": len(validated_tweets),
            "complete_data": len(complete_tweets),
            "incomplete_data": len(incomplete_tweets),
            "incomplete_details": incomplete_tweets if incomplete_tweets else None
        }

        if complete_tweets:
            summary["avg_engagement"] = round(total_engagement / len(complete_tweets), 2)
            summary["avg_impressions"] = round(total_impressions / len(complete_tweets), 2)
            summary["engagement_rate"] = (
                round(total_engagement / total_impressions * 100, 2)
                if total_impressions > 0 else None
            )
            summary["total_engagement"] = total_engagement
            summary["total_impressions"] = total_impressions
        else:
            summary["note"] = "No complete data available for calculations"

        return summary

    def _log_error(self, message: str, details: Dict):
        self.validation_report["errors"].append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "details": details
        })
        self.validation_report["data_quality_score"] = max(
            0, self.validation_report["data_quality_score"] - 10
        )

    def _log_warning(self, message: str, details: Dict):
        self.validation_report["warnings"].append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "details": details
        })
        self.validation_report["data_quality_score"] = max(
            0, self.validation_report["data_quality_score"] - 3
        )

    def finalize_report(self) -> Dict:
        """Finalize and return the complete validation report."""
        self.validation_report["total_checks"] = len(self.validation_report["checks"])
        self.validation_report["total_errors"] = len(self.validation_report["errors"])
        self.validation_report["total_warnings"] = len(self.validation_report["warnings"])
        return self.validation_report


def generate_execution_plan(username: str) -> Dict:
    """
    Generate a step-by-step execution plan for X data analysis.

    This plan is designed to be executed by an AI agent using tool calls.
    The agent reads each step and executes the corresponding tool.
    """
    plan = {
        "analysis_id": f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "username": username,
        "created_at": datetime.now().isoformat(),
        "validation_principles": [
            "Data verifiable: every data point has source and validation record",
            "Anomalies flagged: any anomaly recorded in validation report",
            "NEVER guess to fill gaps: missing data marked as null"
        ],
        "steps": [
            {
                "step": 1,
                "name": "fetch_timeline",
                "description": f"Get recent tweets from {username}",
                "tool": "x-timeline",
                "target": username,
                "on_failure": "STOP — cannot proceed without timeline data"
            },
            {
                "step": 2,
                "name": "validate_timeline",
                "description": "Validate timeline data structure",
                "action": "XDataValidator.validate_timeline_data(timeline_data)",
                "output": "List of valid tweets for detail fetching"
            },
            {
                "step": 3,
                "name": "fetch_tweet_details",
                "description": "Get detailed metrics for each valid tweet",
                "tool": "x-tweet-info",
                "iteration": "For each tweet in valid_tweets",
                "on_failure": "SKIP this tweet, continue with others"
            },
            {
                "step": 4,
                "name": "validate_and_cross_check",
                "description": "Cross-validate and sanity-check each tweet's data",
                "action": "XDataValidator.validate_tweet_details(details, original)",
                "checks": [
                    "ID consistency",
                    "Author consistency",
                    "Timestamp consistency",
                    "Metrics completeness",
                    "Data sanity (likes <= impressions, no negatives)"
                ]
            },
            {
                "step": 5,
                "name": "calculate_metrics",
                "description": "Calculate summary statistics from complete data only",
                "action": "XDataValidator.calculate_metrics(validated_tweets)",
                "note": "Missing data excluded, not estimated"
            },
            {
                "step": 6,
                "name": "generate_report",
                "description": "Produce final validation report",
                "action": "XDataValidator.finalize_report()",
                "output": ["data_quality_score", "metrics_summary", "errors", "warnings"]
            }
        ]
    }
    return plan


if __name__ == "__main__":
    print("X Data Validator v3.0")
    print("=" * 40)
    print()
    print("This module provides data validation for X analytics.")
    print("It is designed to be used by an AI agent, not executed directly.")
    print()
    print("Usage:")
    print("  from x_data_validator import XDataValidator, generate_execution_plan")
    print()
    print("  validator = XDataValidator('@handle')")
    print("  plan = generate_execution_plan('@handle')")
    print()
    print("See SKILL.md for full integration details.")
