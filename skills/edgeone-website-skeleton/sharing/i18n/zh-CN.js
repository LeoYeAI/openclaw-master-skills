/**
 * i18n — 中文（zh-CN）
 *
 * Phase 3 L2-2 实现
 *
 * 使用方式：
 *   import { zhCN } from './zh-CN.js';
 *   import { t } from './i18n.js';
 *
 *   t('nav.home') // → '首页'
 */

export const zhCN = {
  // ===== 导航 =====
  nav: {
    home: '首页',
    cart: '购物车',
    orders: '我的订单',
    login: '登录',
    register: '注册',
    logout: '退出',
    admin: '管理后台',
    search: '搜索',
  },

  // ===== 产品 =====
  product: {
    addToCart: '加入购物车',
    outOfStock: '缺货',
    inStock: '有货',
    price: '价格',
    category: '分类',
    all: '全部商品',
    viewDetail: '查看详情',
    buyNow: '立即购买',
  },

  // ===== 购物车 =====
  cart: {
    title: '购物车',
    empty: '购物车是空的',
    total: '合计',
    checkout: '去结算',
    remove: '删除',
    quantity: '数量',
    clearCart: '清空购物车',
    syncLogin: '登录后同步购物车',
  },

  // ===== 订单 =====
  order: {
    title: '我的订单',
    noOrders: '暂无订单',
    createOrder: '创建订单',
    cancelOrder: '取消订单',
    confirmReceipt: '确认收货',
    applyRefund: '申请退款',
    orderNo: '订单号',
    totalAmount: '总金额',
    createTime: '创建时间',
    expressCompany: '快递公司',
    expressNo: '运单号',
    cancelReason: '取消原因',
    refundReason: '退款原因',
    status: {
      PENDING:   '待支付',
      PAID:      '已支付',
      SHIPPED:   '已发货',
      COMPLETED: '已完成',
      CANCELLED: '已取消',
      REFUNDED:  '已退款',
    },
  },

  // ===== 支付 =====
  payment: {
    title: '选择支付方式',
    wechat: '微信支付',
    alipay: '支付宝',
    total: '应付金额',
    payNow: '立即支付',
    timeout: '支付超时，请重新下单',
  },

  // ===== Auth =====
  auth: {
    email: '邮箱',
    password: '密码',
    confirmPassword: '确认密码',
    username: '用户名',
    loginBtn: '登录',
    registerBtn: '注册',
    forgotPassword: '忘记密码',
    noAccount: '还没有账号？',
    hasAccount: '已有账号？',
    loginSuccess: '登录成功',
    registerSuccess: '注册成功',
    logoutSuccess: '已退出登录',
    loginRequired: '请先登录',
    invalidCredentials: '账号或密码错误',
    emailExists: '该邮箱已被注册',
  },

  // ===== 错误信息 =====
  error: {
    required: '此项为必填项',
    invalidEmail: '请输入有效的邮箱地址',
    passwordMismatch: '两次密码输入不一致',
    serverError: '服务器错误，请稍后重试',
    networkError: '网络连接失败',
    unauthorized: '未授权，请重新登录',
    forbidden: '无权限访问',
    notFound: '页面不存在',
  },

  // ===== Toast / 提示 =====
  toast: {
    addedToCart: '已加入购物车',
    removedFromCart: '已从购物车移除',
    orderCreated: '订单创建成功',
    orderCancelled: '订单已取消',
    refundApplied: '退款申请已提交',
    copied: '已复制',
  },

  // ===== SEO =====
  seo: {
    homeTitle: '极客商城 - 精选科技好物',
    homeDescription: '精选科技好物，放心购。全场低价，品质保障。',
    cartTitle: '购物车 - 极客商城',
    ordersTitle: '我的订单 - 极客商城',
    loginTitle: '登录 - 极客商城',
    registerTitle: '注册 - 极客商城',
  },
};
