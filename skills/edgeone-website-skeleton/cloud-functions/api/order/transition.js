/**
 * 订单状态变更 API — 统一入口
 *
 * Phase 3 P2-2 实现
 *
 * POST /api/order/transition
 * Body: {
 *   orderId: number,
 *   toStatus: string,          // PENDING→PAID 时由系统（支付回调）触发
 *   express_company?: string,   // SHIPPED 必填
 *   express_no?: string,         // SHIPPED 必填
 *   reason?: string              // 取消/退款原因
 * }
 *
 * Auth: Bearer JWT（user 或 admin role）
 */

import { Pool } from 'mysql2/promise';
import { canTransition, StateMachineError, OrderStatus } from '../utils/order-state-machine.js';

// ===================== 依赖文件（需在同级目录或共享） =====================
// 这些函数假设从 ../../../sharing/ 或同级 utils 导入
// import { auth } from '../../../sharing/auth.js'; // 根据实际目录结构调整

// ===================== 库存回补 =====================

/**
 * 取消/退款时回补库存（乐观锁）
 */
async function releaseStock(pool, orderId) {
  const [items] = await pool.query(`
    SELECT oi.product_id, oi.qty, p.version
    FROM order_items oi
    JOIN products p ON p.id = oi.product_id
    WHERE oi.order_id = ?
  `, [orderId]);

  for (const item of items) {
    const [result] = await pool.query(
      'UPDATE products SET stock = stock + ?, version = version + 1 WHERE id = ? AND version = ?',
      [item.qty, item.product_id, item.version]
    );
    if (result.affectedRows === 0) {
      console.warn(`[StateMachine] Stock release conflict for product ${item.product_id}`);
    }
  }
}

// ===================== 审计日志写入 =====================

async function writeStatusLog(pool, orderId, fromStatus, toStatus, operatorId, reason) {
  await pool.query(
    `INSERT INTO order_status_logs (order_id, from_status, to_status, operator, reason)
     VALUES (?, ?, ?, ?, ?)`,
    [orderId, fromStatus, toStatus, operatorId, reason || null]
  );
}

// ===================== 通知钩子触发 =====================

async function notifyStatusChange(pool, orderId, fromStatus, toStatus, operatorId) {
  // 从 Cloud Function 通知钩子模块导入（避免循环依赖）
  // const { onOrderCancelled, onOrderRefunded, onOrderShipped } = await import('../utils/notification-hooks.js');

  const orderMap = {
    [OrderStatus.CANCELLED]: 'onOrderCancelled',
    [OrderStatus.REFUNDED]:  'onOrderRefunded',
    [OrderStatus.SHIPPED]:   'onOrderShipped',
    [OrderStatus.COMPLETED]: 'onOrderCompleted',
  };

  if (orderMap[toStatus]) {
    console.log(`[Notification] Triggering ${orderMap[toStatus]} for order ${orderId}`);
    // 异步触发，不阻塞状态变更
    // await import('../utils/notification-hooks.js').then(m => m[orderMap[toStatus]]({ orderId, fromStatus, toStatus }));
  }
}

// ===================== 主处理函数 =====================

export async function onRequest(request, env) {
  // === 认证 ===
  const authHeader = request.headers.get('Authorization') || '';
  const token = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : null;
  if (!token) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), {
      status: 401, headers: { 'Content-Type': 'application/json' }
    });
  }

  // const payload = await verifyAccessToken(token, env); // JWT 验证
  // 简化：实际从 middleware 或 auth service 获取
  let userId, role;
  try {
    // TODO: 替换为实际 JWT 验证
    // const payload = await verifyJWT(token, env);
    // userId = payload.sub;
    // role = payload.role;
    throw new Error('JWT verification not implemented in this stub');
  } catch {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), {
      status: 401, headers: { 'Content-Type': 'application/json' }
    });
  }

  // === 解析请求 ===
  let body;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON' }), {
      status: 400, headers: { 'Content-Type': 'application/json' }
    });
  }

  const { orderId, toStatus, express_company, express_no, reason } = body;

  if (!orderId || !toStatus) {
    return new Response(JSON.stringify({ error: 'orderId 和 toStatus 为必填项' }), {
      status: 400, headers: { 'Content-Type': 'application/json' }
    });
  }

  // === SHIPPED 状态校验物流信息 ===
  if (toStatus === OrderStatus.SHIPPED) {
    if (!express_company || !express_no) {
      return new Response(JSON.stringify({
        error: '发货需要提供快递公司和运单号'
      }), { status: 400, headers: { 'Content-Type': 'application/json' } });
    }
  }

  // === 获取连接池 ===
  const pool = new Pool({ connectionString: env.DATABASE_URL });

  try {
    // === Step 1: SELECT FOR UPDATE 锁行 ===
    const [orders] = await pool.query(
      'SELECT id, status, user_id, version FROM orders WHERE id = ? FOR UPDATE',
      [orderId]
    );

    if (!orders.length) {
      return new Response(JSON.stringify({ error: '订单不存在' }), {
        status: 404, headers: { 'Content-Type': 'application/json' }
      });
    }

    const order = orders[0];
    const { id, status: fromStatus, user_id: orderUserId, version } = order;

    // === Step 2: 状态机 + 权限校验 ===
    try {
      canTransition(fromStatus, toStatus, { role, userId, orderUserId });
    } catch (e) {
      if (e instanceof StateMachineError) {
        return new Response(JSON.stringify({
          error: e.message,
          code: 'STATE_MACHINE_REJECTED'
        }), { status: 403, headers: { 'Content-Type': 'application/json' } });
      }
      throw e;
    }

    // === Step 3: 库存回补（取消/退款时） ===
    if ([OrderStatus.CANCELLED, OrderStatus.REFUNDED].includes(toStatus)) {
      await releaseStock(pool, orderId);
    }

    // === Step 4: 更新状态（含 version 乐观锁）===
    const updateFields = ['status = ?', 'version = version + 1'];
    const updateParams = [toStatus];

    if (toStatus === OrderStatus.PAID) {
      updateFields.push('paid_at = NOW()');
    }
    if (toStatus === OrderStatus.SHIPPED) {
      updateFields.push('express_company = ?', 'express_no = ?');
      updateParams.push(express_company, express_no);
    }

    updateParams.push(orderId, version);

    const [result] = await pool.query(
      `UPDATE orders SET ${updateFields.join(', ')} WHERE id = ? AND version = ?`,
      updateParams
    );

    if (result.affectedRows === 0) {
      return new Response(JSON.stringify({
        error: '并发冲突，请重试',
        code: 'CONCURRENT_UPDATE'
      }), { status: 409, headers: { 'Content-Type': 'application/json' } });
    }

    // === Step 5: 审计日志 ===
    await writeStatusLog(pool, orderId, fromStatus, toStatus, userId, reason);

    // === Step 6: 异步触发通知 ===
    await notifyStatusChange(pool, orderId, fromStatus, toStatus, userId);

    return new Response(JSON.stringify({
      ok: true,
      orderId,
      fromStatus,
      toStatus,
      version: version + 1,
      message: `订单已变更为 ${toStatus}`
    }), { status: 200, headers: { 'Content-Type': 'application/json' } });

  } catch (err) {
    console.error('[Order Transition] Error:', err);
    return new Response(JSON.stringify({ error: '服务器错误' }), {
      status: 500, headers: { 'Content-Type': 'application/json' }
    });
  } finally {
    await pool.end();
  }
}
