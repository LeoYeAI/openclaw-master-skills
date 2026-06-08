from pathlib import Path


def test_skill_mentions_openclaw_memory_search_baseline():
    repo_root = Path(__file__).resolve().parents[1]
    skill_text = (repo_root / 'SKILL.md').read_text(encoding='utf-8')

    assert 'memory_search' in skill_text
    assert 'OpenClaw 内置 memory_search 已足够' in skill_text
    assert '先跑起来再优化' in skill_text
