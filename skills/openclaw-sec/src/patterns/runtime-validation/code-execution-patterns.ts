import { SecurityPattern, Severity } from '../../types';

export const codeExecutionPatterns: SecurityPattern[] = [
  {
    id: 'code_execution_001',
    category: 'code_execution',
    subcategory: 'nodejs_process_exit',
    pattern: /process\.exit\s*\(/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Node.js process.exit() call (denial of service)',
    examples: [
      'process.exit(0)',
      'process.exit(1)'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['code-execution', 'nodejs', 'process', 'dos']
  },
  {
    id: 'code_execution_002',
    category: 'code_execution',
    subcategory: 'nodejs_child_process',
    pattern: /require\s*\(\s*['"]child_process['"]\s*\)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Node.js child_process module import for command execution',
    examples: [
      "require('child_process').exec('ls')",
      "const cp = require('child_process')"
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['code-execution', 'nodejs', 'child-process', 'critical']
  },
  {
    id: 'code_execution_003',
    category: 'code_execution',
    subcategory: 'nodejs_fs_access',
    pattern: /require\s*\(\s*['"]fs['"]\s*\)/i,
    severity: Severity.MEDIUM,
    language: 'all',
    description: 'Node.js fs module import for filesystem access',
    examples: [
      "require('fs').readFileSync('/etc/passwd')",
      "const fs = require('fs')"
    ],
    falsePositiveRisk: 'high',
    enabled: true,
    tags: ['code-execution', 'nodejs', 'filesystem']
  },
  {
    id: 'code_execution_004',
    category: 'code_execution',
    subcategory: 'nodejs_prototype_pollution',
    pattern: /(?:global|Object)\s*(?:\.\s*)?__proto__/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Node.js global prototype pollution',
    examples: [
      'global.__proto__.isAdmin = true',
      'Object.__proto__.polluted = true'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['code-execution', 'nodejs', 'prototype-pollution', 'critical']
  },
  {
    id: 'code_execution_005',
    category: 'code_execution',
    subcategory: 'python_import_os',
    pattern: /__import__\s*\(\s*['"](?:os|subprocess|shutil|sys|socket|ctypes)['"]\s*\)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Python __import__ for dangerous module loading',
    examples: [
      '__import__("os").system("id")',
      '__import__("subprocess").call(["ls"])',
      '__import__("socket")'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['code-execution', 'python', 'import', 'critical']
  },
  {
    id: 'code_execution_006',
    category: 'code_execution',
    subcategory: 'python_builtins',
    pattern: /(?:__builtins__|__builtin__)(?:\s*\.\s*|\[['"])\w+/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Python __builtins__ access for code execution',
    examples: [
      '__builtins__.__import__("os")',
      '__builtins__["eval"]("malicious")',
      '__builtin__.open("/etc/passwd")'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['code-execution', 'python', 'builtins', 'critical']
  },
  {
    id: 'code_execution_007',
    category: 'code_execution',
    subcategory: 'python_globals',
    pattern: /(?:globals|locals)\s*\(\s*\)\s*\[/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Python globals()/locals() access for code manipulation',
    examples: [
      'globals()["__builtins__"]',
      'locals()["__import__"]'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['code-execution', 'python', 'globals']
  },
  {
    id: 'code_execution_008',
    category: 'code_execution',
    subcategory: 'python_exec_eval',
    pattern: /\b(?:exec|eval|compile)\s*\(\s*(?:['"`]|[a-zA-Z_])/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Python exec()/eval()/compile() dynamic code execution',
    examples: [
      'exec("import os; os.system(\'id\')")',
      'eval("__import__(\'os\').popen(\'ls\').read()")',
      'compile("malicious", "<string>", "exec")'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['code-execution', 'python', 'exec', 'eval']
  },
  {
    id: 'code_execution_009',
    category: 'code_execution',
    subcategory: 'python_unsafe_deserialization',
    pattern: /(?:pickle\.loads?|yaml\.(?:unsafe_)?load|marshal\.loads?)\s*\(/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Python unsafe deserialization (pickle/yaml/marshal)',
    examples: [
      'pickle.loads(user_input)',
      'yaml.load(data)',
      'yaml.unsafe_load(payload)',
      'marshal.loads(bytecode)'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['code-execution', 'python', 'deserialization', 'critical']
  },
  {
    id: 'code_execution_010',
    category: 'code_execution',
    subcategory: 'php_system',
    pattern: /\b(?:system|passthru|shell_exec|popen|proc_open)\s*\(/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'PHP system command execution functions',
    examples: [
      'system("ls -la")',
      'passthru("whoami")',
      'shell_exec("cat /etc/passwd")',
      'popen("id", "r")'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['code-execution', 'php', 'system', 'critical']
  },
  {
    id: 'code_execution_011',
    category: 'code_execution',
    subcategory: 'java_runtime_exec',
    pattern: /Runtime\s*\.\s*getRuntime\s*\(\s*\)\s*\.\s*exec\s*\(/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Java Runtime.getRuntime().exec() command execution',
    examples: [
      'Runtime.getRuntime().exec("calc")',
      'Runtime.getRuntime().exec(new String[]{"cmd", "/c", "whoami"})'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['code-execution', 'java', 'runtime', 'critical']
  },
  {
    id: 'code_execution_012',
    category: 'code_execution',
    subcategory: 'java_processbuilder',
    pattern: /new\s+ProcessBuilder\s*\(/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Java ProcessBuilder for command execution',
    examples: [
      'new ProcessBuilder("cmd", "/c", "whoami").start()',
      'new ProcessBuilder(Arrays.asList("bash", "-c", "id"))'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['code-execution', 'java', 'processbuilder']
  },
  {
    id: 'code_execution_013',
    category: 'code_execution',
    subcategory: 'prototype_pollution',
    pattern: /(?:__proto__\s*(?:\[|\.))|(?:constructor\s*\.\s*constructor\s*\()/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Prototype pollution via __proto__ or constructor.constructor',
    examples: [
      '__proto__.polluted = true',
      'constructor.constructor("return process")().exit()',
      'obj.__proto__["isAdmin"] = true'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['code-execution', 'prototype-pollution', 'critical']
  },
  {
    id: 'code_execution_014',
    category: 'code_execution',
    subcategory: 'dynamic_function_constructor',
    pattern: /(?:Function|GeneratorFunction|AsyncFunction)\s*\(\s*['"`]/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Dynamic function construction via Function constructor',
    examples: [
      'Function("return process")()',
      'new Function("a", "return a+1")',
      'GeneratorFunction("yield 1")'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['code-execution', 'function-constructor', 'dynamic']
  }
];
