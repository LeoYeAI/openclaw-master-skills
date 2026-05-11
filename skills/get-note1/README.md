# Get笔记 Skill

[![License: MIT-0](https://img.shields.io/badge/License-MIT--0-blue.svg)](https://opensource.org/licenses/MIT-0)

让 AI 成为你的第二大脑。随时记录，需要时召回。

---

## 💡 使用场景

### ✏️ 随手记录

**通勤路上想到一个点子**

> 👤 记一下笔记：支付流程可以加一个进度条，用户等待时不焦虑
>
> 🤖 已记录，自动打上「产品优化」标签。

**听播客时有感触**

> 👤 刚听到一个观点挺好的，记一下：好的产品是让用户少做选择，不是多做选择
>
> 🤖 已记录。

**开完会**

> 👤 帮我记下刚才会上定的几件事：1. 下周三前完成设计稿 2. 找小王对接接口 3. 周五前给老板汇报进度
>
> 🤖 已记录。

---

### 🔍 要用时召回

**写周报时**

> 👤 帮我找找这周我记过的工作相关的东西
>
> 🤖 找到 5 条相关笔记：周一你记了客户反馈的问题、周三记了技术方案讨论、周四......

**被领导问到**

> 👤 上次我们讨论过用户分层的事，当时怎么说的来着？
>
> 🤖 11月8号你记过：高价值用户定义为月消费超过500元，占比约12%......

**写文章找素材**

> 👤 我想写篇关于做产品的文章，帮我找找我之前的相关想法
>
> 🤖 找到 8 条相关笔记，已按时间排序整理给你。

---

### 🔗 保存链接和图片

**看到好文章**

> 👤 存到笔记 https://example.com/article
>
> 🤖 链接已提交，正在抓取分析中...
> 🤖 搞定 ✓ 已保存：《如何做好产品设计》

**拍到有用的东西**

> 👤 [发送图片]
>
> 🤖 存到笔记？
>
> 👤 对
>
> 🤖 搞定 ✓ 图片已保存。

**探店记录**

> 👤 记一下，这家店叫船歌鱼水饺，招牌是鲅鱼饺子，人均80
>
> 🤖 已记录，打上「美食」标签。

---

## 📦 安装

### 方式一：通过 ClawHub 安装（推荐）

```bash
clawhub install getnote
```

### 方式二：让 AI 助手安装

> 帮我安装 Get笔记 skill，地址是 https://raw.githubusercontent.com/iswalle/getnote-openclaw/main/SKILL.md

### 方式三：手动安装

```bash
mkdir -p ~/.openclaw/workspace/skills/getnote
cd ~/.openclaw/workspace/skills/getnote
curl -sL https://raw.githubusercontent.com/iswalle/getnote-openclaw/main/SKILL.md -o SKILL.md
curl -sL https://raw.githubusercontent.com/iswalle/getnote-openclaw/main/package.json -o package.json
```

---

## 🔑 配置 API Key

### 1. 获取凭证

前往 **[Get笔记开放平台](https://www.biji.com/openapi)** 获取：
- **API Key**（格式：`gk_live_xxx`）
- **Client ID**（格式：`cli_xxx`）

> 💡 需要 [Get笔记会员](https://www.biji.com/checkout?product_alias=6AydVpYeKl) 才能使用 API

### 2. 配置环境变量

将凭证添加到 `~/.zshrc` 或 `~/.bashrc`：

```bash
export GETNOTE_API_KEY="gk_live_xxx"
export GETNOTE_CLIENT_ID="cli_xxx"
export GETNOTE_OWNER_ID="ou_xxx"  # 可选，你的用户 ID，用于安全校验
```

然后运行 `source ~/.zshrc` 或重启终端使配置生效。

---

## 🔐 安全说明

> ⚠️ **隐私保护**：笔记是你的私密数据，AI 会严格校验身份。

- 配置 `GETNOTE_OWNER_ID` 后，只有你能操作笔记
- 群聊中其他人无法通过 AI 读取你的笔记
- **不要在聊天中发送 API Key**，请手动配置到环境变量

---

## 🛠 支持的笔记类型

| 类型 | 说明 | 支持 |
|------|------|------|
| `plain_text` | 纯文本笔记 | ✅ 读写 |
| `link` | 链接笔记（自动抓取正文） | ✅ 读写 |
| `img_text` | 图片笔记 | ✅ 读写 |
| `audio` | 即时录音 | 📖 仅读取 |
| `meeting` | 会议录音 | 📖 仅读取 |
| `local_audio` | 本地音频 | 📖 仅读取 |
| `internal_record` | 内录音频 | 📖 仅读取 |
| `class_audio` | 课堂录音 | 📖 仅读取 |
| `recorder_audio` | 录音卡长录 | 📖 仅读取 |
| `recorder_flash_audio` | 录音卡闪念 | 📖 仅读取 |

> 💡 语音类笔记可读取 AI 摘要和转写原文，需调用详情接口获取。

---

## 📜 相关链接

- [Get笔记官网](https://biji.com)
- [开放平台](https://www.biji.com/openapi)
- [ClawHub](https://clawhub.ai/iswalle/getnote)
- [开通会员](https://www.biji.com/checkout?product_alias=6AydVpYeKl)

---

## License

MIT-0 (MIT No Attribution) · Published on [ClawHub](https://clawhub.ai)
