from pathlib import Path


def test_skill_documents_local_first_positioning_and_optional_backends():
    repo_root = Path(__file__).resolve().parents[1]
    skill_text = (repo_root / 'SKILL.md').read_text(encoding='utf-8')

    assert '本地优先的文件工作流和恢复约定' in skill_text
    assert '不是托管式 memory platform' in skill_text
    assert '核心架构（本地优先分层）' in skill_text
    assert '### 第一层：恢复层（`SESSION-STATE.md`）' in skill_text
    assert '### 第二层：毛坯层（`working-buffer.md`）' in skill_text
    assert '### 第三层：长期记忆层（`MEMORY.md`）' in skill_text
    assert '### 第五层：归档与可选召回层' in skill_text
    assert '### 可选召回后端' in skill_text
    assert '`memory_search` 是默认优先的轻量召回入口' in skill_text
