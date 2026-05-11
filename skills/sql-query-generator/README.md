# SQL Query Generator - Ultra Secure Edition

## 🔒 Military-Grade Security for SQL Query Generation

AI-powered SQL query generator with **100x enhanced security** features, designed to prevent SQL injection, protect sensitive data, and ensure safe database operations.

## 🛡️ Security Features

### New in latest update (v0.3.0)
- Table allowlist now enforced on **JOIN tables** too (not just primary table).
- New `generate_paginated_select_query(...)` helper:
  - strict page/page_size validation
  - safe sort column + sort direction validation
  - automatic LIMIT/OFFSET generation
- New `query_fingerprint(query)` helper for deterministic cache/audit correlation.
- Stronger log sanitization: redacts `api_key`, `token`, and `secret` patterns.
- Structured query analysis (`analyze_query`) retained for CI/automation scoring.

### Core Security Mechanisms

1. **SQL Injection Prevention**
   - Pattern-based detection (18+ injection patterns)
   - Input validation on ALL identifiers
   - Mandatory parameterized queries
   - Null byte detection
   - Hex encoding detection

2. **Input Validation**
   - Type validation (integers, strings, dates, emails)
   - Length constraints
   - Format validation (regex-based)
   - Whitelist validation for enums
   - SQL keyword blocking

3. **Rate Limiting**
   - Per-user request throttling
   - Automatic penalty system for violations
   - Configurable time windows
   - Thread-safe implementation

4. **Audit Logging**
   - Complete query history
   - Security event tracking
   - Sanitized logging (PII protection)
   - JSON-formatted logs for analysis

5. **Error Sanitization**
   - No sensitive data exposure
   - Generic error messages for users
   - Detailed logging for admins
   - Stack trace protection

6. **Data Sanitization**
   - Credit card number redaction
   - SSN redaction
   - Password redaction
   - Sensitive pattern detection

## 📊 Security Levels

```python
SecurityLevel.STRICT      # Maximum validation (RECOMMENDED)
SecurityLevel.NORMAL      # Standard validation
SecurityLevel.PERMISSIVE  # Minimal validation (NOT RECOMMENDED)
```

## 🚀 Installation

### Basic Installation

```bash
git clone https://github.com/cerbug45/sql-query-generator.git
cd sql-query-generator

# No external dependencies for core functionality
python sql_query_generator.py
```

### With Database Drivers (Optional)

```bash
# PostgreSQL
pip install psycopg2-binary

# MySQL
pip install mysql-connector-python

# SQL Server
pip install pyodbc

# Oracle
pip install cx_Oracle
```

### System Requirements

- Python 3.7+
- No external dependencies for core features
- Database drivers only for execution

## 💻 Quick Start

### Basic Usage

```python
from sql_query_generator import SQLQueryGenerator, DatabaseType, SecurityLevel

# Initialize with maximum security
generator = SQLQueryGenerator(
    DatabaseType.POSTGRESQL,
    security_level=SecurityLevel.STRICT,
    enable_audit_log=True,
    enable_rate_limit=True
)

# Generate secure query
query = generator.generate_select_query(
    tables=['users'],
    columns=['id', 'username', 'email'],
    where_conditions=['status = $1', 'created_at > $2'],
    order_by=['created_at DESC'],
    limit=100,
    user_id='john_doe'  # For rate limiting and audit
)
```

### Security Validation

```python
# Validate query for security issues
warnings = generator.validate_query_security(query, user_id='john_doe')

if warnings:
    for warning in warnings:
        print(f"⚠ {warning}")
else:
    print("✓ Query is secure")
```

### Safe Pagination Helper (new)

```python
q = generator.generate_paginated_select_query(
    table='orders',
    columns=['order_id', 'customer_id', 'created_at'],
    sort_by='created_at',
    sort_direction='DESC',
    page=2,
    page_size=25,
    where_conditions=['status = $1'],
    user_id='john_doe'
)

print(generator.query_fingerprint(q))  # e.g. '9f1a2b3c4d5e6f70'
```

### Performance Optimization

```python
# Get optimization suggestions
_, suggestions = generator.optimize_query(query)

for suggestion in suggestions:
    print(f"💡 {suggestion}")
```

## 🔐 Security Best Practices

### 1. Always Use Parameterized Queries

```python
# ✅ CORRECT - Parameterized
query = "SELECT * FROM users WHERE email = $1"
cursor.execute(query, (user_email,))

# ❌ WRONG - String concatenation (SQL INJECTION RISK!)
query = f"SELECT * FROM users WHERE email = '{user_email}'"
cursor.execute(query)
```

### 2. Validate ALL Inputs

