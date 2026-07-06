---
name: Feishu Cloud Drive
name_zh: 飞书云盘助手
description: 基于飞书官方 API 的云盘管理技能，支持文件列表查询、上传、下载、文件夹创建、权限管理、文件搜索、统计信息、快捷方式、复制移动等完整功能。参考 feishu-drive 技能开发，修复了原技能中的 API 调用错误，并新增了自动化权限管理功能。
metadata:
  openclaw:
    requires:
      env:
        - FEISHU_APP_ID
        - FEISHU_APP_SECRET
      bins:
        - python3
        - pip3
    primaryEnv: FEISHU_APP_SECRET
    install:
      - id: pip-deps
        kind: python
        package: requests
        label: Install Python dependencies

---

# 🎯 项目起源

本技能参考了社区中的 `feishu-drive` 技能，但在实现过程中发现原技能存在以下问题：

1. **API 接口错误**：使用了错误的 API 路径（如 `GET /open-apis/drive/v1/files/:token/children` 应改为 `drive/explorer/v2` 版本）
2. **文档与实际不符**：SKILL.md 中描述的 API 与飞书官方文档不一致
3. **权限管理缺失**：创建的文件夹默认只有机器人可见，未处理权限问题

因此基于飞书官方文档重新开发了此技能，修复了所有已知问题，并新增了权限管理功能。

---

# 飞书云盘管理 (官方API版本)

你是飞书云盘管理专家，负责通过飞书官方 API 实现文件列表查询、上传、下载和文件夹管理。

## 使用方式

### 1. 配置环境变量

设置环境变量：

```bash
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
export FEISHU_ROOT_FOLDER_TOKEN="your_folder_token"  # 可选：指定默认根目录
```

### 2. 设置根目录（推荐）

**在使用技能之前，先指定一个根目录**，后续所有操作都以此目录为基准：

```python
from feishu_drive_client import create_client, FeishuDriveClient
import os

# 方式1：使用便捷函数（推荐）
# 自动从环境变量 FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_ROOT_FOLDER_TOKEN 读取
client = create_client()

# 方式2：手动创建客户端，从环境变量读取
client = FeishuDriveClient(
    app_id=os.getenv("FEISHU_APP_ID"),
    app_secret=os.getenv("FEISHU_APP_SECRET"),
    root_folder_token=os.getenv("FEISHU_ROOT_FOLDER_TOKEN")  # 可选
)

# 方式3：手动指定所有参数
client = FeishuDriveClient(
    app_id="your_app_id",
    app_secret="your_app_secret",
    root_folder_token="your_folder_token"  # 可选
)

# 方式4：后续动态设置根目录
client = FeishuDriveClient(app_id, app_secret)
client.set_root_folder("your_folder_token")
```

### 3. 使用示例

设置根目录后，所有操作默认在根目录下进行：

```python
# 在根目录下创建子文件夹（无需传入 folder_token）
result = client.create_folder("新文件夹")

# 在根目录下上传文件
result = client.upload_file("/path/to/file.jpg")

# 列出根目录内容
result = client.list_folder()

# 如需操作其他目录，可临时指定 folder_token
result = client.create_folder("其他位置的文件夹", parent_folder_token="其他token")
```

**优先级规则**：`传入的 folder_token` > `设置的 root_folder_token` > `空字符串（根目录）`

---

## API 基础信息

| 项目 | 值 |
|------|---|
| Base URL | `https://open.feishu.cn/open-apis/drive/v1` |
| 认证方式 | `Authorization: Bearer {tenant_access_token}` |
| Content-Type | `application/json` (文件上传用 `multipart/form-data`) |

---

## 核心功能

### 1. 获取根文件夹 Token

**接口说明**: 获取用户"我的空间"根文件夹的元数据

```
GET /open-apis/drive/explorer/v2/root_folder/meta
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "token": "nodcnXXXXXX",
    "id": "7110173013420512356",
    "user_id": "7103496998321312356"
  },
  "msg": "success"
}
```

**注意事项**:
- 需要权限: `drive:drive` 或 `drive:drive.metadata:readonly`
- 返回的 token 可用于后续的文件夹操作

---

### 2. 创建文件夹

**接口说明**: 在指定父文件夹下创建新文件夹

```
POST /open-apis/drive/v1/files/create_folder
```

