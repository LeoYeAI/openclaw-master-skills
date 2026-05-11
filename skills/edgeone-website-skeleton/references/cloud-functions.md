# Cloud Functions 参考文档

> **版本：** v2.2 · **Phase：** Layer 0（Core）
> **职责：** 含密钥操作、MySQL 事务、支付 SDK、AI SSE、bcrypt 哈希

---

## 一、Cloud Functions 概述

Cloud Functions 运行在 **Node.js 环境**，可以：
- 访问 MySQL（主数据库）
- 使用密钥（bcrypt、支付 SDK）
- 执行长时间任务（SSE 流）
- 发起外部 HTTP 请求

### 目录结构

```
cloud-functions/
├── api/
│   ├── auth/
│   │   └── register.js          # bcrypt 注册
│   ├── pay/
│   │   ├── create-order.js      # 微信/支付宝预下单
│   │   ├── wx-notify.js        # 微信回调
│   │   └── ali-notify.js        # 支付宝回调
│   ├── order/
│   │   ├── create.js           # SELECT FOR UPDATE 创建订单
│   │   └── transition.js        # 状态机变更
│   ├── admin/
│   │   ├── products.js         # 商品 CRUD
│   │   ├── orders.js           # 订单查询
│   │   └── stats.js            # 运营统计
│   └── ai/
│       └── chat-stream.js       # SSE 流式响应
├── utils/
│   ├── db.js                    # MySQL 连接池
│   ├── payment-sdk.js           # 微信/支付宝 SDK 封装
│   ├── admin-guard.js          # 权限校验
│   └── notification-hooks.js   # 通知钩子
└── cron/
    └── order-cron.js            # 定时任务
```

> ⚠️ **目录名必须是 `cloud-functions/`，EdgeOne Pages 平台硬性要求。

---

## 二、函数签名

EdgeOne Pages Cloud Functions 的导出格式：

```javascript
// Node.js
export async function onRequest(request, env) {
  // request: Request 对象
  // env: 环境变量
  return new Response('...', { status: 200 });
}
```

### 接收请求参数

```javascript
// GET 请求
export async function onRequest(request, env) {
  const url = new URL(request.url);
  const id = url.searchParams.get('id');
}

// POST 请求
export async function onRequest(request, env) {
  const body = await request.json();
  // 或
  const body = await request.formData();
}
```

---

## 三、MySQL 连接池

```javascript
// cloud-functions/utils/db.js

import { Pool } from 'mysql2/promise';

let pool = null;

export async function getPool(connectionString) {
  if (!pool) {
    pool = new Pool({
      connectionString,
      waitForConnections: true,
      connectionLimit: 10,
      queueLimit: 0,
      enableKeepAlive: true,
      keepAliveInitialDelay: 0
    });
  }
  return pool;
}

// Cloud Function 中使用
export async function onRequest(request, env) {
  const pool = await getPool(env.DATABASE_URL);
  try {
    const [rows] = await pool.query('SELECT * FROM users WHERE id = ?', [userId]);
    return new Response(JSON.stringify(rows[0]));
  } finally {
    // Cloud Functions 不需要手动关闭池
  }
}
```

### 事务示例

```javascript
export async function withTransaction(pool, fn) {
  const conn = await pool.getConnection();
  try {
    await conn.beginTransaction();
    const result = await fn(conn);
    await conn.commit();
    return result;
  } catch (err) {
    await conn.rollback();
    throw err;
  } finally {
    conn.release();
  }
}
```

---

## 四、bcrypt 密码哈希

```javascript
// cloud-functions/api/auth/register.js
import bcrypt from 'bcryptjs';

const BCRYPT_ROUNDS = 12;

export async function onRequest(request, env) {
  const { email, password, name } = await request.json();

  if (!email || !password || password.length < 8) {
    return new Response(JSON.stringify({ error: 'Invalid input' }), { status: 400 });
  }

  const pool = await getPool(env.DATABASE_URL);
  const [existing] = await pool.query('SELECT id FROM users WHERE email = ?', [email]);
  if (existing.length > 0) {
    return new Response(JSON.stringify({ error: '邮箱已被注册' }), { status: 409 });
  }

  const passwordHash = await bcrypt.hash(password, BCRYPT_ROUNDS);

  const [result] = await pool.query(
    'INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)',
    [email, passwordHash, name || '']
  );

  return new Response(JSON.stringify({
    userId: result.insertId,
    email
  }), { status: 201, headers: { 'Content-Type': 'application/json' } });
}
```

---

## 五、微信支付 SDK 封装

```javascript
// cloud-functions/utils/payment-sdk.js

/**
 * 微信支付 V3 — 统一下单
 */
export async function wxPayCreateOrder(env, { outTradeNo, amount, description, notifyUrl }) {
  const url = 'https://api.mch.weixin.qq.com/v3/pay/transactions/native';

  const payload = {
    appid: env.WX_APPID,
    mchid: env.WX_MCHID,
    description,
    out_trade_no: outTradeNo,
    notify_url: notifyUrl,
    amount: { total: amount, currency: 'CNY' }
  };

  const token = await getWxAuthToken(env);
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `WECHATPAY2-SHA256-RSA2048 ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Wechat pay error: ${err}`);
  }

  const data = await response.json();
  return { codeUrl: data.code_url, tradeNo: data.id };
}
```

---

## 六、AI SSE 流式响应

```javascript
// cloud-functions/api/ai/chat-stream.js

export async function onRequest(request, env) {
  const url = new URL(request.url);
  const historyParam = url.searchParams.get('history');
  const history = historyParam ? JSON.parse(decodeURIComponent(historyParam)) : [];

  const stream = new ReadableStream({
    async start(controller) {
      const encoder = new TextEncoder();

      const sendEvent = (event, data) => {
        controller.enqueue(encoder.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`));
      };

      try {
        const messages = [
          ...history.map(h => ({ role: h.role, content: h.content })),
        ];

        const aiResponse = await fetch('https://api.example.com/chat', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${env.AI_API_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ messages, stream: true })
        });

        const reader = aiResponse.body.getReader();
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const text = new TextDecoder().decode(value);
          sendEvent('message', { content: text });
        }

        sendEvent('done', {});
      } catch (err) {
        sendEvent('error', { message: err.message });
      } finally {
        controller.close();
      }
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    }
  });
}
```

---

## 七、环境变量（Cloud Functions）

| 变量 | 必填 | 说明 |
|------|------|------|
| `DATABASE_URL` | ✅ | MySQL 连接串 |
| `WX_APPID` | ✅（电商） | 微信 AppID |
| `WX_MCHID` | ✅（电商） | 微信商户号 |
| `WX_API_KEY` | ✅（电商） | 微信 APIv3 密钥 |
| `WX_CERT_PATH` | ✅（电商） | 微信证书路径 |
| `ALI_APP_ID` | ✅（电商） | 支付宝 AppID |
| `ALI_PRIVATE_KEY` | ✅（电商） | 支付宝私钥 |
| `AI_API_KEY` | ✅（AI 栈） | AI 模型 API Key |
| `EDGE_BASE` | ✅（电商） | Edge Function 内部网关 |
| `ADMIN_EMAIL` | 可选 | 管理员通知邮箱 |
