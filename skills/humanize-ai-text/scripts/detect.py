#!/usr/bin/env python3
"""Detect AI patterns in text based on Wikipedia's Signs of AI Writing."""
import argparse, json, re, sys
from pathlib import Path
from dataclasses import dataclass, field

SCRIPT_DIR = Path(__file__).parent
PATTERNS = json.loads((SCRIPT_DIR / "patterns.json").read_text())

@dataclass
class DetectionResult:
    significance_inflation: list = field(default_factory=list)
    notability_emphasis: list = field(default_factory=list)
    superficial_analysis: list = field(default_factory=list)
    promotional_language: list = field(default_factory=list)
    vague_attributions: list = field(default_factory=list)
    challenges_formula: list = field(default_factory=list)
    ai_vocabulary: list = field(default_factory=list)
    copula_avoidance: list = field(default_factory=list)
    filler_phrases: list = field(default_factory=list)
    chatbot_artifacts: list = field(default_factory=list)
    hedging_phrases: list = field(default_factory=list)
    negative_parallelisms: list = field(default_factory=list)
    rule_of_three: list = field(default_factory=list)
    markdown_artifacts: list = field(default_factory=list)
    citation_bugs: list = field(default_factory=list)
    knowledge_cutoff: list = field(default_factory=list)
    curly_quotes: int = 0
    em_dashes: int = 0
    total_issues: int = 0
    ai_probability: str = "low"
    word_count: int = 0

def find_matches(text: str, patterns: list) -> list:
    matches, lower = [], text.lower()
    for p in patterns:
        count = lower.count(p.lower())
        if count > 0:
            matches.append((p, count))
    return sorted(matches, key=lambda x: -x[1])

def detect(text: str) -> DetectionResult:
    r = DetectionResult()
    r.word_count = len(text.split())
    r.significance_inflation = find_matches(text, PATTERNS["significance_inflation"])
    r.notability_emphasis = find_matches(text, PATTERNS["notability_emphasis"])
    r.superficial_analysis = find_matches(text, PATTERNS["superficial_analysis"])
    r.promotional_language = find_matches(text, PATTERNS["promotional_language"])
    r.vague_attributions = find_matches(text, PATTERNS["vague_attributions"])
    r.challenges_formula = find_matches(text, PATTERNS["challenges_formula"])
    r.ai_vocabulary = find_matches(text, PATTERNS["ai_vocabulary"])
    r.copula_avoidance = find_matches(text, list(PATTERNS["copula_avoidance"].keys()))
    r.filler_phrases = find_matches(text, list(PATTERNS["filler_replacements"].keys()))
    r.chatbot_artifacts = find_matches(text, PATTERNS["chatbot_artifacts"])
    r.hedging_phrases = find_matches(text, PATTERNS["hedging_phrases"])
    r.negative_parallelisms = find_matches(text, PATTERNS["negative_parallelisms"])
    r.rule_of_three = find_matches(text, PATTERNS["rule_of_three_patterns"])
    r.markdown_artifacts = find_matches(text, PATTERNS["markdown_artifacts"])
    r.citation_bugs = find_matches(text, PATTERNS["citation_bugs"])
    r.knowledge_cutoff = find_matches(text, PATTERNS["knowledge_cutoff"])
    r.curly_quotes = len(re.findall(r'[""'']', text))
    r.em_dashes = text.count("—") + text.count(" -- ")
    
    r.total_issues = (
        sum(c for _, c in r.significance_inflation) + sum(c for _, c in r.notability_emphasis) +
        sum(c for _, c in r.superficial_analysis) + sum(c for _, c in r.promotional_language) +
        sum(c for _, c in r.vague_attributions) + sum(c for _, c in r.challenges_formula) +
        sum(c for _, c in r.ai_vocabulary) + sum(c for _, c in r.copula_avoidance) +
        sum(c for _, c in r.filler_phrases) + sum(c for _, c in r.chatbot_artifacts) * 3 +
        sum(c for _, c in r.hedging_phrases) + sum(c for _, c in r.negative_parallelisms) +
        sum(c for _, c in r.markdown_artifacts) * 2 + sum(c for _, c in r.citation_bugs) * 5 +
        sum(c for _, c in r.knowledge_cutoff) * 3 + r.curly_quotes + (r.em_dashes if r.em_dashes > 3 else 0)
    )
    
    density = r.total_issues / max(r.word_count, 1) * 100
    if r.citation_bugs or r.knowledge_cutoff or r.chatbot_artifacts:
        r.ai_probability = "very high"
    elif density > 5 or r.total_issues > 30:
        r.ai_probability = "high"
    elif density > 2 or r.total_issues > 15:
        r.ai_probability = "medium"
    return r