**请求参数**:
```json
{
  "name": "文件夹名称",
  "folder_token": "父文件夹token"
}
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "token": "fldcnXXXXXX",
    "url": "https://xxx.feishu.cn/drive/folder/fldcnXXXXXX",
    "name": "文件夹名称"
  }
}
```

**注意事项**:
- `folder_token` 为父文件夹 token，可以通过 URL 获取或通过 API 查询
- 创建的文件夹默认只有机器人可见，如需用户可见需要设置权限

---

### 3. 获取文件夹内容

**接口说明**: 获取指定文件夹下的文件和子文件夹列表

**推荐方法 (Explorer v2)**:

```
GET /open-apis/drive/explorer/v2/folder/:folder_token/children
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "children": {
      "file_token1": {
        "token": "file_token1",
        "name": "文件名",
        "type": "file"
      },
      "folder_token1": {
        "token": "folder_token1",
        "name": "文件夹名",
        "type": "folder"
      }
    },
    "parentToken": "folder_token"
  },
  "msg": "success"
}
```

**注意事项**:
- `type` 为 `folder` 表示文件夹，为 `file` 表示文件
- v2 版本的 `children` 是字典格式，不是数组

---

### 4. 上传文件

**接口说明**: 上传文件到指定文件夹

```
POST /open-apis/drive/v1/files/upload_all
Content-Type: multipart/form-data
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | binary | 是 | 文件二进制内容 |
| file_name | string | 是 | 文件名 |
| parent_type | string | 是 | 父节点类型，`explorer` = 云空间 |
| parent_node | string | 是 | 父节点 token（文件夹 token） |
| size | number | 是 | 文件大小（字节） |

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "file_token": "file_token"
  }
}
```

**注意事项**:
- `parent_type` 使用 `explorer` 表示云空间文件夹
- `size` 参数必填，建议在上传前计算文件大小
- 大文件（超过 10MB）建议使用分片上传接口

---

### 5. 下载文件

**接口说明**: 根据文件 token 下载文件

```
GET /open-apis/drive/v1/files/:file_token/download
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file_token | string | 是 | 文件 token |

**响应**:
- 返回文件二进制流
- Content-Type 根据文件类型自动设置

**注意事项**:
- 需要在请求头中携带 `Authorization: Bearer {tenant_access_token}`
- 下载的是二进制流，需要正确处理响应体

---

### 6. 获取用户 Open ID

**接口说明**: 通过邮箱或手机号获取用户的 open_id

```
POST /open-apis/contact/v3/users/batch_get_id
```

**请求参数**:
```json
{
  "emails": ["user@example.com"],
  "mobiles": ["13800138000"],
  "include_resigned": false
}
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "user_list": [
      {
        "user_id": "ou_xxxxxxxxx",
        "email": "user@example.com",
        "status": {
          "is_activated": true,
          "is_resigned": false
        }
      }
    ]
  }
}
```

**注意事项**:
- 支持批量查询，最多 50 个邮箱或手机号
- 需要 `contact:user.id:readonly` 权限
- 返回的 `user_id` 就是 `open_id`

---

### 7. 添加文件夹权限

**接口说明**: 为文件夹添加用户权限

```
POST /open-apis/drive/v1/permissions/:token/members?type=folder
```

**请求参数**:
```json
{
  "member_type": "openid",
  "member_id": "ou_xxxxxxxxx",
  "perm": "full_access",
  "perm_type": "container",
  "type": "user"
}
```

**权限类型**:
| perm | 说明 |
|------|------|
| `view` | 可阅读 |
| `edit` | 可编辑 |
| `full_access` | 可管理（完全访问） |

**注意事项**:
- 创建文件夹后，默认只有机器人可见
- 必须通过此接口为用户添加权限，用户才能看到文件夹
- `member_id` 必须是 `open_id`，不能是 `user_id`
- **权限问题排查**：如果遇到机器人无法获取所创建文件夹的权限，请参考官方文档 https://open.feishu.cn/document/server-docs/docs/drive-v1/faq#b02e5bfb

---

### 8. 获取文件元数据

**接口说明**: 获取文件的详细信息

```
GET /open-apis/drive/v1/files/:file_token
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file_token | string | 是 | 文件或文件夹 token |

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "token": "token",
    "name": "名称",
    "type": "file/folder",
    "size": 1024,
    "created_time": 1234567890,
    "owner": {
      "open_id": "xxx"
    }
  }
}
```

---

### 9. 删除文件夹

**接口说明**: 删除指定文件夹（删除后进入回收站）

```
DELETE /open-apis/drive/v1/files/:folder_token?type=folder
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| folder_token | string | 是 | 文件夹 token |
| type | string | 是 | 固定值 `folder` |

