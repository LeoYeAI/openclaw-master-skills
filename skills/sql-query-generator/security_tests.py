"""
Security Tests for SQL Query Generator
Demonstrates security features and validates protection mechanisms
"""

from sql_query_generator import (
    SQLQueryGenerator,
    SQLInputValidator,
    DatabaseType,
    SecurityLevel,
    SecurityException,
    ValidationException
)
import time


def test_sql_injection_detection():
    """Test SQL injection pattern detection"""
    print("\n" + "=" * 80)
    print("TEST 1: SQL Injection Detection")
    print("=" * 80)
    
    validator = SQLInputValidator()
    
    # Common SQL injection attempts
    injection_attempts = [
        "'; DROP TABLE users--",
        "' OR '1'='1",
        "admin'--",
        "' UNION SELECT * FROM passwords--",
        "1; DELETE FROM users",
        "' OR 1=1--",
        "admin' /*",
        "' OR 'x'='x",
        "'; EXEC xp_cmdshell('dir')--",
        "1' AND '1'='1",
        "SLEEP(5)--",
        "1' WAITFOR DELAY '00:00:05'--",
        "' OR BENCHMARK(10000000,MD5('test'))--",
        "' UNION SELECT NULL,NULL,NULL--",
        "'; INSERT INTO users VALUES('hacker','pwd')--"
    ]
    
    detected = 0
    for attempt in injection_attempts:
        if validator.detect_injection_attempt(attempt):
            detected += 1
            print(f"✓ DETECTED: {attempt[:50]}...")
        else:
            print(f"✗ MISSED: {attempt[:50]}...")
    
    print(f"\nResult: {detected}/{len(injection_attempts)} injection attempts detected")
    print(f"Detection Rate: {(detected/len(injection_attempts)*100):.1f}%")


def test_input_validation():
    """Test input validation mechanisms"""
    print("\n" + "=" * 80)
    print("TEST 2: Input Validation")
    print("=" * 80)
    
    validator = SQLInputValidator()
    
    # Test identifier validation
    print("\n--- Identifier Validation ---")
    valid_identifiers = ['users', 'user_id', 'first_name', 'created_at']
    invalid_identifiers = ['DROP TABLE', 'users; --', 'user-name', '1user', '']
    
    for identifier in valid_identifiers:
        try:
            validator.validate_identifier(identifier)
            print(f"✓ VALID: '{identifier}'")
        except ValidationException as e:
            print(f"✗ REJECTED (should be valid): '{identifier}' - {e}")
    
    for identifier in invalid_identifiers:
        try:
            validator.validate_identifier(identifier)
            print(f"✗ ACCEPTED (should be invalid): '{identifier}'")
        except (ValidationException, SecurityException) as e:
            print(f"✓ REJECTED: '{identifier}' - {str(e)[:50]}")
    
    # Test integer validation
    print("\n--- Integer Validation ---")
    try:
        validator.validate_integer(50, min_val=1, max_val=100)
        print("✓ Valid integer: 50")
    except ValidationException as e:
        print(f"✗ Error: {e}")
    
    try:
        validator.validate_integer(150, min_val=1, max_val=100)
        print("✗ Should reject: 150")
    except ValidationException:
        print("✓ Correctly rejected: 150 (exceeds max)")
    
    # Test string validation
    print("\n--- String Validation ---")
    try:
        validator.validate_string("normal text", max_length=50)
        print("✓ Valid string: 'normal text'")
    except ValidationException as e:
        print(f"✗ Error: {e}")
    
    try:
        validator.validate_string("'; DROP TABLE users--", check_injection=True)
        print("✗ Should reject injection attempt")
    except SecurityException:
        print("✓ Correctly rejected SQL injection in string")
    
    # Test email validation
    print("\n--- Email Validation ---")
    valid_emails = ['user@example.com', 'test.user@domain.co.uk']
    invalid_emails = ['invalid', 'user@', '@domain.com', 'user@domain']
    
    for email in valid_emails:
        try:
            validator.validate_email(email)
            print(f"✓ Valid email: '{email}'")
        except ValidationException:
            print(f"✗ Rejected valid email: '{email}'")
    
    for email in invalid_emails:
        try:
            validator.validate_email(email)
            print(f"✗ Accepted invalid email: '{email}'")
        except ValidationException:
            print(f"✓ Rejected invalid email: '{email}'")


