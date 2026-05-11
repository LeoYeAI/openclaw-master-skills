# Auth 模块参考文档

## 一、认证架构总览

```
未登录 → 跳转登录页（AuthGuard）
已登录 → JWT Cookie → Edge Middleware 验证 → context.user 注入
过期 → 自动刷新 RT → 换新 JWT
```

## 二、JWT 配置

```javascript
// edge-functions/utils/jwt-helper.js
import { crypto } from '@edge-runtime/primitives';

const JWT_SECRET = new TextEncoder().encode(env.JWT_SECRET);
const ALGORITHM = 'HS256';

export async function signAccessToken(payload) {
  const header = btoa(JSON.stringify({ alg: ALGORITHM, typ: 'JWT' }));
  const body = btoa(JSON.stringify({ ...payload, exp: Date.now() + 15 * 60 * 1000, iat: Date.now() }));
  const signature = await crypto.subtle.sign('HMAC', JWT_SECRET, new TextEncoder().encode(`${header}.${body}`));
  return `${header}.${body}.${btoa(String.fromCharCode(...new Uint8Array(signature)))}`;
}

export async function verifyAccessToken(token) {
  try {
    const [header, body, sig] = token.split('.');
    const valid = await crypto.subtle.verify('HMAC', JWT_SECRET, Uint8Array.from(atob(sig), c => c.charCodeAt(0)), new TextEncoder().encode(`${header}.${body}`));
    if (!valid) return null;
    const payload = JSON.parse(atob(body));
    if (payload.exp < Date.now()) return null;
    return payload;
  } catch {
    return null;
  }
}
```

### 【Phase 3 新增】RS256 双轨迁移

> **版本：** Phase 3 P2-1
> **密钥生成：**
> ```bash
> openssl genrsa -out private.pem 2048
> openssl rsa -in private.pem -pubout -out public.pem
> ```
> **环境变量：**
> - `JWT_PRIVATE_KEY` — RSA 私钥（PEM，换行符用 `\n` 转义）
> - `JWT_PUBLIC_KEY`  — RSA 公钥（PEM，换行符用 `\n` 转义）
> - `JWT_SECRET`      — HS256 密钥（30 天兼容窗口后删除）

```javascript
// sharing/jwt-helper.js — RS256 实现（完整源码）

// ===================== PEM 解析 =====================
function parsePem(pem) {
  const lines = pem.replace(/\\n/g, '\n').split('\n');
  const base64 = lines.filter(l => !l.startsWith('-----')).join('');
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes;
}

function base64UrlEncode(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function base64UrlDecode(str) {
  let s = str.replace(/-/g, '+').replace(/_/g, '/');
  while (s.length % 4) s += '=';
  const binary = atob(s);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes;
}

// ===================== RS256 签发 =====================
export async function signJWT(payload, expiresInMs, env) {
  const now = Math.floor(Date.now() / 1000);
  const header = { alg: 'RS256', typ: 'JWT' };
  const body = { ...payload, iat: now, exp: now + Math.floor(expiresInMs / 1000) };

  const headerEncoded = base64UrlEncode(new TextEncoder().encode(JSON.stringify(header)));
  const bodyEncoded = base64UrlEncode(new TextEncoder().encode(JSON.stringify(body)));
  const signingInput = `${headerEncoded}.${bodyEncoded}`;

  const keyData = parsePem(env.JWT_PRIVATE_KEY);
  const privateKey = await crypto.subtle.importKey(
    'pkcs8', keyData, { name: 'RSA-PSS', hash: 'SHA-256' }, false, ['sign']
  );
  const signature = await crypto.subtle.sign(
    { name: 'RSA-PSS', saltLength: 32 }, privateKey,
    new TextEncoder().encode(signingInput)
  );

  return `${signingInput}.${base64UrlEncode(signature)}`;
}

// ===================== 双轨验证 =====================
export async function verifyJWT(token, env) {
  const parts = token.split('.');
  if (parts.length !== 3) return null;
  const [headerEnc, bodyEnc, sigEnc] = parts;

  const header = JSON.parse(new TextDecoder().decode(base64UrlDecode(headerEnc)));
  const body = JSON.parse(new TextDecoder().decode(base64UrlDecode(bodyEnc)));
  const now = Math.floor(Date.now() / 1000);

  // RS256 优先验证
  if (header.alg === 'RS256' && env.JWT_PUBLIC_KEY) {
    try {
      const keyData = parsePem(env.JWT_PUBLIC_KEY);
      const pubKey = await crypto.subtle.importKey(
        'spki', keyData, { name: 'RSA-PSS', hash: 'SHA-256' }, false, ['verify']
      );
      const valid = await crypto.subtle.verify(
        { name: 'RSA-PSS', saltLength: 32 }, pubKey,
        base64UrlDecode(sigEnc), new TextEncoder().encode(`${headerEnc}.${bodyEnc}`)
      );
      if (valid && body.exp > now) return { ...body, _alg: 'RS256' };
    } catch {}
  }

  // HS256 兼容（30 天窗口内）
  if (header.alg === 'HS256' && env.JWT_SECRET) {
    try {
      const secretKey = await crypto.subtle.importKey(
        'raw', new TextEncoder().encode(env.JWT_SECRET),
        { name: 'HMAC', hash: 'SHA-256' }, false, ['verify']
      );
      const valid = await crypto.subtle.verify(
        'HMAC', secretKey, base64UrlDecode(sigEnc),
        new TextEncoder().encode(`${headerEnc}.${bodyEnc}`)
      );
      if (valid && body.exp > now) {
        // 仅接受 30 天内签发的旧 token
        const compatDeadline = Date.now() - 30 * 24 * 3600 * 1000;
        if (body.iat * 1000 > compatDeadline) {
          return { ...body, _alg: 'HS256' };
        }
      }
    } catch {}
  }

  return null;
}
```

