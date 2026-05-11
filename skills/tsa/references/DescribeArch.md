# DescribeArch — 获取云架构详情

获取指定云架构图的详细信息，包括名称、SVG 数据、节点列表、绑定资源等。

## 参数

| 参数 | 必选 | 类型 | 描述 |
|------|------|------|------|
| ArchId | 是 | String | 云架构 ID，如 `arch-jcxtbe9t` |
| Username | 是 | String | 用户名，用于记录最近访问 |
| VersionId | 否 | Integer | 版本 ID，不传默认获取最新版 |
| SvgType | 否 | String | SVG 类型，默认 `3D`，可指定为 `2D` |
| WithoutDetail | 否 | Boolean | 是否不返回 detail 数据，默认 `false` |

## 调用示例

```bash
python3 {baseDir}/scripts/tcloud_api.py \
  advisor \
  advisor.tencentcloudapi.com \
  DescribeArch \
  2020-07-21 \
  '{"ArchId":"arch-jcxtbe9t","Username":"user1"}'
```

## 返回示例

```json
{
  "success": true,
  "action": "DescribeArch",
  "data": {
    "Arch": {
      "ArchId": "arch-jcxtbe9t",
      "ArchName": "架构图1",
      "FolderId": 123,
      "CreateTime": "2023-11-14 10:29:04",
      "VersionName": "版本1",
      "VersionId": 76,
      "NodeList": [
        {
          "DiagramId": "ddd",
          "NodeName": "CVM节点",
          "ProductType": "CVM",
          "ResourceList": [
            {"InstanceId": "ins-j7uxx5im", "Attributes": "aaa"}
          ]
        }
      ]
    }
  },
  "requestId": "b90a5cc7-..."
}
```

## 免密登录链接规则

返回结果包含架构图时，**必须**调用免密登录脚本为该架构图生成控制台直达链接（见 SKILL.md 第五章），架构图页面 URL 格式为：
`https://console.cloud.tencent.com/advisor?archId={ArchId}`

生成链接后，以 Markdown 超链接形式展示给用户：`[跳转控制台](免密登录URL)`，不要直接展示完整 URL。

> **⚠️ 注意**：免密登录链接**每次都必须重新生成**，不可缓存或复用之前生成的链接。每次向用户展示架构图信息时，都必须重新调用 `login_url.py` 生成新的链接。
