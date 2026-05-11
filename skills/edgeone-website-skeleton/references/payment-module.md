# Payment 模块参考文档

## 一、支付架构

```
用户下单 → Cloud: 创建订单（SELECT FOR UPDATE） → 生成 out_trade_no
       → 微信/支付宝统一下单 API → 返回支付二维码/链接
       → 用户扫码支付
       → 支付平台回调 → Cloud: wx-notify/ali-notify
                              → Edge: 幂等锁 putIfNotExists
                              → Cloud: 业务处理
                              → 返回 SUCCESS
```

## 二、金额安全规则

```javascript
// 核心原则：金额永远从服务端 MySQL 读取，前端只传 productId + qty

// ❌ 危险：从前端接收金额
{ productId: "p001", qty: 1, price: 99.9 }  // 前端可控！

// ✅ 安全：Cloud Function 查 MySQL 获取价格
const [rows] = await pool.query(
  'SELECT price FROM products WHERE id = ? AND status = "active"',
  [productId]
);
const total = rows[0].price * quantity;  // 服务端计算，不可篡改
```

## 三、幂等原子锁（Edge + Cloud 协作）

```javascript
// Edge Function：cloud-functions/internal/idempotency.js
// Edge 是唯一能访问 KV 的运行时
export async function onRequest(context) {
  const { KV } = context.env;
  const { out_trade_no, callback_id } = await context.request.json();
  const acquired = await KV.putIfNotExists(
    `pay:idempotency:${out_trade_no}`,
    callback_id,           // 微信 transaction_id，作为幂等证据
    { expirationTtl: 86400 }
  );
  return new Response(JSON.stringify({ acquired }), { status: 200 });
}

// Cloud Function：cloud-functions/api/pay/wx-notify.js
export async function onRequest(request, env) {
  const rawBody = await request.text();
  if (!await verifyWechatSignature(rawBody, env.WX_MCH_SECRET))
    return new Response('FAIL', { status: 401 });

  const { out_trade_no, transaction_id, trade_state } = JSON.parse(rawBody);

  const { acquired } = await fetch(`${env.EDGE_BASE}/api/internal/idempotency`, {
    method: 'POST',
    body: JSON.stringify({ out_trade_no, callback_id: transaction_id })
  }).then(r => r.json());

  if (!acquired) return new Response('SUCCESS');  // 已处理过，幂等跳过

  if (trade_state === 'SUCCESS') await processPayment(out_trade_no, transaction_id, env);
  return new Response('SUCCESS');
}
```

## 四、微信支付 V3 签名验证

```javascript
// cloud-functions/utils/payment-sdk.js
import { createHmac } from 'crypto';

export async function verifyWechatSignature(rawBody, mchSecret) {
  const body = JSON.parse(rawBody);
  const signature = request.headers.get('wechatpay-signature');
  const timestamp = request.headers.get('wechatpay-timestamp');
  const nonce = request.headers.get('wechatpay-nonce');

  const message = `${timestamp}\n${nonce}\n${rawBody}\n`;
  const expectSign = createHmac('sha256', mchSecret).update(message).digest('base64');

  return signature === expectSign;
}
```

## 五、支付状态机

```
PENDING（待支付）
  ↓ 支付成功回调（幂等）
PAID（已支付，待发货）
  ↓ 管理员发货
SHIPPED（已发货）
  ↓ 确认收货/签收
COMPLETED（已完成）
  ↓ 超时/用户取消
CANCELLED（已取消）
  ↓
REFUNDED（已退款）
```

## 六、限流配置

```javascript
// /api/pay/create-order
const { allowed } = await rateLimit(request, `pay:${userId}`, 10, 60);
// 10 次/分钟/用户，超限返回 429
```
