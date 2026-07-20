# 🚀 自动发布功能配置指南

从主题到发布，全自动视频生产线！

---

## 🎬 一键完成全流程

```bash
# 最简单用法：生成视频并发布到 B 站
bash scripts/auto-video-from-topic.sh \
    --topic "如何制作一杯完美的咖啡" \
    --publish bilibili \
    --title "咖啡教程" \
    --tags "咖啡，教程"
```

**自动完成：**
1. ✅ AI 生成文案
2. ✅ 搜集素材
3. ✅ TTS 配音
4. ✅ 自动成片
5. ✅ 上传发布

---

## 📤 平台配置

### 1️⃣ 创建配置目录

```bash
mkdir -p ~/.fcpx-assistant/publish
chmod 700 ~/.fcpx-assistant/publish
```

### 2️⃣ B 站配置

创建文件 `~/.fcpx-assistant/publish/bilibili.json`:

```json
{
  "username": "你的 B 站账号",
  "password": "你的密码（建议使用 cookie）",
  "cookie": "登录后复制的 cookie（推荐）",
  "upload_source": 1
}
```

**获取 Cookie 方法：**
1. 登录 https://www.bilibili.com
2. 打开开发者工具（F12）
3. 复制请求头中的 Cookie 值

**安装上传工具：**
```bash
pip install biliup
biliup login  # 登录 B 站
```

### 3️⃣ YouTube 配置

创建文件 `~/.fcpx-assistant/publish/youtube.json`:

```json
{
  "client_secrets": "/path/to/client_secret.json",
  "token": "/path/to/token.json"
}
```

**获取 API 凭证：**
1. 访问 https://console.cloud.google.com
2. 创建项目，启用 YouTube Data API
3. 创建 OAuth 2.0 凭证
4. 下载 client_secret.json

### 4️⃣ 抖音配置

创建文件 `~/.fcpx-assistant/publish/tiktok.json`:

```json
{
  "cookie": "登录后复制的 cookie"
}
```

**获取 Cookie：**
1. 登录 https://creator.douyin.com
2. 打开开发者工具（F12）
3. 复制 Cookie 值

### 5️⃣ 小红书配置

创建文件 `~/.fcpx-assistant/publish/xiaohongshu.json`:

```json
{
  "cookie": "登录后复制的 cookie"
}
```

---

## 🔒 安全提示

1. **设置文件权限：**
   ```bash
   chmod 600 ~/.fcpx-assistant/publish/*.json
   ```

2. **不要提交到 Git：**
   ```bash
   echo "*.json" >> ~/.fcpx-assistant/publish/.gitignore
   ```

3. **建议使用 Cookie 而非密码**

4. **定期更新 Cookie**（有过期时间）

---

## 📋 使用示例

### 只生成视频，不发布

```bash
bash scripts/auto-video-from-topic.sh \
    --topic "今天的旅行见闻" \
    --style vlog \
    --duration 90
```

### 生成并发布到不同平台

```bash
# B 站
bash scripts/auto-video-from-topic.sh \
    --topic "教程内容" \
    --publish bilibili \
    --title "超详细教程" \
    --tags "教程，干货"

# YouTube
bash scripts/auto-video-from-topic.sh \
    --topic "Tutorial Content" \
    --publish youtube \
    --title "Amazing Tutorial" \
    --tags "tutorial,howto"

# 抖音（竖屏）
bash scripts/auto-video-from-topic.sh \
    --topic "快速技巧" \
    --style fast \
    --duration 30 \
    --publish tiktok \
    --title "30 秒学会"
```

### 手动上传已有视频

```bash
bash scripts/auto-publish.sh \
    --video ./output/final.mp4 \
    --platform bilibili \
    --title "我的视频" \
    --tags "vlog，日常" \
    --description "这是视频描述"
```

---

## 🛠️ 故障排查

### B 站上传失败

```bash
# 检查 biliup 是否安装
which biliup

# 检查登录状态
biliup login

# 查看详细错误
biliup upload video.mp4 --debug
```

### Cookie 过期

重新登录平台，复制新的 Cookie 值更新配置文件。

### 视频格式不支持

使用 auto-video-maker.sh 生成的视频已优化为各平台兼容格式。
如手动上传失败，检查：
- 分辨率（B 站：16:9 或 9:16，抖音：9:16）
- 码率（建议 5-10 Mbps）
- 格式（MP4 H.264）

---

## 📞 需要帮助？

查看完整文档：
```bash
bash scripts/auto-publish.sh --help
bash scripts/auto-video-from-topic.sh --help
```

---

*Made with ❤️ by Steve & Steven*
