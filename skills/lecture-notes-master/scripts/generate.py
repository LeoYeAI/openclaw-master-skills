#!/usr/bin/env python3
"""
Lecture Notes Master - Note Generation Engine
Generates Obsidian-compatible markdown notes from templates.

Usage:
    # Main lecture note with N concepts (not limited to 3)
    python3 generate.py --type lecture --title "Memory Optimization" \
        --concepts "Shared Memory,Bank Conflicts,Tiling,Coalescing" \
        --output "/path/to/00-Inbox/Topic/"

    # Atomic note (any layer: L1, L2, L3)
    python3 generate.py --type atomic --concept "Shared Memory" \
        --parent "GPU-Computing-Lecture-07-Notes" \
        --children "Shared-Memory-vs-Global,Synchronization" \
        --siblings "Bank-Conflicts,Tiling" \
        --output "/path/to/00-Inbox/Topic/"

    # Glossary entry
    python3 generate.py --type glossary \
        --term-en "Shared Memory" --term-cn "共享内存" \
        --definition "Fast on-chip memory shared among threads in a block" \
        --output "/path/to/00-Inbox/Topic/glossary/"

    # Course MOC
    python3 generate.py --type moc --course "GPU Computing" --semester "2025ws"
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(SCRIPT_DIR, "..", "templates")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "..", "config.json")


def load_config():
    """Load user configuration from config.json."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_default_output():
    """Get default output path from config or fallback."""
    config = load_config()
    vault = config.get("obsidian", {}).get("vault_path", "")
    inbox = config.get("obsidian", {}).get("inbox_dir", "00-Inbox/")
    if vault:
        return os.path.join(vault, inbox)
    return os.path.expanduser("~/00-Inbox/")


