# GetMCTicketById — 查询工单详情

## 触发词

- "工单详情"、"查看工单"、"工单进展"、"工单状态"、"这个工单怎么样了"
- "ticket detail"、"ticket status"、"check ticket"

## 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `TicketId` | string | **是** | — | 工单 ID（如 `202603244502`） |
| `ReturnCosUrl` | bool | 否 | — | 是否返回附件的 COS 签名 URL |
| `IsPage` | bool | 否 | — | 是否分页返回评论 |
| `Page` | int | 否 | `1` | 评论页码 |
| `PageSize` | int | 否 | `20` | 每页评论条数 |
| `Sort` | string | 否 | `desc` | 评论排序：`desc` 最新在前 / `asc` 最早在前 |

## 示例命令

```bash
# 查询工单详情
python3 {baseDir}/scripts/andon-api.py -a GetMCTicketById -d '{"TicketId":"202603244502"}'

# 包含附件 URL
python3 {baseDir}/scripts/andon-api.py -a GetMCTicketById -d '{"TicketId":"202603244502","ReturnCosUrl":true}'

# 评论分页（第 2 页，每页 5 条）
python3 {baseDir}/scripts/andon-api.py -a GetMCTicketById -d '{"TicketId":"202603244502","IsPage":true,"Page":2,"PageSize":5}'
```

## 成功响应

```json
{
  "success": true,
  "action": "GetMCTicketById",
  "data": {
    "TicketId": "202603244502",
    "Question": "CVM 无法登录",
    "Content": "我的 CVM 实例 ins-xxx 无法通过 SSH 登录，报错 Connection refused",
    "StatusId": 1,
    "CreateTime": "2026-03-24 10:30:00",
    "UpdateTime": "2026-03-24 14:00:00",
    "Product": "云服务器 CVM",
    "LevelId": 2,
    "Comments": [
      {
        "Content": "您好，请检查安全组是否放通 22 端口",
        "Role": "support",
        "CreateTime": "2026-03-24 11:00:00"
      },
      {
        "Content": "已检查，安全组已放通",
        "Role": "customer",
        "CreateTime": "2026-03-24 12:30:00"
      }
    ]
  },
  "requestId": "xxx"
}
```

## 工单状态

接口返回的工单数据中包含中文状态名字段，展示时直接使用返回的状态名，无需自行映射 StatusId。

## 展示规则

工单详情分段展示：

```
🎫 工单详情 — 202603244502

状态：处理中
产品：云服务器 CVM
创建时间：2026-03-24 10:30:00
最后更新：2026-03-24 14:00:00

问题描述：
我的 CVM 实例 ins-xxx 无法通过 SSH 登录，报错 Connection refused

--- 沟通记录 ---

[客服] 2026-03-24 11:00
您好，请检查安全组是否放通 22 端口

[用户] 2026-03-24 12:30
已检查，安全组已放通
```

- 状态显示中文名（参考状态码映射表）
- `Comments` 按时间顺序展示，标注角色（客服/用户）
- 如有附件（`ReturnCosUrl=true`），展示为可点击链接
- 若 `StatusId == 7`（待补充），提醒用户需要补充信息

## 常见错误

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| `AuthFailure` | AK/SK 不正确或已过期 | 检查密钥配置 |
| `ResourceNotFound` | 工单 ID 不存在 | 检查工单 ID 是否正确 |
| `InvalidParameter` | 参数格式错误 | 检查 TicketId 格式 |
