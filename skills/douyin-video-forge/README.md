# douyin-video-forge

抖音短视频全链路自动化制作 — OpenClaw Agent Skill

## 项目简介

`douyin-video-forge` 是一个 OpenClaw Agent Skill，覆盖抖音短视频制作的完整链路：

```
热点数据采集（浏览器）→ 低粉高赞视频筛选 → 竞品分析 → 语音转写分析 →
数据洞察 → 双版本脚本生成 → AI 视频生成 → 多段拼接成片
```

运营人员只需通过 OpenClaw 聊天界面用自然语言描述需求，Skill 会自动完成从趋势采集到成品视频的全部流程。

### v3.0 核心变化

**去掉 MCP Server，改为纯 Agent Skill。** 安装 = 复制文件夹，零配置，Windows/macOS/Linux 全平台支持。

| 维度 | v2.0 | v3.0 |
|------|------|------|
| 架构 | MCP Server + 9 个工具 | 纯 Agent Skill（bash 模板 + 极简 Python 脚本） |
| 安装 | pip install 5 包 + jq + MCP 配置 | 复制文件夹（或 `clawhub install`） |
| Python 依赖 | 必需（MCP Server 运行时） | 可选（仅 Kling API 和语音转写需要） |
| 平台 | macOS / Linux | macOS / Linux / **Windows** |
| 必需工具 | python3 + ffmpeg + yt-dlp | ffmpeg + yt-dlp |

---

## 功能特性

- **浏览器自动采集抖音热榜/搜索** — 直接浏览 douyin.com，零 API 成本
- **低粉高赞视频智能筛选** — LLM 自然语言指令实现阶梯降级筛选
- **竞品分析** — 浏览器访问竞品主页，分析内容表现
- **语音转写深度分析** — faster-whisper 本地转写，分析脚本结构、钩子、节奏
- **双版本脚本生成（可灵 + Seedance）** — 同时输出两种格式的脚本
- **可灵 3.0 API 自动视频生成** — 文生视频 + 图生视频，首末帧衔接确保段落连贯
- **FFmpeg 多段拼接 + BGM** — 自动拼接多段视频并叠加背景音乐
- **Cron 多日计划自动化** — 每日结合最新热点生成内容

---

## 环境要求

| 依赖 | 必需? | 说明 |
|------|-------|------|
| FFmpeg | 是 | 音视频处理 |
| yt-dlp | 是 | 抖音视频下载 |
| python3 | 否 | 仅 Kling API 视频生成和语音转写需要 |
| pyjwt + httpx | 否 | Kling API 依赖（`pip install pyjwt httpx`） |
| faster-whisper | 否 | 语音转写（`pip install faster-whisper`） |

**只需 ffmpeg + yt-dlp 即可使用数据采集和脚本生成（Phase 0-4）。**

---

## 快速安装

### 方式 1：ClawHub（推荐）

```bash
clawhub install douyin-video-forge
```

### 方式 2：手动安装

```bash
# 克隆仓库
git clone <repo-url>
cd douyin-video-forge

# 运行安装脚本
bash install.sh
```

安装脚本会：
1. 检查 ffmpeg 和 yt-dlp（必需）
2. 检查 python3 / pyjwt / httpx / faster-whisper（可选）
3. 复制 Skill 到 `~/.openclaw/skills/douyin-video-forge/`
4. 打印状态摘要

### 可选：配置可灵 API Key

```bash
export KLING_ACCESS_KEY="your-access-key"
export KLING_SECRET_KEY="your-secret-key"
```

获取地址：[klingai.com](https://klingai.com) → API 管理

---

## 使用方法

安装完成后，直接在 OpenClaw 中用自然语言对话即可。

### 示例提示语

```
# 新项目启动
我们接了一个新客户「花漾肌密」，做玻尿酸精华液推广视频。
目标人群20-35岁女性，3月15日到22日发布20个视频，周一至五每天2个，周末每天3个。

# 日常热点
帮我看看今天抖音上有什么和护肤相关的热点。

# 竞品分析
帮我分析一下润百颜这个账号的内容表现。

# 脚本生成
基于今天的热点数据，帮我生成3个45秒的种草类短视频脚本。
```

### 工作流概览

```
1. 需求录入 → 运营填写/口述项目需求
2. 内容策略 → Skill 生成品牌定位与内容方向（一次性）
3. 每日循环 →
   ├── 浏览器采集（热榜 + 搜索 + 竞品）
   ├── 视频下载 + 语音转写
   ├── 数据分析（热点匹配 + 脚本结构分析 + 方向推荐）
   ├── 脚本生成（口播文案 / 可灵版 / Seedance 版）
   ├── 视频生成（可灵 API，可选）
   └── 视频拼接（FFmpeg + BGM）
4. 成品输出 → MP4 1080x1920 竖屏视频
```

---

## 成本估算

| 场景 | 数据采集 | 可灵 API | 合计 |
|------|---------|----------|------|
| 仅脚本（不生成视频） | **$0**（浏览器免费） | $0 | **$0** |
| 每日 2 个 45s 视频 | $0 | ~$227-454/月 | ~$227-454/月 |
| 每日 3 个 45s 视频 | $0 | ~$340-680/月 | ~$340-680/月 |

> 仅输出脚本时总成本为零。

---

## API Key 获取指南

| Key | 获取地址 | 说明 |
|-----|---------|------|
| `KLING_ACCESS_KEY` | [klingai.com](https://klingai.com) | 在「API 管理」中创建，用于视频生成（可选） |
| `KLING_SECRET_KEY` | [klingai.com](https://klingai.com) | 与 Access Key 配对使用 |

> API Key 仅存储在环境变量中，不会写入代码或进入聊天记录。

---

## 常见问题 (FAQ)

**Q: 需要配置 API Key 才能使用吗？**
不需要。数据采集和脚本生成（Phase 0-4）完全通过浏览器完成，无需任何 API Key。可灵 Key 仅 AI 视频自动生成（Phase 5-6）才需要。

**Q: 需要 Python 吗？**
数据采集和脚本生成不需要 Python。Python 仅在使用可灵 API 视频生成或 faster-whisper 语音转写时需要。

**Q: 语音转写需要 GPU 吗？**
faster-whisper 默认使用 CPU（int8 量化），无需 GPU。有 GPU 时自动使用（device="auto"）。

**Q: 推荐使用什么 LLM 模型？**
强烈推荐 **Claude Sonnet 4.6+**，数据分析和创意脚本需要强推理能力。

**Q: 视频段落之间如何保持连贯？**
使用「首末帧衔接」：提取段落 1 最后一帧作为段落 2 首帧输入。配合 `--kling-elements` 参数保持角色一致性。

**Q: Windows 可以用吗？**
v3.0 支持 Windows（通过 Git Bash 或 WSL 运行 bash 命令）。

---

## 卸载

```bash
rm -rf ~/.openclaw/skills/douyin-video-forge
```
