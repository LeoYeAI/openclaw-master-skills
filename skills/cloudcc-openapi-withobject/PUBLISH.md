# 发布到 ClawHub 指南

## 前置准备

### 1. 登录 ClawHub

```bash
# 登录（会打开浏览器）
clawhub login

# 或手动访问登录链接
# https://clawhub.ai/cli/auth
```

### 2. 验证登录状态

```bash
clawhub whoami
```

---

## 发布技能

### 方法 1: 直接发布

```bash
cd ~/.openclaw/skills/cloudcc-openapi-withobject

# 发布技能
clawhub publish .
```

### 方法 2: 使用 sync 同步发布

```bash
cd ~/.openclaw/skills/

# 同步并发布所有新/更新的技能
clawhub sync
```

---

## 发布信息

| 属性 | 值 |
|------|-----|
| **技能名称** | cloudcc-openapi-withobject |
| **版本** | 2.1.0 |
| **描述** | CloudCC OpenAPI 调用技能 - 提供完整的 REST API 接口调用能力，支持对象/字段元数据查询和安全日志 |
| **作者** | 鲁班 |
| **许可证** | MIT |
| **分类** | productivity, business, development |
| **关键词** | cloudcc, crm, api, openapi, rest, metadata, logging |

---

## 发布后验证

```bash
# 搜索已发布的技能
clawhub search cloudcc-openapi-withobject

# 查看技能详情
clawhub inspect cloudcc-openapi-withobject

# 安装测试
clawhub install cloudcc-openapi-withobject
```

---

## 更新技能

```bash
# 修改技能后更新版本
# 1. 更新 package.json 中的 version
# 2. 更新 SKILL.md 中的版本历史
# 3. 重新发布

cd ~/.openclaw/skills/cloudcc-openapi-withobject
clawhub publish .
```

---

## 注意事项

1. **版本号** - 每次发布必须更新版本号（semver 格式）
2. **SKILL.md** - 必须包含完整的技能文档
3. **package.json** - 必须包含正确的元数据
4. **权限声明** - 在 package.json 中声明网络和文件权限
5. **测试** - 发布前确保所有脚本正常工作

---

## 故障排查

### 登录失败
```bash
# 清除登录状态重试
clawhub logout
clawhub login
```

### 发布失败
```bash
# 检查 package.json 格式
cat package.json | jq .

# 查看详细错误
clawhub publish . --verbose
```

### 技能已存在
```bash
# 更新现有技能（需要更高版本号）
clawhub publish . --force
```

---

## 技能包内容

```
cloudcc-openapi-withobject/
├── package.json          # 技能元数据（发布必需）
├── SKILL.md              # 完整技能文档
├── README.md             # 快速入门指南
├── PUBLISH.md            # 本文件
├── config.example.json   # 配置模板
├── logs/                 # 日志目录（不发布）
│   └── .gitkeep
└── scripts/
    ├── logger.sh         # 日志管理工具
    ├── get-token.sh      # 获取 accessToken
    ├── call-api.sh       # 通用 API 调用
    ├── find-object.sh    # 查找对象
    ├── get-objects.sh    # 获取对象列表
    └── get-fields.sh     # 获取对象字段
```

---

## ClawHub 链接

- **技能页面**: https://clawhub.com/skills/cloudcc-openapi-withobject
- **Registry**: https://clawhub.ai
- **文档**: https://docs.openclaw.ai