def load_template(template_name):
    """Load a template file."""
    filepath = os.path.join(TEMPLATE_DIR, f"{template_name}.md")
    if not os.path.exists(filepath):
        print(f"Error: Template not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def _to_link(name):
    """Convert a concept/note name to wiki-link target (matches filename without .md)."""
    return name.strip().replace(" ", "-")


def apply_replacements(template, replacements):
    """Apply replacements and fill remaining placeholders with TODO markers."""
    result = template
    for key, value in replacements.items():
        result = result.replace(key, value)
    result = re.sub(r"\{\{([^}]+)\}\}", r"TODO: \1", result)
    return result


def generate_lecture_note(title, concepts=None, date=None, course="", source=""):
    """Generate a main lecture note scaffold with N concepts (not limited to 3)."""
    template = load_template("lecture-note")
    today = date or datetime.now().strftime("%Y-%m-%d")

    concepts = concepts or ["Concept 1", "Concept 2", "Concept 3"]
    concept_links = [_to_link(c) for c in concepts]

    # Build dynamic sections for N concepts
    sections = []
    for i, concept in enumerate(concepts, 1):
        link = concept_links[i - 1]
        section = f"""## {i}. {concept}

→ 详见 [[{link}]]

### TODO: Sub-sections

TODO: Content with Mermaid diagrams, tables, key insights

### Key Takeaway（关键要点）

> TODO: {concept} takeaway

---
"""
        sections.append(section)

    # Build related notes
    related = "\n".join(f"- [[{link}]]" for link in concept_links)

    replacements = {
        "{{TITLE}}": title,
        "{{TITLE_CN}}": "",
        "{{DATE}}": today,
        "{{COURSE_OR_TOPIC}}": course or title,
        "{{TAG_1}}": title.lower().replace(" ", "-")[:30],
        "{{TAG_2}}": concepts[0].lower().replace(" ", "-") if concepts else "topic",
        "{{TAG_3}}": "lecture-notes",
        "{{SOURCE_1}}": source or "TODO: source",
        "{{ALIAS_1}}": "",
        "{{ALIAS_2}}": "",
        "{{ONE_SENTENCE_SUMMARY_WITH_INLINE_WIKILINKS_TO_GLOSSARY_TERMS}}": f"TODO: Core idea of {title}",
        "{{SOURCE_LINKS}}": source or "TODO: source links",
    }

    result = apply_replacements(template, replacements)

    # Replace the template section placeholders with dynamic sections
    # Find the first section marker and replace everything until Summary
    section_pattern = r"## 1\..*?(?=## Summary)"
    combined_sections = "\n".join(sections)
    result = re.sub(section_pattern, combined_sections, result, flags=re.DOTALL)

    # Replace related notes
    result = re.sub(
        r"- \[\[.*?L1_ATOMIC_NOTE.*?\]\].*$",
        related,
        result,
        flags=re.MULTILINE | re.DOTALL,
    )

    return result


def generate_atomic_note(
    concept_name,
    date=None,
    parent="",
    children=None,
    siblings=None,
):
    """Generate a rich atomic concept note scaffold (works for L1, L2, L3).

    Args:
        concept_name: Name of the concept.
        date: Optional date string.
        parent: File stem of the parent note (for wiki-link).
        children: List of child concept names (for wiki-links).
        siblings: List of sibling concept names (for wiki-links).
    """
    template = load_template("atomic-note")
    today = date or datetime.now().strftime("%Y-%m-%d")

    children = children or []
    siblings = siblings or []

    # Build child links
    child_links = "\n".join(
        f"- [[{_to_link(c)}]]" for c in children if c.strip()
    )
    if not child_links:
        child_links = "- (none — terminal layer)"

    # Build sibling links
    sibling_links = "\n".join(
        f"- [[{_to_link(s)}]]"
        for s in siblings
        if s.strip() and s.strip() != concept_name.strip()
    )
    if not sibling_links:
        sibling_links = "- (none)"

    replacements = {
        "{{CONCEPT_NAME}}": concept_name,
        "{{CONCEPT_NAME_CN}}": "",
        "{{DATE}}": today,
        "{{TAG_1}}": concept_name.lower().replace(" ", "-")[:30],
        "{{TAG_2}}": "atomic-note",
        "{{TAG_3}}": "",
        "{{ALIAS_CN}}": "",
        "{{ALIAS_EN_VARIANT}}": "",
        "{{ONE_PARAGRAPH_DEFINITION_WITH_INLINE_WIKILINKS_TO_GLOSSARY_TERMS}}": f"TODO: Definition of {concept_name}",
        "{{LANGUAGE_OR_OMIT}}": "",
        "{{CONCEPT}}": concept_name,
        "{{PARENT_NOTE}}": parent or "TODO: Parent-Note",
    }

    result = apply_replacements(template, replacements)

    # Replace child and sibling placeholders
    result = re.sub(
        r"- \[\[.*?CHILD_NOTE.*?\]\]\n?- \[\[.*?CHILD_NOTE.*?\]\]",
        child_links,
        result,
    )
    result = re.sub(
        r"- \[\[.*?SIBLING_NOTE.*?\]\]\n?- \[\[.*?SIBLING_NOTE.*?\]\]",
        sibling_links,
        result,
    )

    # Clean up empty wiki-links [[]] or [[TODO: ...]]
    result = re.sub(r"- \[\[\]\]\n?", "", result)

    return result


def generate_glossary_entry(term_en, term_cn="", definition="", date=None, topic_tag=""):
    """Generate a glossary entry scaffold."""
    template = load_template("glossary-entry")
    today = date or datetime.now().strftime("%Y-%m-%d")

    replacements = {
        "{{ENGLISH_TERM}}": term_en,
        "{{CHINESE_TERM}}": term_cn or "TODO: 中文术语",
        "{{DATE}}": today,
        "{{TOPIC_TAG}}": topic_tag or "topic",
        "{{ABBREVIATION_IF_ANY}}": "",
        "{{BILINGUAL_DEFINITION_1_TO_3_SENTENCES — concise, precise, with inline wikilinks to related terms}}": definition
        or f"TODO: Definition of {term_en}",
    }

    return apply_replacements(template, replacements)


def generate_moc(course, semester, date=None):
    """Generate a course MOC scaffold."""
    template = load_template("course-moc")
    today = date or datetime.now().strftime("%Y-%m-%d")

    replacements = {
        "{{COURSE}}": course,
        "{{COURSE_TAG}}": course.lower().replace(" ", "-"),
        "{{SEMESTER}}": semester,
        "{{STATUS}}": "In Progress",
    }

    return apply_replacements(template, replacements)


def write_file(content, filepath):
    """Write content to file, creating directories if needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] Created: {filepath}")


def main():
    default_output = get_default_output()

    parser = argparse.ArgumentParser(
        description="Lecture Notes Master - Note Generation Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate main lecture note with N concepts
  python3 generate.py --type lecture --title "Memory Optimization" \\
      --concepts "Shared Memory,Bank Conflicts,Tiling,Coalescing"

  # Generate atomic note with cross-references
  python3 generate.py --type atomic --concept "Shared Memory" \\
      --parent "GPU-Lecture-07-Notes" \\
      --children "SM-vs-Global,SM-Sync" --siblings "Bank-Conflicts,Tiling"

  # Generate glossary entry
  python3 generate.py --type glossary --term-en "Shared Memory" \\
      --term-cn "共享内存" --definition "Fast on-chip memory in GPU"

  # Generate course MOC
  python3 generate.py --type moc --course "GPU Computing" --semester "2025ws"
        """,
    )
    parser.add_argument(
        "--type",
        choices=["lecture", "atomic", "glossary", "moc"],
        default="lecture",
        help="Type of note to generate",
    )
    parser.add_argument("--title", help="Lecture/topic title (for lecture type)")
    parser.add_argument("--concepts", help="Comma-separated list of L1 concept names")
    parser.add_argument("--concept", help="Single concept name (for atomic type)")
    parser.add_argument("--parent", default="", help="Parent note file stem (for atomic)")
    parser.add_argument("--children", default="", help="Comma-separated child names (for atomic)")
    parser.add_argument("--siblings", default="", help="Comma-separated sibling names (for atomic)")
    parser.add_argument("--term-en", default="", help="English term (for glossary)")
    parser.add_argument("--term-cn", default="", help="Chinese term (for glossary)")
    parser.add_argument("--definition", default="", help="Term definition (for glossary)")
    parser.add_argument("--course", help="Course name (for moc)")
    parser.add_argument("--semester", default="", help="Semester (e.g., 2025ws)")
    parser.add_argument("--source", default="", help="Source URL")
    parser.add_argument("--date", help="Date (YYYY-MM-DD, default: today)")
    parser.add_argument(
        "--output",
        default=default_output,
        help="Output directory (default: from config.json)",
    )

    args = parser.parse_args()
    output_dir = os.path.expanduser(args.output)

    print(f"\n  Lecture Notes Master - Generator")
    print(f"  Output: {output_dir}\n")

    if args.type == "lecture":
        if not args.title:
            parser.error("--title required for lecture type")

        concepts = [c.strip() for c in args.concepts.split(",")] if args.concepts else None

        content = generate_lecture_note(
            args.title, concepts, args.date, args.course or "", args.source
        )
        filename = f"{args.title.replace(' ', '-')}-Notes.md"
        write_file(content, os.path.join(output_dir, filename))

        # Generate atomic note scaffolds for each concept
        if concepts:
            for concept in concepts:
                atomic_content = generate_atomic_note(
                    concept,
                    args.date,
                    parent=args.title.replace(" ", "-") + "-Notes",
                    siblings=concepts,
                )
                atomic_filename = f"{concept.replace(' ', '-')}.md"
                write_file(atomic_content, os.path.join(output_dir, atomic_filename))

        file_count = 1 + (len(concepts) if concepts else 0)
        print(f"\n  Generated {file_count} files")

    elif args.type == "atomic":
        if not args.concept:
            parser.error("--concept required for atomic type")

        children = [c.strip() for c in args.children.split(",")] if args.children else []
        siblings = [c.strip() for c in args.siblings.split(",")] if args.siblings else []

        content = generate_atomic_note(
            args.concept, args.date, args.parent, children, siblings
        )
        filename = f"{args.concept.replace(' ', '-')}.md"
        write_file(content, os.path.join(output_dir, filename))

        print(f"\n  Generated 1 file")

    elif args.type == "glossary":
        if not args.term_en:
            parser.error("--term-en required for glossary type")

        content = generate_glossary_entry(
            args.term_en, args.term_cn, args.definition, args.date
        )
        # Glossary filename includes both English and Chinese
        if args.term_cn:
            filename = f"{args.term_en}（{args.term_cn}）.md"
        else:
            filename = f"{args.term_en}.md"
        write_file(content, os.path.join(output_dir, filename))

        print(f"\n  Generated 1 file")

    elif args.type == "moc":
        if not args.course:
            parser.error("--course required for moc type")

        content = generate_moc(args.course, args.semester, args.date)
        filename = f"{args.course.replace(' ', '-')}-MOC.md"
        write_file(content, os.path.join(output_dir, filename))

        print(f"\n  Generated 1 file")

    print("  Done!\n")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
