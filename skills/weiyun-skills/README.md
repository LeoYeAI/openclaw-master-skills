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

# 腾讯微云管理 Skills
> 一套用于管理腾讯微云（Weiyun）云存储服务的 Python 工具集，支持 **扫码登录** 和 **Cookies 登录** 两种认证方式。

---

## 🚀 使用方法

### 1. 安装依赖

```bash
cd weiyun-skills
pip install -r requirements.txt
```

### 2. 登录认证（二选一）

#### 方式一：扫码登录（推荐）

运行扫码登录脚本，终端会显示二维码，使用微信/QQ 扫码即可完成登录：

```bash
python weiyun_skills/login.py --method qrcode
```

扫码成功后，Cookies 会自动保存到 `cookies.json` 文件中，后续操作无需重复登录。

#### 方式二：复制 Cookies 登录

1. 在浏览器中登录 [腾讯微云](https://www.weiyun.com/)
2. 打开开发者工具 (F12) → Network → 任意请求 → 复制 `Cookie` 请求头的值
3. 运行以下命令：

```bash
python weiyun_skills/login.py --method cookies --cookies "your_cookie_string_here"
```

或者直接编辑 `cookies.json` 文件：

```json
{
  "cookies_str": "uin=o012345678; skey=@abcdef1234; ...",
  "update_time": "2026-03-15 21:00:00"
}
```

### 3. 使用 Skills

```bash
# List files in root directory
python weiyun_skills/main.py list /

# Upload a file
python weiyun_skills/main.py upload ./local_file.pdf /云端目录/

# Download a file
python weiyun_skills/main.py download /云端目录/file.pdf ./local_dir/

# Create a share link
python weiyun_skills/main.py share /云端目录/file.pdf --expire 7 --password abc123

# Get space usage info
python weiyun_skills/main.py space

# Search files by keyword
python weiyun_skills/main.py search "报告"

# Delete a file (to recycle bin)
python weiyun_skills/main.py delete /云端目录/old_file.pdf

# Move a file
python weiyun_skills/main.py move /源路径/file.pdf /目标路径/

# Create a folder
python weiyun_skills/main.py mkdir /新文件夹/子文件夹
```

### 4. 在 Python 中调用

```python
from weiyun_skills.client import WeiyunClient

# Initialize client (auto-loads cookies.json)
client = WeiyunClient()

# Or pass cookies string directly
client = WeiyunClient(cookies_str="uin=o012345678; skey=@abcdef1234; ...")

# List files
files = client.list_files("/我的文档")
for f in files:
    print(f["name"], f["size"])

# Upload file
client.upload_file("./report.pdf", "/我的文档/report.pdf")

# Download file
client.download_file("/我的文档/report.pdf", "./downloads/report.pdf")

# Create share link
share = client.create_share("/我的文档/report.pdf", expire_days=7, password="abc1")
print(share["share_url"])

# Get space info
info = client.get_space_info()
print(f"Used: {info['used_space_str']} / {info['total_space_str']}")
```

---

## 📋 项目简介

本项目提供了一组 Python 脚本，用于自动化管理腾讯微云中的文件。核心特性：

- ✅ **扫码登录** — 终端展示二维码，微信/QQ 扫码完成认证
- ✅ **Cookies 登录** — 从浏览器复制 Cookies 快速登录
- ✅ **自动保存会话** — 登录状态持久化，无需重复认证
- ✅ **文件管理** — 上传、下载、删除、移动、复制、重命名、搜索
- ✅ **分享管理** — 创建/取消分享链接，支持密码和有效期
- ✅ **空间管理** — 查看容量、回收站操作
- ✅ **命令行工具** — 所有功能均可通过命令行直接使用

---

## 📁 项目结构

```
weiyun-skills/
├── README.md                        # Project documentation
├── SKILL.md                         # Skills definition
├── LICENSE                          # MIT License
├── requirements.txt                 # Python dependencies
├── cookies.json                     # Saved login cookies (auto-generated)
└── weiyun_skills/
    ├── __init__.py                  # Package init
    ├── login.py                     # QR code login & cookies login
    ├── client.py                    # Weiyun API client
    ├── main.py                      # CLI entry point
    └── utils.py                     # Utility functions
```

---

## ⚙️ 依赖说明

| 依赖包 | 用途 |
|--------|------|
| `requests` | HTTP 请求 |
| `qrcode` | 终端展示扫码登录二维码 |
| `Pillow` | 图片处理（二维码渲染） |
| `tabulate` | 命令行表格输出 |

---

## 🛠️ Skills 一览

详细定义请参阅 [SKILL.md](./SKILL.md)。

| 分类 | Skill | 说明 |
|------|-------|------|
| 🔑 认证 | `qrcode_login` | 扫码登录 |
| 🔑 认证 | `cookies_login` | Cookies 登录 |
| 📂 文件 | `list_files` | 列出文件 |
| 📂 文件 | `upload_file` | 上传文件 |
| 📂 文件 | `download_file` | 下载文件 |
| 📂 文件 | `delete_file` | 删除文件 |
| 📂 文件 | `move_file` | 移动文件 |
| 📂 文件 | `copy_file` | 复制文件 |
| 📂 文件 | `rename_file` | 重命名 |
| 📂 文件 | `create_folder` | 创建文件夹 |
| 📂 文件 | `search_files` | 搜索文件 |
| 🔗 分享 | `create_share` | 创建分享 |
| 🔗 分享 | `cancel_share` | 取消分享 |
| 🔗 分享 | `list_shares` | 列出分享 |
| 💾 空间 | `get_space_info` | 空间信息 |
| 💾 空间 | `get_recycle_bin` | 回收站 |
| 💾 空间 | `restore_file` | 恢复文件 |
| 💾 空间 | `clear_recycle_bin` | 清空回收站 |

---

## 📝 注意事项

1. **Cookies 有效期**：腾讯微云的 Cookies 通常在 24 小时后过期，届时需重新登录
2. **扫码登录**：需要终端支持 Unicode 字符显示（大部分现代终端均支持）
3. **频率限制**：请避免短时间内大量请求，以免触发风控
4. **大文件上传**：支持分片上传，默认分片大小为 4MB

---

## 📄 许可证

[MIT License](./LICENSE) © 2026 enoyao
