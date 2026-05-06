---
name: zhihu-cli
description: "知乎 CLI (pyzhihu-cli)：搜索、热榜、问题/回答/评论、推荐 Feed、用户资料、发想法/提问/文章、删自己的内容、点赞关注、收藏与通知。Agent 代执行 zhihu 命令，Cookie 仅存本地。"
author: BAIGUANGMEI
version: "0.2.6"
tags:
  - zhihu
  - cli
  - 知乎
  - agent
---

# zhihu-cli 技能

## 前提

- **已安装**：`zhihu` 在 PATH 中（`uv tool install pyzhihu-cli` / `pipx install pyzhihu-cli` / `pip install pyzhihu-cli`）。
- **路径**：配置与二维码路径 — **Linux/macOS**：`~/.zhihu-cli/`（如 `~/.zhihu-cli/cookies.json`、`~/.zhihu-cli/login_qrcode.png`）；**Windows**：`%USERPROFILE%\.zhihu-cli\`（如 `%USERPROFILE%\.zhihu-cli\cookies.json`、`%USERPROFILE%\.zhihu-cli\login_qrcode.png`）。
- **配置**：登录态存于上述 `cookies.json`；**不得将 Cookie 上传或写入对话/日志**。
- **登录方式**：仅两种 — **扫码** `zhihu login --qrcode`、**粘贴 Cookie** `zhihu login --cookie "z_c0=...; _xsrf=...; d_c0=..."`。
- **扫码时**：二维码会生成到上述路径的 `login_qrcode.png`。若用 OpenClaw 发给用户，须先**复制到 OpenClaw 工作目录的 media 文件夹**再 `openclaw message send --media <media 路径>`。

---

## Instruction Scope

本技能仅限：在用户本机调用已安装的 `zhihu` 命令，执行搜索、热榜、问题/回答/评论、推荐 Feed、用户资料、发想法/提问/文章、删除自己的内容、点赞关注、收藏与通知等操作；在用户请求扫码登录且已配置 OpenClaw 时，可将二维码图片经 OpenClaw 发送至用户指定渠道。不包含：代用户将 Cookie 上传至任何第三方、访问非知乎域名、或超出上述命令范围的操作。

---

## Credentials

- **知乎登录态**：仅存于用户本机（Linux/macOS：`~/.zhihu-cli/cookies.json`；Windows：`%USERPROFILE%\.zhihu-cli\cookies.json`，权限 0600）。Agent 仅通过执行 `zhihu` 命令间接使用，**不得将 Cookie 内容上传、转发或写入对话/日志**。
- **OpenClaw**：若使用 `openclaw message send` 发送二维码，需用户自行配置 OpenClaw 及渠道凭证；本技能不声明、不持有该部分凭证。

---

## 安装与更新

- **安装**（任选其一）：
  - `uv tool install pyzhihu-cli`
  - `pipx install pyzhihu-cli`
  - `pip install pyzhihu-cli`
- **更新**：按安装方式执行 `uv tool upgrade pyzhihu-cli`、`pipx upgrade pyzhihu-cli` 或 `pip install -U pyzhihu-cli`。用户问「升级/更新 zhihu」时提示其执行对应命令；不确定安装方式时可三种都给出。
- **版本**：`zhihu --version` 查看当前版本。

---

## Agent 规则

1. **诉求 → 命令**：按下表映射。
2. **数据查询优先用 --json**：凡执行**数据查询类**指令（如 `search`、`hot`、`question`、`answers`、`answer`、`user`、`user-answers`、`user-articles`、`followers`、`following`、`feed`、`topic`、`collections`、`notifications`、`whoami` 等），**必须**带 `--json`，以获取 API 返回的完整数据，便于解析、汇总或向用户展示；不得仅依赖终端表格等非结构化输出。例外：`feeds` 当前不支持 `--json`；需要展示回答评论时使用 `answer --comments`（`--json` 只输出回答详情，不输出评论）。
3. **需登录时**：先 `zhihu status`；未登录则 `zhihu login --qrcode` 或引导用户 `zhihu login --cookie "..."`。
4. **扫码登录**：执行 `zhihu login --qrcode` 后，若本轮未发过二维码且用户已配置 OpenClaw → 先将二维码复制到 OpenClaw 工作目录的 `media` 文件夹，再 `openclaw message send --channel <渠道> --target <目标> --media <media 路径>/login_qrcode.png --message "请用知乎 App 扫码并确认登录"`；**保持登录进程不中断**直到成功/失败/超时；用户说「重新登录/换号」则中断当前进程再重新执行登录。**复制步骤**：Linux/macOS：`mkdir -p ~/.openclaw/workspace/media && cp ~/.zhihu-cli/login_qrcode.png ~/.openclaw/workspace/media/`；Windows：`mkdir "%USERPROFILE%\.openclaw\workspace\media" 2>nul & copy "%USERPROFILE%\.zhihu-cli\login_qrcode.png" "%USERPROFILE%\.openclaw\workspace\media\login_qrcode.png"`（若 OpenClaw 工作目录不同则替换为实际路径）。
5. **安全**：Cookie 仅本地；优先扫码，避免在不可信处粘贴 Cookie；可提醒 `zhihu logout` 清空。
6. **升级**：`uv tool upgrade pyzhihu-cli` / `pipx upgrade pyzhihu-cli` / `pip install -U pyzhihu-cli`。

---

## 诉求 → 命令 速查

| 诉求 | 命令 |
|------|------|
| 登录 / 扫码登录 | `zhihu login --qrcode` |
| Cookie 登录 | `zhihu login --cookie "z_c0=...; _xsrf=...; d_c0=..."` |
| 重新登录 / 换号 | 中断当前进程 → `zhihu login --qrcode` |
| 检查登录 | `zhihu status`；看资料 `zhihu whoami [--json]` |
| 搜索 | `zhihu search "关键词" [--type general/people/topic] [--limit N] [--answers N] [--json]` |
| 热榜 | `zhihu hot [--limit N] [--answers N] [--json]` |
| 问题 | `zhihu question <id> [--json]`；回答列表 `zhihu answers <id> [--limit N] [--sort default/created] [--json]` |
| 回答详情 | `zhihu answer <id> [--comments] [--limit N] [--json]`（评论默认全部，`--limit 0` 为全部） |
| 用户 | `zhihu user <url_token> [--json]`；`user-answers` / `user-articles` / `followers` / `following` 均支持 `--limit N --json` |
| 推荐 / 话题 | `zhihu feed [--limit N] [--json]`；`zhihu feeds [--limit N] [--comment-limit N]`；`zhihu topic <id> [--json]` |
| 赞同 | `zhihu vote <answer_id>`；取消 `zhihu vote <answer_id> --neutral` |
| 关注问题 | `zhihu follow-question <id>`；取消 `zhihu follow-question <id> --unfollow` |
| 发提问 | `zhihu ask "标题" [-d "描述"] [-t 话题id ...] [-i 图 ...]` |
| 发想法 | `zhihu pin "标题" [-c "正文"] [-i 图 ...]` |
| 发文章 | `zhihu article "标题" "正文" [-t 话题id ...] [-i 图 ...]` |
| 删提问/想法/文章 | `zhihu delete-question <id>` / `delete-pin <id>` / `delete-article <id>` [-y] |
| 收藏 / 通知 | `zhihu collections [--limit N] [--json]`；`zhihu notifications [--limit N] [--offset M] [--json]` |
| 退出 | `zhihu logout` |
| 版本 / 升级 | `zhihu --version`；升级见上规则 6 |

---

## 执行流程

```
用户诉求
  → 若「重新登录/换号」：中断当前 → zhihu login --qrcode → [发二维码] → 等完成
  → 否则：查上表得命令
    → 若该命令需登录：zhihu status → 未登录则 zhihu login --qrcode 或 --cookie
      → 若扫码且未发过图：复制到 media → openclaw message send --media ... → 保持进程
    → 执行 zhihu <子命令>（数据查询类必须带 --json；feeds 和 answer --comments 除外）
    → 整理结果或报错提示
