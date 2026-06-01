# douyin-video-forge v3.0 产品需求文档

## 1. 文档信息

| 项目 | 内容 |
|------|------|
| 版本 | v3.0 |
| 日期 | 2026-03-18 |
| 状态 | 开发中 |
| 变更摘要 | MCP Server → 纯 Agent Skill，零配置安装，Windows 支持 |

### 版本演进

| 维度 | v1.0 | v2.0 | v3.0 |
|------|------|------|------|
| 数据采集 | TikHub API（付费） | 浏览器（零成本） | 浏览器（零成本） |
| 工具执行 | MCP Server (13 工具) | MCP Server (9 工具) | **bash 模板 + Python 脚本（零 MCP）** |
| Python 依赖 | 必需 | 必需（MCP 运行时） | **可选**（仅 Kling API / 转写） |
| 安装方式 | pip + MCP 配置 | pip 5 包 + jq + MCP 配置 | **复制文件夹** |
| 平台 | macOS / Linux | macOS / Linux | macOS / Linux / **Windows** |
| 入口门槛 | TIKHUB_API_KEY + Python | Python + FFmpeg + yt-dlp | **FFmpeg + yt-dlp** |

### v2.0 → v3.0 核心决策

v2.0 的 9 个 MCP 工具中 6 个是 CLI 薄包装（yt-dlp、ffmpeg），不值得维护 MCP Server + 依赖链。去掉 MCP Server 后：
- 安装成本降低一个数量级（复制文件夹 vs pip install 5 包 + jq + openclaw.json 配置）
- Windows 兼容性从"需要 WSL/conda 调试"变为"开箱即用"
- Python 从必需降为可选（Tier 1 数据采集+脚本生成不需要 Python）

---

## 2. 产品概述

`douyin-video-forge` 是一个 OpenClaw Skill，覆盖抖音短视频制作的完整链路：

```
热点采集（浏览器）→ 低粉高赞视频筛选（LLM）→ 竞品分析（浏览器）→ 语音转写分析 →
数据洞察 → 脚本生成 → AI 视频生成 → 多段拼接成片
```

**v2.0 核心范式：零第三方数据 API 依赖**。所有数据采集通过 OpenClaw 内置浏览器以语义爬取方式完成，LLM 直接理解页面内容并提取结构化数据。唯一的外部 API 调用仅限于 AI 视频生成（可灵 3.0，可选）。

---

## 3. 目标用户

| 角色 | 使用场景 |
|------|---------|
| 短视频运营人员 | 日常热点追踪、内容策划、脚本批量生产 |
| MCN 机构 | 多账号矩阵内容管理、竞品监控 |
| 品牌方 | 产品推广视频制作、数据驱动内容决策 |

---

## 4. 技术架构

### v3.0 架构图

```
SKILL.md (脑) ─── 编排 ──→ OpenClaw 浏览器 (眼) → 抖音网页
    │                         │
    │                         ├── 热榜：douyin.com/hot
    │                         ├── 搜索：douyin.com/search/<keyword>
    │                         ├── 竞品：douyin.com/user/<sec_uid>
    │                         └── 评论：视频页面评论区
    │
    ├── bash 命令 ──→ yt-dlp（视频下载）/ ffmpeg（音视频处理）
    │
    └── Python 脚本 ──→ scripts/kling_api.py（Kling API）
                        scripts/transcribe.py（语音转写）
```

### 目录结构

```
douyin-video-forge/
├── SKILL.md                     # Agent Skill 编排指令（核心）
├── scripts/
│   ├── kling_api.py             # Kling API CLI（JWT + 生成 + 轮询 + 帧提取）
│   └── transcribe.py            # 语音转写 CLI（faster-whisper）
├── references/                  # LLM 知识库（SKILL.md 按需引用）
│   ├── browser-navigation.md
│   ├── douyin-algorithm.md
│   ├── kling-prompt-guide.md
│   ├── seedance-prompt-guide.md
│   ├── script-templates.md
│   └── trend-analysis.md
├── examples/                    # 示例文件
└── install.sh                   # 前置检查 + 复制安装
```

