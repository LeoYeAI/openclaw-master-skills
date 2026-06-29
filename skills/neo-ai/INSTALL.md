# Neodomain AI Skill 安装指南

## 简介

Neodomain AI 是一个用于生成图片和视频的 AI 服务集成技能。支持文生图、图生视频、运动控制等功能。

## 安装方式

### 方式一：通过 ClawHub 安装（推荐）

```bash
# 安装 ClawHub CLI（如果没有）
npm i -g clawhub

# 安装 neodomain-ai skill
clawhub install neodomain-ai
```

### 方式二：手动安装

```bash
# 克隆或下载 skill 到本地
# skill 目录结构：
# neodomain-ai/
#   ├── SKILL.md        # 技能说明文档
#   └── scripts/        # Python 脚本目录
#       ├── login.py           # 登录获取 token
#       ├── generate_image.py  # 图片生成
#       ├── generate_image_ref.py  # 参考图图片生成
#       ├── generate_video.py  # 视频生成
#       ├── motion_control.py  # 运动控制
#       ├── upload_oss.py      # OSS 上传
#       ├── image_models.py    # 获取可用图片模型
#       └── video_models.py    # 获取可用视频模型
```

## 配置步骤

### 1. 设置环境变量

```bash
# 方式一：临时设置
export NEODOMAIN_ACCESS_TOKEN="your_token_here"

# 方式二：永久设置（添加到 ~/.zshrc 或 ~/.bashrc）
echo 'export NEODOMAIN_ACCESS_TOKEN="your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

### 2. 首次登录获取 Token

如果还没有 token，需要通过手机号登录获取：

```bash
# 发送验证码（替换为你的手机号）
python3 ~/.openclaw/skills/neodomain-ai/scripts/login.py --send-code --contact "你的手机号"

# 使用验证码登录
python3 ~/.openclaw/skills/neodomain-ai/scripts/login.py --login --contact "你的手机号" --code "验证码"
```

登录成功后，会输出 access token，请将其保存到环境变量中。

## 使用示例

### 图片生成

```bash
# 基础文生图
python3 ~/.openclaw/skills/neodomain-ai/scripts/generate_image.py \
  --prompt "一个美丽的女孩" \
  --model "doubao-seedream-4-0-250828" \
  --aspect-ratio "16:9"

# 使用参考图生成（支持多张，最多10张）
python3 ~/.openclaw/skills/neodomain-ai/scripts/generate_image_ref.py \
  --prompt "一个女孩在看书" \
  --reference-image "https://example.com/ref1.jpg" \
  --reference-image "https://example.com/ref2.jpg" \
  --model "doubao-seedream-4-0-250828"
```

### 视频生成

```bash
# 图生视频
python3 ~/.openclaw/skills/neodomain-ai/scripts/generate_video.py \
  --prompt "镜头缓慢推进" \
  --first-frame "https://example.com/image.jpg" \
  --model "seedance-1-5-pro" \
  --generate-audio true
```

### 查看可用模型

```bash
# 查看图片模型
python3 ~/.openclaw/skills/neodomain-ai/scripts/image_models.py

# 查看视频模型
python3 ~/.openclaw/skills/neodomain-ai/scripts/video_models.py
```

## 常用参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--prompt` | 生成描述 | 必填 |
| `--model` | 模型名称 | 见下方 |
| `--aspect-ratio` | 画面比例 | 1:1 |
| `--size` | 图片尺寸 | 2K |
| `--reference-image` | 参考图（可多次使用） | 无 |
| `--token` | Access token | 环境变量 |

### 默认模型

- 图片生成: `doubao-seedream-4-0-250828`
- 图片生成(参考图): `gemini-3.1-flash-image-preview`

## 故障排除

### Token 过期

如果遇到认证错误，需要重新登录获取新 token：

```bash
python3 ~/.openclaw/skills/neodomain-ai/scripts/login.py --send-code --contact "你的手机号"
# 输入验证码
python3 ~/.openclaw/skills/neodomain-ai/scripts/login.py --login --contact "你的手机号" --code "验证码"
```

### 模型不存在

使用前先查看可用模型：

```bash
python3 ~/.openclaw/skills/neodomain-ai/scripts/image_models.py
python3 ~/.openclaw/skills/neodomain-ai/scripts/video_models.py
```

## 相关文档

- [SKILL.md](./SKILL.md) - 完整技能文档
- [ClawHub](https://clawhub.com) - 技能市场
