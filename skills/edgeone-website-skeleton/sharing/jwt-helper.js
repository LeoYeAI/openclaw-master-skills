/**
 * JWT Helper — RS256 双轨迁移版
 *
 * Phase 3 P2-1 实现：
 * - 新 token 使用 RS256 私钥签发
 * - 验证时优先 RS256，30 天内兼容 HS256 旧 token
 * - Edge Functions（V8）专用，使用 crypto.subtle
 *
 * 密钥生成：
 *   openssl genrsa -out private.pem 2048
 *   openssl rsa -in private.pem -pubout -out public.pem
 *
 * 环境变量：
 *   JWT_PRIVATE_KEY — RSA 私钥（PEM 格式，换行符用 \n）
 *   JWT_PUBLIC_KEY  — RSA 公钥（PEM 格式，换行符用 \n）
 *   JWT_SECRET      — HS256 兼容密钥（Phase 3 后逐步废弃）
 */

import { crypto } from '@edge-runtime/primitives';

// ===================== 常量 =====================
const ALGORITHM_RS256 = 'RS256';
const ALGORITHM_HS256 = 'HS256';
const AT_TTL_MS = 15 * 60 * 1000;       // Access Token: 15 min
const RT_TTL_MS = 7 * 24 * 60 * 60 * 1000; // Refresh Token: 7 days
const HS256_COMPAT_WINDOW_MS = 30 * 24 * 60 * 60 * 1000; // 30 天兼容窗口

// ===================== PEM 解析 =====================

/**
 * 将 PEM 字符串（环境变量注入格式）解析为 CryptoKey
 * 环境变量中换行符被转义为 \n，需还原
 */
function parsePem(pem) {
  const lines = pem.replace(/\\n/g, '\n').split('\n');
  const base64 = lines
    .filter(l => !l.startsWith('-----'))
    .join('');
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

/**
 * 导入 RSA 私钥（RS256 签发用）
 */
export async function importPrivateKey(pem) {
  const keyData = parsePem(pem);
  return crypto.subtle.importKey(
    'pkcs8',
    keyData,
    { name: 'RSA-PSS', hash: 'SHA-256' },
    false,
    ['sign']
  );
}

/**
 * 导入 RSA 公钥（RS256 验证用）
 */
export async function importRSAPublicKey(pem) {
  const keyData = parsePem(pem);
  return crypto.subtle.importKey(
    'spki',
    keyData,
    { name: 'RSA-PSS', hash: 'SHA-256' },
    false,
    ['verify']
  );
}

/**
 * 导入 HMAC 密钥（HS256 验证用，兼容旧 token）
 */
export async function importHS256Secret(secret) {
  const encoder = new TextEncoder();
  return crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign', 'verify']
  );
}

// ===================== Base64URL =====================

