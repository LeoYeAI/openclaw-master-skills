# Changelog

## [1.0.3] - 2026-03-26

### Changed
- 移除 baoyu-danger-gemini-web 作为备选生图引擎的引导
- 统一使用 KIE API (kay-image) 作为唯一生图方案
- 简化生图引擎对比表，移除 Gemini 相关选项
- 更新所有代码示例，移除 Gemini 方式的备选示例
- 简化配置检查清单

## [1.0.2] - 2026-03-25

### Changed
- 更新依赖：从 kie-image 迁移到 kay-image
- 添加明确的 metadata 依赖声明（skills: kay-image, env: KIE_API_KEY）
- 更新文档中所有 kie-image 引用为 kay-image
- 优化 SKILL.md frontmatter，添加 requires 配置

## [1.0.1] - 2026-03-25

### Added
- 添加前置要求章节，强制要求先安装 kie-image skill
- 添加 kie-image 安装和配置详细步骤
- 添加 API Key 获取指引（https://kie.ai/）
- 添加安装验证测试命令

### Changed
- 将前置要求移到文档最顶部，确保用户先看到
- 使用 ⚠️ 警告标识强调必须先安装 kie-image

## [1.0.0] - 2026-03-XX

### Features
- 小红书全自动内容创作工作流
- 爆款研究：分析热门笔记风格、构图、文案
- AI 生图：支持 KIE 和 Gemini 双引擎
- 自动发布：保存到小红书草稿箱
- 完整 pipeline：从研究到发布的端到端解决方案
