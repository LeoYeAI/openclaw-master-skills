---
name: sql-query-generator
description: Generate secure SQL queries with validation, pagination helpers, risk analysis, and audit-focused safeguards.
version: 0.3.0
---

# SQL Query Generator Skill

## Overview
This skill enables AI agents to generate accurate, optimized SQL queries from natural language descriptions. It supports multiple database systems and follows best practices for query construction, security, and performance.

## Installation

### Method 1: Direct Download
```bash
# Clone or download the repository
git clone https://github.com/yourusername/sql-query-generator.git
cd sql-query-generator

# No external dependencies required for core functionality
python sql_query_generator.py
```

### Method 2: Using as a Module
```bash
# Copy sql_query_generator.py to your project
cp sql_query_generator.py /path/to/your/project/

# Import in your code
from sql_query_generator import SQLQueryGenerator, DatabaseType
```

### Method 3: AI Agent Integration
For AI agents using this skill:
1. Read this SKILL.md file completely before generating queries
2. Follow all security guidelines strictly
3. Always use parameterized queries
4. Validate all inputs before query generation
5. Include security warnings in responses

### Optional Database Drivers
Install only the drivers you need:

```bash
# PostgreSQL
pip install psycopg2-binary

# MySQL
pip install mysql-connector-python

# SQL Server
pip install pyodbc

# Oracle
pip install cx_Oracle

# For testing and development
pip install pytest pytest-cov
```

### System Requirements
- Python 3.7 or higher
- No external dependencies for core query generation
- Database drivers only needed for actual query execution

## Supported Database Systems
- PostgreSQL
- MySQL
- SQLite
- Microsoft SQL Server
- Oracle Database
- MariaDB

## Core Capabilities

### 1. Query Generation
- **SELECT Queries**: Simple and complex data retrieval
- **JOIN Operations**: INNER, LEFT, RIGHT, FULL OUTER, CROSS
- **Aggregations**: GROUP BY, HAVING, aggregate functions
- **Subqueries**: Correlated and non-correlated
- **CTEs**: Common Table Expressions (WITH clause)
- **Window Functions**: OVER, PARTITION BY, ROW_NUMBER, RANK
- **INSERT/UPDATE/DELETE**: Data manipulation queries
- **DDL**: CREATE, ALTER, DROP statements

### 2. Query Optimization
- Index usage recommendations
- Query execution plan analysis
- Performance optimization suggestions
- Avoiding N+1 query problems

### 3. Security Features
- SQL injection prevention
- Parameterized query generation
- Input validation patterns
- Role-based access control patterns

## Usage Instructions

### Basic Query Generation

When generating SQL queries, follow these steps:

1. **Understand the Request**
   - Parse natural language input
   - Identify required tables
   - Determine join conditions
   - Extract filter criteria

2. **Generate Base Query**
   ```sql
   -- Example structure
   SELECT 
       column1,
       column2,
       aggregate_function(column3) AS alias
   FROM 
       table1
   JOIN 
       table2 ON table1.id = table2.foreign_id
   WHERE 
       condition1 = value1
       AND condition2 > value2
   GROUP BY 
       column1, column2
   HAVING 
       aggregate_condition
   ORDER BY 
       column1 DESC
   LIMIT 100;
   ```

3. **Apply Security Measures**
   - Use parameterized queries
   - Validate all inputs
   - Escape special characters

### Query Patterns

#### Pattern 1: Simple SELECT
```sql
-- Natural language: "Get all users who registered after January 1, 2024"
SELECT 
    id,
    username,
    email,
    registration_date
FROM 
    users
WHERE 
    registration_date > $1  -- Parameterized
ORDER BY 
    registration_date DESC;
```

#### Pattern 2: JOIN with Aggregation
```sql
-- Natural language: "Show total orders by customer in 2024"
SELECT 
    c.customer_name,
    c.email,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_spent
FROM 
    customers c
INNER JOIN 
    orders o ON c.customer_id = o.customer_id
WHERE 
    EXTRACT(YEAR FROM o.order_date) = $1
GROUP BY 
    c.customer_id,
    c.customer_name,
    c.email
HAVING 
    COUNT(o.order_id) > 5
ORDER BY 
    total_spent DESC;
```

#### Pattern 3: Subquery
```sql
-- Natural language: "Find products with above-average prices"
SELECT 
    product_name,
    price,
    category
FROM 
    products
WHERE 
    price > (
        SELECT AVG(price)
        FROM products
    )
ORDER BY 
    price DESC;
```

