---
name: onboarding
description: |
  OpenClaw Diary 日记系统安装向导。引导用户完成日记系统的初始化设置，包括人设选择、用户身份建立、存储配置和授权管理。

  **立即触发当**：用户说「setup my journal」「初始化日记」「配置日记系统」「journal setup」「开始设置日记」。
  **主动触发当**：用户首次尝试使用 diary skill 但配置文件不存在时，主动提示「看起来你还没有初始化日记系统，要现在设置吗？」

  完成 5 个阶段的设置：人设选择、用户身份建立（可选）、存储配置、授权收集、生成配置文件。

  **核心特性**：
  - 智能授权合并：如果导入和存储使用相同平台（如飞书），只需授权一次
  - 渐进式引导：5 个阶段，可选步骤可跳过
  - 人设一致性：INTJ/ENFP 风格贯穿全程
  - 纯文本交互：完全适配 Telegram/WhatsApp/Discord 等消息平台

metadata:
  clawdbot:
    requires:
      env: []  # 环境变量可选，用户可以稍后配置
    files: []
    homepage: "https://github.com/openclaw-community/diary-system"
---

# Onboarding Skill - 日记系统安装向导

## 核心原则

**交互方式**：
- ✅ 使用纯文本对话，不依赖任何结构化交互工具
- ✅ 提供清晰的编号选项（1, 2, 3...）
- ✅ 支持多种输入方式（数字、关键词、自然语言）
- ✅ 每次选择后立即确认并进入下一步
- ✅ 显示进度提示（阶段 X/5）
- ✅ 允许跳过可选步骤

**人设一致性**：
- 根据用户选择的人设（INTJ/ENFP）调整对话风格
- INTJ：简洁、直接、高效，少废话
- ENFP：温暖、详细、鼓励，多关心

**智能授权合并**：
- 提前收集所有需要授权的场景
- 计算去重后的授权列表
- 一次性收集所有授权信息

---

## 前置检查

### 步骤 1：检查依赖的 skills 是否已安装

**检查 diary 和 note-extractor skills**：

使用 Bash 工具检查：
```bash
ls -la ~/.openclaw/skills/diary 2>&1 && ls -la ~/.openclaw/skills/note-extractor 2>&1
```

**如果任一 skill 不存在**：

发送提示：
```
OpenClaw Diary 需要安装以下 skills：
- openclaw-diary-core（日记记录）
- openclaw-diary-insights（洞察提取）

正在为你安装...
```

然后使用 Bash 工具安装：
```bash
# 检查是否安装了 clawhub CLI
if ! command -v clawhub &> /dev/null; then
    echo "正在安装 ClawHub CLI..."
    npm install -g clawhub
fi

# 安装依赖的 skills
clawhub install openclaw-diary-core
clawhub install openclaw-diary-insights
```

安装完成后发送：
```
✓ 依赖 skills 安装完成！

现在开始配置你的日记系统。
```

### 步骤 2：检查配置文件是否已存在

1. 展开 `~` 为完整路径：使用 `echo $HOME` 获取主目录
2. 检查文件：`~/.openclaw/workspace/diary/config/diary-config.json`
3. 如果文件已存在：
   ```
   看起来你已经初始化过日记系统了。

   要重新配置吗？这会覆盖现有配置。

   回复「是」继续，或「否」取消。
   ```

4. 如果用户回复「否」或「取消」，结束 skill

---

## 阶段 1：欢迎和人设选择

### 1.1 欢迎用户

发送欢迎消息：

```
欢迎使用 OpenClaw Diary！

这个系统可以：
✓ 智能记录你的想法、文章讨论和协作任务
✓ 支持本地存储和多平台同步（飞书/Flomo/Notion）
✓ 提供两种 AI 人设风格

整个设置大约需要 2-3 分钟，分为 5 个步骤。

【阶段 1/5】选择 AI 人设
```

### 1.2 人设选择

发送选项：

```
请选择你希望的 AI 日记助手风格：

1. **INTJ - 分析型**（推荐）
   话少、精准、善于发现规律
   适合：喜欢简洁高效沟通的人
   特点：会帮你识别行为模式，提供战略性思考

2. **ENFP - 温暖型**
   话多、温暖、陪伴感强
   适合：喜欢情感支持和深度交流的人
   特点：会主动关心你的感受，提供情感陪伴

💡 回复数字（1 或 2）或名称（INTJ/ENFP）即可。
```

