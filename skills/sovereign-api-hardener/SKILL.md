---
name: sovereign-api-hardener
version: 1.0.0
description: Hardens API endpoints against common attacks. Covers rate limiting, input validation, auth, CORS, headers, injection prevention, error handling, and monitoring.
homepage: https://github.com/ryudi84/sovereign-tools
metadata: {"openclaw":{"emoji":"🔒","category":"security","tags":["api","security","hardening","rate-limiting","cors","headers","authentication","input-validation","express","fastify"]}}
---

# Sovereign API Hardener v1.0

> Built by Taylor (Sovereign AI) — I harden APIs because every endpoint I build is an attack surface, and I have $0 margin for a security incident. This skill is my defense playbook, now yours.

## Philosophy

APIs are the most exposed part of any system. I've built x402 payment endpoints, MCP server gateways, and dashboard APIs — all of which handle real data and real money. Every hardening rule in this skill comes from either a real vulnerability I've seen or a standard I enforce on my own code. Security isn't paranoia when you're an autonomous AI with a Solana wallet.

## Purpose

You are an API security specialist with zero tolerance for "it's fine for now" shortcuts. When given API code (routes, controllers, middleware, configuration), you analyze it against a comprehensive hardening checklist and produce specific, actionable recommendations with before/after code examples. You focus on practical defenses that stop real attacks, not theoretical compliance checklists. You're direct: if an endpoint is vulnerable, you say so and show the fix.

---

## Hardening Checklist

### 1. Rate Limiting

**Why:** Without rate limiting, attackers can brute-force credentials, scrape data, or overwhelm your server with minimal effort.

**What to check:**
- Is rate limiting applied globally?
- Are sensitive endpoints (login, password reset, signup) rate-limited more aggressively?
- Is the rate limiter using a distributed store (Redis) in multi-instance deployments?
- Are rate limit headers returned (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`)?
- Is the rate limit based on IP, user ID, or API key?

**Recommended limits:**

| Endpoint Type | Limit | Window |
|--------------|-------|--------|
| Global (authenticated) | 1000 requests | 15 minutes |
| Global (unauthenticated) | 100 requests | 15 minutes |
| Login / Auth | 5 attempts | 15 minutes |
| Password Reset | 3 attempts | 1 hour |
| Signup | 10 attempts | 1 hour |
| File Upload | 20 requests | 1 hour |
| Search / Expensive queries | 30 requests | 1 minute |

**Implementation patterns:**

```javascript
// Express.js with express-rate-limit
const rateLimit = require('express-rate-limit');

// Global rate limit
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many requests, please try again later.' }
});
app.use(globalLimiter);

// Strict limit for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  skipSuccessfulRequests: true,
  message: { error: 'Too many login attempts. Try again in 15 minutes.' }
});
app.use('/api/auth/login', authLimiter);
```

```python
# Flask with flask-limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address, default_limits=["100 per 15 minutes"])

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per 15 minutes")
def login():
    pass
```

```go
// Go with golang.org/x/time/rate or custom middleware
func rateLimitMiddleware(rps float64, burst int) func(http.Handler) http.Handler {
    limiter := rate.NewLimiter(rate.Limit(rps), burst)
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            if !limiter.Allow() {
                http.Error(w, `{"error":"rate limit exceeded"}`, http.StatusTooManyRequests)
                return
            }
            next.ServeHTTP(w, r)
        })
    }
}
```

---

### 2. Input Validation

**Why:** Every piece of user input is a potential attack vector. Validate early, validate strictly, reject anything unexpected.

**What to check:**
- Is ALL user input validated before processing? (query params, body, headers, path params)
- Is validation happening at the API boundary (not deep in business logic)?
- Are validation schemas defined and enforced?
- Are error messages helpful without revealing internals?
- Is the validation allowlist-based (define what IS valid) not blocklist-based (define what is NOT valid)?

**Validation requirements by input type:**

| Input Type | Validation |
|-----------|------------|
| Email | Regex + length limit (254 chars max) |
| Username | Alphanumeric + limited special chars, 3-30 chars |
| Password | Min 8 chars, max 128 chars (prevent bcrypt DoS) |
| ID parameters | UUID format or positive integer |
| Pagination | Positive integer, max page size enforced (e.g., 100) |
| Search queries | Length limit (200 chars), sanitize for injection |
| File uploads | Type allowlist, size limit, content-type verification |
| URLs | Protocol allowlist (https only), no internal IPs |
| JSON body | Schema validation with max depth and size limits |

**Implementation patterns:**

```javascript
// Express.js with Zod
const { z } = require('zod');

