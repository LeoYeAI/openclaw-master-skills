import { SecurityPattern, Severity } from '../../types';

export const templateInjectionPatterns: SecurityPattern[] = [
  {
    id: 'template_injection_001',
    category: 'template_injection',
    subcategory: 'jinja2_ssti',
    pattern: /\{\{\s*(?:config|self\.__init__|self\.\_TemplateReference\_\_context|request\.|lipsum)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Jinja2/Twig Server-Side Template Injection (config/request access)',
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
    id: 'template_injection_002',
    category: 'template_injection',
    subcategory: 'ssti_arithmetic',
    pattern: /\{\{\s*\d+\s*\*\s*\d+\s*\}\}/,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'SSTI arithmetic probe ({{7*7}} style)',
    examples: [
      '{{7*7}}',
      '{{4*4}}',
      '{{ 9 * 9 }}'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['ssti', 'probe', 'arithmetic', 'template-injection']
  },
  {
    id: 'template_injection_003',
    category: 'template_injection',
    subcategory: 'expression_language',
    pattern: /\$\{\s*(?:Runtime|ProcessBuilder|Thread|System)\b/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Expression Language / Freemarker SSTI (Java runtime access)',
    examples: [
      '${Runtime.getRuntime().exec("id")}',
      '${ProcessBuilder("cmd","whoami").start()}',
      '${System.getenv()}'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssti', 'expression-language', 'freemarker', 'java', 'critical']
  },
  {
    id: 'template_injection_004',
    category: 'template_injection',
    subcategory: 'erb_injection',
    pattern: /<%=?\s*(?:system|exec|`|%x)\s*[\(\[{'"]/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Ruby ERB template injection with command execution',
    examples: [
      "<%=system('id')%>",
      '<%=`whoami`%>',
      "<%=exec('cat /etc/passwd')%>"
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssti', 'erb', 'ruby', 'command-execution', 'critical']
  },
  {
    id: 'template_injection_005',
    category: 'template_injection',
    subcategory: 'hash_brace_injection',
    pattern: /#\{\s*(?:system|exec|`|%x|IO\.popen)\s*[\(\['"]/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Ruby/CoffeeScript hash-brace template injection',
    examples: [
      "#{system('id')}",
      "#{`whoami`}",
      "#{IO.popen('ls')}"
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssti', 'ruby', 'hash-brace', 'command-execution', 'critical']
  },
  {
    id: 'template_injection_006',
    category: 'template_injection',
    subcategory: 'python_dunder',
    pattern: /__(?:class|mro|subclasses|init|globals|builtins|import)__/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Python dunder introspection chain (class/mro/subclasses)',
    examples: [
      "''.__class__.__mro__[1].__subclasses__()",
      '__import__("os").system("id")',
      '__builtins__.__import__("subprocess")'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['ssti', 'python', 'dunder', 'introspection', 'critical']
  },
  {
    id: 'template_injection_007',
    category: 'template_injection',
    subcategory: 'ldap_filter_injection',
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
    id: 'template_injection_008',
    category: 'template_injection',
    subcategory: 'ldap_wildcard',
    pattern: /\(\w+=\*\)/,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'LDAP wildcard/boolean injection',
    examples: [
      '(uid=*)',
      '(cn=*)',
      '(objectClass=*)'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['ldap', 'injection', 'wildcard']
  },
  {
    id: 'template_injection_009',
    category: 'template_injection',
    subcategory: 'xpath_injection',
    pattern: /(?:'\s*\]\s*(?:\/\/|\.\.))|(?:'\s*or\s+['"]?\d+['"]?\s*=\s*['"]?\d+)|(?:doc\s*\(|document\s*\(|string\s*\(|concat\s*\()/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'XPath injection attempts',
    examples: [
      "' or 1=1 or 'a'='a",
      "']//password",
      "doc('http://evil.com/xxe')"
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['xpath', 'injection', 'xml']
  }
];
