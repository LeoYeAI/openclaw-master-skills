# 订单状态机参考文档

> **版本：** v2.2 · **Phase：** P2（可选）
> **职责：** 规范化订单状态流转，防止非法状态变迁导致数据不一致

---

## 1. 状态定义

| 状态 | 值（DB 存储） | 说明 |
|------|-------------|------|
| 待支付 | `PENDING` | 订单创建，等待用户支付 |
| 已支付 | `PAID` | 支付成功，等待发货 |
| 已发货 | `SHIPPED` | 管理员填写物流信息 |
| 已完成 | `COMPLETED` | 用户确认收货或 7 天无售后自动 |
| 已取消 | `CANCELLED` | 用户取消或超时未支付 |
| 已退款 | `REFUNDED` | 用户/管理员发起退款 |

---

## 2. 完整状态流转图

```
┌──────────┐ pay      ┌───────┐ ship     ┌──────────┐ confirm  ┌───────────┐
│ PENDING  │ ───────→ │ PAID  │ ───────→ │ SHIPPED  │ ───────→ │ COMPLETED │
└──────────┘          └───────┘          └──────────┘          └───────────┘
     │                      │                                        │
     │ cancel(user)         │ refund(user/admin)                     │ refund(admin)
     ↓                      ↓                                        ↓
┌──────────┐          ┌──────────┐                              ┌──────────┐
│ CANCELLED│          │ REFUNDED │                              │ REFUNDED │
└──────────┘          └──────────┘                              └──────────┘

超时未支付(30min) → CANCELLED（系统自动触发）
```

---

## 3. 权限规则矩阵

| 目标状态 | 用户（本人订单） | 管理员 |
|---------|----------------|--------|
| CANCELLED | PENDING 时可取消 | 任意阶段可取消 |
| SHIPPED | — | 仅 PAID 时可操作 |
| COMPLETED | SHIPPED 时可确认 | 任意阶段可操作 |
| REFUNDED | PAID/SHIPPED 时可申请 | 任意阶段可退款 |

---

## 4. 各目标状态的触发条件

### 4.1 PENDING → CANCELLED

**触发方**：用户（取消）或系统（超时）

```javascript
// 条件
if (order.status === 'PENDING') {
  // 用户取消：本人订单，任意时间
  // 系统超时：created_at 超过 30 分钟未支付
}
```

### 4.2 PENDING → PAID

**触发方**：支付回调

```javascript
// 条件
if (order.status === 'PENDING' && verifyAmount(order, callback)) {
  // 金额核对一致
}
```

### 4.3 PAID → SHIPPED

**触发方**：管理员（填写物流信息）

```javascript
// 条件
if (order.status === 'PAID' && req.body.express_company && req.body.express_no) {
  // 需管理员权限
  // 需填写快递公司和运单号
}
```

### 4.4 SHIPPED → COMPLETED

**触发方**：用户确认 / 系统自动

```javascript
// 条件
if (order.status === 'SHIPPED') {
  // 用户点击"确认收货"
  // 或：paid_at + 7天 < now（无售后自动完成，需定时任务）
}
```

### 4.5 PAID/SHIPPED/COMPLETED → REFUNDED

**触发方**：用户（PAID）/ 管理员（任意阶段）

```javascript
// 条件
if (canRefund(order.status, role, userId)) {
  // PAID 阶段：用户可直接申请退款
  // SHIPPED 阶段：需先退货
  // COMPLETED 阶段：仅管理员可退款（需审批流程）
}
```

---

## 5. 状态机核心实现

```javascript
// cloud-functions/utils/order-state-machine.js

export const OrderStatus = {
  PENDING:   'PENDING',
  PAID:      'PAID',
  SHIPPED:   'SHIPPED',
  COMPLETED: 'COMPLETED',
  CANCELLED: 'CANCELLED',
  REFUNDED:  'REFUNDED',
};

// 状态流转规则表：currentStatus → [allowedNextStatuses]
const TRANSITIONS = {
  [OrderStatus.PENDING]:   [OrderStatus.PAID, OrderStatus.CANCELLED],
  [OrderStatus.PAID]:      [OrderStatus.SHIPPED, OrderStatus.REFUNDED],
  [OrderStatus.SHIPPED]:    [OrderStatus.COMPLETED, OrderStatus.REFUNDED],
  [OrderStatus.COMPLETED]: [OrderStatus.REFUNDED],
  [OrderStatus.CANCELLED]: [],  // 终态
  [OrderStatus.REFUNDED]:   [],  // 终态
};

// 权限校验：哪些角色可以触发哪些状态变更
const PERMISSIONS = {
  'PENDING→CANCELLED': ['user:own', 'admin'],
  'PAID→SHIPPED':       ['admin'],
  'PAID→REFUNDED':      ['user:own', 'admin'],
  'SHIPPED→COMPLETED':  ['user:own', 'admin'],
  'SHIPPED→REFUNDED':   ['user:own', 'admin'],
  'COMPLETED→REFUNDED': ['admin'],
};

export function canTransition(from, to, { role, userId, orderUserId }) {
  const allowed = TRANSITIONS[from];
  if (!allowed || !allowed.includes(to)) {
    throw new StateMachineError(`禁止的状态变更：${from} → ${to}`);
  }

  const permKey = `${from}→${to}`;
  const required = PERMISSIONS[permKey];
  if (!required) throw new StateMachineError(`未定义权限：${permKey}`);

  const isOwn = userId === orderUserId;
  const roleTag = role === 'admin' ? 'admin' : (isOwn ? 'user:own' : 'user:other');

  if (!required.includes(roleTag)) {
    throw new StateMachineError(`权限不足：需要 ${required.join('/')}，当前 ${roleTag}`);
  }

  return true;
}

export class StateMachineError extends Error {
  constructor(message) {
    super(message);
    this.name = 'StateMachineError';
  }
}
```

---

## 6. 与库存联动

取消订单（CANCELLED）和退款（REFUNDED）需要回补库存：

```javascript
// 取消/退款时回补库存
async function releaseStock(pool, orderId) {
  await pool.query(`
    UPDATE products p
    JOIN order_items oi ON p.id = oi.product_id
    SET p.stock = p.stock + oi.qty,
        p.version = p.version + 1
    WHERE oi.order_id = ?
  `, [orderId]);
}
```

---

## 7. 定时任务（Cron）

```javascript
// cloud-functions/cron/order-cron.js
// 部署为定时触发的 Cloud Function

export async function scheduledHandler(env) {
  const pool = await getPool(env.DATABASE_URL);

  // 任务1：超时未支付自动取消（PENDING > 30min）
  await pool.query(`
    UPDATE orders SET status = 'CANCELLED', version = version + 1
    WHERE status = 'PENDING'
      AND created_at < DATE_SUB(NOW(), INTERVAL 30 MINUTE)
  `);

  // 任务2：已发货 7 天无售后自动完成
  await pool.query(`
    UPDATE orders SET status = 'COMPLETED', version = version + 1
    WHERE status = 'SHIPPED'
      AND paid_at < DATE_SUB(NOW(), INTERVAL 7 DAY)
  `);
}
```

---

## 8. 订单日志（审计追踪）

```sql
CREATE TABLE order_status_logs (
  id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_id   BIGINT UNSIGNED NOT NULL,
  from_status VARCHAR(32),
  to_status  VARCHAR(32) NOT NULL,
  operator   BIGINT UNSIGNED,
  reason     VARCHAR(255),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

> **Phase 1 状态机**：仅基础流转，无 version 乐观锁，无定时任务
> **Phase 2 状态机**：完整权限矩阵 + version 乐观锁 + 库存联动 + 审计日志