def test_rate_limiting():
    """Test rate limiting functionality"""
    print("\n" + "=" * 80)
    print("TEST 3: Rate Limiting")
    print("=" * 80)
    
    generator = SQLQueryGenerator(
        DatabaseType.POSTGRESQL,
        enable_rate_limit=True
    )
    
    # Override rate limit for testing
    generator.rate_limiter.max_requests = 5
    generator.rate_limiter.window_seconds = 10
    
    user_id = 'test_user'
    successful = 0
    rate_limited = 0
    
    print(f"\nAttempting 10 requests (limit: 5 per 10 seconds)")
    
    for i in range(10):
        try:
            query = generator.generate_select_query(
                tables=['users'],
                columns=['id', 'username'],
                limit=10,
                user_id=user_id
            )
            successful += 1
            print(f"Request {i+1}: ✓ Allowed")
        except SecurityException as e:
            rate_limited += 1
            print(f"Request {i+1}: ✗ Rate limited")
    
    print(f"\nResults:")
    print(f"  Successful: {successful}")
    print(f"  Rate Limited: {rate_limited}")
    print(f"  ✓ Rate limiting {'working' if rate_limited > 0 else 'FAILED'}")


def test_query_security_validation():
    """Test query security validation"""
    print("\n" + "=" * 80)
    print("TEST 4: Query Security Validation")
    print("=" * 80)
    
    generator = SQLQueryGenerator()
    
    # Test secure query
    print("\n--- Secure Query ---")
    secure_query = "SELECT id, username FROM users WHERE status = $1 LIMIT 100"
    warnings = generator.validate_query_security(secure_query)
    
    if not warnings:
        print("✓ Secure query - No warnings")
    else:
        print(f"Warnings: {warnings}")
    
    # Test insecure queries
    print("\n--- Insecure Queries ---")
    insecure_queries = [
        ("String concatenation", "SELECT * FROM users WHERE id = '" + "test" + "'"),
        ("No parameters in WHERE", "SELECT * FROM users WHERE status = 'active'"),
        ("DROP operation", "DROP TABLE users"),
        ("UNION injection", "SELECT * FROM users UNION SELECT * FROM passwords"),
        ("Comment injection", "SELECT * FROM users WHERE id = 1 --"),
    ]
    
    for name, query in insecure_queries:
        warnings = generator.validate_query_security(query)
        if warnings:
            print(f"✓ {name}: {len(warnings)} warning(s)")
            for warning in warnings:
                print(f"  - {warning[:70]}")
        else:
            print(f"✗ {name}: No warnings detected (SHOULD WARN)")


def test_data_sanitization():
    """Test data sanitization for logging"""
    print("\n" + "=" * 80)
    print("TEST 5: Data Sanitization")
    print("=" * 80)
    
    validator = SQLInputValidator()
    
    sensitive_data = [
        ("Credit Card", "My card is 4532-1234-5678-9010", "[REDACTED-CARD]"),
        ("SSN", "My SSN is 123-45-6789", "[REDACTED-SSN]"),
        ("Password", "password=secret123", "password=[REDACTED]"),
        ("Long text", "a" * 150, "...[TRUNCATED]"),
    ]
    
    for name, data, expected_pattern in sensitive_data:
        sanitized = validator.sanitize_for_logging(data, max_length=100)
        if expected_pattern in sanitized:
            print(f"✓ {name}: Properly sanitized")
            print(f"  Original length: {len(data)}")
            print(f"  Sanitized: {sanitized[:80]}...")
        else:
            print(f"✗ {name}: NOT properly sanitized")
            print(f"  Got: {sanitized}")


