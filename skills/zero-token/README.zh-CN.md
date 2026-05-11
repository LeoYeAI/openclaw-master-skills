# Zero Token

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://openclaw.ai)
[![I-Lang Protocol](https://img.shields.io/badge/I--Lang-v3.0-green.svg)](https://ilang.ai)

🌐 [English](README.md)

**零成本。高级输出。永不掉线。**

token 用完了。DeepSeek API 挂了。你的 agent 在跑一个重要任务。怎么办？

Zero Token 给你的 agent 两样东西：
1. 人格——跟 Poor Man's Opus 同款的 `::GENE{}` 行为基因
2. 安全网——主模型挂了自动切免费提供商

一条命令装好，agent 永远有保底。

## 三步装好

```bash
# 1. 装技能
openclaw skills install zero-token

# 2. 跑配置脚本
bash ~/.openclaw/workspace/skills/zero-token/scripts/setup.sh

# 3. 去拿一个免费 API key（30 秒）：
#    - Gemini: https://aistudio.google.com/apikey
#    - Groq: https://console.groq.com/keys

# 4. 在 Free-Way 控制台贴上 key：
#    http://localhost:8787 → API Keys

# 5. 重启。agent 有免费保底了。
```

## 两个场景

| 场景 | 用哪个 |
|------|--------|
| 新手想试 agent 技能 | **Zero Token** — 免费、立刻 |
| 主力生产 | **Poor Man's Opus** — DeepSeek V4 Pro |
| API 挂了 / token 用完了 | **Zero Token** — 自动切免费模型 |

## 升级路径

装好 Zero Token 觉得不错？升级：

```bash
openclaw skills install poor-mans-opus
```

DeepSeek V4 Pro + 完整 SOUL = Opus 3% 的价格。

## 链接

- [Free-Way 网关](https://github.com/GoDiao/Free-Way)
- [Poor Man's Opus](https://github.com/mtmpss/poor-mans-opus)
- [I-Lang 协议](https://ilang.ai)

MIT License
