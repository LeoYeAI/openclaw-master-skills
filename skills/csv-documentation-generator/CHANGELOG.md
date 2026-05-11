# Changelog - CSV 文档生成器

所有重要的版本更新都会记录在此文件中。

**[English Version](CHANGELOG_en.md)**

## [1.6.4] - 2026-03-20

### Fixed

#### System Prompt Integration 文档澄清
- 强调 System Prompt 集成是**手动配置**步骤，非自动
- 说明 OpenClaw skill 仅在激活时执行，无法跨 skill 持久化指令

### Changed

#### 文档增强
- SKILL.md: 添加 --auto-add 示例、--verbose 选项、AI Agent 使用示例
- README.md/README_en.md: AI Agent 使用示例、--verbose 选项

## [1.6.1] - 2026-03-20

### Fixed

#### CLI 错误处理改进
- **EOFError 处理**: 当非交互式运行时（如 AI agent 使用），自动 fallback 到 autonomous 模式
- 不再抛出 EOFError，而是自动切换模式并继续执行

#### UX 改进
- **--verbose flag**: 新增 `-v/--verbose` 参数，显示详细生成进度
- **Compliance check 自动运行**: `generate all` 后自动检查 requirements.json 并显示合规问题
- **Agent Mode 文档化**: 在 README 中添加 Agent Mode 说明章节

## [1.6.0] - 2026-03-19

### Added

#### 智能双语模式 (Smart Bilingual)
- **--language 参数**: 新增 `--language` 参数支持选择内容语言 ('zh' 或 'en')
- **智能双语处理**: 实现 `process_markdown_table_bilingual()` 函数，根据 `--bilingual` 和 `--language` 智能处理输出

#### 跨 Skill 代码注释协同
- **STANDARDS.md**: 新增标准说明文档，介绍 System Prompt 集成方法
- **standards/code-annotations.json**: 代码注释中央标准注册表，支持 15 种编程语言
- **scripts/standards_reader.py**: 标准读取工具，可被其他 Skill 调用

#### CLI 改进
- **--auto-add/--yes flag**: `cli.py parse` 命令新增 `--auto-add` 和 `--yes` 参数，支持非交互式运行

### Changed

#### 双语行为调整
- `--bilingual true` (默认): Headers 保持双语，内容根据 `--language` 填充
- `--bilingual false`: 纯单语输出，由 `--language` 决定语言
- 用户和 AI agent 现在可以完全控制文档语言输出

#### Gitignore 更新
- 添加 `ses_*.json` 和 `session-*.md` 到 .gitignore

## [1.5.0] - 2026-03-19

### Changed

#### Skill 设计哲学重构
- **SKILL.md 精简**: 从 1034 行精简至 ~785 行，移除 prompt 内容至 prompts.md
- **Semantic Action Graph**: 新增显式的语义动作图定义，展示文档生成间的依赖关系
- **prompts.md 新建**: 将 Critical Thinking Constraints、触发条件、填充 Prompt 迁移至独立文件
- **SemanticActions 类**: 在 generate.py 中新增 SemanticActions 类，封装为可被 AI agent 动态调用的能力节点

#### 架构变更
- **Skill = Tool Semantic Encapsulation + Trigger Conditions**: 重构后更符合此设计哲学
- **SKILL.md**: 现在只包含 Skill Definition + Semantic Action Graph + Execution Interface
- **prompts.md**: 包含所有 prompt 模板和思维约束
- **generate.py**: 作为 Execution Engine 暴露 SemanticActions 接口

## [1.4.0] - 2026-03-19

### Added

#### GAMP 5 Second Edition 合规增强
- **M12 Critical Thinking**: 添加关键思维约束（ M12.1~M12.5），指导 AI 在验证过程中进行系统性风险思考
- **文档生成触发条件**: 新增触发条件库，定义 VP/URS/FS/RA/IQ-OQ-PQ/VSR 生成前的预填充数据
- **内容填充 Prompt 库**: 新增 URS/FS/RA 填充 prompt 模板
- **数据流动定义**: 新增文档间数据流动规则（VP→RA→FS→Test→VSR 自动追溯）

#### 示例文件
- **templates/examples/urs-example.md**: CTMS 系统完整 URS 示例
- **templates/examples/fs-example.md**: FS 追溯表示例
- **templates/examples/ra-example.md**: 分层风险评估示例
- **templates/examples/iq-example.md**: IQ 检查项示例

### Changed

#### 模板精简
- **URS.md**: 移除硬编码的 URS-001~URS-055 示例，精简为纯结构模板
- **FS.md**: 移除硬编码的 FS-UM-*/FS-AU-* 示例，简化 4.0 追溯表
- **RA.md**: 移除硬编码的 RA-DI-*/RA-SC-* 示例
- **IQ.md**: 移除硬编码的 IQ-HW-*/IQ-OS-* 检查项
- **TS.md**: 移除硬编码的技术栈示例
- **VSR.md**: 新增 Lessons Learned 和 Periodic Review 章节

