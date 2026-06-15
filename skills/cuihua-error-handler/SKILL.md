---
name: cuihua-error-handler
description: |
  🛡️ AI-powered error handling assistant that transforms fragile code into resilient systems.
  Automatically generate comprehensive error handling, recovery strategies, and graceful degradation.
  
  Because every production system deserves bulletproof error handling.

metadata:
  openclaw:
    requires:
      bins:
        - node
      env: []
    primaryEnv: null
  
  version: "1.0.0"
  author: "翠花 (Cuihua) - ClawHub Pioneer"
  license: "MIT"
  tags:
    - error-handling
    - resilience
    - reliability
    - fault-tolerance
    - try-catch
    - exception-handling
    - error-recovery
    - production-ready
  
  capabilities:
    - Automatic try/catch generation
    - Smart error type detection
    - Recovery strategy suggestions
    - Circuit breaker patterns
    - Retry logic with exponential backoff
    - Fallback mechanisms
    - Error logging best practices
    - Error coverage analysis
---

# cuihua-error-handler - Bulletproof Your Code 🛡️

> **Turn fragile code into production-ready, resilient systems.**

An intelligent error handling assistant that automatically:
- 🔍 **Detects** missing error handling
- ✨ **Generates** comprehensive try/catch blocks
- 🔄 **Implements** recovery strategies (retry, fallback, circuit breaker)
- 📊 **Reports** error handling coverage
- 🛡️ **Prevents** silent failures and crashes

## 🎯 Why cuihua-error-handler?

**The harsh reality**:
- ❌ 80% of production issues come from poor error handling
- ❌ Silent failures waste hours of debugging
- ❌ Unhandled rejections crash Node.js servers
- ❌ Generic try/catch blocks hide the real problems

**cuihua-error-handler fixes all of this.**

---

## 🚀 Quick Start

### Analyze error handling

Tell your OpenClaw agent:
> "Check error handling coverage in src/"

The agent will:
- Scan all async functions
- Detect missing try/catch blocks
- Identify swallowed errors
- Report error handling coverage

### Add error handling

> "Add error handling to getUserById in api/users.js"

The agent will:
- Analyze failure points
- Generate specific error types
- Add retry logic for network errors
- Add fallback for missing data
- Add structured logging

### Generate recovery strategies

> "Add circuit breaker to payment service"

The agent will:
- Implement circuit breaker pattern
- Add failure rate monitoring
- Generate fallback responses
- Add automatic recovery

---

## 🎨 Features

### 1. Smart Error Detection 🔍

Automatically finds missing error handling:

```javascript
// ❌ BEFORE - Fragile code
async function getUserById(id) {
  const res = await fetch(`/api/users/${id}`);
  return res.json();
}

// 🔍 DETECTED ISSUES:
// - No error handling for network failures
// - No handling for non-200 responses
// - No handling for invalid JSON
// - No logging for debugging
```

### 2. Comprehensive Error Handling ✨

Generates production-ready error handling:

```javascript
// ✅ AFTER - Bulletproof code
class UserServiceError extends Error {
  constructor(message, options = {}) {
    super(message);
    this.name = 'UserServiceError';
    this.statusCode = options.statusCode;
    this.originalError = options.cause;
  }
}

async function getUserById(id) {
  try {
    // Validation
    if (!id || typeof id !== 'string') {
      throw new UserServiceError('Invalid user ID', { statusCode: 400 });
    }

    // Network request with timeout
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);
    
    const res = await fetch(`/api/users/${id}`, {
      signal: controller.signal
    });
    
    clearTimeout(timeout);

    // HTTP error handling
    if (!res.ok) {
      if (res.status === 404) {
        throw new UserServiceError(`User ${id} not found`, { statusCode: 404 });
      }
      if (res.status >= 500) {
        throw new UserServiceError('Server error, please retry', { statusCode: 502 });
      }
      throw new UserServiceError(`HTTP ${res.status}`, { statusCode: res.status });
    }

    // JSON parsing with error handling
    let data;
    try {
      data = await res.json();
    } catch (parseError) {
      throw new UserServiceError('Invalid response format', {
        statusCode: 502,
        cause: parseError
      });
    }

    return data;

  } catch (error) {
    // Network errors (timeout, connection refused)
    if (error.name === 'AbortError') {
      logger.error('getUserById timeout', { id, timeout: 5000 });
      throw new UserServiceError('Request timeout', {
        statusCode: 504,
        cause: error
      });
    }

    if (error.message.includes('fetch failed')) {
      logger.error('getUserById network error', { id, error: error.message });
      throw new UserServiceError('Network error', {
        statusCode: 503,
        cause: error
      });
    }

    // Re-throw UserServiceError
    if (error instanceof UserServiceError) {
      logger.error('getUserById failed', { id, error: error.message });
      throw error;
    }

    // Unexpected errors
    logger.error('getUserById unexpected error', { id, error });
    throw new UserServiceError('Internal error', {
      statusCode: 500,
      cause: error
    });
  }
}
```

