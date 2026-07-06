---
name: cloudcc-openapi-withobject
description: CloudCC OpenAPI 调用技能 - 提供完整的 REST API 接口调用能力，支持对象/字段元数据查询
version: 2.0.0
author: 鲁班
createDate: 2026-03-20
updateDate: 2026-03-20
---

## 技能信息

- **名称**: cloudcc-openapi-withobject
- **版本**: 2.0.0
- **作者**: 鲁班
- **创建日期**: 2026-03-20
- **更新日期**: 2026-03-20
- **适用范围**: CloudCC One 版本 OpenAPI 接口调用

## 安装配置

### 配置参数

| 参数 | 说明 | 默认值 | 必填 |
|------|------|--------|------|
| `orgId` | 组织 ID | - | 是 |
| `username` | 登录用户名 | - | 是 |
| `safetyMark` | 安全标记（邮箱获取） | - | 是 |
| `clientId` | 连接应用的 clientId | - | 是 |
| `secretKey` | 连接应用的 secretKey | - | 是 |
| `apiDomain` | API 网关地址（动态获取） | - | 否（自动获取） |

### 获取配置信息

1. **组织 ID (orgId)**: 系统设置 - 公司信息中查看
2. **安全标记 (safetyMark)**: 个人信息 - 重置我的安全标记（发送到邮箱）
3. **clientId/secretKey**: 管理设置 - 安全性控制 - 连接的应用程序

### 安装步骤

```bash
# 1. 创建技能目录
mkdir -p ~/.openclaw/skills/cloudcc-openapi-withobject

# 2. 创建配置文件
cat > ~/.openclaw/skills/cloudcc-openapi-withobject/config.json << 'EOF'
{
  "orgId": "your-org-id",
  "username": "your-username",
  "safetyMark": "your-safety-mark",
  "clientId": "your-client-id",
  "secretKey": "your-secret-key"
}
EOF
```

## 核心功能

### 1. 认证管理

- 动态获取组织 API 网关地址
- 获取 accessToken 并自动刷新
- accessToken 有效性验证
- 认证事件日志记录

### 2. 元数据查询（新增 v2.0.0）

| 方法 | 说明 | API 端点 |
|------|------|---------|
| `getAllTabs` | 获取所有选项卡（推荐用于查找对象） | `/openApi/common` (getAllTabs) |
| `pageQuery` | 查询对象数据（不带 fields 返回所有字段） | `/openApi/common` (pageQuery) |
| `getStandardObjects` | 获取标准对象列表 | `/api/customObject/standardObjList` |
| `getCustomObjects` | 获取自定义对象列表 | `/api/customObject/list` |
| `getObjectFields` | 获取对象字段列表 | `/api/fieldSetup/queryField` |

> **注意**: 元数据查询 API (`/api/customObject/*` 和 `/api/fieldSetup/*`) 可能需要额外的权限或使用 Setup 服务域名。推荐使用 `getAllTabs` 方法查找对象 API 名称。

### 3. 数据操作

- **查询**: 普通查询、分页查询、带权限查询、SQL 查询
- **插入**: 普通插入、带权限插入
- **更新**: 普通更新、带权限更新
- **删除**: 普通删除、带权限删除
- **Upsert**: 插入或更新

### 4. 文件服务

- 图片上传（单张/多张）
- 文件上传（流/base64）
- 文件下载
- 附件管理

### 5. 消息服务

- 发送邮件
- 发送手机短信
- Chatter 微帖操作

### 6. 审批流程

- 查询待审批项目
- 批准/拒绝/重新分配
- 提交审批

### 7. 安全日志（v2.1.0 新增）

- 自动记录所有 API 调用（服务名、对象、响应码、耗时）
- 记录认证事件（token 请求、刷新、过期）
- 日志自动清理（保留最近 3 天）
- 支持日志查询、统计、导出

## 使用方法

### 快速开始

