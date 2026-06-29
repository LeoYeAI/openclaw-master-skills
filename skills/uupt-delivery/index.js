const fs = require('fs');
const path = require('path');
const axios = require('axios');
const crypto = require('crypto');

// 配置文件路径
const CONFIG_FILE = path.join(__dirname, 'config.json');
const DEFAULTS_FILE = path.join(__dirname, 'defaults.json');

/**
 * 读取配置文件
 */
function readConfig() {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      const data = fs.readFileSync(CONFIG_FILE, 'utf8');
      return JSON.parse(data);
    }
  } catch (error) {
    console.error('读取配置文件失败:', error.message);
  }
  return {};
}

/**
 * 读取预制默认配置
 */
function readDefaults() {
  try {
    if (fs.existsSync(DEFAULTS_FILE)) {
      const data = fs.readFileSync(DEFAULTS_FILE, 'utf8');
      return JSON.parse(data);
    }
  } catch (error) {
    console.error('读取默认配置失败:', error.message);
  }
  return {};
}

/**
 * 保存配置文件（合并写入）
 */
function saveConfig(config) {
  try {
    const existing = readConfig();
    const merged = { ...existing, ...config };
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(merged, null, 2), 'utf8');
    console.log('配置已保存到:', CONFIG_FILE);
    return true;
  } catch (error) {
    console.error('保存配置文件失败:', error.message);
    return false;
  }
}

/**
 * 获取配置（优先级：环境变量 > config.json > defaults.json）
 */
function getConfig() {
  const defaults = readDefaults();
  const config = readConfig();
  
  return {
    appId: process.env.UUPT_APP_ID || config.appId || defaults.appId || null,
    appSecret: process.env.UUPT_APP_SECRET || config.appSecret || defaults.appSecret || null,
    openId: process.env.UUPT_OPEN_ID || config.openId || defaults.openId || null,
    apiUrl: process.env.UUPT_API_URL || config.apiUrl || defaults.apiUrl || 'https://api-open.uupt.com/openapi/v3/'
  };
}

/**
 * 检查并确保配置完整
 */
function ensureConfig() {
  const config = getConfig();
  
  if (!config.appId || !config.appSecret) {
    console.log('\n[FATAL] 缺少应用凭证，请确认 defaults.json 文件完整');
    throw new Error('[FATAL] 缺少应用凭证 (appId/appSecret)，请确认 defaults.json 文件存在且内容完整');
  }
  
  if (!config.openId) {
    console.log('\n[REGISTRATION_REQUIRED]');
    console.log('尚未注册，请先完成手机号验证获取授权。');
    console.log('请运行注册脚本: node scripts/register.js --mobile="您的手机号"');
    throw new Error('[REGISTRATION_REQUIRED] 尚未注册，请先完成手机号验证获取授权');
  }
  
  return config;
}

/**
 * 生成 MD5 签名
 */
function generateMd5(input) {
  return crypto.createHash('md5').update(input, 'utf8').digest('hex').toUpperCase();
}

/**
 * 发送 API 请求（需要 openId 的业务接口）
 */