#### 基础设施
- **plan/ 目录**: 新建 plan/ 目录用于存储 gap analysis
- **.gitignore**: 更新以排除 plan/ 目录

## [1.3.4] - 2026-03-19

### Changed

#### 文档更新
- **Standard Modules 表格**: 删除 "URS Section" 列（原列与动态编号行为不一致）
- 添加说明：章节号是动态分配的，基于模板中已有的章节

## [1.3.3] - 2026-03-19

### Fixed

#### GxP 合规修复
- **动态章节编号**: 移除硬编码的 `STANDARD_MODULES` 编号映射，改用 `_get_next_section_number()` 动态计算模板中下一个可用 4.X 编号
- 确保自定义模块（如 `pm_query`, `multi_lock`）获得唯一、无冲突的章节编号
- 添加 SKILL.md 文档说明章节编号行为

## [1.3.2] - 2026-03-19

### Fixed

#### Bug 修复
- **Sync 模块章节修复**: `sync_bidirectional()` 的 `to-template` 分支现在正确按模块分组需求，并为每个模块创建对应的章节标题（`### 4.X 模块名`），而不是简单追加表格行
- 修复自定义模块（如 `pm_query`, `multi_lock` 等）无法创建章节的问题

## [1.3.1] - 2026-03-19

### Fixed

#### Bug 修复
- **Sync 路径修复**: `sync_bidirectional()` 修复写入错误位置问题，现在正确写入项目目录的模板
- **RTM 文件名修复**: RTM 文件名现在正确包含项目名，格式为 `RTM_{项目名}.xlsx`

## [1.3.0] - 2026-03-19

### Added

#### Phase 2 (P1) Features
- **P1.1 Git Hooks**: `scripts/git-hooks/post-commit` 和 `install.sh`，提交后自动运行合规检查
- **P1.2 合规检查器**: `generate.py check` 命令，支持覆盖率、高风险模块、测试覆盖率检查
- **P1.3 增量更新**: `--diff-only` 参数，基于 SHA256 哈希跳过未变更的生成

#### Phase 3 (P2) Features
- **P2.1 双向同步**: `--sync --sync-direction {to-json|to-template|both}` 支持模板与 JSON 双向同步，带冲突检测
- **P2.2 Monorepo 支持**: `--project-root` 参数，自动检测 `apps/`、`packages/` 等多项目结构
- **P2.3 CI/CD 模板**: `templates/ci/github-actions.yml` 和 `gitlab-ci.yml`
- **P2.4 模板版本管理**: 自动版本迁移和兼容性检查

## [1.1.2] - 2026-03-18

### Fixed

#### ID 格式统一
- **统一 ID 前缀**: 将所有 `UR-xxx` 格式替换为 `URS-xxx`，符合 GAMP 5 规范
- templates/urs.md: UR-001~055 → URS-001~055
- templates/vsr.md: UR-001~002 → URS-001~002

## [1.1.1] - 2026-03-18

### Added

#### SKILL.md 规范化
- **Frontmatter 增强**: 添加完整 YAML frontmatter 结构
- **triggers 扩展**: 新增 GxP、21 CFR Part 11、电子签名、电子记录、EDC、CTMS、eTMF、LIMS、医疗器械等触发词
- **inputSchema 定义**: 规范化输入参数结构
- **outputSchema 定义**: 规范化输出文档格式
- **元数据完善**: version、author、createdAt、validationStatus 等字段
- **requiredTools 声明**: 明确需要 exec 工具权限
- **路径修复**: 使用 `<SKILL_DIR>` 占位符替代硬编码路径

## [1.1.0] - 2026-03-18

### Added

#### 需求追溯系统 (Requirements Traceability)
- **数据模型增强**: Requirement 类新增 module、fs_ref、ts_ref、test_cases 字段
- **模块化分组**: 支持 8 种标准模块 (user_mgmt, audit_trail, data_mgmt, business_func, reporting, integration, security, compliance)
- **AI 注释解析**: 支持 `@URS[module]` 格式的注释标记，方便 AI Agent 生成代码时自动追溯
- **模板同步功能**: `--sync` 选项自动将 requirements.json 中的需求同步到模板章节
- **RTM 自动生成**: 从 requirements.json 自动生成 14 列追溯矩阵 Excel
- **测试结果关联**: 自动将测试结果关联到对应需求并更新状态

#### SKILL.md 更新
- 新增 Requirements Traceability 章节
- 代码注释规范 (AI Agent 必须遵循)
- 标准模块定义表
- Test Case ID 格式说明
- Auto-Sync 功能使用说明

