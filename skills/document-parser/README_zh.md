# 文档解析 (Document Parser)

> OpenClaw Skill - 高精度文档解析

从 PDF、图片、Word 文档中提取结构化数据。

## 功能特性

- ✅ **多格式支持**: PDF、图片 (JPG/PNG)、Word 文档
- ✅ **版面分析**: 自动检测和解析文档结构元素
- ✅ **表格识别**: 提取表格并输出 HTML 和 Markdown 格式
- ✅ **OCR 识别**: 识别扫描件和图片中的文字
- ✅ **印章检测**: 检测文档中的印章和签章
- ✅ **目录提取**: 从文档中提取目录结构
- ✅ **跨页合并**: 自动合并跨页面的内容

## 快速开始

### 安装

```bash
# 通过 ClawHub 安装
openclaw skills install document-parser

# 或手动安装（本地开发）
cd E:\skills\document-parser
pip install -r requirements.txt
```

### 配置

**方式一：环境变量（推荐）**
```bash
# Windows PowerShell
$env:DOCUMENT_PARSER_API_KEY="your_api_key"
setx DOCUMENT_PARSER_API_KEY "your_api_key"

# 可选：自定义 API 地址
$env:DOCUMENT_PARSER_BASE_URL="http://your-server:8088/taidp/v1/idp/general_parse"
```

**方式二：配置文件**
```bash
cd E:\skills\document-parser
copy config.example.json config.json
# 编辑 config.json 填入你的 API Key
```

### 使用方法

#### 解析文档
```bash
# 基础解析
document-parser parse "C:\docs\report.pdf"

# 启用版面分析和表格识别
document-parser parse "C:\docs\report.pdf" --layout --table

# 指定输出格式
document-parser parse "C:\docs\scan.jpg" --output markdown

# 指定页码范围
document-parser parse "C:\docs\book.pdf" --pages 1-5,10-15
```

#### 查询任务状态
```bash
document-parser status <task_id>
```

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | string | 是 | PDF/图片/Word 文件路径 |
| --layout | flag | 否 | 启用版面分析 |
| --table | flag | 否 | 启用表格识别 |
| --seal | flag | 否 | 启用印章检测 |
| --output | string | 否 | 输出格式：json/markdown/both |
| --pages | string | 否 | 页码范围，如 "1-5,8,10-12" |

## 输出格式

返回结构化 JSON 包含：

```json
{
  "code": 10000,
  "message": "Success",
  "request_id": "xxx-xxx-xxx",
  "elapsed_time": 8.5,
  "pages": [
    {
      "page_no": 1,
      "height": 1654,
      "width": 1169,
      "elements": [...]
    }
  ],
  "markdown": "解析后的 Markdown 文本"
}
```

## 支持的文档元素

| 类型 | 说明 |
|------|------|
| DocumentTitle | 文档标题 |
| LevelTitle | 层级标题 |
| Paragraph | 段落 |
| Table | 表格 |
| Image | 图片 |
| PageHeader | 页眉 |
| PageFooter | 页脚 |
| Seal | 印章 |
| Formula | 公式 |
| TableOfContents | 目录 |

## 错误码

| 错误码 | 消息 | 说明 |
|--------|------|------|
| 10000 | Success | 识别成功 |
| 10001 | Missing parameter | 参数缺失 |
| 10002 | Invalid parameter | 非法参数 |
| 10003 | Invalid file | 文件格式非法 |
| 10004 | Failed to recognize | 识别失败 |
| 10005 | Internal error | 内部错误 |

## 示例

### 解析 PDF 并提取表格
```bash
document-parser parse "C:\docs\financial_report.pdf" --table --output markdown
```

### 解析扫描件并启用 OCR
```bash
document-parser parse "C:\docs\scanned_contract.jpg" --layout
```

### 解析 Word 文档
```bash
document-parser parse "C:\docs\manual.docx" --output json
```

## 依赖

- Python 3.8+
- requests>=2.28.0
- python-docx>=0.8.11
- Pillow>=9.0.0

## 许可证

MIT License

## 支持

如有问题请提交 Issue 或联系作者。