```bash
# 1. 获取 API 网关地址
curl -X GET "https://developer.apis.cloudcc.cn/oauth/apidomain?scope=cloudccCRM&orgId=YOUR_ORG_ID"

# 返回示例:
# {"result":true,"returnInfo":"","returnCode":"1","orgapi_address":"https://xxxx.apis.cloudcc.cn/lightningapi"}

# 2. 获取 accessToken
curl -X POST "https://xxxx.apis.cloudcc.cn/lightningapi/api/cauth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "username":"your-username",
    "safetyMark":"your-safety-mark",
    "clientId":"your-client-id",
    "secretKey":"your-secret-key",
    "orgId":"your-org-id",
    "grant_type":"password"
  }'

# 返回示例:
# {"data":{"accessToken":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},"returnCode":"1","result":true}
```

### 日志管理（v2.1.0 新增）

```bash
# 查看最近的日志
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/logger.sh view 50

# 查看统计信息
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/logger.sh stats 3

# 搜索日志
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/logger.sh search "productuplist"

# 导出日志
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/logger.sh export

# 清理旧日志（保留最近 3 天）
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/logger.sh cleanup 3
```

#### 日志格式

每条日志为 JSON 格式，包含以下字段：

```json
{
  "timestamp": "2026-03-20 12:15:30",
  "type": "API_REQUEST",
  "service": "pageQuery",
  "objectApi": "productuplist",
  "responseCode": "1",
  "durationMs": "125"
}
```

#### 日志类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `API_REQUEST` | API 调用记录 | 记录所有 OpenAPI 调用 |
| `AUTH_EVENT` | 认证事件 | token 请求、刷新、过期 |

### 元数据查询示例（v2.0.0 新增）

#### 获取标准对象列表

```bash
curl -X POST "$API_DOMAIN/api/customObject/standardObjList" \
  -H "accessToken: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**返回示例**:
```json
{
  "result": true,
  "data": [
    {"id": "account", "objname": "客户", "label": "Account", "objprefix": "001"},
    {"id": "contact", "objname": "联系人", "label": "Contact", "objprefix": "003"},
    {"id": "opportunity", "objname": "业务机会", "label": "Opportunity", "objprefix": "002"}
  ]
}
```

#### 获取自定义对象列表

```bash
curl -X POST "$API_DOMAIN/api/customObject/list" \
  -H "accessToken: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id":""}'
```

**返回示例**:
```json
{
  "result": true,
  "data": {
    "objList": [
      {"id": "2021A51AA0D3785lBzwh", "objLabel": "产品需求研发报备记录", "schemetable_name": "productuplist", "prefix": "b70"},
      {"id": "2023D181015EDF0f7G1y", "objLabel": "需求池", "schemetable_name": "requirementpool", "prefix": "c75"}
    ]
  }
}
```

#### 获取对象字段列表

```bash
curl -X POST "$API_DOMAIN/api/fieldSetup/queryField" \
  -H "accessToken: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prefix":"b70"}'
```

**返回示例**:
```json
{
  "result": true,
  "data": {
    "obj": {"id": "2021A51AA0D3785lBzwh", "label": "产品需求研发报备记录"},
    "stdFields": [
      {"id": "1", "labelName": "名称", "schemefieldName": "name", "schemefieldType": "S"}
    ],
    "cusFields": [
      {"id": "c1", "labelName": "产品", "schemefieldName": "product", "schemefieldType": "S"},
      {"id": "c2", "labelName": "状态", "schemefieldName": "zhuangtai", "schemefieldType": "L"}
    ]
  }
}
```

#### 通过选项卡查找对象（实用技巧）

```bash
# 搜索包含关键词的选项卡
curl -X POST "$API_DOMAIN/openApi/common" \
  -H "accessToken: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"serviceName":"getAllTabs"}' | jq '.data[] | select(.tab_name | test("产品 | 需求"))'