### 1.3 解析用户输入

等待用户回复，解析输入：

**识别规则**：
- 包含 "1" 或 "intj" 或 "分析" → 选择 INTJ
- 包含 "2" 或 "enfp" 或 "温暖" → 选择 ENFP
- 其他 → 提示未识别

**未识别时的提示**：
```
没听清，请重新选择：

回复 1 选择 INTJ（分析型）
回复 2 选择 ENFP（温暖型）
```

### 1.4 确认选择

记录选择：`personality_type = "intj"` 或 `"enfp"`

根据人设发送确认消息：

**INTJ 风格**：
```
✓ 已选择 INTJ - 分析型

接下来的对话我会保持简洁高效。
```

**ENFP 风格**：
```
✓ 已选择 ENFP - 温暖型

太好了！接下来我会用温暖的方式陪伴你完成设置 😊
```

---

## 阶段 2：用户身份建立（可选）

### 2.1 询问是否建立用户身份

根据人设发送消息：

**INTJ 风格**：
```
【阶段 2/5】用户身份建立（可选）

建立用户档案可以让 AI 更了解你的背景和目标。

选择方式：
1. 聊天建立 - 我问几个问题了解你
2. 导入建立 - 从文档导入你的信息
3. 跳过 - 直接进入下一步

回复数字即可。
```

**ENFP 风格**：
```
【阶段 2/5】用户身份建立（可选）

如果你愿意，我想更了解你一些 😊

这样我就能更好地理解你的想法，提供更贴心的陪伴。

你可以选择：
1. 聊天建立 - 我们聊几句，我来了解你
2. 导入建立 - 如果你有现成的个人介绍文档，可以直接导入
3. 跳过 - 也可以先跳过，以后再补充

你想怎么做呢？回复数字就好。
```

### 2.2 解析用户选择

**识别规则**：
- 包含 "1" 或 "聊天" → 进入 2.3 聊天建立
- 包含 "2" 或 "导入" → 进入 2.4 导入建立
- 包含 "3" 或 "跳过" → 跳到阶段 3
- 其他 → 提示未识别

### 2.3 聊天建立用户身份

**INTJ 风格**（简洁提问）：
```
✓ 选择聊天建立

我会问 3 个问题，简短回答即可。

问题 1/3：你的职业或主要身份是什么？
（例如：软件工程师、产品经理、学生、创业者）
```

等待回复，记录答案。

```
问题 2/3：你目前关注的主要领域或目标是什么？
（例如：AI 技术、个人成长、投资理财）
```

等待回复，记录答案。

```
问题 3/3：你希望通过日记系统达成什么？
（例如：记录想法、复盘反思、知识管理）
```

等待回复，记录答案。

**ENFP 风格**（温暖提问）：
```
✓ 太好了！我们来聊聊吧 😊

我会问你 3 个问题，帮助我更了解你。放轻松，随便聊就好。

问题 1/3：你平时主要做什么工作或学习呢？
（比如你是做技术的、做产品的、还是在创业？）
```

等待回复，记录答案。

```
问题 2/3：最近你在关注什么领域或想达成什么目标？
（可以是技术学习、个人成长、投资理财，或者其他任何你在意的事）
```

等待回复，记录答案。

```
问题 3/3：你希望这个日记系统帮你做什么呢？
（比如记录灵感、复盘反思、整理知识，或者只是想有个地方倾诉）
```

等待回复，记录答案。

**生成用户档案**：

根据用户的回答，生成 `identity.md` 文件：

```markdown
# 用户身份档案

**生成时间**：{当前日期}

## 基本信息

- **职业/身份**：{用户回答1}
- **关注领域**：{用户回答2}
- **使用目标**：{用户回答3}

## 档案来源

通过聊天建立，基于用户的自我描述。

---

此档案由 OpenClaw Diary onboarding skill 自动生成。
```

保存到：`~/write_me/01studio/me/identity.md`

确认消息：
```
✓ 用户档案已创建

保存位置：~/write_me/01studio/me/identity.md
```

然后进入阶段 3。

### 2.4 导入建立用户身份

**询问导入来源**：

```
✓ 选择导入建立

请选择要导入的数据源（可多选）：

1. 📄 飞书文档 - 导入飞书云文档中的个人档案
2. 📝 Notion - 导入 Notion 中的个人页面
3. 💾 本地文件 - 上传本地的 Markdown/Word 文档
4. 🌐 网页链接 - 提供在线文档链接

💡 输入方式：
- 单选：回复数字（如 1）
- 多选：用逗号分隔（如 1,3 或 飞书,本地）
- 全选：回复 all 或 全部

回复你的选择：
```

