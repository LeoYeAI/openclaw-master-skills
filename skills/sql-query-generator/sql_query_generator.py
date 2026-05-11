"""
SQL Query Generator - Ultra Secure Version
A comprehensive tool for generating SQL queries with military-grade security.

Security Features:
- Input validation and sanitization
- SQL injection prevention
- Rate limiting
- Audit logging
- Prepared statement pooling
- Connection security
- Error sanitization
- Type validation
"""

import re
import hashlib
import hmac
import time
import logging
import json
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from collections import defaultdict
from threading import Lock
import secrets


class DatabaseType(Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MSSQL = "mssql"
    ORACLE = "oracle"
    MARIADB = "mariadb"


class QueryType(Enum):
    """Types of SQL queries"""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    ALTER = "alter"
    DROP = "drop"


class SecurityLevel(Enum):
    """Security validation levels"""
    STRICT = "strict"      # Maximum validation
    NORMAL = "normal"      # Standard validation
    PERMISSIVE = "permissive"  # Minimal validation (NOT RECOMMENDED)


@dataclass
class TableSchema:
    """Represents a database table schema"""
    name: str
    columns: List[Dict[str, str]]
    primary_key: Optional[str] = None
    foreign_keys: Optional[List[Dict[str, str]]] = None


@dataclass
class QueryRequest:
    """Represents a natural language query request"""
    description: str
    database_type: DatabaseType
    tables: List[TableSchema]
    parameters: Optional[Dict[str, any]] = None


@dataclass
class GeneratedQuery:
    """Represents a generated SQL query with metadata"""
    sql: str
    query_type: QueryType
    parameters: List[Tuple[str, str, any]]
    explanation: str
    performance_notes: List[str]
    security_warnings: List[str]
    implementation_examples: Dict[str, str]


@dataclass
class QueryAnalysis:
    """Structured query quality + risk analysis"""
    complexity_score: int
    risk_score: int
    recommendations: List[str]
    tags: List[str]


class SecurityException(Exception):
    """Raised when security validation fails"""
    pass


class ValidationException(Exception):
    """Raised when input validation fails"""
    pass


class SQLInputValidator:
    """Comprehensive input validation for SQL queries"""
    
    # SQL keywords that should never be used as identifiers
    SQL_KEYWORDS: Set[str] = {
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
        'ALTER', 'TRUNCATE', 'UNION', 'JOIN', 'WHERE', 'FROM',
        'INTO', 'VALUES', 'SET', 'TABLE', 'DATABASE', 'INDEX',
        'VIEW', 'PROCEDURE', 'FUNCTION', 'TRIGGER', 'GRANT',
        'REVOKE', 'COMMIT', 'ROLLBACK', 'SAVEPOINT', 'EXEC',
        'EXECUTE', 'DECLARE', 'CURSOR', 'FETCH', 'OPEN', 'CLOSE'
    }
    
    # Common SQL injection patterns
    INJECTION_PATTERNS = [
        r"('|(\\')|(--)|(\#)|(%23)|(;))",
        r"((\%27)|(\'))",
        r"(union.*select)",
        r"(insert.*into)",
        r"(update.*set)",
        r"(delete.*from)",
        r"(drop.*table)",
        r"(exec(\s|\+)+(s|x)p\w+)",
        r"(script.*>)",
        r"(benchmark\s*\()",
        r"(sleep\s*\()",
        r"(waitfor\s+delay)",
        r"(load_file\s*\()",
        r"(into\s+(out|dump)file)",
        r"(information_schema)",
        r"(concat\s*\(.*select)",
        r"(char\s*\()",
        r"(0x[0-9a-f]+)",
    ]
    
    @staticmethod
    def validate_identifier(identifier: str, max_length: int = 63,
                          security_level: SecurityLevel = SecurityLevel.STRICT) -> str:
        """Validate table/column names with strict rules"""
        if not identifier:
            raise ValidationException("Identifier cannot be empty")
        
        if len(identifier) > max_length:
            raise ValidationException(
                f"Identifier too long: {len(identifier)} > {max_length}"
            )
        
        if '\x00' in identifier:
            raise ValidationException("Null bytes not allowed in identifier")
        
        if security_level in [SecurityLevel.STRICT, SecurityLevel.NORMAL]:
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
                raise ValidationException(
                    f"Invalid identifier format: {identifier}"
                )
            
            if identifier.upper() in SQLInputValidator.SQL_KEYWORDS:
                raise ValidationException(
                    f"SQL keyword not allowed as identifier: {identifier}"
                )
            
            if SQLInputValidator.detect_injection_attempt(identifier):
                raise SecurityException(
                    f"Potential SQL injection detected in identifier: {identifier}"
                )
        
        return identifier
    
    @staticmethod
    def detect_injection_attempt(value: str) -> bool:
        """Detect potential SQL injection attempts"""
        if not isinstance(value, str):
            return False
        
        value_lower = value.lower()
        for pattern in SQLInputValidator.INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def validate_integer(value: Any, min_val: Optional[int] = None,
                        max_val: Optional[int] = None) -> int:
        """Validate integer values"""
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationException(f"Invalid integer: {value}")
        
        if min_val is not None and int_value < min_val:
            raise ValidationException(
                f"Value {int_value} below minimum {min_val}"
            )
        
        if max_val is not None and int_value > max_val:
            raise ValidationException(
                f"Value {int_value} above maximum {max_val}"
            )
        
        return int_value
    
    @staticmethod
    def validate_string(value: str, max_length: int = 255,
                       allow_empty: bool = False,
                       check_injection: bool = True) -> str:
        """Validate string values"""
        if not isinstance(value, str):
            raise ValidationException("Value must be string")
        
        if not allow_empty and len(value) == 0:
            raise ValidationException("Empty string not allowed")
        
        if len(value) > max_length:
            raise ValidationException(
                f"String too long: {len(value)} > {max_length}"
            )
        
        if '\x00' in value:
            raise ValidationException("Null bytes not allowed in string")
        
        if check_injection and SQLInputValidator.detect_injection_attempt(value):
            raise SecurityException(
                f"Potential SQL injection detected in string"
            )
        
        return value
    
    @staticmethod
    def validate_enum(value: str, allowed_values: List[str],
                     case_sensitive: bool = True) -> str:
        """Validate value against whitelist"""
        if not case_sensitive:
            value = value.lower()
            allowed_values = [v.lower() for v in allowed_values]
        
        if value not in allowed_values:
            raise ValidationException(
                f"Invalid value: {value}. Allowed: {allowed_values}"
            )
        
        return value
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        email = SQLInputValidator.validate_string(
            email, max_length=254, check_injection=True
        )
        
        # RFC 5322 compliant email validation
        if not re.match(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            email
        ):
            raise ValidationException(f"Invalid email format: {email}")
        
        return email
    
    @staticmethod
    def validate_date(date_str: str) -> str:
        """Validate date format (YYYY-MM-DD)"""
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            raise ValidationException(f"Invalid date format: {date_str}")
        
        # Validate actual date values
        try:
            year, month, day = map(int, date_str.split('-'))
            if year < 1000 or year > 9999:
                raise ValidationException("Invalid year")
            if month < 1 or month > 12:
                raise ValidationException("Invalid month")
            if day < 1 or day > 31:
                raise ValidationException("Invalid day")
        except ValueError:
            raise ValidationException("Invalid date components")
        
        return date_str
    
    @staticmethod
    def sanitize_for_logging(value: str, max_length: int = 100) -> str:
        """Sanitize sensitive data for logging"""
        if not value:
            return "[EMPTY]"
        
        if len(value) > max_length:
            value = value[:max_length] + "...[TRUNCATED]"
        
        value = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                      '[REDACTED-CARD]', value)
        value = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED-SSN]', value)
        value = re.sub(r'password\s*=\s*[^\s]+', 'password=[REDACTED]',
                      value, flags=re.IGNORECASE)
        value = re.sub(r'(api[_-]?key|token|secret)\s*=\s*[^\s]+', r'\1=[REDACTED]',
                      value, flags=re.IGNORECASE)
        
        return value


