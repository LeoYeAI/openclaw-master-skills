# luban_skill

一个强大的 Claude Code Skill，用于高效操作 Luban 游戏配置表。

## 功能特性

- **枚举操作**：增删改查枚举定义
- **Bean 操作**：管理复杂数据结构
- **表操作**：创建、修改、删除配置表
- **字段操作**：动态添加、修改、禁用字段
- **数据行操作**：查询、添加、更新、删除数据
- **类型系统**：智能类型推断和验证
- **批量操作**：支持批量导入导出
- **引用检查**：检查类型引用完整性

## 安装

### 前置条件

1. Python 3.8+
2. openpyxl: `pip install openpyxl`

### 安装 Skill

将本技能目录复制到你的 `.claude/skills/` 目录下：

```bash
cp -r luban_skill ~/.claude/skills/
```

## 快速开始

```bash
# 列出所有表
python scripts/luban_helper.py table list --data-dir DataTables/Datas

# 查看表结构
python scripts/luban_helper.py table get TbItem --data-dir DataTables/Datas

# 查询数据
python scripts/luban_helper.py row get TbItem --field id --value 1001 --data-dir DataTables/Datas
```

## 核心命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `enum list/get/add/delete` | 枚举操作 | `enum get test.EQuality` |
| `bean list/get/add/delete` | Bean 操作 | `bean get test.RewardItem` |
| `table list/get/add/delete` | 表操作 | `table get TbItem` |
| `field list/add/update/delete` | 字段操作 | `field add TbItem desc --type string` |
| `row list/get/query/add/update/delete` | 数据行操作 | `row get TbItem --field id --value 1` |
| `type list/validate/suggest/search/guide` | 类型系统 | `type suggest drops --context monster` |

## 类型系统

Skill 提供强大的类型系统支持：

```bash
# 列出所有可用类型
python scripts/luban_helper.py type list --data-dir DataTables/Datas

# 验证类型
python scripts/luban_helper.py type validate "list<int>" --data-dir DataTables/Datas

# 获取字段类型建议
python scripts/luban_helper.py type suggest quality --context item --data-dir DataTables/Datas

# 搜索类型
python scripts/luban_helper.py type search Quality --data-dir DataTables/Datas

# 查看类型指南
python scripts/luban_helper.py type guide --topic container --data-dir DataTables/Datas
```

## 支持的类型

### 基本类型
`bool`, `byte`, `short`, `int`, `long`, `float`, `double`, `string`, `text`, `datetime`

### 容器类型
- `array<T>` - 定长数组
- `list<T>` - 变长列表
- `set<T>` - 集合
- `map<K,V>` - 键值对映射

### 可空类型
在类型后加 `?`：`int?`, `string?`, `MyBean?`

## 文档

- [SKILL.md](SKILL.md) - 完整使用文档
- [references/commands.md](references/commands.md) - 命令详细参考
- [references/REFERENCE.md](references/REFERENCE.md) - 需求设计文档

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

[MIT License](LICENSE)