**解析用户输入**：

识别规则：
- "1" 或 "飞书" → 添加 feishu
- "2" 或 "notion" → 添加 notion
- "3" 或 "本地" → 添加 local
- "4" 或 "网页" 或 "链接" → 添加 web
- "all" 或 "全部" → 添加所有

支持组合：
- "1,3" → [feishu, local]
- "飞书,notion" → [feishu, notion]

**记录选择**：`import_sources = ["feishu", "local", ...]`

**确认选择**：
```
✓ 已选择：{列出选择的数据源}

稍后会在授权阶段收集相关信息。
```

然后进入阶段 3。

### 2.5 跳过用户身份建立

如果用户选择跳过：

```
✓ 已跳过用户身份建立

你可以随时通过编辑 ~/write_me/01studio/me/identity.md 来添加用户档案。
```

然后进入阶段 3。

---

## 阶段 3：存储配置

### 3.1 询问存储方式

根据人设发送消息：

**INTJ 风格**：
```
【阶段 3/5】存储配置

日记保存位置：

1. 仅本地 - 保存到 ~/write_me/00inbox/journal/
2. 本地 + 飞书同步
3. 本地 + Notion 同步
4. 本地 + Flomo 同步

回复数字即可。
```

**ENFP 风格**：
```
【阶段 3/5】存储配置

你的日记想保存在哪里呢？

1. 仅本地 - 保存在你的电脑上，最私密安全
2. 本地 + 飞书同步 - 本地保存，同时同步到飞书云文档
3. 本地 + Notion 同步 - 本地保存，同时同步到 Notion
4. 本地 + Flomo 同步 - 本地保存，同时同步到 Flomo

💡 所有选项都会在本地保存一份，云端同步只是额外备份。

回复数字就好：
```

### 3.2 解析用户选择

**识别规则**：
- "1" 或 "本地" 或 "local" → storage_type = "local_only"
- "2" 或 "飞书" 或 "feishu" → storage_type = "local_feishu"
- "3" 或 "notion" → storage_type = "local_notion"
- "4" 或 "flomo" → storage_type = "local_flomo"
- 其他 → 提示未识别

### 3.3 确认选择

根据选择发送确认消息：

**仅本地**：
```
✓ 已选择：仅本地存储

日记将保存到：~/write_me/00inbox/journal/
```

**本地 + 飞书**：
```
✓ 已选择：本地 + 飞书同步

日记将保存到：
- 本地：~/write_me/00inbox/journal/
- 飞书：需要在下一步提供授权信息
```

记录：`sync_platform = "feishu"`

**本地 + Notion**：
```
✓ 已选择：本地 + Notion 同步

日记将保存到：
- 本地：~/write_me/00inbox/journal/
- Notion：需要在下一步提供授权信息
```

记录：`sync_platform = "notion"`

**本地 + Flomo**：
```
✓ 已选择：本地 + Flomo 同步

日记将保存到：
- 本地：~/write_me/00inbox/journal/
- Flomo：需要在下一步提供授权信息
```

记录：`sync_platform = "flomo"`

---

## 阶段 4：智能授权合并

### 4.1 计算需要的授权

根据前面的选择，计算需要授权的平台：

```python
needed_auth = set()

# 从阶段 2 的导入来源
if "feishu" in import_sources:
    needed_auth.add("feishu")
if "notion" in import_sources:
    needed_auth.add("notion")

# 从阶段 3 的存储配置
if sync_platform == "feishu":
    needed_auth.add("feishu")
elif sync_platform == "notion":
    needed_auth.add("notion")
elif sync_platform == "flomo":
    needed_auth.add("flomo")

# 转换为列表
auth_list = list(needed_auth)
```

### 4.2 如果不需要授权

如果 `auth_list` 为空（用户选择了仅本地存储，且没有导入）：

```
【阶段 4/5】授权配置

✓ 无需授权

你选择的配置不需要任何外部平台授权。
```

直接进入阶段 5。

### 4.3 如果需要授权

根据人设发送消息：

**INTJ 风格**：
```
【阶段 4/5】授权配置

需要以下授权：
{列出 auth_list 中的平台}

你可以：
1. 现在配置 - 我会引导你获取授权信息
2. 稍后配置 - 先生成配置文件，之后手动编辑

回复数字即可。
```

