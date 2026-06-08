from pathlib import Path


def test_skill_mentions_memory_capture_flow():
    repo_root = Path(__file__).resolve().parents[1]
    skill_text = (repo_root / 'SKILL.md').read_text(encoding='utf-8')

    assert '任务结束 30 秒记录流程' in skill_text
    assert '候选记忆' in skill_text
    assert 'memory-capture.md' in skill_text
    assert '导出备份' in skill_text
    assert '导入恢复' in skill_text
    assert '导入前备份' in skill_text
    assert '--clean' in skill_text
    assert 'clean restore' in skill_text


def test_memory_capture_template_exists():
    repo_root = Path(__file__).resolve().parents[1]
    template_text = (repo_root / 'templates' / 'memory-capture.md').read_text(encoding='utf-8')

    assert '候选决策' in template_text
    assert '候选踩坑' in template_text
    assert '候选长期记忆' in template_text


def test_readmes_document_cross_device_backup_restore():
    repo_root = Path(__file__).resolve().parents[1]
    readme_text = (repo_root / 'README.md').read_text(encoding='utf-8')
    readme_cn_text = (repo_root / 'README_CN.md').read_text(encoding='utf-8')
    readme_en_text = (repo_root / 'README_EN.md').read_text(encoding='utf-8')

    assert 'export' in readme_text
    assert 'import' in readme_text
    assert '--clean' in readme_text
    assert '新设备' in readme_cn_text
    assert '导入前备份' in readme_cn_text
    assert '--clean' in readme_cn_text
    assert '保守' in readme_cn_text
    assert 'new device' in readme_en_text
    assert 'pre-import backup' in readme_en_text
    assert '--clean' in readme_en_text
    assert 'conservative' in readme_en_text
    assert 'overwrite-style restore' in readme_en_text


def test_skill_declares_working_buffer_as_only_short_term_scratchpad():
    repo_root = Path(__file__).resolve().parents[1]
    skill_text = (repo_root / 'SKILL.md').read_text(encoding='utf-8')

    assert '`working-buffer.md` 是唯一的短期毛坯区' in skill_text
    assert '其他 skill 如果也有 working buffer 概念，应复用这个文件' in skill_text
    assert '不要再创建第二份并行写入的 WAL / buffer 文件' in skill_text


def test_readmes_document_memory_layers_and_lookup_order():
    repo_root = Path(__file__).resolve().parents[1]
    readme_paths = ['README.md', 'README_CN.md', 'README_EN.md']

    for path in readme_paths:
        text = (repo_root / path).read_text(encoding='utf-8')
        assert 'MEMORY.md' in text
        assert 'memory/' in text

    readme_cn_text = (repo_root / 'README_CN.md').read_text(encoding='utf-8')
    assert '`MEMORY.md` 用于启动时快速参考' in readme_cn_text
    assert '`memory/` 用于每日笔记和深度归档' in readme_cn_text
    assert '检索顺序' in readme_cn_text


def test_readme_documents_memory_workflow_examples():
    repo_root = Path(__file__).resolve().parents[1]
    readme_text = (repo_root / 'README.md').read_text(encoding='utf-8')

    assert 'First-time workspace bootstrap' in readme_text
    assert 'End-of-task memory capture' in readme_text
    assert 'Distill a daily note into `MEMORY.md`' in readme_text
    assert '### Workflow examples' in readme_text
    assert '### Report examples' in readme_text
    assert 'Maintenance report command' in readme_text
    assert 'python3 scripts/memory_capture.py report' in readme_text
    assert 'Memory workspace report for /path/to/workspace' in readme_text
    assert 'Missing supported file: SESSION-STATE.md' in readme_text
    assert 'python3 scripts/memory_capture.py report --workspace /path/to/workspace --output /path/to/workspace-report.md' in readme_text
    assert '# Memory workspace report' in readme_text
    assert '## Supported files' in readme_text
    assert '## Obsidian setup guide' in readme_text
    assert 'attachments/' in readme_text
    assert 'Calendar' in readme_text
    assert 'Templater' in readme_text
    assert 'crontab' in readme_text
    assert '0 9 * * *' in readme_text
    assert '## Sync options and trade-offs' in readme_text
    assert 'Obsidian Sync' in readme_text
    assert 'Syncthing' in readme_text
    assert 'iCloud' in readme_text
    assert 'git' in readme_text


def test_bilingual_readmes_cover_examples_and_report():
    repo_root = Path(__file__).resolve().parents[1]
    readme_cn_text = (repo_root / 'README_CN.md').read_text(encoding='utf-8')
    readme_en_text = (repo_root / 'README_EN.md').read_text(encoding='utf-8')

    assert '首次引导' in readme_cn_text
    assert '任务结束记忆捕获' in readme_cn_text
    assert '每日笔记蒸馏' in readme_cn_text
    assert '### 工作流示例' in readme_cn_text
    assert '### 报告示例' in readme_cn_text
    assert '维护报告' in readme_cn_text
    assert 'Memory workspace report for /path/to/workspace' in readme_cn_text
    assert 'Missing supported file: SESSION-STATE.md' in readme_cn_text
    assert 'workspace-report.md' in readme_cn_text
    assert '# Memory workspace report' in readme_cn_text
    assert '## Obsidian 配置指南' in readme_cn_text
    assert 'Calendar' in readme_cn_text
    assert 'Templater' in readme_cn_text
    assert 'crontab' in readme_cn_text
    assert '## 同步方案与取舍' in readme_cn_text
    assert 'Obsidian Sync' in readme_cn_text
    assert 'Syncthing' in readme_cn_text
    assert 'iCloud' in readme_cn_text

    assert 'first-time workspace bootstrap' in readme_en_text
    assert 'end-of-task memory capture' in readme_en_text
    assert 'daily note distillation' in readme_en_text
    assert '### Workflow examples' in readme_en_text
    assert '### Report examples' in readme_en_text
    assert 'maintenance report command' in readme_en_text
    assert 'Memory workspace report for /path/to/workspace' in readme_en_text
    assert 'Missing supported file: SESSION-STATE.md' in readme_en_text
    assert 'workspace-report.md' in readme_en_text
    assert '# Memory workspace report' in readme_en_text
    assert '## Obsidian setup guide' in readme_en_text
    assert 'crontab' in readme_en_text
    assert '## Sync options and trade-offs' in readme_en_text
    assert 'Obsidian Sync' in readme_en_text
    assert 'Syncthing' in readme_en_text


def test_skill_mentions_obsidian_setup_and_scheduled_maintenance():
    repo_root = Path(__file__).resolve().parents[1]
    skill_text = (repo_root / 'SKILL.md').read_text(encoding='utf-8')

    assert 'Obsidian 配置' in skill_text
    assert 'attachments/' in skill_text
    assert 'Dataview' in skill_text
    assert 'crontab' in skill_text
    assert '不要自动写入 `MEMORY.md`' in skill_text
    assert '同步取舍' in skill_text
    assert 'Obsidian Sync' in skill_text
    assert 'Syncthing' in skill_text


def test_skill_mentions_report_command():
    repo_root = Path(__file__).resolve().parents[1]
    skill_text = (repo_root / 'SKILL.md').read_text(encoding='utf-8')

    assert 'report command' in skill_text
    assert 'supported files' in skill_text
    assert 'python3 scripts/memory_capture.py report' in skill_text