```python
from sql_query_generator import SQLInputValidator

validator = SQLInputValidator()

# Validate identifier (table/column names)
table_name = validator.validate_identifier(user_input)

# Validate integer
limit = validator.validate_integer(user_limit, min_val=1, max_val=1000)

# Validate string
username = validator.validate_string(user_name, max_length=50)

# Validate email
email = validator.validate_email(user_email)

# Validate against whitelist
status = validator.validate_enum(user_status, ['active', 'inactive'])
```

### 3. Enable Rate Limiting

```python
generator = SQLQueryGenerator(
    enable_rate_limit=True  # Prevents abuse
)

try:
    query = generator.generate_select_query(
        tables=['users'],
        columns=['*'],
        user_id='attacker'  # Tracked for rate limiting
    )
except SecurityException as e:
    print(f"Rate limit exceeded: {e}")
```

### 4. Enable Audit Logging

```python
# All queries are logged with:
# - Timestamp
# - User ID
# - IP address (if provided)
# - Sanitized query
# - Parameter count
# - Execution results

generator = SQLQueryGenerator(
    enable_audit_log=True  # Creates sql_audit.log
)

# Logs automatically include sanitized data:
# - Credit cards → [REDACTED-CARD]
# - SSNs → [REDACTED-SSN]
# - Passwords → password=[REDACTED]
```

### 5. Handle Errors Securely

```python
try:
    cursor.execute(query, params)
except Exception as e:
    # ❌ WRONG - Exposes internal details
    print(f"Error: {e}")
    
    # ✅ CORRECT - Generic message
    print("Database operation failed. Contact administrator.")
    
    # Log detailed error for admins (sanitized)
    logger.error(f"DB error: {type(e).__name__}")
```

## 📚 Complete Examples

### Example 1: Secure User Authentication

```python
from sql_query_generator import SQLQueryGenerator, SQLInputValidator, SecurityException

validator = SQLInputValidator()
generator = SQLQueryGenerator(
    security_level=SecurityLevel.STRICT,
    enable_audit_log=True,
    enable_rate_limit=True
)

def authenticate_user(username: str, password_hash: str, ip_address: str):
    """Secure user authentication with all safety measures"""
    
    try:
        # Validate inputs
        username = validator.validate_string(username, max_length=50)
        
        # Detect injection attempts
        if validator.detect_injection_attempt(username):
            raise SecurityException("Invalid username format")
        
        # Generate secure query
        query = generator.generate_select_query(
            tables=['users'],
            columns=['user_id', 'username', 'password_hash', 'status'],
            where_conditions=['username = $1', 'status = $2'],
            limit=1,
            user_id=ip_address  # Rate limit by IP
        )
        
        # Execute with parameters (NEVER concatenate!)
        cursor.execute(query, (username, 'active'))
        result = cursor.fetchone()
        
        if result and verify_password(password_hash, result['password_hash']):
            return True
        
        return False
        
    except SecurityException as e:
        # Log security event
        logger.critical(f"Security violation: {e}")
        return False
```

### Example 2: Bulk Data Import with Validation

```python
def import_users_safely(users_data: List[Dict]):
    """Import users with comprehensive validation"""
    
    validator = SQLInputValidator()
    generator = SQLQueryGenerator()
    
    validated_users = []
    errors = []
    
    for i, user in enumerate(users_data):
        try:
            # Validate each field
            username = validator.validate_string(
                user['username'],
                max_length=50,
                check_injection=True
            )
            
            email = validator.validate_email(user['email'])
            
            age = validator.validate_integer(
                user['age'],
                min_val=18,
                max_val=120
            )
            
            validated_users.append({
                'username': username,
                'email': email,
                'age': age
            })
            
        except (ValidationException, SecurityException) as e:
            errors.append(f"Row {i}: {e}")
    
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    # Generate INSERT query
    query = generator.generate_insert_query(
        table='users',
        columns=['username', 'email', 'age'],
        returning=['user_id']
    )
    
    # Execute safely
    for user in validated_users:
        cursor.execute(
            query,
            (user['username'], user['email'], user['age'])
        )
    
    connection.commit()
    return True
```

### Example 3: Dynamic Reporting with Security

