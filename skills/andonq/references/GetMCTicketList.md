# GetMCTicketList — 查询工单列表

## 触发词

- "查询工单"、"工单列表"、"我的工单"、"看看工单"、"有哪些工单"
- "list tickets"、"my tickets"、"ticket list"

## 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `StatusIdList` | int[] | 否 | 不传（全部状态） | 状态过滤，见下表 |
| `StartTime` | string | 否 | — | 起始时间，格式 `YYYY-MM-DD` |
| `EndTime` | string | 否 | — | 结束时间，格式 `YYYY-MM-DD` |
| `Search` | string | 否 | — | 关键词搜索（匹配工单标题/内容） |
| `OrderField` | string | 否 | `CreateTime` | 排序字段 |
| `Order` | string | 否 | `desc` | 排序方向：`desc` 降序 / `asc` 升序 |
| `Page` | int | 否 | `1` | 页码 |
| `PageSize` | int | 否 | `20` | 每页条数 |
| `Filters` | object[] | 否 | — | 高级过滤条件，见下方说明 |

## 工单状态

接口返回的工单数据中包含中文状态名字段，展示时直接使用返回的状态名，无需自行映射 StatusId。

`StatusIdList` 过滤参数仍使用数字 ID（如 `[0,1]` 表示待处理+处理中）。

## Filters 高级过滤

`Filters` 数组中每个元素格式：

```json
{"Name": "TicketId", "Values": ["202603244502"]}
```

支持的 Filter Name：
- `TicketId` — 按工单 ID 精确匹配
- `Product` — 按产品名过滤
- `Question` — 按问题描述模糊匹配

## 示例命令

```bash
# 查询最近 20 条工单（默认）
python3 {baseDir}/scripts/andon-api.py -a GetMCTicketList -d '{}'

# 按状态过滤（待处理 + 处理中）
python3 {baseDir}/scripts/andon-api.py -a GetMCTicketList -d '{"StatusIdList":[0,1]}'

# 关键词搜索 + 分页
python3 {baseDir}/scripts/andon-api.py -a GetMCTicketList -d '{"Search":"CVM","Page":1,"PageSize":10}'

# 时间范围查询（先用 GetCurrentTime 获取最近 90 天的时间范围）
python3 {baseDir}/scripts/andon-api.py -a GetCurrentTime -d '{}'
# 用返回的 presets.last_180d 的 startTime/endTime 填入
python3 {baseDir}/scripts/andon-api.py -a GetMCTicketList -d '{"StartTime":"<last_180d.startTime>","EndTime":"<last_180d.endTime>"}'
```

## 成功响应

```json
{
  "success": true,
  "action": "GetMCTicketList",
  "data": {
    "tickets": [
      {
        "TicketId": "202603244502",
        "Question": "CVM 无法登录",
        "StatusId": 1,
        "CreateTime": "2026-03-24 10:30:00",
        "Product": "云服务器 CVM"
      }
    ],
    "total": 15,
    "toBeAddCount": 2,
    "toConfirmCount": 1
  },
  "requestId": "xxx"
}
```

## 展示规则

工单列表以**表格**形式展示：

```
📋 工单列表（共 15 条，第 1 页）

| 工单 ID        | 问题描述              | 状态    | 创建时间            |
|---------------|---------------------|---------|-------------------|
| 202603244502  | CVM 无法登录          | 处理中   | 2026-03-24 10:30  |
| 202603243101  | COS 跨域配置问题       | 待处理   | 2026-03-23 15:20  |

待补充：2 条 | 待确认：1 条
```

- 状态显示中文名（参考状态码映射表）
- `toBeAddCount > 0` 时提示用户有工单需要补充信息
- `toConfirmCount > 0` 时提示用户有工单待确认

## 常见错误

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| `AuthFailure` | AK/SK 不正确或已过期 | 检查密钥配置 |
| `InvalidParameter` | 参数格式错误 | 检查 StatusIdList、时间格式等 |
| `RequestLimitExceeded` | 请求频率超限 | 降低调用频率 |
