# DescribeOrganizationStories — 获取集团成员的需求单列表

## 触发词

- "需求单列表"、"集团需求单"、"组织需求列表"、"成员需求"
- "organization stories"、"story list"、"member stories"

## 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `StartTime` | String | **是** | — | 起始时间，格式 `2006-01-02 15:04:05` |
| `EndTime` | String | **是** | — | 结束时间，格式 `2006-01-02 15:04:05` |
| `Offset` | Integer | **是** | — | 偏移量 |
| `Limit` | Integer | **是** | — | 每页条数，最大 50 |
| `Title` | String | 否 | — | 需求单标题搜索 |
| `Statues` | Integer[] | 否 | — | 状态过滤（注意：API 拼写为 `Statues`） |
| `MemberUins` | Integer[] | 否 | — | 集团成员 UIN 列表 |
| `UinType` | Integer | 否 | — | 维度类型：`0` 集团维度 / `1` 企业维度 |
| `SceneIds` | Integer[] | 否 | — | 场景 ID 过滤 |
| `Ids` | Integer[] | 否 | — | 需求单 ID 过滤 |

## 示例命令

```bash
# 先获取最近 90 天的时间范围
python3 {baseDir}/scripts/andon-api.py -a GetCurrentTime -d '{}'
# 用返回的 presets.last_180d 的 startTime/endTime 填入以下命令

# 查询需求单列表
python3 {baseDir}/scripts/andon-api.py -a DescribeOrganizationStories -d '{"StartTime":"<last_180d.startTime>","EndTime":"<last_180d.endTime>","Offset":0,"Limit":20}'

# 按标题搜索
python3 {baseDir}/scripts/andon-api.py -a DescribeOrganizationStories -d '{"StartTime":"<last_180d.startTime>","EndTime":"<last_180d.endTime>","Offset":0,"Limit":20,"Title":"CDN"}'

# 按成员和状态过滤
python3 {baseDir}/scripts/andon-api.py -a DescribeOrganizationStories -d '{"StartTime":"<last_180d.startTime>","EndTime":"<last_180d.endTime>","Offset":0,"Limit":10,"MemberUins":[100001234],"Statues":[1]}'
```

## 成功响应

```json
{
  "success": true,
  "action": "DescribeOrganizationStories",
  "data": {
    "Stories": [
      {
        "CreateTime": "2026-03-15 14:00:00",
        "Status": 1,
        "StoryId": "9012",
        "Title": "CDN 支持自定义缓存策略",
        "Uin": 100001234
      }
    ],
    "Total": 8
  },
  "requestId": "xxx"
}
```

## 展示规则

需求单列表以**表格**形式展示：

```
📋 需求单列表（共 8 条）

| 需求单 ID | 标题                     | 状态    | 创建时间            | UIN        |
|-----------|------------------------|---------|-------------------|------------|
| 9012      | CDN 支持自定义缓存策略     | 处理中   | 2026-03-15 14:00  | 100001234  |
```

- 表格展示需求单列表，含需求单 ID、标题、状态、创建时间、UIN

## 常见错误

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| `FailedOperation` | 操作失败 | 检查请求参数和权限 |
| `InternalError` | 内部错误 | 稍后重试 |
| `InvalidParameter` | 参数格式错误 | 检查时间格式、Limit 是否超过 50 等 |
| `InvalidParameterValue` | 参数值错误 | 检查参数值是否在合法范围内 |
| `OperationDenied.OrganizationManagerVerifyFailed` | 集团管理员验证失败 | 确认账号具备集团管理员权限 |