### 3. Retry Strategies 🔄

Smart retry with exponential backoff:

```javascript
async function retryWithBackoff(fn, options = {}) {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 10000,
    backoffFactor = 2,
    shouldRetry = (error) => true
  } = options;

  let lastError;
  let delay = initialDelay;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // Check if we should retry
      if (attempt === maxRetries || !shouldRetry(error)) {
        throw error;
      }

      // Wait before retry
      logger.warn(`Retry attempt ${attempt + 1}/${maxRetries} after ${delay}ms`, {
        error: error.message
      });

      await new Promise(resolve => setTimeout(resolve, delay));

      // Exponential backoff
      delay = Math.min(delay * backoffFactor, maxDelay);
    }
  }

  throw lastError;
}

// Usage
async function fetchUserWithRetry(id) {
  return retryWithBackoff(
    () => getUserById(id),
    {
      maxRetries: 3,
      shouldRetry: (error) => {
        // Retry on network errors and 5xx
        return error.statusCode >= 500 || error.name === 'NetworkError';
      }
    }
  );
}
```

### 4. Circuit Breaker Pattern ⚡

Prevent cascading failures:

```javascript
class CircuitBreaker {
  constructor(fn, options = {}) {
    this.fn = fn;
    this.failureThreshold = options.failureThreshold || 5;
    this.resetTimeout = options.resetTimeout || 60000;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.failureCount = 0;
    this.nextAttempt = Date.now();
  }

  async execute(...args) {
    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttempt) {
        throw new Error('Circuit breaker is OPEN');
      }
      // Try to recover
      this.state = 'HALF_OPEN';
    }

    try {
      const result = await this.fn(...args);
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  onSuccess() {
    this.failureCount = 0;
    if (this.state === 'HALF_OPEN') {
      this.state = 'CLOSED';
      logger.info('Circuit breaker recovered');
    }
  }

  onFailure() {
    this.failureCount++;
    if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN';
      this.nextAttempt = Date.now() + this.resetTimeout;
      logger.error('Circuit breaker opened', {
        failureCount: this.failureCount,
        resetTimeout: this.resetTimeout
      });
    }
  }
}

// Usage
const getUserBreaker = new CircuitBreaker(getUserById, {
  failureThreshold: 5,
  resetTimeout: 60000
});

async function fetchUserSafely(id) {
  try {
    return await getUserBreaker.execute(id);
  } catch (error) {
    if (error.message === 'Circuit breaker is OPEN') {
      // Return cached data or default
      return getCachedUser(id) || { id, name: 'Unknown', error: true };
    }
    throw error;
  }
}
```

### 5. Graceful Degradation 🎯

Fallback to cached/default data:

```javascript
async function getUserWithFallback(id) {
  try {
    // Try primary source
    return await getUserById(id);
  } catch (error) {
    logger.warn('Primary source failed, trying fallback', { id, error: error.message });

    try {
      // Try cache
      const cached = await cache.get(`user:${id}`);
      if (cached) {
        logger.info('Returned cached user', { id });
        return { ...cached, _cached: true };
      }
    } catch (cacheError) {
      logger.error('Cache also failed', { id, error: cacheError.message });
    }

    // Return default user
    logger.warn('Returning default user', { id });
    return {
      id,
      name: 'Guest User',
      _default: true,
      _error: error.message
    };
  }
}
```

### 6. Error Coverage Analysis 📊

Comprehensive coverage reporting:

