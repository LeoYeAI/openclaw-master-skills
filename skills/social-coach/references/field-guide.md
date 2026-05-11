# 记录字段详细说明

## 邀约记录 (invitations.jsonl)

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| id | string | 自动生成，格式 INV-NNN | INV-001 |
| date | string | YYYY-MM-DD | 2026-05-03 |
| target | string | 对象代号，不要用真名 | 徒步女生 |
| familiarity | enum | 初次 / 见过1-2次 / 较熟 / 很熟 | 见过1-2次 |
| method | enum | 线上 / 线下 / 电话 | 线上 |
| content | string | 邀约的具体话术或描述行为 | 周末一起去爬山？ |
| response | enum | 接受 / 拒绝 / 推迟 / 模糊 / 未回应 | 接受 |
| selfScore | number | 自我感受 1-10 | 7 |
| keyPoint | string | 用户自评的关键点 | 共同兴趣切入效果很好 |
| note | string | AI 补充分析 | 话术自然无压力 |

## 接触记录 (interactions.jsonl)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | INT-NNN |
| date | string | YYYY-MM-DD |
| type | enum | 破冰 / 接触 / 心态记录 |
| scene | string | 场景描述 |
| target | string | 对象代号（心态记录可为空） |
| myAction | string | 你的话术/行为 |
| theirReaction | string | 对方反应 |
| selfScore | number | 1-10 |
| isSimulated | boolean | true=模拟 false=真实 |

## 会话记录 (conversations.jsonl)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | CONV-NNN |
| date | string | YYYY-MM-DD |
| type | enum | 模拟 / 真实复盘 |
| target | string | 对象代号 |
| summary | string | 会话摘要 |
| similarityScore | number | 用户标记的模拟相似度 1-5（仅模拟） |
| rhythmAnalysis | string | 节奏分析 |
| missedOpportunities | array | 错失的深度连接机会 |

## 复盘记录 (reviews.jsonl)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | REV-NNN |
| date | string | YYYY-MM-DD |
| invitationId | string | 关联的邀约 ID |
| overallScore | number | 综合评分 1-10 |
| responseScore | number | 对方回应质量 1-10 |
| performanceScore | number | 你的表现 1-10 |
| scriptScore | number | 话术合理性 1-10 |
| strengths | array | 值得保持的优点 |
| improvements | array | 改进建议 |
| progressNote | string | 进步趋势说明 |
