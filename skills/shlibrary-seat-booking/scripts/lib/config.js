const REQUIRED_AUTH_FIELDS = ['accessToken', 'sign', 'timestamp'];
const X_ENCODE_PUBLIC_KEY = `-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCC/eZYX+wRw435tzHkao6zL/j1
hjL/of53wgKLPkLyWxCsM/KF0innlLaON6W7slOKNvwTOll63nFslBpzzECBg6tC
O129AbzS6GItOUBvEy6jDzQouIJq7anYs6u+fLMcdU8IvujTjfheKuk5g5W3T9bX
DSTyHnW1hfCpbZugLQIDAQAB
-----END PUBLIC KEY-----`;

const CONFIG = {
  baseUrl: 'yuyue.library.sh.cn',
  floorId: 4,
  defaultHeaders: {
    Accept: 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Content-Type': 'application/json;charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    clientId: '1837178870',
    source: '1'
  }
};

const AREA_NAME_TO_ID = {
  东区: 2,
  西区: 3,
  北区: 4,
  南区: 5
};

const AREA_ID_TO_NAME = {
  '2': '东区',
  '3': '西区',
  '4': '北区',
  '5': '南区'
};

const SLOT_SCHEDULES = {
  monday: {
    下午: ['13:45:00', '16:45:00'],
    晚上: ['17:00:00', '20:30:00']
  },
  regular: {
    上午: ['09:15:00', '12:45:00'],
    下午: ['13:00:00', '16:30:00'],
    晚上: ['16:45:00', '20:15:00']
  }
};

const DAY_BOOKING_ORDER = ['下午', '晚上', '上午'];
const RETRYABLE_MESSAGE_PATTERNS = ['系统拥挤'];
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 1500;
const DAY_BOOKING_SUBMIT_DELAY_MS = 1000;
const AUTH_EXPIRED_MESSAGE_PATTERNS = ['认证失败', 'token', '失效', '未登录', '重新登录'];
const AUTH_EXPIRED_CODES = new Set([-999, 101, 401, 403]);

module.exports = {
  REQUIRED_AUTH_FIELDS,
  X_ENCODE_PUBLIC_KEY,
  CONFIG,
  AREA_NAME_TO_ID,
  AREA_ID_TO_NAME,
  SLOT_SCHEDULES,
  DAY_BOOKING_ORDER,
  RETRYABLE_MESSAGE_PATTERNS,
  MAX_RETRIES,
  RETRY_DELAY_MS,
  DAY_BOOKING_SUBMIT_DELAY_MS,
  AUTH_EXPIRED_MESSAGE_PATTERNS,
  AUTH_EXPIRED_CODES
};