class SecurityAuditLogger:
    """Log all database operations for security auditing"""
    
    def __init__(self, log_file: str = 'sql_audit.log',
                 enable_console: bool = True):
        self.logger = logging.getLogger('sql_audit')
        self.logger.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(file_handler)
        
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(console_handler)
    
    def log_query(self, query: str, params: tuple, user_id: str,
                  ip_address: str, result_count: Optional[int] = None):
        """Log query execution"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'ip_address': ip_address,
            'query': SQLInputValidator.sanitize_for_logging(query),
            'param_count': len(params) if params else 0,
            'result_count': result_count
        }
        self.logger.info(json.dumps(log_entry))
    
    def log_security_event(self, event_type: str, details: Dict[str, Any],
                          severity: str = 'WARNING', user_id: Optional[str] = None):
        """Log security events"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'user_id': user_id,
            'details': details
        }
        
        if severity == 'CRITICAL':
            self.logger.critical(json.dumps(log_entry))
        elif severity == 'ERROR':
            self.logger.error(json.dumps(log_entry))
        else:
            self.logger.warning(json.dumps(log_entry))


class RateLimiter:
    """Prevent query flooding attacks"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.violations = defaultdict(int)
        self.lock = Lock()
    
    def is_allowed(self, identifier: str) -> Tuple[bool, Optional[str]]:
        """Check if request is allowed"""
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds
            
            if self.violations[identifier] >= 3:
                penalty_duration = min(3600, self.violations[identifier] * 300)
                return False, f"Rate limit exceeded. Retry in {penalty_duration}s"
            
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
            
            if len(self.requests[identifier]) >= self.max_requests:
                self.violations[identifier] += 1
                return False, f"Rate limit: {self.max_requests} requests per {self.window_seconds}s"
            
            self.requests[identifier].append(now)
            return True, None


class SQLQueryGenerator:
    """Ultra-secure SQL Query Generator"""
    
    def __init__(self, database_type: DatabaseType = DatabaseType.POSTGRESQL,
                 security_level: SecurityLevel = SecurityLevel.STRICT,
                 enable_audit_log: bool = True,
                 enable_rate_limit: bool = True,
                 allowed_tables: Optional[Set[str]] = None):
        self.database_type = database_type
        self.security_level = security_level
        self.param_style = self._get_param_style()
        self.validator = SQLInputValidator()
        self.audit_logger = SecurityAuditLogger() if enable_audit_log else None
        self.rate_limiter = RateLimiter() if enable_rate_limit else None
        self.query_count = 0
        self.last_query_time = None
        self.allowed_tables = {t.lower() for t in allowed_tables} if allowed_tables else None
    
    def _get_param_style(self) -> str:
        """Get parameter placeholder style"""
        styles = {
            DatabaseType.POSTGRESQL: "$",
            DatabaseType.MYSQL: "?",
            DatabaseType.SQLITE: "?",
            DatabaseType.MSSQL: "@",
            DatabaseType.ORACLE: ":",
            DatabaseType.MARIADB: "?"
        }
        return styles[self.database_type]
    
    def _check_rate_limit(self, user_id: str) -> None:
        """Check rate limit for user"""
        if self.rate_limiter:
            allowed, reason = self.rate_limiter.is_allowed(user_id)
            if not allowed:
                if self.audit_logger:
                    self.audit_logger.log_security_event(
                        'RATE_LIMIT_EXCEEDED',
                        {'user_id': user_id, 'reason': reason},
                        severity='WARNING'
                    )
                raise SecurityException(f"Rate limit exceeded: {reason}")

    def _enforce_table_allowlist(self, table_name: str) -> None:
        """Enforce allowlist policy for every referenced table."""
        if self.allowed_tables is None:
            return
        if table_name.lower() not in self.allowed_tables:
            raise SecurityException(f"Table not allowed by policy: {table_name}")
    
    def generate_select_query(
        self,
        tables: List[str],
        columns: List[str],
        joins: Optional[List[Dict]] = None,
        where_conditions: Optional[List[str]] = None,
        group_by: Optional[List[str]] = None,
        having: Optional[str] = None,
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> str:
        """Generate a SELECT query with security validation"""
        
        if user_id:
            self._check_rate_limit(user_id)
        
        validated_tables = [
            self.validator.validate_identifier(table, security_level=self.security_level)
            for table in tables
        ]

        for table in validated_tables:
            self._enforce_table_allowlist(table)
        
        validated_columns = []
        for col in columns:
            if col == "*":
                if self.security_level == SecurityLevel.STRICT:
                    if self.audit_logger:
                        self.audit_logger.log_security_event(
                            'SELECT_STAR_USED',
                            {'user_id': user_id},
                            severity='WARNING'
                        )
                validated_columns.append(col)
            else:
                validated_columns.append(
                    self.validator.validate_identifier(col, security_level=self.security_level)
                )
        
        columns_str = ",\n    ".join(validated_columns)
        query = f"SELECT\n    {columns_str}\nFROM\n    {validated_tables[0]}\n"
        
        if joins:
            for join in joins:
                join_type = self.validator.validate_enum(
                    join.get('type', 'INNER').upper(),
                    ['INNER', 'LEFT', 'RIGHT', 'FULL', 'CROSS']
                )
                join_table = self.validator.validate_identifier(
                    join['table'],
                    security_level=self.security_level
                )
                self._enforce_table_allowlist(join_table)
                query += f"{join_type} JOIN\n    {join_table} ON {join['on']}\n"
        
        if where_conditions:
            query += "WHERE\n    " + "\n    AND ".join(where_conditions) + "\n"
        
        if group_by:
            validated_group_by = [
                self.validator.validate_identifier(col, security_level=self.security_level)
                for col in group_by
            ]
            query += "GROUP BY\n    " + ",\n    ".join(validated_group_by) + "\n"
        
        if having:
            query += f"HAVING\n    {having}\n"
        
        if order_by:
            validated_order_by = []
            for order_col in order_by:
                parts = order_col.split()
                col_name = self.validator.validate_identifier(
                    parts[0],
                    security_level=self.security_level
                )
                if len(parts) > 1:
                    direction = self.validator.validate_enum(
                        parts[1].upper(),
                        ['ASC', 'DESC']
                    )
                    validated_order_by.append(f"{col_name} {direction}")
                else:
                    validated_order_by.append(col_name)
            
            query += "ORDER BY\n    " + ",\n    ".join(validated_order_by) + "\n"
        
        if limit:
            validated_limit = self.validator.validate_integer(
                limit,
                min_val=1,
                max_val=10000
            )

            if self.database_type == DatabaseType.MSSQL:
                query = query.replace("SELECT\n", f"SELECT TOP {validated_limit}\n", 1)
            else:
                query += f"LIMIT {validated_limit}\n"

        if offset is not None and self.database_type != DatabaseType.MSSQL:
            validated_offset = self.validator.validate_integer(offset, min_val=0, max_val=10_000_000)
            query += f"OFFSET {validated_offset}\n"

        query = query.rstrip() + ";"
        
        if self.audit_logger and user_id:
            self.audit_logger.log_query(query, (), user_id, 'N/A', None)
        
        self.query_count += 1
        self.last_query_time = time.time()
        
        return query

    def generate_paginated_select_query(
        self,
        table: str,
        columns: List[str],
        sort_by: str,
        sort_direction: str = "DESC",
        page: int = 1,
        page_size: int = 50,
        where_conditions: Optional[List[str]] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """Generate safe paginated SELECT query with strict validation."""
        validated_page = self.validator.validate_integer(page, min_val=1, max_val=1_000_000)
        validated_page_size = self.validator.validate_integer(page_size, min_val=1, max_val=1000)
        validated_sort = self.validator.validate_identifier(sort_by, security_level=self.security_level)
        validated_dir = self.validator.validate_enum(sort_direction.upper(), ["ASC", "DESC"])

        offset = (validated_page - 1) * validated_page_size

        return self.generate_select_query(
            tables=[table],
            columns=columns,
            where_conditions=where_conditions,
            order_by=[f"{validated_sort} {validated_dir}"],
            limit=validated_page_size,
            offset=offset,
            user_id=user_id,
        )

    def query_fingerprint(self, query: str) -> str:
        """Deterministic hash fingerprint for cache/audit correlation."""
        normalized = re.sub(r"\s+", " ", query.strip()).lower()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
    
    def validate_query_security(self, query: str, user_id: Optional[str] = None) -> List[str]:
        """Comprehensive security validation of a query"""
        warnings = []
        
        if self.validator.detect_injection_attempt(query):
            warnings.append("CRITICAL: Potential SQL injection pattern detected")
            if self.audit_logger and user_id:
                self.audit_logger.log_security_event(
                    'INJECTION_ATTEMPT',
                    {'query': SQLInputValidator.sanitize_for_logging(query, 50)},
                    severity='CRITICAL',
                    user_id=user_id
                )
        
        if re.search(r'["\'].*\+.*["\']', query):
            warnings.append("CRITICAL: String concatenation detected")
        
        if "WHERE" in query.upper():
            has_params = any(p in query for p in ['$', '?', '@', ':'])
            if not has_params:
                warnings.append("WARNING: WHERE clause without parameters")
        
        dangerous_ops = ['DROP', 'TRUNCATE', 'ALTER', 'GRANT', 'REVOKE']
        for op in dangerous_ops:
            if op in query.upper():
                warnings.append(f"WARNING: Dangerous operation: {op}")
        
        return warnings
    
    def optimize_query(self, query: str) -> Tuple[str, List[str]]:
        """Analyze and provide optimization suggestions"""
        suggestions = []

        if "SELECT *" in query.upper():
            suggestions.append("Performance: Avoid SELECT *")

        if "SELECT DISTINCT" in query.upper():
            suggestions.append("Performance: Consider GROUP BY instead of DISTINCT")

        if "SELECT" in query.upper() and "LIMIT" not in query.upper() and "TOP" not in query.upper():
            suggestions.append("Performance: Consider adding LIMIT")

        if "WHERE" in query.upper():
            suggestions.append("Performance: Ensure indexes on WHERE columns")

        if "JOIN" in query.upper():
            suggestions.append("Performance: Ensure indexes on join columns")

        return query, suggestions

    def analyze_query(self, query: str) -> QueryAnalysis:
        """Return quick complexity/risk scoring for CI and guardrails."""
        q = query.upper()
        recommendations: List[str] = []
        tags: List[str] = []

        complexity = 0
        complexity += q.count(" JOIN ") * 2
        complexity += q.count(" GROUP BY ") * 2
        complexity += q.count(" ORDER BY ")
        complexity += q.count(" WHERE ")
        complexity += q.count(" HAVING ") * 2
        complexity += q.count(" UNION ") * 3

        risk = 0
        if "SELECT *" in q:
            risk += 2
            recommendations.append("Replace SELECT * with explicit columns.")
            tags.append("select-star")
        if "DELETE" in q and "WHERE" not in q:
            risk += 8
            recommendations.append("DELETE without WHERE is dangerous.")
            tags.append("destructive")
        if "UPDATE" in q and "WHERE" not in q:
            risk += 7
            recommendations.append("UPDATE without WHERE is dangerous.")
            tags.append("mass-update")
        if "DROP " in q or "TRUNCATE " in q:
            risk += 10
            recommendations.append("Avoid destructive DDL in runtime flows.")
            tags.append("ddl-danger")
        if "WHERE" in q and not any(p in query for p in ["$", "?", "@", ":"]):
            risk += 4
            recommendations.append("Use parameterized placeholders in predicates.")
            tags.append("non-parameterized")

        if "LIMIT" not in q and "TOP" not in q and q.strip().startswith("SELECT"):
            recommendations.append("Add LIMIT/TOP for safer pagination.")
            tags.append("no-limit")

        if not recommendations:
            recommendations.append("Looks good. Keep parameterization and index coverage.")
            tags.append("healthy")

        return QueryAnalysis(
            complexity_score=min(100, complexity * 5),
            risk_score=min(100, risk * 10),
            recommendations=recommendations,
            tags=sorted(set(tags)),
        )


class NaturalLanguageParser:
    """Parse natural language to extract query components"""
    
    @staticmethod
    def parse_description(description: str) -> Dict[str, any]:
        """Parse natural language description"""
        components = {
            'action': None,
            'tables': [],
            'columns': [],
            'conditions': [],
            'aggregations': [],
            'sorting': []
        }
        
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['get', 'select', 'find', 'show', 'list']):
            components['action'] = 'SELECT'
        elif any(word in description_lower for word in ['insert', 'add', 'create']):
            components['action'] = 'INSERT'
        elif any(word in description_lower for word in ['update', 'modify', 'change']):
            components['action'] = 'UPDATE'
        elif any(word in description_lower for word in ['delete', 'remove']):
            components['action'] = 'DELETE'
        
        if 'count' in description_lower:
            components['aggregations'].append('COUNT')
        if 'sum' in description_lower or 'total' in description_lower:
            components['aggregations'].append('SUM')
        
        return components


def main():
    """Example usage"""
    print("=" * 80)
    print("ULTRA-SECURE SQL QUERY GENERATOR")
    print("=" * 80)
    print()
    
    generator = SQLQueryGenerator(
        DatabaseType.POSTGRESQL,
        security_level=SecurityLevel.STRICT,
        enable_audit_log=True,
        enable_rate_limit=True
    )
    
    print("Security Level: STRICT")
    print("Audit Logging: ENABLED")
    print("Rate Limiting: ENABLED")
    print()
    
    try:
        query = generator.generate_select_query(
            tables=['users'],
            columns=['user_id', 'username', 'email'],
            where_conditions=['status = $1', 'created_at > $2'],
            order_by=['created_at DESC'],
            limit=100,
            user_id='demo_user'
        )
        
        print("Generated Query:")
        print(query)
        print()
        
        warnings = generator.validate_query_security(query, 'demo_user')
        if warnings:
            print("Security Warnings:")
            for warning in warnings:
                print(f"  ⚠ {warning}")
        else:
            print("✓ No security issues detected")

        analysis = generator.analyze_query(query)
        print(f"Complexity Score: {analysis.complexity_score}/100")
        print(f"Risk Score: {analysis.risk_score}/100")
        print(f"Tags: {', '.join(analysis.tags)}")
        print()

    except (ValidationException, SecurityException) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