```
🛡️ Error Handling Coverage Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 Files analyzed: 42
🔍 Functions analyzed: 156
  - Async functions: 89
  - Sync functions: 67

📊 Overall coverage: 68%

❌ Missing error handling (28 functions):

Critical (needs immediate attention):
  1. api/payment.js:45 - processPayment()
     Risk: High - Financial transaction
     Recommendation: Add try/catch + transaction rollback

  2. api/auth.js:23 - verifyToken()
     Risk: High - Security critical
     Recommendation: Add error handling + logging

  3. db/users.js:78 - updateUserProfile()
     Risk: Medium - Data mutation
     Recommendation: Add validation + rollback

⚠️  Weak error handling (12 functions):

  1. api/users.js:12 - getUserById()
     Issue: Generic catch block without specific handling
     Recommendation: Add error type differentiation

  2. services/email.js:34 - sendWelcomeEmail()
     Issue: Swallowed errors (empty catch block)
     Recommendation: Add logging + alerting

💡 Recommendations:
  - Add error handling to 28 unprotected functions
  - Improve 12 weak error handlers
  - Target coverage: 90%+ for production readiness
```

---

## 📋 Usage Examples

### Example 1: Protect API Route

**User**: "Add error handling to POST /api/orders"

**Agent**:
```javascript
// ✅ Generated comprehensive error handling

app.post('/api/orders', async (req, res) => {
  try {
    // Validation
    const { userId, items, paymentMethod } = req.body;
    
    if (!userId || !items || !paymentMethod) {
      return res.status(400).json({
        error: 'Missing required fields',
        required: ['userId', 'items', 'paymentMethod']
      });
    }

    if (!Array.isArray(items) || items.length === 0) {
      return res.status(400).json({
        error: 'Items must be a non-empty array'
      });
    }

    // Create order with error handling
    let order;
    try {
      order = await createOrder({ userId, items, paymentMethod });
    } catch (error) {
      if (error.code === 'INSUFFICIENT_STOCK') {
        return res.status(409).json({
          error: 'Some items are out of stock',
          unavailable: error.items
        });
      }
      throw error; // Re-throw for outer handler
    }

    // Process payment with retry
    let payment;
    try {
      payment = await retryWithBackoff(
        () => processPayment(order.id, paymentMethod),
        { maxRetries: 3 }
      );
    } catch (error) {
      // Rollback order
      await cancelOrder(order.id);
      
      if (error.code === 'PAYMENT_DECLINED') {
        return res.status(402).json({
          error: 'Payment declined',
          reason: error.reason
        });
      }
      throw error;
    }

    // Success
    res.status(201).json({
      orderId: order.id,
      paymentId: payment.id,
      status: 'confirmed'
    });

  } catch (error) {
    logger.error('Order creation failed', {
      body: req.body,
      error: error.message,
      stack: error.stack
    });

    res.status(500).json({
      error: 'Failed to create order',
      message: process.env.NODE_ENV === 'development'
        ? error.message
        : 'Please try again later'
    });
  }
});
```

### Example 2: Database Operations

**User**: "Add error handling to database queries"

**Agent**:
```javascript
class UserRepository {
  async findById(id) {
    try {
      const user = await db.query(
        'SELECT * FROM users WHERE id = $1',
        [id]
      );
      
      if (!user) {
        throw new NotFoundError(`User ${id} not found`);
      }
      
      return user;
    } catch (error) {
      if (error instanceof NotFoundError) {
        throw error;
      }
      
      logger.error('Database query failed', {
        method: 'findById',
        id,
        error: error.message
      });
      
      throw new DatabaseError('Failed to fetch user', { cause: error });
    }
  }

  async update(id, data) {
    const client = await db.getClient();
    
    try {
      await client.query('BEGIN');
      
      const result = await client.query(
        'UPDATE users SET name = $1, email = $2 WHERE id = $3 RETURNING *',
        [data.name, data.email, id]
      );
      
      if (result.rowCount === 0) {
        throw new NotFoundError(`User ${id} not found`);
      }
      
      await client.query('COMMIT');
      return result.rows[0];
      
    } catch (error) {
      await client.query('ROLLBACK');
      
      if (error.code === '23505') { // Unique violation
        throw new ConflictError('Email already exists');
      }
      
      if (error instanceof NotFoundError) {
        throw error;
      }
      
      logger.error('User update failed', { id, data, error: error.message });
      throw new DatabaseError('Failed to update user', { cause: error });
      
    } finally {
      client.release();
    }
  }
}
```

### Example 3: External API Calls

