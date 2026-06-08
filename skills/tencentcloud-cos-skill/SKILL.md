---
name: tencent-cloud-cos
description: >
  腾讯云对象存储(COS)和数据万象(CI)集成技能。当用户需要上传、下载、管理云存储文件，
  或需要进行图片处理（质量评估、超分辨率、抠图、二维码识别、水印）、智能图片搜索、
  文档转PDF、视频智能封面生成等操作时使用此技能。
metadata:
  {
    "openclaw":
      {
        "emoji": "☁️",
        "requires":
          {
            "secrets":
              [
                "TENCENT_COS_SECRET_ID",
                "TENCENT_COS_SECRET_KEY"
              ],
            "config":
              [
                "TENCENT_COS_REGION",
                "TENCENT_COS_BUCKET"
              ],
            "optionalConfig":
              [
                "TENCENT_COS_DATASET_NAME",
                "TENCENT_COS_DOMAIN",
                "TENCENT_COS_SERVICE_DOMAIN",
                "TENCENT_COS_PROTOCOL"
              ]
          },
        "install":
          [
            {
              "id": "node-mcporter",
              "kind": "node",
              "package": "mcporter",
              "bins": ["mcporter"],
              "label": "Install mcporter (MCP CLI)"
            },
            {
              "id": "node-cos-mcp",
              "kind": "node",
              "package": "cos-mcp",
              "bins": ["cos-mcp"],
              "label": "Install cos-mcp (COS MCP Server)"
            },
            {
              "id": "node-cos-sdk",
              "kind": "node",
              "package": "cos-nodejs-sdk-v5",
              "label": "Install COS Node.js SDK"
            }
          ]
      }
  }
---

# 腾讯云 COS 技能

通过 cos-mcp MCP 工具 + Node.js SDK 脚本 + COSCMD 管理腾讯云对象存储和数据万象。

## 首次使用 — 自动设置

当用户首次要求操作 COS 时，按以下流程操作：

### 步骤 1：检查当前状态

```bash
{baseDir}/scripts/setup.sh --check-only
```

如果输出显示一切 OK（cos-mcp 已安装、凭证已配置），跳到「执行策略」。

### 步骤 2：如果未配置，引导用户提供凭证