### 模型推荐

强烈推荐 **Claude Sonnet 4.6+**，数据分析和创意脚本需要强推理能力。

---

## 5. 功能需求

### 就绪标志

| 标志 | 含义 | 检查项 | 阻塞? |
|------|------|--------|-------|
| `data_ready` | 数据采集+脚本生成 | Python 3.10+ / FFmpeg / yt-dlp | **是**，进入 Phase 0 的前提 |
| `video_ready` | AI 视频生成 | Kling API Key + 连通性 | 否，仅 Phase 5-6 需要 |
| `voice_ready` | 语音转写 | faster-whisper 可导入 | 否，降级跳过 |

**`data_ready` 不再需要任何 API Key** — 安装门槛大幅降低。

### Phase 0：需求录入

与 v1.0 相同。展示需求模板，支持自填或引导式填写。

### Phase 1：内容策略框架

与 v1.0 相同。为整个项目建立创作决策边界。

### Phase 2：每日数据采集（v2.0 重写）

| 步骤 | 方式 | 操作 |
|------|------|------|
| 1 热榜 | 浏览器 | 导航 douyin.com/hot → LLM 读取 Top 50 热点 |
| 2 关键词搜索 | 浏览器 | 导航 douyin.com/search/\<keyword\>?type=video → LLM 在脑内应用低粉高赞筛选 |
| 3 行业趋势 | web_search | 与 v1.0 相同 |
| 4 头部视频深度分析 | 浏览器+MCP | 选视频 → video_download → 帧分析 + audio_extract → audio_transcribe → 分析脚本结构 |
| 5 评论阅读 | 浏览器 | 在视频页面滚动到评论区，直接阅读真实评论 |
| 6 竞品分析（可选） | 浏览器 | 导航竞品主页 → 读 profile + 近期作品 → 下载 1-2 个爆款做深度分析 |
| 7 语音转写降级链 | MCP+浏览器 | ① faster-whisper → ② 浏览器读抖音AI章节要点 → ③ 跳过，仅用视觉分析 |

#### 低粉高赞筛选（自然语言版）

筛选标准（在 SKILL.md 中以自然语言描述）：
- 作者粉丝数 ≤ max_followers（默认 5 万）
- 点赞量相对于作者体量偏高（互动率高）
- 若符合条件不足 5 个：放宽粉丝上限 50%，降低互动率要求 25%
- 若仍不足：记录"关键词X结果有限"，继续

### Phase 3：数据分析 + 方向推荐

在 v1.0 基础上新增第 7 维度：

1. 热点匹配
2. 爆款切入角度
3. 评论洞察
4. 视频类型推荐
5. 竞品差异化
6. 内容形态适配性
7. **竞品脚本结构分析**（新）— 基于语音转写分析钩子类型、节奏、用词、情绪曲线

### Phase 4：脚本生成

与 v1.0 基本相同，三种输出格式（口播文案 / 可灵版 / Seedance 版）。

### Phase 4→5 门控检查

检查 `video_ready` 标志（替代旧的 `phase2_ready`）。

### Phase 5：视频生成

与 v1.0 相同（可灵 3.0 API）。

### Phase 6：视频拼接

与 v1.0 相同（FFmpeg concat + BGM）。

---

## 6. 工具清单（v3.0）

v3.0 去掉 MCP Server，工具分为两类：

### bash 命令模板（5 个，SKILL.md 内联）

| 操作 | 命令 | 原 MCP 工具 |
|------|------|------------|
| 视频下载 | `yt-dlp ...` | `video_download` |
| 音频提取 | `ffmpeg -i ... -vn ...` | `audio_extract` |
| 视频拼接 | `ffmpeg -f concat ...` | `video_concat` |
| 帧提取 | `ffprobe + ffmpeg` | `kling_extract_frame` |
| 环境检查 | `which ffmpeg && which yt-dlp` | `env_check` |

