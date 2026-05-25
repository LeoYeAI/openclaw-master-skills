# Onboarding Skill - 设计文档

## 概述

这个 skill 负责引导用户完成日记系统的初始化设置。

## 核心特性

### 1. 智能授权合并

**问题**：如果用户从飞书导入用户档案，又选择写入飞书日记，传统做法会要求用户授权两次。

**解决方案**：
- 在阶段 2（用户身份建立）时，如果用户选择导入，提前询问阶段 3（存储配置）的选择
- 计算所有需要的授权平台（去重）
- 一次性收集所有授权信息
- 避免重复授权

**示例场景**：

| 用户档案导入 | 日记存储 | 需要授权 | 说明 |
|---------|---------|---------|------|
| 飞书 | 飞书 | 飞书（1次） | 合并授权 |
| 飞书 | 本地 | 飞书（1次） | 只需导入授权 |
| 本地文件 | 飞书 | 飞书（1次） | 只需存储授权 |
| Notion | 飞书 | Notion + 飞书（2次） | 不同平台 |
| 聊天建立 | 飞书 | 飞书（1次） | 只需存储授权 |

### 2. 用户身份建立的两种方式

**方式 A：聊天建立**
- AI 问几个问题
- 用户回答
- 生成用户档案

**方式 B：导入建立**
- 用户已有描述自己的文档
- 支持多种来源：
  - 飞书文档（个人简介、年度总结等）
  - 本地文件（Markdown、文本）
  - Notion 页面（关于我、个人页面）
  - 网页链接（个人网站、博客、LinkedIn）
- AI 自动提取和结构化信息
- 生成用户档案

**目的**：让 AI 更了解用户，提供个性化的日记记录服务。

### 3. 渐进式引导

不是一次性问完所有问题，而是分阶段引导：

1. **阶段 1**：人设选择（必选）
2. **阶段 2**：用户身份建立（可选：聊天 / 导入）
3. **阶段 3**：存储配置（必选）
4. **阶段 4**：生成配置（自动）
5. **阶段 5**：完成设置（自动）

每个阶段都可以跳过（除了必选项），降低用户负担。

### 4. 多平台支持

**用户档案导入来源**：
- 飞书文档
- 本地文件（Markdown/文本）
- Notion 页面
- 网页链接（个人网站、博客、LinkedIn）

**日记存储平台**：
- 本地文件系统（必选）
- 飞书云文档（可选同步）
- Flomo（可选同步）
- Notion（可选同步）

**设计原则**：
- 本地存储是基础，云端同步是增强
- 支持多来源导入用户档案（可多选）
- 支持多平台日记同步（可多选）

## 实现流程

### 授权合并实现

```python
# 伪代码
def onboarding_flow():
    # 阶段 1：人设选择
    personality = ask_personality()

    # 阶段 2：用户身份
    identity_method = ask_identity_method()  # 聊天 / 导入 / 跳过

    if identity_method == "import":
        import_sources = ask_import_sources()  # 飞书、本地、Notion、网页

        # 提前询问存储配置（关键步骤）
        storage_config = ask_storage_config()

        # 计算需要的授权（合并）
        needed_auth = set()
        for source in import_sources:
            if source in ["feishu", "notion"]:
                needed_auth.add(source)
        if storage_config.sync_enabled:
            needed_auth.add(storage_config.sync_platform)

        # 一次性收集所有授权
        auth_info = {}
        for platform in needed_auth:
            auth_info[platform] = collect_auth(platform)

        # 执行导入（使用已收集的授权）
        user_identity = import_identity(import_sources, auth_info)

    elif identity_method == "chat":
        user_identity = chat_build_identity()
        storage_config = ask_storage_config()
        auth_info = collect_storage_auth(storage_config)

    else:  # skip
        user_identity = None
        storage_config = ask_storage_config()
        auth_info = collect_storage_auth(storage_config)

    # 阶段 3：存储配置（使用已收集的授权）
    configure_storage(storage_config, auth_info)

    # 阶段 4：生成配置
    generate_config(personality, user_identity, storage_config, auth_info)

    # 阶段 5：完成
    show_summary()
```

### 配置文件生成

最终生成的配置文件结构：

```json
{
  "storage": {
    "type": "local",
    "path": "~/write_me/00inbox/journal",
    "feishu": {
      "enabled": true,
      "folder_token": "fldcnXXXXXXXXXXXXXXXXXXXXXXX"
    },
    "flomo": {
      "enabled": false,
      "api_key": ""
    },
    "notion": {
      "enabled": false,
      "database_id": ""
    }
  },
  "personality": {
    "type": "intj",
    "file": "personalities/intj.md"
  },
  "user_identity": {
    "enabled": true,
    "path": "~/write_me/01studio/me",
    "files": {
      "identity": "identity.md",
      "preferences": "preferences.md",
      "social_accounts": "social-accounts.md"
    }
  },
  "date_format": "YYYY-MM",
  "time_boundary": "06:00",
  "triggers": {
    "explicit": ["记一下", "记录", "写日记", "journal"],
    "implicit": ["今天发生了", "刚才", "我在想"]
  },
  "tags": ["主动记录", "陪读", "协作"],
  "post_processing": {
    "enabled": true,
    "skills": []
  }
}
```

