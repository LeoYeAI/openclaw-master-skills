# document-parser

高精度文档解析技能，从 PDF、图片、Word 文档中提取结构化数据。

## 用途
- 解析 PDF、图片 (JPG/PNG)、Word 文档
- 版面分析与结构提取
- 表格识别（输出 HTML/Markdown）
- OCR 文字识别
- 印章检测
- 目录提取

## 命令

### 解析文档
```
document-parser parse <文件路径> [选项]
```

示例：
```
document-parser parse C:\docs\report.pdf
document-parser parse C:\docs\scan.jpg --layout --table
document-parser parse C:\docs\contract.docx --output markdown
```

### 查询任务状态
```
document-parser status <任务 ID>
```

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| 文件路径 | PDF/图片/Word 文件路径 | `C:\docs\report.pdf` |
| --layout | 启用版面分析 | `--layout` |
| --table | 启用表格识别 | `--table` |
| --seal | 启用印章检测 | `--seal` |
| --output | 输出格式 (json/markdown/both) | `--output markdown` |
| --pages | 页码范围 | `--pages 1-5,8,10-12` |

## 配置

### 方式一：环境变量
```
DOCUMENT_PARSER_API_KEY=your_api_key
DOCUMENT_PARSER_BASE_URL=http://47.111.146.164:8088/taidp/v1/idp/general_parse
```

### 方式二：配置文件
在技能目录创建 `config.json`：
```json
{
  "api_key": "your_api_key",
  "base_url": "http://47.111.146.164:8088/taidp/v1/idp/general_parse"
}
```

## 输出格式

返回结构化 JSON 包含：
- **pages**: 解析后的页面数组
- **elements**: 版面元素（文本、表格、图片等）
- **markdown**: Markdown 格式文本
- **data**: 数据统计摘要

## 依赖
- requests
- python-docx (Word 支持)
- Pillow (图片处理)

## 错误码

| 错误码 | 消息 | 说明 |
|--------|------|------|
| 10000 | Success | 识别成功 |
| 10001 | Missing parameter | 参数缺失 |
| 10002 | Invalid parameter | 非法参数 |
| 10003 | Invalid file | 文件格式非法 |
| 10004 | Failed to recognize | 识别失败 |
| 10005 | Internal error | 内部错误 |
