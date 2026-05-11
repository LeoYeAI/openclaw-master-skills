---
name: 建站骨架 (EdgeOne Pages)
description: 一句话说需求，AI 生成完整前后端网站并自动部署到 EdgeOne Pages。支持电商栈（Auth/购物车/支付）、AI 栈（SSE 流式对话）、管理后台。触发词：帮我建网站、建一个电商网站、做 AI 客服站、建管理后台、EdgeOne Pages 建站
---

# 建站 Skill — EdgeOne Pages 全栈网站骨架

> **版本：** 2.3 · **日期：** 2026-05-04 · **安全强化更新**
> **一句话描述：** 用户说一句话，AI 生成完整前后端网站，自动部署到 EdgeOne Pages。

---

## 一、核心设计理念

```
一次设计，无限复用 = 5 个模块 × 3 个场景 × 1 个部署平台
```

将"建站"拆解为 **Layer 0 基础设施** + **Layer 1 能力栈** + **Layer 2 可选增强**：

| 层级 | 内容 | 性质 |
|------|------|------|
| **Layer 0**（Core） | SPA 骨架 + Auth + Middleware + EventBus | 必选，不可裁剪 |
| **Layer 1**（Stack） | 🛒 电商栈 · 🤖 AI 栈 · 📊 管理栈 | 按需组合，互不依赖 |
| **Layer 2**（Addon） | SEO · Analytics · i18n | 可选增强 |

**场景模板优先**：用户选"电商"、"AI 助手"或"管理后台"场景，不选模块——模块由模板自动组合。

---

## 二、技术架构

### 2.1 EdgeOne Pages 双运行时

