# DescribeTicketOperation — 查询工单流水

## 触发词

- "工单流水"、"工单操作历史"、"工单记录"、"工单操作记录"
- "ticket operations"、"ticket history"、"ticket log"

## 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `TicketId` | Integer | **是** | — | 工单 ID |
| `Region` | String | — | `ap-guangzhou` | 自动注入，无需手动传入 |
| `Offset` | Integer | 否 | — | 偏移量 |
| `Limit` | Integer | 否 | — | 每页条数 |
| `UinType` | Integer | 否 | — | 维度类型：`0` 集团维度 / `1` 企业维度 |

## 操作类型

| OperationType | 含义 |
|---------------|------|
| 3 | 认领 |
| 5 | 转单 |
| 6 | 派单 |
| 8 | 回复 |

## 操作人类型

| OperatorType | 含义 |
|--------------|------|
| 2 | 客服 |
| 3 | 系统 |

## HasSecret 标识

| HasSecret | 含义 |
|-----------|------|
| 0 | 否 |
| 1 | 是 |

## 示例命令

```bash
# 查询工单流水
python3 {baseDir}/scripts/andon-api.py -a DescribeTicketOperation -d '{"TicketId":5678}'

# 分页查询
python3 {baseDir}/scripts/andon-api.py -a DescribeTicketOperation -d '{"TicketId":5678,"Offset":0,"Limit":10}'

# 指定企业维度
python3 {baseDir}/scripts/andon-api.py -a DescribeTicketOperation -d '{"TicketId":5678,"UinType":1}'
```

## 成功响应

```json
{
  "success": true,
  "action": "DescribeTicketOperation",
  "data": {
    "Total": 3,
    "TicketId": "5678",
    "TicketOperationInfoList": [
      {
        "TicketId": "5678",
        "OperationId": "op_001",
        "Operator": "support_001",
        "OperatorType": 2,
        "OperateTime": "2026-03-20 10:35:00",
        "OperationType": 3,
        "OperationTypeDisplay": "认领",
        "ExternReply": "",
        "InnerReply": "",
        "Remark": "客服认领工单",
        "HasSecret": 0
      },
      {
        "TicketId": "5678",
        "OperationId": "op_002",
        "Operator": "support_001",
        "OperatorType": 2,
        "OperateTime": "2026-03-20 11:00:00",
        "OperationType": 8,
        "OperationTypeDisplay": "回复",
        "ExternReply": "您好，请检查安全组配置",
        "InnerReply": "",
        "Remark": "",
        "HasSecret": 0
      },
      {
        "TicketId": "5678",
        "OperationId": "op_003",
        "Operator": "system",
        "OperatorType": 3,
        "OperateTime": "2026-03-21 09:00:00",
        "OperationType": 5,
        "OperationTypeDisplay": "转单",
        "ExternReply": "",
        "InnerReply": "转至二线团队处理",
        "Remark": "",
        "HasSecret": 0
      }
    ]
  },
  "requestId": "xxx"
}
```

## 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `Total` | Integer | 操作记录总数 |
| `TicketId` | String | 工单 ID |
| `TicketOperationInfoList` | Array | 操作记录列表 |

### TicketOperationInfoList 元素字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `TicketId` | String | 工单 ID |
| `OperationId` | String | 操作 ID |
| `Operator` | String | 操作人 |
| `OperatorType` | Integer | 操作人类型，见上方映射表 |
| `OperateTime` | String | 操作时间 |
| `OperationType` | Integer | 操作类型，见上方映射表 |
| `OperationTypeDisplay` | String | 操作类型显示名 |
| `ExternReply` | String | 外部回复内容 |
| `InnerReply` | String | 内部回复内容 |
| `Remark` | String | 备注 |
| `HasSecret` | Integer | 是否包含敏感信息 |

## 展示规则

按**时间顺序**展示操作流水，标注操作类型和操作人：

```
📝 工单流水 — 5678（共 3 条记录）

[2026-03-20 10:35] 认领 — 客服 support_001
  备注：客服认领工单

[2026-03-20 11:00] 回复 — 客服 support_001
  回复内容：您好，请检查安全组配置

[2026-03-21 09:00] 转单 — 系统
  内部备注：转至二线团队处理
```

- 按时间顺序展示操作流水
- 标注操作类型（认领/转单/派单/回复）和操作人
- 操作人类型为客服时显示"客服"，为系统时显示"系统"
- `ExternReply` 不为空时展示为"回复内容"
- `InnerReply` 不为空时展示为"内部备注"
- `HasSecret` 为 1 时提示该记录包含敏感信息

## 常见错误

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| `OperationDenied.OrganizationManagerVerifyFailed` | 集团管理员验证失败 | 确认账号具备集团管理员权限 |