**响应示例**:
```json
{
  "code": 0,
  "msg": "success"
}
```

**注意事项**:
- 删除后文件夹会进入回收站，可以在回收站中恢复
- 需要具有文件夹的编辑权限才能删除
- **重要**: 执行删除操作前必须向用户确认，避免误删

**Python 示例**:
```python
# 删除文件夹（带确认提示）
def delete_folder_with_confirm(client, folder_token, folder_name, confirmed=False):
    # 1. 显示文件夹信息
    print(f"即将删除文件夹: {folder_name}")
    print(f"Token: {folder_token}")
    
    # 2. 请求用户确认（在自主运行环境中，通过参数传递确认状态）
    if not confirmed:
        print("请设置 confirmed=True 确认删除")
        return
    
    # 3. 执行删除
    result = client.delete_folder(folder_token)
    if result.get("code") == 0:
        print("删除成功！文件夹已进入回收站")
    else:
        print(f"删除失败: {result.get('msg')}")

# 使用示例 - 必须显式确认
delete_folder_with_confirm(client, "folder_token", "测试文件夹", confirmed=True)
```

---

### 10. 删除文件

**接口说明**: 删除指定文件（删除后进入回收站）

```
DELETE /open-apis/drive/v1/files/:file_token?type=file
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file_token | string | 是 | 文件 token |
| type | string | 是 | 固定值 `file` |

**注意事项**:
- 删除后文件会进入回收站，可以在回收站中恢复
- 需要具有文件的编辑权限才能删除
- **重要**: 执行删除操作前必须向用户确认

---

### 11. 移动文件或文件夹

**接口说明**: 将文件或文件夹移动到指定文件夹

```
POST /open-apis/drive/v1/files/:file_token/move
```

**请求参数**:
```json
{
  "type": "file",
  "destination_folder_token": "目标文件夹token"
}
```

**类型说明**:
| type 值 | 说明 |
|---------|------|
| `file` | 普通文件 |
| `folder` | 文件夹 |
| `doc` | 文档 |
| `sheet` | 电子表格 |
| `bitable` | 多维表格 |
| `docx` | 新版文档 |

---

### 12. 复制文件

**接口说明**: 复制文件到指定文件夹（异步操作）

```
POST /open-apis/drive/v1/files/:file_token/copy
```

**请求参数**:
```json
{
  "type": "file",
  "destination_folder_token": "目标文件夹token",
  "name": "复制后的新名称(可选)"
}
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "ticket": "task_ticket_xxx"
  },
  "msg": "success"
}
```

**注意事项**:
- 复制是异步操作，返回 ticket 用于查询任务状态
- 使用 `check_task_status(ticket)` 查询复制进度

---

### 13. 批量获取文件元数据

**接口说明**: 批量获取多个文件的元数据信息

```
POST /open-apis/drive/v1/metas/batch_query
```

**请求参数**:
```json
{
  "file_tokens": ["token1", "token2", "token3"]
}
```

**限制**: 最多 100 个文件 token

---

### 14. 获取文件统计信息

**接口说明**: 获取文件的阅读、点赞、评论等统计信息

```
POST /open-apis/drive/v1/files/:file_token/statistics
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "uv": 100,
    "pv": 200,
    "like_count": 10,
    "comment_count": 5
  }
}
```

---

### 15. 获取文件访问记录

**接口说明**: 获取谁访问了该文件的记录

```
POST /open-apis/drive/v1/files/:file_token/view_records
```

**请求参数**:
```json
{
  "page_size": 50,
  "page_token": "可选的分页token"
}
```

---

### 16. 创建文件快捷方式

**接口说明**: 在指定文件夹创建文件的快捷方式

```
POST /open-apis/drive/v1/files/create_shortcut
```

**请求参数**:
```json
{
  "file_token": "源文件token",
  "folder_token": "目标文件夹token",
  "type": "file"
}
```

---

### 17. 搜索文件

**接口说明**: 在云空间中搜索文件

```
POST /open-apis/suite/docs-api/search/object
```

**请求参数**:
```json
{
  "search_key": "title",
  "search_value": "搜索关键词",
  "page_size": 50
}
```

**search_key 说明**:
| 值 | 说明 |
|----|------|
| `title` | 按标题搜索 |
| `content` | 按内容搜索 |

**注意事项**:
- 此接口需要 `user_access_token`，不支持 `tenant_access_token`

---

### 18. 查询异步任务状态

**接口说明**: 查询复制、移动等异步操作的任务状态

```
GET /open-apis/drive/v1/files/task_check?ticket=xxx
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ticket | string | 是 | 异步任务 ticket |

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "status": "success",
    "file_token": "新文件token"
  }
}
```

**status 说明**:
| 值 | 说明 |
|----|------|
| `pending` | 等待中 |
| `processing` | 处理中 |
| `success` | 成功 |
| `failed` | 失败 |

---

## 错误处理

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| 0 | 成功 | — |
| 99991663 | token 过期 | 重新获取 tenant_access_token |
| 1061002 | 无权限 | 检查应用权限和文件夹授权 |
| 1061001 | 文件/文件夹不存在 | 检查 token 是否正确 |
| 1061045 | 文件大小超限 | 使用分片上传或减小文件大小 |
| 404 | 文件不存在 | **常见原因**：使用了字典 key 而非 item['token']，参见下方常见错误 |

---

## ⚠️ 常见错误：Token 混淆导致 404

### 问题描述

在获取文件夹内容后尝试下载文件时，出现 404 错误。

### 根本原因

**混淆了飞书 API 返回数据结构中的两种"token"**：

```json
{
  "children": {
    "nodcn5OkQG6q8Y4SuSncukJmCtc": {  // ← 错误：这是字典的 key，不是下载用 token
      "token": "KdLTbke3BoN85RxQg5qcswFYnah",  // ← 正确：这才是下载用的 token
      "name": "Screenshot_20260323-115306.png",
      "type": "file"
    }
  }
}
```

### 错误写法 ❌

```python
result = client.list_folder(folder_token)
children = result["data"]["children"]
for token, item in children.items():  # ← token 实际是 dict_key (nodcn...)
    file_token = token  # ← 错误！这会导致 404
    client.download_file(file_token, "/path/to/file")
