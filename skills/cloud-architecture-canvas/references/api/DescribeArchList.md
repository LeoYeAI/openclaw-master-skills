# DescribeArchList — 获取云架构列表

分页获取云架构图列表，支持按名称、ID、关键词、文件夹、共享状态等筛选。

## 参数

| 参数 | 必选 | 类型 | 描述 |
|------|------|------|------|
| PageNumber | 是 | Integer | 页码，>0 |
| PageSize | 是 | Integer | 每页数目，>0 且 ≤100 |
| ArchId | 否 | String | 按架构图 ID 搜索 |
| ArchName | 否 | String | 按架构图名称搜索 |
| SearchKey | 否 | String | 按关键词搜索 |
| FolderId | 否 | Integer | 文件夹 ID，不传则全局搜索 |
| ShareStatus | 否 | String | 按共享状态过滤，`"true"` 或 `"false"` |
| UpdateUser | 否 | String | 按更新人过滤 |
| WithoutSvg | 否 | Boolean | 不返回 SVG 数据，默认 `false` |
| WithSvgURL | 否 | Boolean | 返回 SVG 的临时 COS URL，默认 `false` |
| OrderBy | 否 | String | 排序：`CREATE_TIME`（默认）/ `UPDATE_TIME` / `VISIT_TIME` |

## 调用示例

```bash
# 获取第一页，每页10条
python3 {baseDir}/scripts/tcloud_api.py \
  advisor \
  advisor.tencentcloudapi.com \
  DescribeArchList \
  2020-07-21 \
  '{"PageNumber":1,"PageSize":10,"WithSvgURL":true}'

# 按名称搜索
python3 {baseDir}/scripts/tcloud_api.py \
  advisor \
  advisor.tencentcloudapi.com \
  DescribeArchList \
  2020-07-21 \
  '{"PageNumber":1,"PageSize":20,"SearchKey":"生产环境"}'
```

## 返回示例

```json
{
  "success": true,
  "action": "DescribeArchList",
  "data": {
    "TotalCount": 916,
    "ArchList": [
      {
        "ArchId": "arch-xxxxxxx",
        "ArchName": "示例架构图",
        "CreateTime": "2025-10-28 17:18:38",
        "UpdateTime": "2025-10-28 18:58:04",
        "FolderId": 1598964,
        "VersionName": "1.0.0",
        "ShareStatus": false,
        "SvgURL": "https://xxxxxxxxxxx",
        "Tags": []
      }
    ]
  },
  "requestId": "9cbe807c-..."
}
```

## 免密登录链接规则

返回结果包含架构图列表时，只需为列表中的**第一张架构图**调用免密登录脚本生成控制台直达链接（见 SKILL.md 第五章），架构图页面 URL 格式为：
`https://console.cloud.tencent.com/advisor?archId={ArchId}`

生成链接后，以 Markdown 超链接形式展示给用户：`[跳转控制台](免密登录URL)`，不要直接展示完整 URL。仅第一张架构图附带超链接，其余架构图正常展示信息即可。

> **⚠️ 注意**：免密登录链接**每次都必须重新生成**，不可缓存或复用之前生成的链接。每次向用户展示架构图列表时，都必须重新调用 `login_url.py` 生成新的链接。