```

**返回示例**:
```json
{
  "tab_name": "产品需求研发报备记录",
  "objectApi": "productuplist",
  "prefix": "b70",
  "objId": "2021A51AA0D3785lBzwh"
}
```

### 数据查询示例

#### 普通查询 (cquery)

```json
{
  "serviceName": "cquery",
  "objectApiName": "Contact",
  "expressions": "name='test'",
  "isAddDelete": "false",
  "fields": "name,createdate,createbyid"
}
```

#### 分页查询 (pageQuery)

```json
{
  "serviceName": "pageQuery",
  "objectApiName": "Account",
  "fields": "id,name,phone",
  "expressions": "industry='Technology'",
  "pageNUM": 1,
  "pageSize": 20
}
```

#### 插入数据 (insert)

```json
{
  "serviceName": "insert",
  "objectApiName": "Contact",
  "data": "[{\"name\":\"张三\",\"phone\":\"13800138000\",\"email\":\"zhangsan@example.com\"}]"
}
```

#### 更新数据 (update)

```json
{
  "serviceName": "update",
  "objectApiName": "Contact",
  "data": "[{\"id\":\"003202100BDF459HcI1R\",\"name\":\"李四\",\"phone\":\"13900139000\"}]"
}
```

#### 删除数据 (delete)

```json
{
  "serviceName": "delete",
  "objectApiName": "Contact",
  "data": "[{\"id\":\"003202100BDF459HcI1R\"}]"
}
```

#### Upsert (插入或更新)

```json
{
  "serviceName": "upsert",
  "objectApiName": "Contact",
  "data": "[{\"id\":\"003202100BDF459HcI1R\",\"name\":\"王五\"}]"
}
```

## API 接口列表

### 认证相关

| 接口 | 服务名 | 说明 |
|------|--------|------|
| 获取网关 | GET /oauth/apidomain | 动态获取组织 API 地址 |
| 获取 token | POST /api/cauth/token | 获取 accessToken |
| 验证 token | isValidWithBinding | 验证 accessToken 有效性 |

### 元数据查询（v2.0.0 新增）

| 接口 | 端点 | 说明 |
|------|------|------|
| 获取标准对象 | POST /api/customObject/standardObjList | 返回所有标准对象 |
| 获取自定义对象 | POST /api/customObject/list | 返回所有自定义对象 |
| 获取对象字段 | POST /api/fieldSetup/queryField | 根据 prefix 查询字段 |
| 获取选项卡 | POST /openApi/common (getAllTabs) | 返回所有选项卡配置 |

### 查询服务

| 接口 | 服务名 | 说明 |
|------|--------|------|
| 普通查询 | cquery | 基础查询 |
| 带权限查询 | cqueryWithRoleRight | 含权限控制的查询 |
| 分页查询 | pageQuery | 分页数据查询 |
| 分页带权限查询 | pageQueryWithRoleRight | 含权限的分页查询 |
| 获取查询权限 | getQueryPermisson | 获取对象查询权限 |
| SQL 查询 | cqlQueryWithLogInfo | 自定义 SQL 查询 |
| 静态查询 | cqlQueryWithStatic | 支持游标的静态查询 |

### 数据操作

| 接口 | 服务名 | 说明 |
|------|--------|------|
| 插入 | insert | 插入数据 |
| 带权限插入 | insertWithRoleRight | 含权限控制的插入 |
| 更新 | update | 更新数据 |
| 带权限更新 | updateWithRoleRight | 含权限控制的更新 |
| 删除 | delete | 删除数据 |
| 带权限删除 | deleteWithRoleRight | 含权限控制的删除 |
| Upsert | upsert | 插入或更新 |
| Upsert 带权限 | upsertWithRoleRight | 含权限的 upsert |

### 文件服务

| 接口 | 服务名 | 地址 | 说明 |
|------|--------|------|------|
| 上传图片 | uploadImg | /openApi/file | 单张图片上传 |
| 上传多图 | uploadImgMany | /openApi/file | 最多 9 张 |
| 获取图片属性 | getImgProperty | /openApi/common | 查询图片信息 |
| 上传文件 | uploadFile | /openApi/file | 文件流上传 |
| 上传附件 | uploadAttachement | /openApi/common | base64 上传 |
| 下载文件 | downloadFile | /openApi/downloadFile | GET 请求 |
| 下载附件 | downloadAttachement | /openApi/common | base64 下载 |
| 删除附件 | deleteAttachment | /openApi/common | 删除附件 |
| 删除文件 | deleteFile | /openApi/common | 删除文件 |

### 消息服务

| 接口 | 服务名 | 说明 |
|------|--------|------|
| 发送邮件 | sendEmail | 支持模板变量 |
| 发送短信 | telMessage | 手机消息服务 |

### Chatter 服务

| 接口 | 服务名 | 说明 |
|------|--------|------|
| 获取 Chatter | getChatters01 | 查询微帖内容 |
| 获取我的 Chatter | getMyChatter01 | 我追随的内容 |
| 获取追随者 | getFollowUsers | 查询追随关系 |
| 发布帖子 | addMicroPostF | 普通帖子 |
| 发布文件帖 | addMicroPostD | 带文件的帖子 |
| 发布链接帖 | addMicroPostL | 带链接的帖子 |
| 发布投票帖 | addMicroPostV | 投票类型帖子 |
| 投票 | voteMicroPost | 对帖子投票 |
| 发布评论 | addMicroComment | 普通评论 |
| 文件评论 | addMicroCommentFile | 带文件评论 |
| 点赞帖子 | praiseFeed | 喜欢/取消喜欢 |
| 点赞评论 | praiseComment | 评论点赞 |
| 收藏帖子 | favoriteFeed | 收藏/取消收藏 |
| 删除帖子 | removeMicroPost | 删除微帖 |
| 删除评论 | removeMicroComment | 删除评论 |
| 追随操作 | operateFollowRelation | 追随/取消追随 |

### 审批服务

| 接口 | 服务名 | 说明 |
|------|--------|------|
| 待审批列表 | getApprovalPaddingList | 查询待审批项目 |
| 批准 | doApproved | 批准操作 |
| 拒绝 | doRejected | 拒绝操作 |
| 重新分配 | doReassign | 重新分配审批人 |
| 调回 | reCall | 调回审批 |
| 提交审批 | submitForApproval | 提交审批流程 |

### 其他服务

| 接口 | 服务名 | 说明 |
|------|--------|------|
| 获取应用列表 | getAppList | 应用程序列表 |
| 获取选项卡 | getAllTabs | 选项卡信息 |
| 获取应用和选项卡 | getAppAndTabList | 合并查询 |
| 获取搜索设置 | getMySetupObjs | 搜索配置 |
| 获取选项列表值 | getPickListValue | 字段选项值 |
| 保存依赖关系 | saveDependency | 选项依赖配置 |
| 自助服务 | customService | MongoDB 数据操作 |

## 返回码说明

| 代码 | 说明 |
|------|------|
| 1 | 调用成功 |
| -1 | 调用成功但接口异常 |
| -2 | 调用不成功（如失效） |
| -3 | 参数输入有误 |

## 最佳实践

### 1. 查找对象的完整流程（v2.0.0）

```bash
# 步骤 1: 通过选项卡名称查找对象（最直观）
curl -X POST "$API_DOMAIN/openApi/common" \
  -H "accessToken: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"serviceName":"getAllTabs"}' | jq '.data[] | select(.tab_name | test("产品需求"))'

