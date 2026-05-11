# 萤石开放平台 API 文档 - 设备抓图

本文档包含设备抓图技能所需的 API 接口详细说明。

---

## 1. 获取 AccessToken 接口

**文档 URL**: https://open.ys7.com/help/81  
**更新时间**: 2025.02.21

### 接口说明

AccessToken 是访问令牌，接口调用必备的公共参数之一，用于校验接口访问/调用是否有权限。

**重要特性**:
- 有效期为 **7 天**，有效期内不需要重复申请
- 新 Token 不会使老 Token 失效
- 最佳实践：本地缓存，即将过期或报错 10002 时再获取

### 请求地址

```
POST https://open.ys7.com/api/lapp/token/get
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

### 返回字段

| 字段名 | 类型 | 描述 |
|--------|------|------|
| accessToken | String | 获取的 accessToken |
| expireTime | long | 具体过期时间，精确到毫秒 |

### 错误码

| 返回码 | 返回消息 | 描述 |
|--------|----------|------|
| 200 | 操作成功 | 请求成功 |
| 10001 | 参数错误 | 参数为空或格式不正确 |
| 10005 | appKey 异常 | appKey 被冻结 |
| 10017 | appKey 不存在 | 确认 appKey 是否正确 |
| 10030 | appkey 和 appSecret 不匹配 | - |

---

## 2. 设备抓拍图片接口

**文档 URL**: https://open.ys7.com/help/687  
**更新时间**: 2025.11.25

### 接口功能

抓拍设备当前画面，**该接口仅适用于 IPC 或者关联 IPC 的 DVR 设备**。

**该接口需要设备支持能力集**：`support_capture=1`

> ⚠️ **注意**：设备抓图能力有限，请勿频繁调用，建议每个摄像头调用的间隔**4s 以上**。

### 请求地址

```
POST https://open.ys7.com/api/lapp/device/capture
```

### 请求参数

| 参数名 | 类型 | 描述 | 是否必选 |
|--------|------|------|----------|
| accessToken | String | 授权过程获取的 access_token | Y |
| deviceSerial | String | 设备序列号，字母需为大写 | Y |
| channelNo | int | 通道号，IPC 设备填写 1 | Y |
| quality | int | 视频清晰度（此参数不生效） | N |

### 返回数据

```json
{
  "data": {
    "picUrl": "https://opencapture.ys7.com/.../capture/xxx.jpg?Expires=xxx&..."
  },
  "code": "200",
  "msg": "操作成功!"
}
```

### 返回字段

| 字段名 | 类型 | 描述 |
|--------|------|------|
| picUrl | String | 抓拍后的图片路径，**图片保存有效期为 2 小时** |

### 错误码

| 返回码 | 返回消息 | 描述 |
|--------|----------|------|
| 200 | 操作成功 | 请求成功 |
| 10001 | 参数错误 | 参数为空或格式不正确 |
| 10002 | accessToken 异常或过期 | 重新获取 accessToken |
| 10028 | 抓图接口调用次数超限 | 降低频率，间隔>4s |
| 20002 | 设备不存在 | 检查设备序列号 |
| 20006 | 网络异常 | 检查设备网络状况 |
| 20007 | 设备不在线 | 检查设备是否在线 |
| 20008 | 设备响应超时 | 操作过于频繁或设备不支持 |
| 20014 | deviceSerial 不合法 | 检查序列号格式 |
| 60020 | 不支持该命令 | 确认设备是否支持抓图 |

---

## 最佳实践

### 1. Token 管理

```python
# 缓存 token，避免频繁请求
TOKEN_CACHE = {}

def get_cached_token(app_key, app_secret):
    cache_key = f"{app_key}:{app_secret}"
    
    if cache_key in TOKEN_CACHE:
        token_info = TOKEN_CACHE[cache_key]
        # 提前 1 小时刷新
        if time.time() * 1000 < token_info['expire_time'] - 3600000:
            return token_info['access_token']
    
    # 获取新 token
    token_result = get_access_token(app_key, app_secret)
    TOKEN_CACHE[cache_key] = token_result
    return token_result['access_token']
```

### 2. 批量抓图

```python
# 控制频率，避免超限
devices = ["device1", "device2", "device3"]
for device in devices:
    result = capture_device_image(token, device)
    time.sleep(1)  # 间隔 1 秒
```

### 3. 错误处理

```python
result = capture_device_image(token, device)
if not result['success']:
    code = result.get('code', '')
    if code == '10002':
        # Token 过期，重新获取
        token = get_access_token(app_key, app_secret)
    elif code == '10028':
        # 频率超限，等待后重试
        time.sleep(5)
```
