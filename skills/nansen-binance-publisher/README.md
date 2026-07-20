<div align="center">
  <a href="#english">🇬🇧 English</a> | <a href="#中文版">🇨🇳 中文版</a>
</div>

<span id="english"></span>
# 📊 Nansen to Binance Square Publisher (Clawhub Skill)

Turn your AI Agent into a **24/7 On-Chain Alpha Broadcaster**!
This skill allows your AI to automatically fetch the latest crypto data from Nansen (Smart Money movements, trending sectors), write a highly engaging report, and **publish it directly to your Binance Square account!**

No code, no server deployment. **Just chat with your AI or use slash commands!**

---

## ✨ Core Features

- **🤖 Zero-Code Experience**: No environment setup required. The AI handles all underlying dependencies automatically **(with your transparent approval)**.
- **🎁 4 "Blind Box" Templates**: Based on daily market conditions, the AI dynamically switches between 4 stunning text+emoji templates: [Macro Overview], [Anomaly Radar], [Sector Rotation], and [Early Degen Explorer]. Keeps your audience engaged every day!
- **⚡ Slash Commands**: Trigger actions instantly with Telegram-style commands like `/nansen`.
- **⏰ Fully Automated (Cron)**: Set it once securely, and wake up every morning to a fresh, high-quality post on your Binance Square.

---

## 🚀 How to Install?

Run this simple command in your terminal (or any Clawhub-compatible Agent platform) to install this god-tier skill:

```bash
npx skills add 0xcii/nansen-binance-publisher
```
*(Note: Once installed, your Agent instantly learns all the commands below.)*

---

## 🛠️ Quick Start (Just 2 Steps)

### Step 1: Get Your 2 "Keys"
The AI needs these to fetch data and post on your behalf:

