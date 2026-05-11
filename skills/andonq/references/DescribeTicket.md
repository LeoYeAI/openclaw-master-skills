# DescribeTicket — 查看工单详情

## 触发词

- "集团工单详情"、"组织工单详情"、"查看成员工单"
- "organization ticket detail"、"describe ticket"

## 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `TicketId` | String | **是** | — | 工单 ID |
| `Region` | String | — | `ap-guangzhou` | 自动注入，无需手动传入 |
| `UinType` | Integer | 否 | — | 维度类型：`0` 集团维度 / `1` 企业维度 |

## 示例命令

```bash
# 查询工单详情
python3 {baseDir}/scripts/andon-api.py -a DescribeTicket -d '{"TicketId":"5678"}'

# 指定企业维度
python3 {baseDir}/scripts/andon-api.py -a DescribeTicket -d '{"TicketId":"5678","UinType":1}'
```

## 成功响应

```json
{
  "success": true,
  "action": "DescribeTicket",
  "data": {
    "TicketId": "5678",
    "Uin": 100001234,
    "ServiceChannel": 1,
    "ServiceChannelDisplay": "官网",
    "CreateTime": "2026-03-20 10:30:00",
    "CurrentOperator": "support_001",
    "CurrentOperatorDisplay": "张三",
    "LastStaff": "support_001",
    "LastStaffDisplay": "张三",
    "LastOperateTime": "2026-03-21 09:00:00",
    "Status": 1,
    "StatusDisplay": "处理中",
    "ExternStatus": 1,
    "ExternStatusDisplay": "处理中",
    "CompanyId": "comp_001",
    "CompanyDisplay": "某某公司",
    "Question": "CVM 实例 ins-xxx 无法启动，控制台显示异常状态",
    "Title": "CVM 实例无法启动",
    "ServiceSceneChecked": "云服务器",
    "QCloudTicketId": "QC202603201234",
    "OwnerUin": 100001234,
    "LtcId": "ltc_001",
    "PointId": "point_001",
    "Priority": 0,
    "CustomName": "某某公司",
    "QuestionStartTime": "2026-03-20 09:00:00",
    "QuestionEndTime": "",
    "CloseTime": "",
    "ServiceSceneNameList": ["云服务器", "实例管理"]
  },
  "requestId": "xxx"
}
```

> **注意**：`Data` 可能返回 `null`，需做空值判断。

## Priority 优先级映射

| Priority 值 | 显示 |
|-------------|------|
| -1 | L1 |
| 0 | L2 |
| 1 | L3 |
| 2 | L4 |

## 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `TicketId` | String | 工单 ID |
| `Uin` | Integer | 用户 UIN |
| `ServiceChannel` | Integer | 服务渠道 |
| `ServiceChannelDisplay` | String | 服务渠道显示名 |
| `CreateTime` | String | 创建时间 |
| `CurrentOperator` | String | 当前处理人 |
| `CurrentOperatorDisplay` | String | 当前处理人显示名 |
| `LastStaff` | String | 最后处理客服 |
| `LastStaffDisplay` | String | 最后处理客服显示名 |
| `LastOperateTime` | String | 最后操作时间 |
| `Status` | Integer | 状态码 |
| `StatusDisplay` | String | 状态显示名 |
| `ExternStatus` | Integer | 外部状态码 |
| `ExternStatusDisplay` | String | 外部状态显示名 |
| `CompanyId` | String | 公司 ID |
| `CompanyDisplay` | String | 公司显示名 |
| `Question` | String | 问题描述 |
| `Title` | String | 工单标题 |
| `ServiceSceneChecked` | String | 服务场景 |
| `QCloudTicketId` | String | 腾讯云工单 ID |
| `OwnerUin` | Integer | 工单所有者 UIN |
| `LtcId` | String | LTC ID |
| `PointId` | String | Point ID |
| `Priority` | Integer | 优先级，见 Priority 映射表 |
| `CustomName` | String | 客户名称 |
| `QuestionStartTime` | String | 问题开始时间 |
| `QuestionEndTime` | String | 问题结束时间 |
| `CloseTime` | String | 关闭时间 |
| `ServiceSceneNameList` | String[] | 服务场景名称列表 |

## 展示规则

工单详情**分段展示**基本信息 + 问题描述：

```
🎫 工单详情 — 5678

标题：CVM 实例无法启动
状态：处理中
优先级：L2
UIN：100001234
公司：某某公司
服务渠道：官网
服务场景：云服务器、实例管理
创建时间：2026-03-20 10:30:00
最后操作时间：2026-03-21 09:00:00
当前处理人：张三

问题描述：
CVM 实例 ins-xxx 无法启动，控制台显示异常状态
```

- 分段展示基本信息 + 问题描述
- `Priority` 按映射表显示为 L1/L2/L3/L4
- `Data` 为 `null` 时提示用户工单不存在或无权查看

## 常见错误

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| `OperationDenied.OrganizationManagerVerifyFailed` | 集团管理员验证失败 | 确认账号具备集团管理员权限 |
