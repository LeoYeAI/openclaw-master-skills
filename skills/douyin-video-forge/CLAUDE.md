# douyin-video-forge 开发指南

## 项目结构

```
douyin-video-forge/
├── SKILL.md                     # Agent Skill 编排指令（核心）
├── scripts/
│   ├── kling_api.py             # Kling API CLI（JWT + 生成 + 轮询 + 帧提取）
│   └── transcribe.py            # 语音转写 CLI（faster-whisper）
├── references/                  # LLM 知识库（SKILL.md 按需引用）
├── examples/                    # 示例文件
├── install.sh                   # 前置检查 + 复制安装（~60 行）
├── CLAUDE.md                    # 本文件
├── PRD.md                       # 产品需求文档
└── README.md                    # 安装使用说明
```

## 关键设计决策

1. **v3.0 纯 Agent Skill**：去掉 MCP Server，bash 命令模板 + 极简 Python 脚本替代。安装 = 复制文件夹
2. **浏览器语义爬取**：数据采集由 SKILL.md 编排 OpenClaw 内置浏览器完成
3. **bash 优先**：5 个原 MCP 工具变为 SKILL.md 内 bash 命令模板（yt-dlp、ffmpeg）
4. **极简 Python 脚本**：仅 Kling JWT 签名和 faster-whisper 需要 Python（2 个脚本）
5. **Auto-poll**：`kling_api.py generate` 内部自动轮询任务状态（interval=10s, timeout=300s）
6. **JSON stdout**：Python 脚本 JSON 输出到 stdout，进度/错误到 stderr
7. **临时文件管理**：下载的视频和帧存入 `mktemp -d`，返回绝对路径
8. **三层降级链**：语音转写 → 抖音AI章节要点（浏览器）→ 跳过
9. **错误全中文**：所有错误消息使用中文，面向非技术运营人员

## 开发命令

```bash
# 验证 kling_api.py CLI
python3 scripts/kling_api.py --help
python3 scripts/kling_api.py check-connectivity

# 验证 transcribe.py CLI
python3 scripts/transcribe.py --help

# 语法检查 install.sh
bash -n install.sh

# 检查 SKILL.md 无 MCP 残留
grep -c "MCP\|mcp_server\|FastMCP\|ToolError\|fastmcp" SKILL.md  # 应为 0
```

## 代码约定

- 所有用户可见文本使用中文
- API Key 只从环境变量读取，绝不硬编码
- Python 脚本仅依赖 pyjwt + httpx（Kling）或 faster-whisper（转写）
- SKILL.md 中 bash 命令模板使用完整路径 `~/.openclaw/skills/douyin-video-forge/scripts/`
- python3 为可选依赖（Tier 1 数据采集+脚本生成不需要 Python）

## 依赖

### 必需（Tier 1：数据采集 + 脚本生成）
- `ffmpeg`：系统级，音视频处理
- `yt-dlp`：视频下载

### 可选（Tier 2：AI 视频生成）
- `python3`：运行 kling_api.py
- `pyjwt`：Kling API JWT 签名
- `httpx`：HTTP 客户端

### 可选（Tier 3：语音转写）
- `faster-whisper`：本地语音转写
