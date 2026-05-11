import { SecurityPattern, Severity } from '../../types';

export const pathTraversalPatterns: SecurityPattern[] = [
  {
    id: 'path_001',
    category: 'path_traversal',
    subcategory: 'dot_dot_slash',
    pattern: /\.\.[\\/]/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Path traversal using ../ or ..\\',
    examples: [
      '../etc/passwd',
      '..\\windows\\system32',
      'files/../../secret.txt',
      'data\\..\\..\\config.ini'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['path-traversal', 'directory-traversal', 'high-confidence']
  },
  {
    id: 'path_002',
    category: 'path_traversal',
    subcategory: 'encoded_dot_dot_slash',
    pattern: /(?:%2e%2e[%/\\]|\.\.%2f|\.\.%5c)/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'URL-encoded path traversal',
    examples: [
      '%2e%2e%2f',
      '%2e%2e/',
      '..%2f',
      '..%5c',
      '%2e%2e%5c'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['path-traversal', 'encoded', 'url-encoding', 'high-confidence']
  },
  {
    id: 'path_003',
    category: 'path_traversal',
    subcategory: 'double_encoded',
    pattern: /%252e%252e[%/\\]/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Double URL-encoded path traversal',
    examples: [
      '%252e%252e%252f',
      '%252e%252e/',
      '%252e%252e%255c'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['path-traversal', 'double-encoded', 'evasion', 'high-confidence']
  },
  {
    id: 'path_004',
    category: 'path_traversal',
    subcategory: 'unix_passwd',
    pattern: /(?:\/etc\/passwd|\/etc\/shadow)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Attempt to access Unix password files',
    examples: [
      '/etc/passwd',
      '/etc/shadow',
      '../../etc/passwd',
      'files/../../../etc/shadow'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['path-traversal', 'unix', 'credential-access', 'critical']
  },
  {
    id: 'path_005',
    category: 'path_traversal',
    subcategory: 'ssh_keys',
    pattern: /(?:\.ssh\/(?:id_rsa|id_dsa|id_ecdsa|id_ed25519|authorized_keys|known_hosts))/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Attempt to access SSH private keys',
    examples: [
      '.ssh/id_rsa',
      '.ssh/id_ed25519',
      '../.ssh/authorized_keys',
      '/home/user/.ssh/id_rsa',
      '../../.ssh/known_hosts'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['path-traversal', 'ssh', 'credential-access', 'critical']
  },
  {
    id: 'path_006',
    category: 'path_traversal',
    subcategory: 'windows_sam',
    pattern: /(?:\\windows\\system32\\config\\(?:sam|system|security)|\/windows\/system32\/config\/(?:sam|system|security))/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Attempt to access Windows SAM database',
    examples: [
      'C:\\windows\\system32\\config\\sam',
      '\\windows\\system32\\config\\system',
      '/windows/system32/config/security',
      '..\\..\\windows\\system32\\config\\sam'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['path-traversal', 'windows', 'credential-access', 'critical']
  },
  {
    id: 'path_007',
    category: 'path_traversal',
    subcategory: 'environment_files',
    pattern: /(?:\.env(?:\.local|\.production|\.development)?|\.git\/config|\.gitconfig)/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Attempt to access environment or git configuration files',
    examples: [
      '.env',
      '.env.local',
      '.env.production',
      '../.env',
      '.git/config',
      '../../.gitconfig'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['path-traversal', 'config', 'secrets', 'high-confidence']
  },
  {
    id: 'path_008',
    category: 'path_traversal',
    subcategory: 'aws_credentials',
    pattern: /(?:\.aws\/credentials|\.aws\/config)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Attempt to access AWS credentials',
    examples: [
      '.aws/credentials',
      '.aws/config',
      '../../.aws/credentials',
      '/home/user/.aws/credentials'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['path-traversal', 'aws', 'credential-access', 'critical']
  },
  {
    id: 'path_009',
    category: 'path_traversal',
    subcategory: 'docker_secrets',
    pattern: /(?:\/run\/secrets\/|\/var\/run\/secrets\/kubernetes\.io\/serviceaccount\/)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Attempt to access Docker or Kubernetes secrets',
    examples: [
      '/run/secrets/db_password',
      '/var/run/secrets/kubernetes.io/serviceaccount/token',
      '/run/secrets/api_key'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['path-traversal', 'docker', 'kubernetes', 'secrets', 'critical']
  },
  {
    id: 'path_010',
    category: 'path_traversal',
    subcategory: 'backup_files',
    pattern: /(?:\.bak|\.backup|\.old|\.tmp|~)$/i,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'Attempt to access backup or temporary files',
    examples: [
      'config.php.bak',
      'database.sql.backup',
      'secret.txt.old',
      'data.json.tmp',
      'file~'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['path-traversal', 'backup', 'information-disclosure']
  },
  {
    id: 'path_011',
    category: 'path_traversal',
    subcategory: 'log_files',
    pattern: /(?:\/var\/log\/|\/logs\/|\.log$)/i,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'Attempt to access log files',
    examples: [
      '/var/log/apache2/access.log',
      '/var/log/nginx/error.log',
      '../logs/application.log',
      'debug.log'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['path-traversal', 'logs', 'information-disclosure']
  },
  {
    id: 'path_012',
    category: 'path_traversal',
    subcategory: 'proc_filesystem',
    pattern: /\/proc\/(?:self\/(?:environ|cmdline|maps)|[0-9]+\/(?:environ|cmdline|maps))/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Attempt to access /proc filesystem',
    examples: [
      '/proc/self/environ',
      '/proc/self/cmdline',
      '/proc/1/environ',
      '/proc/self/maps'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['path-traversal', 'proc', 'unix', 'information-disclosure']
  },
  {
    id: 'path_013',
    category: 'path_traversal',
    subcategory: 'null_byte',
    pattern: /%00/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Null byte injection for path truncation',
    examples: [
      'file.txt%00.jpg',
      '../../../etc/passwd%00',
      'config%00.php'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['path-traversal', 'null-byte', 'evasion', 'high-confidence']
  },
  {
    id: 'path_014',
    category: 'path_traversal',
    subcategory: 'absolute_unix_paths',
    pattern: /^\/(?:etc|root|home|usr|var|opt|bin|sbin)\//,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'Absolute Unix paths to sensitive directories',
    examples: [
      '/etc/hosts',
      '/root/.bashrc',
      '/home/user/.profile',
      '/var/www/config.php',
      '/usr/local/bin/script.sh'
    ],
    falsePositiveRisk: 'high',
    enabled: true,
    tags: ['path-traversal', 'unix', 'absolute-path']
  },
  {
    id: 'path_015',
    category: 'path_traversal',
    subcategory: 'windows_absolute_paths',
    pattern: /^[a-z]:\\(?:windows|users|program files|boot|system)/i,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'Absolute Windows paths to sensitive directories',
    examples: [
      'C:\\windows\\win.ini',
      'C:\\users\\admin\\desktop',
      'D:\\program files\\app\\config.xml',
      'C:\\boot\\bcd'
    ],
    falsePositiveRisk: 'high',
    enabled: true,
    tags: ['path-traversal', 'windows', 'absolute-path']
  }
];
