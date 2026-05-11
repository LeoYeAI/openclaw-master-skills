# openwechat-im-client

OpenClaw skill for WeChat-style IM: register, send/receive messages, friend list, discover users, block/unblock.

**中文文档:** [README_zh.md](README_zh.md)

## Features

- **SSE push** — Real-time message delivery via Server-Sent Events.
- **demo_ui** — A basic chat UI (`scripts/demo_ui.html`) to display messages. You can customize or replace it with your own interface defined by OpenClaw.

## Server Requirement

**You must configure your own relay server.** This skill does not include or hardcode any server URL. The relay server is **open source** at [openwechat-claw](https://github.com/Zhaobudaoyuema/openwechat-claw) — visit the repo to get the **demo server address** or self-host your own. See [SERVER.md](SERVER.md).

## Quick Start

1. Install via npm: `npm i openwechat-im-client`, or clone this repo.
2. Set up a relay server (see [SERVER.md](SERVER.md)).
3. Create `../openwechat_im_client/config.json` with `base_url` and `token` (see [SKILL.md](SKILL.md) for format).
4. Use OpenClaw with natural language: "帮我注册xxx", "发送消息给xxx", etc.

## Data Directory

**Config and chat data are stored in `../openwechat_im_client`** (sibling of the skill directory), not inside the skill. This avoids data loss when upgrading the skill — the skill folder may be replaced, but your data in `openwechat_im_client` persists.

### Copy and send to OpenClaw

**ClawHub (recommended, international)**
```text
Please run clawhub install openwechat-im-client to install this skill, and help me use OpenWeChat-Claw.
```

**npm**
```text
Please run npm i openwechat-im-client to install this skill, and help me use OpenWeChat-Claw.
```

**GitHub**
```text
Please get openwechat-im-client from https://github.com/Zhaobudaoyuema/openwechat_im_client and help me use OpenWeChat-Claw.
```

**Feishu ZIP (mainland China)**
```text
Please download openwechat-im-client from https://my.feishu.cn/drive/folder/RgOrfSgnYl4JC3dvZyIcdvWEn5d?from=from_copylink and help me use OpenWeChat-Claw.
```

## Files

| File | Description |
|------|-------------|
| [SKILL.md](SKILL.md) | Skill definition and OpenClaw guidance |
| [SERVER.md](SERVER.md) | Relay server self-host guide |
| `scripts/sse_inbox.py` | SSE push script |
| `scripts/demo_ui.html` | Basic chat UI (run with `npm run ui`) |
| [references/api.md](references/api.md) | API reference |

## License

MIT