# 返回：{"objectApi":"productuplist","prefix":"b70","objId":"2021A51AA0D3785lBzwh"}

# 步骤 2: 使用 objectApi 查询数据
curl -X POST "$API_DOMAIN/openApi/common" \
  -H "accessToken: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"serviceName":"pageQuery","objectApiName":"productuplist","pageNUM":1,"pageSize":20}'

# 步骤 3: 使用 prefix 查询字段结构
curl -X POST "$API_DOMAIN/api/fieldSetup/queryField" \
  -H "accessToken: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prefix":"b70"}'
```

### 2. 网关地址动态获取

**禁止写死 API 地址**，组织网关可能根据负载漂移：

```bash
# 每次启动时获取
API_DOMAIN=$(curl -s "https://developer.apis.cloudcc.cn/oauth/apidomain?scope=cloudccCRM&orgId=$ORG_ID" | jq -r '.orgapi_address')
```

### 3. accessToken 管理

- accessToken 放入请求头：`accessToken: <value>`
- 定期验证有效性（使用 `isValidWithBinding`）
- 失效时重新获取

### 4. 批量操作

- 插入/更新/删除支持批量操作
- data 参数为 JSON 数组：`[{...}, {...}]`
- 注意 API 调用配额限制

### 5. 特殊字符处理

URL 中的特殊字符需要 URL 编码：
```java
java.net.URLEncoder.encode("%", "UTF-8")
```

### 6. 字段命名规范

- 服务名和参数名**首字母小写**
- 如文档中大写，请改为小写

## API 配额限制

| 版本 | 基础次数 | 每用户额外 | 最大限额/24h |
|------|---------|-----------|-------------|
| 专业版 | 5000 | 用户数×150 | 10000 |
| 企业版 | 50000 | 用户数×300 | 200000 |
| 旗舰版 | 50000 | 用户数×500 | 500000 |
| 超级版 | 50000 | 用户数×500 | 500000 |

> ⚠️ 禁止超负荷请求，否则 API Client 可能被停用

## 故障排查

### 常见问题

1. **accessToken 失效**: 重新调用 `/api/cauth/token`
2. **网关地址变化**: 重新获取 `/oauth/apidomain`
3. **权限不足**: 检查简档权限或使用带权限接口
4. **参数错误**: 检查字段名是否小写、JSON 格式是否正确
5. **对象不存在**: 使用 `getAllTabs` 或 `getCustomObjects` 确认对象 API 名称

### 调试技巧

```bash
# 1. 验证 token 有效性
curl -X POST "$API_DOMAIN/openApi/common" \
  -H "accessToken: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"serviceName":"isValidWithBinding"}'

