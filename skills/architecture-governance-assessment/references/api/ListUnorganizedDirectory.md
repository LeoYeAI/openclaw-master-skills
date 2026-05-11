# ListUnorganizedDirectory — 查询待整理目录

查询新版目录下的待整理（未归类）目录结构。

## 参数

| 参数 | 必选 | 类型 | 描述 |
|------|------|------|------|
| FolderId | 否 | Integer | 目录 ID |
| ShareStatus | 否 | String | 架构图共享状态 |
| SearchKey | 否 | String | 查询关键词 |

## 调用示例

```bash
# 查询全部待整理目录
python3 {baseDir}/scripts/tcloud_api.py \
  advisor \
  advisor.tencentcloudapi.com \
  ListUnorganizedDirectory \
  2020-07-21 \
  '{}'
```

## 返回示例

```json
{
  "success": true,
  "action": "ListUnorganizedDirectory",
  "data": {
    "Folders": [
      {
        "Id": 12,
        "Name": "folder1",
        "Type": "Directory",
        "Children": [
          {
            "Id": 13,
            "Name": "folder2",
            "Type": "Directory",
            "Children": [
              {"Id": 14, "Name": "folder4", "Type": "Directory"}
            ]
          }
        ]
      }
    ]
  },
  "requestId": "xxxx-xxxx-xxxx-xxxx"
}
```
