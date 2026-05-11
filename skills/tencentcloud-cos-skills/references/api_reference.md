# 腾讯云 COS 操作参考

本文档记录三种操作方式的详细参数定义，供执行操作时查阅。

**环境设置**：首次使用请运行 `scripts/setup.sh`，详见 `SKILL.md` 首次使用章节。

**官方文档链接：**
- cos-mcp GitHub: https://github.com/Tencent/cos-mcp
- COS Node.js SDK: https://www.tencentcloud.com/zh/document/product/436/8629
- COSCMD 工具: https://www.tencentcloud.com/zh/document/product/436/10976

---

## 方式一：cos-mcp MCP 工具参数参考

## 存储操作工具

### getCosConfig
获取当前 COS 配置信息。
- 参数：无

### putObject
上传本地文件到存储桶。
- `filePath` (string, **必需**): 本地文件路径（包含文件名）
- `fileName` (string, 可选): 存储桶中的文件名
- `targetDir` (string, 可选): 存储桶中的目标目录

### putString
上传字符串内容到存储桶。
- `content` (string, **必需**): 要上传的字符串内容
- `fileName` (string, **必需**): 存储桶中的文件名
- `targetDir` (string, 可选): 目标目录
- `contentType` (string, 可选): MIME 类型，默认 `text/plain`

### putBase64
上传 base64 编码内容到存储桶。
- `base64Content` (string, **必需**): base64 编码的内容
- `fileName` (string, **必需**): 存储桶中的文件名
- `targetDir` (string, 可选): 目标目录
- `contentType` (string, 可选): MIME 类型，如 `image/png`、`application/pdf`

### putBuffer
上传 buffer 内容到存储桶。
- `content` (string, **必需**): buffer 内容字符串
- `fileName` (string, **必需**): 存储桶中的文件名
- `targetDir` (string, 可选): 目标目录
- `contentType` (string, 可选): MIME 类型，默认 `application/octet-stream`
- `encoding` (string, 可选): 编码格式，枚举值: `hex` | `base64` | `utf8` | `ascii` | `binary`，默认 `utf8`

### putObjectSourceUrl
通过 URL 下载文件并上传到存储桶。
- `sourceUrl` (string, **必需**): 可下载的文件 URL
- `fileName` (string, 可选): 存储桶中的文件名
- `targetDir` (string, 可选): 目标目录

### getObject
下载存储桶内的文件。
- `objectKey` (string, **必需**): 文件在存储桶中的路径

### getBucket
查询存储桶内的文件列表。
- `Prefix` (string, 可选): 路径前缀过滤，默认根路径

### getObjectUrl
获取文件的带签名下载链接。
- `objectKey` (string, **必需**): 文件在存储桶中的路径

## 图片处理工具

### imageInfo
获取图片元数据信息。
- `objectKey` (string, **必需**): 图片在存储桶中的路径

### assessQuality
评估图片质量分数。
- `objectKey` (string, **必需**): 图片在存储桶中的路径

### aiSuperResolution
AI 超分辨率，提升图片分辨率。
- `objectKey` (string, **必需**): 图片在存储桶中的路径

### aiPicMatting
AI 智能抠图，去除图片背景。
- `objectKey` (string, **必需**): 图片在存储桶中的路径
- `width` (string, 可选): 输出宽度
- `height` (string, 可选): 输出高度

### aiQrcode
识别存储桶内图片中的二维码内容。
- `objectKey` (string, **必需**): COS 对象键完整路径，如 `images/qrcode.jpg`

### waterMarkFont
生成带文字水印的图片。
- `objectKey` (string, **必需**): COS 对象键完整路径，如 `images/photo.jpg`
- `text` (string, 可选): 水印文字内容（支持中文），默认 `test`

## 智能搜索工具

### imageSearchPic
以图搜图，从数据集中检索相似图片。
- `uri` (string, **必需**): 图片地址

### imageSearchText
文本搜图，根据文字描述检索匹配图片。
- `text` (string, **必需**): 检索文本

## 文档与媒体处理工具

### createDocToPdfJob
创建文档转 PDF 处理任务。
- `objectKey` (string, **必需**): 文档在存储桶中的路径

### describeDocProcessJob
查询文档转码任务结果。
- `jobId` (string, **必需**): 任务 ID（通过提交文档任务的响应获取）

### createMediaSmartCoverJob
创建视频智能封面任务。
- `objectKey` (string, **必需**): 视频在存储桶中的路径

### describeMediaJob
查询智能封面任务结果。
- `jobId` (string, **必需**): 任务 ID（通过提交智能封面任务的响应获取）

---

## 方式二：scripts/cos_node.mjs 命令参考

脚本位于 `scripts/cos_node.mjs`，依赖 `cos-nodejs-sdk-v5`（`npm install cos-nodejs-sdk-v5`）。
所有凭证通过环境变量读取。输出 JSON 格式。

### 可用操作

| 操作 | 命令 | 说明 |
|------|------|------|
| upload | `node scripts/cos_node.mjs upload --file <path> --key <key>` | 上传本地文件 |
| put-string | `node scripts/cos_node.mjs put-string --content <text> --key <key> [--content-type <mime>]` | 上传字符串内容 |
| download | `node scripts/cos_node.mjs download --key <key> --output <path>` | 下载文件到本地 |
| list | `node scripts/cos_node.mjs list [--prefix <prefix>] [--max-keys <n>]` | 列出文件 |
| sign-url | `node scripts/cos_node.mjs sign-url --key <key> [--expires <seconds>]` | 获取签名下载链接 |
| delete | `node scripts/cos_node.mjs delete --key <key>` | 删除文件 |
| head | `node scripts/cos_node.mjs head --key <key>` | 查看文件元信息 |

### 返回格式

成功时 `success: true`，退出码 0；失败时 `success: false`，退出码 1。

---

## 方式三：COSCMD 命令参考

依赖 Python，通过 `pip install coscmd` 安装。首次使用需配置（写入 `~/.cos.conf`，后续无需重复）：

```bash
coscmd config -a $TENCENT_COS_SECRET_ID -s $TENCENT_COS_SECRET_KEY -b $TENCENT_COS_BUCKET -r $TENCENT_COS_REGION
```

### 常用命令

| 操作 | 命令 | 说明 |
|------|------|------|
| 上传文件 | `coscmd upload <localpath> <cospath>` | 上传单个文件 |
| 递归上传目录 | `coscmd upload -r <localdir> <cosdir>` | 上传整个目录 |
| 下载文件 | `coscmd download <cospath> <localpath>` | 下载单个文件 |
| 递归下载目录 | `coscmd download -r <cosdir> <localdir>` | 下载整个目录 |
| 列出文件 | `coscmd list [cospath]` | 列出文件，加 `-r` 递归 |
| 删除文件 | `coscmd delete <cospath>` | 删除单个文件 |
| 递归删除 | `coscmd delete -r <cosdir> -f` | 强制递归删除 |
| 签名 URL | `coscmd signurl <cospath> [-t <seconds>]` | 获取带签名的下载链接 |
| 文件信息 | `coscmd info <cospath>` | 查看文件元信息 |
| 复制 | `coscmd copy <source> <dest>` | 桶内/跨桶复制 |
| 移动 | `coscmd move <source> <dest>` | 移动文件（复制+删除源） |

### 全局参数

- `-c <CONFIG_PATH>`：指定配置文件路径（默认 `~/.cos.conf`）
- `-b <BucketName-APPID>`：指定存储桶（覆盖配置文件）
- `-r <Region>`：指定区域
- `-d`：调试模式，输出详细日志