### Python CLI 脚本（4 个操作，2 个脚本）

| 脚本 | 子命令 | 功能 | 原 MCP 工具 |
|------|--------|------|------------|
| `kling_api.py` | `generate` | 文生视频（自动轮询） | `kling_generate` |
| `kling_api.py` | `generate-with-image` | 图生视频（首末帧衔接） | `kling_generate_with_image` |
| `kling_api.py` | `check-status` | 查询任务状态 | `kling_check_status` |
| `transcribe.py` | — | 语音转写 | `audio_transcribe` |

---

## 7. 浏览器策略

### MVP（v2.0 当前）

- 意图导向指令：写"找到搜索框输入关键词"而非 CSS 选择器
- 步骤间 3-5 秒间隔，防触发反爬
- 每步以"你应该看到..."结尾，LLM 自验证
- 降级链：页面不可用时的备选方案

### V2（规划中）

- Camoufox 反检测浏览器
- 指纹随机化
- 代理轮转

### V3（远期）

- 多账号会话管理
- Cookie 池
- 验证码自动识别

---

## 8. 数据源规格

### 浏览器数据采集

| 数据 | URL 模式 | 采集方式 |
|------|---------|---------|
| 热榜 Top 50 | `douyin.com/hot` | 页面直读 |
| 视频搜索 | `douyin.com/search/<keyword>?type=video` | 页面直读 + 滚动加载 |
| 用户主页 | `douyin.com/user/<sec_uid>` | 页面直读 profile + 作品列表 |
| 视频评论 | 视频详情页评论区 | 滚动加载评论 |

### 精度说明

浏览器采集的数据精度低于 API（如播放量可能为"xx万"而非精确数字）。这是可接受的 tradeoff：**可靠性 > 精度**。语音转写能力补偿了深度分析的需求。

---

## 9. 视频生成规格

与 v1.0 相同，使用可灵 3.0 API：

| 参数 | 值 |
|------|-----|
| 模型 | kling-v3 |
| 分辨率 | 1080×1920（pro 模式） |
| 段落时长 | 10-15 秒 |
| 首末帧衔接 | kling_extract_frame → kling_generate_with_image |
| 角色一致性 | kling_elements（2-50 张参考图） |

---

## 10. 安装部署

### 依赖

| 依赖 | 类型 | 必需? | 说明 |
|------|------|-------|------|
| FFmpeg | 系统级 | 是 | 音视频处理 |
| yt-dlp | pip/系统 | 是 | 视频下载 |
| python3 | 系统级 | 否 | 仅 Kling API 和语音转写需要 |
| pyjwt + httpx | pip | 否 | Kling API JWT 签名和 HTTP |
| faster-whisper | pip | 否 | 语音转写，首次运行下载 ~1.5GB 模型 |

### 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| KLING_ACCESS_KEY | 否（仅视频生成） | 可灵 API |
| KLING_SECRET_KEY | 否（仅视频生成） | 可灵 API |

### 安装步骤

```bash
# 推荐
clawhub install douyin-video-forge

# 或手动
bash install.sh
```

安装脚本自动完成：检查 ffmpeg/yt-dlp → 检查可选依赖 → 复制 Skill 到 `~/.openclaw/skills/` → 打印状态摘要。

---

## 11. SKILL.md 元数据

```yaml
metadata:
  openclaw:
    requires:
      bins:
        - ffmpeg
        - yt-dlp
      optionalBins:
        - python3
      optionalEnv:
        - KLING_ACCESS_KEY
        - KLING_SECRET_KEY
    emoji: "🎬"
    os:
      - darwin
      - linux
      - win32
```

关键变化：`python3` 从 `requires.bins` → `optionalBins`；新增 `win32` 平台支持。

