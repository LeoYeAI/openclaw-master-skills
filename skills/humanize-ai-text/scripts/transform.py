#!/usr/bin/env python3
"""Transform AI text to bypass detection."""
import argparse, json, re, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PATTERNS = json.loads((SCRIPT_DIR / "patterns.json").read_text())

def replace_bounded(text: str, old: str, new: str) -> tuple[str, int]:
    pattern = re.compile(re.escape(old), re.IGNORECASE) if " " in old or old.endswith(",") else re.compile(r"\b" + re.escape(old) + r"\b", re.IGNORECASE)
    matches = pattern.findall(text)
    return pattern.sub(new, text) if matches else text, len(matches)

def apply_replacements(text: str, replacements: dict) -> tuple[str, list]:
    changes = []
    for old, new in replacements.items():
        text, count = replace_bounded(text, old, new)
        if count:
            changes.append(f'"{old}" → "{new}"' if new else f'"{old}" removed')
    return text, changes

def fix_quotes(text: str) -> tuple[str, bool]:
    original = text
    for old, new in PATTERNS["curly_quotes"].items():
        text = text.replace(old, new)
    return text, text != original

def remove_chatbot_sentences(text: str) -> tuple[str, list]:
    changes = []
    for artifact in PATTERNS["chatbot_artifacts"]:
        pattern = re.compile(r"[^.!?\n]*" + re.escape(artifact) + r"[^.!?\n]*[.!?]?\s*", re.IGNORECASE)
        if pattern.search(text):
            changes.append(f'Removed "{artifact}" sentence')
            text = pattern.sub("", text)
    return text, changes

def strip_markdown(text: str) -> tuple[str, list]:
    changes = []
    if "**" in text:
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        changes.append("Stripped bold")
    if re.search(r'^#{1,6}\s', text, re.MULTILINE):
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        changes.append("Stripped headers")
    if "```" in text:
        text = re.sub(r'```\w*\n?', '', text)
        changes.append("Stripped code blocks")
    return text, changes

def reduce_em_dashes(text: str) -> tuple[str, int]:
    count = text.count("—") + text.count(" -- ")
    text = re.sub(r"\s*—\s*", ", ", text)
    text = re.sub(r"\s+--\s+", ", ", text)
    return text, count

def remove_citations(text: str) -> tuple[str, list]:
    changes = []
    patterns = [
        (r'\[oai_citation:\d+[^\]]*\]\([^)]+\)', "oai_citation"),
        (r':contentReference\[oaicite:\d+\]\{[^}]+\}', "contentReference"),
        (r'turn0search\d+', "turn0search"), (r'turn0image\d+', "turn0image"),
        (r'\?utm_source=(chatgpt\.com|openai)', "ChatGPT UTM"),
    ]
    for pattern, name in patterns:
        if re.search(pattern, text):
            text = re.sub(pattern, '', text)
            changes.append(f"Removed {name}")
    return text, changes

def simplify_ing(text: str) -> tuple[str, list]:
    changes = []
    for word in ["highlighting", "underscoring", "emphasizing", "showcasing", "fostering"]:
        pattern = re.compile(rf',?\s*{word}\s+[^,.]+[,.]', re.IGNORECASE)
        if pattern.search(text):
            text = pattern.sub('. ', text)
            changes.append(f"Simplified {word} clause")
    return text, changes

def clean(text: str) -> str:
    text = re.sub(r" +", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)
    return text.strip()

def transform(text: str, aggressive: bool = False) -> tuple[str, list]:
    all_changes = []
    text, changes = remove_citations(text); all_changes.extend(changes)
    text, changes = strip_markdown(text); all_changes.extend(changes)
    text, changes = remove_chatbot_sentences(text); all_changes.extend(changes)
    text, changes = apply_replacements(text, PATTERNS["copula_avoidance"]); all_changes.extend(changes)
    text, changes = apply_replacements(text, PATTERNS["filler_replacements"]); all_changes.extend(changes)
    text, fixed = fix_quotes(text)
    if fixed:
        all_changes.append("Fixed curly quotes")
    if aggressive:
        text, changes = simplify_ing(text); all_changes.extend(changes)
        text, count = reduce_em_dashes(text)
        if count > 2:
            all_changes.append(f"Replaced {count} em dashes")
    return clean(text), all_changes

def main():
    parser = argparse.ArgumentParser(description="Transform AI text to human-like")
    parser.add_argument("input", nargs="?", help="Input file (or stdin)")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("-a", "--aggressive", action="store_true", help="Aggressive mode")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress change log")
    args = parser.parse_args()
    
    text = Path(args.input).read_text() if args.input else sys.stdin.read()
    result, changes = transform(text, aggressive=args.aggressive)
    
    if not args.quiet and changes:
        print(f"CHANGES ({len(changes)}):", file=sys.stderr)
        for c in changes:
            print(f"  • {c}", file=sys.stderr)
    
    if args.output:
        Path(args.output).write_text(result)
        if not args.quiet:
            print(f"→ {args.output}", file=sys.stderr)
    else:
        print(result)

if __name__ == "__main__":
    main()
