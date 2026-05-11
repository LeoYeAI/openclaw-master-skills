# Notification 模块参考文档

> **版本：** v2.2 · **Phase：** Layer 2 Addon（Phase 2 实现）
> **职责：** 统一事件驱动的通知发送（邮件/微信/钉钉/SMS）

---

## 1. 架构设计

```
业务事件发生
    ↓
emit(event, payload)  ← 业务代码调用
    ↓
钩子注册表查找（registerHandler）
    ↓
并行触发所有已注册处理器
    ↓
各通道适配器独立执行（失败不阻塞其他通道）
```

**设计原则**：
- 事件驱动：业务代码只调用 `emit()`，不直接写通知逻辑
- 通道解耦：每种通知方式独立适配器，插拔式
- 优雅降级：某个通道失败不影响其他通道
- 异步执行：通知不阻塞主业务流程

---

## 2. 事件类型

```javascript
export const NotificationEvent = {
  // 订单事件
  ORDER_CREATED:    'order.created',    // 订单创建
  ORDER_PAID:        'order.paid',      // 支付成功
  ORDER_SHIPPED:     'order.shipped',   // 已发货
  ORDER_DELIVERED:   'order.delivered', // 已签收
  ORDER_CANCELLED:   'order.cancelled', // 已取消
  ORDER_REFUNDED:    'order.refunded',  // 已退款
  ORDER_COMPLETED:   'order.completed', // 已完成

  // 用户事件
  USER_REGISTERED:  'user.registered', // 注册成功
  PASSWORD_CHANGED: 'password.changed', // 密码修改
  EMAIL_VERIFIED:   'email.verified',  // 邮箱验证
};
```

---

## 3. 通道适配器

### 3.1 邮件适配器（需 SMTP 配置）

**环境变量**：
```
NOTIFICATION_SMTP_HOST=smtp.example.com
NOTIFICATION_SMTP_PORT=587
NOTIFICATION_SMTP_USER=noreply@example.com
NOTIFICATION_SMTP_PASS=xxxx
NOTIFICATION_FROM_EMAIL=noreply@example.com
NOTIFICATION_FROM_NAME=网站名称
```

**适配器实现**：

```javascript
// cloud-functions/utils/notification/channels/email.js
import nodemailer from 'nodemailer';

let transporter = null;

function getTransporter(env) {
  if (!transporter) {
    transporter = nodemailer.createTransport({
      host: env.NOTIFICATION_SMTP_HOST,
      port: parseInt(env.NOTIFICATION_SMTP_PORT || '587'),
      secure: env.NOTIFICATION_SMTP_PORT === '465',
      auth: {
        user: env.NOTIFICATION_SMTP_USER,
        pass: env.NOTIFICATION_SMTP_PASS,
      },
    });
  }
  return transporter;
}

export async function sendEmail(env, { to, subject, html }) {
  if (!env.NOTIFICATION_SMTP_HOST) {
    console.log('[Email] SMTP not configured, skipping');
    return;
  }
  try {
    await getTransporter(env).sendMail({
      from: `"${env.NOTIFICATION_FROM_NAME}" <${env.NOTIFICATION_FROM_EMAIL}>`,
      to,
      subject,
      html,
    });
    console.log(`[Email] Sent to ${to}: ${subject}`);
  } catch (err) {
    console.error(`[Email] Failed to send to ${to}:`, err.message);
    throw err; // 让 emit() 捕获但不阻塞其他通道
  }
}
```

### 3.2 微信模板消息（需微信公众号配置）

**环境变量**：
```
WX_APPID=wx1234567890
WX_TEMPLATE_ID_ORDER=xxxxx
WX_TEMPLATE_ID_SHIP=xxxxx
```

**适配器实现**：

```javascript
// cloud-functions/utils/notification/channels/wechat.js
// 需要微信公众号的 Access Token（需定期刷新）

async function getAccessToken(env) {
  const cacheKey = 'wx:access_token';
  const cached = await KV.get(cacheKey);
  if (cached) return cached;

  const res = await fetch(
    `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${env.WX_APPID}&secret=${env.WX_APP_SECRET}`
  );
  const data = await res.json();
  await KV.put(cacheKey, data.access_token, { expirationTtl: 7000 }); // 提前 3 分钟过期
  return data.access_token;
}

export async function sendWechatTemplate(env, { openid, templateId, data }) {
  if (!env.WX_APPID || !templateId) return;
  const token = await getAccessToken(env);
  await fetch(`https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=${token}`, {
    method: 'POST',
    body: JSON.stringify({
      touser: openid,
      template_id: templateId,
      data,
    }),
  });
}
```

### 3.3 钉钉 Webhook

```javascript
// cloud-functions/utils/notification/channels/dingtalk.js
export async function sendDingtalk(env, { msgtype = 'text', content, title }) {
  if (!env.DINGTALK_WEBHOOK_URL) return;
  await fetch(env.DINGTALK_WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ msgtype, text: { content }, title }),
  });
}
```

---

## 4. 事件处理器注册

```javascript
// cloud-functions/utils/notification-hooks.js
import { sendEmail } from './channels/email.js';
import { sendWechatTemplate } from './channels/wechat.js';
import { sendDingtalk } from './channels/dingtalk.js';

// 订单支付成功：发邮件 + 发微信模板
registerHandler(NotificationEvent.ORDER_PAID, async ({ order, user, env }) => {
  await Promise.allSettled([
    sendEmail(env, {
      to: user.email,
      subject: `订单 ${order.order_no} 支付成功`,
      html: `<h2>感谢您的购买！</h2><p>订单号：${order.order_no}</p><p>金额：¥${order.total}</p>`,
    }),
    user.openid ? sendWechatTemplate(env, {
      openid: user.openid,
      templateId: env.WX_TEMPLATE_ID_ORDER,
      data: {
        keyword1: { value: order.order_no },
        keyword2: { value: `¥${order.total}` },
        keyword3: { value: '支付成功' },
      },
    }) : Promise.resolve(),
  ]);
});

// 订单发货：发邮件
registerHandler(NotificationEvent.ORDER_SHIPPED, async ({ order, user, env }) => {
  await sendEmail(env, {
    to: user.email,
    subject: `订单 ${order.order_no} 已发货`,
    html: `<p>快递公司：${order.express_company}</p><p>运单号：${order.express_no}</p>`,
  });
  // 管理员通知（钉钉群）
  await sendDingtalk(env, {
    content: `📦 订单 ${order.order_no} 已发货，请关注`,
  });
});
```

---

## 5. 业务调用示例

```javascript
// cloud-functions/api/pay/wx-notify.js
import { emit, NotificationEvent } from '../../utils/notification-hooks.js';

export async function onRequest(request, env) {
  const { out_trade_no, transaction_id, trade_state } = await parseCallback(request);

  if (trade_state === 'SUCCESS') {
    const order = await updateOrderToPaid(out_trade_no, transaction_id, env);
    const user = await getUserByOrder(order.user_id, env);

    // 异步发送通知（不阻塞回调响应）
    emit(NotificationEvent.ORDER_PAID, { order, user, env });
  }

  return new Response('SUCCESS');
}
```

---

## 6. Phase 1 vs Phase 2 区别

| 项目 | Phase 1 | Phase 2 |
|------|---------|---------|
| 钩子结构 | 空壳（仅框架） | 邮件/微信/钉钉适配器 |
| 事件类型 | 2 个 | 11 个 |
| 调用方式 | 预留接口 | 完整实现 |
| 配置 | 无 | env-vars 注入 |