#### Pattern 4: CTE (Common Table Expression)
```sql
-- Natural language: "Get top 3 products per category by sales"
WITH product_sales AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category_id,
        c.category_name,
        SUM(oi.quantity * oi.unit_price) AS total_sales,
        ROW_NUMBER() OVER (
            PARTITION BY p.category_id 
            ORDER BY SUM(oi.quantity * oi.unit_price) DESC
        ) AS rank_in_category
    FROM 
        products p
    JOIN 
        order_items oi ON p.product_id = oi.product_id
    JOIN 
        categories c ON p.category_id = c.category_id
    GROUP BY 
        p.product_id,
        p.product_name,
        p.category_id,
        c.category_name
)
SELECT 
    category_name,
    product_name,
    total_sales,
    rank_in_category
FROM 
    product_sales
WHERE 
    rank_in_category <= 3
ORDER BY 
    category_name,
    rank_in_category;
```

#### Pattern 5: Window Functions
```sql
-- Natural language: "Show running total of sales per day"
SELECT 
    sale_date,
    daily_total,
    SUM(daily_total) OVER (
        ORDER BY sale_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total,
    AVG(daily_total) OVER (
        ORDER BY sale_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_average_7days
FROM (
    SELECT 
        DATE(order_date) AS sale_date,
        SUM(total_amount) AS daily_total
    FROM 
        orders
    GROUP BY 
        DATE(order_date)
) daily_sales
ORDER BY 
    sale_date;
```

## Best Practices

### 1. Query Structure
- Always use explicit column names (avoid SELECT *)
- Use meaningful table aliases
- Indent for readability
- Comment complex logic

### 2. Performance
- Create appropriate indexes
- Avoid SELECT DISTINCT when possible (use GROUP BY instead)
- Use EXISTS instead of IN for large datasets
- Limit result sets when appropriate
- Use EXPLAIN to analyze query plans

### 3. Security (CRITICAL)

#### 3.1 MANDATORY Security Rules
**THESE RULES ARE NON-NEGOTIABLE AND MUST ALWAYS BE FOLLOWED:**

1. **NEVER CONCATENATE USER INPUT INTO SQL**
   ```python
   # WRONG - CRITICAL SECURITY VULNERABILITY
   query = f"SELECT * FROM users WHERE username = '{user_input}'"
   
   # CORRECT - Always use parameters
   query = "SELECT * FROM users WHERE username = %s"
   cursor.execute(query, (user_input,))
   ```

2. **ALL VALUES MUST BE PARAMETERIZED**
   - Even seemingly "safe" values like numbers
   - Even values from "trusted" sources
   - Even internal application values
   - NO EXCEPTIONS

3. **VALIDATE AND SANITIZE ALL INPUTS**
   ```python
   # Whitelist validation
   VALID_STATUSES = ['active', 'inactive', 'pending']
   if status not in VALID_STATUSES:
       raise ValueError("Invalid status")
   
   # Type validation
   if not isinstance(user_id, int):
       raise TypeError("user_id must be integer")
   
   # Length validation
   if len(username) > 50:
       raise ValueError("username too long")
   ```

4. **ESCAPE DYNAMIC IDENTIFIERS PROPERLY**
   ```python
   from psycopg2 import sql
   
   # For table/column names that must be dynamic
   query = sql.SQL("SELECT * FROM {} WHERE id = %s").format(
       sql.Identifier(table_name)
   )
   cursor.execute(query, (user_id,))
   ```

