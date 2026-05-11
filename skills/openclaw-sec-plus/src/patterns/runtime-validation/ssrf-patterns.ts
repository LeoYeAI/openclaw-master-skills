import { SecurityPattern, Severity } from '../../types';

export const ssrfPatterns: SecurityPattern[] = [
  {
    id: 'ssrf_001',
    category: 'ssrf',
    subcategory: 'private_ip_10',
    pattern: /(?:https?:\/\/)?(?:[^@\s]+@)?10\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d+)?(?:\/|$)/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Private IP address in 10.0.0.0/8 range (RFC 1918)',
    examples: [
      'http://10.0.0.1/api',
      'http://10.255.255.255/admin',
      'http://user:pass@10.1.1.1/secret'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssrf', 'private-ip', 'rfc1918', 'high-confidence']
  },
  {
    id: 'ssrf_002',
    category: 'ssrf',
    subcategory: 'private_ip_172',
    pattern: /(?:https?:\/\/)?(?:[^@\s]+@)?172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}(?::\d+)?(?:\/|$)/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Private IP address in 172.16.0.0/12 range (RFC 1918)',
    examples: [
      'http://172.16.0.1/api',
      'http://172.31.255.255/admin',
      'http://172.20.10.5/internal'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssrf', 'private-ip', 'rfc1918', 'high-confidence']
  },
  {
    id: 'ssrf_003',
    category: 'ssrf',
    subcategory: 'private_ip_192',
    pattern: /(?:https?:\/\/)?(?:[^@\s]+@)?192\.168\.\d{1,3}\.\d{1,3}(?::\d+)?(?:\/|$)/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Private IP address in 192.168.0.0/16 range (RFC 1918)',
    examples: [
      'http://192.168.1.1/router',
      'http://192.168.0.1/admin',
      'http://192.168.255.255/api'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssrf', 'private-ip', 'rfc1918', 'high-confidence']
  },
  {
    id: 'ssrf_004',
    category: 'ssrf',
    subcategory: 'localhost',
    pattern: /(?:https?:\/\/)?(?:[^@\s]+@)?(?:localhost|127\.\d{1,3}\.\d{1,3}\.\d{1,3}|0\.0\.0\.0)(?::\d+)?(?:\/|$)/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Localhost or loopback address access',
    examples: [
      'http://localhost:8080/api',
      'http://127.0.0.1/admin',
      'http://0.0.0.0/service',
      'http://127.0.0.2/internal'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssrf', 'localhost', 'loopback', 'high-confidence']
  },
  {
    id: 'ssrf_005',
    category: 'ssrf',
    subcategory: 'aws_metadata',
    pattern: /(?:https?:\/\/)?169\.254\.169\.254(?::\d+)?\/(?:latest\/meta-data|meta-data)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'AWS EC2 metadata service endpoint',
    examples: [
      'http://169.254.169.254/latest/meta-data/',
      'http://169.254.169.254/latest/meta-data/iam/security-credentials/',
      'http://169.254.169.254/meta-data/identity-credentials/ec2/security-credentials/'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssrf', 'aws', 'metadata', 'cloud', 'critical']
  },
  {
    id: 'ssrf_006',
    category: 'ssrf',
    subcategory: 'gcp_metadata',
    pattern: /(?:https?:\/\/)?(?:metadata\.google\.internal|metadata\.goog)(?::\d+)?\/computeMetadata/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'GCP metadata service endpoint',
    examples: [
      'http://metadata.google.internal/computeMetadata/v1/',
      'http://metadata.goog/computeMetadata/v1/instance/service-accounts/',
      'http://metadata.google.internal/computeMetadata/v1/instance/attributes/'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssrf', 'gcp', 'metadata', 'cloud', 'critical']
  },
  {
    id: 'ssrf_007',
    category: 'ssrf',
    subcategory: 'link_local',
    pattern: /(?:https?:\/\/)?(?:[^@\s]+@)?169\.254\.\d{1,3}\.\d{1,3}(?::\d+)?(?:\/|$)/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Link-local address in 169.254.0.0/16 range (APIPA)',
    examples: [
      'http://169.254.1.1/api',
      'http://169.254.169.254/metadata',
      'http://169.254.255.255/service'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssrf', 'link-local', 'apipa', 'high-confidence']
  },
  {
    id: 'ssrf_008',
    category: 'ssrf',
    subcategory: 'ipv6_localhost',
    pattern: /(?:https?:\/\/)?(?:[^@\s]+@)?\[?::1\]?(?::\d+)?(?:\/|$)/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'IPv6 localhost address (::1)',
    examples: [
      'http://[::1]/api',
      'http://[::1]:8080/admin',
      'http://[::1]/internal'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssrf', 'ipv6', 'localhost', 'high-confidence']
  },
  {
    id: 'ssrf_009',
    category: 'ssrf',
    subcategory: 'ipv6_ipv4_mapped',
    pattern: /(?:https?:\/\/)?(?:[^@\s]+@)?\[?::ffff:127\.\d{1,3}\.\d{1,3}\.\d{1,3}\]?(?::\d+)?(?:\/|$)/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'IPv4-mapped IPv6 loopback address (::ffff:127.0.0.0/104)',
    examples: [
      'http://[::ffff:127.0.0.1]/api',
      'http://[::ffff:127.0.0.1]:8080/admin',
      'http://[::ffff:127.1.1.1]/internal'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssrf', 'ipv6', 'ipv4-mapped', 'localhost', 'high-confidence']
  },
  {
    id: 'ssrf_010',
    category: 'ssrf',
    subcategory: 'file_protocol',
    pattern: /file:\/\/(?:localhost)?[^\s]*/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'File protocol URL (local file access)',
    examples: [
      'file:///etc/passwd',
      'file://localhost/etc/shadow',
      'file:///var/log/system.log',
      'file:///C:/Windows/System32/config/sam'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssrf', 'file-protocol', 'local-file-inclusion', 'critical']
  },
  {
    id: 'ssrf_011',
    category: 'ssrf',
    subcategory: 'azure_imds',
    pattern: /(?:https?:\/\/)?169\.254\.169\.254(?::\d+)?\/metadata\/instance/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Azure Instance Metadata Service (IMDS) endpoint',
    examples: [
      'http://169.254.169.254/metadata/instance',
      'http://169.254.169.254/metadata/instance?api-version=2021-02-01'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssrf', 'azure', 'imds', 'metadata', 'cloud', 'critical']
  },
  {
    id: 'ssrf_012',
    category: 'ssrf',
    subcategory: 'azure_wire_server',
    pattern: /(?:https?:\/\/)?168\.63\.129\.16(?::\d+)?(?:\/|$)/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Azure Wire Server IP address',
    examples: [
      'http://168.63.129.16/',
      'http://168.63.129.16/machine?comp=goalstate'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssrf', 'azure', 'wire-server', 'cloud']
  },
  {
    id: 'ssrf_013',
    category: 'ssrf',
    subcategory: 'digitalocean_metadata',
    pattern: /(?:https?:\/\/)?169\.254\.169\.254(?::\d+)?\/metadata\/v1/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'DigitalOcean metadata service endpoint',
    examples: [
      'http://169.254.169.254/metadata/v1/',
      'http://169.254.169.254/metadata/v1/hostname'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssrf', 'digitalocean', 'metadata', 'cloud', 'critical']
  },
  {
    id: 'ssrf_014',
    category: 'ssrf',
    subcategory: 'oracle_metadata',
    pattern: /(?:https?:\/\/)?169\.254\.169\.254(?::\d+)?\/opc\/v[12]/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Oracle Cloud Infrastructure metadata endpoint',
    examples: [
      'http://169.254.169.254/opc/v1/instance/',
      'http://169.254.169.254/opc/v2/instance/metadata/'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssrf', 'oracle', 'oci', 'metadata', 'cloud', 'critical']
  },
  {
    id: 'ssrf_015',
    category: 'ssrf',
    subcategory: 'alibaba_metadata',
    pattern: /(?:https?:\/\/)?100\.100\.100\.200(?::\d+)?\/latest\/meta-data/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Alibaba Cloud metadata service endpoint',
    examples: [
      'http://100.100.100.200/latest/meta-data/',
      'http://100.100.100.200/latest/meta-data/instance-id'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssrf', 'alibaba', 'aliyun', 'metadata', 'cloud', 'critical']
  },
  {
    id: 'ssrf_016',
    category: 'ssrf',
    subcategory: 'kubernetes_api',
    pattern: /(?:https?:\/\/)?kubernetes\.default\.svc(?:\.[a-z]+)*(?::\d+)?(?:\/|$)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Kubernetes internal API server endpoint',
    examples: [
      'https://kubernetes.default.svc/api/v1/namespaces',
      'https://kubernetes.default.svc.cluster.local/api',
      'http://kubernetes.default.svc/'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssrf', 'kubernetes', 'k8s', 'api-server', 'cloud', 'critical']
  }
];
