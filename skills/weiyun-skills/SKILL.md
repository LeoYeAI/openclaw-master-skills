---
name: weiyun-management
license: MIT
description: >
  This skill should be used when the user needs to manage Tencent Weiyun
  cloud storage, including file upload/download, sharing, space management,
  and account authentication via QR code scanning or cookies. It provides
  a complete Python toolkit for automating Weiyun operations with CLI and
  SDK support. Trigger phrases include "upload to weiyun", "download from
  weiyun", "weiyun share", "weiyun space", "manage weiyun files",
  "weiyun login", "scan QR code", "微云管理", "微云上传", "微云下载",
  "微云分享", "微云空间", "扫码登录", "文件管理", "云存储管理",
  "微云文件", "weiyun files", "cloud storage".
---

# SKILL.md — 腾讯微云管理 Skills 定义
> **使用方法**：本文档定义了所有可用的腾讯微云管理 Skills。AI Agent 或开发者可根据此文档调用 Python 脚本完成云存储操作。
>
> **认证方式**（二选一）：
> ```bash
> # Method 1: QR code login (recommended)
> python weiyun_skills/login.py --method qrcode
>
> # Method 2: Copy cookies from browser
> python weiyun_skills/login.py --method cookies --cookies "uin=o012345678; skey=@abcdef1234; ..."
> ```
>
> **调用方式**：
> ```bash
> # CLI
> python weiyun_skills/main.py <command> [args] [options]
>
> # Python SDK
> from weiyun_skills.client import WeiyunClient
> client = WeiyunClient()
> client.<skill_name>(**params)
> ```
>
> **统一返回格式**：
> ```json
> { "success": true, "data": { ... }, "message": "ok" }
> ```

---

## 目录