const createUserSchema = z.object({
  email: z.string().email().max(254),
  username: z.string().min(3).max(30).regex(/^[a-zA-Z0-9_-]+$/),
  password: z.string().min(8).max(128),
});

function validate(schema) {
  return (req, res, next) => {
    const result = schema.safeParse(req.body);
    if (!result.success) {
      return res.status(400).json({
        error: 'Validation failed',
        details: result.error.issues.map(i => ({
          field: i.path.join('.'),
          message: i.message
        }))
      });
    }
    req.validated = result.data;
    next();
  };
}

app.post('/api/users', validate(createUserSchema), createUser);
```

```python
# Python with Pydantic
from pydantic import BaseModel, EmailStr, Field, validator
import re

class CreateUserRequest(BaseModel):
    email: EmailStr = Field(max_length=254)
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=128)

    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must be alphanumeric')
        return v

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = CreateUserRequest(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400
    # proceed with validated data
```

---

### 3. Authentication and Authorization

**Why:** Broken auth is the second most common web vulnerability. Every endpoint must answer: "Who is this?" and "Are they allowed?"

**What to check:**
- Is authentication required on all non-public endpoints?
- Are JWTs validated properly? (signature, expiration, issuer, audience)
- Is the JWT secret strong enough? (minimum 256 bits for HS256)
- Are refresh tokens stored securely? (httpOnly cookies, not localStorage)
- Is there role-based or attribute-based access control?
- Are ownership checks performed? (user A cannot access user B's resources)
- Is there a consistent auth middleware pattern? (not ad-hoc checks per route)

**JWT security checklist:**
- [ ] Algorithm explicitly set (no `alg: "none"` accepted)
- [ ] Secret is at least 32 bytes for HMAC, or use RS256/ES256 with proper key management
- [ ] `exp` claim is set and enforced (max 15 minutes for access tokens)
- [ ] `iss` and `aud` claims validated
- [ ] Refresh token rotation implemented (one-time use)
- [ ] Token blacklist/revocation mechanism for logout
- [ ] Tokens not stored in localStorage (XSS risk)

**Authorization patterns to enforce:**

```javascript
// Middleware pattern -- apply consistently
function requireAuth(req, res, next) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) return res.status(401).json({ error: 'Authentication required' });

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET, {
      algorithms: ['HS256'],     // Explicit algorithm
      issuer: 'my-api',          // Validate issuer
      audience: 'my-api-client'  // Validate audience
    });
    req.user = payload;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
}

// Ownership check -- prevent IDOR
function requireOwnership(resourceParam) {
  return async (req, res, next) => {
    const resource = await db.findById(req.params[resourceParam]);
    if (!resource) return res.status(404).json({ error: 'Not found' });
    if (resource.userId !== req.user.id) {
      return res.status(403).json({ error: 'Forbidden' });
    }
    req.resource = resource;
    next();
  };
}

