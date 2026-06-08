from pathlib import Path
import re


def test_skill_uses_canonical_openclaw_name():
    repo_root = Path(__file__).resolve().parents[1]
    skill_text = (repo_root / 'SKILL.md').read_text(encoding='utf-8')

    assert 'name: memory-system' in skill_text
    assert 'Use when' in skill_text


def test_manifest_exists_for_publish_workflows():
    repo_root = Path(__file__).resolve().parents[1]
    manifest_text = (repo_root / 'manifest.toml').read_text(encoding='utf-8')

    for token in [
        'name = "Agent Memory System Guide"',
        'slug = "agent-memory-system-guide"',
        'skill_id = "14ff5aad-4df3-4b33-ba0b-6cc217cdb939"',
        '[openclaw]',
        '[clawhub]',
    ]:
        assert token in manifest_text


def test_release_entrypoints_match_manifest_version():
    repo_root = Path(__file__).resolve().parents[1]
    manifest_text = (repo_root / 'manifest.toml').read_text(encoding='utf-8')
    match = re.search(r'^version = "([^"]+)"$', manifest_text, re.MULTILINE)

    assert match is not None
    version = match.group(1)

    assert f'version = "{version}"' in manifest_text

    for path in ['README.md', 'README_CN.md', 'README_EN.md', 'INSTALL.md']:
        text = (repo_root / path).read_text(encoding='utf-8')
        assert f'`{version}`' in text
