import { SecurityPattern, Severity } from '../../types';

export const obfuscationPatterns: SecurityPattern[] = [
  {
    id: 'obfuscation_001',
    category: 'obfuscation',
    subcategory: 'base64_encoded',
    pattern: /(?:^|[^a-zA-Z0-9])([a-zA-Z0-9+/]{40,}={0,2})(?:[^a-zA-Z0-9]|$)/,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'Base64 encoded string (potentially obfuscated content)',
    examples: [
      'SGVsbG8gV29ybGQhIFRoaXMgaXMgYSBsb25nIGJhc2U2NCBlbmNvZGVkIHN0cmluZy4=',
      'aGVsbG8gd29ybGQgdGhpcyBpcyBhIGxvbmdlciBzdHJpbmcgZm9yIHRlc3Rpbmc='
    ],
    falsePositiveRisk: 'high',
    enabled: true,
    tags: ['obfuscation', 'encoding', 'base64']
  },
  {
    id: 'obfuscation_002',
    category: 'obfuscation',
    subcategory: 'hex_encoded',
    pattern: /(?:0x)?[a-fA-F0-9]{64,}/,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'Hexadecimal encoded string (potentially obfuscated)',
    examples: [
      '48656c6c6f20576f726c6421205468697320697320612074657374206d6573736167652e',
      '0x4142434445464748494a4b4c4d4e4f505152535455565758595a'
    ],
    falsePositiveRisk: 'high',
    enabled: true,
    tags: ['obfuscation', 'encoding', 'hex']
  },
  {
    id: 'obfuscation_003',
    category: 'obfuscation',
    subcategory: 'unicode_escape',
    pattern: /(?:\\u[0-9a-fA-F]{4}){4,}/,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'Unicode escape sequences (potential obfuscation)',
    examples: [
      '\\u0048\\u0065\\u006c\\u006c\\u006f',
      '\\u0041\\u0042\\u0043\\u0044\\u0045'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['obfuscation', 'unicode', 'escape-sequences']
  },
  {
    id: 'obfuscation_004',
    category: 'obfuscation',
    subcategory: 'unicode_homoglyphs',
    pattern: /[а-яА-ЯёЁ]{2,}.*[a-zA-Z]{2,}|[a-zA-Z]{2,}.*[а-яА-ЯёЁ]{2,}/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Mixed Latin and Cyrillic characters (homoglyph attack)',
    examples: [
      'аdmin',
      'Міcrosoft',
      'Gооgle',
      'раypal'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['obfuscation', 'homoglyphs', 'cyrillic', 'spoofing']
  },
  {
    id: 'obfuscation_005',
    category: 'obfuscation',
    subcategory: 'zero_width_chars',
    pattern: /[\u200B-\u200D\uFEFF]/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Zero-width Unicode characters (invisible obfuscation)',
    examples: [
      'admin\u200Buser',
      'pass\u200Cword',
      'api\u200Dkey'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['obfuscation', 'unicode', 'zero-width', 'invisible', 'high-confidence']
  },
  {
    id: 'obfuscation_006',
    category: 'obfuscation',
    subcategory: 'rtl_override',
    pattern: /[\u202E\u202D]/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Right-to-left override character (text direction manipulation)',
    examples: [
      'file\u202Etxt.exe',
      'admin\u202D\u202Euser'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['obfuscation', 'unicode', 'rtl', 'bidi', 'high-confidence']
  },
  {
    id: 'obfuscation_007',
    category: 'obfuscation',
    subcategory: 'mixed_scripts',
    pattern: /(?=.*[a-zA-Z])(?=.*[\u0400-\u04FF])(?=.*[\u0370-\u03FF])/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Mixed scripts from different alphabets',
    examples: [
      'αdmin',
      'pаyρal',
      'Miсrοsoft'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['obfuscation', 'mixed-scripts', 'spoofing']
  },
  {
    id: 'obfuscation_008',
    category: 'obfuscation',
    subcategory: 'eval_function',
    pattern: /\beval\s*\(/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'JavaScript eval() function (code execution)',
    examples: [
      'eval("alert(1)")',
      'eval(atob("base64code"))',
      'window.eval(code)'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['obfuscation', 'eval', 'code-execution', 'javascript']
  },
  {
    id: 'obfuscation_009',
    category: 'obfuscation',
    subcategory: 'javascript_obfuscation',
    pattern: /String\.fromCharCode\s*\((?:\s*\d+\s*,?\s*){4,}\)/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'String.fromCharCode obfuscation',
    examples: [
      'String.fromCharCode(72, 101, 108, 108, 111)',
      'String.fromCharCode(97, 108, 101, 114, 116)'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['obfuscation', 'javascript', 'fromCharCode', 'high-confidence']
  },
  {
    id: 'obfuscation_010',
    category: 'obfuscation',
    subcategory: 'javascript_unescape',
    pattern: /unescape\s*\(['"]\%/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'JavaScript unescape() with encoded content',
    examples: [
      'unescape("%48%65%6c%6c%6f")',
      'unescape("%61%6c%65%72%74")'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['obfuscation', 'javascript', 'unescape', 'high-confidence']
  },
  {
    id: 'obfuscation_011',
    category: 'obfuscation',
    subcategory: 'atob_btoa',
    pattern: /\b(?:atob|btoa)\s*\(/i,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'JavaScript base64 encoding/decoding functions',
    examples: [
      'atob("SGVsbG8gV29ybGQ=")',
      'btoa("Hello World")',
      'eval(atob(encoded))'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['obfuscation', 'javascript', 'base64', 'atob', 'btoa']
  },
  {
    id: 'obfuscation_012',
    category: 'obfuscation',
    subcategory: 'excessive_escaping',
    pattern: /(?:\\x[0-9a-fA-F]{2}){8,}/,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'Excessive hexadecimal escape sequences',
    examples: [
      '\\x48\\x65\\x6c\\x6c\\x6f\\x20\\x57\\x6f\\x72\\x6c\\x64',
      '\\x61\\x6c\\x65\\x72\\x74\\x28\\x31\\x29'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['obfuscation', 'escape-sequences', 'hex', 'high-confidence']
  },
  {
    id: 'obfuscation_013',
    category: 'obfuscation',
    subcategory: 'octal_escaping',
    pattern: /(?:\\[0-7]{3}){6,}/,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'Octal escape sequences',
    examples: [
      '\\110\\145\\154\\154\\157',
      '\\141\\154\\145\\162\\164'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['obfuscation', 'escape-sequences', 'octal']
  },
  {
    id: 'obfuscation_014',
    category: 'obfuscation',
    subcategory: 'html_entities',
    pattern: /(?:&(?:#x?[0-9a-fA-F]+|[a-zA-Z]+);){6,}/,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'Excessive HTML entity encoding',
    examples: [
      '&#72;&#101;&#108;&#108;&#111;',
      '&#x48;&#x65;&#x6c;&#x6c;&#x6f;',
      '&lt;&gt;&amp;&quot;&apos;&nbsp;'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['obfuscation', 'html', 'entities', 'encoding']
  },
  {
    id: 'obfuscation_015',
    category: 'obfuscation',
    subcategory: 'url_encoding_excessive',
    pattern: /(?:%[0-9a-fA-F]{2}){8,}/,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'Excessive URL encoding',
    examples: [
      '%48%65%6c%6c%6f%20%57%6f%72%6c%64',
      '%61%6c%65%72%74%28%31%29'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['obfuscation', 'url-encoding', 'encoding']
  },
  {
    id: 'obfuscation_016',
    category: 'obfuscation',
    subcategory: 'concatenation_obfuscation',
    pattern: /(['"`])\s*\+\s*\1\s*\+\s*\1/,
    severity: Severity.LOW,
    language: 'all',
    description: 'String concatenation obfuscation',
    examples: [
      '"a" + "l" + "e" + "r" + "t"',
      "'e' + 'v' + 'a' + 'l'",
      '`a` + `d` + `m` + `i` + `n`'
    ],
    falsePositiveRisk: 'high',
    enabled: false,
    tags: ['obfuscation', 'concatenation', 'string-splitting']
  },
  {
    id: 'obfuscation_017',
    category: 'obfuscation',
    subcategory: 'double_encoding',
    pattern: /%25[0-9a-fA-F]{2}/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Double URL encoding (%25 = encoded %)',
    examples: [
      '%2527',
      '%253C',
      '%2520'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['obfuscation', 'double-encoding', 'url-encoding', 'evasion', 'high-confidence']
  },
  {
    id: 'obfuscation_018',
    category: 'obfuscation',
    subcategory: 'php_chr_concat',
    pattern: /chr\s*\(\s*\d+\s*\)\s*\.\s*chr\s*\(/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'PHP chr() concatenation obfuscation',
    examples: [
      'chr(72).chr(101).chr(108).chr(108).chr(111)',
      'chr(101).chr(118).chr(97).chr(108)'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['obfuscation', 'php', 'chr', 'high-confidence']
  },
  {
    id: 'obfuscation_019',
    category: 'obfuscation',
    subcategory: 'python_chr_join',
    pattern: /(?:chr\(\d+\)\s*,?\s*){4,}/,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'Python chr() obfuscation',
    examples: [
      "chr(72), chr(101), chr(108), chr(108), chr(111)",
      "''.join([chr(72), chr(101), chr(108), chr(108), chr(111)])"
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['obfuscation', 'python', 'chr']
  },
  {
    id: 'obfuscation_020',
    category: 'obfuscation',
    subcategory: 'invisible_separator',
    pattern: /[\u2000-\u200F\u2028-\u202F\u205F-\u206F]/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Invisible Unicode separator characters',
    examples: [
      'admin\u2000user',
      'pass\u2009word',
      'api\u200Akey'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['obfuscation', 'unicode', 'invisible', 'separators', 'high-confidence']
  }
];
