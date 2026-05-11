# API接口文档

## 接口地址
`POST https://your-api-server.com/api/v1/face-analysis`

## 请求头
| 字段 | 必选 | 说明 |
|------|------|------|
| X-API-Key | 是 | API访问密钥 |
| Content-Type | 是 | multipart/form-data（文件上传）或 application/json（URL模式） |

## 请求参数
### 1. 文件上传模式
| 字段 | 类型 | 必选 | 说明 |
|------|------|------|------|
| video | file | 是 | MP4视频文件 |
| detail_level | string | 否 | 输出详细程度：basic/standard/full，默认standard |

### 2. URL模式
| 字段 | 类型 | 必选 | 说明 |
|------|------|------|------|
| video_url | string | 是 | 可公开访问的视频URL |
| detail_level | string | 否 | 输出详细程度：basic/standard/full，默认standard |

## 响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "analysis_time": "2026-03-10 15:30:00",
    "face_detection": {
      "status": "success",
      "face_count": 1,
      "quality_score": 95
    },
    "diagnosis": {
      "overall_constitution": "平和质",
      "organ_condition": {
        "liver": "正常",
        "heart": "轻微火旺",
        "spleen": "略虚",
        "lung": "正常",
        "kidney": "正常"
      },
      "color_analysis": {
        "complexion": "微黄",
        "correspondence": "脾胃功能略弱"
      }
    },
    "health_warnings": [
      "注意休息，避免熬夜"
    ],
    "suggestions": [
      "饮食清淡，减少辛辣食物摄入"
    ]
  }
}
```

## 错误码说明
| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | API密钥无效 |
| 403 | 权限不足 |
| 413 | 文件过大 |
| 415 | 不支持的文件格式 |
| 500 | 服务器内部错误 |
