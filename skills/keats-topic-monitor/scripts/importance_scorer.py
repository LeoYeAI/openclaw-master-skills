#!/usr/bin/env python3
"""
AI-powered importance scoring for research findings.

Scores findings as:
- HIGH: Immediate alert
- MEDIUM: Include in digest
- LOW: Ignore
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime, timedelta


class ImportanceScorer:
    """Score research findings for importance."""
    
    def __init__(self, topic: Dict, settings: Dict):
        self.topic = topic
        self.settings = settings
        self.learning_enabled = settings.get("learning_enabled", False)
    
    def score(self, result: Dict) -> Tuple[str, float, str]:
        """
        Score a search result.
        
        Returns:
            (priority, score, reason)
            priority: "high", "medium", "low"
            score: 0.0-1.0
            reason: Human-readable explanation
        """
        signals = []
        total_score = 0.0
        
        # Extract fields
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        url = result.get("url", "")
        published = result.get("published_date", "")
        content = f"{title} {snippet}".lower()
        
        # Signal 1: Keyword matching (0.0 - 0.3)
        keyword_score, keyword_reason = self._score_keywords(content)
        signals.append(("keyword_match", keyword_score, keyword_reason))
        total_score += keyword_score
        
        # Signal 2: Freshness (0.0 - 0.2)
        freshness_score, freshness_reason = self._score_freshness(published)
        signals.append(("freshness", freshness_score, freshness_reason))
        total_score += freshness_score
        
        # Signal 3: Source quality (0.0 - 0.2)
        source_score, source_reason = self._score_source(url)
        signals.append(("source_quality", source_score, source_reason))
        total_score += source_score
        
        # Signal 4: Alert conditions (0.0 - 0.3)
        condition_score, condition_reason = self._score_conditions(content, title)
        signals.append(("alert_conditions", condition_score, condition_reason))
        total_score += condition_score
        
        # Determine priority
        threshold = self.topic.get("importance_threshold", "medium")
        
        if threshold == "high":
            # Only very high scores alert
            if total_score >= 0.8:
                priority = "high"
            elif total_score >= 0.5:
                priority = "medium"
            else:
                priority = "low"
        elif threshold == "medium":
            # Balanced
            if total_score >= 0.6:
                priority = "high"
            elif total_score >= 0.3:
                priority = "medium"
            else:
                priority = "low"
        else:  # low
            # Almost everything goes to digest
            if total_score >= 0.4:
                priority = "high"
            elif total_score >= 0.1:
                priority = "medium"
            else:
                priority = "low"
        
        # Build reason
        top_signals = sorted(signals, key=lambda x: x[1], reverse=True)[:2]
        reason_parts = [s[2] for s in top_signals if s[2]]
        reason = " + ".join(reason_parts) if reason_parts else "low_relevance"
        
        return priority, total_score, reason
    
    def _score_keywords(self, content: str) -> Tuple[float, str]:
        """Score based on keyword matching."""
        keywords = self.topic.get("keywords", [])
        if not keywords:
            return 0.0, ""
        
        matches = 0
        exact_matches = 0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Check for negation (keywords starting with -)
            if keyword.startswith("-"):
                negative_keyword = keyword_lower[1:]
                if negative_keyword in content:
                    return 0.0, f"contains_excluded_{negative_keyword}"
                continue
            
            # Exact match (whole word)
            if re.search(r'\b' + re.escape(keyword_lower) + r'\b', content):
                exact_matches += 1
                matches += 1
            # Partial match
            elif keyword_lower in content:
                matches += 1
        
        if exact_matches >= 2:
            return 0.3, f"exact_match_{exact_matches}_keywords"
        elif exact_matches == 1:
            return 0.2, "exact_match_1_keyword"
        elif matches >= 2:
            return 0.15, f"partial_match_{matches}_keywords"
        elif matches == 1:
            return 0.1, "partial_match_1_keyword"
        else:
            return 0.0, "no_keyword_match"
    
    def _score_freshness(self, published: str) -> Tuple[float, str]:
        """Score based on recency."""
        if not published:
            return 0.0, ""
        
        try:
            # Try parsing ISO format
            if "T" in published:
                pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
            else:
                pub_date = datetime.strptime(published, "%Y-%m-%d")
            
            age = datetime.now() - pub_date.replace(tzinfo=None)
            
            if age < timedelta(hours=6):
                return 0.2, "very_fresh_<6h"
            elif age < timedelta(days=1):
                return 0.15, "fresh_<24h"
            elif age < timedelta(days=3):
                return 0.1, "recent_<3d"
            else:
                return 0.05, "older_>3d"
        except:
            return 0.0, ""
    
    def _score_source(self, url: str) -> Tuple[float, str]:
        """Score based on source quality."""
        # Check boost sources
        boost_sources = self.topic.get("boost_sources", [])
        for source in boost_sources:
            if source in url:
                return 0.2, f"boosted_source_{source}"
        
        # Check ignore sources
        ignore_sources = self.topic.get("ignore_sources", [])
        for source in ignore_sources:
            if source in url:
                return -1.0, f"ignored_source_{source}"
        
        # Default trusted sources
        trusted = ["github.com", "arxiv.org", "news.ycombinator.com", 
                   "techcrunch.com", "theverge.com", "arstechnica.com"]
        for source in trusted:
            if source in url:
                return 0.15, f"trusted_source_{source}"
        
        return 0.05, "standard_source"
    
    def _score_conditions(self, content: str, title: str) -> Tuple[float, str]:
        """Score based on alert conditions."""
        alert_on = self.topic.get("alert_on", [])
        
        for condition in alert_on:
            if condition == "price_change_10pct":
                if self._detect_price_change(content, threshold=0.10):
                    return 0.3, "price_change_>10%"
            
            elif condition == "keyword_exact_match":
                # Already handled in keyword scoring, but boost it
                keywords = self.topic.get("keywords", [])
                for kw in keywords:
                    if re.search(r'\b' + re.escape(kw.lower()) + r'\b', content):
                        return 0.2, "exact_keyword_in_condition"
            
            elif condition == "major_paper":
                if "arxiv" in content or "paper" in title.lower():
                    return 0.25, "academic_paper_detected"
            
            elif condition == "model_release":
                if re.search(r'(release|launch|announce).*\b(model|gpt|llm)\b', content, re.I):
                    return 0.3, "model_release_detected"
            
            elif condition == "patch_release":
                if re.search(r'(patch|update|version|release).*\d+\.\d+', content, re.I):
                    return 0.25, "patch_release_detected"
            
            elif condition == "major_bug_fix":
                if re.search(r'(fix|patch|solve).*(critical|major|bug)', content, re.I):
                    return 0.2, "major_bug_fix_detected"
            
            elif condition == "high_engagement":
                # Would need engagement data from API
                pass
            
            elif condition == "source_tier_1":
                # Already handled in source scoring
                pass
        
        return 0.0, ""
    
    def _detect_price_change(self, content: str, threshold: float = 0.10) -> bool:
        """Detect significant price changes."""
        # Look for percentage patterns
        pct_pattern = r'(\d+(?:\.\d+)?)\s*%'
        matches = re.findall(pct_pattern, content)
        
        for match in matches:
            pct = float(match)
            if pct >= threshold * 100:  # Convert to percentage
                return True
        
        # Look for price change keywords
        change_keywords = ["surge", "plunge", "jump", "drop", "spike", "crash"]
        for keyword in change_keywords:
            if keyword in content.lower():
                return True
        
        return False


def score_result(result: Dict, topic: Dict, settings: Dict) -> Tuple[str, float, str]:
    """
    Score a single search result.
    
    Convenience function for scoring without creating scorer instance.
    """
    scorer = ImportanceScorer(topic, settings)
    return scorer.score(result)
