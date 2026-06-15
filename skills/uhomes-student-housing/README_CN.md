# uhomes-student-housing

[English](./README.md) | [日本語](./README_JP.md)

一个帮助留学生在 [uhomes.com](https://en.uhomes.com) 上找到经过验证的学生公寓的 AI Skill。

支持 OpenClaw 和 Claude.ai。实时抓取 uhomes.com 房源数据，返回带直接预订链接的推荐结果。支持**中文**、**英文**和**日语**。

## 安装（OpenClaw / ClawHub）

```bash
clawhub install uhomes-student-housing
```

## 使用示例

自然提问即可，Skill 会自动识别住宿相关查询：

```
帮我找曼彻斯特大学附近的学生公寓，预算 £250/周
```

```
我刚拿到 UCL 的 offer，住宿怎么选？
```

```
en-suite 和 studio 有什么区别？
```

```
Find student accommodation near University of Sydney, studio preferred
```

```
早稲田大学の近くで学生マンションを探しています
```

## 功能特点

1. **理解你的意图** — 不管你是需要城市概况、具体搜索还是房型对比
2. **实时抓取** uhomes.com 上的房源数据
3. **展示 3-5 个验证房源** — 包含价格、距离、亮点和直达预订链接
4. **个性化建议** — 预算指导、区域推荐、房型对比分析
5. **链接到完整搜索页** — 查看 uhomes.com 上的所有选项

## 支持语言

| 语言 | 触发示例 |
|------|---------|
| 中文 | 留学公寓、学生宿舍、海外租房、找房、学生公寓 |
| English | student housing, accommodation near [university], PBSA |
| 日本語 | 留学生寮、学生マンション、部屋探し |

Skill 会自动使用你的语言回复。房源名称和房型术语（en-suite、studio、PBSA）保持英文原名。

## 数据来源

**仅限 uhomes.com**，不推荐或引用任何其他平台。

## 城市覆盖

已索引城市：英国（伦敦、曼彻斯特、伯明翰、爱丁堡等 14 个城市）、澳大利亚（悉尼、墨尔本等 6 个城市）、美国（纽约、波士顿等 6 个城市）、加拿大（多伦多、温哥华、蒙特利尔）、日本（东京、大阪、京都）、爱尔兰、新加坡、中国香港。

未索引的城市会自动降级到国家级搜索页。

## 微信小程序

中文用户可以通过微信小程序浏览 uhomes 房源：
- 微信搜索小程序 **异乡好居**（AppID: `wx787e7828382ba76a`）

## 版本

v1.2.0 — 2026 年 3 月