告诉用户：
> 我需要你的腾讯云凭证来连接 COS 存储服务。请提供：
> 1. **SecretId** — 腾讯云 API 密钥 ID
> 2. **SecretKey** — 腾讯云 API 密钥 Key
> 3. **Region** — 存储桶区域（如 ap-guangzhou）
> 4. **Bucket** — 存储桶名称（格式 name-appid，如 mybucket-1250000000）
> 5. **DatasetName**（可选） — 数据万象数据集名称（仅智能搜索需要）
> 6. **Domain**（可选） — 自定义域名，用于替换默认的 COS 访问域名（如 cdn.example.com）
> 7. **ServiceDomain**（可选） — 自定义服务域名，用于自定义 COS API 请求域名
> 8. **Protocol**（可选） — 协议，如 https 或 http
>
> 你可以在 [腾讯云控制台 > 访问管理 > API密钥管理](https://console.cloud.tencent.com/cam/capi) 获取密钥，
> 在 [COS 控制台](https://console.cloud.tencent.com/cos/bucket) 查看存储桶信息。
>
> ⚠️ **安全要求**：**必须使用子账号密钥**，仅授予 COS 相关权限（如 `QcloudCOSDataFullControl`），**严禁使用主账号密钥**。详见下方「最小权限与子账号密钥」章节。

### 步骤 3：用户提供凭证后，运行自动设置

**推荐方式**（凭证不会出现在 shell 历史中）：
```bash
export TENCENT_COS_SECRET_ID="<SecretId>"
export TENCENT_COS_SECRET_KEY="<SecretKey>"
export TENCENT_COS_REGION="<Region>"
export TENCENT_COS_BUCKET="<Bucket>"
# 可选：
# export TENCENT_COS_DATASET_NAME="<DatasetName>"
# export TENCENT_COS_DOMAIN="<Domain>"
# export TENCENT_COS_SERVICE_DOMAIN="<ServiceDomain>"
# export TENCENT_COS_PROTOCOL="<Protocol>"

{baseDir}/scripts/setup.sh --from-env
```

备选方式（凭证会出现在 shell 历史中，不推荐）：
```bash
{baseDir}/scripts/setup.sh --secret-id "<SecretId>" --secret-key "<SecretKey>" --region "<Region>" --bucket "<Bucket>"
```

脚本会自动：
- 检查并本地安装 cos-mcp 和 cos-nodejs-sdk-v5 到项目 `node_modules`（`npm install`，非全局）
- 检查并本地安装 mcporter 到项目 `node_modules`（`npm install`，非全局；通过 `npx mcporter` 调用）
- 将凭证导出到当前 shell session 的环境变量中（**不写入** `~/.zshrc` / `~/.bashrc`）
- 创建/更新 `~/.mcporter/mcporter.json`，写入 cos-mcp 服务器配置（凭证通过 env 字段传递，权限 600）
- 如 coscmd 已安装则配置 `~/.cos.conf`（权限 600）；**不会**自动安装 coscmd
- 验证 COS 连接

### 系统变更摘要

用户安装前应了解 setup.sh 会产生的所有变更：

| 变更类型 | 具体内容 | 持久性 |
|----------|----------|--------|
| npm 本地安装 | `cos-mcp`、`cos-nodejs-sdk-v5`、`mcporter` 安装到项目 `node_modules/` | 持久（仅限项目目录） |
| 项目文件 | 如无 `package.json` 则创建 | 持久（仅限项目目录） |
| 配置文件 | `~/.mcporter/mcporter.json`（含凭证） | 持久（用户主目录） |
| 配置文件 | `~/.cos.conf`（仅当 coscmd 已安装时） | 持久（用户主目录） |
| 环境变量 | `TENCENT_COS_*` export 到当前 session | 临时（关闭终端失效） |

> ⚠️ 脚本**不会**：
> - 写入 `~/.zshrc` / `~/.bashrc` 或任何 shell 启动文件
> - 执行 `npm install -g`（全局安装）
> - 执行 `pip install`（不自动安装 Python 包）
> - 修改用户 shell 配置文件的权限

**凭证写入的文件**（⚠️ 持久化存储凭证会增加暴露风险，详见「安全注意事项」）：
| 文件 | 内容 | 权限 |
|------|------|------|
| `~/.mcporter/mcporter.json` | MCP 服务器配置中的 env 字段含凭证 | 600 |
| `~/.cos.conf` | coscmd 配置（仅当 coscmd 已安装时） | 600 |

> 如需完全清理凭证：`rm -f ~/.mcporter/mcporter.json ~/.cos.conf`
> 如需持久化环境变量，用户可自行在 shell 配置中添加 export 语句。
> **强烈建议使用子账号最小权限密钥**，详见「最小权限与子账号密钥」章节。

设置完成后即可开始使用。

## 执行策略

三种方式按优先级降级，确保操作始终可完成：

1. **方式一：cos-mcp MCP 工具**（优先） — 功能最全，支持存储 + 图片处理 + 智能搜索 + 文档媒体处理
2. **方式二：Node.js SDK 脚本** — 通过 `scripts/cos_node.mjs` 执行存储操作
3. **方式三：COSCMD 命令行** — 通过 shell 命令执行存储操作

```
mcporter + cos-mcp 可用？（npx mcporter --version && 配置存在）
  ├─ 是 → 使用方式一 mcporter 调用（全部功能）
  └─ 否 → cos-mcp MCP 工具可直接调用？（getCosConfig 返回结果）
              ├─ 是 → 使用方式一直接调用（全部功能）
              └─ 否 → Node.js + cos-nodejs-sdk-v5 可用？
                        ├─ 是 → 使用方式二（存储操作）
                        └─ 否 → coscmd 可用？（which coscmd）
                                  ├─ 是 → 使用方式三（存储操作）
                                  └─ 否 → 运行 setup.sh 安装
```

**判断方式一(mcporter)**：`npx mcporter --version` 成功 且 `cat ~/.mcporter/mcporter.json | grep cos-mcp` 有输出。
**判断方式一(直接)**：尝试调用 `getCosConfig` MCP 工具，若返回结果则可用。
**判断方式二**：`node -e "require('cos-nodejs-sdk-v5')"` 成功则可用。
**判断方式三**：`which coscmd` 有输出则可用。

---

## 方式一：cos-mcp MCP 工具（优先）

> GitHub: https://github.com/Tencent/cos-mcp

MCP 配置模板见 `references/config_template.json`。

### 调用格式

通过 mcporter 命令行调用 cos-mcp MCP 工具：

```
npx mcporter call cos-mcp.<tool_name> --config ~/.mcporter/mcporter.json --output json [--args '<JSON>']
```

列出所有可用工具：
```
npx mcporter list cos-mcp --config ~/.mcporter/mcporter.json --schema
```

**判断 mcporter 是否可用**：`npx mcporter --version` 成功 且 `~/.mcporter/mcporter.json` 包含 cos-mcp 配置。
如果 mcporter 不可用，可回退到客户端直接调用 MCP 工具（`getCosConfig` 等）。

### 工具总览

| 类别 | 说明 |
|------|------|
| 存储操作 | 上传、下载、列出、获取签名URL |
| 图片处理 | 质量评估、超分辨率、抠图、二维码识别、水印 |
| 智能搜索 | 以图搜图、文本搜图（需预建数据集） |
| 文档媒体 | 文档转PDF、视频智能封面（异步任务） |

### 常用操作

> 以下示例同时展示两种调用格式。mcporter 格式省略公共前缀 `npx mcporter call cos-mcp.` 和 `--config ~/.mcporter/mcporter.json --output json`。
> 完整 mcporter 命令：`npx mcporter call cos-mcp.<tool> --config ~/.mcporter/mcporter.json --output json --args '<JSON>'`

#### 存储

```bash
# 上传本地文件（mcporter 格式）
npx mcporter call cos-mcp.putObject --config ~/.mcporter/mcporter.json --output json --args '{"filePath":"/path/to/file.jpg","targetDir":"images"}'

# 上传本地文件（客户端直接调用格式）
putObject  filePath="/path/to/file.jpg"  targetDir="images"

# 上传字符串内容
putString  content="hello world"  fileName="test.txt"  targetDir="docs"

# 通过 URL 上传
putObjectSourceUrl  sourceUrl="https://example.com/image.png"  targetDir="images"

# 列出文件
getBucket  Prefix="images/"

# 下载文件
getObject  objectKey="images/photo.jpg"

# 获取签名下载链接
getObjectUrl  objectKey="images/photo.jpg"
```

#### 图片处理

```
# 图片质量评估
assessQuality  objectKey="images/photo.jpg"

# AI 超分辨率
aiSuperResolution  objectKey="images/photo.jpg"

# AI 智能抠图
aiPicMatting  objectKey="images/photo.jpg"

# 二维码识别
aiQrcode  objectKey="images/qrcode.jpg"

# 添加文字水印
waterMarkFont  objectKey="images/photo.jpg"  text="版权所有"

# 获取图片元信息
imageInfo  objectKey="images/photo.jpg"
```

#### 智能搜索（需预建数据集）

```
# 以图搜图
imageSearchPic  uri="https://example.com/query.jpg"

# 文本搜图
imageSearchText  text="蓝天白云"
```

#### 文档与媒体处理（异步任务）

```
# 文档转 PDF
createDocToPdfJob  objectKey="docs/report.docx"
# 查询任务结果
describeDocProcessJob  jobId="<jobId>"

# 视频智能封面
createMediaSmartCoverJob  objectKey="videos/demo.mp4"
# 查询任务结果
describeMediaJob  jobId="<jobId>"
```

工具详细参数定义见 `references/api_reference.md`。

---

## 方式二：Node.js SDK 脚本

> 官方文档: https://www.tencentcloud.com/zh/document/product/436/8629

当 cos-mcp 不可用时，通过 `scripts/cos_node.mjs` 执行存储操作。凭证从环境变量读取。

支持的环境变量：
- `TENCENT_COS_SECRET_ID` / `TENCENT_COS_SECRET_KEY` / `TENCENT_COS_REGION` / `TENCENT_COS_BUCKET`（必需）
- `TENCENT_COS_DOMAIN` / `TENCENT_COS_SERVICE_DOMAIN` / `TENCENT_COS_PROTOCOL`（可选，自定义域名）

### 常用命令

> 以下省略 `node {baseDir}/scripts/cos_node.mjs` 前缀。完整格式：`node {baseDir}/scripts/cos_node.mjs <action> [options]`

```bash
# 上传文件
upload --file /path/to/file.jpg --key remote/path/file.jpg

# 上传字符串
put-string --content "文本内容" --key remote/file.txt --content-type "text/plain"

# 下载文件
download --key remote/path/file.jpg --output /path/to/save/file.jpg

# 列出文件
list --prefix "images/"

# 获取签名 URL
sign-url --key remote/path/file.jpg --expires 3600

# 查看文件信息
head --key remote/path/file.jpg

# 删除文件
delete --key remote/path/file.jpg
```

所有命令输出 JSON 格式，`success: true` 表示成功，退出码 0。

### 限制

仅支持存储操作，**不支持**图片处理、智能搜索、文档转换。

---

## 方式三：COSCMD 命令行

> 官方文档: https://www.tencentcloud.com/zh/document/product/436/10976

当方式一和方式二均不可用时使用。配置持久化在 `~/.cos.conf`。

自定义域名支持（有限）：
- **ServiceDomain** — 对应 coscmd 的 `-e ENDPOINT` 参数，设置后 Region 失效
- **Protocol** — 若为 `http`，对应 coscmd 的 `--do-not-use-ssl` 参数
- **Domain** — COSCMD 不支持 CDN 自定义域名

### 常用命令

```bash
# 上传
coscmd upload /path/to/file.jpg remote/path/file.jpg
coscmd upload -r /path/to/folder/ remote/folder/

# 下载
coscmd download remote/path/file.jpg /path/to/save/file.jpg
coscmd download -r remote/folder/ /path/to/save/

# 列出文件
coscmd list images/

# 删除
coscmd delete remote/path/file.jpg
coscmd delete -r remote/folder/ -f

# 签名 URL
coscmd signurl remote/path/file.jpg -t 3600

# 文件信息
coscmd info remote/path/file.jpg

# 复制/移动
coscmd copy <BucketName-APPID>.cos.<Region>.myqcloud.com/source.jpg dest.jpg
coscmd move <BucketName-APPID>.cos.<Region>.myqcloud.com/source.jpg dest.jpg
```

### 限制

仅支持存储操作，**不支持**图片处理、智能搜索、文档转换。

---

## 功能对照表

| 功能 | 方式一 cos-mcp | 方式二 Node SDK | 方式三 COSCMD |
|------|:-:|:-:|:-:|
| 上传文件 | ✅ | ✅ | ✅ |
| 上传字符串/Base64 | ✅ | ✅ | ❌ |
| 通过 URL 上传 | ✅ | ❌ | ❌ |
| 下载文件 | ✅ | ✅ | ✅ |
| 列出文件 | ✅ | ✅ | ✅ |
| 获取签名 URL | ✅ | ✅ | ✅ |
| 删除文件 | ❌ | ✅ | ✅ |
| 查看文件信息 | ❌ | ✅ | ✅ |
| 递归上传/下载目录 | ❌ | ❌ | ✅ |
| 图片处理（CI） | ✅ | ❌ | ❌ |
| 智能搜索 | ✅ | ❌ | ❌ |
| 文档转 PDF | ✅ | ❌ | ❌ |
| 视频智能封面 | ✅ | ❌ | ❌ |

## 安全注意事项

### 凭证处理策略

setup.sh 在处理凭证时遵循以下原则：

1. **不修改用户的 shell 配置文件**：凭证不会写入 `~/.zshrc`、`~/.bashrc` 或其他 shell RC 文件
2. **环境变量仅当前 session 有效**：关闭终端后环境变量失效，需重新 export
3. **配置文件权限 600**：所有写入的配置文件仅当前用户可读写
4. **不执行全局安装**：npm 包安装到项目本地 `node_modules/`，不使用 `npm install -g`
5. **不自动安装系统包**：不执行 `pip install` 或其他系统级包安装

### 凭证持久化存储与暴露风险

> ⚠️ **重要安全提示**：setup.sh 会将 SecretId/SecretKey 持久化写入磁盘文件。虽然文件权限设为 600（仅当前用户可读写），但持久存储仍增加了凭证暴露风险（如磁盘被窃取、备份泄露、恶意软件读取等）。用户应充分了解此风险。

setup.sh 运行后，凭证会存储在以下文件中：

| 文件 | 写入场景 | 存储内容 | 权限 | 风险 |
|------|----------|----------|------|------|
| `~/.mcporter/mcporter.json` | 始终写入 | cos-mcp 服务器配置的 env 字段含 SecretId/SecretKey | 600 | 凭证明文存储在用户主目录 |
| `~/.cos.conf` | 仅当 coscmd 已预装时 | coscmd 配置含 SecretId/SecretKey | 600 | 凭证明文存储在用户主目录 |

**降低风险的措施**：
1. **使用最小权限子账号密钥**（见下方详细指导），不要使用主账号密钥
2. **不再使用时及时清理凭证**：`rm -f ~/.mcporter/mcporter.json ~/.cos.conf`
3. **定期轮换密钥**：在 [腾讯云控制台 > 访问管理 > API密钥管理](https://console.cloud.tencent.com/cam/capi) 定期更换密钥
4. 如条件允许，优先使用**临时凭证（STS Token）**替代永久密钥

### 安装包供应链风险

本技能通过 npm 安装以下 registry 包（标准 npm 安装，无任意 URL 下载）：
- `cos-mcp` — 腾讯云 COS MCP 服务器
- `cos-nodejs-sdk-v5` — 腾讯云 COS Node.js SDK
- `mcporter` — MCP 命令行工具

这些包来自 npm 公共 registry，与所有 npm 包一样存在供应链风险。建议在安装前通过 `npm info <package>` 核实包的发布者和版本。

### 最小权限与子账号密钥（强烈推荐）

> ⚠️ **永远不要使用主账号密钥**。主账号密钥拥有账户下所有资源的完全控制权，一旦泄露后果严重。

推荐创建专用子账号并授予仅限 COS 操作的最小权限策略：

1. 进入 [腾讯云控制台 > 访问管理 > 用户列表](https://console.cloud.tencent.com/cam)，创建子用户
2. 仅授予以下预设策略之一：
   - `QcloudCOSDataReadOnlyAccess` — 仅读取（如果只需下载/列出）
   - `QcloudCOSDataFullControl` — COS 数据读写（推荐，如需上传+下载）
   - 如需数据万象(CI)功能，额外添加 `QcloudCIFullAccess`
3. 可进一步通过**自定义策略**限制到具体存储桶：
   ```json
   {
     "statement": [{
       "effect": "allow",
       "action": ["cos:*"],
       "resource": ["qcs::cos:<Region>::uid/<APPID>:<BucketName>/*"]
     }]
   }
   ```
4. 为该子账号创建 API 密钥，并使用该密钥配置本技能

### 临时凭证（STS Token）

对于更高安全要求的场景，建议使用腾讯云 [STS 临时凭证](https://cloud.tencent.com/document/product/1312/48195)：
- 临时凭证有有效期（默认 1800 秒），过期自动失效
- 适合自动化流水线或短期任务场景
- cos-mcp 支持通过环境变量传入 STS Token（设置 `TENCENT_COS_TOKEN` 环境变量）

### 其他安全建议

1. **凭证属于敏感信息**：SecretId / SecretKey 泄露可导致存储桶数据被窃取或篡改
2. **推荐使用 `--from-env` 模式**设置凭证，避免凭证出现在 shell 历史记录中
3. **凭证不明文展示**：永远不要在对话中回显用户的 SecretId/SecretKey，引导用户自行通过 setup.sh 或编辑配置文件设置
4. **mcporter 配置使用 env 方式**：凭证通过环境变量传递给子进程，不暴露在 `ps aux` 进程列表中
5. **定期轮换密钥**：建议每 90 天更换一次 API 密钥，在 [控制台 > API密钥管理](https://console.cloud.tencent.com/cam/capi) 操作
6. **凭证清理**：不再使用时执行 `rm -f ~/.mcporter/mcporter.json ~/.cos.conf` 清除持久化凭证

## 使用规范

1. **首次使用先运行** `{baseDir}/scripts/setup.sh --check-only` 检查环境
2. **mcporter 调用必须带** `--config ~/.mcporter/mcporter.json` 和 `--output json`（使用 `npx mcporter` 调用）
3. **所有文件路径**（`objectKey`/`cospath`/`--key`）为存储桶内的相对路径，如 `images/photo.jpg`
4. **图片处理/智能搜索/文档转换仅方式一可用**，不可用时明确告知用户
5. **异步任务**（文档转换、视频封面）需通过 `jobId` 轮询结果
6. **上传后主动获取链接**：上传完成后调用 `getObjectUrl` 或 `sign-url` 返回访问链接
7. **错误处理**：调用失败时先用 `setup.sh --check-only` 诊断环境问题
8. **方式二脚本源码**见 `scripts/cos_node.mjs`
9. **MCP 工具详细参数**见 `references/api_reference.md`
10. **MCP 配置模板**见 `references/config_template.json`
