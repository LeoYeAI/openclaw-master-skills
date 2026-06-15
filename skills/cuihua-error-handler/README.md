# cuihua-error-handler

🛡️ **AI-powered error handling assistant - Turn fragile code into bulletproof systems**

Automatically analyze, generate, and improve error handling in your codebase.

## Quick Start

### Check error handling coverage

```bash
node error-handler.js check ./src
```

### Generate error handling for a function

```bash
node error-handler.js generate ./api/users.js getUserById
```

## Features

- 🔍 **Analyze** error handling coverage
- ✨ **Generate** production-ready try/catch blocks
- 🔄 **Implement** retry logic with exponential backoff
- ⚡ **Add** circuit breaker patterns
- 🎯 **Create** graceful degradation
- 📊 **Report** weak and missing error handling

## Error Patterns

- ✅ Try/catch with specific error types
- ✅ Retry with exponential backoff
- ✅ Circuit breaker for external services
- ✅ Fallback mechanisms
- ✅ Structured error logging
- ✅ Transaction rollback

## Usage with OpenClaw

Tell your agent:
> "Check error handling coverage in src/"

> "Add error handling to processPayment function"

> "Add circuit breaker to API calls"

## Installation

Via ClawHub:
```bash
clawhub install cuihua-error-handler
```

## Example Output

```
🛡️ Error Handling Coverage Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 Files scanned: 42
🔍 Functions analyzed: 156

📊 Overall coverage: 68%
  ✅ With error handling: 106
  ⚠️  Weak error handling: 12
  ❌ Missing error handling: 38

❌ Critical functions without error handling:
  1. api/payment.js:45 - processPayment()
  2. api/auth.js:23 - verifyToken()
  3. db/users.js:78 - updateUserProfile()
```

## License

MIT

## Author

Made with 🌸 by 翠花 (Cuihua)

---

**Part of the Cuihua Series** | ClawHub Pioneer
