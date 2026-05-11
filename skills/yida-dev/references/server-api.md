# 宜搭服务端 Open API

宜搭提供服务端 API，支持从后端系统调用进行数据操作。

## 认证流程

### 1. 获取 access_token

```js
// 请求
POST https://api.dingtalk.com/v1.0/oauth2/accessToken
Content-Type: application/json

{
  "appKey": "xxx",
  "appSecret": "xxx"
}

// 响应
{
  "accessToken": "xxx",
  "expireIn": 7200
}
```

### 2. 添加接口权限

在钉钉开发者后台为应用添加：
- 宜搭表单数据读权限
- 宜搭表单数据写权限
- 宜搭流程数据读权限
- 宜搭流程数据写权限

## API 分类

### 表单 API

| 接口 | 说明 |
|------|------|
| `POST /v1/form/createInst` | 新增表单数据 |
| `POST /v1/form/updateInst` | 更新表单数据 |
| `POST /v1/form/deleteInst` | 删除表单数据 |
| `POST /v1/form/getInst` | 查询单条数据 |
| `POST /v1/form/listInstData` | 查询数据列表 |

### 流程 API

| 接口 | 说明 |
|------|------|
| `POST /v1/process/startInstance` | 发起审批 |
| `POST /v1/process/terminate` | 终止流程 |
| `POST /v1/process/delete` | 删除流程实例 |

### 附件 API

| 接口 | 说明 |
|------|------|
| `POST /v1/attachment/getTempUrl` | 获取附件临时地址 |

## 调用示例

```js
// 新增表单数据
POST /dingtalk/web/APP_xxx/v1/form/createInst.json
{
  "formUuid": "FORM-xxx",
  "formDataJson": "{\"textField_xxx\": \"值\"}",
  "userId": "xxx"
}
```

详见 `scripts/server_api_example.js`

## 版本要求

| 版本 | 支持 |
|------|------|
| 免费版 | ❌ |
| 轻享版 | ❌ |
| 专业版 | ✅ |
| 专属版 | ✅ |