#### 3.2 Input Validation Framework
```python
import re
from typing import Any, List, Optional

class SQLInputValidator:
    """Comprehensive input validation for SQL queries"""
    
    @staticmethod
    def validate_identifier(identifier: str, max_length: int = 63) -> str:
        """Validate table/column names"""
        # Check length
        if len(identifier) > max_length:
            raise ValueError(f"Identifier too long: {len(identifier)} > {max_length}")
        
        # Only alphanumeric and underscore
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
            raise ValueError(f"Invalid identifier: {identifier}")
        
        # Prevent SQL keywords as identifiers
        SQL_KEYWORDS = {
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
            'ALTER', 'TRUNCATE', 'UNION', 'JOIN', 'WHERE', 'FROM'
        }
        if identifier.upper() in SQL_KEYWORDS:
            raise ValueError(f"SQL keyword not allowed: {identifier}")
        
        return identifier
    
    @staticmethod
    def validate_integer(value: Any, min_val: Optional[int] = None, 
                        max_val: Optional[int] = None) -> int:
        """Validate integer values"""
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid integer: {value}")
        
        if min_val is not None and int_value < min_val:
            raise ValueError(f"Value {int_value} below minimum {min_val}")
        
        if max_val is not None and int_value > max_val:
            raise ValueError(f"Value {int_value} above maximum {max_val}")
        
        return int_value
    
    @staticmethod
    def validate_string(value: str, max_length: int = 255, 
                       allow_empty: bool = False) -> str:
        """Validate string values"""
        if not isinstance(value, str):
            raise TypeError("Value must be string")
        
        if not allow_empty and len(value) == 0:
            raise ValueError("Empty string not allowed")
        
        if len(value) > max_length:
            raise ValueError(f"String too long: {len(value)} > {max_length}")
        
        # Check for null bytes
        if '\x00' in value:
            raise ValueError("Null bytes not allowed in string")
        
        return value
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        email = SQLInputValidator.validate_string(email, max_length=254)
        
        # Basic email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError(f"Invalid email format: {email}")
        
        return email
    
    @staticmethod
    def validate_date(date_str: str) -> str:
        """Validate date format (YYYY-MM-DD)"""
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            raise ValueError(f"Invalid date format: {date_str}")
        
        return date_str
    
    @staticmethod
    def validate_enum(value: str, allowed_values: List[str]) -> str:
        """Validate value against whitelist"""
        if value not in allowed_values:
            raise ValueError(f"Invalid value: {value}. Allowed: {allowed_values}")
        
        return value
```

#### 3.3 SQL Injection Attack Patterns to Prevent
```python
# Detect common SQL injection patterns
INJECTION_PATTERNS = [
    r"('|(\\')|(--)|(\#)|(%23)|(;))",  # Basic SQL injection
    r"((\%27)|(\'))",                   # Single quote variations
    r"(union.*select)",                 # UNION-based injection
    r"(insert.*into)",                  # INSERT injection
    r"(update.*set)",                   # UPDATE injection
    r"(delete.*from)",                  # DELETE injection
    r"(drop.*table)",                   # DROP TABLE
    r"(exec(\s|\+)+(s|x)p\w+)",        # Stored procedure execution
    r"(script.*>)",                     # XSS attempts
]

def detect_injection_attempt(value: str) -> bool:
    """Detect potential SQL injection attempts"""
    value_lower = value.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, value_lower):
            return True
    return False
```

#### 3.4 Secure Query Builder
```python
class SecureQueryBuilder:
    """Build SQL queries with mandatory security checks"""
    
    def __init__(self, db_type: DatabaseType):
        self.db_type = db_type
        self.validator = SQLInputValidator()
        self.params = []
    
    def build_select(self, table: str, columns: List[str], 
                    conditions: dict) -> tuple:
        """Build SELECT query with validation"""
        # Validate table name
        table = self.validator.validate_identifier(table)
        
        # Validate columns
        validated_columns = [
            self.validator.validate_identifier(col) 
            for col in columns
        ]
        
        # Build query
        query = f"SELECT {', '.join(validated_columns)} FROM {table}"
        
        # Add WHERE clause with parameters
        if conditions:
            where_parts = []
            for key, value in conditions.items():
                key = self.validator.validate_identifier(key)
                where_parts.append(f"{key} = %s")
                self.params.append(value)
            
            query += " WHERE " + " AND ".join(where_parts)
        
        return query, tuple(self.params)
```

#### 3.5 Database Connection Security
```python
import ssl
from typing import Optional

class SecureConnection:
    """Secure database connection configuration"""
    
    @staticmethod
    def get_postgresql_ssl_config() -> dict:
        """PostgreSQL SSL configuration"""
        return {
            'sslmode': 'require',  # or 'verify-full' for production
            'sslrootcert': '/path/to/ca-cert.pem',
            'sslcert': '/path/to/client-cert.pem',
            'sslkey': '/path/to/client-key.pem'
        }
    
    @staticmethod
    def get_connection_timeout() -> dict:
        """Connection timeout settings"""
        return {
            'connect_timeout': 10,
            'command_timeout': 30,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5
        }
    
    @staticmethod
    def create_secure_connection(database_url: str) -> Any:
        """Create connection with security settings"""
        import psycopg2
        
        # Parse connection string securely
        # NEVER log the connection string (contains credentials)
        
        conn = psycopg2.connect(
            database_url,
            **SecureConnection.get_postgresql_ssl_config(),
            **SecureConnection.get_connection_timeout()
        )
        
        # Set session security parameters
        cursor = conn.cursor()
        cursor.execute("SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        cursor.execute("SET statement_timeout = 30000")  # 30 seconds
        cursor.close()
        
        return conn
```

