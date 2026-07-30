# 💝 Personal CRM — Never Forget a Birthday Again

A personal relationship manager skill for [OpenClaw](https://github.com/openclaw/openclaw), powered by Feishu/Lark Bitable.

## Why?

Because you forgot your girlfriend's birthday and got yelled at. Because you can't remember what your friend told you last month. Because maintaining relationships is hard, and your brain wasn't built to be a database.

This isn't a cold sales pipeline tool. It's a warm, human relationship memory that helps you be a better friend, partner, and family member.

## Features

- **Smart capture** — Mention someone in conversation and it automatically records the interaction. No need to say "save this."
- **Contact management** — Track names, relationships, birthdays, hobbies, preferences, and personal notes.
- **Interaction logging** — Record stories and details, not boring meeting minutes. Captures the mood and follow-ups.
- **Birthday & anniversary reminders** — Daily proactive alerts with gift suggestions based on the person's interests.
- **Lunar calendar support** — For cultures that celebrate lunar birthdays (农历生日), automatic conversion to solar dates each year.
- **Relationship maintenance** — Alerts when you haven't contacted someone in too long, based on your desired frequency.
- **Natural language** — Just talk naturally. "Had dinner with Xiao Wang yesterday, he's switching jobs to ByteDance" triggers both an interaction record and a contact update.
- **Auto setup** — One command creates all required Bitable tables and fields automatically.

## Quick Start

1. Install: `clawhub install personal-crm`
2. Make sure your OpenClaw has the Feishu/Lark plugin enabled
3. Tell your agent: "Initialize Personal CRM" — it will create all tables automatically
4. Start using it: "I met a new friend today, Zhang Wei, he works at Google as a PM"

## Requirements

- OpenClaw with Feishu/Lark plugin enabled
- A Feishu/Lark account with Bitable access

## Data Storage

All data lives in your own Feishu/Lark Bitable — nothing is stored externally. You own your data.

## License

MIT

---

# 💝 Personal CRM — 再也不会忘记生日了

一个基于[飞书多维表格](https://www.feishu.cn)的个人关系管理技能，适用于 [OpenClaw](https://github.com/openclaw/openclaw)。

## 为什么做这个？

因为忘了女朋友生日被骂了。因为记不住上个月朋友跟你说了什么。因为维护人际关系很难，而你的大脑不是数据库。

这不是冷冰冰的销售管线工具，而是一个有温度的人际关系记忆助手，帮你做一个更好的朋友、伴侣和家人。

## 功能

- **智能捕捉** — 聊天中提到某人，自动记录互动。不需要说"帮我记一下"
- **联系人管理** — 记录姓名、关系、生日、爱好、偏好、备注等
- **互动记录** — 记录故事和细节，不是干巴巴的会议纪要。还能记录氛围和后续待办
- **生日/纪念日提醒** — 每天主动推送，附带基于对方爱好的送礼建议
- **农历生日支持** — 自动将农历日期转换为当年公历进行提醒
- **关系维护提醒** — 根据你设定的联系频率，提醒你该联系谁了
- **自然语言交互** — 直接说"昨天和小王吃饭，他说要跳槽去字节了"，自动创建互动记录并更新联系人信息
- **一键建表** — 说"初始化 Personal CRM"，自动创建所有飞书表格和字段

## 快速开始

1. 安装：`clawhub install personal-crm`
2. 确保 OpenClaw 已启用飞书插件
3. 对 agent 说："初始化 Personal CRM" — 自动创建所有表格
4. 开始使用："今天认识了一个新朋友张伟，在谷歌做产品经理"

## 要求

- OpenClaw + 飞书插件已启用
- 飞书账号（需要多维表格权限）

## 数据存储

所有数据存在你自己的飞书多维表格里，不会上传到任何外部服务。数据完全属于你。