```

### 正确写法 ✅

```python
result = client.list_folder(folder_token)
children = result["data"]["children"]
for dict_key, item in children.items():  # dict_key 是 nodcn...
    file_token = item["token"]  # ← 正确！从 item 中获取 token
    client.download_file(file_token, "/path/to/file")

# 或者直接使用 list_all() 方法，它已经处理了这个问题
files = client.list_all(folder_token)
for file in files:
    client.download_file(file["token"], f"/path/to/{file['name']}")
```

### 记住这个规则

| 位置 | 值 | 用途 |
|------|-----|------|
| 字典 key | `nodcn5OkQG6q8Y4SuSncukJmCtc` | 仅用于迭代，通常不使用 |
| `item['token']` | `KdLTbke3BoN85RxQg5qcswFYnah` | **下载、删除、复制、移动等所有操作** |

---

## 使用建议

### 权限配置

确保应用已获取以下权限：
- `drive:file:read` - 读取文件
- `drive:file:write` - 写入文件
- `drive:folder:read` - 读取文件夹
- `drive:folder:write` - 创建文件夹
- `contact:user.id:readonly` - 获取用户 ID（用于权限管理）

### 最佳实践

1. **最小权限原则**: 为飞书应用仅授予必需的权限，避免过度授权
2. **测试应用**: 建议创建专门的测试应用，使用受限权限进行开发测试
3. **权限管理**: 通过 API 创建的文件默认只有机器人可见，需要注意权限设置
4. **冒烟测试**: 执行任何操作前，先用 `get_file_info` 测试 token 是否可用
5. **分页处理**: 文件列表可能很多，务必处理分页逻辑
6. **错误重试**: 对于网络错误和临时错误，建议实现重试机制

### 安全注意事项

1. **不要在前端代码中暴露 tenant_access_token**
2. **不要分享生产环境的 FEISHU_APP_SECRET**
3. **不要将凭证提交到代码仓库**
2. 定期轮换访问令牌
3. 限制文件上传大小，避免滥用
4. 验证文件类型，防止上传恶意文件