#### 3.6 Rate Limiting
```python
import time
from collections import defaultdict
from threading import Lock

class RateLimiter:
    """Prevent query flooding attacks"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed"""
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds
            
            # Clean old requests
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
            
            # Check limit
            if len(self.requests[identifier]) >= self.max_requests:
                return False
            
            # Add new request
            self.requests[identifier].append(now)
            return True
```

#### 3.7 Audit Logging
```python
import logging
import json
from datetime import datetime
from typing import Any, Dict

class SecurityAuditLogger:
    """Log all database operations for security auditing"""
    
    def __init__(self, log_file: str = '/var/log/sql_audit.log'):
        self.logger = logging.getLogger('sql_audit')
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_query(self, query: str, params: tuple, user_id: str,
                  ip_address: str, result_count: int = None):
        """Log query execution"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'ip_address': ip_address,
            'query': query,
            'param_count': len(params),
            'result_count': result_count
        }
        self.logger.info(json.dumps(log_entry))
    
    def log_security_event(self, event_type: str, details: Dict[str, Any],
                          severity: str = 'WARNING'):
        """Log security events"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'details': details
        }
        
        if severity == 'CRITICAL':
            self.logger.critical(json.dumps(log_entry))
        elif severity == 'ERROR':
            self.logger.error(json.dumps(log_entry))
        else:
            self.logger.warning(json.dumps(log_entry))
```

#### 3.8 Prepared Statement Pool
```python
from typing import Dict, Any
import hashlib

class PreparedStatementPool:
    """Reuse prepared statements for better performance and security"""
    
    def __init__(self, connection):
        self.connection = connection
        self.statements: Dict[str, Any] = {}
    
    def get_statement(self, query: str):
        """Get or create prepared statement"""
        # Create hash of query for lookup
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
        
        if query_hash not in self.statements:
            # Create new prepared statement
            cursor = self.connection.cursor()
            statement_name = f"stmt_{query_hash}"
            cursor.execute(f"PREPARE {statement_name} AS {query}")
            self.statements[query_hash] = statement_name
        
        return self.statements[query_hash]
    
    def execute(self, query: str, params: tuple):
        """Execute using prepared statement"""
        stmt_name = self.get_statement(query)
        cursor = self.connection.cursor()
        param_list = ', '.join(['%s'] * len(params))
        cursor.execute(f"EXECUTE {stmt_name}({param_list})", params)
        return cursor
```

### 4. Parameterization Examples

**PostgreSQL/Python (psycopg2)**
```python
# CORRECT - Parameterized
cursor.execute(
    "SELECT * FROM users WHERE email = %s AND status = %s",
    (user_email, status)
)

# WRONG - String concatenation (SQL injection risk)
cursor.execute(
    f"SELECT * FROM users WHERE email = '{user_email}'"
)
```

**MySQL/Python (mysql-connector)**
```python
# CORRECT
cursor.execute(
    "SELECT * FROM products WHERE price > %s",
    (min_price,)
)
```

**SQLite/Python**
```python
# CORRECT
cursor.execute(
    "SELECT * FROM orders WHERE order_date > ?",
    (start_date,)
)
```

**Node.js (PostgreSQL)**
```javascript
// CORRECT
const result = await client.query(
    'SELECT * FROM users WHERE id = $1',
    [userId]
);
```

### 5. Database-Specific Syntax

**PostgreSQL**
- Use `$1, $2, $3` for parameters
- Supports advanced features: JSONB, arrays, full-text search
- Use `RETURNING` clause for INSERT/UPDATE/DELETE
- Case-sensitive text search with ILIKE

**MySQL**
- Use `?` for parameters
- LIMIT syntax: `LIMIT offset, count`
- Use backticks for identifiers with spaces
- Date functions: DATE_FORMAT, CURDATE()

**SQL Server**
- Use `@param1, @param2` for parameters
- TOP instead of LIMIT
- Use square brackets for identifiers
- Date functions: GETDATE(), DATEADD()

**SQLite**
- Use `?` for parameters
- Limited ALTER TABLE support
- No RIGHT JOIN or FULL OUTER JOIN
- Date functions as strings

## Error Handling

When generating queries, include error handling recommendations:

```python
import psycopg2
from psycopg2 import sql

try:
    cursor.execute(
        sql.SQL("SELECT * FROM {} WHERE id = %s").format(
            sql.Identifier('users')
        ),
        (user_id,)
    )
    results = cursor.fetchall()
except psycopg2.Error as e:
    print(f"Database error: {e}")
    # Log error, return appropriate response
finally:
    cursor.close()
```

