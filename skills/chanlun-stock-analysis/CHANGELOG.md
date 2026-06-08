# Changelog

所有版本的变更记录。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

---

## [1.1.0] - 2026-03-26

### 新增
- 新增 `README.md`，包含完整的功能说明、安装方法、使用示例和版本历史
- 新增 `CHANGELOG.md` 版本变更记录
- 新增 `assets/` 目录说明

### 变更
- **重构 SKILL.md 文档结构**，符合 ClawHub 发布规范：
  - 新增标准 `metadata.openclaw` frontmatter 字段（emoji、os、requires）
  - 新增 `使用场景` 章节（✅ Use when / ❌ NOT for）
  - 新增 `快速开始` 章节
  - 新增 `配置选项` 表格
  - 新增 `错误处理` 章节
  - 新增 `安全注意` 章节（含风险提示和隐私保护说明）
  - 新增 `相关文件` 章节（明确列出所有 references 文件用途）
  - 新增 `依赖说明` 章节（说明外部技能和 Python 依赖）
  - description 字段按 ClawHub 规范添加 `Use when` 和 `NOT for` 标注

---

## [1.0.0] - 2026-03-01

### 新增
- 初始版本发布
- 支持缠论技术分析（中枢、笔、背驰、买卖点）
- 支持14维度多指标共振评分系统
- 支持基本面分析（盈利/成长/健康度）
- 支持多维估值分析（PE/PB/EV/DCF/PEG）
- 自动生成专业排版 PDF 报告
- 支持 A 股沪深主板、创业板、科创板，以及港股、美股
