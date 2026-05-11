import { SecurityPattern, Severity } from '../../types';

export const secretPatterns: SecurityPattern[] = [
  {
    id: 'secret_001',
    category: 'secret',
    subcategory: 'anthropic_api_key',
    pattern: /sk-ant-api03-[a-zA-Z0-9\-_]{95}/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Anthropic API key',
    examples: [
      'sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'anthropic', 'critical']
  },
  {
    id: 'secret_002',
    category: 'secret',
    subcategory: 'openai_api_key',
    pattern: /sk-[a-zA-Z0-9]{48}/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'OpenAI API key',
    examples: [
      'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['secret', 'api-key', 'openai', 'critical']
  },
  {
    id: 'secret_003',
    category: 'secret',
    subcategory: 'github_token',
    pattern: /gh[pousr]_[a-zA-Z0-9]{36,}/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'GitHub personal access token',
    examples: [
      'ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
      'gho_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
      'ghu_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
      'ghs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
      'ghr_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'github', 'critical']
  },
  {
    id: 'secret_004',
    category: 'secret',
    subcategory: 'github_oauth',
    pattern: /gho_[a-zA-Z0-9]{36}/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'GitHub OAuth access token',
    examples: [
      'gho_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'oauth', 'github', 'critical']
  },
  {
    id: 'secret_005',
    category: 'secret',
    subcategory: 'aws_access_key',
    pattern: /(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'AWS access key ID',
    examples: [
      'AKIAIOSFODNN7EXAMPLE',
      'ASIATESTACCESSKEYID',
      'AIDAI23KAKVEXAMPLEID'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'aws', 'critical']
  },
  {
    id: 'secret_006',
    category: 'secret',
    subcategory: 'aws_secret_key',
    pattern: /(?:aws_secret_access_key\s*[=:]\s*|AWS_SECRET_ACCESS_KEY\s*[=:]\s*)([a-zA-Z0-9/+=]{40})/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'AWS secret access key',
    examples: [
      'aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
      'AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'aws', 'critical']
  },
  {
    id: 'secret_007',
    category: 'secret',
    subcategory: 'azure_subscription_key',
    pattern: /[a-f0-9]{32}/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Azure subscription key (generic 32-char hex)',
    examples: [
      'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'
    ],
    falsePositiveRisk: 'high',
    enabled: false,
    tags: ['secret', 'api-key', 'azure', 'high-false-positive']
  },
  {
    id: 'secret_008',
    category: 'secret',
    subcategory: 'google_api_key',
    pattern: /AIza[0-9A-Za-z\-_]{35}/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Google API key',
    examples: [
      'AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'google', 'critical']
  },
  {
    id: 'secret_009',
    category: 'secret',
    subcategory: 'google_oauth',
    pattern: /ya29\.[0-9A-Za-z\-_]+/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Google OAuth access token',
    examples: [
      'ya29.a0AfH6SMBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'oauth', 'google', 'critical']
  },
  {
    id: 'secret_010',
    category: 'secret',
    subcategory: 'slack_token',
    pattern: /xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,32}/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Slack token',
    examples: [
      'xoxb-REDACTED-TEST-TOKEN',
      'xoxa-REDACTED-TEST-TOKEN',
      'xoxp-REDACTED-TEST-TOKEN',
      'xoxr-REDACTED-TEST-TOKEN',
      'xoxs-REDACTED-TEST-TOKEN'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'slack', 'critical']
  },
  {
    id: 'secret_011',
    category: 'secret',
    subcategory: 'slack_webhook',
    pattern: /https:\/\/hooks\.slack\.com\/services\/T[a-zA-Z0-9_]+\/B[a-zA-Z0-9_]+\/[a-zA-Z0-9_]+/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Slack webhook URL',
    examples: [
      'https://hooks.slack.com/services/TFAKETEST1/BFAKETEST2/FAKE3EXAMPLE4TESTING56789'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'webhook', 'slack', 'high-confidence']
  },
  {
    id: 'secret_012',
    category: 'secret',
    subcategory: 'stripe_api_key',
    pattern: /(?:sk|pk)_(?:live|test)_[0-9a-zA-Z]{24,}/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Stripe API key',
    examples: [
      'sk_live_FAKE1EXAMPLE2TESTING345',
      'pk_live_FAKE1EXAMPLE2TESTING345',
      'sk_test_FAKE1EXAMPLE2TESTING345',
      'pk_test_FAKE1EXAMPLE2TESTING345'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'stripe', 'payment', 'critical']
  },
  {
    id: 'secret_013',
    category: 'secret',
    subcategory: 'twilio_api_key',
    pattern: /SK[a-z0-9]{32}/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Twilio API key',
    examples: [
      'SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['secret', 'api-key', 'twilio', 'critical']
  },
  {
    id: 'secret_014',
    category: 'secret',
    subcategory: 'mailgun_api_key',
    pattern: /key-[0-9a-zA-Z]{32}/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Mailgun API key',
    examples: [
      'key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['secret', 'api-key', 'mailgun']
  },
  {
    id: 'secret_015',
    category: 'secret',
    subcategory: 'sendgrid_api_key',
    pattern: /SG\.[a-zA-Z0-9_\-]{22}\.[a-zA-Z0-9_\-]{43}/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'SendGrid API key',
    examples: [
      'SG.xxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'sendgrid', 'critical']
  },
  {
    id: 'secret_016',
    category: 'secret',
    subcategory: 'jwt_token',
    pattern: /eyJ[a-zA-Z0-9_\-]*\.eyJ[a-zA-Z0-9_\-]*\.[a-zA-Z0-9_\-]*/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'JSON Web Token (JWT)',
    examples: [
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['secret', 'jwt', 'token']
  },
  {
    id: 'secret_017',
    category: 'secret',
    subcategory: 'private_key',
    pattern: /-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Private key header',
    examples: [
      '-----BEGIN PRIVATE KEY-----',
      '-----BEGIN RSA PRIVATE KEY-----',
      '-----BEGIN EC PRIVATE KEY-----',
      '-----BEGIN OPENSSH PRIVATE KEY-----'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'private-key', 'ssh', 'critical']
  },
  {
    id: 'secret_018',
    category: 'secret',
    subcategory: 'generic_api_key',
    pattern: /(?:api[_-]?key|apikey|access[_-]?token|auth[_-]?token)\s*[=:]\s*['"]([a-zA-Z0-9_\-]{20,})['\"]/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Generic API key or token assignment',
    examples: [
      'api_key = "xxxxxxxxxxxxxxxxxxxxxxxx"',
      'apiKey: "xxxxxxxxxxxxxxxxxxxxxxxx"',
      "access_token = 'xxxxxxxxxxxxxxxxxxxxxxxx'",
      'auth-token: "xxxxxxxxxxxxxxxxxxxxxxxx"'
    ],
    falsePositiveRisk: 'high',
    enabled: true,
    tags: ['secret', 'api-key', 'generic']
  },
  {
    id: 'secret_019',
    category: 'secret',
    subcategory: 'generic_password',
    pattern: /(?:password|passwd|pwd)\s*[=:]\s*['"]([^'"]{8,})['\"]/i,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'Password assignment in code',
    examples: [
      'password = "MySecretPassword123"',
      'passwd: "Pa$$w0rd"',
      "pwd = 'S3cr3t!'"
    ],
    falsePositiveRisk: 'high',
    enabled: true,
    tags: ['secret', 'password', 'generic']
  },
  {
    id: 'secret_020',
    category: 'secret',
    subcategory: 'heroku_api_key',
    pattern: /[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Heroku API key (UUID format)',
    examples: [
      '12345678-1234-1234-1234-123456789abc'
    ],
    falsePositiveRisk: 'high',
    enabled: false,
    tags: ['secret', 'api-key', 'heroku', 'uuid', 'high-false-positive']
  },
  {
    id: 'secret_021',
    category: 'secret',
    subcategory: 'discord_token',
    pattern: /(?:discord.*)?[MN][a-zA-Z0-9_\-]{23}\.[a-zA-Z0-9_\-]{6}\.[a-zA-Z0-9_\-]{27}/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Discord bot token',
    examples: [
      'NxxxxxxxxxxxxxxxxxxxxxxxxX.xxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxx',
      'Mxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'discord', 'bot']
  },
  {
    id: 'secret_022',
    category: 'secret',
    subcategory: 'pypi_token',
    pattern: /pypi-AgEIcHlwaS5vcmc[a-zA-Z0-9_\-]{50,}/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'PyPI upload token',
    examples: [
      'pypi-AgEIcHlwaS5vcmcxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'pypi', 'python']
  },
  {
    id: 'secret_023',
    category: 'secret',
    subcategory: 'npm_token',
    pattern: /npm_[a-zA-Z0-9]{36}/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'NPM access token',
    examples: [
      'npm_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'npm', 'nodejs']
  },
  {
    id: 'secret_024',
    category: 'secret',
    subcategory: 'gitlab_token',
    pattern: /glpat-[a-zA-Z0-9_\-]{20}/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'GitLab personal access token',
    examples: [
      'glpat-xxxxxxxxxxxxxxxxxxxx'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'gitlab', 'critical']
  },
  {
    id: 'secret_025',
    category: 'secret',
    subcategory: 'supabase_key',
    pattern: /sbp_[a-f0-9]{40}/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Supabase service key',
    examples: [
      'sbp_' + 'a'.repeat(40)
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'supabase', 'critical']
  },
  {
    id: 'secret_026',
    category: 'secret',
    subcategory: 'vercel_token',
    pattern: /vc_[a-zA-Z0-9_\-]{24,}/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Vercel authentication token',
    examples: [
      'vc_' + 'x'.repeat(24)
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'vercel']
  },
  {
    id: 'secret_027',
    category: 'secret',
    subcategory: 'cloudflare_api_token',
    pattern: /cf_[a-zA-Z0-9_\-]{37,}/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Cloudflare API token',
    examples: [
      'cf_' + 'x'.repeat(40)
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'cloudflare']
  },
  {
    id: 'secret_028',
    category: 'secret',
    subcategory: 'azure_connection_string',
    pattern: /(?:DefaultEndpointsProtocol|AccountName|AccountKey|EndpointSuffix)\s*=[^\s;]+/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Azure Storage connection string component',
    examples: [
      'DefaultEndpointsProtocol=https;AccountName=mystorageaccount;AccountKey=abc123==;EndpointSuffix=core.windows.net'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['secret', 'connection-string', 'azure', 'critical']
  },
  {
    id: 'secret_029',
    category: 'secret',
    subcategory: 'databricks_token',
    pattern: /dapi[a-f0-9]{32}/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Databricks personal access token',
    examples: [
      'dapi' + 'a'.repeat(32)
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'databricks']
  },
  {
    id: 'secret_030',
    category: 'secret',
    subcategory: 'huggingface_token',
    pattern: /hf_[a-zA-Z0-9]{34,}/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'HuggingFace API token',
    examples: [
      'hf_' + 'x'.repeat(34)
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'huggingface', 'ai']
  },
  {
    id: 'secret_031',
    category: 'secret',
    subcategory: 'replicate_token',
    pattern: /r8_[a-zA-Z0-9]{36,}/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Replicate API token',
    examples: [
      'r8_' + 'x'.repeat(36)
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'replicate', 'ai']
  },
  {
    id: 'secret_032',
    category: 'secret',
    subcategory: 'planetscale_token',
    pattern: /pscale_tkn_[a-zA-Z0-9_\-]{32,}/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'PlanetScale database token',
    examples: [
      'pscale_tkn_' + 'x'.repeat(32)
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'planetscale', 'database']
  },
  {
    id: 'secret_033',
    category: 'secret',
    subcategory: 'linear_api_key',
    pattern: /lin_api_[a-zA-Z0-9]{32,}/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Linear API key',
    examples: [
      'lin_api_' + 'x'.repeat(32)
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'linear']
  },
  {
    id: 'secret_034',
    category: 'secret',
    subcategory: 'grafana_cloud_token',
    pattern: /glc_[a-zA-Z0-9_\-]{32,}/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Grafana Cloud API token',
    examples: [
      'glc_' + 'x'.repeat(32)
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'grafana']
  },
  {
    id: 'secret_035',
    category: 'secret',
    subcategory: 'hashicorp_vault_token',
    pattern: /hvs\.[a-zA-Z0-9_\-]{24,}/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'HashiCorp Vault service token',
    examples: [
      'hvs.' + 'x'.repeat(24)
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'hashicorp', 'vault', 'critical']
  },
  {
    id: 'secret_036',
    category: 'secret',
    subcategory: 'doppler_token',
    pattern: /dp\.st\.[a-zA-Z0-9_\-]{40,}/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Doppler service token',
    examples: [
      'dp.st.' + 'x'.repeat(40)
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['secret', 'api-key', 'doppler']
  },
  {
    id: 'secret_037',
    category: 'secret',
    subcategory: 'firebase_key',
    pattern: /AIzaSy[0-9A-Za-z\-_]{33}/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Firebase API key',
    examples: [
      'AIzaSy' + 'x'.repeat(33)
    ],
    falsePositiveRisk: 'medium',
    enabled: false,
    tags: ['secret', 'api-key', 'firebase', 'google', 'disabled-duplicate']
  }
];