- [SKILL.md — 腾讯微云管理 Skills 定义](#skillmd--腾讯微云管理-skills-定义)
  - [目录](#目录)
  - [1. 认证 Skills](#1-认证-skills)
    - [1.1 qrcode\_login — 扫码登录](#11-qrcode_login--扫码登录)
    - [1.2 cookies\_login — Cookies 登录](#12-cookies_login--cookies-登录)
  - [2. 文件管理 Skills](#2-文件管理-skills)
    - [2.1 list\_files — 列出文件](#21-list_files--列出文件)
    - [2.2 upload\_file — 上传文件](#22-upload_file--上传文件)
    - [2.3 download\_file — 下载文件](#23-download_file--下载文件)
    - [2.4 delete\_file — 删除文件](#24-delete_file--删除文件)
    - [2.5 move\_file — 移动文件](#25-move_file--移动文件)
    - [2.6 copy\_file — 复制文件](#26-copy_file--复制文件)
    - [2.7 rename\_file — 重命名](#27-rename_file--重命名)
    - [2.8 create\_folder — 创建文件夹](#28-create_folder--创建文件夹)
    - [2.9 search\_files — 搜索文件](#29-search_files--搜索文件)
  - [3. 分享管理 Skills](#3-分享管理-skills)
    - [3.1 create\_share — 创建分享](#31-create_share--创建分享)
    - [3.2 cancel\_share — 取消分享](#32-cancel_share--取消分享)
    - [3.3 list\_shares — 列出分享](#33-list_shares--列出分享)
  - [4. 空间管理 Skills](#4-空间管理-skills)
    - [4.1 get\_space\_info — 空间信息](#41-get_space_info--空间信息)
    - [4.2 get\_recycle\_bin — 回收站](#42-get_recycle_bin--回收站)
    - [4.3 restore\_file — 恢复文件](#43-restore_file--恢复文件)
    - [4.4 clear\_recycle\_bin — 清空回收站](#44-clear_recycle_bin--清空回收站)
  - [附录 A：统一错误码](#附录-a统一错误码)
  - [附录 B：Cookies 关键字段说明](#附录-bcookies-关键字段说明)

---

## 1. 认证 Skills

### 1.1 qrcode_login — 扫码登录

**描述**：生成腾讯微云登录二维码，用户使用微信/QQ 扫码完成认证。登录成功后自动保存 Cookies 到 `cookies.json`。

**CLI**：

```bash
python weiyun_skills/login.py --method qrcode
```

**Python**：

```python
from weiyun_skills.login import qrcode_login

cookies = qrcode_login()
# Terminal will display QR code, scan with WeChat/QQ
# After success, cookies are saved to cookies.json
```

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `save_path` | `string` | ❌ | `cookies.json` | Cookies 保存路径 |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `success` | `boolean` | 是否登录成功 |
| `uin` | `string` | 用户 UIN |
| `nickname` | `string` | 用户昵称 |
| `cookies_str` | `string` | Cookies 字符串 |
| `save_path` | `string` | Cookies 保存路径 |

**流程**：

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Request QR  │────▶│ Display QR   │────▶│ User scans  │
│ code URL    │     │ in terminal  │     │ with WeChat  │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
┌─────────────┐     ┌──────────────┐             │
│ Save to     │◀────│ Get cookies  │◀────────────┘
│ cookies.json│     │ from server  │
└─────────────┘     └──────────────┘
```

---

### 1.2 cookies_login — Cookies 登录

**描述**：使用从浏览器复制的 Cookies 字符串完成登录认证。

**CLI**：

```bash
python weiyun_skills/login.py --method cookies --cookies "uin=o012345678; skey=@abcdef1234; p_uin=o012345678; pt4_token=xxxxx; p_skey=xxxxx"
```

**Python**：

```python
from weiyun_skills.login import cookies_login

cookies = cookies_login(
    cookies_str="uin=o012345678; skey=@abcdef1234; ..."
)
```

**如何获取 Cookies**：

1. 打开浏览器访问 https://www.weiyun.com/ 并登录
2. 按 `F12` 打开开发者工具
3. 切换到 `Network`（网络）标签页
4. 刷新页面，点击任意一个请求
5. 在 `Headers`（请求头）中找到 `Cookie` 字段
6. 复制完整的 Cookie 值

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `cookies_str` | `string` | ✅ | - | 从浏览器复制的 Cookie 字符串 |
| `save_path` | `string` | ❌ | `cookies.json` | Cookies 保存路径 |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `success` | `boolean` | 是否验证成功 |
| `uin` | `string` | 用户 UIN |
| `nickname` | `string` | 用户昵称 |
| `save_path` | `string` | Cookies 保存路径 |

---

## 2. 文件管理 Skills

### 2.1 list_files — 列出文件

**描述**：列出微云指定目录下的所有文件和文件夹。

**CLI**：

```bash
python weiyun_skills/main.py list /
python weiyun_skills/main.py list /我的文档 --sort size --order desc
```

**Python**：

```python
files = client.list_files("/我的文档", sort_by="size", sort_order="desc")
```

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `remote_path` | `string` | ❌ | `/` | 目录路径，默认根目录 |
| `sort_by` | `string` | ❌ | `name` | 排序字段：`name`/`size`/`time` |
| `sort_order` | `string` | ❌ | `asc` | 排序方向：`asc`/`desc` |
| `page` | `integer` | ❌ | `1` | 分页页码 |
| `page_size` | `integer` | ❌ | `100` | 每页数量 |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `files` | `array` | 文件列表 |
| `files[].file_id` | `string` | 文件唯一 ID |
| `files[].name` | `string` | 文件名 |
| `files[].type` | `string` | `file` 或 `folder` |
| `files[].size` | `integer` | 大小（字节） |
| `files[].size_str` | `string` | 可读大小（如 `2.5 MB`） |
| `files[].path` | `string` | 完整路径 |
| `files[].updated_at` | `string` | 最后修改时间 |
| `total` | `integer` | 总数量 |

**示例输出**：

```json
{
  "success": true,
  "data": {
    "files": [
      {
        "file_id": "f_abc123",
        "name": "report.pdf",
        "type": "file",
        "size": 2621440,
        "size_str": "2.5 MB",
        "path": "/我的文档/report.pdf",
        "updated_at": "2026-03-15 10:30:00"
      },
      {
        "file_id": "d_folder01",
        "name": "照片",
        "type": "folder",
        "size": 0,
        "size_str": "-",
        "path": "/我的文档/照片",
        "updated_at": "2026-03-14 08:00:00"
      }
    ],
    "total": 2
  },
  "message": "ok"
}
```

---

### 2.2 upload_file — 上传文件

**描述**：将本地文件上传到微云指定目录。支持大文件分片上传。

**CLI**：

```bash
python weiyun_skills/main.py upload ./report.pdf /我的文档/
python weiyun_skills/main.py upload ./big_video.mp4 /视频/ --overwrite
```

**Python**：

```python
result = client.upload_file("./report.pdf", "/我的文档/report.pdf", overwrite=True)
```

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `local_path` | `string` | ✅ | - | 本地文件路径 |
| `remote_path` | `string` | ✅ | - | 微云目标路径 |
| `overwrite` | `boolean` | ❌ | `false` | 是否覆盖同名文件 |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `file_id` | `string` | 上传后的文件 ID |
| `name` | `string` | 文件名 |
| `size` | `integer` | 文件大小 |
| `remote_path` | `string` | 云端路径 |
| `md5` | `string` | 文件 MD5 |
| `uploaded_at` | `string` | 上传时间 |

---

### 2.3 download_file — 下载文件

**描述**：从微云下载文件到本地。

**CLI**：

```bash
python weiyun_skills/main.py download /我的文档/report.pdf ./downloads/
python weiyun_skills/main.py download /我的文档/report.pdf ./downloads/ --overwrite
```

**Python**：

```python
result = client.download_file("/我的文档/report.pdf", "./downloads/report.pdf")
```

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `remote_path` | `string` | ✅ | - | 微云文件路径 |
| `local_path` | `string` | ✅ | - | 本地保存路径 |
| `overwrite` | `boolean` | ❌ | `false` | 是否覆盖本地文件 |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `local_path` | `string` | 本地保存路径 |
| `size` | `integer` | 文件大小 |
| `md5` | `string` | MD5 校验值 |
| `elapsed` | `float` | 下载耗时（秒） |

---

### 2.4 delete_file — 删除文件

**描述**：删除微云文件或文件夹（移入回收站）。

**CLI**：

```bash
python weiyun_skills/main.py delete /我的文档/old_file.pdf
python weiyun_skills/main.py delete /我的文档/old_file.pdf --permanent
```

**Python**：

```python
result = client.delete_file("/我的文档/old_file.pdf", permanent=False)
```

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `remote_path` | `string` | ✅ | - | 文件/文件夹路径 |
| `permanent` | `boolean` | ❌ | `false` | 是否永久删除（跳过回收站） |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `deleted_path` | `string` | 已删除的路径 |
| `is_permanent` | `boolean` | 是否永久删除 |
| `deleted_at` | `string` | 删除时间 |

---

### 2.5 move_file — 移动文件

**描述**：将文件或文件夹移动到另一个目录。

**CLI**：

```bash
python weiyun_skills/main.py move /我的文档/report.pdf /归档/2026/
```

**Python**：

```python
result = client.move_file("/我的文档/report.pdf", "/归档/2026/")
```

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `source_path` | `string` | ✅ | - | 源路径 |
| `target_path` | `string` | ✅ | - | 目标目录路径 |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `source_path` | `string` | 原路径 |
| `target_path` | `string` | 新路径 |

---

### 2.6 copy_file — 复制文件

**描述**：复制文件或文件夹到另一个目录。

**CLI**：

```bash
python weiyun_skills/main.py copy /我的文档/report.pdf /备份/
```

**Python**：

```python
result = client.copy_file("/我的文档/report.pdf", "/备份/")
```

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `source_path` | `string` | ✅ | - | 源路径 |
| `target_path` | `string` | ✅ | - | 目标目录路径 |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `source_path` | `string` | 源路径 |
| `target_path` | `string` | 副本路径 |
| `new_file_id` | `string` | 副本文件 ID |

---

### 2.7 rename_file — 重命名

**描述**：重命名文件或文件夹。

**CLI**：

```bash
python weiyun_skills/main.py rename /我的文档/report.pdf "年度报告.pdf"
```

**Python**：

```python
result = client.rename_file("/我的文档/report.pdf", "年度报告.pdf")
```

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `remote_path` | `string` | ✅ | - | 文件当前路径 |
| `new_name` | `string` | ✅ | - | 新文件名 |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `old_path` | `string` | 原路径 |
| `new_path` | `string` | 新路径 |

---

### 2.8 create_folder — 创建文件夹

**描述**：在微云上创建文件夹，支持递归创建多级目录。

**CLI**：

```bash
python weiyun_skills/main.py mkdir /工作/2026/Q1/报告
```

**Python**：

```python
result = client.create_folder("/工作/2026/Q1/报告")
```

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `remote_path` | `string` | ✅ | - | 文件夹路径 |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `folder_id` | `string` | 文件夹 ID |
| `path` | `string` | 完整路径 |
| `created_at` | `string` | 创建时间 |

---

### 2.9 search_files — 搜索文件

**描述**：按关键词搜索微云中的文件。

**CLI**：

```bash
python weiyun_skills/main.py search "报告"
python weiyun_skills/main.py search "报告" --type document
```

**Python**：

```python
results = client.search_files("报告", file_type="document")
```

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `keyword` | `string` | ✅ | - | 搜索关键词 |
| `file_type` | `string` | ❌ | `all` | 类型过滤：`all`/`document`/`image`/`video`/`audio` |
| `page` | `integer` | ❌ | `1` | 分页页码 |
| `page_size` | `integer` | ❌ | `50` | 每页数量 |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `results` | `array` | 搜索结果列表 |
| `results[].file_id` | `string` | 文件 ID |
| `results[].name` | `string` | 文件名 |
| `results[].type` | `string` | 类型 |
| `results[].size_str` | `string` | 可读大小 |
| `results[].path` | `string` | 路径 |
| `total` | `integer` | 匹配总数 |

---

## 3. 分享管理 Skills

### 3.1 create_share — 创建分享

**描述**：为文件或文件夹创建分享链接，支持设置密码和有效期。

**CLI**：

```bash
python weiyun_skills/main.py share /我的文档/report.pdf
python weiyun_skills/main.py share /我的文档/report.pdf --expire 7 --password abc1
```

**Python**：

```python
share = client.create_share(
    "/我的文档/report.pdf",
    expire_days=7,
    password="abc1"
)
print(share["share_url"])
```

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `remote_path` | `string` | ✅ | - | 文件/文件夹路径 |
| `password` | `string` | ❌ | `null` | 分享密码（4 位） |
| `expire_days` | `integer` | ❌ | `0` | 有效天数，0 为永久 |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `share_id` | `string` | 分享 ID |
| `share_url` | `string` | 分享链接 |
| `password` | `string` | 分享密码 |
| `expire_at` | `string` | 过期时间 |
| `created_at` | `string` | 创建时间 |

**示例输出**：

```json
{
  "success": true,
  "data": {
    "share_id": "s_abc123",
    "share_url": "https://share.weiyun.com/xxxx",
    "password": "abc1",
    "expire_at": "2026-03-22 21:00:00",
    "created_at": "2026-03-15 21:00:00"
  },
  "message": "ok"
}
```

---

### 3.2 cancel_share — 取消分享

**描述**：取消已创建的分享链接。

**CLI**：

```bash
python weiyun_skills/main.py unshare s_abc123
```

**Python**：

```python
result = client.cancel_share("s_abc123")
```

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `share_id` | `string` | ✅ | - | 分享 ID |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `share_id` | `string` | 已取消的分享 ID |
| `cancelled_at` | `string` | 取消时间 |

---

### 3.3 list_shares — 列出分享

**描述**：列出当前用户所有的分享链接。

**CLI**：

```bash
python weiyun_skills/main.py shares
python weiyun_skills/main.py shares --status active
```

**Python**：

```python
shares = client.list_shares(status="active")
```

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `status` | `string` | ❌ | `all` | 状态过滤：`all`/`active`/`expired` |
| `page` | `integer` | ❌ | `1` | 分页页码 |
| `page_size` | `integer` | ❌ | `20` | 每页数量 |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `shares` | `array` | 分享列表 |
| `shares[].share_id` | `string` | 分享 ID |
| `shares[].share_url` | `string` | 分享链接 |
| `shares[].file_name` | `string` | 文件名 |
| `shares[].status` | `string` | 状态 |
| `shares[].view_count` | `integer` | 查看次数 |
| `shares[].download_count` | `integer` | 下载次数 |
| `shares[].created_at` | `string` | 创建时间 |
| `shares[].expire_at` | `string` | 过期时间 |
| `total` | `integer` | 总数量 |

---

## 4. 空间管理 Skills

### 4.1 get_space_info — 空间信息

**描述**：获取微云存储空间使用情况。

**CLI**：

```bash
python weiyun_skills/main.py space
```

**Python**：

```python
info = client.get_space_info()
print(f"Used: {info['used_space_str']} / {info['total_space_str']}")
```

**输入参数**：无

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `total_space` | `integer` | 总空间（字节） |
| `total_space_str` | `string` | 可读总空间（如 `10 GB`） |
| `used_space` | `integer` | 已用空间（字节） |
| `used_space_str` | `string` | 可读已用空间 |
| `free_space` | `integer` | 剩余空间（字节） |
| `free_space_str` | `string` | 可读剩余空间 |
| `usage_percent` | `float` | 使用百分比 |
| `file_count` | `integer` | 文件总数 |
| `folder_count` | `integer` | 文件夹总数 |

**示例输出**：

```json
{
  "success": true,
  "data": {
    "total_space": 10737418240,
    "total_space_str": "10.00 GB",
    "used_space": 5368709120,
    "used_space_str": "5.00 GB",
    "free_space": 5368709120,
    "free_space_str": "5.00 GB",
    "usage_percent": 50.0,
    "file_count": 1234,
    "folder_count": 56
  },
  "message": "ok"
}
```

---

### 4.2 get_recycle_bin — 回收站

**描述**：获取回收站中的文件列表。

**CLI**：

```bash
python weiyun_skills/main.py recycle
```

**Python**：

```python
items = client.get_recycle_bin()
```

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `page` | `integer` | ❌ | `1` | 分页页码 |
| `page_size` | `integer` | ❌ | `50` | 每页数量 |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `files` | `array` | 回收站文件列表 |
| `files[].file_id` | `string` | 文件 ID |
| `files[].name` | `string` | 文件名 |
| `files[].size_str` | `string` | 可读大小 |
| `files[].original_path` | `string` | 原始路径 |
| `files[].deleted_at` | `string` | 删除时间 |
| `total` | `integer` | 总数量 |
| `total_size_str` | `string` | 回收站总大小 |

---

### 4.3 restore_file — 恢复文件

**描述**：从回收站恢复文件到原始位置。

**CLI**：

```bash
python weiyun_skills/main.py restore f_del001
```

**Python**：

```python
result = client.restore_file("f_del001")
```

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `file_id` | `string` | ✅ | - | 回收站中的文件 ID |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `file_id` | `string` | 文件 ID |
| `restored_path` | `string` | 恢复后路径 |
| `restored_at` | `string` | 恢复时间 |

---

### 4.4 clear_recycle_bin — 清空回收站

**描述**：清空回收站，永久删除所有回收站文件。**⚠️ 此操作不可逆！**

**CLI**：

```bash
python weiyun_skills/main.py clear-recycle --confirm
```

**Python**：

```python
result = client.clear_recycle_bin(confirm=True)
```

**输入参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `confirm` | `boolean` | ✅ | - | 必须为 `true` 才执行 |

**输出参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `deleted_count` | `integer` | 删除文件数 |
| `freed_space_str` | `string` | 释放的空间大小 |
| `cleared_at` | `string` | 清空时间 |

---

## 附录 A：统一错误码

| 错误码 | 说明 |
|--------|------|
| `AUTH_EXPIRED` | Cookies 已过期，需重新登录 |
| `AUTH_FAILED` | 认证失败 |
| `FILE_NOT_FOUND` | 文件不存在 |
| `FOLDER_NOT_FOUND` | 文件夹不存在 |
| `SPACE_FULL` | 空间已满 |
| `FILE_TOO_LARGE` | 文件过大 |
| `DUPLICATE_NAME` | 名称重复 |
| `PERMISSION_DENIED` | 权限不足 |
| `RATE_LIMITED` | 请求频率超限 |
| `NETWORK_ERROR` | 网络错误 |
| `SHARE_EXPIRED` | 分享已过期 |
| `INVALID_PARAM` | 参数无效 |
| `QR_EXPIRED` | 二维码已过期，需刷新 |
| `QR_CANCELLED` | 用户取消了扫码 |

**错误响应格式**：

```json
{
  "success": false,
  "data": null,
  "message": "Cookies expired, please re-login",
  "error_code": "AUTH_EXPIRED"
}
```

---

## 附录 B：Cookies 关键字段说明

| Cookie 名称 | 说明 |
|-------------|------|
| `uin` | 用户 QQ 号标识 |
| `skey` | 会话密钥 |
| `p_uin` | 加密的用户标识 |
| `p_skey` | 加密的会话密钥 |
| `pt4_token` | PT4 认证 Token |
| `pt2gguin` | 辅助认证字段 |

> **提示**：并非所有 Cookie 字段都是必需的，核心字段为 `uin`、`skey`、`p_skey`。