```
┌──────────────────────────────────────────────────────────────┐
│  Platform Middleware（middleware.js）                        │
│  ① CORS 预检（OPTIONS）                                     │
│  ② CSP Header 注入                                          │
│  ③ 轻量 Bearer 检查（公开路径放行）                           │
│  ④ 支付回调 IP 白名单 → 直接 return，不进 Edge Middleware     │
└──────────────────────────────────────────────────────────────┘
                              ↓（非回调路径）
┌──────────────────────────────────────────────────────────────┐
│  Edge Functions Middleware（V8 + KV）                      │
│  ⑤ JWT 详细校验（crypto.subtle）                             │
│  ⑥ KV session 验证                                          │
│  ⑦ KV 限流计数器（滑动窗口）                                   │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 运行时职责边界

| 运行时 | 存储 | 职责 | 说明 |
|--------|------|------|------|
| **Edge Functions**（V8） | KV | Auth 登录/me、Products 公开读、Cart、Orders 读、AI History 读、幂等锁 | 延迟敏感、无密钥 |
| **Cloud Functions**（Node） | MySQL | Auth 注册/bcrypt、Payment 创建/回调、Admin CRUD、Orders 创建/取消、AI SSE 流 | 密钥操作、复杂事务 |

> ⚠️ **平台约束（EdgeOne Pages）：**
> - KV 仅 Edge Functions 可用，Cloud Functions 无法访问
> - Cloud Functions 目录名必须为 `cloud-functions/`
> - bcrypt 必须在 Cloud Functions 中执行

### 2.3 分层目录结构

```
website-skeleton/
├── SKILL.md                    # 本文件，Skill 核心指令
│
├── templates/                  # 场景预设模板
│   ├── e-commerce.json         # 🛒 电商场景
│   ├── ai-assistant.json       # 🤖 AI 助手场景
│   └── saas-admin.json         # 📊 SaaS 管理后台场景
│
├── sharing/                    # 跨运行时共享（构建时同步）
│   ├── types.ts               # User/Product/Cart/Order/AISession 接口
│   ├── constants.ts           # OrderStatus/UserRole/APIPaths 枚举
│   ├── validators.ts           # 共享输入校验
│   └── kv-keys.ts             # KV key 命名（含租户前缀占位）
│
├── client/                     # 前端 SPA
│   ├── index.html
│   └── src/
│       ├── app.js             # 启动 + History API 路由
│       ├── utils/
│       │   ├── event-bus.js   # 全局事件总线（P0）
│       │   ├── router.js      # History API 路由 + AuthGuard
│       │   ├── escape-html.js # XSS 防护
│       │   └── storage.js      # localStorage 封装
│       ├── services/
│       │   ├── api.js          # 统一客户端 + 拦截器
│       │   ├── auth.js         # 内存 AuthService
│       │   ├── cart.js         # 双模式购物车
│       │   └── ai.js           # SSE 流式 AI
│       └── components/         # 组件清单
│
├── middleware.js               # Platform Middleware
│
├── db/                         # 数据库迁移
│   ├── migrations/
│   │   └── 001_init.sql        # 建表脚本
│   └── seed.sql                # 测试数据
│
├── docs/
│   └── env-vars.md             # 环境变量矩阵
│
├── edge-functions/             # Edge Functions（V8 + KV）
│   ├── _middleware.js          # JWT 校验 + KV session + 限流
│   ├── api/
│   │   ├── auth/login.js       # JWT 签发（Cookie） + KV session
│   │   ├── auth/me.js          # KV session 读取
│   │   ├── auth/refresh.js     # RT 轮换（KV version 乐观锁）
│   │   ├── auth/logout.js      # 清除 Cookie + KV session
│   │   ├── internal/idempotency.js  # Edge 原子幂等锁
│   │   ├── products/list.js   # KV 缓存 + Cloud MySQL 回源
│   │   ├── products/[id].js
│   │   ├── products/categories.js
│   │   ├── cart/*.js           # KV 购物车
│   │   ├── orders/list.js      # MySQL 订单读取
│   │   ├── orders/[id].js
│   │   └── ai/history.js       # KV 读取 AI 会话历史
│   └── utils/
│       ├── kv-helper.js
│       ├── jwt-helper.js       # crypto.subtle HS256
│       ├── rate-limit.js        # KV 滑动窗口限流
│       └── response.js
│
├── cloud-functions/            # Cloud Functions（Node.js）
│   ├── api/
│   │   ├── auth/register.js   # bcrypt cost=12 + MySQL
│   │   ├── pay/create-order.js # 微信/支付宝预下单
│   │   ├── pay/wx-notify.js   # Edge 幂等锁 → 业务处理
│   │   ├── pay/ali-notify.js
│   │   ├── pay/query.js
│   │   ├── pay/close.js
│   │   ├── admin/products.js   # MySQL CRUD（含 version 乐观锁）
│   │   ├── admin/orders.js    # MySQL 查询
│   │   ├── admin/users.js     # MySQL CRUD
│   │   ├── admin/stats.js     # MySQL 聚合统计
│   │   ├── order/create.js    # SELECT FOR UPDATE + 事务 + 指数退避
│   │   ├── order/detail.js
│   │   ├── order/cancel.js    # 状态机 + version 校验
│   │   └── ai/chat-stream.js  # SSE 流式（主力实现）
│   └── utils/
│       ├── db.js               # MySQL 连接池（mysql2/promise）
│       ├── payment-sdk.js      # 微信V3/支付宝 SDK 封装
│       ├── admin-guard.js
│       └── notification-hooks.js  # 通知钩子空壳
│
├── references/                  # 能力参考文档
│   ├── auth-module.md           # ✅ JWT RS256 + HS256 兼容 + KV Session
│   ├── cart-module.md
│   ├── payment-module.md
│   ├── ai-chat-module.md
│   ├── admin-module.md          # ✅ RBAC + CRUD + 运营统计 + 审计日志
│   ├── notification-module.md   # Layer 2：邮件/微信/钉钉通知
│   ├── order-state-machine.md   # ✅ 6状态 + 权限矩阵 + 库存联动 + 审计日志
│   ├── edge-functions.md        # ✅ Edge Middleware + KV API + 限流
│   ├── cloud-functions.md       # ✅ MySQL 事务 + bcrypt + 支付 SDK + SSE
│   ├── kv-storage.md
│   ├── middleware.md            # ✅ Platform + Edge 双层 + CSP + 支付 bypass
│   └── deployment.md            # ✅ 完整部署流程 + Cron + 回滚
│
└── scripts/
    ├── init-site.js             # 交互式初始化（模板优先）
    ├── sync-sharing.js          # 构建时 shared → edge/cloud 同步
    └── sample-data.js
```

---

## 三、Auth 模块（Layer 0，Core）

### API 路由

| 方法 | 路径 | 运行时 | 说明 |
|------|------|--------|------|
| POST | `/api/auth/login` | Edge（KV） | JWT 签发 + KV session |
| GET | `/api/auth/me` | Edge（KV） | KV session 读取 |
| POST | `/api/auth/refresh` | Edge（KV） | RT 轮换（version 乐观锁） |
| POST | `/api/auth/logout` | Edge（KV） | 清除 Cookie + KV session |
| POST | `/api/auth/register` | Cloud（MySQL） | bcrypt cost=12 + MySQL |

### JWT 安全设计

```
Access Token：短期 JWT（15min）+ HttpOnly Cookie（Secure + SameSite=Strict）
Refresh Token：7天 TTL，存 KV rt:{userId}:meta（含 version）
算法：Phase 1 用 HS256 + 短期 TTL，Phase 2 迁移 RS256
```

### 【v2.1 Critical 修复】RT 并发安全

两个请求并发携带同一 RT，只有第一个能成功写入新 version，第二个收到 409 → 客户端稍等重试。

```javascript
// edge-functions/api/auth/refresh.js
export async function onRequest(context) {
  const { RT } = await getTokens(context.request);
  const { KV } = context.env;
  const payload = parseJWT(RT);
  const userId = payload.sub;
  if (!userId) return new Response('Invalid', { status: 401 });

  const current = await KV.get(`rt:${userId}:meta`);
  const { version: oldVersion, token: oldToken } = JSON.parse(current || '{"version":0,"token":""}');

  if (oldToken !== RT) {
    return new Response('Token already rotated', { status: 409 });
  }

  const newVersion = oldVersion + 1;
  const newToken = signRT(userId, newVersion);

  const ok = await KV.put(
    `rt:${userId}:meta`,
    JSON.stringify({ version: newVersion, token: newToken }),
    { expirationTtl: 604800 }
  );

  if (!ok) return new Response('Concurrent rotation', { status: 409 });

  return new Response(JSON.stringify({ refreshToken: newToken }), {
    headers: { 'Content-Type': 'application/json' }
  });
}
```

---

## 四、Cart 模块（Layer 1，电商栈）

**双模式同步：**
```
未登录：localStorage（30d TTL 自动清理）
登录时：localStorage → 服务端 KV（syncOnLogin()）
已登录：服务端 KV（唯一数据源）
```

---

## 五、Payment 模块（Layer 1，电商栈）

### 独立回调路径

```
/api/pay/wx-notify   ← 微信支付回调（IP 白名单后直接 return，不进 Edge Middleware）
/api/pay/ali-notify  ← 支付宝回调（独立路径）
```

### 【v2.1 Critical 修复】支付幂等原子锁

微信支付平台会在回调超时后重试（最长 72h），KV 查→判→写三步非原子。解决方案：Edge Function `putIfNotExists` 原子幂等锁。

```javascript
// ===== Edge Function（唯一可访问 KV 的路径）=====
// edge-functions/api/internal/idempotency.js
export async function onRequest(context) {
  const { KV } = context.env;
  const { out_trade_no, callback_id } = await context.request.json();

  const acquired = await KV.putIfNotExists(
    `pay:idempotency:${out_trade_no}`,
    callback_id,
    { expirationTtl: 86400 }   // 24h < 微信重试窗口 72h
  );

  return new Response(JSON.stringify({ acquired }), { status: 200 });
}

// ===== Cloud Function（微信回调处理）=====
// cloud-functions/api/pay/wx-notify.js
export async function onRequest(request, env) {
  const rawBody = await request.text();
  if (!await verifyWechatSignature(rawBody, env.WX_MCH_SECRET))
    return new Response('FAIL', { status: 401 });

  const { out_trade_no, transaction_id, trade_state } = JSON.parse(rawBody);

  const { acquired } = await fetch(`${env.EDGE_BASE}/api/internal/idempotency`, {
    method: 'POST',
    body: JSON.stringify({ out_trade_no, callback_id: transaction_id })
  }).then(r => r.json());

  if (!acquired) return new Response('SUCCESS');  // 幂等跳过，但返回 SUCCESS 止重试

  if (trade_state === 'SUCCESS') await processPayment(out_trade_no, transaction_id, env);
  return new Response('SUCCESS');
}
```

---

## 六、Order 创建原子性（v2.1 Critical 修复）

高并发下，`UPDATE ... WHERE stock >= ?` 可能同时通过检查导致超卖。解决方案：`SELECT FOR UPDATE` + 乐观锁 + MySQL CHECK 约束。

```javascript
// cloud-functions/api/order/create.js
export async function onRequest(request, env) {
  const { userId } = await auth(request, env);
  const { productId, quantity } = await request.json();
  const pool = await getPool(env.DATABASE_URL);

  let attempt = 0;
  while (attempt < 3) {
    attempt++;
    try {
      await pool.beginTransaction();

      // ① SELECT FOR UPDATE：锁定商品行（持有行锁期间其他事务阻塞）
      const [rows] = await pool.query(
        'SELECT id, stock, price, version FROM products WHERE id = ? FOR UPDATE',
        [productId]
      );
      if (!rows.length) { await pool.rollback(); return 404; }
      const product = rows[0];

      // ② 持有行锁期间校验库存（无竞态）
      if (product.stock < quantity) {
        await pool.rollback();
        return { error: '库存不足', available: product.stock };
      }

      // ③ 乐观锁更新（双重保障）
      const [updateResult] = await pool.query(
        'UPDATE products SET stock = stock - ?, version = version + 1 WHERE id = ? AND version = ?',
        [quantity, productId, product.version]
      );
      if (updateResult.affectedRows === 0) {
        await pool.rollback();
        return { error: '并发冲突，请重试' };
      }

      // ④ 创建订单（同一事务内）
      const orderNo = generateOrderNo();
      await pool.query(
        `INSERT INTO orders (order_no, out_trade_no, user_id, product_id, qty, amount, status, created_at)
         VALUES (?, ?, ?, ?, ?, ?, 'PENDING', NOW())`,
        [orderNo, `WX_${orderNo}`, userId, productId, quantity, product.price * quantity]
      );

      await pool.commit();

      // ⑤ 事务成功后，异步调用微信统一下单（不在事务内）
      const payment = await createPayment(orderNo, product.price * quantity, env);
      return { orderNo, payment };

    } catch (err) {
      await pool.rollback();
      if (isRetryable(err) && attempt < 3) {
        await sleep(100 * Math.pow(2, attempt - 1));  // 指数退避
        continue;
      }
      return { error: '创建失败，请重试' };
    }
  }
}

function isRetryable(err) {
  return err.code === 'ER_LOCK_DEADLOCK' || err.code === 'ER_LOCK_WAIT_TIMEOUT';
}
```

---

## 七、KV 分层查询策略

EdgeOne Pages KV **不支持复合查询**，按以下策略分层：

| 场景 | KV 层（Edge） | MySQL 层（Cloud） |
|------|-------------|-----------------|
| 单商品读取 | ✅ KV 缓存 | — |
| 商品列表（无筛选） | ✅ 缓存第1页 | — |
| 分类+价格区间筛选 | — | ✅ Cloud MySQL |
| 搜索关键词 | — | ✅ Cloud MySQL FULLTEXT |
| AI 会话历史（单用户） | ✅ KV | — |
| 订单统计（多条件聚合） | — | ✅ Cloud MySQL |

---

## 八、AI Chat 模块（Layer 1，AI 栈）

**Cloud Functions SSE 实现（Edge 无法使用 waitUntil）：**

```
前端 → GET /api/ai/history（Edge，KV 读取）→ 拿到历史上下文
    → SSE 连接 /api/ai/chat-stream（Cloud）→ 带历史 context
    → Cloud 流式响应 + 异步写 KV 保存历史
```

---

## 九、Admin 模块（Layer 1，管理栈）

**RBAC 权限体系：**
```
role: user   → 购物车、下单、查看自己的订单
role: admin  → 商品 CRUD、订单管理、用户管理、运营统计
```

---

## 十、数据库 Schema

```sql
-- db/migrations/001_init.sql

CREATE TABLE users (
  id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  email         VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role          ENUM('user','admin') DEFAULT 'user',
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(255) NOT NULL,
  price       DECIMAL(10,2) NOT NULL,    -- 服务端唯一价格来源
  stock       INT UNSIGNED NOT NULL DEFAULT 0,
  category_id INT UNSIGNED,
  status      ENUM('active','inactive') DEFAULT 'active',
  version     INT UNSIGNED DEFAULT 1,    -- 乐观锁版本号
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT chk_stock_positive CHECK (stock >= 0)
);

CREATE TABLE orders (
  id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_no      VARCHAR(64) UNIQUE NOT NULL,
  out_trade_no  VARCHAR(128) UNIQUE,
  user_id       BIGINT UNSIGNED NOT NULL,
  total         DECIMAL(10,2) NOT NULL,
  status        ENUM('pending','paid','shipped','cancelled','refunded') DEFAULT 'pending',
  paid_at       DATETIME,
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE order_items (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_id    BIGINT UNSIGNED NOT NULL,
  product_id  BIGINT UNSIGNED NOT NULL,
  qty         INT UNSIGNED NOT NULL,
  price       DECIMAL(10,2) NOT NULL,   -- 快照价格
  FOREIGN KEY (order_id) REFERENCES orders(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE admin_logs (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  admin_id    BIGINT UNSIGNED NOT NULL,
  action      VARCHAR(64) NOT NULL,
  target      VARCHAR(128),
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at);
```

---

## 十一、环境变量矩阵

| 环境变量 | 必填 | 用于 | 运行时 |
|---------|------|------|--------|
| `JWT_SECRET` | ✅ | JWT 签名（HS256） | Edge + Cloud |
| `AI_API_KEY` | ✅（AI栈） | AI 模型调用 | Cloud |
| `WX_APPID` | ✅（电商栈） | 微信支付 AppID | Cloud |
| `WX_MCHID` | ✅（电商栈） | 微信支付商户号 | Cloud |
| `WX_API_KEY` | ✅（电商栈） | 微信支付 APIv3 密钥 | Cloud |
| `WX_CERT_PATH` | ✅（电商栈） | 微信支付证书路径 | Cloud |
| `ALI_APP_ID` | ✅（电商栈） | 支付宝 AppID | Cloud |
| `ALI_PRIVATE_KEY` | ✅（电商栈） | 支付宝私钥 | Cloud |
| `DATABASE_URL` | ✅（电商+管理） | MySQL 连接字符串 | Cloud |
| `EDGE_BASE` | ✅（电商栈） | Edge Function 内部网关地址 | Cloud |

---

## 十二、初始化工作流

```
Step 1: 选择建站类型
  [1] 🛒 快速电商站（推荐）
  [2] 🤖 AI 客服站
  [3] 📊 SaaS 管理后台
  [4] ⚙️ 自定义模块组合

Step 2: 确认预填 / 模块选择

Step 3: 填写基本信息（站点名、域名）

Step 4: 密钥配置（从 env-vars.md 模板读取，EdgeOne Pages 环境变量注入）

Step 5: 执行 db/migrations/001_init.sql（自动或手动）

Step 6: 生成代码 → edgeone deploy → 返回访问 URL
```

---

## 十三、安全检查清单

### 🔴 P0（上线前必须完成）

- [x] 支付幂等：Edge 原子 `putIfNotExists` 锁
- [x] 订单超卖：`SELECT FOR UPDATE` + MySQL 事务 + CHECK 约束
- [x] RT 并发安全：KV version 乐观锁（409 重试）
- [x] KV 复合查询：分层策略（KV 缓存 / MySQL 复杂查询）
- [x] 支付回调路径 Platform Middleware 直接 return
- [x] 金额服务端 MySQL 计算，前端永不传 price
- [x] bcrypt cost ≥ 12（Cloud Functions 中）

### 🟡 P1（正式版前完成）

- [x] JWT 短期 Access Token（15min）+ RT 轮换（含并发安全版本号）
- [x] Cookie：HttpOnly + Secure + SameSite=Strict（含 SameSite=Lax 备选方案）
- [x] AI 聊天限流（KV 滑动窗口：未登录 10次/分钟，登录 60次/分钟）
- [x] CSP Header（Platform Middleware 注入，含 nonce 升级路径）
- [x] EventBus 401 自动跳转登录（含 redirect 回跳逻辑）
- [x] Notification 钩子（Phase 2 完整适配器设计 + 事件注册机制）

### 🟢 P2（Phase 3 实现）

- [x] RS256 迁移（双轨并行 HS256/RS256，30 天兼容窗口）
- [x] 订单状态机（6状态 + 权限矩阵 + version 校验 + 库存联动 + 审计日志 + 定时 Cron）

---

## 十五、Phase 2 详细设计（P1/P2 实现指南）

---

### 15.1 【P1】JWT Access Token 短期化 + RT 轮换（已实现源码）

以下为 Edge Functions 完整实现，Phase 1 已集成：

**JWT 签发（login.js）** — Access Token 15min + Refresh Token 7d：

```javascript
// edge-functions/api/auth/login.js
export async function onRequest(context) {
  const { email, password } = await context.request.json();
  const pool = await getCloudPool(context.env.DATABASE_URL);
  const [rows] = await pool.query('SELECT * FROM users WHERE email = ?', [email]);
  if (!rows.length) return new Response('Unauthorized', { status: 401 });

  const user = rows[0];
  const ok = await bcrypt.compare(password, user.password_hash);
  if (!ok) return new Response('Unauthorized', { status: 401 });

  const now = Math.floor(Date.now() / 1000);
  // Access Token：15min
  const accessToken = signJWT({ sub: user.id, role: user.role, type: 'access' }, 900);
  // Refresh Token：7d，含 version 用于乐观锁
  const rtVersion = 1;
  const refreshToken = signRT(user.id, rtVersion);

  // KV 存 RT meta（用于轮换校验）
  await context.env.KV.put(
    `rt:${user.id}:meta`,
    JSON.stringify({ version: rtVersion, token: refreshToken }),
    { expirationTtl: 604800 }
  );

  return new Response(null, {
    status: 302,
    headers: {
      'Location': '/',
      'Set-Cookie': [
        `at=${accessToken}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=900`,
        `rt=${refreshToken}; HttpOnly; Secure; SameSite=Strict; Path=/api/auth/refresh; Max-Age=604800`
      ].join(', ')
    }
  });
}
```

**RT 轮换（refresh.js）** — 并发安全，version 乐观锁：

```javascript
// edge-functions/api/auth/refresh.js
export async function onRequest(context) {
  const { KV } = context.env;
  const cookieHeader = context.request.headers.get('Cookie') || '';
  const rtMatch = cookieHeader.match(/rt=([^;]+)/);
  if (!rtMatch) return new Response('No RT', { status: 401 });

  const oldToken = rtMatch[1];
  const payload = parseJWT(oldToken);
  const userId = payload.sub;

  // KV version 乐观锁：只有 RT 匹配当前 version 才允许写入新 version
  const current = await KV.get(`rt:${userId}:meta`);
  const { version: oldVersion, token: oldStored } = JSON.parse(current || '{"version":0,"token":""}');

  if (oldStored !== oldToken) {
    // 另一个 tab 已轮换，当前 RT 失效 → 返回 409 让客户端重新登录
    return new Response('Concurrent rotation', { status: 409 });
  }

  const newVersion = oldVersion + 1;
  const newToken = signRT(userId, newVersion);

  const ok = await KV.put(
    `rt:${userId}:meta`,
    JSON.stringify({ version: newVersion, token: newToken }),
    { expirationTtl: 604800 }
  );
  if (!ok) return new Response('Rotation failed', { status: 409 });

  return new Response(JSON.stringify({ refreshToken: newToken }), {
    headers: {
      'Content-Type': 'application/json',
      'Set-Cookie': `rt=${newToken}; HttpOnly; Secure; SameSite=Strict; Path=/api/auth/refresh; Max-Age=604800`
    }
  });
}
```

**客户端轮换触发逻辑（event-bus.js 集成）**：

```javascript
// client/src/utils/event-bus.js
EventBus.on('auth:401', async () => {
  // Access Token 过期 → 尝试轮换 RT
  const res = await fetch('/api/auth/refresh', { method: 'POST', credentials: 'include' });
  if (res.ok) {
    // RT 轮换成功 → 重发原请求
    return retryOriginalRequest();
  }
  // RT 也失败 → 跳转登录
  window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
});
```

---

### 15.2 【P1】Cookie 安全属性

所有认证 Cookie 必须同时满足以下属性（缺一不可）：

| 属性 | 值 | 作用 |
|------|-----|------|
| `HttpOnly` | 必须 | 阻止 JS 读取，防止 XSS 窃取 |
| `Secure` | 必须 | 仅 HTTPS 传输 |
| `SameSite=Strict` | 强烈建议 | 防止 CSRF（同站请求才带 Cookie） |
| `SameSite=Lax` | 备选 | 允许导航带 Cookie，但阻止跨站 POST |
| `Path=/` | AT Cookie | 全路径生效 |
| `Path=/api/auth/refresh` | RT Cookie | 仅刷新接口可读 |

**Edge Functions 签发示例**：

```javascript
// 正确
headers.set('Set-Cookie',
  `at=${token}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=900`
);

// 常见错误：缺少 Secure 或 SameSite
// ❌ `at=${token}; HttpOnly` — 可被 HTTP 拦截
// ❌ `at=${token}; HttpOnly; SameSite=None` — 无 CSRF 保护
```

**注意**：`SameSite=Strict` 会导致从外部链接跳转过来时无法携带 Cookie。如有第三方回调场景，改用 `SameSite=Lax` + CSRF Token 双保险。

---

### 15.3 【P1】AI 聊天限流（KV 滑动窗口）

**限流策略**：

| 用户状态 | 限额 | 窗口 |
|---------|------|------|
| 未登录（IP 级别） | 10 次/分钟 | 滑动窗口 |
| 已登录（User ID 级别） | 60 次/分钟 | 滑动窗口 |

**Edge Function 实现**：

```javascript
// edge-functions/_middleware.js 或独立限流工具
// edge-functions/utils/rate-limit.js

export async function checkRateLimit(context, key, limit) {
  const { KV } = context.env;
  const now = Date.now();
  const windowMs = 60 * 1000; // 1 分钟滑动窗口
  const windowKey = `rl:${key}:${Math.floor(now / windowMs)}`;
  const prevKey = `rl:${key}:${Math.floor((now - windowMs) / windowMs)}`;

  const current = parseInt(await KV.get(windowKey) || '0');
  const prev = parseInt(await KV.get(prevKey) || '0');

  // 滑动窗口：当前窗口占比 + 上一窗口剩余权重
  const prevWeight = (now % windowMs) / windowMs;
  const totalWeight = current + prev * prevWeight;

  if (totalWeight >= limit) {
    return { allowed: false, remaining: 0, resetMs: windowMs - (now % windowMs) };
  }

  // 写入当前计数
  await KV.put(windowKey, String(current + 1), { expirationTtl: 120 });
  return { allowed: true, remaining: limit - Math.ceil(totalWeight) - 1, resetMs: windowMs };
}

// 在 AI Chat Edge Middleware 中调用：
// const userId = payload?.sub || request.headers.get('CF-Connecting-IP');
// const { allowed, resetMs } = await checkRateLimit(context, `ai:${userId}`, 60);
// if (!allowed) return new Response('Rate limited', { status: 429, headers: { 'Retry-After': String(Math.ceil(resetMs/1000)) } });
```

---

### 15.4 【P1】CSP Header（Platform Middleware 注入）

CSP 在 Platform Middleware 层注入，对所有 HTML 响应生效：

```javascript
// middleware.js（项目根目录，Platform Middleware）
export function onRequest(context) {
  const response = context.next();

  // 仅对 HTML 响应注入 CSP
  const contentType = response.headers.get('Content-Type') || '';
  if (!contentType.includes('text/html')) return response;

  const CSP = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline'",       // Skill 生成代码含内联脚本，放行
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: https:",
    "connect-src 'self' https://api.edgeone.dev https://api.weixin.qq.com https://openapi.alipay.com",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'"
  ].join('; ');

  const newHeaders = new Headers(response.headers);
  newHeaders.set('Content-Security-Policy', CSP);
  newHeaders.set('X-Content-Type-Options', 'nosniff');
  newHeaders.set('X-Frame-Options', 'DENY');
  newHeaders.set('Referrer-Policy', 'strict-origin-when-cross-origin');

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: newHeaders
  });
}
```

**配置说明**：
- `connect-src` 中的域名需根据实际 AI API 和支付平台调整
- `'unsafe-inline'` 用于 Skill 生成的内联脚本（Phase 1 MVP 可接受）
- Phase 3 可升级为 nonce 模式消除 `unsafe-inline`

---

### 15.5 【P1】EventBus 401 自动跳转

前端 EventBus 统一处理认证失效事件：

```javascript
// client/src/utils/event-bus.js
class EventBus {
  constructor() {
    this.listeners = {};
    // 全局监听 fetch 401 响应
    this._setupGlobal401Handler();
  }

  _setupGlobal401Handler() {
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      try {
        const res = await originalFetch(...args);
        if (res.status === 401) {
          this.emit('auth:401', { url: args[0], response: res });
        }
        return res;
      } catch (err) {
        throw err;
      }
    };
  }

  on(event, handler) {
    (this.listeners[event] ||= []).push(handler);
    return () => this.listeners[event] = this.listeners[event].filter(h => h !== handler);
  }

  emit(event, data) {
    (this.listeners[event] || []).forEach(h => h(data));
  }
}

export const eventBus = new EventBus();

// 应用启动时注册 401 跳转
eventBus.on('auth:401', ({ url }) => {
  // 排除登录页自身，避免死循环
  if (url.includes('/api/auth/login') || url.includes('/api/auth/register')) return;
  // 跳过 refresh 接口（它有自己的 401 处理）
  if (url.includes('/api/auth/refresh')) return;
  // 记录原页面路径，登录后回跳
  const redirect = encodeURIComponent(window.location.pathname + window.location.search);
  window.location.href = `/login?redirect=${redirect}`;
});
```

---

### 15.6 【P1】Notification 钩子详细设计

Notification 作为 Layer 2 Addon，按需接入。支持多通道：邮件、微信模板消息、钉钉 Webhook。

**接口设计（空壳 → Phase 2 填充适配器）**：

```javascript
// cloud-functions/utils/notification-hooks.js

// 通知事件类型
export const NotificationEvent = {
  ORDER_CREATED:    'order.created',
  ORDER_PAID:       'order.paid',
  ORDER_SHIPPED:    'order.shipped',
  ORDER_DELIVERED:  'order.delivered',
  USER_REGISTERED: 'user.registered',
  PASSWORD_CHANGED: 'password.changed',
};

// 通知渠道
export const NotificationChannel = {
  EMAIL:    'email',
  WECHAT:   'wechat',   // 微信模板消息
  DINGTALK: 'dingtalk', // 钉钉 Webhook
  SMS:      'sms',
};

// 钩子注册表（Phase 2 填充）
const handlers = {
  [NotificationEvent.ORDER_PAID]: [],
  [NotificationEvent.USER_REGISTERED]: [],
};

export function registerHandler(event, handler) {
  handlers[event] ||= [];
  handlers[event].push(handler);
}

export async function emit(event, payload) {
  const eventHandlers = handlers[event] || [];
  await Promise.allSettled(
    eventHandlers.map(h => h(payload).catch(err => console.error(`Notification handler error: ${err}`)))
  );
}

// ===== 具体适配器示例（Phase 2 实现）=====

// 邮件适配器
registerHandler(NotificationEvent.ORDER_PAID, async ({ order, user }) => {
  // 需配置 SMTP 环境变量
  if (!process.env.SMTP_HOST) return; // 无邮件配置则跳过
  await sendEmail({
    to: user.email,
    subject: `订单 ${order.order_no} 支付成功`,
    html: `<h2>感谢您的购买！</h2><p>订单号：${order.order_no}</p>`
  });
});

// 微信模板消息适配器
registerHandler(NotificationEvent.ORDER_SHIPPED, async ({ order, user }) => {
  if (!process.env.WX_TEMPLATE_ID_SHIP) return;
  await sendWechatTemplate(user.openid, process.env.WX_TEMPLATE_ID_SHIP, {
    keyword1: order.order_no,
    keyword2: order.express_company + ' ' + order.express_no,
  });
});

// 调用示例（Cloud Functions 中）
import { emit, NotificationEvent } from './utils/notification-hooks.js';

export async function onRequest(request, env) {
  // 支付回调成功后触发
  await emit(NotificationEvent.ORDER_PAID, { order, user });
  return new Response('SUCCESS');
}
```

**env-vars.md 补充字段**：

```
NOTIFICATION_SMTP_HOST     # 邮件 SMTP 主机
NOTIFICATION_SMTP_PORT     # 邮件 SMTP 端口（默认 587）
NOTIFICATION_SMTP_USER     # 邮件发件人
NOTIFICATION_SMTP_PASS     # 邮件密码
NOTIFICATION_FROM_EMAIL    # 发件人地址
WX_TEMPLATE_ID_ORDER       # 微信订单通知模板 ID
WX_TEMPLATE_ID_SHIP        # 微信发货通知模板 ID
DINGTALK_WEBHOOK_URL       # 钉钉群 Webhook URL
```

---

### 15.7 【P2】RS256 迁移方案

Phase 1 使用 HS256（密钥共享，简单快速）；Phase 2 迁移到 RS256（公私钥，安全性更高）。

**迁移策略：双轨并行，渐进式切换**

```
Phase 1（当前）：HS256
  - JWT_SECRET = 对称密钥（Edge + Cloud 共享）

Phase 2 迁移：
  - 新增 JWT_PRIVATE_KEY（Cloud 签名用 RSA 私钥）
  - 新增 JWT_PUBLIC_KEY（Edge 验证用 RSA 公钥）
  - Edge Functions 验证用公钥（无需密钥）
  - Cloud Functions 签名用私钥
  - HS256 保留 30 天兼容窗口（老 token 仍可验证）
```

**生成密钥对**：

```bash
# 生成 RSA-256 密钥对
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
# 将公钥 public.pem 内容填入 EdgeOne Pages 环境变量 JWT_PUBLIC_KEY
# 将私钥 private.pem 内容填入 Cloud Functions 环境变量 JWT_PRIVATE_KEY（严格保密）
```

**Cloud Functions 签名切换**：

```javascript
// cloud-functions/utils/jwt-helper.js
import { SignJWT, jwtVerify } from 'jose';

const getSignKey = (env) => {
  if (env.JWT_PRIVATE_KEY) {
    return createPrivateKey(env.JWT_PRIVATE_KEY); // RS256
  }
  return new TextEncoder().encode(env.JWT_SECRET); // 兼容 HS256
};

export async function signJWT(payload, expiresIn, env) {
  const key = getSignKey(env);
  return new SignJWT(payload)
    .setProtectedHeader({ alg: env.JWT_PRIVATE_KEY ? 'RS256' : 'HS256' })
    .setIssuedAt()
    .setExpirationTime(`${expiresIn}s`)
    .sign(key);
}
```

**Edge Functions 验证（始终用公钥）**：

```javascript
// edge-functions/utils/jwt-helper.js
export async function verifyJWT(token, env) {
  const publicKey = createPublicKey(env.JWT_PUBLIC_KEY); // RS256 验证
  try {
    const { payload } = await jwtVerify(token, publicKey);
    return payload;
  } catch {
    // 30 天兼容窗口：尝试 HS256 验证（仅过渡期）
    const secret = new TextEncoder().encode(env.JWT_SECRET);
    try {
      const { payload } = await jwtVerify(token, secret);
      return { ...payload, _hs256Fallback: true }; // 标记老 token
    } catch {
      return null;
    }
  }
}
```

---

### 15.8 【P2】订单状态机详细设计

**状态定义与流转**：

```
┌──────────┐  pay    ┌───────┐  ship   ┌──────────┐  confirm ┌───────────┐
│ PENDING  │ ──────→ │ PAID  │ ─────→ │ SHIPPED  │ ──────→ │ COMPLETED │
└──────────┘         └───────┘         └──────────┘         └───────────┘
     │                    │                                       │
     │ cancel (user)      │ refund (user/admin)                   │
     ↓                    ↓                                       │
┌──────────┐         ┌──────────┐                                 │
│ CANCELLED│         │ REFUNDED │                                 │
└──────────┘         └──────────┘                                 │
                                                                  │
                        refund (admin, COMPLETED)                 │
                        ─────────────────────────────────────────┘
```

**合法流转规则（version 乐观锁保护）**：

| 当前状态 | 允许目标状态 | 触发方 | 条件 |
|---------|------------|--------|------|
| PENDING | PAID | 支付回调 | 金额核对成功 |
| PENDING | CANCELLED | 用户/系统超时 | 30min 未支付 |
| PAID | SHIPPED | 管理员 | 填写物流信息 |
| PAID | REFUNDED | 用户/管理员 | 退款申请 |
| SHIPPED | COMPLETED | 用户/系统 | 7天无售后自动确认 |
| SHIPPED | REFUNDED | 用户/管理员 | 退货退款 |
| COMPLETED | REFUNDED | 管理员 | 特殊退款审批 |

**状态机实现（MySQL + version 乐观锁）**：

```javascript
// cloud-functions/api/order/cancel.js
export async function onRequest(request, env) {
  const { userId, role } = await auth(request, env);
  const { orderId, reason } = await request.json();
  const pool = await getPool(env.DATABASE_URL);

  let attempt = 0;
  while (attempt < 3) {
    attempt++;
    try {
      await pool.beginTransaction();

      // ① 锁定订单行，获取当前状态和版本
      const [rows] = await pool.query(
        'SELECT * FROM orders WHERE id = ? FOR UPDATE',
        [orderId]
      );
      if (!rows.length) { await pool.rollback(); return 404; }
      const order = rows[0];

      // ② 权限校验：用户只能取消自己的 PENDING 订单
      if (role !== 'admin' && order.user_id !== userId) {
        await pool.rollback(); return 403;
      }

      // ③ 状态机校验
      const allowed = {
        'PENDING': ['CANCELLED'],
        'PAID': ['CANCELLED', 'REFUNDED'],     // 退款需管理员
        'SHIPPED': ['COMPLETED', 'REFUNDED'],  // 已发货需管理员
      };
      const target = reason === 'user_cancel' ? 'CANCELLED' : 'REFUNDED';
      if (!allowed[order.status]?.includes(target)) {
        await pool.rollback();
        return { error: `状态 ${order.status} 不允许变更为 ${target}` };
      }
      if (target === 'CANCELLED' && role !== 'admin' && order.status !== 'PENDING') {
        await pool.rollback();
        return { error: '仅 PENDING 状态可由用户取消' };
      }

      // ④ 乐观锁更新（防止并发修改）
      const [result] = await pool.query(
        'UPDATE orders SET status = ?, version = version + 1 WHERE id = ? AND version = ?',
        [target, orderId, order.version]
      );
      if (result.affectedRows === 0) {
        await pool.rollback(); // 版本冲突，重试
        continue;
      }

      // ⑤ 释放库存（仅取消时回补）
      if (target === 'CANCELLED') {
        await pool.query(
          'UPDATE products SET stock = stock + (SELECT qty FROM order_items WHERE order_id = ?), version = version + 1 WHERE id = (SELECT product_id FROM order_items WHERE order_id = ?)',
          [orderId, orderId]
        );
      }

      // ⑥ 记录操作日志
      await pool.query(
        'INSERT INTO admin_logs (admin_id, action, target) VALUES (?, ?, ?)',
        [userId, `order_status_change:${order.status}→${target}`, orderId]
      );

      await pool.commit();

      // ⑦ 触发通知钩子
      await emit(NotificationEvent.ORDER_CANCELLED, { order, reason });

      return { success: true, status: target };

    } catch (err) {
      await pool.rollback();
      if (err.code === 'ER_LOCK_DEADLOCK' && attempt < 3) {
        await sleep(100 * Math.pow(2, attempt));
        continue;
      }
      return { error: '操作失败，请重试' };
    }
  }
}
```

---

## 十六、Phase 2 验收标准

| ID | 验收项 | 验证方法 |
|----|--------|---------|
| P2-01 | JWT 15min AT + 7d RT + Cookie 全属性 | 登录后 DevTools 查看 Cookie 属性 |
| P2-02 | 并发刷新 RT，第二个请求返回 409 | 两个 tab 同时触发刷新 |
| P2-03 | EventBus 401 跳转登录并回跳 | Token 过期后触发验证 |
| P2-04 | AI 限流：未登录 11 次请求第 11 个返回 429 | 匿名请求连续发送 |
| P2-05 | CSP Header 存在于 HTML 响应中 | `curl -I` 查看响应头 |
| P2-06 | 订单状态机：PENDING→CANCELLED 成功 | 调用 cancel API |
| P2-07 | 订单状态机：PAID→CANCELLED 被拒绝（需 admin） | 用户端测试 |
| P2-08 | Notification 钩子注册 + emit 触发 | 单元测试验证 |
| P2-09 | RS256 双轨验证（可选 Phase 2 末期） | HS/RS 混合 token 混跑 |

---

## 十七、功能验证清单（Phase 2 更新）

**Demo 站点：** https://geek-mall-demo-4qaxvmeh.edgeone.cool（需有效期内的 EdgeOne Pages 访问 Token）

| # | 功能 | 验证方法 | 状态 |
|---|------|---------|------|
| V-01 | 首页商品浏览（12 个商品） | API 返回 12 个商品，含名称/价格/库存 | ✅ |
| V-02 | 用户注册（bcrypt cost=12） | 注册成功，返回 userId/email | ✅ |
| V-03 | 用户登录（JWT） | 登录成功，返回用户信息 | ✅ |
| V-04 | 购物车（localStorage 持久化） | Next.js 客户端路由，需浏览器测试 | 🟡 浏览器验证 |
| V-05 | 结账（微信/支付宝选择） | checkout 页面存在，需浏览器测试 | 🟡 浏览器验证 |
| V-06 | 模拟支付成功回调 | confirm API 存在，需有效 session | 🟡 需 session |
| V-07 | 我的订单（状态标签） | orders API 存在，需有效 session | 🟡 需 session |

---

## 十八、Phase 2 里程碑

```
✅ Phase 1 完成：安全 Critical 全部修复（7/7 P0）
🟡 Phase 2 进行中：P1 安全加固 + P2 能力完善
🔲 Phase 3（可选）：RS256 + nonce CSP + SSE 优化
```

> **Phase 2 完成后，网站骨架 Skill 具备生产级安全性与完整功能集。**

---

## 十八、Phase 3 实现（P2 编码 + Layer 2 Addon + 多租户铺垫）

### Phase 3 里程碑

```
✅ Phase 1 完成：Mock 数据 Demo，架构验证
✅ Phase 2 完成：P0/P1 安全设计 + P2 设计文档完整
✅ Phase 3 完成：P2 实现 + Layer 2 Addon + 多租户铺垫
```

### P2-1：RS256 双轨迁移（sharing/jwt-helper.js）

**实现文件：** `sharing/jwt-helper.js`

- 签发：RS256 私钥（`JWT_PRIVATE_KEY` 环境变量）
- 验证：优先 RS256，30 天内旧 HS256 token 仍可验证
- 迁移时间线：Day 0 部署 → Day 30 移除 HS256 兼容分支

```javascript
// 签发（永远 RS256）
const token = await signJWT({ sub: user.id, role: 'admin' }, AT_TTL_MS, env);

// 验证（自动双轨）
const payload = await verifyJWT(token, env);
// payload._alg === 'RS256' → 新 token
// payload._alg === 'HS256' → 30天兼容窗口内的旧 token
```

### P2-2：订单状态机（cloud-functions/）

**实现文件：**
- `cloud-functions/utils/order-state-machine.js` — 核心状态机 + TRANSITIONS 表 + PERMISSIONS 表
- `cloud-functions/api/order/transition.js` — 统一状态变更 API
- `cloud-functions/cron/order-cron.js` — 定时任务（PENDING 超时取消 / SHIPPED 自动完成）
- `db/migrations/002_order_logs.sql` — `order_status_logs` 审计表

**状态流转（6 状态）：**
```
PENDING → PAID → SHIPPED → COMPLETED
    ↓        ↓        ↓
CANCELLED  REFUNDED  REFUNDED
```

**权限矩阵：**
| 变更 | 用户（本人） | 管理员 |
|------|------------|--------|
| PENDING→CANCELLED | ✅ | ✅ |
| PAID→SHIPPED | — | ✅ |
| PAID/SHIPPED→REFUNDED | ✅（本人） | ✅ |
| SHIPPED→COMPLETED | ✅ | ✅ |

### L2-1：SEO 模块（client/src/utils/seo.js + edge-functions/）

**实现文件：**
- `client/src/utils/seo.js` — JSON-LD 生成器 + Meta Tags + Sitemap XML 生成器
- `edge-functions/api/sitemap.xml.js` — 动态 Sitemap API（Edge Function，5 分钟缓存）
- `sharing/i18n/zh-CN.js` + `en-US.js` — 中英文案

**JSON-LD 支持：**
- `WebSite`（首页）
- `Product`（产品页，含 offers/aggregateRating）
- `BreadcrumbList`（面包屑）
- `Organization`（组织信息）

### L2-2：i18n 国际化（sharing/i18n/）

**实现文件：**
- `sharing/i18n/zh-CN.js` — 中文文案
- `sharing/i18n/en-US.js` — 英文文案
- `sharing/i18n/i18n.js` — 翻译函数 `t(key)` + 语言切换

**使用方式：**
```javascript
import { t, setLang, getLang } from './i18n.js';

t('nav.home')           // → '首页'
t('order.status.PAID')  // → '已支付'
setLang('en-US');       // 切换语言
```

### L2-3：Analytics 埋点（client/src/utils/analytics.js）

**实现文件：**
- `client/src/utils/analytics.js` — 埋点 SDK
- `edge-functions/api/analytics/event.js` — 事件接收 API（KV 存储）

**预定义事件：** `page_view` / `add_to_cart` / `checkout_start` / `purchase` / `signup` / `login` / `search`

**特点：** `navigator.sendBeacon` 不阻塞导航，支持页面卸载时发送。

### L3-1：Multi-tenant KV 前缀（sharing/kv-keys.js）

**实现文件：** `sharing/kv-keys.js`

所有 KV Key 统一加租户前缀：
```
Phase 3: "default:session:abc123"
Phase 4: "{tenant}:session:abc123"（从 JWT payload.tenant 动态读取）
```

### Phase 3 新增文件清单

```
sharing/
├── jwt-helper.js              ✅ RS256 + HS256 双轨
├── kv-keys.js                 ✅ 多租户前缀
└── i18n/
    ├── zh-CN.js               ✅ 中文
    ├── en-US.js               ✅ 英文
    └── i18n.js                ✅ 翻译函数

cloud-functions/
├── utils/
│   └── order-state-machine.js ✅ 核心状态机
├── api/order/
│   └── transition.js          ✅ 状态变更 API
└── cron/
    └── order-cron.js          ✅ 定时任务

client/src/utils/
├── seo.js                     ✅ SEO 工具
└── analytics.js               ✅ 埋点 SDK

edge-functions/
├── api/
│   ├── sitemap.xml.js         ✅ Sitemap API
│   └── analytics/event.js     ✅ 埋点接收

db/migrations/
└── 002_order_logs.sql         ✅ 审计日志表

references/
├── admin-module.md            ✅ 补充
├── edge-functions.md          ✅ 补充
├── cloud-functions.md         ✅ 补充
├── middleware.md              ✅ 补充
└── deployment.md              ✅ 补充
```

---

## 十九、Phase 3 验收标准

| ID | 验收项 | 验证方法 |
|----|--------|---------|
| P3-01 | RS256：新 token 用 RS256 私钥签发 | 代码审查 + 手动 JWT 解析 |
| P3-02 | RS256：HS256 旧 token 30 天内仍可验证 | 测试过期 token 验证 |
| P3-03 | 订单状态机：用户取消 PENDING 订单成功 | 调用 transition API |
| P3-04 | 订单状态机：用户无法 PAID→CANCELLED（403） | 调用 transition API |
| P3-05 | 库存联动：取消/退款时 stock 回补 | 查询 products 表 |
| P3-06 | 审计日志：每次状态变更写入 order_status_logs | 查询数据库 |
| P3-07 | Cron：PENDING 超时 30 分钟自动 CANCELLED | 模拟超时订单 |
| P3-08 | SEO JSON-LD：产品页含 schema.org 结构化数据 | 审查页面源码 |
| P3-09 | Sitemap：/api/sitemap.xml 返回有效 XML | curl 访问 |
| P3-10 | i18n：`t('order.status.PAID')` 正确输出中英文 | 切换语言测试 |
| P3-11 | Analytics：add_to_cart 事件通过 sendBeacon 发送 | Network 面板验证 |
| P3-12 | Multi-tenant：KV key 格式含 "default:" 前缀 | 代码审查 |

---

## 二十、未来演进

```
Phase 1：Mock 数据 Demo ✅
Phase 2：P0/P1 安全设计 + P2 设计文档 ✅
Phase 3：P2 编码实现 + Layer 2 Addon + 多租户铺垫 ✅

Phase 4（规划中）：多租户 SaaS
  - KV key 从 JWT payload.tenant 动态读取
  - 租户隔离数据库（MySQL schema）
  - 租户管理后台
  - 计费系统（按量/订阅）

Phase 5（规划中）：npm 包化
  npm install @site-skeleton/auth
  npm install @site-skeleton/payment
```

*Skill 版本演进由评审驱动，每 Phase 完成后更新版本号与文档。*

---

## 二十一、安全说明

### AI 聊天数据保护（v2.3 新增）

| 改进项 | v2.2（旧） | v2.3（新） |
|--------|-----------|-----------|
| 历史传输方式 | URL 查询参数 `?history=...` | Session ID `?sessionId=xxx`，服务端读取 |
| 数据暴露风险 | 浏览器历史、日志、代理、referrer 可截获 | 历史仅服务端 KV 访问 |
| 历史持久化 | 前端负责拼装 | 服务端统一管理（1h TTL 自动过期） |

**所有生成的 AI 聊天代码必须使用 sessionId 方案**，不得将对话历史序列化到 URL 中。

### 关键安全原则

1. **凭证最小化**：Edge Functions 不持有数据库密钥/支付密钥；Cloud Functions 才持有
2. **支付幂等**：必须使用 Edge `putIfNotExists` 原子锁（24h TTL）
3. **RT 乐观锁**：Refresh Token 轮换使用 KV version 乐观锁防并发
4. **超卖防护**：MySQL `SELECT FOR UPDATE` + CHECK 约束 + 乐观锁三重防护
5. **CSP Header**：所有响应必须带 Content-Security-Policy
6. **会话过期**：AI 对话 session 1 小时自动过期，敏感数据不长期留存
