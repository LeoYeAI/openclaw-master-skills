# openclaw-feishu-docs-perm-auto 🔐

> 自动为飞书文档添加用户权限

## 📖 简介

飞书应用创建的文档，用户默认无权限访问。这个 Skill 帮你自动添加权限，让用户可以直接访问和编辑文档。

## ✨ 功能特性

- ✅ **自动权限添加** - 创建飞书文档后自动添加用户权限
- ✅ **多文档类型支持** - 支持多维表格、文档、电子表格、文件夹、知识库等
- ✅ **智能配置检测** - 自动检查配置完整性，缺失时引导用户配置
- ✅ **URL 自动解析** - 从文档链接自动识别文档类型和 token
- ✅ **幂等处理** - 权限已存在时自动跳过，不会报错
- ✅ **Token 缓存** - 缓存 tenant_access_token，减少 API 调用

## 📦 安装

### ClawHub 安装（推荐）

```bash
clawhub install openclaw-feishu-docs-perm-auto
```

### 手动安装

将 `openclaw-feishu-docs-perm-auto` 文件夹复制到 OpenClaw 的 skills 目录：

```bash
cp -r openclaw-feishu-docs-perm-auto ~/.openclaw/workspace/skills/
```

## 🚀 使用方法

### 前置条件

| 条件 | 说明 |
|------|------|
| 飞书开发者账号 | 需要有飞书开放平台的开发者权限 |
| 企业自建应用 | 已创建或有权创建飞书应用 |
| 应用权限 | 应用需开通 `docs:permission.member:create` 权限 |

### 配置

在 `~/.openclaw/openclaw.json` 中添加飞书应用配置：

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxxxxxxx",
      "appSecret": "xxxxxxxx",
      "ownerOpenId": "ou_xxx"
    }
  }
}
```

| 字段 | 说明 | 必需 |
|------|------|------|
| `appId` | 飞书应用 ID | ✅ |
| `appSecret` | 飞书应用密钥 | ✅ |
| `ownerOpenId` | 用户的 open_id | ⚪ 可选（会话上下文补充） |

### 使用场景

#### 场景 1：创建文档后自动添加权限

```
用户：帮我创建一个多维表格叫「项目进度追踪」

Agent：
[1/3] 创建多维表格...
[2/3] 添加用户权限...  ← 自动触发此 skill
[3/3] 完成！

✅ 多维表格「项目进度追踪」已创建！
🔗 链接：https://xxx.feishu.cn/base/bascnxxx
🔐 已自动为你添加完整权限
```

#### 场景 2：补充添加权限

```
用户：这个文档我打不开 https://xxx.feishu.cn/docx/doxcnxxx

Agent：
[1/3] 解析文档信息...
[2/3] 添加权限...
[3/3] 完成！

✅ 权限添加成功！你现在可以直接访问了。
```

## 📋 支持的文档类型

| 类型 | doc_type | URL 示例 |
|------|----------|----------|
| 多维表格 | `bitable` | `/base/【token】` |
| 新版文档 | `docx` | `/docx/【token】` |
| 旧版文档 | `doc` | `/docs/【token】` |
| 电子表格 | `sheet` | `/【token】` |
| 文件夹 | `folder` | `/drive/folder/【token】` |
| 云空间文件 | `file` | `/file/【token】` |
| 知识库节点 | `wiki` | `/wiki/【token】` |

## 🔐 权限级别

| 权限值 | 说明 | 适用场景 |
|--------|------|----------|
| `view` | 只读 | 分享给他人查看 |
| `edit` | 可编辑 | 协作编辑 |
| `full_access` | 完整权限 | 文档所有者（默认） |

## ⚠️ 错误处理

| 错误码 | 原因 | 解决方案 |
|--------|------|----------|
| `10003` | App ID/Secret 错误 | 检查配置 |
| `99991661` | 成员已存在 | 视为成功 |
| `99991663` | Token 过期 | 重新获取 |
| `99991664` | 应用无权限 | 配置应用权限 |

## 🔗 相关链接

| 资源 | 链接 |
|------|------|
| ClawHub | https://clawhub.com/skills/openclaw-feishu-docs-perm-auto |
| GitHub | https://github.com/sadjjk/openclaw-feishu-docs-perm-auto |
| 飞书开放平台 | https://open.feishu.cn/app |
| 权限配置指南 | https://open.feishu.cn/document/docs/permission/permission-member/batch_create |
| 获取 Open ID | https://open.feishu.cn/document/faq/trouble-shooting/how-to-obtain-openid |

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/image?repos=sadjjk/openclaw-feishu-docs-perm-auto&type=date&legend=top-left)](https://www.star-history.com/?repos=sadjjk%2Fopenclaw-feishu-docs-perm-auto&type=date&legend=top-left)
