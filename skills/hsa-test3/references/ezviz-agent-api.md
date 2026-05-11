# 萤石开放平台 API 文档 - 智能体分析

本文档包含多模态理解技能所需的 API 接口详细说明。

---

## 1. 获取 AccessToken 接口

**文档 URL**: https://openai.ys7.com/help/81

### 请求地址

```
POST https://openai.ys7.com/api/lapp/token/get
```

### 请求参数

| 参数名 | 类型 | 描述 | 是否必选 |
|--------|------|------|----------|
| appKey | String | appKey | Y |
| appSecret | String | appSecret | Y |

### 返回数据

```json
{
  "data": {
    "accessToken": "at.xxxxxxxxxxxxx",
    "expireTime": 1470810222045
  },
  "code": "200",
  "msg": "操作成功!"
}
```

---

## 2. 设备抓拍图片接口

**文档 URL**: https://openai.ys7.com/help/687

### 请求地址

```
POST https://openai.ys7.com/api/lapp/device/capture
```

### 请求参数

| 参数名 | 类型 | 描述 | 是否必选 |
|--------|------|------|----------|
| accessToken | String | 访问令牌 | Y |
| deviceSerial | String | 设备序列号（大写） | Y |
| channelNo | int | 通道号 | Y |

### 返回数据

```json
{
  "data": {
    "picUrl": "https://opencapture.ys7.com/.../capture/xxx.jpg"
  },
  "code": "200",
  "msg": "操作成功!"
}
```

---

## 3. 智能体分析接口

**文档 URL**: https://openai.ys7.com/help/5006  
**更新时间**: 2026.01.05

### 接口功能

调用 AI 智能体对图片或视频进行多模态理解分析。

### 请求地址

```
POST https://aidialoggw.ys7.com/api/service/open/intelligent/agent/engine/agent/anaylsis
```

### 请求参数

#### Header

| 名称 | 类型 | 必填 | 描述 |
|------|------|------|------|
| accessToken | string | Y | 萤石开放 API 访问令牌 |

#### Body (JSON)

| 名称 | 类型 | 必填 | 描述 | 示例 |
|------|------|------|------|------|
| appId | string | Y | 智能体 ID | 98af3e**** |
| mediaType | string | Y | 媒体类型：video、image | image |
| text | string | N | 分析要求/提示词 | 帮我识别视频 |
| dataType | string | Y | 数据格式类型 | url |
| data | string | Y | 数据 URL | https://openrecord.ys7.com/** |

### 请求示例

```bash
curl --location --request POST 'https://aidialoggw.ys7.com/api/service/open/intelligent/agent/engine/agent/anaylsis' \
  --header 'accessToken: at.75zsez8426qp1g9s6n******' \
  --header 'Content-Type: application/json' \
  --data-raw '{
    "appId": "98af3ea07f564e****f",
    "text": "帮我识别视频",
    "mediaType": "video",
    "dataType": "url",
    "data": "https://openrecord.ys7.com/E1/1o4/14/c1cbc1d4e86d49a*****"
  }'
```

### 返回数据

| 名称 | 类型 | 描述 |
|------|------|------|
| meta | object | 元数据 |
| └─ code | int | 状态码 |
| └─ message | string | 状态信息 |
| └─ moreInfo | object | 更多信息 |
| data | object/string | 分析结果（依赖智能体配置） |

### 返回示例

```json
{
  "meta": {
    "code": 200,
    "message": "操作成功",
    "moreInfo": null
  },
  "data": "{ \"是否进球\": \"是\", \"是否有威胁进球\": \"否\", \"是否有射门\": \"否\", \"球员号码\": \"号码缺失\", \"球衣颜色\": \"白色\" }"
}
```

**注意**: `data` 字段是 JSON 字符串，需要二次解析。

### 错误码

| 状态码 | 错误码 | 错误信息 | 解决方案 |
|--------|--------|----------|----------|
| 200 | 200 | 操作成功 | - |
| 400 | 400 | 参数错误 | 检查请求参数格式 |
| 500 | 500 | 服务异常 | 联系技术支持 |

---

## 完整流程

```
1. GET /api/lapp/token/get
   Input: appKey, appSecret
   Output: accessToken

2. POST /api/lapp/device/capture
   Input: accessToken, deviceSerial, channelNo
   Output: picUrl

3. POST /api/service/open/intelligent/agent/engine/agent/anaylsis
   Input: accessToken, appId, mediaType="image", dataType="url", data=picUrl
   Output: AI analysis result
```

---

## 智能体创建

1. 访问：https://openai.ys7.com/console/aiAgent/aiAgent.html
2. 创建新智能体
3. 配置提示词和分析逻辑
4. 获取 agentId（appId）

---

## 注意事项

1. **分析结果格式** - 依赖智能体的提示词配置，不固定
2. **data 字段** - 返回的是 JSON 字符串，需要二次解析
3. **超时时间** - 建议设置 60s 以上
4. **图片有效期** - 抓拍的图片 URL 有效期 2 小时