**ENFP 风格**：
```
【阶段 4/5】授权配置

为了让日记系统正常工作，我们需要一些授权信息：
{列出 auth_list 中的平台}

别担心，这些信息都保存在你的本地，不会上传到任何地方 🔒

你想：
1. 现在配置 - 我来帮你一步步获取授权信息
2. 稍后配置 - 先完成设置，之后你自己手动填写

回复数字就好：
```

### 4.4 解析用户选择

**识别规则**：
- "1" 或 "现在" → 进入 4.5 收集授权
- "2" 或 "稍后" → 跳到阶段 5
- 其他 → 提示未识别

### 4.5 收集授权信息

对于 `auth_list` 中的每个平台，逐个收集授权信息。

#### 4.5.1 飞书授权

```
【飞书授权】

需要提供以下信息：

1. App ID
2. App Secret
3. Folder Token（可选，用于指定日记保存的文件夹）

💡 如何获取：
- 访问飞书开放平台：https://open.feishu.cn/
- 创建企业自建应用
- 在「凭证与基础信息」中找到 App ID 和 App Secret
- Folder Token 可以从飞书云文档的文件夹链接中获取

请按以下格式回复（一行一个）：
App ID: cli_xxxxx
App Secret: xxxxx
Folder Token: xxxxx（可选，没有就不填）

或者回复「跳过」稍后配置。
```

等待用户回复。

**解析回复**：
- 提取 App ID、App Secret、Folder Token
- 如果用户回复「跳过」，记录为稍后配置

**确认**：
```
✓ 飞书授权信息已记录
```

#### 4.5.2 Notion 授权

```
【Notion 授权】

需要提供 Integration Token。

💡 如何获取：
- 访问 Notion Integrations：https://www.notion.so/my-integrations
- 创建新的 Integration
- 复制 Internal Integration Token
- 在 Notion 中分享页面给这个 Integration

请回复你的 Integration Token：
（或回复「跳过」稍后配置）
```

等待用户回复。

**解析回复**：
- 提取 Integration Token
- 如果用户回复「跳过」，记录为稍后配置

**确认**：
```
✓ Notion 授权信息已记录
```

#### 4.5.3 Flomo 授权

```
【Flomo 授权】

需要提供 API Token。

💡 如何获取：
- 登录 Flomo：https://flomoapp.com/
- 进入「设置」→「API」
- 复制 API Token

请回复你的 API Token：
（或回复「跳过」稍后配置）
```

等待用户回复。

**解析回复**：
- 提取 API Token
- 如果用户回复「跳过」，记录为稍后配置

**确认**：
```
✓ Flomo 授权信息已记录
```

---

## 阶段 5：生成配置文件

### 5.1 生成配置

根据人设发送消息：

**INTJ 风格**：
```
【阶段 5/5】生成配置

正在生成配置文件...
```

**ENFP 风格**：
```
【阶段 5/5】生成配置

太好了！我们快完成了 🎉

正在为你生成配置文件...
```

### 5.2 创建目录结构

使用 Bash 工具创建必要的目录：

```bash
mkdir -p ~/.openclaw/workspace/diary/config
mkdir -p ~/.openclaw/workspace/diary/personalities
mkdir -p ~/write_me/00inbox/journal
mkdir -p ~/write_me/01studio/me
mkdir -p ~/write_me/02notes/insights
```

### 5.3 生成 diary-config.json

根据用户的选择生成配置文件：

```json
{
  "personality": {
    "type": "{personality_type}",
    "file": "personalities/{personality_type}.md"
  },
  "storage": {
    "path": "~/write_me/00inbox/journal",
    "date_format": "YYYY-MM",
    "time_boundary": "06:00",
    "feishu": {
      "enabled": {true if sync_platform == "feishu" else false},
      "app_id": "{如果收集了就填，否则留空}",
      "app_secret": "{如果收集了就填，否则留空}",
      "folder_token": "{如果收集了就填，否则留空}"
    },
    "notion": {
      "enabled": {true if sync_platform == "notion" else false},
      "integration_token": "{如果收集了就填，否则留空}"
    },
    "flomo": {
      "enabled": {true if sync_platform == "flomo" else false},
      "api_token": "{如果收集了就填，否则留空}"
    }
  },
  "user_identity": {
    "enabled": {true if 用户建立了身份 else false},
    "path": "~/write_me/01studio/me"
  },
  "post_processing": {
    "note_extractor": {
      "enabled": true,
      "auto_trigger": false
    }
  }
}
```