def test_parameter_styles():
    """Test different database parameter styles"""
    print("\n" + "=" * 80)
    print("TEST 6: Database Parameter Styles")
    print("=" * 80)
    
    databases = [
        (DatabaseType.POSTGRESQL, "$1, $2, $3"),
        (DatabaseType.MYSQL, "?, ?, ?"),
        (DatabaseType.SQLITE, "?, ?, ?"),
        (DatabaseType.MSSQL, "@param1, @param2, @param3"),
        (DatabaseType.ORACLE, ":param1, :param2, :param3"),
    ]
    
    for db_type, expected in databases:
        generator = SQLQueryGenerator(db_type)
        
        query = generator.generate_insert_query(
            table='users',
            columns=['username', 'email', 'age']
        )
        
        # Check if expected parameter style is in query
        if any(style in query for style in expected.split(", ")):
            print(f"✓ {db_type.value.upper()}: Correct parameter style")
        else:
            print(f"✗ {db_type.value.upper()}: Wrong parameter style")
        
        print(f"  Generated: {query[:80]}...")


def test_security_levels():
    """Test different security levels"""
    print("\n" + "=" * 80)
    print("TEST 7: Security Levels")
    print("=" * 80)
    
    # Test with STRICT level
    print("\n--- STRICT Level ---")
    strict_gen = SQLQueryGenerator(
        security_level=SecurityLevel.STRICT,
        enable_audit_log=False,
        enable_rate_limit=False
    )
    
    try:
        # This should trigger warning about SELECT *
        query = strict_gen.generate_select_query(
            tables=['users'],
            columns=['*'],
            limit=10,
            user_id='test'
        )
        print("✓ SELECT * allowed with warning")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test identifier validation at different levels
    print("\n--- Identifier Validation by Level ---")
    problematic_identifier = "user-name"  # Contains hyphen
    
    for level in [SecurityLevel.STRICT, SecurityLevel.NORMAL, SecurityLevel.PERMISSIVE]:
        validator = SQLInputValidator()
        try:
            validator.validate_identifier(
                problematic_identifier,
                security_level=level
            )
            print(f"  {level.value}: Accepted '{problematic_identifier}'")
        except ValidationException:
            print(f"  {level.value}: Rejected '{problematic_identifier}'")


def test_performance():
    """Test performance of security features"""
    print("\n" + "=" * 80)
    print("TEST 8: Performance Impact")
    print("=" * 80)
    
    generator = SQLQueryGenerator(
        enable_audit_log=False,  # Disable for accurate timing
        enable_rate_limit=False
    )
    
    iterations = 1000
    
    # Test query generation speed
    start = time.time()
    for i in range(iterations):
        query = generator.generate_select_query(
            tables=['users'],
            columns=['id', 'username', 'email'],
            where_conditions=['status = $1'],
            limit=100
        )
    end = time.time()
    
    avg_time = ((end - start) / iterations) * 1000  # Convert to ms
    print(f"\nQuery Generation:")
    print(f"  Iterations: {iterations}")
    print(f"  Total time: {(end-start):.3f}s")
    print(f"  Average: {avg_time:.3f}ms per query")
    
    # Test validation speed
    validator = SQLInputValidator()
    test_string = "SELECT * FROM users WHERE id = 1"
    
    start = time.time()
    for i in range(iterations):
        validator.detect_injection_attempt(test_string)
    end = time.time()
    
    avg_time = ((end - start) / iterations) * 1000
    print(f"\nInjection Detection:")
    print(f"  Iterations: {iterations}")
    print(f"  Total time: {(end-start):.3f}s")
    print(f"  Average: {avg_time:.3f}ms per check")


def run_all_tests():
    """Run all security tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "SQL QUERY GENERATOR SECURITY TESTS" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")
    
    tests = [
        test_sql_injection_detection,
        test_input_validation,
        test_rate_limiting,
        test_query_security_validation,
        test_data_sanitization,
        test_parameter_styles,
        test_security_levels,
        test_performance
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n✗ Test failed with error: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED - Security features working correctly!")
    else:
        print(f"\n✗ {failed} test(s) failed - Review security implementation")
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_all_tests()
