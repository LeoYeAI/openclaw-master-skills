#!/usr/bin/env node
/**
 * 360Guard Node.js Scanner
 * Usage: node scanner.cjs /path/to/skill
 */

const fs = require('fs');
const path = require('path');

// Exclude paths - don't scan these directories
const EXCLUDE_DIRS = ['node_modules', '.git', 'scripts', '__pycache__', '.pytest_cache'];

const DANGER_PATTERNS = {
  CRITICAL: [
    { pattern: /eval\s*\(/, name: 'eval() execution', desc: 'Dynamic code execution' },
    { pattern: /exec\s*\(/, name: 'exec() execution', desc: 'System command execution' },
    { pattern: /shell\s*=\s*true/i, name: 'subprocess shell=True', desc: 'Shell injection risk' },
    { pattern: /base64.*decode/i, name: 'base64 decode', desc: 'Code obfuscation detection' },
    { pattern: /pickle\.load/i, name: 'pickle deserialization', desc: 'Python deserialization vulnerability' },
    { pattern: /yaml\.load/i, name: 'yaml deserialization', desc: 'YAML deserialization risk' },
    { pattern: /__import__\s*\(/, name: 'dynamic import', desc: 'Dynamic module loading' },
    { pattern: /importlib\.import_module/i, name: 'importlib dynamic load', desc: 'Runtime loading' },
    { pattern: /xmlrpc/i, name: 'XML-RPC', desc: 'Remote procedure call' },
    { pattern: /reverse.*shell|nc\s+-e|bash\s+-i/i, name: 'reverse shell', desc: 'Potential backdoor' },
    { pattern: /child_process.*spawn.*shell/i, name: 'shell spawn', desc: 'Command execution' }
  ],
  HIGH: [
    { pattern: /curl\s+['"`]/i, name: 'curl request', desc: 'Network request' },
    { pattern: /wget\s+['"`]/i, name: 'wget download', desc: 'File download' },
    { pattern: /fetch\s*\(/, name: 'fetch request', desc: 'HTTP request' },
    { pattern: /axios\./, name: 'axios request', desc: 'HTTP request' },
    { pattern: /https?:\/\/\d{1,3}\.\d{1,3}/, name: 'direct IP connection', desc: 'Non-domain network request' },
    { pattern: /process\.env/i, name: 'environment variable access', desc: 'Possible credential leak' },
    { pattern: /child_process/, name: 'subprocess', desc: 'System command execution' },
    { pattern: /http\.createServer|express\(\)/i, name: 'create server', desc: 'Local service' }
  ],
  MEDIUM: [
    { pattern: /\/\.ssh\//, name: 'SSH directory', desc: 'Sensitive directory access' },
    { pattern: /\/\.aws\//, name: 'AWS directory', desc: 'Cloud credential directory' },
    { pattern: /keychain/i, name: 'Keychain', desc: 'System keychain' },
    { pattern: /credentials|token|secret|api[_-]?key/i, name: 'credential related', desc: 'Sensitive information' },
    { pattern: /cron|systemd|launchd/i, name: 'persistence mechanism', desc: 'Auto-start on boot' },
    { pattern: /setTimeout|setInterval.*eval/i, name: 'timer eval', desc: 'Dynamic execution' },
    { pattern: /document\.cookie/i, name: 'Cookie access', desc: 'Session hijacking' },
    { pattern: /localStorage|sessionStorage/i, name: 'storage access', desc: 'Data storage' }
  ]
};

function scanFile(filePath) {
  const results = { CRITICAL: [], HIGH: [], MEDIUM: [] };
  
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    
    for (const [level, patterns] of Object.entries(DANGER_PATTERNS)) {
      for (const { pattern, name, desc } of patterns) {
        const matches = content.match(new RegExp(pattern, 'gi'));
        if (matches) {
          lines.forEach((line, idx) => {
            if (pattern.test(line)) {
              results[level].push({ 
                file: filePath, 
                line: idx + 1,
                issue: name,
                desc: desc,
                snippet: line.trim().substring(0, 80)
              });
            }
          });
        }
      }
    }
  } catch (e) {
    // Skip unreadable files
  }
  
  // Deduplicate
  for (const level of Object.keys(results)) {
    results[level] = results[level].filter((v, i, a) => 
      a.findIndex(t => t.file === v.file && t.issue === v.issue) === i
    );
  }
  
  return results;
}

function scanDirectory(dirPath) {
  const allResults = { CRITICAL: [], HIGH: [], MEDIUM: [] };
  
  function walk(dir) {
    try {
      const files = fs.readdirSync(dir);
      for (const file of files) {
        // Skip excluded directories
        if (EXCLUDE_DIRS.includes(file) || file.startsWith('.')) continue;
        
        const fullPath = path.join(dir, file);
        try {
          const stat = fs.statSync(fullPath);
          
          if (stat.isDirectory()) {
            walk(fullPath);
          } else if (stat.isFile()) {
            const ext = path.extname(file);
            if (['.js', '.ts', '.jsx', '.tsx', '.py', '.sh', '.bash', '.zsh'].includes(ext)) {
              const results = scanFile(fullPath);
              for (const level of Object.keys(allResults)) {
                allResults[level].push(...results[level]);
              }
            }
          }
        } catch (e) {
          // Skip inaccessible files
        }
      }
    } catch (e) {
      // Skip inaccessible directories
    }
  }
  
  walk(dirPath);
  return allResults;
}

function generateReport(skillPath, results) {
  console.log('\n🛡️ 360Guard Security Scan Report');
  console.log('='.repeat(50));
  console.log(`📂 Scan path: ${skillPath}`);
  console.log(`⏰ Scan time: ${new Date().toISOString()}`);
  console.log('');
  
  const riskOrder = ['CRITICAL', 'HIGH', 'MEDIUM'];
  const emoji = { CRITICAL: '🔴', HIGH: '⚠️', MEDIUM: '🟡' };
  
  for (const level of riskOrder) {
    if (results[level].length > 0) {
      console.log(`\n${emoji[level]} ${level} risk (${results[level].length} items):`);
      for (const item of results[level]) {
        console.log(`  • ${item.issue}`);
        console.log(`    Location: ${item.file}:${item.line}`);
        console.log(`    Code: ${item.snippet}...`);
      }
    }
  }
  
  console.log('\n' + '='.repeat(50));
  
  if (results.CRITICAL.length > 0) {
    console.log('🔴 Conclusion: Critical risks found, not recommended to install');
    console.log('⚠️ Please stop immediately and delete the Skill');
    process.exit(1);
  } else if (results.HIGH.length > 0) {
    console.log('⚠️ Conclusion: High risk found, human approval required');
    process.exit(2);
  } else if (results.MEDIUM.length > 0) {
    console.log('🟡 Conclusion: Medium risk found, please review carefully before installing');
    process.exit(0);
  } else {
    console.log('✅ Conclusion: No obvious risks found');
    process.exit(0);
  }
}

// Main program
const skillPath = process.argv[2] || '.';

if (!fs.existsSync(skillPath)) {
  console.error('❌ Path does not exist:', skillPath);
  console.log('Usage: node scanner.cjs /path/to/skill');
  process.exit(1);
}

const stat = fs.statSync(skillPath);
const results = stat.isDirectory() ? scanDirectory(skillPath) : scanFile(skillPath);

generateReport(skillPath, results);
