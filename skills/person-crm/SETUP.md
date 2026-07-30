# Setup Guide — Personal CRM

This guide helps you create the required Feishu/Lark Bitable tables for the Personal CRM skill.

## Step 1: Create a Bitable

1. Open [Feishu](https://www.feishu.cn) or [Lark](https://www.larksuite.com)
2. Create a new Bitable (多维表格)
3. Note the `app_token` from the URL: `https://xxx.feishu.cn/base/{app_token}`

## Step 2: Create the Contacts Table (联系人表)

Create a table with these fields:

| Field Name | Type | Options / Notes |
|-----------|------|-----------------|
| Personal CRM | Text | Primary field — stores the person's name |
| 关系 | SingleSelect | 家人, 女朋友, 朋友, 同事, 领导, 客户, 合作伙伴, 导师, 其他 |
| 手机 | Phone | |
| 微信 | Text | |
| 邮箱 | Text | |
| 城市 | Text | |
| 公司 | Text | |
| 职位 | Text | |
| 生日 | DateTime | Format: yyyy-MM-dd |
| 农历生日 | Text | e.g. "1997年九月十三" (Chinese lunar date) |
| 过农历生日 | Checkbox | Check if this person celebrates lunar birthday |
| 纪念日 | DateTime | Format: yyyy-MM-dd |
| 纪念日说明 | Text | e.g. "恋爱纪念日" |
| 提醒提前天数 | Number | Integer, default 3 |
| 爱好 | MultiSelect | Add options as needed |
| 标签 | MultiSelect | Add options as needed |
| 备注 | Text | Free-form notes |
| 最后联系 | DateTime | Format: yyyy-MM-dd |
| 联系频率 | SingleSelect | 每周, 每月, 每季度, 偶尔 |

The "创建时间" (CreatedTime) field is auto-created by Bitable.

## Step 3: Create the Interactions Table (互动记录表)

Create a second table in the same Bitable:

| Field Name | Type | Options / Notes |
|-----------|------|-----------------|
| 多行文本 | Text | Primary field — brief event summary |
| 联系人 | Text | Person's name |
| 日期 | DateTime | Format: yyyy-MM-dd |
| 类型 | SingleSelect | 见面, 通话, 消息, 会议, 吃饭, 邮件 |
| 要点 | Text | What happened, stories, details |
| 后续 | Text | Follow-up actions |
| 氛围 | SingleSelect | 开心, 平淡, 深入, 紧张, 感动, 尴尬 |
| 费用 | Number | Expense amount |

## Step 4: Configure OpenClaw

Note the `table_id` for each table from the URL: `?table={table_id}`

Add to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "personal-crm": {
        "enabled": true,
        "config": {
          "app_token": "YOUR_APP_TOKEN",
          "contacts_table_id": "YOUR_CONTACTS_TABLE_ID",
          "interactions_table_id": "YOUR_INTERACTIONS_TABLE_ID"
        }
      }
    }
  }
}
```

## Step 5: Set Up Daily Reminders (Optional)

Create a cron job for birthday/anniversary/contact reminders:

```bash
openclaw cron add \
  --name "Personal CRM Reminders" \
  --cron "0 9 * * *" \
  --tz "Your/Timezone" \
  --session isolated \
  --no-deliver \
  --timeout-seconds 120 \
  --message 'Check Personal CRM for birthday/anniversary reminders and overdue contacts. Send results via message tool to the configured channel.'
```

## Feishu App Permissions

Make sure your Feishu app has these scopes:
- `bitable:app` — Read/write Bitable data
- `bitable:app:readonly` — Read Bitable data (minimum for reminders)
