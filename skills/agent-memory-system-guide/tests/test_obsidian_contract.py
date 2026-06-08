from pathlib import Path


def test_skill_mentions_obsidian_primitives_and_query_fields():
    repo_root = Path(__file__).resolve().parents[1]
    skill_text = (repo_root / 'SKILL.md').read_text(encoding='utf-8')

    for token in ['frontmatter', 'Dataview', 'wikilink', 'backlinks', 'embeds', 'attachments']:
        assert token in skill_text

    # Dataview should be able to query these frontmatter fields.
    for field in ['type', 'status', 'tags', 'related']:
        assert field in skill_text

