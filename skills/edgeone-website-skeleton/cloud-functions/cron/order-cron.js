/**
 * 订单定时任务 — Cron Job
 *
 * Phase 3 P2-2 实现
 *
 * EdgeOne Pages Cron 触发器配置：
 * 每 5 分钟执行一次
 *
 * 定时任务：
 * 1. PENDING 超时 30 分钟 → CANCELLED（用户超时未支付）
 * 2. SHIPPED 超过 7 天无售后 → COMPLETED（自动确认收货）
 *
 * EdgeOne Pages cron 配置（edgeone pages cron add 或配置文件中）：
 * trigger:
 *   type: schedule
 *   cron: "*/5 * * * *"   # 每 5 分钟
 *   function: cloud-functions/cron/order-cron.js
 */

import { Pool } from 'mysql2/promise';

/**
 * 获取数据库连接池
 * @param {Object} env
 */
async function getPool(env) {
  return new Pool({ connectionString: env.DATABASE_URL });
}

/**
 * 回补库存（用于取消订单）
 * @param {Pool} pool
 * @param {number} orderId
 */
async function releaseStock(pool, orderId) {
  await pool.query(`
    UPDATE products p
    JOIN order_items oi ON p.id = oi.product_id
    SET p.stock = p.stock + oi.qty,
        p.version = p.version + 1
    WHERE oi.order_id = ?
  `, [orderId]);
}

/**
 * 写入状态变更日志
 * @param {Pool} pool
 * @param {number} orderId
 * @param {string} from
 * @param {string} to
 */
async function writeLog(pool, orderId, from, to) {
  // 操作者为 null 表示系统操作
  await pool.query(
    `INSERT INTO order_status_logs (order_id, from_status, to_status, operator, reason)
     VALUES (?, ?, ?, NULL, ?)`,
    [orderId, from, to, 'System: auto-cron']
  );
}

/**
 * 定时任务主入口
 *
 * EdgeOne Pages Cron 触发时调用此函数
 * @param {Object} event - Cron 触发事件（含 scheduledTime）
 * @param {Object} env - 环境变量
 */
export async function scheduled(event, env) {
  console.log('[OrderCron] Starting scheduled job at', new Date().toISOString());

  const pool = await getPool(env);
  let totalCancelled = 0;
  let totalCompleted = 0;

  try {
    // === 任务 1：PENDING 超时 30 分钟 → CANCELLED ===
    // 先查出要取消的订单（避免在事务内做复杂逻辑）
    const [pendingOrders] = await pool.query(`
      SELECT id, user_id FROM orders
      WHERE status = 'PENDING'
        AND created_at < DATE_SUB(NOW(), INTERVAL 30 MINUTE)
    `);

    if (pendingOrders.length > 0) {
      console.log(`[OrderCron] Found ${pendingOrders.length} expired PENDING orders to cancel`);

      for (const order of pendingOrders) {
        const conn = await pool.getConnection();
        try {
          await conn.beginTransaction();

          const [orders] = await conn.query(
            'SELECT id, status, version FROM orders WHERE id = ? FOR UPDATE',
            [order.id]
          );
          const o = orders[0];
          if (!o || o.status !== 'PENDING') {
            // 已被其他进程处理，跳过
            await conn.rollback();
            continue;
          }

          // 回补库存
          await releaseStock(conn, order.id);

          // 更新状态
          await conn.query(
            'UPDATE orders SET status = ?, version = version + 1 WHERE id = ? AND version = ?',
            ['CANCELLED', order.id, o.version]
          );

          // 写日志
          await writeLog(conn, order.id, 'PENDING', 'CANCELLED');

          await conn.commit();
          totalCancelled++;
          console.log(`[OrderCron] Order ${order.id} auto-cancelled`);
        } catch (err) {
          await conn.rollback();
          console.error(`[OrderCron] Failed to cancel order ${order.id}:`, err.message);
        } finally {
          conn.release();
        }
      }
    }

    // === 任务 2：SHIPPED 超时 7 天 → COMPLETED ===
    const [shippedOrders] = await pool.query(`
      SELECT id, user_id FROM orders
      WHERE status = 'SHIPPED'
        AND paid_at < DATE_SUB(NOW(), INTERVAL 7 DAY)
    `);

    if (shippedOrders.length > 0) {
      console.log(`[OrderCron] Found ${shippedOrders.length} orders to auto-complete`);

      for (const order of shippedOrders) {
        const conn = await pool.getConnection();
        try {
          await conn.beginTransaction();

          const [orders] = await conn.query(
            'SELECT id, status, version FROM orders WHERE id = ? FOR UPDATE',
            [order.id]
          );
          const o = orders[0];
          if (!o || o.status !== 'SHIPPED') {
            await conn.rollback();
            continue;
          }

          await conn.query(
            'UPDATE orders SET status = ?, version = version + 1 WHERE id = ? AND version = ?',
            ['COMPLETED', order.id, o.version]
          );

          await writeLog(conn, order.id, 'SHIPPED', 'COMPLETED');

          await conn.commit();
          totalCompleted++;
          console.log(`[OrderCron] Order ${order.id} auto-completed`);
        } catch (err) {
          await conn.rollback();
          console.error(`[OrderCron] Failed to complete order ${order.id}:`, err.message);
        } finally {
          conn.release();
        }
      }
    }

    console.log(`[OrderCron] Job completed: ${totalCancelled} cancelled, ${totalCompleted} completed`);

  } catch (err) {
    console.error('[OrderCron] Job failed:', err);
    throw err; // 让 EdgeOne Pages 记录错误
  } finally {
    await pool.end();
  }
}
