# Changelog

All notable changes to gorm-expert-skill are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.6.0] - 2026-03-15

### Added
- `base_model.go` 新增 `Config` 全局配置系统：
  - 多租户开关（`TenantEnabled`/`TenantField`/`TenantExtractor`/`TenantStrict`）
  - 可配置查询限制（`MaxListSize`/`MaxListAllSize`/`MaxInSize`/`MaxPageSize`）
  - `SetConfig()` / `GetConfig()` 全局配置函数
- `base_model.go` `GetTxDB` 自动注入多租户条件，所有 CRUD 方法自动隔离
- `analyze_gorm.py` R27: `references:` tag 未加 `constraint:false` 检测（ERROR）

### Changed
- SKILL.md 核心原则 #1 改为「禁止物理外键，必须使用逻辑外键」
- SKILL.md §1 新增多租户 Config 配置示例，§6 多租户改为 Config 驱动
- SKILL.md §7 补充 `references:` tag 的逻辑外键规范
- `base_model.go` 所有硬编码限制常量改为读取 `globalConfig`
- `example_order_model.go` 多租户改为 Config 驱动（移除手动 injectTenant）
- `init_project.py` 后续步骤新增多租户 Config 配置示例
- `references/base-model-pattern.md` §8 重写为 Config 开关式多租户文档

---

## [1.5.1] - 2026-03-15

### Added
- `base_model.go` Page/PageAfter 参数自动校验（page≤0→1, pageSize 范围 [1,1000]）
- `base_model.go` IN 子句大小限制 `maxInSize=1000`（DeleteByIds/ListByIds 超限报错）
- `base_model.go` List 方法新增 `maxListSize=5000` 软上限保护
- `query_builder.go` 新增 `NotLike` 方法（NOT LIKE '%value%'）
- `analyze_gorm.py` R26: 大 IN 子句检测（WARN）
- `references/base-model-pattern.md` 新增 §10–§13 文档（参数校验、IN 限制、List 保护、NotLike）

### Changed
- SKILL.md 按 Claude Code Skill 最新规范重构：
  - 移除非标准 frontmatter 字段（`version`、`compatibility`）
  - `description` 精简至 4 行（含触发词）
  - 合并 §0/§1 为统一的「初始化与连接池」章节
  - 压缩重复代码示例，583 → 440 行（规范要求 ≤500）
  - §14 参考表去除冗余 `references/` 前缀，精简触发时机列

---

## [1.5.0] - 2026-03-15

### Added
- `assets/dbcore/auto_id.go` 重写为可插拔 ID 生成器架构：
  - `IDGenerator` 接口 + `SetIDGenerator()` 全局切换
  - `NewSnowflakeGenerator` — 内置雪花算法（无需外部依赖 bwmarrin/snowflake），含时钟回拨保护（≤5s 等待，>5s panic）
  - `NewLeafSegmentGenerator` — 美团 Leaf 号段模式（双 Buffer 异步预加载，严格递增）
  - `NewUUIDGenerator` — UUID v4（零依赖）
  - `autoFillID` 支持 string / int64 / uint64 类型 ID 字段
  - `WithIDGenerator` / `IDGeneratorFromContext` 支持 context 级别策略切换
- `references/id-generation.md` — 分布式 ID 策略完整指南：
  - Snowflake vs Leaf-Segment vs UUID 选型对比表
  - 时钟回拨原因、保护机制、chrony 配置建议
  - K8s nodeID 管理（StatefulSet / Redis INCR / 环境变量注入）
  - Leaf 号段表建表 SQL、step 调优、高可用与容灾
  - UUID 性能问题（B-Tree 页分裂实测数据）与优化方案（BINARY(16) / UUID v7）
  - 自定义 ID 生成器示例（Redis 自增、ULID）
  - 从 AUTO_INCREMENT 迁移到分布式 ID 的步骤
- `references/soft-delete.md` — 软删除完整指南（唯一约束兼容、时间戳模式、归档清理）
- SKILL.md §2.4 投影到自定义 struct（Scan/ScanRows 流式读取）
- SKILL.md §2.5 Group/Having/Distinct/SubQuery 用法
- SKILL.md §3.3 RowsAffected 检查模式
- SKILL.md §9 新增反模式：Save 全量更新、忽略 RowsAffected
- `analyze_gorm.py` 新增 5 条规则：
  - R22: Where 字符串拼接（SQL 注入）
  - R23: 未检查 RowsAffected（INFO）
  - R24: Save 全量更新警告（INFO）
  - R25: AutoMigrate 在业务代码中调用（WARN）
- `analyze_gorm.py --format json` CI 集成输出格式

