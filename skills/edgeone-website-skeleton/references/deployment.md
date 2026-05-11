# 部署参考文档

> **版本：** v2.2 · **Phase：** Layer 0（Core）
> **部署平台：** EdgeOne Pages

---

## 一、快速部署

### 1.1 环境准备

```bash
# 1. 安装 EdgeOne CLI
npm install -g edgeone@latest

# 2. 登录（选择中国区）
edgeone login --site china

# 3. 查看账号
edgeone whoami
# → 刘博 · 100043397965
```

### 1.2 初始化项目

```bash
# 交互式初始化（回答引导问题）
npx create-edgeone-app

# 或手动创建后部署
cd my-site
edgeone pages deploy
```

### 1.3 环境变量配置（EdgeOne Console）

在 EdgeOne Console → 项目设置 → 环境变量中注入：

```bash
# === 认证（Phase 3 RS256）===
JWT_PRIVATE_KEY=<私钥内容，换行替换为\n>
JWT_PUBLIC_KEY=<公钥内容，换行替换为\n>
JWT_SECRET=<HS256密钥，30天兼容用>

# === 数据库 ===
DATABASE_URL=mysql://user:password@host:3306/dbname

# === 微信支付 ===
WX_APPID=wx...
WX_MCHID=1234567890
WX_API_KEY=...
WX_CERT_PATH=./cert/apiclient_cert.pem

# === 支付宝 ===
ALI_APP_ID=202100...
ALI_PRIVATE_KEY=...

# === AI（AI 栈）===
AI_API_KEY=sk-...

# === 内部网关 ===
EDGE_BASE=https://xxx.edgeone.dev

# === 站点 ===
SITE_URL=https://your-site.edgeone.cool
```

### 1.4 数据库迁移

```bash
# 1. 执行初始化迁移
mysql -h host -u user -p dbname < db/migrations/001_init.sql

# 2. 执行订单日志迁移
mysql -h host -u user -p dbname < db/migrations/002_order_logs.sql
```

### 1.5 部署

```bash
# 部署（自动构建 + 上传 + 部署）
edgeone pages deploy --project my-site --output ./dist

# 部署后查看 URL
edgeone pages list
```

---

## 二、部署配置（edgeone.json）

```json
{
  "name": "my-geek-mall",
  "output": "./dist",
  "env": "production",
  "routes": [
    {
      "pattern": "/api/*",
      "target": "edge-functions"
    },
    {
      "pattern": "/api/pay/*",
      "target": "cloud-functions"
    }
  ],
  "vars": {
    "SITE_URL": "https://my-geek-mall.edgeone.cool"
  }
}
```

---

## 三、Edge Functions vs Cloud Functions 路由

EdgeOne Pages 自动识别：
- `edge-functions/` → 编译为 Edge Functions（部署到全球边缘节点）
- `cloud-functions/` → 编译为 Cloud Functions（Node.js）
- `client/` → 编译为静态资源（SPA）

### 手动指定路由

在 `edgeone.json` 中配置路由规则：

```json
{
  "routing": {
    "/api/auth/*": "cloud-functions",
    "/api/pay/*": "cloud-functions",
    "/api/admin/*": "cloud-functions",
    "/api/order/*": "cloud-functions",
    "/api/ai/*": "cloud-functions",
    "/api/*": "edge-functions"
  }
}
```

---

## 四、KV Storage 配置

在 EdgeOne Console 中创建 KV 命名空间：

```
KV Namespaces:
  - main: 用于 Session、RT、Cart、AI History
```

绑定到 Edge Functions 环境变量：

```bash
KV_NAMESPACE=main
```

> ⚠️ **重要**：KV 仅 Edge Functions 可直接访问。Cloud Functions 需通过 HTTP 调用 Edge Function `edge-functions/api/internal/*` 访问 KV。

---

## 五、Cron 定时任务配置

在 `edgeone.json` 中配置定时触发器：

```json
{
  "triggers": [
    {
      "name": "order-cron",
      "type": "schedule",
      "cron": "*/5 * * * *",
      "function": "cloud-functions/cron/order-cron.js",
      "enabled": true
    }
  ]
}
```

或通过 EdgeOne Console UI 配置。

---

## 六、域名绑定（可选）

```bash
# 添加自定义域名
edgeone domains add --project my-site --domain shop.example.com

# 验证 DNS
edgeone domains verify --project my-site --domain shop.example.com

# 申请 SSL 证书（自动）
edgeone ssl issue --project my-site --domain shop.example.com
```

---

## 七、本地开发

```bash
# 1. 启动本地 Edge Functions 模拟器
edgeone dev

# 2. 启动本地 Next.js 开发服务器（单独进程）
npm run dev

# 3. 两个服务并行运行：
# - EdgeOne dev: http://localhost:8787
# - Next.js: http://localhost:3000
```

### 本地 .env.local

```bash
# .env.local（本地开发）
JWT_PRIVATE_KEY="$(cat keys/private.pem | tr '\n' ' ')"
JWT_PUBLIC_KEY="$(cat keys/public.pem | tr '\n' ' ')"
JWT_SECRET=local-dev-secret
DATABASE_URL=mysql://root:password@localhost:3306/geek_mall
EDGE_BASE=http://localhost:8787
```

---

## 八、回滚与监控

### 回滚

```bash
# 查看部署历史
edgeone pages deployments list --project my-site

# 回滚到指定版本
edgeone pages rollback --project my-site --deployment d-xxxxx
```

### 监控

```bash
# 查看实时日志
edgeone logs --project my-site --function edge-functions/api/products/list.js --tail

# 查看调用统计
edgeone pages stats --project my-site --period 24h
```

---

## 九、常见问题

### Q: 部署后 KV 数据丢失？
A: KV 数据在项目关联的 KV Namespace 中，删除项目会清空。迁移时需导出 KV 数据。

### Q: Cloud Functions 访问不到 KV？
A: 这是 EdgeOne Pages 平台约束。解决方案：通过 `fetch(EDGE_BASE + '/api/internal/idempotency')` 从 Cloud 调用 Edge Function 访问 KV。

### Q: 微信回调返回 "签名验证失败"？
A: 微信 V3 回调需使用微信平台证书公钥验签，证书每 1 年需更新。

### Q: JWT RS256 签发失败？
A: 检查 `JWT_PRIVATE_KEY` 环境变量格式，确保换行符正确转义为 `\n`。
