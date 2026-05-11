# API参考文档

## Python包装器 API

### TencentCOSWrapper 类

#### 初始化
```python
from scripts.cos_wrapper import TencentCOSWrapper

# 使用环境变量
cos = TencentCOSWrapper()

# 使用自定义配置
config = {
    'Region': 'ap-guangzhou',
    'Bucket': 'your-bucket',
    'SecretId': 'your-secret-id',
    'SecretKey': 'your-secret-key'
}
cos = TencentCOSWrapper(config)
```

#### 文件操作
```python
# 上传文件
result = cos.upload_file(local_path, cos_key=None)

# 下载文件
result = cos.download_file(cos_key, local_path=None)

# 列出文件
result = cos.list_files(prefix='', max_keys=100)

# 获取文件URL
result = cos.get_file_url(cos_key, expires=3600)
```

#### 图片处理
```python
# 评估图片质量
result = cos.assess_image_quality(cos_key)

# 提升分辨率
result = cos.enhance_image_resolution(cos_key)

# 去除背景
result = cos.remove_image_background(cos_key)

# 识别二维码
result = cos.detect_qrcode(cos_key)

# 添加文字水印
result = cos.add_text_watermark(cos_key, text)
```

#### 智能搜索
```python
# 文本搜索图片
result = cos.search_by_text(text)

# 以图搜图
result = cos.search_by_image(cos_key)
```

#### 文档处理
```python
# 文档转PDF
result = cos.convert_to_pdf(cos_key)

# 生成视频封面
result = cos.generate_video_cover(cos_key)
```

### 返回结果格式
所有方法返回字典格式的结果：
```python
{
    'success': True,  # 或 False
    'tool': 'tool_name',
    'params': {...},  # 调用参数
    'message': '操作描述',
    'data': {...},    # 返回数据
    'error': '错误信息（如果失败）'
}
```

## 命令行工具

### 基本用法
```bash
# 上传文件
python3 scripts/cos_wrapper.py --action upload --local-path file.jpg --cos-key remote/key.jpg

# 下载文件
python3 scripts/cos_wrapper.py --action download --cos-key remote/key.jpg --local-path local.jpg

# 列出文件
python3 scripts/cos_wrapper.py --action list --prefix images/

# 搜索图片
python3 scripts/cos_wrapper.py --action search-text --text "风景照片"
```

### 可用操作
- `upload`: 上传文件
- `download`: 下载文件
- `list`: 列出文件
- `url`: 获取文件URL
- `assess-quality`: 评估图片质量
- `search-text`: 文本搜索图片

## MCP工具参考

### 存储操作工具
- `putObject`: 上传对象
- `getObject`: 下载对象
- `getBucket`: 列出对象
- `deleteObject`: 删除对象
- `getObjectUrl`: 获取对象URL

### 图片处理工具
- `assessQuality`: 评估图片质量
- `aiSuperResolution`: AI超分辨率
- `aiPicMatting`: AI抠图
- `aiQrcode`: AI二维码识别
- `waterMarkFont`: 文字水印

### 搜索工具
- `imageSearchText`: 文本搜图
- `imageSearchPic`: 以图搜图

### 文档工具
- `docProcess`: 文档处理
- `createMediaSmartCoverJob`: 创建智能封面
