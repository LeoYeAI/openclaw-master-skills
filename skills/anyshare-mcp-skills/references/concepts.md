# AnyShare 核心概念参考

> 完整概念说明——SKILL.md 中仅保留速查，详细信息在此文件备用。

## docid vs id

概念：`docid = gns://<库ID>/<父目录ID>/.../<id>`，其中 **最后一段**为 **id**。

下面用**纯 ASCII 示例**画对齐（避免中英混排导致等宽字体下箭头错位）：

```
gns://E6D15886/A51FA4844/2DDD46B195F24BCEB238DB59151CD15E
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                         id（最后一段）
```

| 字段 | 是什么 | 示例 |
|------|--------|------|
| **docid** | 完整路径，gns:// 开头 | `gns://E6D15886.../A51FA4844.../2DDD46B195F24BCEB238DB59151CD15E` |
| **id** | docid 的最后一段 | `2DDD46B195F24BCEB238DB59151CD15E` |
| **parent_path** | docid 去掉最后一段 | `gns://E6D15886.../A51FA4844.../` |

**传参规则（工具调用时）：**

| 工具 | 参数 | 传什么 |
|------|------|--------|
| `chat_send` | `source_ranges[].id` | **id**（最后一段） |
| `folder_sub_objects` | `id` | **完整 docid** |
| `file_osdownload` | `docid` | **完整 docid** |
| `file_upload` | `docid` | **完整 docid**（目标目录） |
| `file_convert_path` | `docid` | **完整 docid**（仅用于展示 namepath） |
| `file_search` | — | 不需要手动拼接 |

## sharedlink 解析

分享链接格式：`https://anyshare.aishu.cn/link/AR...`

点击后重定向到含参数的 URL：
```
https://anyshare.aishu.cn/anyshare/zh-cn/link/ARXXXXX
  ?_tb=none
  &belongs_to=document
  &item_id=gns%3A%2F%2F{编码docid}
  &item_type=folder
  &type=realname
```

**解析步骤：**
1. 从 URL 提取 `item_id` 参数（已 URL 编码）
2. URL 解码 → 完整 docid
3. 取最后一段 → **id**
4. 根据 `item_type` 判断：
   - `folder` → 用 `folder_sub_objects`
   - `file` 或其他 → 直接用 id 传给 `chat_send`

## namepath 是什么

`file_convert_path(docid)` 返回的 **`namepath`** 是云盘展示用路径，如 `库名/文件夹/文件名`。**仅供阅读**，不得当作 docid 传参。

## 文件/文件夹判断

判断对象是文件还是文件夹：**看 `size = -1` 即为文件夹**（最可靠依据），而非 `doc_type` 或 `extension`。

## skill_name 枚举值

以 `mcporter list asmcp` 返回的 schema 为准，不做假设。当前已知：

- `__全文写作__2` — 生成大纲
- `__大纲写作__1` — 基于大纲生成正文
- Bot 问答（普通模式，`skill_name` 不带下划线时为 Bot 模式）
