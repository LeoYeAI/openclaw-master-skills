const crypto = require('crypto');
const fs = require('fs');

const {
  REQUIRED_AUTH_FIELDS,
  X_ENCODE_PUBLIC_KEY,
  CONFIG,
  AUTH_EXPIRED_CODES,
  AUTH_EXPIRED_MESSAGE_PATTERNS
} = require('./config');
const { getResultMessage, request } = require('./http');
const { resolveProfileFile } = require('./profile_store');

function normalizeAuthContext(input = null) {
  if (!input) {
    return {
      profileName: null,
      profileDir: null,
      authFile: null
    };
  }

  if (typeof input === 'string') {
    return {
      profileName: input,
      profileDir: null,
      authFile: null
    };
  }

  return {
    profileName: input.profileName || null,
    profileDir: input.profileDir || null,
    authFile: input.authFile || null
  };
}

function resolveAuthFile(input = null) {
  const authContext = normalizeAuthContext(input);
  return resolveProfileFile(authContext).filePath;
}

function validateAuth(auth) {
  if (!auth || typeof auth !== 'object') {
    return { valid: false, missing: REQUIRED_AUTH_FIELDS };
  }

  const missing = REQUIRED_AUTH_FIELDS.filter((field) => {
    const value = auth[field];
    return typeof value !== 'string' || value.trim() === '';
  });

  return { valid: missing.length === 0, missing };
}

function generateXEncode() {
  const nonce = Math.random().toString().substring(0, 16);
  const payload = Buffer.from(nonce, 'utf8').toString('base64');

  return crypto.publicEncrypt(
    {
      key: X_ENCODE_PUBLIC_KEY,
      padding: crypto.constants.RSA_PKCS1_PADDING
    },
    Buffer.from(payload, 'utf8')
  ).toString('base64');
}

function buildAuthHeaders(auth) {
  return {
    accessToken: auth.accessToken,
    sign: auth.sign,
    timestamp: auth.timestamp,
    'x-encode': auth.xEncode || generateXEncode(),
    Origin: `https://${CONFIG.baseUrl}`,
    redirect: 'https://www.library.sh.cn/reservation/mine?type=2',
    Referer: `https://${CONFIG.baseUrl}/pickSeat?floorId=${CONFIG.floorId}&floorType=0&clientId=${CONFIG.defaultHeaders.clientId}&sign=${encodeURIComponent(auth.sign)}&accessToken=${encodeURIComponent(auth.accessToken)}&timestamp=${encodeURIComponent(auth.timestamp)}&redirect_uri=${encodeURIComponent('https://www.library.sh.cn/reservation/mine?type=2')}`
  };
}

function buildUsePageHeaders(auth) {
  return {
    ...buildAuthHeaders(auth),
    Referer: `https://${CONFIG.baseUrl}/use?platform=uni&clientId=${CONFIG.defaultHeaders.clientId}&sign=${encodeURIComponent(auth.sign)}&accessToken=${encodeURIComponent(auth.accessToken)}&timestamp=${encodeURIComponent(auth.timestamp)}&libraryId=undefined`
  };
}

function hasAnyEnvAuth() {
  return false;
}

function isAuthExpiredResult(result) {
  const code = result?.resultStatus?.code;
  const message = getResultMessage(result);

  if (AUTH_EXPIRED_CODES.has(code)) {
    return true;
  }

  return AUTH_EXPIRED_MESSAGE_PATTERNS.some((pattern) =>
    message.toLowerCase().includes(pattern.toLowerCase())
  );
}

function getAuth(input = null) {
  const authContext = normalizeAuthContext(input);
  const authFileCandidates = [resolveAuthFile(authContext)];

  for (const authFile of authFileCandidates) {
    try {
      if (!authFile || !fs.existsSync(authFile)) {
        continue;
      }

      const fileAuth = JSON.parse(fs.readFileSync(authFile, 'utf8'));
      const fileValidation = validateAuth(fileAuth);
      if (!fileValidation.valid) {
        console.error(`认证文件缺少必要字段: ${fileValidation.missing.join(', ')}`);
        return null;
      }

      return {
        accessToken: fileAuth.accessToken.trim(),
        sign: fileAuth.sign.trim(),
        timestamp: fileAuth.timestamp.trim(),
        xEncode: typeof fileAuth.xEncode === 'string' && fileAuth.xEncode.trim()
          ? fileAuth.xEncode.trim()
          : null
      };
    } catch (error) {
      console.error('读取认证文件失败:', error.message);
    }
  }

  return null;
}

async function probeAuth(input = null) {
  const authContext = normalizeAuthContext(input);
  const auth = getAuth(authContext);
  if (!auth) {
    return { ok: false, reason: 'missing-auth' };
  }

  const options = {
    hostname: CONFIG.baseUrl,
    path: '/eastLibReservation/library',
    method: 'GET',
    headers: {
      ...CONFIG.defaultHeaders,
      ...buildUsePageHeaders(auth)
    }
  };

  try {
    const result = await request(options);
    if (isAuthExpiredResult(result)) {
      return { ok: false, reason: 'expired', result };
    }

    return { ok: true, result };
  } catch (error) {
    return { ok: false, reason: 'request-failed', error };
  }
}

async function runLogin(input = null) {
  const authContext = normalizeAuthContext(input);
  const { runLoginCli } = require('../login');
  const success = await runLoginCli(authContext);
  if (!success) {
    throw new Error('登录流程失败');
  }
}

async function ensureValidAuth(input = null) {
  const authContext = normalizeAuthContext(input);
  const auth = getAuth(authContext);
  const probe = await probeAuth(authContext);

  if (probe.ok) {
    return;
  }

  if (probe.reason === 'request-failed') {
    throw probe.error;
  }

  if (probe.reason === 'missing-auth') {
    console.log('⚠️ 未找到认证信息，准备拉起登录流程...');
  } else if (probe.reason === 'expired') {
    console.log(`⚠️ 检测到认证信息可能已过期: ${getResultMessage(probe.result) || '无效登录态'}`);
    console.log('准备拉起登录流程...');
  } else if (!auth) {
    console.log('⚠️ 当前没有可用认证信息，准备拉起登录流程...');
  }

  await runLogin(authContext);

  const refreshedProbe = await probeAuth(authContext);
  if (!refreshedProbe.ok) {
    if (refreshedProbe.reason === 'request-failed') {
      throw refreshedProbe.error;
    }
    throw new Error('登录完成后认证校验仍未通过，请检查登录流程是否成功');
  }
}

module.exports = {
  normalizeAuthContext,
  resolveAuthFile,
  buildAuthHeaders,
  buildUsePageHeaders,
  getAuth,
  generateXEncode,
  hasAnyEnvAuth,
  probeAuth,
  ensureValidAuth,
  getResultMessage
};
