---
name: amemo-send-task
description: 由 amemo-save-task 在用户确认邮箱后内部调用，将任务提醒以邮件形式发送到指定邮箱地址。
---

# amemo-send-task — 发送任务

---

## 接口信息

| 属性 | 值 |
|:-----|:---|
| **路由** | `POST https://skill.amemo.cn/send-task` |
| **Bean** | `TaskBean` |
| **Content-Type** | `application/json` |

---

## 请求参数

> ⚠️ 服务端要求所有字段必须存在。`userToken`、`taskEmail`、`taskTime` 必填且有值，其他字段可选但字段必须存在。

| 参数 | 类型 | 必填 | 说明 |
|:-----|:----:|:----:|:-----|
| `userToken` | str | ✅ | 用户登录凭证 |
| `taskId` | str | — | 要发送的任务 ID，不传则传 `null` |
| `taskTitle` | str | — | 任务标题，不传则传 `null` |
| `taskExplain` | str | — | 任务说明，不传则传 `null` |
| `taskTime` | str | ✅ | 任务时间（不能为空） |
| `taskEmail` | list[str] | ✅ | 接收通知的邮箱列表（不能为空） |

---

## 请求示例

```bash
# 发送任务通知
curl -X POST https://skill.amemo.cn/send-task \
  -H "Content-Type: application/json" \
  -d '{
    "userToken": "<token>",
    "taskId": null,
    "taskTitle": null,
    "taskExplain": null,
    "taskTime": "2025-12-31",
    "taskEmail": ["a@example.com", "b@example.com"]
  }'
```

---

## 响应示例

```json
{
  "code": 200,
  "desc": "success",
  "data": "..."
}
```

---

## 注意事项

> 📧 **邮件通知**：此接口用于将任务通知推送给指定邮箱
>
> 👥 **多人通知**：`taskEmail` 为字符串数组，可同时通知多人
>
> 🔐 **认证要求**：必须携带有效的 userToken
>
> ⚠️ **字段要求**：所有字段必须存在，即使不传值也要传 `null`

---

## 执行流程（由主模块调度）

### 邮箱格式验证

> **正则表达式：** `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

---

### 执行步骤

```
1. 接收来自 amemo-save-task 的邮件发送请求
    ↓
2. 验证邮箱格式
    ↓
3. 调用 POST /send-task 接口
    ↓
4. 返回发送结果
```

---

## 回复模板

### 邮件发送成功

```
✅ 邮件提醒已设置！
📧 接收邮箱：user@example.com
⏰ 提醒时间：2026-03-23 07:00:00

测试邮件已发送，请查收。
```

---

## 错误处理

| 异常类型 | 用户提示 |
|:---------|:--------|
| 邮箱格式错误 | `❌ 邮箱格式不正确，请重新输入` |
| 网络超时 | `网络有点慢，请稍后重试` |
| 服务繁忙 | `服务正忙，请稍后再试` |
| 未知错误 | `出了点小问题，请稍后重试` |
