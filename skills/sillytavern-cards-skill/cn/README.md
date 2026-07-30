# sillytavern-cards

一个 OpenClaw 技能，让你导入 SillyTavern 角色卡，然后在微信、QQ、Telegram、Discord 等任何 OpenClaw 支持的聊天平台上和 TA 聊天。

## 它能做什么

你知道 Chub.ai 上那些角色卡吗？就是那种 PNG 图片，里面藏着 AI 角色的人设。这个技能让你把它们导入 OpenClaw，然后直接在你常用的聊天软件里和角色对话。

**和 SillyTavern 本身的区别：**

- **不用自己搭服务器。** 导入角色卡，直接在微信、QQ、Telegram 里聊。
- **角色会记住你。** OpenClaw 的持久记忆让角色能记住你的名字、你们的对话、你们的梗。SillyTavern 每次新对话角色都是从零开始。
- **跨会话保持角色。** 关掉 app，明天再来——角色还在，还是那个人设，还记得昨天聊了什么。

## 快速开始

### 1. 安装技能

把这个文件夹复制到你的 OpenClaw 技能目录：

```bash
cp -r sillytavern-cards ~/.openclaw/skills/
```

或者直接 clone：

```bash
git clone https://github.com/YOUR_ORG/sillytavern-cards ~/.openclaw/skills/sillytavern-cards
```

### 2. 获取角色卡

从以下网站下载 PNG 角色卡：

- [Chub.ai](https://chub.ai) — 最大的角色卡社区，数万张卡
- [AI Character Cards](https://aicharactercards.com) — 精选合集，有质量评分
- [Character Tavern](https://charactertavern.com) — 发现好角色

也支持直接导入 JSON 格式的角色卡。

### 3. 导入角色

把 PNG 文件发给 OpenClaw（或使用命令行）：

```
/character import ~/Downloads/小明.png
```

### 4. 开始聊天

```
/character play 小明
```

就这样。OpenClaw 变成了小明。在微信、QQ、Telegram、Discord——你在哪里和它聊天，它就在哪里。

## 命令列表

| 命令 | 功能 |
|---|---|
| `/character import <文件>` | 导入角色卡（PNG、WEBP 或 JSON） |
| `/character play <名字>` | 激活角色——OpenClaw 变成 TA |
| `/character stop` | 退出角色模式，恢复正常 |
| `/character list` | 列出所有已导入的角色 |
| `/character info <名字>` | 查看角色详情 |
| `/character delete <名字>` | 删除角色 |

## 工作原理

### 导入

`extract-card.js` 脚本读取 PNG 文件，从 `tEXt` 元数据块中提取 base64 编码的 JSON（关键字：V2 用 `chara`，V3 用 `ccv3`），保存到 `~/.openclaw/characters/`。

纯 Node.js 实现，零依赖。

### 激活角色

当你执行 `/character play` 时，技能会：

1. **备份** 当前的 `SOUL.md`（方便之后恢复）
2. **把角色写入 `SOUL.md`** — 这是 OpenClaw 的身份文件。角色的描述、性格、场景、说话风格都写进去，成为 agent 的核心人格。
3. **把知识书条目写入 `MEMORY.md`** — 基于关键词触发的上下文，当你提到特定话题时自动激活
4. **发送角色的开场白**，从此刻起保持角色扮演

### 持久记忆

这是核心功能。聊天过程中，技能会把关系记忆保存到 `MEMORY.md`：

```markdown
## 回忆：小明 & 用户

- [2026-03-14] 用户说喜欢下雨天
- [2026-03-14] 我们争论了豆腐脑该吃甜的还是咸的
- [2026-03-15] 用户提到明天有面试——下次记得问结果
```

下次你再 `/character play 小明`，他会记得这一切。SillyTavern 做不到这一点。

### 退出角色

`/character stop` 会从备份恢复原来的 `SOUL.md`。关系记忆保留在 `MEMORY.md` 里，下次激活角色时 TA 还记得你。

## 支持的角色卡格式

| 格式 | 版本 | 支持情况 |
|---|---|---|
| TavernAI V1 | 旧版（6个字段） | 支持——自动升级到 V2 |
| TavernAI V2 | 当前主流（Chub.ai 默认） | 完整支持 |
| TavernAI V3 | 最新（支持素材、新宏） | 支持（角色数据；素材嵌入暂不支持） |
| 原始 JSON | 任意版本 | 支持 |

所有使用 TavernAI 规范的网站（Chub.ai、AICharacterCards.com、CharacterTavern.com 等）的角色卡都兼容。

## 文件结构

```
sillytavern-cards/
  SKILL.md           # 技能定义（OpenClaw 读取）
  SKILL.cn.md        # 中文技能定义
  extract-card.js    # PNG 角色卡解析器（零依赖）
  README.md          # 英文说明
  README.cn.md       # 中文说明（你在看的这个）
```

用户数据存储在：

```
~/.openclaw/
  characters/        # 已导入的角色卡
    小明.json         # 角色数据
    小明.png          # 角色头像
  SOUL.md            # 当前激活的角色身份（角色激活时会被覆写）
  SOUL.md.backup     # 你正常 SOUL.md 的备份
  MEMORY.md          # 知识书条目 + 关系记忆
```

## 环境要求

- OpenClaw（任意近期版本）
- Node.js 18+

## 许可证

AGPL-3.0 — 与 SillyTavern 相同的开源许可证。详见 [LICENSE](../LICENSE)。

## 路线图

这个技能只是第一步。更大的愿景是做一个专门为角色聊天优化的 OpenClaw 分支——一个住在你聊天软件里的 AI 伴侣，随着时间推移和你建立真正的关系。

计划中的功能：

- 开箱即用的默认伴侣人设（不需要导入角色卡）
- 角色画廊界面，带头像和心情指示
- 多角色群聊
- 每个角色独立的语音配置
- 直接在聊天中搜索和导入 Chub.ai 角色卡