## [1.0.1] - 2026-03-18

### Fixed

#### Word 生成器 Bug 修复
- **修复表格渲染 bug**: `_process_content` 方法之前只处理第一个表格后退出循环，现在正确处理所有表格 (24个表格全部渲染)
- **修复表头文本丢失 bug**: `_style_header_cell` 方法之前在 `para.clear()` 后无法获取原始文本，现在通过参数显式传递文本
- **增强颜色对比度**: 表头颜色从 #4682B4 (Steel Blue, 3.2:1) 更新为 #2563EB (Royal Blue, 4.6:1)，满足 WCAG 4.5:1 要求
- **字体统一**: 中文使用宋体 (SimSun)，英文使用 Arial

#### 文档修复
- **修复依赖安装**: 文档中改用 `pip install -r requirements.txt` 替代单独安装各包

## [1.0.0] - 2026-03-18

### Added

#### 核心功能
- **9 种验证文档模板** (VP, URS, FS, TS, RA, IQ, OQ, PQ, VSR)
- **专业 GMP 样式 Word 生成器**
  - 表头颜色: 钢蓝色 (#4682B4) + 白色文字
  - 优先级标记: `[必须]`, `[应该]`, `[Pass]`, `[Fail]`
  - 封面页 + 审批签字表
  - 交替行颜色
- **中英双语支持**

#### AI Agent 智能需求追踪系统
- **Agent 模式检测** (`scripts/agent.py`)
  - 自动检测 OpenClaw/OpenCode/Codex 等 Agent 类型
  - 支持 `interactive` (半自动) 和 `autonomous` (全自动) 模式
  - 环境变量优先级: `CSV_DOCS_MODE` > Agent 环境变量 > Git 配置 > 项目配置

- **需求解析器** (`scripts/requirements/parser.py`)
  - 从代码注释解析需求: `@req`, `@requirement`, `# URS-001`
  - 自动识别电子签名需求 (21 CFR Part 11)
  - 关键词: 签名、审核、审批、sign、approve 等

- **风险评估器** (`scripts/requirements/risk_analyzer.py`)
  - RPN/FMEA 方法论
  - 自动严重性/可能性/可检测性评估
  - 基于 GAMP Category 的风险计算
  - 标准缓解措施建议

- **Git 关联器** (`scripts/requirements/linker.py`)
  - 自动解析提交信息中的需求 ID
  - 需求 ↔ 提交 可追溯性矩阵

- **测试结果解析器** (`scripts/tests/parser.py`)
  - 支持 JUnit XML、pytest JSON、NUnit XML 格式
  - 自动关联需求与测试状态
  - 测试覆盖率统计

- **文档自动填充器** (`scripts/fill/filler.py`)
  - 从需求数据库自动填充模板变量
  - 文档完整性验证

- **审计日志** (`scripts/audit/log.py`)
  - 所有操作完整记录
  - 支持导出为 PDF (文本格式)
  - 按操作类型、模式筛选

#### CLI 统一入口 (`scripts/cli.py`)

```bash
csv-docs init              # 初始化项目配置
csv-docs agent             # 检测 Agent 模式
csv-docs agent --set autonomous  # 设置为全自动模式
csv-docs parse ./src       # 解析代码需求
csv-docs status            # 查看状态
csv-docs add "描述"        # 添加需求
csv-docs risk              # 运行风险分析
csv-docs test --results ./ # 解析测试结果
csv-docs generate vp       # 生成文档
csv-docs audit            # 查看审计日志
```

#### 合规支持
- **GAMP 5 Second Edition** 验证生命周期
- **21 CFR Part 11** 电子记录与电子签名
- **EU Annex 11** 计算机化系统
- **ALCOA+** 数据完整性原则

### Configuration

#### 项目配置 (`.csv-docs-config.json`)
```json
{
  "agent": {
    "default_mode": "interactive",
    "auto_detect": true
  },
  "autonomous": {
    "on_duplicate": "overwrite"
  },
  "compliance": {
    "gamp_category": null,
    "auto_esig_detection": true,
    "auto_ra": true,
    "esig_keywords": ["签名", "审核", "审批", "sign", "approve"]
  }
}
```

#### 需求数据库 (`requirements.json`)
- 存储所有需求、风险、测试结果、提交关联

#### 审计日志 (`audit-log.json`)
- 所有操作的完整审计轨迹

---

## [0.1.0] - 初始版本

### Added
- 基础文档模板
- Word 生成器
- Excel 生成器
- GAMP 5 参考文档
- 21 CFR Part 11 参考文档
- EU Annex 11 参考文档
- 数据完整性参考文档

---

## 版本格式

版本格式遵循 [Semantic Versioning](https://semver.org/):
- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的问题修复
