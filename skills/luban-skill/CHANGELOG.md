# Changelog

所有 notable 变化都将记录在此文件。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added
- 新增 `type suggest` 命令，根据字段名智能推荐类型
- 新增 `type validate` 命令，验证类型字符串有效性
- 新增 `type search` 命令，搜索枚举和 Bean 类型
- 新增 `type guide` 命令，提供类型使用指南
- 完善类型系统文档

## [3.8.0] - 2024-03-24

### Added
- 增强 `type` 命令，支持子命令（info, list, validate, suggest, search, guide）
- 添加智能类型推断功能，支持上下文感知
- 添加字段名模式匹配（30+ 种常见模式）

### Fixed
- 修复 `row list/get` 返回空结果的问题
- 修复 `table list` 无法扫描子目录的问题
- 修复 Windows 下的中文编码问题
- 修复 `add_table` 无法创建子目录的问题

## [3.7.0] - 2024-03-23

### Added
- 支持自动导入表格式（`#*.xlsx`）
- 添加 `auto` 命令管理自动导入表
- 添加 `field disable/enable` 命令
- 添加 `multirow` 命令支持多行结构

### Changed
- 优化 Excel 文件解析逻辑
- 改进数据行插入算法（智能排序）

## [3.6.0] - 2024-03-22

### Added
- 添加 `batch` 命令支持批量操作
- 添加 `export/import` 命令
- 添加 `validate` 命令验证表数据
- 添加 `ref` 命令检查引用完整性

### Fixed
- 修复枚举/Bean 定义解析问题

## [3.5.0] - 2024-03-21

### Added
- 添加 `template` 命令支持配置模板
- 添加 `rename/copy` 命令管理表
- 添加 `diff` 命令对比表差异
- 添加 `tag/variant` 命令

## [3.0.0] - 2024-03-20

### Added
- 初始版本发布
- 支持枚举、Bean、表的增删改查
- 支持字段操作（添加、修改、删除）
- 支持数据行操作
- 支持缓存管理

[Unreleased]: https://github.com/luban-tools/luban_skill/compare/v3.8.0...HEAD
[3.8.0]: https://github.com/luban-tools/luban_skill/compare/v3.7.0...v3.8.0
[3.7.0]: https://github.com/luban-tools/luban_skill/compare/v3.6.0...v3.7.0
[3.6.0]: https://github.com/luban-tools/luban_skill/compare/v3.5.0...v3.6.0
[3.5.0]: https://github.com/luban-tools/luban_skill/compare/v3.0.0...v3.5.0
[3.0.0]: https://github.com/luban-tools/luban_skill/releases/tag/v3.0.0
