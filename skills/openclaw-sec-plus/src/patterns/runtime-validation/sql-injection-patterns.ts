import { SecurityPattern, Severity } from '../../types';

export const sqlInjectionPatterns: SecurityPattern[] = [
  {
    id: 'sql_injection_001',
    category: 'sql_injection',
    subcategory: 'tautology',
    pattern: /['"]?\s*(?:OR|AND)\s+['"]?\d+['"]?\s*=\s*['"]?\d+/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'SQL tautology injection (OR 1=1 style)',
    examples: [
      "' OR 1=1 --",
      "' OR '1'='1",
      '" AND 1=1 --'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['sql-injection', 'tautology', 'authentication-bypass', 'critical']
  },
  {
    id: 'sql_injection_002',
    category: 'sql_injection',
    subcategory: 'union_select',
    pattern: /\bUNION\s+(?:ALL\s+)?SELECT\b/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'SQL UNION SELECT injection',
    examples: [
      "' UNION SELECT username, password FROM users --",
      "1 UNION ALL SELECT null, table_name FROM information_schema.tables"
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['sql-injection', 'union', 'data-extraction', 'critical']
  },
  {
    id: 'sql_injection_003',
    category: 'sql_injection',
    subcategory: 'drop_table',
    pattern: /\bDROP\s+(?:TABLE|DATABASE|INDEX|VIEW)\b/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'SQL DROP TABLE/DATABASE destructive command',
    examples: [
      "'; DROP TABLE users; --",
      "1; DROP DATABASE production --"
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['sql-injection', 'destructive', 'drop', 'critical']
  },
  {
    id: 'sql_injection_004',
    category: 'sql_injection',
    subcategory: 'stacked_queries',
    pattern: /;\s*(?:DELETE|INSERT|UPDATE)\s+(?:FROM|INTO|SET)\b/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'SQL stacked queries with data modification',
    examples: [
      "'; DELETE FROM users; --",
      "1; INSERT INTO admin (user) VALUES ('attacker')",
      "'; UPDATE users SET role='admin' WHERE id=1; --"
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['sql-injection', 'stacked-queries', 'data-modification']
  },
  {
    id: 'sql_injection_005',
    category: 'sql_injection',
    subcategory: 'comment_termination',
    pattern: /['"];\s*--/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'SQL comment termination injection',
    examples: [
      "admin'; --",
      "1'; -- end"
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['sql-injection', 'comment', 'termination']
  },
  {
    id: 'sql_injection_006',
    category: 'sql_injection',
    subcategory: 'time_based_blind',
    pattern: /\b(?:SLEEP|WAITFOR\s+DELAY|BENCHMARK)\s*\(/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'SQL time-based blind injection (SLEEP/WAITFOR/BENCHMARK)',
    examples: [
      "' AND SLEEP(5) --",
      "'; WAITFOR DELAY '0:0:5' --",
      "1 AND BENCHMARK(10000000,SHA1('test'))"
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['sql-injection', 'blind', 'time-based']
  },
  {
    id: 'sql_injection_007',
    category: 'sql_injection',
    subcategory: 'mongodb_operators',
    pattern: /\$(?:gt|ne|lt|gte|lte|in|nin|regex|where|exists)\b/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'MongoDB query operator injection',
    examples: [
      '{"username": {"$ne": ""}}',
      '{"$gt": ""}',
      '{"$where": "this.password.length > 0"}'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['nosql-injection', 'mongodb', 'operator']
  },
  {
    id: 'sql_injection_008',
    category: 'sql_injection',
    subcategory: 'nosql_json_injection',
    pattern: /\{\s*['"]\$(?:where|regex|gt|ne|or|and)['"]\s*:/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'NoSQL JSON injection with query operators',
    examples: [
      '{"$where": "function() { return true }"}',
      '{"$or": [{"user": "admin"}, {"user": "root"}]}',
      '{"password": {"$regex": ".*"}}'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['nosql-injection', 'json', 'mongodb']
  },
  {
    id: 'sql_injection_009',
    category: 'sql_injection',
    subcategory: 'information_schema',
    pattern: /\binformation_schema\.\w+/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'SQL information_schema enumeration',
    examples: [
      "UNION SELECT table_name FROM information_schema.tables",
      "SELECT column_name FROM information_schema.columns WHERE table_name='users'"
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['sql-injection', 'information-schema', 'enumeration']
  },
  {
    id: 'sql_injection_010',
    category: 'sql_injection',
    subcategory: 'file_access',
    pattern: /\b(?:LOAD_FILE|INTO\s+(?:OUT|DUMP)FILE)\b/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'SQL file access operations (LOAD_FILE/INTO OUTFILE)',
    examples: [
      "UNION SELECT LOAD_FILE('/etc/passwd')",
      "INTO OUTFILE '/var/www/html/shell.php'",
      "INTO DUMPFILE '/tmp/data'"
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['sql-injection', 'file-access', 'critical']
  }
];