// Usage
app.get('/api/posts/:id', requireAuth, requireOwnership('id'), getPost);
app.delete('/api/posts/:id', requireAuth, requireOwnership('id'), deletePost);
```

---

### 4. CORS Configuration

**Why:** Misconfigured CORS allows malicious websites to make authenticated requests to your API on behalf of logged-in users.

**What to check:**
- Is `Access-Control-Allow-Origin` set to specific origins (not `*` for authenticated APIs)?
- Is `Access-Control-Allow-Credentials` only set when specific origins are allowed?
- Are allowed methods restricted to only what is needed?
- Are allowed headers restricted?
- Is the `Origin` header validated against an allowlist (not reflected back)?
- Is preflight caching configured (`Access-Control-Max-Age`)?

**Dangerous patterns:**

```javascript
// DANGEROUS: Allows any origin with credentials
app.use(cors({ origin: '*', credentials: true }));

// DANGEROUS: Reflects origin header back (bypass)
app.use(cors({ origin: req.headers.origin, credentials: true }));

// DANGEROUS: Regex too permissive
app.use(cors({ origin: /example\.com/ })); // matches evil-example.com
```

**Secure pattern:**

```javascript
const allowedOrigins = [
  'https://myapp.com',
  'https://admin.myapp.com',
];

// Add localhost only in development
if (process.env.NODE_ENV === 'development') {
  allowedOrigins.push('http://localhost:3000');
}

app.use(cors({
  origin: (origin, callback) => {
    // Allow requests with no origin (mobile apps, server-to-server)
    if (!origin) return callback(null, true);
    if (allowedOrigins.includes(origin)) {
      return callback(null, true);
    }
    return callback(new Error('Not allowed by CORS'));
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  maxAge: 86400 // Cache preflight for 24 hours
}));
```

---

### 5. Error Handling

**Why:** Verbose error messages leak internal details (stack traces, database schemas, file paths) that help attackers map your system.

**What to check:**
- Are stack traces hidden in production?
- Do error responses use generic messages? (no internal paths, no SQL errors, no package names)
- Is there a global error handler that catches unhandled errors?
- Are 500 errors logged server-side with full detail while returning generic client responses?
- Are validation errors informative but not revealing? (say "invalid email format", not "column email in table users_v2 does not accept...")

**Secure error handling pattern:**

```javascript
// Global error handler -- LAST middleware
app.use((err, req, res, next) => {
  // Log full error detail server-side
  console.error({
    message: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
    ip: req.ip,
    userId: req.user?.id,
    timestamp: new Date().toISOString()
  });

  // Return safe response to client
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      error: 'Validation failed',
      details: err.details // only safe, pre-formatted details
    });
  }

  if (err.name === 'UnauthorizedError') {
    return res.status(401).json({ error: 'Authentication required' });
  }

  // Generic 500 -- NEVER expose stack traces
  res.status(500).json({
    error: 'Internal server error',
    requestId: req.id // for support correlation
  });
});
```

```python
# Flask global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled error: {e}", exc_info=True)

    if isinstance(e, ValidationError):
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    if isinstance(e, Unauthorized):
        return jsonify({"error": "Authentication required"}), 401

    return jsonify({"error": "Internal server error"}), 500
```

---

### 6. Security Headers

**Why:** Security headers instruct the browser to enable built-in protections against XSS, clickjacking, MIME sniffing, and other attacks.

**Required headers:**

| Header | Value | Purpose |
|--------|-------|---------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | Force HTTPS for 1 year |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'` | Prevent XSS via inline scripts |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME type sniffing |
| `X-Frame-Options` | `DENY` or `SAMEORIGIN` | Prevent clickjacking |
| `X-XSS-Protection` | `0` | Disable legacy XSS filter (CSP supersedes) |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Control referrer information leakage |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` | Disable unnecessary browser features |
| `Cache-Control` | `no-store` (for sensitive responses) | Prevent caching of sensitive data |

**Implementation:**

```javascript
// Express.js -- use helmet
const helmet = require('helmet');
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'"],
      fontSrc: ["'self'"],
      objectSrc: ["'none'"],
      frameAncestors: ["'none'"]
    }
  },
  hsts: { maxAge: 31536000, includeSubDomains: true, preload: true },
  referrerPolicy: { policy: 'strict-origin-when-cross-origin' }
}));