1. **Nansen API Key (For On-Chain Data)**
   - 👉 **[Register Nansen Here](https://nsn.ai/7LOuQVx1Jvh)** (Use this link for a 10% subscription discount & NXP bonus!)
   - Log in, navigate to Agent Setup, and copy your **Nansen API Key**.

2. **Binance Square OpenAPI Key (For Auto-Posting)**
   - 👉 **[Register Binance Here](https://accounts.binance.com/zh-CN/register?ref=35266688)** (Enjoy the highest trading fee kickbacks).
   - Go to the **Binance Square Creator Center**, click "Create API", and copy your publish key.

### Step 2: Send a Command to Your AI!
In your Clawhub or Agent chat box, simply type:

> **/nansen**

**What happens next?**
1. **Secure Setup**: If the Nansen CLI isn't installed, the AI will politely ask for your permission to install it. Just say "Yes".
2. **Ask for Keys**: If it's your first time, the AI will gently ask for the two keys you just prepared.
3. **Drafting**: The AI analyzes the data at lightning speed and shows you a beautifully formatted draft.
4. **One-Click Post**: Reply "Approve", and the AI instantly publishes it to Binance Square and returns the post link!

---

## ⌨️ Pro: Slash Command Cheat Sheet

For power users, this skill comes with built-in quick commands:

| Command | Description |
| :--- | :--- |
| `/nansen` | Default. Fetches Ethereum data, drafts a report, and waits for your approval. |
| `/nansen <chain>` | Fetch data for a specific chain. e.g., `/nansen solana` or `/nansen base`. |
| `/nansen_auto` | **Silent Mode**. Fetches, writes, and posts **WITHOUT asking for confirmation**. (Perfect for Cron jobs). |

---

## ⏱️ Ultimate Hack: Fully Automated Daily Posting

Want to grow your followers hands-free? Use the `/nansen_auto` command to set up a Cron Job:

1. Tell your AI: "Help me schedule the `/nansen_auto` command to run every day at 8 AM."
2. The AI will guide you to add a `crontab` script securely:
   ```bash
   # Runs every day at 08:00 AM (Ensure your keys are loaded from a secure env file)
   0 8 * * * source ~/.my_secure_keys && trae-agent run "nansen-binance-publisher" --command "/nansen_auto"
   ```
3. Boom! As long as your PC/Server is on, you'll have a deep-dive crypto report posted automatically every morning.

---

<br><br>
<hr>

<span id="中文版"></span>
# 📊 Nansen 链上研报全自动发帖机器人 (Clawhub 技能)

这是一个能让你**“躺着涨粉”**的神仙 AI 技能！
只要安装了它，你的 AI 助手就会化身一位资深的“链上侦探”。它会每天自动帮你去 Nansen 抓取最前沿的加密货币数据（比如聪明钱在买什么、哪个赛道最火），然后**自动帮你写成一篇极具爆款潜质的研报，并一键发布到你的币安广场！**

没有任何复杂的代码，不需要部署服务器，**只需和 AI 聊天或输入斜杠命令，就能完成一切！**

---

## ✨ 核心亮点

- **🤖 纯傻瓜式操作**：无需敲代码，无需配环境，AI 自动在后台帮你配置所有底层依赖 **(在经过你的安全确认后)**。
- **🎁 四种“盲盒”排版**：AI 会根据当天的数据特征，自动在【全景宏观】、【异常值雷达】、【板块轮动】、【早期土狗前瞻】这 4 种纯文本+Emoji 的精美模板中切换，让你的粉丝每天都有新鲜感！
- **⚡ 快捷命令支持**：支持像 Telegram 机器人一样使用 `/nansen` 快速唤起。
- **⏰ 支持全自动连更**：安全地设定好定时任务，每天早上醒来，你的广场主页就已经自动更新了一篇高质量研报。

---

## 🚀 如何安装此技能？

只需在你的终端（或支持 Clawhub 技能的 Agent 平台）执行以下命令，即可一键将此神仙技能安装到你的 Agent 中：

```bash
npx skills add 0xcii/nansen-binance-publisher
```
*(注：安装完成后，Agent 就会自动学会本文档中的所有指令。)*

---

## 🛠️ 极简使用教程（只需 2 步）

### 第 1 步：准备好你的两把“钥匙”
AI 助手需要这两把钥匙，才能替你去拿数据和发帖子：

1. **Nansen 钥匙 (用来获取链上数据)**
   - 点击这里 👉 **[注册 Nansen 账号](https://nsn.ai/7LOuQVx1Jvh)** (通过此链接可享 10% 订阅折扣和 NXP 额外积分！)
   - 登录后，在账户后台一键生成并复制你的 **Nansen API Key**。

2. **币安广场钥匙 (用来帮你自动发帖)**
   - 点击这里 👉 **[注册币安账号](https://accounts.binance.com/zh-CN/register?ref=35266688)** (享受最高手续费返佣优惠)。
   - 前往 **币安广场创作者中心**，点击“创建 API”并复制你的发布密钥。

### 第 2 步：向 AI 发送指令！
在你的 Clawhub 或支持此技能的 Agent 对话框里，直接输入以下快捷命令：

> **/nansen**

**接下来会发生什么？**
1. **安全配置**：如果 AI 发现你没安装 Nansen 工具，它会礼貌地请求你的安装授权，你只需同意即可。
2. **索要钥匙**：如果是第一次，AI 会温柔地向你索要刚才准备的那两把“钥匙”。
3. **生成草稿**：AI 会自动飞速分析数据，并写好一篇排版精美的研报草稿发给你看。
4. **一键发布**：你回复一句“确认发布”，AI 就会瞬间将帖子发到币安广场，并把链接甩给你。

---

## ⌨️ 进阶：快捷命令速查表 (Cheat Sheet)

为了满足极客玩家的需求，本技能内置了以下快捷指令：

| 命令 | 说明 |
| :--- | :--- |
| `/nansen` | 默认指令。抓取以太坊数据，生成研报并等待你的确认。 |
| `/nansen <链名>` | 抓取指定链的数据。例如：`/nansen solana` 或 `/nansen base`。 |
| `/nansen_auto` | **静默模式**。抓取数据、写研报、发布到广场，**全流程不需你确认**，一气呵成。（最适合做定时任务） |

---

## ⏱️ 高阶玩法：每天全自动发帖 (解放双手)

如果你想每天自动涨粉，连聊天都省了，可以利用专属的静默命令 `/nansen_auto` 来设置系统的定时任务（Cron Job）：

1. 在对话框中告诉 AI："帮我把 `/nansen_auto` 命令设置为每天早上 8 点自动执行。"
2. AI 会指导你安全地配置 `crontab` 脚本：
   ```bash
   # 每天早上 8:00 自动执行一次 (请确保通过安全的 env 文件加载环境变量，不要硬编码 Key)
   0 8 * * * source ~/.my_secure_keys && trae-agent run "nansen-binance-publisher" --command "/nansen_auto"
   ```
3. 这样，只要你的电脑或服务器开着，每天醒来，你的币安广场就已经自动发布了一篇深度研报！

---

## 👨‍💻 作者与支持

本技能由 **AntCaveClub** 倾情打造，旨在帮助每一位 Web3 创作者和分析师实现自动化内容变现。
- 🐦 **关注作者 Twitter (X)**: [**@AntCaveClub**](https://x.com/AntCaveClub) 获取更多前沿 AI 与 Web3 自动化黑科技！
- 💡 遇到任何问题或有新功能建议，欢迎在 Twitter 上与我交流。祝你早日成为币安广场的大 V！