## Query Validation Checklist

Before providing a query, verify:
- [ ] All table and column names are valid
- [ ] JOIN conditions are correct
- [ ] WHERE clause logic is accurate
- [ ] Parameters are used (not string concatenation)
- [ ] Appropriate indexes exist or are recommended
- [ ] Query is optimized for the expected dataset size
- [ ] Results will be properly limited if needed
- [ ] Error handling is included in implementation code

## Response Format

When responding to a query request, provide:

1. **The SQL Query** (properly formatted and commented)
2. **Explanation** of what the query does
3. **Parameters** that need to be passed
4. **Expected Result** structure
5. **Performance Notes** (if applicable)
6. **Security Warnings** (if applicable)
7. **Implementation Example** in the requested language

## Example Response Structure

```markdown
### SQL Query
```sql
-- Get active users with their order counts
SELECT 
    u.user_id,
    u.username,
    u.email,
    COUNT(o.order_id) AS order_count,
    COALESCE(SUM(o.total_amount), 0) AS lifetime_value
FROM 
    users u
LEFT JOIN 
    orders o ON u.user_id = o.user_id
WHERE 
    u.status = $1
    AND u.created_at >= $2
GROUP BY 
    u.user_id,
    u.username,
    u.email
HAVING 
    COUNT(o.order_id) >= $3
ORDER BY 
    lifetime_value DESC
LIMIT $4;
```

### Parameters
- `$1`: status (string, e.g., 'active')
- `$2`: created_at (date, e.g., '2024-01-01')
- `$3`: min_orders (integer, e.g., 5)
- `$4`: limit (integer, e.g., 100)

### Explanation
This query retrieves active users who joined after a specified date and have placed a minimum number of orders. It calculates their total order count and lifetime value, sorted by highest spending customers first.

### Expected Result
| user_id | username | email | order_count | lifetime_value |
|---------|----------|-------|-------------|----------------|
| 123 | john_doe | john@example.com | 15 | 2500.00 |

### Performance Notes
- Ensure index on `users.status` and `users.created_at`
- Ensure index on `orders.user_id`
- For large datasets, consider pagination

### Implementation Example (Python/psycopg2)
```python
cursor.execute(query, ('active', '2024-01-01', 5, 100))
results = cursor.fetchall()
```
```

## Advanced Topics

### 1. Query Optimization Techniques
- Use EXPLAIN ANALYZE to understand query plans
- Create covering indexes
- Partition large tables
- Use materialized views for complex aggregations
- Implement query result caching

### 2. Complex Scenarios
- Recursive CTEs for hierarchical data
- Pivot/Unpivot operations
- Full-text search
- Geospatial queries
- Time-series analysis

### 3. Migration Support
- Generate queries for data migration
- Schema comparison queries
- Data validation queries
- Backup and restore scripts

## Testing Recommendations

Always suggest testing generated queries with:
1. Small dataset first
2. EXPLAIN or EXPLAIN ANALYZE
3. Various edge cases (NULL values, empty sets)
4. Performance benchmarks
5. Security scanning tools

## Common Pitfalls to Avoid

1. **N+1 Query Problem**: Use JOINs instead of multiple queries
2. **SELECT ***: Specify needed columns explicitly
3. **Missing Indexes**: Recommend indexes on filter/join columns
4. **Cartesian Products**: Ensure proper JOIN conditions
5. **Implicit Type Conversions**: Cast explicitly when needed
6. **Timezone Issues**: Always use timezone-aware timestamps

## Integration Examples

### REST API
```python
from flask import Flask, request, jsonify
import psycopg2

@app.route('/api/users', methods=['GET'])
def get_users():
    status = request.args.get('status', 'active')
    
    # Validate input
    if status not in ['active', 'inactive', 'suspended']:
        return jsonify({'error': 'Invalid status'}), 400
    
    try:
        cursor.execute(
            "SELECT id, username, email FROM users WHERE status = %s",
            (status,)
        )
        users = cursor.fetchall()
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### GraphQL Resolver
```javascript
const resolvers = {
  Query: {
    users: async (_, { status, limit }, { db }) => {
      const result = await db.query(
        'SELECT * FROM users WHERE status = $1 LIMIT $2',
        [status, limit]
      );
      return result.rows;
    }
  }
};
```

## Conclusion

This skill provides comprehensive SQL query generation capabilities with a focus on security, performance, and best practices. Always prioritize parameterized queries and provide clear documentation with generated SQL.
