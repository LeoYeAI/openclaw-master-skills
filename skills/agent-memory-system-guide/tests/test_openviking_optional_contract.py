from pathlib import Path


def test_skill_marks_openviking_as_optional():
    repo_root = Path(__file__).resolve().parents[1]
    skill_text = (repo_root / 'SKILL.md').read_text(encoding='utf-8')
    assert 'OpenViking 可选增强' in skill_text
    assert 'OpenViking 不是强依赖' in skill_text
    assert 'OpenViking-compatible optional enhancement' in skill_text