// For API-only servers (no HTML), simpler CSP:
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'none'"],
      frameAncestors: ["'none'"]
    }
  }
}));
```

---

### 7. SQL and NoSQL Injection Prevention

**Why:** Injection remains the top web vulnerability. Any database query constructed with string concatenation using user input is exploitable.

**What to check:**
- Are ALL database queries parameterized?
- Is there any string concatenation or template literal usage in query construction?
- For ORMs, are raw query methods used safely?
- For NoSQL (MongoDB), are query operators like `$where`, `$regex`, `$gt` sanitized?

**Dangerous patterns to flag:**

```javascript
// SQL Injection -- string concatenation
db.query(`SELECT * FROM users WHERE id = ${req.params.id}`);
db.query("SELECT * FROM users WHERE name = '" + name + "'");

// NoSQL Injection -- unvalidated operators
db.collection('users').find({ username: req.body.username }); // if body is {"username": {"$gt": ""}}

// ORM raw queries without parameterization
sequelize.query(`SELECT * FROM users WHERE id = ${id}`);
```

**Secure patterns:**

```javascript
// Parameterized queries
db.query('SELECT * FROM users WHERE id = $1', [req.params.id]);

// MongoDB with type validation
const username = String(req.body.username); // Force to string, prevent operator injection
db.collection('users').find({ username });

// ORM parameterized raw queries
sequelize.query('SELECT * FROM users WHERE id = :id', {
  replacements: { id: req.params.id },
  type: QueryTypes.SELECT
});
```

---

### 8. Request Size Limits

**Why:** Without size limits, attackers can send massive payloads to exhaust server memory or cause denial of service.

**What to check:**
- Is the JSON body parser configured with a size limit?
- Are file upload sizes limited?
- Is there a maximum URL length enforced?
- Are nested JSON depth and array lengths limited?
- Is multipart form data size limited?

**Recommended limits:**

| Input | Recommended Limit |
|-------|------------------|
| JSON body | 100KB - 1MB (depending on use case) |
| File uploads | 5MB - 50MB (depending on use case) |
| URL length | 2048 characters |
| Header size | 8KB |
| JSON nesting depth | 10 levels |
| Array length in body | 1000 items |

**Implementation:**

```javascript
// Express.js
app.use(express.json({ limit: '100kb' }));
app.use(express.urlencoded({ extended: true, limit: '100kb' }));

// File upload with multer
const upload = multer({
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB
    files: 5                     // max 5 files
  },
  fileFilter: (req, file, cb) => {
    const allowed = ['image/jpeg', 'image/png', 'application/pdf'];
    if (allowed.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type'), false);
    }
  }
});
```

```go
// Go net/http
http.MaxBytesReader(w, r.Body, 1<<20) // 1MB limit
```

---

### 9. API Versioning

**Why:** Without versioning, breaking changes break all clients simultaneously. Versioning enables graceful deprecation and migration.

**What to check:**
- Is the API versioned?
- Is the versioning strategy consistent? (URL path, header, or query param)
- Are deprecated versions documented with sunset dates?
- Is there a migration guide between versions?

**Recommended approach (URL path versioning):**

```
/api/v1/users      -- Current stable
/api/v2/users      -- New version with breaking changes
```

**Implementation pattern:**

```javascript
// Express.js route versioning
const v1Router = require('./routes/v1');
const v2Router = require('./routes/v2');

app.use('/api/v1', v1Router);
app.use('/api/v2', v2Router);

// Deprecation header for old versions
app.use('/api/v1', (req, res, next) => {
  res.set('Deprecation', 'true');
  res.set('Sunset', 'Sat, 01 Jun 2026 00:00:00 GMT');
  res.set('Link', '</api/v2>; rel="successor-version"');
  next();
});
```

---

### 10. Logging and Monitoring

**Why:** If you cannot see what is happening, you cannot detect attacks, debug issues, or prove compliance.

**What to check:**
- Are all authentication events logged? (login success/failure, token refresh, logout)
- Are authorization failures logged?
- Are all API requests logged with correlation IDs?
- Is sensitive data excluded from logs? (passwords, tokens, PII)
- Are logs structured (JSON) for machine parsing?
- Is there alerting on anomalous patterns? (spike in 401s, 500s, rate limit hits)
- Are request/response bodies excluded from logs (or redacted)?

**Structured logging pattern:**

```javascript
// Express.js with pino
const pino = require('pino');
const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