## 用户体验设计

### 最小化配置

**默认值**：
- 人设：INTJ（推荐）
- 用户身份：跳过
- 数据导入：跳过
- 存储：仅本地
- 路径：`~/write_me/00inbox/journal`

**最快路径**：
1. 选择人设 → INTJ
2. 跳过用户身份
3. 跳过数据导入
4. 选择仅本地存储
5. 使用默认路径
6. 完成

总共只需要 3 次选择，约 30 秒完成。

### 进度提示

在每个阶段显示进度：

```
[1/5] 人设选择
[2/5] 用户身份建立（可选）
[3/5] 数据导入（可选）
[4/5] 存储配置
[5/5] 生成配置
```

### 错误恢复

**配置文件已存在**：
- 提供选项：重新配置 / 保留现有 / 查看现有
- 不强制覆盖

**授权失败**：
- 提供详细的错误信息
- 允许重新输入
- 提供获取授权的帮助链接

**目录创建失败**：
- 检查权限
- 建议手动创建或选择其他路径
- 提供具体的命令示例

## 技术实现

### 使用的工具

1. **AskUserQuestion**：收集用户选择
2. **Read**：检查现有配置
3. **Write**：创建配置文件和用户身份文件
4. **Bash**：创建目录、设置环境变量
5. **MCP 工具**：
   - `mcp__feishu__*`：飞书集成
   - 未来：Flomo、Notion MCP 工具

### 路径处理

```bash
# 展开 ~ 为完整路径
HOME=$(echo $HOME)
CONFIG_PATH="$HOME/.openclaw/workspace/diary/config"
STORAGE_PATH="$HOME/write_me/00inbox/journal"
IDENTITY_PATH="$HOME/write_me/01studio/me"

# 创建目录
mkdir -p "$CONFIG_PATH"
mkdir -p "$STORAGE_PATH"
mkdir -p "$IDENTITY_PATH"
```

### 环境变量设置

```bash
# 检测 shell 类型
SHELL_TYPE=$(basename $SHELL)

# 确定配置文件
if [ "$SHELL_TYPE" = "zsh" ]; then
    RC_FILE="$HOME/.zshrc"
elif [ "$SHELL_TYPE" = "bash" ]; then
    RC_FILE="$HOME/.bashrc"
fi

# 添加环境变量
echo 'export FEISHU_APP_ID="xxx"' >> "$RC_FILE"
echo 'export FEISHU_APP_SECRET="xxx"' >> "$RC_FILE"

# 重新加载
source "$RC_FILE"
```

## 测试场景

### 场景 1：最小配置
- 人设：INTJ
- 用户身份：跳过
- 存储：仅本地
- 预期：快速完成，生成最小配置

### 场景 2：聊天建立档案
- 人设：ENFP
- 用户身份：聊天建立
- 存储：本地 + 飞书同步
- 预期：AI 问几个问题，生成用户档案，配置飞书同步

### 场景 3：导入建立档案（智能合并授权）
- 人设：INTJ
- 用户身份：从飞书导入
- 存储：本地 + 飞书同步
- 预期：合并飞书授权，只授权一次，从飞书文档提取用户信息

### 场景 4：多来源导入
- 用户身份：从飞书 + 本地文件 + 网页导入
- 存储：本地 + Notion 同步
- 预期：收集飞书和 Notion 授权（2次），从多个来源提取信息并合并

### 场景 4：配置冲突
- 已存在配置文件
- 预期：提供选项，不强制覆盖

## 未来扩展

### 1. 导入器插件系统

在 `importers/` 目录下添加平台特定的导入脚本：

```
onboarding/
├── SKILL.md
├── README.md
└── importers/
    ├── feishu.py
    ├── flomo.py
    └── notion.py
```

每个导入器实现标准接口：
```python
def import_data(auth_info, output_dir):
    # 从平台获取数据
    # 转换为标准格式
    # 写入 output_dir
    pass
```

### 2. 配置验证

添加配置验证功能：
- 检查授权是否有效
- 测试网络连接
- 验证路径权限
- 提供诊断报告

### 3. 配置迁移

支持从旧版本配置迁移：
- 检测旧配置格式
- 自动转换为新格式
- 保留用户数据

### 4. 可视化配置编辑器

提供 Web UI 或 TUI 来编辑配置：
- 更直观的界面
- 实时验证
- 配置预览

## 协作者

- **Yitong**：阶段 1（人设选择）、阶段 3（数据导入）、阶段 4（存储配置）
- **DK**：阶段 2（用户身份建立）
- **共同**：授权合并逻辑、配置文件生成

---

最后更新：2026-03-14