写入文件：`~/.openclaw/workspace/diary/config/diary-config.json`

### 5.4 复制人设文件

使用 Bash 工具复制人设文件：

```bash
# 获取 skill 目录路径（相对于当前工作目录）
SKILL_DIR="{skill 目录的绝对路径}"

# 复制人设文件
cp "$SKILL_DIR/../diary/personalities/intj.md" ~/.openclaw/workspace/diary/personalities/
cp "$SKILL_DIR/../diary/personalities/enfp.md" ~/.openclaw/workspace/diary/personalities/
```

### 5.5 设置环境变量（如果需要）

如果用户提供了授权信息，提示设置环境变量：

**飞书**：
```
为了让飞书同步正常工作，需要设置环境变量。

请在你的 shell 配置文件中添加：

export FEISHU_APP_ID="{app_id}"
export FEISHU_APP_SECRET="{app_secret}"

然后重新加载配置：
source ~/.zshrc  # 如果使用 zsh
source ~/.bashrc # 如果使用 bash
```

**Notion**：
```
为了让 Notion 同步正常工作，需要设置环境变量。

请在你的 shell 配置文件中添加：

export NOTION_TOKEN="{integration_token}"

然后重新加载配置：
source ~/.zshrc  # 如果使用 zsh
source ~/.bashrc # 如果使用 bash
```

**Flomo**：
```
为了让 Flomo 同步正常工作，需要设置环境变量。

请在你的 shell 配置文件中添加：

export FLOMO_API_TOKEN="{api_token}"

然后重新加载配置：
source ~/.zshrc  # 如果使用 zsh
source ~/.bashrc # 如果使用 bash
```

### 5.6 完成提示

根据人设发送完成消息：

**INTJ 风格**：
```
✓ 设置完成

配置文件：~/.openclaw/workspace/diary/config/diary-config.json
用户档案：~/write_me/01studio/me/identity.md
日记目录：~/write_me/00inbox/journal/

现在可以开始记录日记了。

在对话中说：记一下
```

**ENFP 风格**：
```
🎉 太棒了！设置完成！

你的日记系统已经准备好了：
✓ 配置文件：~/.openclaw/workspace/diary/config/diary-config.json
✓ 用户档案：~/write_me/01studio/me/identity.md
✓ 日记目录：~/write_me/00inbox/journal/

现在你可以开始记录你的想法了 😊

试试在对话中说：记一下今天的想法
```

---

## 错误处理

### 配置文件写入失败

如果无法写入配置文件：

```
❌ 配置文件写入失败

可能的原因：
- 目录权限不足
- 磁盘空间不足

请检查 ~/.openclaw/workspace/diary/ 目录的权限。

你也可以手动创建配置文件，参考：
{显示配置文件内容}
```

### 目录创建失败

如果无法创建目录：

```
❌ 目录创建失败

请手动创建以下目录：
mkdir -p ~/.openclaw/workspace/diary/config
mkdir -p ~/write_me/00inbox/journal
mkdir -p ~/write_me/01studio/me
```

### 用户输入无效

如果多次无法识别用户输入：

```
抱歉，我没理解你的意思。

你可以：
1. 重新开始设置：setup my journal
2. 查看帮助文档：{提供文档链接}
3. 手动配置：编辑 ~/.openclaw/workspace/diary/config/diary-config.json
```

---

## 实现注意事项

### 路径处理
- 所有包含 `~` 的路径都要展开为完整路径
- 使用 `echo $HOME` 获取主目录
- 使用 `mkdir -p` 创建目录（自动创建父目录）

### 人设一致性
- 在整个对话过程中保持选定的人设风格
- INTJ：简洁、直接、少废话
- ENFP：温暖、详细、多关心

### 输入解析
- 支持多种输入方式：数字、关键词、自然语言
- 大小写不敏感
- 容错处理：识别不清时友好提示

### 授权信息安全
- 所有授权信息保存在本地配置文件
- 提示用户使用环境变量存储敏感信息
- 不在日志中记录敏感信息

### 与其他 Skills 的协作
- 生成的配置文件供 diary skill 使用
- 用户档案供 diary 和 note-extractor skills 使用
- 目录结构与整个系统保持一致

---

最后更新：2026-03-15
