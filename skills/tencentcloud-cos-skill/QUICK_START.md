# 腾讯云COS技能快速启动指南 🚀

本指南将帮助您在5分钟内启动并使用腾讯云COS Clawdbot技能。

## ⏱️ 5分钟快速启动

### 步骤1: 安装技能
```bash
# 克隆或下载技能
git clone <repository-url>
cd tencent-cos

# 运行安装脚本
chmod +x install.sh
./install.sh
```

### 步骤2: 获取腾讯云COS配置
1. 登录 [腾讯云控制台](https://console.cloud.tencent.com/cos)
2. 创建或选择存储桶，记录：
   - **区域**: 如 `ap-guangzhou`
   - **存储桶名称**: 如 `my-bucket-123456`
3. 进入 [访问管理](https://console.cloud.tencent.com/cam/capi)
4. 创建API密钥，记录：
   - **SecretId**: `AKIDxxxxxxxxxxxxxxxxxxxxxxxx`
   - **SecretKey**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 步骤3: 配置技能
```bash
# 复制环境变量模板
cp config/env.template .env

# 编辑.env文件，填入您的配置
nano .env  # 或使用您喜欢的编辑器
```

`.env`文件内容示例：
```bash
export TENCENT_COS_REGION="ap-guangzhou"
export TENCENT_COS_BUCKET="my-bucket-123456"
export TENCENT_COS_SECRET_ID="AKIDxxxxxxxxxxxxxxxxxxxxxxxx"
export TENCENT_COS_SECRET_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TENCENT_COS_DEBUG="false"
```

### 步骤4: 测试安装
```bash
# 运行测试脚本
python3 test_skill.py

# 运行示例程序
python3 examples/basic_usage.py
```

### 步骤5: 在Clawdbot中使用
1. 确保Clawdbot正在运行
2. 在Clawdbot中尝试以下命令：
   ```
   上传文件到腾讯云COS: /path/to/your/file.jpg
   列出我的COS文件
   评估这张图片质量: image.jpg
   ```

## 🎯 常用命令速查

### 文件管理
```
# 上传文件
上传文件到COS: /home/user/photos/vacation.jpg

# 下载文件  
从COS下载文件: photos/vacation.jpg

# 列出文件
列出COS中的文件
列出图片文件夹: images/

# 删除文件
删除COS文件: old-file.txt
```

### 图片处理
```
# 质量评估
评估图片质量: product-image.jpg

# 提升分辨率
提升这张图片分辨率: low-quality.jpg

# 去除背景
去除图片背景: portrait.png

# 识别二维码
识别二维码: qrcode-image.jpg

# 添加水印
添加水印到图片: original.jpg 文字: "公司LOGO"
```

### 智能搜索
```
# 文本搜索
搜索风景图片
搜索美食照片

# 图片搜索
搜索相似图片: reference-image.jpg
```

### 文档处理
```
# 文档转换
转换文档为PDF: report.docx

# 视频处理
生成视频封面: presentation.mp4
```

## 🔧 故障排除

### 常见问题

#### 1. 认证失败
```
错误: 缺少必要的腾讯云COS配置
解决方案: 检查.env文件中的SecretId和SecretKey是否正确
```

#### 2. 权限不足
```
错误: 操作被拒绝
解决方案: 确保API密钥有对应存储桶的读写权限
```

#### 3. 网络连接问题
```
错误: 连接超时
解决方案: 检查网络连接，确认区域配置正确
```

### 调试模式
```bash
# 启用详细日志
export TENCENT_COS_DEBUG="true"

# 重新测试
python3 test_skill.py
```

## 📱 移动端使用提示

### 通过手机使用技能
1. **文件上传**: 可以直接从手机相册上传图片
2. **图片处理**: 处理手机拍摄的照片
3. **文档管理**: 备份手机中的文档到云端

### 语音命令示例
```
"嘿Clawdbot，帮我把这张照片上传到腾讯云"
"评估一下我刚拍的照片质量"
"搜索我去年旅行的照片"
```

## 🚀 高级功能快速启用

### 批量处理
```python
# 批量上传文件夹中的所有图片
from scripts.cos_wrapper import TencentCOSWrapper
import os

cos = TencentCOSWrapper()
folder = '/path/to/photos'

for filename in os.listdir(folder):
    if filename.endswith(('.jpg', '.png')):
        cos.upload_file(os.path.join(folder, filename), f'photos/{filename}')
        print(f"已上传: {filename}")
```

### 自动化工作流
```python
# 自动处理新上传的图片
def process_new_image(image_path):
    cos = TencentCOSWrapper()
    
    # 1. 上传原始图片
    cos.upload_file(image_path, f'raw/{os.path.basename(image_path)}')
    
    # 2. 评估质量
    quality = cos.assess_image_quality(f'raw/{os.path.basename(image_path)}')
    
    # 3. 根据质量决定是否优化
    if quality.get('score', 0) < 80:
        cos.enhance_image_resolution(f'raw/{os.path.basename(image_path)}')
    
    # 4. 添加水印
    cos.add_text_watermark(f'raw/{os.path.basename(image_path)}', 'Processed')
    
    print("图片处理完成")
```

## 📞 获取帮助

### 官方资源
- **腾讯云COS文档**: https://cloud.tencent.com/document/product/436
- **cos-mcp项目**: https://github.com/Tencent/cos-mcp
- **Clawdbot社区**: https://discord.com/invite/clawd

### 社区支持
- **GitHub Issues**: 报告问题或请求功能
- **Discord频道**: 实时交流和技术支持
- **文档贡献**: 帮助改进本文档

## 🎉 恭喜！

您已成功设置腾讯云COS Clawdbot技能。现在可以：

1. ✅ **备份文件**到云端存储
2. ✅ **智能处理**图片和文档  
3. ✅ **快速搜索**您的数字资产
4. ✅ **自动化**重复性任务

开始探索更多可能性吧！ 🚀

---
*需要更多帮助？查看完整文档: [README.md](README.md)*
*有建议或问题？加入我们的社区讨论！*