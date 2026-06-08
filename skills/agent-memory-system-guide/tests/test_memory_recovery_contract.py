from pathlib import Path


def test_skill_mentions_recovery_templates():
    repo_root = Path(__file__).resolve().parents[1]
    skill_text = (repo_root / 'SKILL.md').read_text(encoding='utf-8')
    assert 'SESSION-STATE.md' in skill_text
    assert 'working-buffer.md' in skill_text
    assert 'templates/OBSIDIAN-NOTE.md' in skill_text
    assert 'frontmatter' in skill_text
    assert 'Dataview' in skill_text
    assert '启动时' in skill_text
    assert '结束时' in skill_text
    assert '恢复' in skill_text


def test_session_state_template_uses_compact_recovery_format():
    repo_root = Path(__file__).resolve().parents[1]
    template_text = (repo_root / 'templates' / 'SESSION-STATE.md').read_text(encoding='utf-8')

    for section in ['## 当前任务', '## 已完成', '## 卡点', '## 下一步', '## 恢复信息']:
        assert section in template_text

    for forbidden in ['## Task', '## Status', '## Owner', '## Last Updated', '## Cleanup Rule']:
        assert forbidden not in template_text


def test_skill_declares_session_state_as_single_compact_contract():
    repo_root = Path(__file__).resolve().parents[1]
    skill_text = (repo_root / 'SKILL.md').read_text(encoding='utf-8')

    assert '`SESSION-STATE.md` 只使用仓库模板提供的简洁结构' in skill_text
    assert '不要写入 `Task`、`Status`、`Owner`、`Last Updated`、`Cleanup Rule`' in skill_text
    assert '`Current Task` 合并到 `当前任务`' in skill_text
    assert '`Status` 合并到 `已完成`、`卡点` 或 `下一步`' in skill_text
