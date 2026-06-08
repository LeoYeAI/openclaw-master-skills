# Local AI Search

> 本地知识库 AI 搜索，支持 100G-1T 文件的全文检索和自然语言查询

[![Skill](https://img.shields.io/badge/Skill-Local%20AI%20Search-blue)](https://github.com/khoj-ai/khoj)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 触发条件

**当用户说以下内容时，调用此 Skill：**
- "帮我在本地搜索..."
- "帮我在本电脑搜索..."
- "帮我在某个文件夹中搜索..."
- "搜索本地文件..."
- "搜索我的文档..."
- 或任何涉及**本地/本机/文件夹内容检索**的请求

## 快速开始

### 安装

```bash
# 安装依赖
pip install khoj "markitdown[xlsx,pptx]"

# 配置 API Key
export OPENAI_API_KEY="your-api-key"
# 或 DeepSeek
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.deepseek.com/v1"
```

### 使用

```bash
# 启动服务
local-ai-search start

# 转换文档
local-ai-search convert ~/Documents/source -o ~/Documents/converted

# 索引到知识库
local-ai-search index ~/Documents/converted

# 查询
local-ai-search query "第三季度销售数据"
```

## 特性

- ✅ 支持 100G-1T 大规模文件
- ✅ 支持 xlsx, xls, pptx, ppt, docx, doc, pdf, md, txt, csv 等格式
- ✅ 本地 OCR 支持扫描版 PDF（使用 Tesseract，无需云 API）
- ✅ 自然语言查询
- ✅ 云端 LLM API（无需本地大模型）
- ✅ 精确定位到源文件位置
- ✅ 轻量级部署（8GB+ RAM 友好）
- ✅ 内存占用仅 ~70MB

## 支持的文件格式

| 格式 | 说明 | 支持状态 |
|------|------|----------|
| `.xlsx`, `.xls` | Excel 表格 | ✅ 支持 |
| `.pptx`, `.ppt` | PowerPoint 演示文稿 | ✅ 支持 |
| `.docx` | Word 文档 (2007+) | ✅ 支持 |
| `.doc` | Word 文档 (97-2003) | ✅ 支持 (需 LibreOffice) |
| `.pdf` | PDF 文档 | ✅ 支持 (含扫描版 OCR) |
| `.md` | Markdown 文档 | ✅ 支持 |
| `.txt` | 纯文本 | ✅ 支持 |
| `.csv` | CSV 数据 | ✅ 支持 |

### 不支持的文件格式

以下格式会被自动跳过：

| 类别 | 格式 | 原因 |
|------|------|------|
| 图片 | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.svg`, `.webp` | 二进制图片，无文本内容 |
| 音频 | `.mp3`, `.wav`, `.aac`, `.flac`, `.pcm` | 音频文件，需语音识别 |
| 视频 | `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm` | 视频文件，需视频处理 |
| 代码 | `.js`, `.py`, `.ts`, `.java`, `.go`, `.html`, `.css` | 代码文件，通常不需要索引 |
| 压缩包 | `.zip`, `.rar`, `.7z`, `.tar`, `.gz` | 压缩文件，需先解压 |
| 其他 | `.rtf`, `.mat`, `.db`, `.sqlite`, `.dll`, `.so` | 不常见或二进制格式 |

## 依赖安装

```bash
# 基础依赖
pip install khoj "markitdown[xlsx,pptx]" requests

# PDF 转图片（用于 OCR）
pip install pdf2image

# 本地 OCR（扫描版 PDF 必需）
pip install pytesseract

# macOS 安装 Tesseract
brew install tesseract tesseract-lang

# Ubuntu 安装 Tesseract
sudo apt install tesseract-ocr tesseract-ocr-chi-sim

# .doc 文件支持（可选）
# macOS
brew install libreoffice
# Ubuntu
sudo apt install libreoffice
```

## 文件结构

```
~/.agents/skills/local-ai-search/
├── SKILL.md              # 完整文档
├── khoj_cli.py           # CLI 工具
├── config.yaml           # 配置文件
├── requirements.txt      # 依赖
└── scripts/
    ├── start_server.sh   # 启动脚本
    ├── convert.py        # 转换脚本
    └── query.py          # 查询脚本
```

## 系统要求

- Python 3.10+
- 8GB+ 可用内存
- 足够的磁盘空间（文档大小的 25-40%）

## 文档

完整文档请参阅 [SKILL.md](SKILL.md)

## 许可证

MIT License