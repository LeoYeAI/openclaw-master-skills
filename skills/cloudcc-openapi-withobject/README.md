# cloudcc-openapi-withobject

CloudCC OpenAPI 调用技能 - 提供完整的 REST API 接口调用能力，支持对象/字段元数据查询

**版本**: 2.1.0  
**更新日期**: 2026-03-20

## 快速开始

### 1. 配置认证信息

```bash
# 复制配置模板
cp ~/.openclaw/skills/cloudcc-openapi-withobject/config.example.json \
   ~/.openclaw/skills/cloudcc-openapi-withobject/config.json

# 编辑配置文件，填写你的认证信息
vi ~/.openclaw/skills/cloudcc-openapi-withobject/config.json
```

### 2. 获取认证凭据

| 凭据 | 获取方式 |
|------|---------|
| `orgId` | 系统设置 - 公司信息 |
| `safetyMark` | 个人信息 - 重置我的安全标记（邮箱接收） |
| `clientId` | 管理设置 - 安全性控制 - 连接的应用程序 |
| `secretKey` | 管理设置 - 安全性控制 - 连接的应用程序 |

### 3. 获取 accessToken

```bash
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/get-token.sh
```

### 4. 调用 API

```bash
# 查询联系人
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/call-api.sh \
  cquery \
  '{"objectApiName":"Contact","fields":"id,name,phone","expressions":"name=\"测试\""}'

# 插入数据
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/call-api.sh \
  insert \
  '{"objectApiName":"Contact","data":[{"name":"张三","phone":"13800138000"}]}'
```

## 元数据查询（v2.0.0 新增）

### 查找对象

```bash
# 通过选项卡名称搜索对象
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/find-object.sh \
  -k "产品需求"

# 输出:
# 选项卡名称                              对象 API                   前缀        对象 ID
# --------                              --------                   ----        --------
# 产品需求研发报备记录                    productuplist              b70         2021A51AA0D3785lBzwh
```

### 获取对象列表

```bash
# 获取所有对象（标准 + 自定义）
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/get-objects.sh

# 只获取自定义对象
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/get-objects.sh -c

# 搜索包含关键词的对象
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/get-objects.sh -k "需求"
```

### 获取对象字段

```bash
# 方法 1: 通过对象 API 名称查询字段（需要额外权限）
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/get-fields.sh \
  -o productuplist

# 方法 2: 通过对象前缀查询字段（需要额外权限）
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/get-fields.sh \
  -p b70

# 方法 3: 通过查询一条记录获取所有字段（推荐，无需额外权限）
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/call-api.sh \
  cquery \
  '{"objectApiName":"productuplist","expressions":"id=\"b7020254FF6E5C5PvLWi\""}' | jq '.data[0] | keys'
```

## 常用 API 示例

### 普通查询

```json
{
  "serviceName": "cquery",
  "objectApiName": "Account",
  "fields": "id,name,phone,industry",
  "expressions": "industry='Technology'"
}
```

### 分页查询

```json
{
  "serviceName": "pageQuery",
  "objectApiName": "Opportunity",
  "fields": "id,name,amount,stage",
  "expressions": "stage='Prospecting'",
  "pageNUM": 1,
  "pageSize": 20
}
```

### SQL 查询

```json
{
  "serviceName": "cqlQueryWithLogInfo",
  "objectApiName": "Account",
  "expressions": "select id, name, industry from Account where createdate > '2026-01-01'"
}
```

### 发送邮件

```json
{
  "serviceName": "sendEmail",
  "data": {
    "toAddress": "user@example.com",
    "ccAddress": "manager@example.com",
    "subject": "测试邮件",
    "content": "这是一封测试邮件",
    "isText": true
  }
}
```

## 目录结构

```
cloudcc-openapi-withobject/
├── SKILL.md              # 完整技能文档
├── README.md             # 快速入门（本文件）
├── config.example.json   # 配置模板
├── config.json           # 实际配置（需自行创建）
├── logs/                 # 日志目录（自动创建）
│   └── api-calls.log     # API 调用日志
└── scripts/
    ├── get-token.sh      # 获取 accessToken（带日志）
    ├── call-api.sh       # 通用 API 调用（带日志）
    ├── logger.sh         # 日志管理工具（v2.1.0）
    ├── find-object.sh    # 查找对象（v2.0.0）
    ├── get-objects.sh    # 获取对象列表（v2.0.0）
    └── get-fields.sh     # 获取对象字段（v2.0.0）
```

## 脚本说明

| 脚本 | 说明 | 示例 |
|------|------|------|
| `get-token.sh` | 获取/刷新 accessToken（带日志） | `./get-token.sh` |
| `call-api.sh` | 调用任意 OpenAPI（带日志） | `./call-api.sh cquery '{...}'` |
| `logger.sh` | 日志管理工具（v2.1.0） | `./logger.sh view 50` |
| `find-object.sh` | 通过选项卡名称查找对象 | `./find-object.sh -k "产品"` |
| `get-objects.sh` | 获取标准/自定义对象列表 | `./get-objects.sh -c -k "需求"` |
| `get-fields.sh` | 获取对象字段结构 | `./get-fields.sh -p b70` |

### 日志管理命令（v2.1.0）

| 命令 | 说明 | 示例 |
|------|------|------|
| `view [count]` | 查看最近的日志 | `./logger.sh view 50` |
| `stats [days]` | 显示统计信息 | `./logger.sh stats 3` |
| `search <kw>` | 搜索日志 | `./logger.sh search productuplist` |
| `export` | 导出日志为 JSON | `./logger.sh export` |
| `cleanup [days]` | 清理旧日志 | `./logger.sh cleanup 3` |

## 注意事项

1. **网关地址动态获取** - 禁止写死 API 地址
2. **accessToken 有效期** - 默认 2 小时，过期自动刷新
3. **字段名小写** - 服务名和参数名首字母必须小写
4. **API 配额** - 注意每日调用限额
5. **安全日志** - 所有 API 调用自动记录到 `logs/api-calls.log`，保留最近 3 天

## 参考文档

- [CloudCC OpenAPI 概览](https://help.cloudcc.cn/product03/apigai-lan/)
- [CloudCC 系统接口说明书](https://help.cloudcc.cn/)

---

**版本**: 2.1.0  
**作者**: 鲁班  
**创建日期**: 2026-03-20  
**更新日期**: 2026-03-20

## 安全日志（v2.1.0）

### 日志位置

```
~/.openclaw/skills/cloudcc-openapi-withobject/logs/api-calls.log
```

### 日志内容

所有 API 调用自动记录，包含：
- 时间戳
- 服务名称（cquery, pageQuery, insert 等）
- 对象 API 名称
- 响应码
- 耗时（毫秒）

### 日志管理

```bash
# 查看最近 50 条日志
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/logger.sh view 50

# 查看最近 3 天统计
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/logger.sh stats 3

# 搜索特定对象的调用
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/logger.sh search "productuplist"

# 导出日志
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/logger.sh export

# 清理 3 天前的日志
~/.openclaw/skills/cloudcc-openapi-withobject/scripts/logger.sh cleanup 3
```

### 日志保留策略

- 默认保留最近 **3 天** 的日志
- 可通过 `cleanup` 命令手动清理
- 可在 `config.json` 中配置 `logging.maxLogDays`
