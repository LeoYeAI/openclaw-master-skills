# 配置说明

## 📋 快速配置指南

### 1. 获取Notion API Token

1. 访问 [Notion Integrations](https://www.notion.so/my-integrations)
2. 点击 "New integration"
3. 填写名称并选择工作空间
4. 复制 **Internal Integration Token**（格式：`secret_xxx`）

### 2. 设置环境变量

```bash
# 编辑 ~/.bashrc 或 ~/.zshrc
echo 'export NOTION_API_KEY="secret_xxx"' >> ~/.bashrc
source ~/.bashrc

# 可选：设置默认数据库ID
echo 'export NOTION_DATABASE_ID="your_database_id"' >> ~/.bashrc
source ~/.bashrc
```

### 3. 分享数据库给Integration

1. 打开你的Notion数据库
2. 点击右上角 `...` 菜单
3. 选择 "Connections"（连接）
4. 搜索并选择你创建的integration

### 4. 安装依赖

```bash
# 安装Python依赖
pip install requests

# 下载BBDown（B站下载器）
curl -L -o /tmp/BBDown.zip "https://github.com/nilaoda/BBDown/releases/download/1.6.3/BBDown_1.6.3_20240814_linux-x64.zip"
unzip /tmp/BBDown.zip -d /tmp/
chmod +x /tmp/BBDown

# 安装FFmpeg（BBDown依赖）
apt-get install ffmpeg
```

## 🔧 验证配置

### 测试Notion API连接

```bash
python3 -c "
import requests
import os

token = os.environ.get('NOTION_API_KEY')
headers = {
    'Authorization': f'Bearer {token}',
    'Notion-Version': '2022-06-28'
}

response = requests.get('https://api.notion.com/v1/users', headers=headers)
if response.status_code == 200:
    print('✅ Notion API连接成功')
else:
    print(f'❌ 连接失败: {response.status_code}')
"
```

### 测试BBDown

```bash
/tmp/BBDown --version
```

### 测试FFmpeg

```bash
ffmpeg -version
```

## 📝 使用示例

### 基本使用

```bash
cd skills/bilibili-cc-to-notion/scripts

# 使用环境变量中的token和数据库ID
export NOTION_API_KEY="secret_xxx"
export NOTION_DATABASE_ID="your_database_id"

python3 bilibili_to_notion.py \
  --url "https://www.bilibili.com/video/BV1xx411c7mW" \
  --database-id "$NOTION_DATABASE_ID" \
  --tags "Python,机器学习,教程"
```

### 指定token和数据库ID

```bash
python3 create_notion_notes.py \
  --token "secret_xxx" \
  --database-id "your_database_id" \
  --video-title "测试视频" \
  --video-url "https://www.bilibili.com/video/BV1xx411c7mW" \
  --segments '[{"start_time": "00:00:00,000", "end_time": "00:00:03,000", "text": "测试内容", "concepts": ["测试"], "is_key_point": true}]' \
  --tags "测试,演示"
```

## 🔍 故障排除

### 问题1: Notion API返回401错误

**原因**: API token无效或未正确设置

**解决方案**:
```bash
# 检查环境变量
echo $NOTION_API_KEY

# 重新设置
export NOTION_API_KEY="secret_xxx"
```

### 问题2: 数据库权限错误

**原因**: Integration未分享到数据库

**解决方案**:
1. 打开Notion数据库
2. 点击 `...` → Connections
3. 搜索并添加你的integration

### 问题3: BBDown下载失败

**原因**: 视频需要登录或没有字幕

**解决方案**:
1. 使用公开视频测试
2. 或登录B站账号后重试

### 问题4: 文件大小限制

**原因**: Notion有文件大小限制

**解决方案**:
- 免费工作空间: 5MB/文件
- 付费工作空间: 5GB/文件

## 📚 参考文档

- [Notion API文档](https://developers.notion.com/)
- [BBDown项目](https://github.com/nilaoda/BBDown)
- [Notion Integrations](https://www.notion.so/my-integrations)
