# Changelog

All notable changes to this project will be documented in this file.

## [v6.0.0] - 2026-03-24

### Added
- ✅ 五层记忆架构（L1 工作记忆 → L2 情景记忆 → L3 语义记忆 → L4 知识宫殿 → L5 元认知层）
- ✅ memory_watcher.py — OpenClaw 记忆文件监听（watchdog，跨平台）
- ✅ fact_store.py — L2/L3 统一事实存储层
- ✅ distill_engine.py — L2→L3 LLM 驱动提炼引擎
- ✅ palace_index.py — 记忆宫殿空间索引
- ✅ pyramid_engine.py — 金字塔知识组织（实例→规则→模式→本体）
- ✅ palace_classifier.py — 宫殿分类调度器（延迟防抖机制）
- ✅ decay_function.py — Ebbinghaus 记忆衰减函数
- ✅ health/ — 健康系统 5 模块（manager/hygiene/correction/evolution/abstraction）
- ✅ LLM 智能处理：质量评估 / 去重 / 分类，多模型配置
- ✅ 集成测试 37/37 通过

### Fixed
- ✅ FB-007: cognitive_profile.py `profile['exp']` KeyError
- ✅ FB-008: Anima 与 OpenClaw 记忆写入打通（memory_watcher）
- ✅ memory_sync.py 路径硬编码（workspace-shuheng → 自动检测）
- ✅ anima_tools.py FACTS_BASE 默认值改为 /home/画像

### Changed
- ✅ 工程整理：合并 anima-core + anima-skill → anima-aios
- ✅ 清理 20+ 个过时文档
- ✅ SKILL.md 重写，只描述已实现功能

---

## [v5.0.6] - 2026-03-22

### Fixed
- ✅ 五维认知画像维度分配 Bug（creation/metacognition/collaboration 始终为 0）
- ✅ semantic 记忆正确归到 creation 维度
- ✅ 每日任务按类型分配维度

## [v5.0.5] - 2026-03-22

### Fixed
- ✅ Doctor 硬编码 workspace 路径
- ✅ 自动 workspace 检测
- ✅ 集成 OpenClaw 身份检测

## [v5.0.4] - 2026-03-22

### Added
- ✅ OpenClaw 身份体系集成（SOUL.md/IDENTITY.md 解析）
- ✅ Doctor 记忆同步工具
- ✅ 7 层身份检测降级机制

## [v5.0.3] - 2026-03-22

### Fixed
- ✅ 3 层同步机制 Bug（记忆只写第 1 层）
- ✅ EXP 计算错误（C 级质量得 0 EXP）

## [v5.0.2] - 2026-03-21

### Added
- ✅ 三层记忆同步机制
- ✅ Doctor 记忆同步检查

## [v5.0.1] - 2026-03-21

### Added
- ✅ Doctor 自检自修工具

## [v5.0.0] - 2026-03-21

### Added
- ✅ 品牌升级：Memora → Anima-AIOS
- ✅ 游戏化成长系统（EXP + 等级 + 每日任务 + 团队排行）
- ✅ 五维认知画像
- ✅ 9 个核心工具