# 2. 检查返回码
# returnCode: "1" 表示成功
# returnCode: "-1" 表示接口异常
# returnCode: "-2" 表示 token 失效
# returnCode: "-3" 表示参数错误

# 3. 查找对象 API 名称
curl -X POST "$API_DOMAIN/openApi/common" \
  -H "accessToken: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"serviceName":"getAllTabs"}' | jq '.data[] | select(.tab_name | test("关键词"))'
```

## 版本历史

### v2.1.0 (2026-03-20)
- ✅ 新增安全日志功能
- ✅ 支持 `logger.sh` - 日志管理工具
- ✅ 自动记录所有 API 调用（服务名、对象、响应码、耗时）
- ✅ 自动记录认证事件（token 请求、刷新、过期）
- ✅ 日志自动清理（保留最近 3 天）
- ✅ 支持日志查询、统计、导出

### v2.0.0 (2026-03-20)
- ✅ 新增元数据查询能力
- ✅ 支持 `getStandardObjects` - 获取标准对象列表
- ✅ 支持 `getCustomObjects` - 获取自定义对象列表
- ✅ 支持 `getObjectFields` - 获取对象字段列表
- ✅ 支持 `getAllTabs` - 获取选项卡信息
- ✅ 新增对象查找最佳实践文档

### v1.0.0 (2026-03-20)
- ✅ 初始版本
- ✅ 完整 API 接口文档
- ✅ 认证管理
- ✅ 数据 CRUD 操作
- ✅ 文件服务
- ✅ 消息服务
- ✅ Chatter 接口
- ✅ 审批流程

---

**维护人**: 鲁班  
**参考文档**: https://help.cloudcc.cn/product03/apigai-lan/
