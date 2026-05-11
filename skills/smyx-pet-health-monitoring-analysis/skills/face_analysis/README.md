# 中医面诊分析工具 (face-analysis)

## 技能介绍
这是一个基于AI的中医面诊分析技能，可以通过面部视频自动分析健康状况，返回结构化的诊断结果和养生建议。

## 快速开始
### 1. 配置API信息
编辑 `scripts/config.py`，设置你的API地址和密钥：
```python
DEFAULT_API_URL = "https://your-api-server.com/api/v1/face-analysis"
DEFAULT_API_KEY = "your-api-key-here"
```

### 2. 分析本地视频
```bash
python scripts/face_analysis.py --input /path/to/your/video.mp4
```

### 3. 分析网络视频
```bash
python scripts/face_analysis.py --url https://example.com/video.mp4
```

## 功能特性
- ✅ 支持本地MP4视频上传
- ✅ 支持网络视频URL分析
- ✅ 三种输出详细程度：精简/标准/完整
- ✅ 结构化JSON结果输出
- ✅ 自动保存结果到文件
- ✅ 内置视频格式和大小校验

## 目录结构
```
face-analysis/
├── SKILL.md              # 技能说明文件（系统自动加载）
├── README.md             # 本说明文件
├── scripts/
│   ├── face_analysis.py  # 主程序
│   └── config.py         # 配置文件
├── references/
│   ├── api_doc.md        # API接口文档
│   ├── tcm_theory.md     # 中医面诊理论参考
│   └── faq.md            # 常见问题
└── assets/
    └── template.json     # 返回结果模板
```

## 使用示例
### 标准输出
```
📊 中医面诊分析报告
==================================================
⏰ 分析时间: 2026-03-10 15:30:00
🎯 人脸检测: success (置信度: 95分)

🔍 诊断结果:
  整体体质: 平和质
  脏腑状况:
    liver: 正常
    heart: 轻微火旺
    spleen: 略虚
    lung: 正常
    kidney: 正常
  面色分析: 微黄
  对应提示: 脾胃功能略弱

⚠️ 健康警示:
  ⚠️  注意休息，避免熬夜

💡 养生建议:
  💡 饮食清淡，减少辛辣食物摄入
  💡 保持规律作息，每晚11点前入睡
  💡 适当进行有氧运动，如散步、太极拳
==================================================
```

### 输出到JSON文件
```bash
python scripts/face_analysis.py --input video.mp4 --detail full --output result.json
```

## 注意事项
1. 视频要求：清晰正面面部，光线充足，时长5-30秒为宜
2. 支持格式：mp4、avi、mov，最大100MB
3. API需要自行部署或接入第三方服务
4. 结果仅供参考，不能替代专业医生诊断