def print_section(title: str, items: list, replacements: dict = None):
    if not items:
        return
    print(f"{title}:")
    for phrase, count in items:
        if replacements and phrase in replacements:
            repl = replacements[phrase]
            arrow = f' → "{repl}"' if repl else " → (remove)"
            print(f"  • \"{phrase}\"{arrow}: {count}x")
        else:
            print(f"  • {phrase}: {count}x")
    print()

def print_report(r: DetectionResult):
    icons = {"very high": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    print(f"\n{'='*60}")
    print(f"AI DETECTION SCAN - {r.total_issues} issues ({r.word_count} words)")
    print(f"AI Probability: {icons.get(r.ai_probability, '')} {r.ai_probability.upper()}")
    print(f"{'='*60}\n")
    
    if r.citation_bugs:
        print("⚠️  CRITICAL: CHATGPT CITATION BUGS")
        print_section("Citation Artifacts", r.citation_bugs)
    if r.knowledge_cutoff:
        print("⚠️  CRITICAL: KNOWLEDGE CUTOFF PHRASES")
        print_section("Cutoff Phrases", r.knowledge_cutoff)
    if r.chatbot_artifacts:
        print("⚠️  HIGH: CHATBOT ARTIFACTS")
        print_section("Artifacts", r.chatbot_artifacts)
    if r.markdown_artifacts:
        print("⚠️  MARKDOWN DETECTED")
        print_section("Markdown", r.markdown_artifacts)
    
    print_section("SIGNIFICANCE INFLATION", r.significance_inflation)
    print_section("PROMOTIONAL LANGUAGE", r.promotional_language)
    print_section("AI VOCABULARY", r.ai_vocabulary)
    print_section("SUPERFICIAL -ING", r.superficial_analysis)
    print_section("COPULA AVOIDANCE", r.copula_avoidance, PATTERNS["copula_avoidance"])
    print_section("FILLER PHRASES", r.filler_phrases, PATTERNS["filler_replacements"])
    print_section("VAGUE ATTRIBUTIONS", r.vague_attributions)
    print_section("CHALLENGES FORMULA", r.challenges_formula)
    print_section("HEDGING", r.hedging_phrases)
    print_section("NEGATIVE PARALLELISMS", r.negative_parallelisms)
    print_section("NOTABILITY EMPHASIS", r.notability_emphasis)
    
    if r.curly_quotes:
        print(f"CURLY QUOTES: {r.curly_quotes} (ChatGPT signature)\n")
    if r.em_dashes > 3:
        print(f"EM DASHES: {r.em_dashes} (excessive)\n")
    if r.total_issues == 0:
        print("✓ No AI patterns detected.\n")

def main():
    parser = argparse.ArgumentParser(description="Detect AI patterns in text")
    parser.add_argument("input", nargs="?", help="Input file (or stdin)")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    parser.add_argument("--score-only", "-s", action="store_true", help="Score and probability only")
    args = parser.parse_args()
    
    text = Path(args.input).read_text() if args.input else sys.stdin.read()
    result = detect(text)
    
    if args.json:
        print(json.dumps({
            "total_issues": result.total_issues, "word_count": result.word_count,
            "ai_probability": result.ai_probability, "significance_inflation": result.significance_inflation,
            "promotional_language": result.promotional_language, "ai_vocabulary": result.ai_vocabulary,
            "chatbot_artifacts": result.chatbot_artifacts, "citation_bugs": result.citation_bugs,
            "filler_phrases": result.filler_phrases, "curly_quotes": result.curly_quotes, "em_dashes": result.em_dashes,
        }, indent=2))
    elif args.score_only:
        print(f"Issues: {result.total_issues} | Words: {result.word_count} | AI: {result.ai_probability}")
    else:
        print_report(result)

if __name__ == "__main__":
    main()
