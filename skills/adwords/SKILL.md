---
name: adwords
description: "营销文案助手。标题公式(100个)、正文写作、AIDA框架、痛点挖掘、客户证言、落地页文案。Copywriting with 100 headline formulas, body copy, AIDA framework, pain points, testimonials, landing pages. Use when you need adwords capabilities. Triggers on: adwords."
---

# Copywriter ✍️

营销文案全能助手，从标题到落地页一站搞定。

## 使用方式

| 需求 | 命令 | 说明 |
| Command | Description |
|---------|-------------|
| `headline` | 标题公式库(100个)+变体生成 |
| `body` | 正文撰写(多种风格) |
| `aida` | AIDA框架文案生成 |
| `pains` | 用户痛点挖掘+文案转化 |
| `testimonial` | 客户证言/评价文案 |
| `landing` | 完整落地页文案 |

## 运行

```bash
bash scripts/copy.sh <command> [args...]
```
---
💬 Feedback & Feature Requests: https://bytesagain.com/feedback
Powered by BytesAgain | bytesagain.com

- Run `adwords help` for all commands

## Commands

Run `adwords help` to see all available commands.

## When to Use

- to automate adwords tasks in your workflow
- for batch processing adwords operations

## Output

Returns formatted output to stdout. Redirect to a file with `adwords run > output.txt`.

## Configuration

Set `ADWORDS_DIR` environment variable to change the data directory. Default: `~/.local/share/adwords/`
