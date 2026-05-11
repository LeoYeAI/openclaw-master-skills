"""
SERP content analyzer for SEO-AGI.
Analyzes competitor content structure and identifies content gaps.
"""

import statistics
from typing import Optional


def analyze_serp(
    serp_data: dict,
    content_data: list[Optional[dict]],
    target_keyword: str,
) -> dict:
    """
    Analyze SERP results + parsed competitor content.

    Args:
        serp_data: Output from DataForSEOClient.serp_live()
        content_data: List of DataForSEOClient.content_parse() results
            (one per organic result, may contain None for failed parses)
        target_keyword: The keyword being targeted

    Returns:
        Analysis dict with intent, word count stats, topic coverage, gaps.
    """
    organic = serp_data.get("organic", [])
    paa = serp_data.get("paa", [])

    # Word count analysis
    word_counts = []
    all_headings = []
    all_topics = set()

    for i, content in enumerate(content_data):
        if content is None:
            continue

        wc = content.get("word_count", 0)
        if wc > 0:
            word_counts.append(wc)

        headings = content.get("headings", [])
        all_headings.extend(headings)

        # Extract topics from H2/H3 headings
        for h in headings:
            if h.startswith(("H2:", "H3:")):
                topic = h.split(":", 1)[1].strip().lower()
                all_topics.add(topic)

    # Word count statistics
    wc_stats = {}
    if word_counts:
        wc_stats = {
            "min": min(word_counts),
            "max": max(word_counts),
            "median": int(statistics.median(word_counts)),
            "mean": int(statistics.mean(word_counts)),
            "recommended_min": int(statistics.median(word_counts) * 0.8),
            "recommended_max": int(statistics.median(word_counts) * 1.3),
            "count_analyzed": len(word_counts),
        }

    # Intent detection
    intent = detect_intent(target_keyword, organic, serp_data)

    # Topic frequency (which topics appear in multiple competitors)
    topic_freq = _count_topic_frequency(content_data)

    # Heading patterns
    heading_patterns = _analyze_heading_patterns(content_data)

    return {
        "keyword": target_keyword,
        "intent": intent,
        "word_count_stats": wc_stats,
        "paa_questions": paa,
        "topic_frequency": topic_freq,
        "heading_patterns": heading_patterns,
        "competitors_analyzed": len(
            [c for c in content_data if c is not None]
        ),
        "total_organic_results": len(organic),
        "featured_snippet": serp_data.get("featured_snippet"),
    }


def detect_intent(
    keyword: str, organic: list[dict], serp_data: dict
) -> str:
    """
    Detect search intent from keyword and SERP features.

    Returns: informational, commercial, transactional, or navigational
    """
    kw_lower = keyword.lower()

    # Navigational signals
    nav_signals = [
        "login",
        "sign in",
        "website",
        "official",
        ".com",
        ".org",
    ]
    if any(s in kw_lower for s in nav_signals):
        return "navigational"

    # Transactional signals
    transactional_signals = [
        "buy",
        "purchase",
        "order",
        "download",
        "subscribe",
        "deal",
        "discount",
        "coupon",
        "price",
        "pricing",
        "cost",
        "cheap",
        "free trial",
    ]
    if any(s in kw_lower for s in transactional_signals):
        return "transactional"

    # Commercial investigation signals
    commercial_signals = [
        "best",
        "top",
        "review",
        "comparison",
        "vs",
        "versus",
        "alternative",
        "vs.",
        "compared to",
        "pros and cons",
    ]
    if any(s in kw_lower for s in commercial_signals):
        return "commercial"

    # Informational signals
    informational_signals = [
        "how to",
        "what is",
        "what are",
        "why",
        "guide",
        "tutorial",
        "learn",
        "example",
        "definition",
        "meaning",
        "explain",
    ]
    if any(s in kw_lower for s in informational_signals):
        return "informational"

    # Default: check SERP patterns
    if serp_data.get("featured_snippet"):
        return "informational"

    # If titles contain pricing/comparison language
    titles = [r.get("title", "").lower() for r in organic[:5]]
    title_text = " ".join(titles)

    if any(s in title_text for s in ["best", "top", "review", "vs"]):
        return "commercial"
    if any(
        s in title_text for s in ["how to", "guide", "what", "tutorial"]
    ):
        return "informational"

    return "commercial"  # default for ambiguous


def _count_topic_frequency(
    content_data: list[Optional[dict]],
) -> list[dict]:
    """Count how often topics (H2/H3 headings) appear across competitors."""
    topic_counts = {}

    for content in content_data:
        if content is None:
            continue

        seen_in_page = set()
        for heading in content.get("headings", []):
            if heading.startswith(("H2:", "H3:")):
                topic = heading.split(":", 1)[1].strip().lower()
                # Normalize common variations
                topic = _normalize_topic(topic)
                if topic and topic not in seen_in_page:
                    seen_in_page.add(topic)
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1

    # Sort by frequency
    sorted_topics = sorted(
        topic_counts.items(), key=lambda x: x[1], reverse=True
    )
    return [
        {"topic": t, "competitor_count": c} for t, c in sorted_topics[:30]
    ]


def _normalize_topic(topic: str) -> str:
    """Basic topic normalization."""
    # Remove common filler words at start
    for prefix in [
        "the ",
        "a ",
        "an ",
        "our ",
        "your ",
        "my ",
        "about ",
    ]:
        if topic.startswith(prefix):
            topic = topic[len(prefix) :]

    # Strip trailing punctuation
    topic = topic.rstrip(".:!?")

    return topic.strip()


def _analyze_heading_patterns(
    content_data: list[Optional[dict]],
) -> dict:
    """Analyze heading patterns across competitors."""
    h2_counts = []
    h3_counts = []

    for content in content_data:
        if content is None:
            continue

        headings = content.get("headings", [])
        h2_count = sum(1 for h in headings if h.startswith("H2:"))
        h3_count = sum(1 for h in headings if h.startswith("H3:"))
        h2_counts.append(h2_count)
        h3_counts.append(h3_count)

    return {
        "avg_h2_count": (
            round(statistics.mean(h2_counts), 1) if h2_counts else 0
        ),
        "avg_h3_count": (
            round(statistics.mean(h3_counts), 1) if h3_counts else 0
        ),
        "median_h2_count": (
            int(statistics.median(h2_counts)) if h2_counts else 0
        ),
        "median_h3_count": (
            int(statistics.median(h3_counts)) if h3_counts else 0
        ),
    }
