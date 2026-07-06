# Feishu Cloud Drive - 飞书云盘助手

<div align="center">

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Feishu API](https://img.shields.io/badge/Feishu-Drive%20API-orange.svg)

基于飞书官方 Drive API 的云盘管理技能，支持文件列表查询、上传、下载、文件夹创建和权限管理。

[快速开始](#快速开始) • [功能特性](#功能特性) • [使用示例](#使用示例) • [常见问题](#常见问题)

</div>

## 📖 目录

- [功能特性](#功能特性)
- [项目起源](#项目起源)
- [快速开始](#快速开始)
- [使用示例](#使用示例)
- [API 文档](#api-文档)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## ✨ 功能特性

所有以下功能均已在 `feishu_drive_client.py` 中完整实现：

- 📁 **文件管理** - 获取文件列表、上传、下载、创建文件夹、删除、移动、复制
- 🔐 **权限管理** - 自动为创建的文件夹添加用户权限
- 👥 **用户查询** - 通过邮箱/手机号获取用户 open_id
- 📊 **文件统计** - 获取文件阅读、点赞、评论等统计信息 (`get_file_statistics`)
- 👁️ **访问记录** - 获取文件访问记录 (`get_file_view_records`)
- 🔍 **文件搜索** - 按标题或内容搜索云空间文件 (`search_files`)
- 📎 **快捷方式** - 创建文件快捷方式 (`create_shortcut`)
- 📋 **批量元数据** - 批量获取多个文件的元数据信息 (`batch_get_file_meta`)
- 📚 **完整文档** - 详细的 API 文档和使用示例
- 🛡️ **错误处理** - 完善的错误码和解决方案
- 🔧 **环境变量配置** - 统一使用环境变量管理凭证
- ⚠️ **安全删除** - 删除操作前强制确认，避免误删

> **代码验证**: 所有宣传的功能均可在 `feishu_drive_client.py` 中找到对应的实现方法。

---

## 🎯 项目起源

本技能参考了社区中的 `feishu-drive` 技能，但在实现过程中发现原技能存在多处 API 调用错误和文档不符的问题。因此基于飞书官方文档重新开发了此技能，修复了所有已知问题，并新增了权限管理功能。

### 📌 与原 feishu-drive 技能的对比

| 特性     | 原 feishu-drive | Feishu Cloud Drive |
| ------ | -------------- | ------------------ |
| API 版本 | 使用错误的 API 路径   | ✅ 基于官方文档验证         |
| 文档准确性  | 文档与实际 API 不符   | ✅ 完全符合官方文档         |
| 权限管理   | ❌ 未处理权限问题      | ✅ 完整的权限管理功能        |
| 错误处理   | 基础             | ✅ 完善的错误码和解决方案      |
| 最佳实践   | 缺失             | ✅ 提供安全注意事项和最佳实践    |

---

## ⚠️ 安装前检查

在安装和使用此技能前，请注意以下几点：

### 凭证管理

- **必需环境变量**：`FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`
- ⚠️ **切勿**将凭证直接写入代码或提交到公共仓库
- ✅ **推荐**：通过环境变量或安全的配置管理工具管理凭证
- ✅ **验证**：所有 API 请求仅发送至 `open.feishu.cn`（飞书官方域名）

### 权限要求

本技能需要以下飞书应用权限（请根据实际需要授予最小范围）：

- `drive:file:read` - 读取文件
- `drive:file:write` - 写入文件
- `drive:folder:read` - 读取文件夹
- `drive:folder:write` - 创建文件夹
- `contact:user.id:readonly` - 获取用户 ID（权限管理需要）

### 令牌处理

- 技能使用 `tenant_access_token` 认证机制
- 令牌在客户端实例中缓存，避免重复获取
- 令牌由飞书 API 返回的 `app_access_token` 字段提供

### 安全建议

- 🔒 **最小权限原则**：建议创建专门的飞书应用用于测试，仅授予必需的权限
- 🔍 **代码审查**：首次使用前，请审查完整的 `feishu_drive_client.py` 源代码
- 🧪 **测试环境**：先在测试环境中验证功能，再投入生产使用
- ⚠️ **凭证保护**：切勿将 `FEISHU_APP_SECRET` 提交到代码仓库或分享给他人
- 🏢 **生产环境**：在生产环境中使用时，确保应用仅拥有必要的权限范围

---

## 🚀 快速开始

### 前置要求

- Python 3.6 或更高版本
- 飞书开发者账号
- 已创建飞书应用并获取凭证

### 1. 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn)
2. 创建应用或选择已有应用
3. 获取 `App ID` 和 `App Secret`
4. 在权限管理页面申请以下权限：
   - `drive:file:read` - 读取文件
   - `drive:file:write` - 写入文件
   - `drive:folder:read` - 读取文件夹
   - `drive:folder:write` - 创建文件夹
   - `contact:user.id:readonly` - 获取用户ID（权限管理需要）

### 2. 安装依赖

```bash
pip install requests
```

### 3. 配置应用凭证

使用环境变量配置应用凭证：

```bash
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
export FEISHU_ROOT_FOLDER_TOKEN="your_folder_token"  # 可选：设置默认根目录
```

然后在代码中：

```python
from feishu_drive_client import create_client

client = create_client()  # 自动从环境变量读取配置
```

或者手动创建客户端：

```python
from feishu_drive_client import FeishuDriveClient

client = FeishuDriveClient(
    app_id="your_app_id",
    app_secret="your_app_secret",
    root_folder_token="your_folder_token"  # 可选
)
```

### 4. 首次使用

获取根文件夹 token 并列出文件：

```python
# 获取"我的空间"根文件夹 token
root_token = client.get_root_folder_token()
print(f"根文件夹 token: {root_token}")

# 列出根文件夹内容
result = client.list_folder(root_token)
children = result["data"]["children"]
for dict_key, item in children.items():
    # ⚠️ 重要：dict_key 是字典 key（nodcn...），不是下载用 token
    # 真正的 file_token 存储在 item['token'] 中
    file_token = item['token']
    print(f"{item['name']} ({item['type']}) - token: {file_token}")
```

---

## 💡 使用示例

### 上传文件

```python
result = client.upload_file(
    file_path="/path/to/file.jpg",
    parent_folder_token=folder_token,
    file_name="uploaded_file.jpg"
)
if result["code"] == 0:
    print(f"上传成功！文件 token: {result['data']['file_token']}")
else:
    print(f"上传失败: {result['msg']}")
```

### 下载文件

```python
result = client.download_file(
    file_token="file_token",
    save_path="/path/to/downloaded_file.jpg"
)
if result["code"] == 0:
    print(f"下载成功！保存路径: {result['data']['save_path']}")
else:
    print(f"下载失败: {result['msg']}")
```

### 创建文件夹

```python
result = client.create_folder(
    name="新建文件夹",
    parent_folder_token=folder_token
)
if result["code"] == 0:
    print(f"创建成功！文件夹 token: {result['data']['token']}")
else:
    print(f"创建失败: {result['msg']}")
```

### 创建文件夹并添加权限

```python
# 创建文件夹并自动为用户添加完全访问权限
result = client.create_folder_with_permission(
    name="共享文件夹",
    parent_folder_token=folder_token,
    user_emails=["user@example.com"],  # 或使用 user_mobiles
    perm="full_access"  # 可选: view, edit, full_access
)
if result["code"] == 0:
    print("创建成功！权限已自动添加")
```

### 获取用户 open_id

```python
# 通过邮箱获取用户 open_id
result = client.get_user_open_id(emails=["user@example.com"])
if result["code"] == 0:
    user_list = result["data"]["user_list"]
    for user in user_list:
        print(f"用户 {user['email']} 的 open_id: {user['user_id']}")
```

### 删除文件夹（带确认提示）

```python
# ⚠️ 删除前必须向用户确认！
def delete_folder_with_confirm(client, folder_token, folder_name, confirmed=False):
    print(f"\n⚠️  即将删除文件夹: {folder_name}")
    print(f"Token: {folder_token}")

    # 请求用户确认（在自主运行环境中，通过参数传递确认状态）
    if not confirmed:
        print("请设置 confirmed=True 确认删除")
        return

    # 执行删除
    result = client.delete_folder(folder_token)
    if result["code"] == 0:
        print("✅ 删除成功！文件夹已进入回收站")
    else:
        print(f"❌ 删除失败: {result['msg']}")

# 使用示例 - 必须显式确认
delete_folder_with_confirm(client, "folder_token", "测试文件夹", confirmed=True)
```

### 删除文件（带确认提示）

```python
# ⚠️ 删除前必须向用户确认！
def delete_file_with_confirm(client, file_token, file_name, confirmed=False):
    print(f"\n⚠️  即将删除文件: {file_name}")
    
    if not confirmed:
        print("请设置 confirmed=True 确认删除")
        return
    
    result = client.delete_file(file_token)
    if result["code"] == 0:
        print("✅ 文件删除成功！")
    else:
        print(f"❌ 删除失败: {result['msg']}")

# 使用示例 - 必须显式确认
delete_file_with_confirm(client, "file_token", "文件名", confirmed=True)
```

### 移动文件/文件夹

```python
# 将文件移动到另一个文件夹
result = client.move_file(
    file_token="file_token",
    target_folder_token="target_folder_token",
    file_type="file"  # 可选: file, folder, doc, sheet, bitable, docx
)
if result["code"] == 0:
    print("✅ 移动成功！")
else:
    print(f"❌ 移动失败: {result['msg']}")
```

### 复制文件

```python
# 复制文件到另一个文件夹（异步操作）
result = client.copy_file(
    file_token="source_file_token",
    target_folder_token="target_folder_token",
    file_type="file",
    name="复制后的文件名(可选)"
)
if result["code"] == 0:
    ticket = result["data"]["ticket"]
    print(f"复制任务已提交，ticket: {ticket}")

    # 查询任务状态
    task_result = client.check_task_status(ticket)
    print(f"任务状态: {task_result['data']['status']}")
```

### 批量获取文件元数据

```python
# 批量获取多个文件的元数据
result = client.batch_get_file_meta(["token1", "token2", "token3"])
if result["code"] == 0:
    for file_meta in result["data"]["metas"]:
        print(f"{file_meta['name']}: {file_meta['size']} bytes")
```

### 获取文件统计信息

```python
# 获取文件的阅读、点赞、评论数
result = client.get_file_statistics("file_token")
if result["code"] == 0:
    stats = result["data"]
    print(f"阅读数: {stats.get('uv', 0)}")
    print(f"点赞数: {stats.get('like_count', 0)}")
    print(f"评论数: {stats.get('comment_count', 0)}")
```

### 获取文件访问记录

```python
# 查看谁访问了文件
result = client.get_file_view_records("file_token", page_size=20)
if result["code"] == 0:
    for record in result["data"]["view_records"]:
        print(f"{record['user_name']} 在 {record['view_time']} 访问了文件")
```

### 创建文件快捷方式

```python
# 在另一个文件夹创建文件的快捷方式
result = client.create_shortcut(
    file_token="source_file_token",
    folder_token="target_folder_token",
    file_type="file"
)
if result["code"] == 0:
    print(f"✅ 快捷方式创建成功: {result['data']['url']}")
```

### 搜索文件

```python
# 按标题搜索文件
result = client.search_files(
    search_key="title",      # 或 "content" 按内容搜索
    search_value="关键词",
    page_size=20
)
if result["code"] == 0:
    for file in result["data"]["files"]:
        print(f"找到文件: {file['name']} ({file['type']})")
```

---

## 📚 API 文档

完整的 API 文档请查看 [SKILL.md](./SKILL.md)，包含：

- 根文件夹操作
- 文件夹操作（创建、列出、删除、移动）
- 文件列表查询
- 文件上传/下载/删除/复制/移动
- 文件统计和访问记录
- 文件搜索
- 快捷方式创建
- 权限管理
- 文件信息查询
- 错误处理
- 最佳实践

---

## ❓ 常见问题

### Q1: 如何配置应用凭证？

**A:** 使用环境变量配置：

```bash
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
export FEISHU_ROOT_FOLDER_TOKEN="your_folder_token"  # 可选
```

然后在代码中使用 `create_client()` 创建客户端实例，或手动创建 `FeishuDriveClient`。

### Q2: 为什么通过 API 创建的文件夹用户看不到？

**A:** API 创建的文件夹默认只有机器人可见。需要使用 `add_permission()` 或 `create_folder_with_permission()` 方法为用户添加权限。

### Q3: 上传文件时提示文件大小超限怎么办？

**A:** 当前使用的是简单上传接口，限制为 10MB。如果文件超过 10MB，建议使用飞书提供的分片上传接口。

### Q4: 如何获取文件夹 token？

**A:** 有两种方式：

1. 从飞书云盘的文件夹 URL 中获取（格式：`https://xxx.feishu.cn/drive/folder/{token}`）
2. 使用 `get_root_folder_token()` 获取根文件夹，然后通过 `list_folder()` 遍历找到目标文件夹

### Q5: open_id 和 user_id 有什么区别？

**A:**

- `open_id`：用户的唯一标识符，格式为 `ou_xxxxx`，用于权限管理
- `user_id`：数字格式的用户ID，部分旧接口使用
- 权限管理 API 必须使用 `open_id`

### Q6: 获取 tenant_access_token 失败怎么办？

**A:** 检查以下几点：

1. App ID 和 App Secret 是否正确
2. 应用是否已发布
3. 应用权限是否已申请并批准
4. 检查错误码 `99991663`，这通常表示 token 过期或无效

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

如果你发现了 Bug 或有新的功能建议，请：

1. 查看 [Issues](https://github.com/your-repo/issues) 确认问题未被提出
2. 创建新的 Issue，详细描述问题或建议
3. 如果你愿意修复，欢迎提交 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](./LICENSE) 文件。

---

## 🔗 技术支持

- [飞书开放平台](https://open.feishu.cn)
- [Drive API 文档](https://open.feishu.cn/document/server-docs/docs/drive-v1)
- [Explorer API 文档](https://open.feishu.cn/document/server-docs/docs/drive-explorer)
- [权限管理 API 文档](https://open.feishu.cn/document/server-docs/docs/permission/permission-member/create)

---

## 📝 版本历史

### v1.1.5 (2026-03-23)

- 🐛 **重要修复**：修复 token 混淆导致的 404 错误
- 📝 增强 README 和 SKILL 文档，添加常见错误诊断部分
- ⚠️ 添加详细的 token 混淆错误说明和正确用法示例
- 🔧 改进 `list_all()` 方法的注释，澄清 dict_key 和 file_token 的区别

### v1.1.4 (2026-03-23)

- 🔧 修复 ClawHub 审核反馈的元数据不一致问题
- 📝 确保所有宣传的功能都在代码中实现
- 📦 统一 _meta.json、SKILL.md 和 README 中的元数据

### v1.0.7 (2026-03-23)

- 📦 添加 `dependencies` 和 `install` 字段到 _meta.json
- 🔧 修复删除示例，避免使用 `input()` 以适应自主运行环境
- 📝 更新删除函数，使用 `confirmed` 参数替代交互式确认

### v1.0.6 (2026-03-23)

- 🔒 强化安全建议，强调最小权限原则
- 📝 更新 README 和 SKILL.md 安全注意事项
- ⚠️ 添加凭证保护和测试应用建议

### v1.0.5 (2026-03-23)

- 🔧 修复注册表元数据不一致问题
- 📝 添加 `homepage` 和 `source` 字段
- 🔒 添加 `primary_credential` 声明

### v1.0.4 (2026-03-23)

- 🔧 修复 ClawHub 反馈的问题
- 📝 统一文档与代码中环境变量的说明
- ✨ 完善 `create_client()` 函数，支持 `FEISHU_ROOT_FOLDER_TOKEN`
- 🔗 添加权限问题排查官方文档链接

### v1.0.3 (2026-03-23)

- ✨ 新增根目录设置功能，支持 `FEISHU_ROOT_FOLDER_TOKEN` 环境变量
- 🔧 更新 `create_client()` 函数以支持根目录配置
- 📝 更新文档，添加根目录配置说明和手动创建客户端示例

### v1.0.2 (2026-03-23)

- 🔧 统一使用环境变量配置凭证，移除直接传入凭证的方式
- 🐛 修复文档与代码不一致的问题（回应 clawhub 反馈）
- 📝 更新 _meta.json 描述和元数据，同步注册表信息
- 🔒 添加"安装前检查"章节，明确安全注意事项和权限要求

### v1.0.0 (2026-03-23)

- ✨ 初始版本发布
- 🐛 修复原 feishu-drive 技能的 API 调用错误
- 📚 完善的 API 文档和使用示例
- 🔐 新增权限管理功能
- 🛡️ 添加完整的错误处理和最佳实践

---

<div align="center">

**如果这个技能对你有帮助，请给它一个 ⭐️**

Made with ❤️ by WorkBuddy Community

</div>