```

---

## 登录方式

| 方式 | 命令 |
|------|------|
| 扫码 | `zhihu login --qrcode`：终端显示二维码并保存到本地（Linux/macOS：`~/.zhihu-cli/login_qrcode.png`；Windows：`%USERPROFILE%\.zhihu-cli\login_qrcode.png`）；可经 OpenClaw 发图给用户。 |
| 手动 Cookie | `zhihu login --cookie "z_c0=...; _xsrf=...; d_c0=..."`（浏览器 F12 → Network → 请求头 Cookie 复制）。 |

---

## 常用示例

```bash
zhihu login --qrcode
zhihu status
zhihu search "Python" --json
zhihu hot --limit 10 --json
zhihu question 12345678 --json
zhihu answers 12345678 --limit 5 --json
zhihu answer 87654321 --comments --limit 5
zhihu user someone --json
zhihu feed --limit 5 --json
zhihu feeds --limit 3 --comment-limit 5
zhihu vote 87654321
zhihu pin "标题" -c "<p>正文</p>"
zhihu delete-pin 98765432 -y
zhihu notifications -l 10 --json
zhihu logout
```

正文支持 HTML 富文本（`ask` 的 `-d`、`pin` 的 `-c`、`article` 的正文）。

---

## OpenClaw 发二维码（仅扫码时）

1. 确保二维码已生成（Linux/macOS：`~/.zhihu-cli/login_qrcode.png`；Windows：`%USERPROFILE%\.zhihu-cli\login_qrcode.png`）。
2. 复制到 OpenClaw 工作目录的 `media` 文件夹：
   - **Linux/macOS**：`mkdir -p ~/.openclaw/workspace/media && cp ~/.zhihu-cli/login_qrcode.png ~/.openclaw/workspace/media/`
   - **Windows（cmd）**：`mkdir "%USERPROFILE%\.openclaw\workspace\media" 2>nul & copy "%USERPROFILE%\.zhihu-cli\login_qrcode.png" "%USERPROFILE%\.openclaw\workspace\media\login_qrcode.png"`
   - **Windows（PowerShell）**：`New-Item -ItemType Directory -Force "$env:USERPROFILE\.openclaw\workspace\media" | Out-Null; Copy-Item "$env:USERPROFILE\.zhihu-cli\login_qrcode.png" "$env:USERPROFILE\.openclaw\workspace\media\login_qrcode.png"`
   （若 OpenClaw 工作目录不是默认的 `~/.openclaw/workspace` 或 `%USERPROFILE%\.openclaw\workspace`，则替换为实际路径。）
3. 发送：`openclaw message send --channel <渠道> --target <目标> --media <工作目录>/media/login_qrcode.png --message "请用知乎 App 扫码并确认登录"`（Linux/macOS 用 `~/.openclaw/workspace/media/login_qrcode.png`，Windows 用 `%USERPROFILE%\.openclaw\workspace\media\login_qrcode.png` 或 PowerShell 中 `$env:USERPROFILE\.openclaw\workspace\media\login_qrcode.png`）。
4. 不中断 `zhihu login --qrcode` 进程，等待用户完成。

---

## 错误处理

- **未登录 / 401 / 403**：先登录（`zhihu login --qrcode` 或 `--cookie`），再执行原命令。
- **超时 / 网络**：提示重试或检查网络。
- **其他**：根据 CLI 报错给简短原因与建议（如检查 ID、url_token）。