### Fixed
- `gen_model.py:294` — TableName 方法接收者语法错误（多余的右括号）
- `query_builder.go` OrGroup 缺少外层括号，导致 AND/OR 优先级错误
  - 修改前: `name = ? AND (status = ?) OR (status = ?)` — 逻辑错误
  - 修改后: `name = ? AND ((status = ?) OR (status = ?))` — 正确
- `analyze_gorm.py` docstring 规则范围标注修正（R1–R18 → R1–R26）

### Security
- `query_builder.go` 所有字段名参数增加 `safeField()` 校验，防止 SQL 注入
- `base_model.go` Order.Field 增加正则校验，只允许 `[a-zA-Z0-9_.]`

---

## [1.4.0] - 2026-03-15

### Changed
- SKILL.md slimmed from 805 → ~500 lines; detailed content moved to references/
- description shortened to 12 lines; removed imperative trigger language
- Section subsection numbers corrected (13.x was mislabeled as 14.x)
- Replaced 必须/强制 phrasing in references with softer 建议/应该/需

### Added
- `assets/dbcore/auto_id.go` — snowflake ID implementation for BaseModel
- `references/README.md` — indexed guide to all 15 reference documents
- `CHANGELOG.md` — this file

### Fixed
- `analyze_gorm.py` R18a/R18b labels were both named "R18"; now clearly distinguished
- `assets/dbcore/example_order_model.go` — added `//go:build ignore` and fixed import placeholder
- `references/migration.md` — added safety warnings before raw DDL CLI commands

### Security
- `SKILL.md` frontmatter now declares `compatibility` block (runtime, binaries, no_credentials, disk_access)
- Script table annotated with 🔍 read-only / 📝 write-on-explicit-flag permissions

---

## [1.3.1] - 2026-03-15

### Security (ClawHub audit fix)
- Added `compatibility` block to SKILL.md frontmatter declaring python >= 3.8, no credentials
- Annotated `disk_access.read_only` (6 scripts) vs `write_on_explicit_flag` (2 scripts)
- Added security docstrings to `bench_template.py` and `init_project.py`
- Script table now shows 🔍/📝 permission icons

---

## [1.3.0] - 2026-03-15

### Added — GORM v2 Specific Features
- `references/session.md` — Session mechanism, goroutine safety, 8 common traps
- `references/clause.md` — Clause system (FOR UPDATE / SKIP LOCKED / Upsert / RETURNING / custom)
- `references/association.md` — Association ops (Preload/Joins/Append/Replace/Select+Omit)
- `references/serializer.md` — Serializer (json/gob/unixtime) and custom data types
- `references/raw-sql.md` — First/Take/Find behavior diff table, v2 error handling

### Added — analyze_gorm.py
- R19: goroutine unsafe *gorm.DB sharing (WARN)
- R20: *gorm.DB condition accumulation without Session (INFO)
- R21: v1 gorm.IsRecordNotFoundError usage (ERROR)

### Fixed
- R19–R21 were dead code (placed after `return issues`); now correctly inside function

---

## [1.2.1] - 2026-03-15

### Added
- `assets/dbcore/example_order_model.go` — complete OrderModel demo
- `scripts/init_project.py --example` flag to generate the demo file

---

## [1.2.0] - 2026-03-15

### Added
- `scripts/init_project.py` — scaffold dbcore package into target project
- `assets/dbcore/` — base_model.go, query_builder.go, transaction.go (production-ready, bug-fixed)
- SKILL.md section 0 "Project Init"

---

## [1.1.1] - 2026-03-15

### Added
- `references/base-model-pattern.md` — BaseModel design rules and bug fixes (312 lines)

### Fixed
- `query_builder.go` InStrings/InInts args ordering bug
- `order.go` soft-delete + unique index conflict
- `base_model.go` Find→Take, ListAll soft limit, Page dedup, PageAfter cursor pagination

---

## [1.1.0] - 2026-03-15

### Added
- SKILL.md sections: Scopes/multi-tenant, Cache-Aside integration
- `scripts/scope_gen.py` — auto-generate Scope functions
- `scripts/gen_model.py --dialect pg` — PostgreSQL type support
- `scripts/pool_advisor.py` — health check code output
- `references/scopes.md`, `references/caching.md`
- analyze_gorm.py refactored to dual-loop architecture

---

## [1.0.2] - 2026-03-15

### Added
- SKILL.md sections: Sharding, Observability
- analyze_gorm.py R11–R18 rules
- `references/sharding.md`, `references/observability.md`

---

## [1.0.1] - 2026-03-15

### Fixed
- description: removed 必须触发/不得跳过 language to pass ClawHub security scan

---

## [1.0.0] - 2026-03-15

### Added
- Initial release: SKILL.md with 9 sections, 6 scripts, 6 reference docs