async function postRequest(bizParams, apiPath) {
  const config = ensureConfig();
  const timestamp = Math.floor(Date.now() / 1000);
  const bizJson = JSON.stringify(bizParams);
  
  const signStr = bizJson + config.appSecret + timestamp;
  const sign = generateMd5(signStr);
  
  const payload = {
    openId: config.openId,
    timestamp: timestamp,
    biz: bizJson,
    sign: sign
  };
  
  const url = config.apiUrl + apiPath;
  
  try {
    console.log(`🔄 正在请求: ${apiPath}...`);
    
    const response = await axios.post(url, payload, {
      headers: {
        'X-App-Id': config.appId,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.status === 200) {
      console.log('✅ 请求成功\n');
      return response.data;
    } else {
      console.error('❌ 请求失败:', response.status);
      return null;
    }
  } catch (error) {
    console.error('❌ 请求异常:', error.message);
    return null;
  }
}

/**
 * 发送无需 openId 的 API 请求（用于注册/授权接口）
 */
async function postUnauthorizedRequest(bizParams, apiPath) {
  const config = getConfig();
  
  if (!config.appId || !config.appSecret) {
    throw new Error('[FATAL] 缺少应用凭证 (appId/appSecret)，请确认 defaults.json 文件存在且内容完整');
  }
  
  const timestamp = Math.floor(Date.now() / 1000);
  const bizJson = JSON.stringify(bizParams);
  
  const signStr = bizJson + config.appSecret + timestamp;
  const sign = generateMd5(signStr);
  
  const payload = {
    timestamp: timestamp,
    biz: bizJson,
    sign: sign
  };
  
  const url = config.apiUrl + apiPath;
  
  try {
    console.log(`🔄 正在请求: ${apiPath}...`);
    
    const response = await axios.post(url, payload, {
      headers: {
        'X-App-Id': config.appId,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.status === 200) {
      console.log('✅ 请求成功\n');
      return response.data;
    } else {
      console.error('❌ 请求失败:', response.status);
      return null;
    }
  } catch (error) {
    console.error('❌ 请求异常:', error.message);
    return null;
  }
}

/**
 * 获取用户公网 IP
 * 使用多个备用服务，提高成功率
 */
async function getPublicIp() {
  const ipServices = [
    { url: 'https://httpbin.org/ip', extract: (data) => data.origin },
    { url: 'https://ipinfo.io/json', extract: (data) => data.ip },
    { url: 'https://api64.ipify.org?format=json', extract: (data) => data.ip },
    { url: 'https://api.ipify.org?format=json', extract: (data) => data.ip }
  ];

  for (const service of ipServices) {
    try {
      const response = await axios.get(service.url, { timeout: 5000 });
      const ip = service.extract(response.data);
      if (ip) {
        // 处理可能的逗号分隔的多个IP
        const cleanIp = ip.split(',')[0].trim();
        return cleanIp;
      }
    } catch (error) {
      console.log(`[IP查询] ${service.url} 失败: ${error.message}`);
      continue;
    }
  }

  console.error('[错误] 所有IP查询服务均不可用');
  return '';
}

/**
 * 发送短信验证码
 * @param {Object} params
 * @param {string} params.userMobile - 用户手机号（必填）
 * @param {string} params.userIp - 用户公网 IP（必填）
 * @param {string} params.imageCode - 图片验证码（可选）
 */
async function sendSmsCode(params) {
  const { userMobile, userIp, imageCode } = params;
  
  if (!userMobile) {
    throw new Error('手机号为必填项');
  }
  if (!userIp) {
    throw new Error('用户公网 IP 为必填项');
  }
  
  const biz = {
    userMobile: userMobile,
    userIp: userIp,
    imageCode: imageCode || ''
  };
  
  console.log('📱 正在发送短信验证码...');
  return await postUnauthorizedRequest(biz, 'user/unauthorized/sendSmsCode');
}

/**
 * 商户授权（获取 openId）
 * @param {Object} params
 * @param {string} params.userMobile - 用户手机号（必填）
 * @param {string} params.userIp - 用户公网 IP（必填）
 * @param {string} params.smsCode - 短信验证码（必填）
 */
async function auth(params) {
  const { userMobile, userIp, smsCode } = params;
  
  if (!userMobile) {
    throw new Error('手机号为必填项');
  }
  if (!userIp) {
    throw new Error('用户公网 IP 为必填项');
  }
  if (!smsCode) {
    throw new Error('短信验证码为必填项');
  }
  
  const biz = {
    userMobile: userMobile,
    userIp: userIp,
    smsCode: smsCode,
    cityName: '郑州市',
    countyName: ''
  };
  
  console.log('🔐 正在进行商户授权...');
  const result = await postUnauthorizedRequest(biz, 'user/unauthorized/auth');
  
  if (result && result.body && result.body.openId) {
    saveConfig({ openId: result.body.openId });
    console.log('✅ 授权成功，openId 已保存');
  }
  
  return result;
}

/**
 * 订单询价
 * @param {Object} params - 询价参数
 * @param {string} params.fromAddress - 起始地址（必填）
 * @param {string} params.toAddress - 目的地址（必填）
 * @param {string} params.cityName - 城市名称（可选，默认郑州市）
 */
async function orderPrice(params) {
  const { fromAddress, toAddress, cityName = '郑州市' } = params;
  
  if (!fromAddress || !toAddress) {
    throw new Error('起始地址和目的地址为必填项');
  }
  
  // 确保城市名带"市"
  let city = cityName;
  if (city && !city.endsWith('市')) {
    city = city + '市';
  }
  
  const biz = {
    fromAddress: fromAddress,
    toAddress: toAddress,
    sendType: 'SEND',
    cityName: city,
    specialChannel: 2
  };
  
  console.log('💰 正在查询配送价格...');
  return await postRequest(biz, 'order/orderPrice');
}

/**
 * 创建订单
 * @param {Object} params - 订单参数
 * @param {string} params.priceToken - 询价返回的 token（必填）
 * @param {string} params.receiverPhone - 收件人电话（必填）
 */
async function createOrder(params) {
  const { priceToken, receiverPhone } = params;
  
  if (!priceToken) {
    throw new Error('priceToken 为必填项，请先调用订单询价接口');
  }
  
  if (!receiverPhone) {
    throw new Error('收件人电话为必填项');
  }
  
  const biz = {
    priceToken: priceToken,
    receiver_phone: receiverPhone,
    pushType: 'OPEN_ORDER',
    payType: 'BALANCE_PAY',
    specialChannel: 2,
    specialType: 'NOT_NEED_WARM'
  };
  
  console.log('📦 正在创建订单...');
  return await postRequest(biz, 'order/addOrder');
}

/**
 * 查询订单详情
 * @param {Object} params - 查询参数
 * @param {string} params.orderCode - 订单编号（必填）
 */
async function orderDetail(params) {
  const { orderCode } = params;
  
  if (!orderCode) {
    throw new Error('订单编号为必填项');
  }
  
  const biz = {
    order_code: orderCode
  };
  
  console.log('📋 正在查询订单详情...');
  return await postRequest(biz, 'order/orderDetail');
}

/**
 * 取消订单
 * @param {Object} params - 取消参数
 * @param {string} params.orderCode - 订单编号（必填）
 * @param {string} params.reason - 取消原因（可选）
 */
async function cancelOrder(params) {
  const { orderCode, reason } = params;
  
  if (!orderCode) {
    throw new Error('订单编号为必填项');
  }
  
  const biz = {
    order_code: orderCode,
    reason: reason || ''
  };
  
  console.log('❌ 正在取消订单...');
  return await postRequest(biz, 'order/cancelOrder');
}

/**
 * 跑男实时追踪
 * @param {Object} params - 追踪参数
 * @param {string} params.orderCode - 订单编号（必填）
 */
async function driverTrack(params) {
  const { orderCode } = params;
  
  if (!orderCode) {
    throw new Error('订单编号为必填项');
  }
  
  const biz = {
    order_code: orderCode
  };
  
  console.log('🏃 正在查询跑男信息...');
  return await postRequest(biz, 'order/driverTrack');
}

/**
 * 格式化价格（分转元）
 */
function formatPrice(priceInFen) {
  return (priceInFen / 100).toFixed(2);
}

// 导出函数
module.exports = {
  readConfig,
  readDefaults,
  saveConfig,
  getConfig,
  ensureConfig,
  postUnauthorizedRequest,
  getPublicIp,
  sendSmsCode,
  auth,
  orderPrice,
  createOrder,
  orderDetail,
  cancelOrder,
  driverTrack,
  formatPrice
};

// 如果直接运行此文件，显示帮助信息
if (require.main === module) {
  console.log(`
🚚 UU跑腿同城配送服务

可用命令:
  node scripts/register.js       - 手机号注册/获取授权
  node scripts/order-price.js    - 订单询价
  node scripts/create-order.js   - 创建订单
  node scripts/order-detail.js   - 查询订单详情
  node scripts/cancel-order.js   - 取消订单
  node scripts/driver-track.js   - 跑男实时追踪

首次使用:
  运行任何命令时会自动检测是否需要注册。
  如需手动注册: node scripts/register.js --mobile="您的手机号"
`);
}
