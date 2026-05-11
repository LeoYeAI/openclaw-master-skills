# DescribeOrganizationTickets — 获取集团成员的工单列表

## 触发词

- "集团工单"、"组织工单列表"、"成员工单"、"集团工单列表"
- "organization tickets"、"member tickets"

## 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `StartTime` | String | **是** | — | 起始时间，格式 `2006-01-02 15:04:05` |
| `EndTime` | String | **是** | — | 结束时间，格式 `2006-01-02 15:04:05` |
| `Offset` | Integer | **是** | — | 偏移量 |
| `Limit` | Integer | **是** | — | 每页条数，最大 50 |
| `MemberUins` | Integer[] | 否 | — | 集团成员 UIN 列表 |
| `Title` | String | 否 | — | 工单标题搜索 |
| `Statues` | Integer[] | 否 | — | 工单状态过滤（注意：API 拼写为 `Statues`） |
| `Channels` | Integer[] | 否 | — | 渠道过滤，见下表 |
| `Tags` | Integer[] | 否 | — | 标签过滤 |
| `UinType` | Integer | 否 | — | 维度类型：`0` 集团维度 / `1` 企业维度 |
| `SceneIds` | Integer[] | 否 | — | 场景 ID 过滤 |
| `Ids` | Integer[] | 否 | — | 工单 ID 过滤 |
| `ServiceRates` | Integer[] | 否 | — | 服务评价过滤 |

## 渠道类型

| Channel | 含义 |
|---------|------|
| 1 | 官网 |
| 2 | 电话 |
| 3 | 大客户群 |
| 4 | 其他 |

## 示例命令

```bash
# 先获取最近 90 天的时间范围
python3 {baseDir}/scripts/andon-api.py -a GetCurrentTime -d '{}'
# 用返回的 presets.last_180d 的 startTime/endTime 填入以下命令

# 查询最近工单列表
python3 {baseDir}/scripts/andon-api.py -a DescribeOrganizationTickets -d '{"StartTime":"<last_180d.startTime>","EndTime":"<last_180d.endTime>","Offset":0,"Limit":20}'

# 按成员 UIN 过滤
python3 {baseDir}/scripts/andon-api.py -a DescribeOrganizationTickets -d '{"StartTime":"<last_180d.startTime>","EndTime":"<last_180d.endTime>","Offset":0,"Limit":20,"MemberUins":[100001234]}'

# 按状态和渠道过滤
python3 {baseDir}/scripts/andon-api.py -a DescribeOrganizationTickets -d '{"StartTime":"<last_180d.startTime>","EndTime":"<last_180d.endTime>","Offset":0,"Limit":10,"Statues":[1,2],"Channels":[1]}'
```

## 成功响应

```json
{
  "success": true,
  "action": "DescribeOrganizationTickets",
  "data": {
    "Tickets": [
      {
        "Channel": 1,
        "CreateTime": "2026-03-20 10:30:00",
        "QcloudTicketId": "QC202603201234",
        "Status": 1,
        "TicketId": "5678",
        "Title": "CVM 实例无法启动",
        "Uin": 100001234
      }
    ],
    "Total": 15
  },
  "requestId": "xxx"
}
```

## 展示规则

工单列表以**表格**形式展示：

```
📋 集团工单列表（共 15 条）

| 工单 ID | 标题                | 状态    | 创建时间            | UIN        |
|---------|-------------------|---------|-------------------|------------|
| 5678    | CVM 实例无法启动     | 处理中   | 2026-03-20 10:30  | 100001234  |
```

- 表格展示工单列表，含工单 ID、标题、状态、创建时间、UIN
- 渠道显示中文名（参考渠道类型映射表）

## 常见错误

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| `FailedOperation` | 操作失败 | 检查请求参数和权限 |
| `InternalError` | 内部错误 | 稍后重试 |
| `InvalidParameter` | 参数格式错误 | 检查时间格式、Limit 是否超过 50 等 |
| `InvalidParameterValue` | 参数值错误 | 检查参数值是否在合法范围内 |
| `OperationDenied.OrganizationManagerVerifyFailed` | 集团管理员验证失败 | 确认账号具备集团管理员权限 |