### RS256 迁移时间线

```
Day 0:      部署 RS256 签发 + 双轨验证（JWT_PRIVATE_KEY/JWT_PUBLIC_KEY 注入）
Day 1-30:   HS256 旧 token 仍可验证（向后兼容，日志记录 _alg: 'HS256'）
Day 30:     移除 HS256 兼容分支（仅 RS256）
Day 30:     删除 JWT_SECRET 环境变量
```
```

## 三、KV Session 存储

```javascript
// edge-functions/utils/kv-helper.js
const SESSION_TTL = 86400;  // 24h

export async function getSession(kv, sessionId) {
  const data = await kv.get(`session:${sessionId}`);
  return data ? JSON.parse(data) : null;
}

export async function setSession(kv, sessionId, userData) {
  await kv.put(`session:${sessionId}`, JSON.stringify({ ...userData, createdAt: Date.now() }), {
    expirationTtl: SESSION_TTL
  });
}

export async function deleteSession(kv, sessionId) {
  await kv.delete(`session:${sessionId}`);
}
```

## 四、Cookie 安全属性

```javascript
// Edge Middleware 中签发 Cookie
new Response(body, {
  headers: {
    'Set-Cookie': [
      `access_token=${token}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=900`,
      `refresh_token=${rt}; HttpOnly; Secure; SameSite=Strict; Path=/api/auth/refresh; Max-Age=604800`
    ].join(', ')
  }
});
```

## 五、RT 轮换（version 乐观锁）

```javascript
// edge-functions/api/auth/refresh.js
// 见 SKILL.md 主文件完整实现
// 核心：KV.put 在 version 不匹配时返回 false → 返回 409 → 客户端重试
```

## 六、skipAuthPaths 白名单

```javascript
const skipAuthPaths = [
  '/api/auth/login',
  '/api/auth/register',
  '/api/auth/refresh',
  '/api/products',
  '/api/products/list',
  '/api/products/categories',
  '/api/products/[id]',
  '/api/ai/chat',
  '/api/pay/wx-notify',
  '/api/pay/ali-notify',
];
```

## 七、前端 AuthService（内存模式）

```javascript
// client/src/services/auth.js
let _currentUser = null;

export const AuthService = {
  async getCurrentUser() {
    if (_currentUser) return _currentUser;
    const res = await fetch('/api/auth/me', { credentials: 'include' });
    if (!res.ok) return null;
    _currentUser = await res.json();
    return _currentUser;
  },
  setUser(user) { _currentUser = user; },
  clearUser() { _currentUser = null; },
  isLoggedIn() { return !!_currentUser; },
  onAuthChange(callback) {
    window.addEventListener('auth:changed', (e) => callback(e.detail));
  }
};

window.dispatchEvent(new CustomEvent('auth:changed', { detail: user }));
```
