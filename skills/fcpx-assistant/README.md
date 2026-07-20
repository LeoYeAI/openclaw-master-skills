# FCPX Assistant - Final Cut Pro 自动视频生产助手

> 从文案到发布，全自动视频生产线 🎬

---

## 🚀 快速开始

### 一键生成并发布视频

```bash
bash scripts/auto-video-from-topic.sh \
    --topic "如何制作一杯完美的咖啡" \
    --publish bilibili \
    --title "咖啡教程" \
    --tags "咖啡，教程"
```

---

## 📦 安装依赖

### 系统依赖

```bash
# 安装 ffmpeg（视频处理核心）
brew install homebrew-ffmpeg/ffmpeg/ffmpeg

# 安装 jq（JSON 处理）
brew install jq

# 安装 trash（安全删除）
brew install trash
```

### Python 依赖（可选，用于 B 站上传）

```bash
pip3 install --break-system-packages biliup
```

### 外部服务

#### 1. Qwen TTS WebUI（配音必需）

详细部署指南见 [Qwen TTS 部署说明](#-qwen-tts-webui-部署指南)

**快速启动：**
```bash
# 假设你已经克隆了 qwen-tts-webui 项目
cd ~/qwen-tts-webui
python3 app.py --port 7860
```

**验证服务：**
```bash
curl http://localhost:7860/gradio_api/info
```

#### 2. B 站登录（上传必需）

```bash
# 登录 B 站
biliup login

# 选择"扫码登录"，用手机 B 站 APP 扫码

# 验证登录
biliup renew
```

---

## 🎬 核心功能

### 1. AI 文案自动生成

```bash
bash scripts/ai-script-generator.sh \
    --topic "你的视频主题" \
    --style vlog \
    --duration 60 \
    --output script.txt
```

**支持风格：** `vlog`, `科普`, `教程`, `带货`, `故事`

**支持平台：** `general`, `tiktok`, `youtube`, `bilibili`

### 2. 素材搜集

```bash
bash scripts/media-collector.sh \
    --keywords "nature ocean sunset" \
    --count 10 \
    --output ./my-project
```

### 3. TTS 配音

```bash
# 合并模式（推荐，音色一致）
bash scripts/tts-voiceover.sh \
    --script-file script.txt \
    --output voiceover \
    --merge \
    --cleanup
```

### 4. 自动成片

```bash
bash scripts/auto-video-maker.sh \
    --project ./my-project \
    --script-file script.txt \
    --voiceover voiceover \
    --style vlog \
    --output final.mp4 \
    --cleanup
```

### 5. 自动上传发布

```bash
bash scripts/auto-publish.sh \
    --video final.mp4 \
    --platform bilibili \
    --title "视频标题" \
    --tags "标签 1，标签 2"
```

---

## 🔧 Qwen TTS WebUI 部署指南

### 系统要求

- **内存**: 至少 8GB（推荐 16GB+）
- **GPU**: 可选（有 GPU 时生成速度更快）
- **磁盘**: 约 5GB（模型文件）

### 部署步骤

1. **克隆项目**
```bash
git clone https://github.com/your-org/qwen-tts-webui.git
cd qwen-tts-webui
```

2. **安装依赖**
```bash
pip3 install -r requirements.txt
```

3. **下载模型**
```bash
python3 scripts/download_model.py --model Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice
```

4. **启动服务**
```bash
python3 app.py --port 7860
```

5. **验证服务**
```bash
curl http://localhost:7860/gradio_api/info
```

### 配置说明

在 `tts-voiceover.sh` 中可修改：

```bash
TTS_HOST="http://127.0.0.1:7860"  # TTS 服务地址
INSTRUCT="活泼开朗的年轻男声，语调轻快有活力"  # 声音特征
MODEL="Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"  # 模型
```

### 替代方案

如果不想部署 Qwen TTS：

1. 使用其他 TTS 服务（修改 API 调用）
2. 使用本地录音文件
3. 跳过配音，仅生成字幕视频

---

## 📁 项目结构

```
fcpx-assistant/
├── SKILL.md                  # 技能定义
├── README.md                 # 本文档
├── AUTO_PUBLISH_README.md    # B 站发布配置指南
├── scripts/
│   ├── ai-script-generator.sh      # AI 文案生成
│   ├── media-collector.sh          # 素材搜集
│   ├── tts-voiceover.sh            # TTS 配音
│   ├── auto-video-maker.sh         # 自动成片
│   ├── auto-publish.sh             # 自动发布
│   ├── auto-video-from-topic.sh    # 一键全流程
│   └── ... (其他辅助脚本)
└── outputs/                  # 输出目录（自动生成）
```

---

## 🎯 使用示例

### 示例 1：快速生成 Vlog

```bash
bash scripts/auto-video-from-topic.sh \
    --topic "今天的旅行见闻" \
    --style vlog \
    --duration 90
```

### 示例 2：生成并发布到 B 站

```bash
bash scripts/auto-video-from-topic.sh \
    --topic "如何学习编程" \
    --style 教程 \
    --publish bilibili \
    --title "编程入门教程" \
    --tags "编程，教程，入门"
```

### 示例 3：分步执行

```bash
# 1. 生成文案
bash scripts/ai-script-generator.sh --topic "咖啡制作" --style 教程

# 2. 搜集素材
bash scripts/media-collector.sh --keywords "coffee making" --count 10

# 3. 生成配音
bash scripts/tts-voiceover.sh --script-file script.txt --merge

# 4. 自动成片
bash scripts/auto-video-maker.sh --project . --voiceover voiceover

# 5. 上传 B 站
bash scripts/auto-publish.sh --video output.mp4 --platform bilibili
```

---

## ⚠️ 注意事项

1. **TTS 服务必须运行**：配音功能依赖 Qwen TTS WebUI
2. **B 站登录有效期**：Cookie 约 180 天过期，需定期更新
3. **素材版权**：Pexels 素材免费可商用，但仍需遵守许可协议
4. **视频时长**：建议控制在 1-10 分钟，过长会增加处理时间
5. **磁盘空间**：确保有足够空间存储临时文件和输出视频

---

## 🐛 故障排查

### TTS 服务无法连接

```bash
# 检查服务是否运行
curl http://localhost:7860/gradio_api/info

# 如果失败，启动服务
cd ~/qwen-tts-webui && python3 app.py --port 7860
```

### B 站上传失败

```bash
# 检查登录状态
biliup renew

# 重新登录
biliup login
```

### ffmpeg 错误

```bash
# 确保安装完整版 ffmpeg
brew uninstall ffmpeg
brew install homebrew-ffmpeg/ffmpeg/ffmpeg
```

---

## 📝 更新日志

### v2.0.0 (2026-03-29)
- ✨ 新增 AI 文案自动生成功能
- ✨ 新增 B 站自动上传发布功能
- ✨ 新增一键全流程脚本
- 🐛 修复 TTS 音色不一致问题（添加 --merge 模式）
- 🐛 修复临时文件清理问题
- 📚 完善依赖说明和部署指南

### v1.0.0
- 初始版本：基础视频剪辑功能

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

**作者**: Steve & Steven  
**许可**: MIT

---

*Made with ❤️ for Final Cut Pro X users*