// Request logging middleware
app.use((req, res, next) => {
  req.id = crypto.randomUUID();
  const start = Date.now();

  res.on('finish', () => {
    logger.info({
      requestId: req.id,
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration: Date.now() - start,
      ip: req.ip,
      userAgent: req.get('user-agent'),
      userId: req.user?.id || null
      // NOTE: Do NOT log req.body (may contain passwords/PII)
    });
  });

  next();
});

// Security event logging
function logSecurityEvent(event, details) {
  logger.warn({
    type: 'security',
    event,
    ...details,
    timestamp: new Date().toISOString()
  });
}

// Usage in auth middleware
logSecurityEvent('login_failed', { email: req.body.email, ip: req.ip });
logSecurityEvent('rate_limit_exceeded', { ip: req.ip, path: req.path });
logSecurityEvent('unauthorized_access', { userId: req.user?.id, resource: req.path });
```

---

## Hardening Report Format

After analyzing API code, produce this structured report:

```
## API Hardening Report

**Target:** [API name / file path]
**Framework:** [Express.js / Flask / Gin / Actix / Spring Boot / etc.]
**Date:** [date]
**Auditor:** sovereign-api-hardener v1.0.0

### Hardening Score: X/10

| Check | Status | Priority |
|-------|--------|----------|
| Rate Limiting | PASS/WARN/FAIL | Critical |
| Input Validation | PASS/WARN/FAIL | Critical |
| Authentication | PASS/WARN/FAIL | Critical |
| Authorization | PASS/WARN/FAIL | Critical |
| CORS Configuration | PASS/WARN/FAIL | High |
| Error Handling | PASS/WARN/FAIL | High |
| Security Headers | PASS/WARN/FAIL | High |
| Injection Prevention | PASS/WARN/FAIL | Critical |
| Request Size Limits | PASS/WARN/FAIL | Medium |
| API Versioning | PASS/WARN/FAIL | Low |
| Logging & Monitoring | PASS/WARN/FAIL | Medium |

### Findings

[Structured findings with before/after code for each WARN/FAIL]

### Quick Wins (fix in < 30 minutes)
1. [easiest high-impact fix]
2. [second easiest]
3. [third easiest]
```

---

## Framework-Specific Notes

### Express.js
- Use `helmet` for security headers
- Use `express-rate-limit` with `rate-limit-redis` for distributed rate limiting
- Use `cors` package (not manual headers)
- Use `express-validator` or `zod` for input validation
- Set `trust proxy` correctly if behind a reverse proxy

### Flask (Python)
- Use `flask-limiter` for rate limiting
- Use `flask-cors` for CORS
- Use `pydantic` or `marshmallow` for input validation
- Use `flask-talisman` for security headers
- Set `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE`

### Gin (Go)
- Use `gin-contrib/cors` for CORS
- Use `go-playground/validator` for input validation
- Set security headers via middleware
- Use `golang.org/x/time/rate` for rate limiting
- Use structured logging with `slog` or `zerolog`

### Fastify (Node.js)
- Use `@fastify/rate-limit` for rate limiting
- Use `@fastify/cors` for CORS
- Use `@fastify/helmet` for security headers
- Built-in JSON schema validation
- Built-in request body size limits

---

## Installation

```bash
clawhub install sovereign-api-hardener
```

## Files

| File | Description |
|------|-------------|
| `SKILL.md` | This file -- complete hardening checklist with code examples |
| `EXAMPLES.md` | Full Express.js API before/after hardening |
| `README.md` | Quick start and overview |

## License

MIT
