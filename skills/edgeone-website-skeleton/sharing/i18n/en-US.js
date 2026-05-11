/**
 * i18n — English (en-US)
 *
 * Phase 3 L2-2 实现
 */

export const enUS = {
  // ===== Navigation =====
  nav: {
    home: 'Home',
    cart: 'Cart',
    orders: 'My Orders',
    login: 'Login',
    register: 'Register',
    logout: 'Logout',
    admin: 'Admin',
    search: 'Search',
  },

  // ===== Product =====
  product: {
    addToCart: 'Add to Cart',
    outOfStock: 'Out of Stock',
    inStock: 'In Stock',
    price: 'Price',
    category: 'Category',
    all: 'All Products',
    viewDetail: 'View Details',
    buyNow: 'Buy Now',
  },

  // ===== Cart =====
  cart: {
    title: 'Shopping Cart',
    empty: 'Your cart is empty',
    total: 'Total',
    checkout: 'Checkout',
    remove: 'Remove',
    quantity: 'Qty',
    clearCart: 'Clear Cart',
    syncLogin: 'Sign in to sync your cart',
  },

  // ===== Order =====
  order: {
    title: 'My Orders',
    noOrders: 'No orders yet',
    createOrder: 'Place Order',
    cancelOrder: 'Cancel Order',
    confirmReceipt: 'Confirm Receipt',
    applyRefund: 'Request Refund',
    orderNo: 'Order No.',
    totalAmount: 'Total',
    createTime: 'Created',
    expressCompany: 'Carrier',
    expressNo: 'Tracking No.',
    cancelReason: 'Cancellation Reason',
    refundReason: 'Refund Reason',
    status: {
      PENDING:   'Pending Payment',
      PAID:      'Paid',
      SHIPPED:   'Shipped',
      COMPLETED: 'Completed',
      CANCELLED: 'Cancelled',
      REFUNDED:  'Refunded',
    },
  },

  // ===== Payment =====
  payment: {
    title: 'Choose Payment Method',
    wechat: 'WeChat Pay',
    alipay: 'Alipay',
    total: 'Amount Due',
    payNow: 'Pay Now',
    timeout: 'Payment timeout, please place a new order',
  },

  // ===== Auth =====
  auth: {
    email: 'Email',
    password: 'Password',
    confirmPassword: 'Confirm Password',
    username: 'Username',
    loginBtn: 'Sign In',
    registerBtn: 'Sign Up',
    forgotPassword: 'Forgot Password?',
    noAccount: "Don't have an account?",
    hasAccount: 'Already have an account?',
    loginSuccess: 'Signed in successfully',
    registerSuccess: 'Account created successfully',
    logoutSuccess: 'Signed out',
    loginRequired: 'Please sign in first',
    invalidCredentials: 'Invalid email or password',
    emailExists: 'This email is already registered',
  },

  // ===== Errors =====
  error: {
    required: 'This field is required',
    invalidEmail: 'Please enter a valid email address',
    passwordMismatch: 'Passwords do not match',
    serverError: 'Server error, please try again later',
    networkError: 'Network connection failed',
    unauthorized: 'Unauthorized, please sign in again',
    forbidden: 'Access denied',
    notFound: 'Page not found',
  },

  // ===== Toast =====
  toast: {
    addedToCart: 'Added to cart',
    removedFromCart: 'Removed from cart',
    orderCreated: 'Order placed successfully',
    orderCancelled: 'Order cancelled',
    refundApplied: 'Refund requested',
    copied: 'Copied',
  },

  // ===== SEO =====
  seo: {
    homeTitle: 'Geek Mall - Premium Tech Products',
    homeDescription: 'Premium tech products, quality guaranteed. Shop with confidence.',
    cartTitle: 'Cart - Geek Mall',
    ordersTitle: 'My Orders - Geek Mall',
    loginTitle: 'Sign In - Geek Mall',
    registerTitle: 'Sign Up - Geek Mall',
  },
};
