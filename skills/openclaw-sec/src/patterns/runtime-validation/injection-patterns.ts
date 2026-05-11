import { SecurityPattern, Severity } from '../../types';

export const injectionPatterns: SecurityPattern[] = [
  {
    id: 'injection_001',
    category: 'injection',
    subcategory: 'sql_union_select',
    pattern: /\bUNION\s+(?:ALL\s+)?SELECT\b/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'SQL UNION SELECT injection for data extraction',
    examples: [
      "' UNION SELECT username, password FROM users --",
      "1 UNION ALL SELECT null, table_name FROM information_schema.tables"
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['sql-injection', 'union-select', 'data-extraction', 'critical']
  },
  {
    id: 'injection_002',
    category: 'injection',
    subcategory: 'sql_boolean_blind',
    pattern: /['"]?\s*(?:AND|OR)\s+['"]?\d+['"]?\s*=\s*['"]?\d+/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'SQL boolean-based blind injection',
    examples: [
      "' AND 1=1 --",
      "' OR 1=1 --",
      '" AND 2=2 --'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['sql-injection', 'boolean-blind', 'authentication-bypass']
  },
  {
    id: 'injection_003',
    category: 'injection',
    subcategory: 'sql_stacked_queries',
    pattern: /;\s*(?:SELECT|DELETE|INSERT|UPDATE|DROP|ALTER|CREATE|TRUNCATE)\b/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'SQL stacked queries injection',
    examples: [
      "'; SELECT * FROM users; --",
      "'; DROP TABLE users; --",
      "1; DELETE FROM sessions --"
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['sql-injection', 'stacked-queries', 'critical']
  },
  {
    id: 'injection_004',
    category: 'injection',
    subcategory: 'sql_comment_based',
    pattern: /(?:--|#|\/\*)\s*$/m,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'SQL comment-based injection termination',
    examples: [
      "admin'--",
      "1' #",
      "test'/*"
    ],
    falsePositiveRisk: 'high',
    enabled: true,
    tags: ['sql-injection', 'comment', 'termination']
  },
  {
    id: 'injection_005',
    category: 'injection',
    subcategory: 'nosql_mongodb_operators',
    pattern: /\$(?:gt|ne|lt|gte|lte|in|nin|regex|exists|elemMatch)\b/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'MongoDB query operator injection',
    examples: [
      '{"username": {"$ne": ""}}',
      '{"age": {"$gt": 0}}',
      '{"field": {"$regex": ".*"}}'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['nosql-injection', 'mongodb', 'operators']
  },
  {
    id: 'injection_006',
    category: 'injection',
    subcategory: 'nosql_where',
    pattern: /['"]\$where['"]\s*:\s*['"`]?(?:function|this\.|return\b)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'MongoDB $where JavaScript injection',
    examples: [
      '{"$where": "function() { return true; }"}',
      '{"$where": "this.password.length > 0"}',
      '{$where: "return this.isAdmin"}'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['nosql-injection', 'mongodb', 'where', 'javascript', 'critical']
  },
  {
    id: 'injection_007',
    category: 'injection',
    subcategory: 'ldap_filter',
    pattern: /[()]\s*[|&]\s*\(\s*\w+\s*[=~><]=?\s*\*?\s*\)/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'LDAP filter injection',
    examples: [
      '(|(uid=*))',
      '(&(uid=admin)(password=*))',
      '(|(cn=*)(sn=*))'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['ldap', 'injection', 'filter', 'directory']
  },
  {
    id: 'injection_008',
    category: 'injection',
    subcategory: 'xpath_injection',
    pattern: /(?:'\s*\]\s*(?:\/\/|\.\.))|(?:'\s*or\s+['"]?\d+['"]?\s*=\s*['"]?\d+)|(?:doc\s*\(|document\s*\()/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'XPath injection',
    examples: [
      "' or 1=1 or 'a'='a",
      "']//password",
      "doc('http://evil.com/xxe')"
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['xpath', 'injection', 'xml']
  },
  {
    id: 'injection_009',
    category: 'injection',
    subcategory: 'ssti_jinja2',
    pattern: /\{\{\s*(?:config|self\.__init__|request\.|lipsum|cycler|joiner|namespace)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Jinja2/Twig Server-Side Template Injection',
    examples: [
      '{{config}}',
      '{{self.__init__.__globals__}}',
      '{{request.application.__globals__}}'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssti', 'jinja2', 'twig', 'template-injection', 'critical']
  },
  {
    id: 'injection_010',
    category: 'injection',
    subcategory: 'ssti_expression_language',
    pattern: /\$\{\s*(?:Runtime|ProcessBuilder|Thread|System|Class\.forName)\b/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Expression Language SSTI (Java)',
    examples: [
      '${Runtime.getRuntime().exec("id")}',
      '${ProcessBuilder("cmd","whoami").start()}',
      '${Class.forName("java.lang.Runtime")}'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssti', 'expression-language', 'java', 'critical']
  },
  {
    id: 'injection_011',
    category: 'injection',
    subcategory: 'ssti_python_dunder',
    pattern: /__(?:class|mro|subclasses|init|globals|builtins|import)__/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Python dunder introspection chain for SSTI',
    examples: [
      "''.__class__.__mro__[1].__subclasses__()",
      '__import__("os").system("id")',
      '__builtins__.__import__("subprocess")'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssti', 'python', 'dunder', 'introspection', 'critical']
  }
];
