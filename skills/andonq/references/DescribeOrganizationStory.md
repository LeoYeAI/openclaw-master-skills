# DescribeOrganizationStory — 获取需求单详情

## 触发词

- "需求单详情"、"查看需求单"、"需求进展"
- "story detail"、"describe story"

## 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `StoryId` | Integer | **是** | — | 需求单 ID |

## 示例命令

```bash
# 查询需求单详情
python3 {baseDir}/scripts/andon-api.py -a DescribeOrganizationStory -d '{"StoryId":9012}'
```

## 成功响应

```json
{
  "success": true,
  "action": "DescribeOrganizationStory",
  "data": {
    "Story": {
      "StoryId": "9012",
      "Title": "CDN 支持自定义缓存策略",
      "Uin": 100001234,
      "Status": 1,
      "SceneId": 10,
      "SceneName": "CDN",
      "CreateTime": "2026-03-15 14:00:00",
      "ExpectedTime": "2026-06-01 00:00:00",
      "Comments": [
        {
          "StoryId": "9012",
          "Content": "已收到需求，评估中[br]预计下个版本支持",
          "CreateTime": "2026-03-16 10:00:00",
          "CustomerName": "张三"
        },
        {
          "StoryId": "9012",
          "Content": "请问能否支持正则匹配？[br]附截图：[img]https://example.com/screenshot.png[/img]",
          "CreateTime": "2026-03-17 15:30:00",
          "CustomerName": "李四"
        }
      ]
    }
  },
  "requestId": "xxx"
}
```

## 响应字段说明

### Story 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `StoryId` | String | 需求单 ID |
| `Title` | String | 需求单标题 |
| `Uin` | Integer | 用户 UIN |
| `Status` | Integer | 需求单状态 |
| `SceneId` | Integer | 场景 ID |
| `SceneName` | String | 场景名称 |
| `CreateTime` | String | 创建时间 |
| `ExpectedTime` | String | 预期完成时间 |
| `Comments` | Array | 评论列表 |

### Comment 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `StoryId` | String | 需求单 ID |
| `Content` | String | 评论内容，支持 `[br]` 和 `[img]` 标签 |
| `CreateTime` | String | 评论时间 |
| `CustomerName` | String | 评论人名称 |

## 展示规则

需求单详情**分段展示**基本信息 + 评论列表：

```
📄 需求单详情 — 9012

标题：CDN 支持自定义缓存策略
状态：处理中
UIN：100001234
场景：CDN
创建时间：2026-03-15 14:00:00
预期完成时间：2026-06-01 00:00:00

--- 评论记录 ---

[张三] 2026-03-16 10:00
已收到需求，评估中
预计下个版本支持

[李四] 2026-03-17 15:30
请问能否支持正则匹配？
附截图：https://example.com/screenshot.png
```

- 分段展示基本信息 + 评论列表
- 评论 `Content` 中的 `[br]` 转换为换行
- 评论 `Content` 中的 `[img]...[/img]` 提取为图片链接展示
- 评论按时间顺序展示

## 常见错误

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| `FailedOperation` | 操作失败 | 检查请求参数和权限，确认需求单 ID 存在 |
