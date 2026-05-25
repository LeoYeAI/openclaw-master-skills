# Digital Life Import - 数据源导入器

这个目录包含从不同来源导入用户数字生活数据的实现指南。

## 核心概念

**Digital Life Import** 是 OpenClaw Diary 的核心功能，目标是：
- 自动接入用户的数字生活数据源
- 统一导入为 AI Memory
- 建立完整的用户档案

## 支持的数据源

### 第一优先级（推荐）

| 数据源 | 文件 | 说明 |
|--------|------|------|
| OpenClaw Memory | 本地读取 | 无需 MCP，直接读取 `~/.claude/projects/*/memory/` |
| Obsidian | mcp-obsidian | 本地 Vault，隐私安全 |
| GitHub | 原生支持 | 代码仓库、README、Issues |

### 第二优先级（需要授权）

| 数据源 | MCP 服务器 | 说明 |
|--------|-----------|------|
| Notion | notion-mcp | 官方 MCP 支持 |
| Gmail | google-workspace-mcp | Google OAuth |
| Google Docs | google-workspace-mcp | Google OAuth |
| Google Drive | google-workspace-mcp | Google OAuth |
| 飞书 | feishu-mcp | App ID + Secret |

### 第三优先级（可选）

| 数据源 | MCP 服务器 | 说明 |
|--------|-----------|------|
| Slack | slack-mcp | Bot Token |
| Dropbox | dbx-mcp-server | OAuth |
| X/Twitter | twitter-mcp | API Key |
| RSS | mcp-rss-aggregator | 无需授权 |

## 文件说明

- `digital_life_import.md` - 完整的导入指南和 MCP 配置说明
- `feishu_importer.md` - 飞书文档导入详细实现
- `README.md` - 本文件

## 导入流程

```
1. detectSources()     # 自动检测可用数据源
2. 用户选择要导入的来源
3. 收集授权信息（智能合并）
4. importSource(source) # 统一导入接口
5. Memory Pipeline     # 数据转换
6. 生成用户档案
```

## Memory Root

所有导入的数据保存到：

```
~/write_me/01studio/me/
├── identity/          # 用户身份
├── auth/              # 授权配置
├── imports/           # 导入的原始数据
└── memory/            # 结构化记忆
```

## 命令行接口

```bash
/import-data              # 显示导入向导
/import-data github       # 只导入 GitHub
/import-data --all        # 导入所有已配置的数据源
/import-data --refresh    # 刷新已导入的数据
```

## 开发指南

### 添加新的数据源

1. 确认是否有可用的 MCP 服务器
2. 在 `importSource()` 中添加新的导入函数
3. 更新 `detectSources()` 检测逻辑
4. 添加授权收集逻辑
5. 更新文档

### 统一导入接口

```python
async def importSource(source):
    """统一导入接口"""
    importers = {
        "openclaw_memory": importOpenClawMemory,
        "obsidian": importObsidian,
        "notion": importNotion,
        # ... 其他导入器
    }
    return await importers[source]()
```

### Memory Pipeline

```
source data → markdown → memory chunk → memory graph
```

所有数据经过统一的 Pipeline 处理，确保格式一致。

---

最后更新：2026-03-15
