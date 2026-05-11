/**
 * 订单状态机 — 核心实现
 *
 * Phase 3 P2-2 实现：
 * - 6 个状态 + 完整状态流转规则
 * - 权限矩阵（user:own / admin）
 * - 状态机错误类
 *
 * 使用方式：
 *   import { canTransition, OrderStatus, StateMachineError } from './order-state-machine';
 *
 *   try {
 *     canTransition('PENDING', 'CANCELLED', { role: 'user', userId: 123, orderUserId: 123 });
 *   } catch (e) {
 *     // StateMachineError: 权限不足或非法状态变更
 *   }
 */

// ===================== 状态定义 =====================
export const OrderStatus = {
  PENDING:   'PENDING',    // 待支付
  PAID:      'PAID',       // 已支付
  SHIPPED:   'SHIPPED',    // 已发货
  COMPLETED: 'COMPLETED',  // 已完成
  CANCELLED: 'CANCELLED',  // 已取消（终态）
  REFUNDED:  'REFUNDED',   // 已退款（终态）
};

// ===================== 状态流转表 =====================
// currentStatus → [allowedNextStatuses]
export const TRANSITIONS = {
  [OrderStatus.PENDING]:   [OrderStatus.PAID, OrderStatus.CANCELLED],
  [OrderStatus.PAID]:      [OrderStatus.SHIPPED, OrderStatus.REFUNDED],
  [OrderStatus.SHIPPED]:   [OrderStatus.COMPLETED, OrderStatus.REFUNDED],
  [OrderStatus.COMPLETED]: [OrderStatus.REFUNDED],
  [OrderStatus.CANCELLED]:  [], // 终态
  [OrderStatus.REFUNDED]:  [], // 终态
};

// ===================== 权限矩阵 =====================
// 'from→to': ['requiredRoles']
// 'user:own' = 本人订单的普通用户
// 'admin'    = 管理员（任意订单）
export const PERMISSIONS = {
  'PENDING→CANCELLED': ['user:own', 'admin'],  // 用户可取消本人待支付订单
  'PAID→SHIPPED':      ['admin'],                // 仅管理员可发货
  'PAID→REFUNDED':     ['user:own', 'admin'],  // 用户可退款本人已支付订单
  'SHIPPED→COMPLETED': ['user:own', 'admin'],  // 用户确认收货或管理员操作
  'SHIPPED→REFUNDED':  ['user:own', 'admin'],  // 发货后可退货退款
  'COMPLETED→REFUNDED':['admin'],               // 已完成仅管理员可退款（需审批）
};

// ===================== 状态机校验 =====================

/**
 * 校验状态变更是否合法
 * @param {string} from - 当前状态
 * @param {string} to - 目标状态
 * @param {{ role: string, userId: number, orderUserId: number }} ctx - 权限上下文
 * @returns {boolean} true = 允许
 * @throws {StateMachineError} 非法变更或权限不足
 */
export function canTransition(from, to, { role, userId, orderUserId }) {
  // Step 1：校验目标状态是否在允许列表中
  const allowed = TRANSITIONS[from];
  if (!allowed || !allowed.includes(to)) {
    throw new StateMachineError(
      `禁止的状态变更：${from} → ${to}（当前状态 "${from}" 不允许变更为 "${to}"）`
    );
  }

  // Step 2：校验权限
  const permKey = `${from}→${to}`;
  const required = PERMISSIONS[permKey];
  if (!required) {
    throw new StateMachineError(`未定义权限规则：${permKey}`);
  }

  // 确定当前操作者身份
  const isAdmin = role === 'admin';
  const isOwnOrder = userId === orderUserId;

  let hasPermission = false;

  if (isAdmin) {
    hasPermission = required.includes('admin');
  } else {
    // 普通用户：本人订单 → 'user:own'，非本人 → 无权限
    hasPermission = isOwnOrder && required.includes('user:own');
  }

  if (!hasPermission) {
    const roleTag = isAdmin ? 'admin' : (isOwnOrder ? 'user:own' : 'user:other');
    throw new StateMachineError(
      `权限不足：${from} → ${to} 需要 [${required.join('/')}]，当前身份 "${roleTag}"（${isOwnOrder ? '本人订单' : '非本人订单'}）`
    );
  }

  return true;
}

/**
 * 获取当前状态允许的全部目标状态
 * @param {string} from - 当前状态
 * @param {{ role: string, userId: number, orderUserId: number }} ctx - 权限上下文
 * @returns {string[]} 允许的状态列表
 */
export function getAllowedTransitions(from, { role, userId, orderUserId }) {
  const allowed = TRANSITIONS[from] || [];
  return allowed.filter(to => {
    try {
      canTransition(from, to, { role, userId, orderUserId });
      return true;
    } catch {
      return false;
    }
  });
}

// ===================== 错误类 =====================

export class StateMachineError extends Error {
  constructor(message) {
    super(message);
    this.name = 'StateMachineError';
  }
}

// ===================== 状态显示文本 =====================

export const STATUS_LABELS = {
  [OrderStatus.PENDING]:   { 'zh-CN': '待支付', 'en-US': 'Pending Payment' },
  [OrderStatus.PAID]:      { 'zh-CN': '已支付', 'en-US': 'Paid' },
  [OrderStatus.SHIPPED]:   { 'zh-CN': '已发货', 'en-US': 'Shipped' },
  [OrderStatus.COMPLETED]: { 'zh-CN': '已完成', 'en-US': 'Completed' },
  [OrderStatus.CANCELLED]: { 'zh-CN': '已取消', 'en-US': 'Cancelled' },
  [OrderStatus.REFUNDED]:  { 'zh-CN': '已退款', 'en-US': 'Refunded' },
};

export function getStatusLabel(status, lang = 'zh-CN') {
  return STATUS_LABELS[status]?.[lang] || status;
}

// ===================== 状态颜色 =====================

export const STATUS_COLORS = {
  [OrderStatus.PENDING]:   { bg: '#fff7e6', text: '#d48806', border: '#ffe599' },
  [OrderStatus.PAID]:      { bg: '#e6f7ff', text: '#1890ff', border: '#91d5ff' },
  [OrderStatus.SHIPPED]:   { bg: '#f0f5ff', text: '#597ef7', border: '#adc6ff' },
  [OrderStatus.COMPLETED]:  { bg: '#f6ffed', text: '#52c41a', border: '#b7eb8f' },
  [OrderStatus.CANCELLED]:  { bg: '#fff1f0', text: '#ff4d4f', border: '#ffccc7' },
  [OrderStatus.REFUNDED]:   { bg: '#fff1f0', text: '#ff7875', border: '#ffd8d8' },
};
