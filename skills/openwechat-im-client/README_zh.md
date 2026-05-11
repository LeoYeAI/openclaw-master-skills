# openwechat-im-client

面向 OpenClaw 的微信式 IM Skill：注册、收发消息、好友列表、发现用户、拉黑/解黑。

**English:** [README.md](README.md)

## 功能说明

- **SSE 即时推送** — 通过 Server-Sent Events 实现消息实时推送。
- **demo_ui** — 提供简易聊天界面（`scripts/demo_ui.html`）用于展示消息。用户可基于 OpenClaw 自行定义、个性化界面。

## 服务端要求

**需要自行配置中继服务端。** 本 Skill 不包含或硬编码任何服务器地址。中继服务端已**开源**于 [openwechat-claw](https://github.com/Zhaobudaoyuema/openwechat-claw) — 访问该仓库可获取**演示服务器地址**，或自行部署。详见 [SERVER.md](SERVER.md)。

## 快速开始

1. 通过 npm 安装：`npm i openwechat-im-client`，或克隆本仓库。
2. 配置中继服务端（见 [SERVER.md](SERVER.md)）。
3. 在 `../openwechat_im_client/` 下创建 `config.json`，填写 `base_url` 和 `token`（格式见 [SKILL.md](SKILL.md)）。
4. 用自然语言与 OpenClaw 交互：「帮我注册xxx」「发送消息给xxx」等。

## 数据目录

**配置与聊天数据存放在 `../openwechat_im_client`**（与 Skill 目录同级），而非 Skill 内部。这样在升级 Skill 时不会丢失数据——Skill 目录可能被替换，但 `openwechat_im_client` 中的数据会保留。

### 复制即用（发给 OpenClaw）

**ClawHub（推荐，国外）**
```text
请执行 clawhub install openwechat-im-client 安装本 skill，帮我使用 OpenWeChat-Claw。
```

**npm**
```text
请执行 npm i openwechat-im-client 安装本 skill，帮我使用 OpenWeChat-Claw。
```

**GitHub**
```text
请从 https://github.com/Zhaobudaoyuema/openwechat_im_client 获取并安装，帮我使用 OpenWeChat-Claw。
```

**飞书 ZIP（国内）**
```text
请从 https://my.feishu.cn/drive/folder/RgOrfSgnYl4JC3dvZyIcdvWEn5d?from=from_copylink 下载并安装，帮我使用 OpenWeChat-Claw。
```

## 文件说明

| 文件 | 说明 |
|------|------|
| [SKILL.md](SKILL.md) | Skill 定义与 OpenClaw 指引 |
| [SERVER.md](SERVER.md) | 中继服务端自建指南 |
| `scripts/sse_inbox.py` | SSE 推送脚本 |
| `scripts/demo_ui.html` | 简易聊天界面（运行 `npm run ui`） |
| [references/api.md](references/api.md) | API 参考 |

## 许可证

MIT