---

## 12. 风险矩阵

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| 抖音反爬阻断浏览器 | 高 | 数据采集中断 | 步骤间 3-5s 等待 + CAPTCHA 降级 + V2 Camoufox |
| 页面结构变化导致指令失效 | 中 | 采集失败 | 意图导向指令 + LLM 实时适应 + references/ 独立更新 |
| yt-dlp 抖音提取器失效 | 中 | 视频下载失败 | 活跃维护 + pip install --upgrade yt-dlp + 浏览器截图降级 |
| whisper 首次下载 1.5GB | 确定 | 首次等待 | env_check 提前提示 + install.sh 可选预下载 |
| 浏览器数据精度低于 API | 确定 | 分析精度下降 | 可接受 tradeoff + 语音转写补偿深度分析 |

---

## 13. 安全合规

- API Key 仅存储在环境变量中，绝不硬编码或进入聊天记录
- 浏览器访问遵循抖音 robots.txt 和使用条款
- 不存储用户个人信息，仅处理公开内容数据
- 视频下载仅用于内容分析，不进行二次分发
- 语音转写完全在本地执行，音频数据不上传到任何外部服务

---

## 14. 开发计划（v3.0）

| # | 内容 | 状态 |
|---|------|------|
| 1 | 创建 `scripts/kling_api.py`（从 MCP 移植，async→sync） | 完成 |
| 2 | 创建 `scripts/transcribe.py`（从 MCP 移植） | 完成 |
| 3 | 改造 SKILL.md（MCP 调用 → bash/script 命令） | 完成 |
| 4 | 精简 install.sh（390 行 → ~60 行） | 完成 |
| 5 | 更新 CLAUDE.md / PRD.md / README.md | 完成 |
| 6 | 删除 `mcp_server/` 和 `requirements.txt` | 完成 |
| 7 | 验证（语法检查 + CLI 可用性） | 完成 |

---

## 15. 迁移指南

### v2.0 → v3.0 升级步骤

1. **更新代码**：`git pull` 获取最新代码
2. **重新安装**：`bash install.sh`（会自动清理旧的 MCP 相关文件）
3. **清理 MCP 配置**：从 `~/.openclaw/openclaw.json` 的 `mcpServers` 中移除 `douyin-video-forge` 条目
4. **可选**：`pip install pyjwt httpx`（仅 Kling API 需要）

### v3.0 破坏性变更

- 删除 `mcp_server/` 目录和 `requirements.txt`
- 删除 9 个 MCP 工具 → 替换为 bash 命令模板 + Python CLI 脚本
- 不再需要 fastmcp、jq 依赖
- `openclaw.json` 中不再需要 MCP Server 配置
- python3 从必需降为可选

---

## 附录

### A. yt-dlp 命令参考

```bash
# 下载抖音视频（最佳画质）
yt-dlp -f best "https://www.douyin.com/video/xxx"

# 下载并提取音频
yt-dlp -x --audio-format wav "https://www.douyin.com/video/xxx"

# 更新 yt-dlp
pip install --upgrade yt-dlp
```

### B. faster-whisper 模型对照

| 模型 | 大小 | 中文准确率 | 推荐场景 |
|------|------|-----------|---------|
| tiny | ~75MB | ~80% | 快速测试 |
| base | ~150MB | ~85% | 开发调试 |
| small | ~500MB | ~90% | 日常使用 |
| medium | ~1.5GB | ~95% | **推荐**（精度/速度平衡） |
| large-v3 | ~3GB | ~97% | 最高精度 |

### C. 可灵 3.0 API

参见 v1.0 附录，无变化。

### D. FFmpeg 常用命令

```bash
# 提取音频（16kHz mono WAV）
ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav

# 每 2 秒提取一帧
ffmpeg -i video.mp4 -vf "fps=0.5" -q:v 2 frame_%03d.jpg

# 拼接视频
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
```