```python
def generate_sales_report(
    start_date: str,
    end_date: str,
    category: str,
    user_id: str
):
    """Generate sales report with security validation"""
    
    validator = SQLInputValidator()
    generator = SQLQueryGenerator(
        security_level=SecurityLevel.STRICT,
        enable_audit_log=True,
        enable_rate_limit=True
    )
    
    # Validate inputs
    start_date = validator.validate_date(start_date)
    end_date = validator.validate_date(end_date)
    category = validator.validate_enum(
        category,
        ['Electronics', 'Clothing', 'Food', 'Books']
    )
    
    # Generate secure query
    query = generator.generate_select_query(
        tables=['sales s'],
        columns=[
            's.sale_date',
            's.product_name',
            's.category',
            'SUM(s.amount) AS total_sales',
            'COUNT(s.sale_id) AS transaction_count'
        ],
        where_conditions=[
            's.sale_date >= $1',
            's.sale_date <= $2',
            's.category = $3'
        ],
        group_by=['s.sale_date', 's.product_name', 's.category'],
        order_by=['total_sales DESC'],
        limit=100,
        user_id=user_id
    )
    
    # Security check
    warnings = generator.validate_query_security(query, user_id)
    if any('CRITICAL' in w for w in warnings):
        raise SecurityException("Query failed security validation")
    
    # Execute safely
    cursor.execute(query, (start_date, end_date, category))
    return cursor.fetchall()
```

## 🔍 Security Validation Reference

### Detected Injection Patterns

1. Single quote variations: `'`, `\'`, `%27`
2. SQL comments: `--`, `#`, `/*`
3. UNION-based: `UNION SELECT`
4. Blind injection: `OR 1=1`, `AND 1=1`
5. Time-based: `SLEEP()`, `WAITFOR`, `BENCHMARK()`
6. Stacked queries: `;`
7. Command execution: `EXEC`, `EXECUTE`, `xp_cmdshell`
8. File operations: `LOAD_FILE`, `INTO OUTFILE`
9. Schema probing: `information_schema`
10. Encoding bypass: `0x...`, `CHAR()`
11. And many more...

### Validation Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `validate_identifier()` | Table/column names | `validate_identifier('users')` |
| `validate_integer()` | Numeric values | `validate_integer(limit, 1, 1000)` |
| `validate_string()` | Text values | `validate_string(name, 50)` |
| `validate_email()` | Email addresses | `validate_email(email)` |
| `validate_date()` | Date values | `validate_date('2024-01-01')` |
| `validate_enum()` | Whitelist values | `validate_enum(status, ['active', 'inactive'])` |
| `detect_injection_attempt()` | SQL injection | `detect_injection_attempt(input)` |

## 📊 Audit Log Format

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "user_id": "john_doe",
  "ip_address": "192.168.1.100",
  "query": "SELECT user_id, username FROM users WHERE status = $1",
  "param_count": 1,
  "result_count": 42,
  "execution_time_ms": 15.3
}
```

### Security Events Logged

- `INJECTION_ATTEMPT` - SQL injection detected
- `RATE_LIMIT_EXCEEDED` - User exceeded request limit
- `VALIDATION_FAILURE` - Input validation failed
- `SELECT_STAR_USED` - SELECT * used (warning)
- `DANGEROUS_OPERATION` - DROP, TRUNCATE, etc.

## ⚠️ Common Security Mistakes to Avoid

### 1. String Concatenation
```python
# ❌ CRITICAL VULNERABILITY
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ SECURE
query = "SELECT * FROM users WHERE id = $1"
cursor.execute(query, (user_id,))
```

### 2. Dynamic Table Names (Unsafe)
```python
# ❌ WRONG
table = input("Enter table name: ")
query = f"SELECT * FROM {table}"

# ✅ CORRECT
table = validator.validate_identifier(input("Enter table name: "))
query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table))
```

### 3. Exposing Error Details
```python
# ❌ WRONG
except Exception as e:
    return f"Error: {e}"

# ✅ CORRECT
except Exception as e:
    logger.error(f"DB error: {type(e).__name__}")
    return "Operation failed"
```

### 4. Missing Rate Limits
```python
# ❌ WRONG - No protection against abuse
def search(query):
    return db.execute(query)

# ✅ CORRECT
generator = SQLQueryGenerator(enable_rate_limit=True)
query = generator.generate_select_query(..., user_id=user_id)
```

## 📈 Performance Considerations

- Input validation adds <1ms overhead
- Rate limiting uses in-memory store (fast)
- Audit logging is asynchronous (no blocking)
- Security checks run in O(n) time

## 🤝 Contributing

We welcome contributions focused on:
- New injection pattern detection
- Additional validation methods
- Performance improvements
- Documentation enhancements

Please ensure all contributions maintain security standards.

## 📄 License

MIT License - See LICENSE file

## 🆘 Support

For security issues: security@example.com
For general questions: support@example.com

## 🔗 Resources

- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)
- [NIST Secure Coding Guidelines](https://www.nist.gov/)

## ⭐ Key Takeaways

1. **ALWAYS** use parameterized queries
2. **VALIDATE** all inputs before processing
3. **ENABLE** audit logging for compliance
4. **USE** rate limiting to prevent abuse
5. **SANITIZE** errors before showing to users
6. **TEST** queries with security validation
7. **MONITOR** audit logs for suspicious activity

---

**Remember: Security is not optional. One SQL injection can compromise your entire database.**
