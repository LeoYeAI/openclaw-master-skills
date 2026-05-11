# ListDirectoryV2 — 新版目录查询

查询云架构图的目录树结构。

## 参数

| 参数 | 必选 | 类型 | 描述 |
|------|------|------|------|
| FolderId | 否 | Integer | 目录 ID |
| ShareStatus | 否 | String | 共享状态 |
| SearchKey | 否 | String | 模糊搜索关键词 |

## 调用示例

```bash
# 查询全部目录
python3 {baseDir}/scripts/tcloud_api.py \
  advisor \
  advisor.tencentcloudapi.com \
  ListDirectoryV2 \
  2020-07-21 \
  '{}'

# 按关键词搜索目录
python3 {baseDir}/scripts/tcloud_api.py \
  advisor \
  advisor.tencentcloudapi.com \
  ListDirectoryV2 \
  2020-07-21 \
  '{"SearchKey":"arch"}'
```

## 返回示例

```json
{
  "success": true,
  "action": "ListDirectoryV2",
  "data": {
    "FirstFolderId": 1,
    "Folders": [
      {
        "Id": 1,
        "Name": "folder",
        "Type": "Directory",
        "FolderTypeId": 2,
        "Children": []
      }
    ]
  },
  "requestId": "909d6e2b-..."
}
```