function base64UrlEncode(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

function base64UrlDecode(str) {
  let s = str
    .replace(/-/g, '+')
    .replace(/_/g, '/');
  while (s.length % 4) s += '=';
  const binary = atob(s);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

// ===================== RS256 签发 =====================

/**
 * 签发 RS256 JWT（新版默认）
 * @param {Object} payload - JWT payload
 * @param {number} expiresInMs - 过期时间（毫秒）
 * @param {Object} env - 环境变量（含 JWT_PRIVATE_KEY）
 */
export async function signJWT(payload, expiresInMs, env) {
  const now = Math.floor(Date.now() / 1000);
  const header = { alg: ALGORITHM_RS256, typ: 'JWT' };
  const body = { ...payload, iat: now, exp: now + Math.floor(expiresInMs / 1000) };

  const headerEncoded = base64UrlEncode(new TextEncoder().encode(JSON.stringify(header)));
  const bodyEncoded = base64UrlEncode(new TextEncoder().encode(JSON.stringify(body)));
  const signingInput = `${headerEncoded}.${bodyEncoded}`;

  const privateKey = await importPrivateKey(env.JWT_PRIVATE_KEY);
  const signature = await crypto.subtle.sign(
    { name: 'RSA-PSS', saltLength: 32 },
    privateKey,
    new TextEncoder().encode(signingInput)
  );
  const signatureEncoded = base64UrlEncode(signature);

  return `${signingInput}.${signatureEncoded}`;
}

/**
 * 签发 Access Token（15 分钟，RS256）
 */
export async function signAccessToken(payload, env) {
  return signJWT(payload, AT_TTL_MS, env);
}

/**
 * 签发 Refresh Token（含 userId + version，用于乐观锁）
 * RT 也使用 RS256（Phase 3 后统一）
 */
export async function signRefreshToken(userId, version, env) {
  return signJWT(
    { sub: String(userId), type: 'refresh', v: version },
    RT_TTL_MS,
    env
  );
}

// ===================== JWT 验证 =====================

/**
 * RS256 验证（新版）
 */
async function verifyRS256(token, publicKey) {
  const parts = token.split('.');
  if (parts.length !== 3) return { valid: false };
  const [headerEncoded, bodyEncoded, sigEncoded] = parts;

  const signingInput = `${headerEncoded}.${bodyEncoded}`;
  const sigBytes = base64UrlDecode(sigEncoded);
  const header = JSON.parse(new TextDecoder().decode(base64UrlDecode(headerEncoded)));

  if (header.alg !== ALGORITHM_RS256) return { valid: false };

  const valid = await crypto.subtle.verify(
    { name: 'RSA-PSS', saltLength: 32 },
    publicKey,
    sigBytes,
    new TextEncoder().encode(signingInput)
  );

  if (!valid) return { valid: false };

  const body = JSON.parse(new TextDecoder().decode(base64UrlDecode(bodyEncoded)));
  const now = Math.floor(Date.now() / 1000);
  if (body.exp < now) return { valid: false };

  return { valid: true, payload: body };
}

/**
 * HS256 验证（30 天兼容窗口内旧 token）
 */
async function verifyHS256(token, secret) {
  const parts = token.split('.');
  if (parts.length !== 3) return { valid: false };
  const [headerEncoded, bodyEncoded, sigEncoded] = parts;

  const header = JSON.parse(new TextDecoder().decode(base64UrlDecode(headerEncoded)));
  if (header.alg !== ALGORITHM_HS256) return { valid: false };

  const signingInput = `${headerEncoded}.${bodyEncoded}`;
  const expectedSigBytes = base64UrlDecode(sigEncoded);
  const secretKey = await importHS256Secret(secret);

  const valid = await crypto.subtle.verify(
    'HMAC',
    secretKey,
    expectedSigBytes,
    new TextEncoder().encode(signingInput)
  );

  if (!valid) return { valid: false };

  const body = JSON.parse(new TextDecoder().decode(base64UrlDecode(bodyEncoded)));
  const now = Math.floor(Date.now() / 1000);
  if (body.exp < now) return { valid: false };

  return { valid: true, payload: body };
}

/**
 * 双轨 JWT 验证（核心函数）
 *
 * 优先 RS256，30 天内旧 HS256 token 仍可验证（向后兼容）
 *
 * @param {string} token - JWT token
 * @param {Object} env - 环境变量
 * @returns {Object|null} payload 或 null（验证失败）
 */
export async function verifyJWT(token, env) {
  // 方案 A：RS256 验证（新版 token，优先）
  try {
    if (env.JWT_PUBLIC_KEY) {
      const publicKey = await importRSAPublicKey(env.JWT_PUBLIC_KEY);
      const result = await verifyRS256(token, publicKey);
      if (result.valid) {
        return { ...result.payload, _alg: ALGORITHM_RS256 };
      }
    }
  } catch (err) {
    console.warn('[JWT] RS256 verification failed, trying HS256:', err.message);
  }

  // 方案 B：HS256 兼容（30 天窗口内旧 token）
  try {
    if (env.JWT_SECRET) {
      const result = await verifyHS256(token, env.JWT_SECRET);
      if (result.valid) {
        // 检查是否在 30 天兼容窗口内
        const issuedAt = result.payload.iat * 1000;
        const compatDeadline = Date.now() - HS256_COMPAT_WINDOW_MS;
        if (issuedAt > compatDeadline) {
          console.info(`[JWT] HS256 token accepted (within 30d compat window, iat=${new Date(issuedAt).toISOString()})`);
          return { ...result.payload, _alg: ALGORITHM_HS256 };
        } else {
          console.info('[JWT] HS256 token rejected (outside 30d compat window)');
        }
      }
    }
  } catch (err) {
    console.warn('[JWT] HS256 verification failed:', err.message);
  }

  return null;
}

/**
 * 解析 JWT（不解签名，仅读取 payload，用于 RT 轮换时取 userId）
 * ⚠️ 不做签名验证，仅解析——验证由 verifyJWT 负责
 */
export function parseJWTWithoutVerify(token) {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const body = JSON.parse(new TextDecoder().decode(base64UrlDecode(parts[1])));
    return body;
  } catch {
    return null;
  }
}

// ===================== 便捷封装 =====================

/**
 * 验证 Access Token，返回 payload 或 null
 */
export async function verifyAccessToken(token, env) {
  const payload = await verifyJWT(token, env);
  if (!payload) return null;
  if (payload.type === 'refresh') return null; // RT 不能当 AT 用
  return payload;
}

/**
 * 验证 Refresh Token，返回 payload 或 null
 */
export async function verifyRefreshToken(token, env) {
  return verifyJWT(token, env);
}

// ===================== Token 提取（从请求中） =====================

/**
 * 从请求 Cookie 或 Authorization Header 提取 JWT
 */
export function extractToken(request) {
  // 1. Authorization: Bearer <token>
  const auth = request.headers.get('Authorization');
  if (auth?.startsWith('Bearer ')) {
    return { token: auth.slice(7), source: 'Bearer' };
  }

  // 2. Cookie: at=<token>
  const cookieHeader = request.headers.get('Cookie') || '';
  const atMatch = cookieHeader.match(/(?:^|;\s*)at=([^;]+)/);
  if (atMatch) {
    return { token: decodeURIComponent(atMatch[1]), source: 'Cookie' };
  }

  return null;
}

/**
 * 从 Cookie 提取 Refresh Token
 */
export function extractRefreshToken(request) {
  const cookieHeader = request.headers.get('Cookie') || '';
  const rtMatch = cookieHeader.match(/(?:^|;\s*)rt=([^;]+)/);
  if (rtMatch) {
    return decodeURIComponent(rtMatch[1]);
  }
  return null;
}