**User**: "Add resilience to third-party API calls"

**Agent**:
```javascript
class WeatherAPI {
  constructor() {
    this.breaker = new CircuitBreaker(this._fetch.bind(this), {
      failureThreshold: 5,
      resetTimeout: 60000
    });
    this.cache = new Map();
  }

  async getWeather(city) {
    // Try cache first
    const cached = this.cache.get(city);
    if (cached && Date.now() - cached.timestamp < 300000) { // 5 min cache
      logger.info('Returning cached weather', { city });
      return cached.data;
    }

    try {
      // Call with circuit breaker
      const data = await this.breaker.execute(city);
      
      // Update cache
      this.cache.set(city, {
        data,
        timestamp: Date.now()
      });
      
      return data;
      
    } catch (error) {
      logger.error('Weather API failed', { city, error: error.message });
      
      // Return stale cache if available
      if (cached) {
        logger.warn('Returning stale cached data', { city });
        return { ...cached.data, _stale: true };
      }
      
      // Return default
      return {
        city,
        temperature: null,
        condition: 'Unknown',
        _error: error.message
      };
    }
  }

  async _fetch(city) {
    const response = await retryWithBackoff(
      () => fetch(`https://api.weather.com/v1/${city}`),
      {
        maxRetries: 3,
        shouldRetry: (error) => {
          // Don't retry client errors
          return !error.statusCode || error.statusCode >= 500;
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Weather API error: ${response.status}`);
    }

    return response.json();
  }
}
```

---

## ⚙️ Configuration

Create `.errorhandlerrc.json`:

```json
{
  "coverage": {
    "minimum": 80,
    "target": 95,
    "failOnBelow": true
  },
  "patterns": {
    "enableRetry": true,
    "enableCircuitBreaker": true,
    "enableFallback": true,
    "maxRetries": 3,
    "retryDelay": 1000
  },
  "logging": {
    "logLevel": "error",
    "includeStack": true,
    "structuredLogging": true
  },
  "customErrors": {
    "baseClass": "AppError",
    "errorTypes": [
      "ValidationError",
      "NotFoundError",
      "UnauthorizedError",
      "ForbiddenError"
    ]
  }
}
```

---

## 🔒 Error Types

### Built-in Error Types

```javascript
// Base error class
class AppError extends Error {
  constructor(message, options = {}) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = options.statusCode || 500;
    this.code = options.code;
    this.originalError = options.cause;
  }
}

// Domain-specific errors
class ValidationError extends AppError {
  constructor(message, fields) {
    super(message, { statusCode: 400 });
    this.fields = fields;
  }
}

class NotFoundError extends AppError {
  constructor(resource) {
    super(`${resource} not found`, { statusCode: 404 });
    this.resource = resource;
  }
}

class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized') {
    super(message, { statusCode: 401 });
  }
}

class ConflictError extends AppError {
  constructor(message) {
    super(message, { statusCode: 409 });
  }
}

class ServiceUnavailableError extends AppError {
  constructor(service) {
    super(`${service} is temporarily unavailable`, { statusCode: 503 });
    this.service = service;
  }
}
```

---

## 💰 Pricing

### Free Tier
- ✅ Error coverage analysis
- ✅ Basic try/catch generation
- ✅ Up to 10 files per project

### Pro ($10/month)
- ✅ Unlimited files
- ✅ Advanced patterns (retry, circuit breaker)
- ✅ Custom error types
- ✅ CI/CD integration
- ✅ Priority support

### Enterprise ($79/month)
- ✅ Everything in Pro
- ✅ Team error handling policies
- ✅ Error monitoring integration
- ✅ Custom recovery strategies
- ✅ SLA support

---

## 📚 Resources

- 📖 [Full Documentation](./docs/README.md)
- 🎓 [Error Handling Best Practices](./docs/best-practices.md)
- 💬 [Discord Community](https://discord.gg/clawd)
- 🐛 [Report Issues](https://github.com/cuihua/error-handler/issues)

---

## 📜 License

MIT License - see [LICENSE](./LICENSE) for details.

---

## 🙏 Acknowledgments

Built with 🌸 by 翠花 (Cuihua) for the OpenClaw community.

Because production systems deserve bulletproof error handling.

---

**Made with 🌸 | Cuihua Series | ClawHub Pioneer**

_Transform fragile code into resilient systems._
