#!/usr/bin/env node

/**
 * cuihua-error-handler - AI-Powered Error Handling Assistant
 * Analyze and generate production-ready error handling
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class ErrorHandler {
  constructor(options = {}) {
    this.options = {
      minimumCoverage: options.minimumCoverage || 80,
      enableRetry: options.enableRetry !== false,
      enableCircuitBreaker: options.enableCircuitBreaker !== false,
      maxRetries: options.maxRetries || 3,
      ...options
    };
    
    this.functions = [];
    this.stats = {
      filesScanned: 0,
      functionsAnalyzed: 0,
      asyncFunctions: 0,
      withErrorHandling: 0,
      missingErrorHandling: 0,
      weakErrorHandling: 0
    };
  }

  /**
   * Analyze file for error handling
   */
  analyzeFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const ext = path.extname(filePath);
    
    if (!['.js', '.ts', '.jsx', '.tsx'].includes(ext)) {
      return;
    }
    
    this.stats.filesScanned++;
    
    // Find all functions
    this.findFunctions(content, filePath);
  }

  /**
   * Find and analyze functions
   */
  findFunctions(content, filePath) {
    // Pattern 1: async function name()
    const asyncFnPattern = /async\s+function\s+(\w+)\s*\([^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}/g;
    let match;
    
    while ((match = asyncFnPattern.exec(content)) !== null) {
      const name = match[1];
      const body = match[2];
      const hasErrorHandling = this.checkErrorHandling(body);
      
      this.addFunction({
        name,
        file: filePath,
        isAsync: true,
        hasErrorHandling,
        body,
        line: this.getLineNumber(content, match.index)
      });
    }

    // Pattern 2: const name = async () =>
    const asyncArrowPattern = /const\s+(\w+)\s*=\s*async\s*\([^)]*\)\s*=>\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}/g;
    
    while ((match = asyncArrowPattern.exec(content)) !== null) {
      const name = match[1];
      const body = match[2];
      const hasErrorHandling = this.checkErrorHandling(body);
      
      this.addFunction({
        name,
        file: filePath,
        isAsync: true,
        hasErrorHandling,
        body,
        line: this.getLineNumber(content, match.index)
      });
    }

    // Pattern 3: Regular functions with potential errors
    const syncFnPattern = /function\s+(\w+)\s*\([^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}/g;
    
    while ((match = syncFnPattern.exec(content)) !== null) {
      const name = match[1];
      const body = match[2];
      
      // Check if it has risky operations
      if (this.hasRiskyOperations(body)) {
        const hasErrorHandling = this.checkErrorHandling(body);
        
        this.addFunction({
          name,
          file: filePath,
          isAsync: false,
          hasErrorHandling,
          body,
          line: this.getLineNumber(content, match.index)
        });
      }
    }
  }

  /**
   * Check if function has error handling
   */
  checkErrorHandling(body) {
    // Has try/catch
    if (/try\s*\{/.test(body)) {
      // Check if catch block is not empty
      const catchMatch = body.match(/catch\s*\([^)]*\)\s*\{([^}]*)\}/);
      if (catchMatch) {
        const catchBody = catchMatch[1].trim();
        
        // Empty catch or just console.log
        if (!catchBody || /^console\.log/.test(catchBody)) {
          return 'weak';
        }
        
        return 'yes';
      }
    }

    // Has .catch()
    if (/\.catch\s*\(/.test(body)) {
      return 'yes';
    }

    return 'no';
  }

  /**
   * Check if function has risky operations
   */
  hasRiskyOperations(body) {
    const riskyPatterns = [
      /JSON\.parse/,
      /parseInt|parseFloat/,
      /\.\w+\s*\(/,  // Method calls
      /fetch\(/,
      /fs\./,
      /require\(/
    ];
    
    return riskyPatterns.some(pattern => pattern.test(body));
  }

  /**
   * Add function to analysis
   */
  addFunction(fn) {
    this.functions.push(fn);
    this.stats.functionsAnalyzed++;
    
    if (fn.isAsync) {
      this.stats.asyncFunctions++;
    }
    
    if (fn.hasErrorHandling === 'yes') {
      this.stats.withErrorHandling++;
    } else if (fn.hasErrorHandling === 'weak') {
      this.stats.weakErrorHandling++;
    } else {
      this.stats.missingErrorHandling++;
    }
  }

  /**
   * Get line number from content offset
   */
  getLineNumber(content, offset) {
    return content.substring(0, offset).split('\n').length;
  }

  /**
   * Generate error handling code
   */
  generateErrorHandling(fn) {
    const { name, isAsync, body, file } = fn;
    
    // Determine risk level
    const risk = this.assessRisk(body, file);
    
    let code = '';
    
    if (isAsync) {
      code = this.generateAsyncErrorHandling(name, body, risk);
    } else {
      code = this.generateSyncErrorHandling(name, body, risk);
    }
    
    return code;
  }

  /**
   * Assess risk level
   */
  assessRisk(body, file) {
    if (/payment|transaction|order|checkout/i.test(file) || /payment|transaction/.test(body)) {
      return 'critical';
    }
    if (/auth|login|token|password/i.test(file) || /auth|token|password/.test(body)) {
      return 'high';
    }
    if (/db|database|query|update|delete/i.test(body)) {
      return 'medium';
    }
    return 'low';
  }

  /**
   * Generate async error handling
   */
  generateAsyncErrorHandling(name, body, risk) {
    const errorClass = risk === 'critical' ? 'CriticalError' : 
                      risk === 'high' ? 'SecurityError' :
                      risk === 'medium' ? 'DataError' : 'AppError';
    
    return `async function ${name}(...args) {
  try {
    // Original logic
${body.trim().split('\n').map(line => '    ' + line).join('\n')}
    
  } catch (error) {
    // Network/timeout errors
    if (error.name === 'AbortError') {
      logger.error('${name} timeout', { args });
      throw new ${errorClass}('Request timeout', { cause: error });
    }
    
    if (error.message.includes('fetch failed')) {
      logger.error('${name} network error', { args, error: error.message });
      throw new ${errorClass}('Network error', { cause: error });
    }
    
    // Re-throw known errors
    if (error instanceof ${errorClass}) {
      logger.error('${name} failed', { args, error: error.message });
      throw error;
    }
    
    // Unexpected errors
    logger.error('${name} unexpected error', { args, error });
    throw new ${errorClass}('Internal error', { cause: error });
  }
}`;
  }

  /**
   * Generate sync error handling
   */
  generateSyncErrorHandling(name, body, risk) {
    return `function ${name}(...args) {
  try {
    // Original logic
${body.trim().split('\n').map(line => '    ' + line).join('\n')}
    
  } catch (error) {
    logger.error('${name} failed', { args, error: error.message });
    throw new Error(\`${name} error: \${error.message}\`, { cause: error });
  }
}`;
  }

  /**
   * Generate report
   */
  generateReport() {
    const coverage = this.stats.functionsAnalyzed > 0
      ? Math.round((this.stats.withErrorHandling / this.stats.functionsAnalyzed) * 100)
      : 0;
    
    let report = `\n🛡️ Error Handling Coverage Report\n`;
    report += `━`.repeat(50) + `\n\n`;
    report += `📁 Files scanned: ${this.stats.filesScanned}\n`;
    report += `🔍 Functions analyzed: ${this.stats.functionsAnalyzed}\n`;
    report += `  - Async functions: ${this.stats.asyncFunctions}\n`;
    report += `  - Sync functions: ${this.stats.functionsAnalyzed - this.stats.asyncFunctions}\n\n`;
    
    report += `📊 Overall coverage: ${coverage}%\n`;
    report += `  ✅ With error handling: ${this.stats.withErrorHandling}\n`;
    report += `  ⚠️  Weak error handling: ${this.stats.weakErrorHandling}\n`;
    report += `  ❌ Missing error handling: ${this.stats.missingErrorHandling}\n\n`;

    // Missing error handling
    if (this.stats.missingErrorHandling > 0) {
      report += `❌ Missing error handling (${this.stats.missingErrorHandling} functions):\n\n`;
      
      const missing = this.functions.filter(fn => fn.hasErrorHandling === 'no');
      const critical = missing.filter(fn => this.assessRisk(fn.body, fn.file) === 'critical');
      const high = missing.filter(fn => this.assessRisk(fn.body, fn.file) === 'high');
      const medium = missing.filter(fn => this.assessRisk(fn.body, fn.file) === 'medium');
      
      if (critical.length > 0) {
        report += `  🔴 Critical (${critical.length}):\n`;
        critical.slice(0, 3).forEach((fn, i) => {
          report += `    ${i + 1}. ${fn.file}:${fn.line} - ${fn.name}()\n`;
          report += `       Risk: Critical - Financial/Security\n`;
        });
        if (critical.length > 3) {
          report += `    ... and ${critical.length - 3} more\n`;
        }
        report += `\n`;
      }
      
      if (high.length > 0) {
        report += `  🟠 High (${high.length}):\n`;
        high.slice(0, 3).forEach((fn, i) => {
          report += `    ${i + 1}. ${fn.file}:${fn.line} - ${fn.name}()\n`;
        });
        if (high.length > 3) {
          report += `    ... and ${high.length - 3} more\n`;
        }
        report += `\n`;
      }
      
      if (medium.length > 0) {
        report += `  🟡 Medium (${medium.length}):\n`;
        medium.slice(0, 2).forEach((fn, i) => {
          report += `    ${i + 1}. ${fn.file}:${fn.line} - ${fn.name}()\n`;
        });
        if (medium.length > 2) {
          report += `    ... and ${medium.length - 2} more\n`;
        }
      }
    }

    // Weak error handling
    if (this.stats.weakErrorHandling > 0) {
      report += `\n⚠️  Weak error handling (${this.stats.weakErrorHandling} functions):\n\n`;
      
      const weak = this.functions.filter(fn => fn.hasErrorHandling === 'weak');
      weak.slice(0, 5).forEach((fn, i) => {
        report += `  ${i + 1}. ${fn.file}:${fn.line} - ${fn.name}()\n`;
        report += `     Issue: Empty or inadequate catch block\n`;
      });
      if (weak.length > 5) {
        report += `  ... and ${weak.length - 5} more\n`;
      }
    }

    report += `\n💡 Recommendations:\n`;
    if (coverage < this.options.minimumCoverage) {
      report += `  - Coverage (${coverage}%) below target (${this.options.minimumCoverage}%)\n`;
      report += `  - Add error handling to ${this.stats.missingErrorHandling} functions\n`;
    }
    if (this.stats.weakErrorHandling > 0) {
      report += `  - Improve ${this.stats.weakErrorHandling} weak error handlers\n`;
    }
    if (coverage >= 90) {
      report += `  - Excellent coverage! Production ready ✨\n`;
    }
    
    return report;
  }

  /**
   * Scan directory recursively
   */
  scanDirectory(dir) {
    const files = fs.readdirSync(dir);
    
    files.forEach(file => {
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);
      
      if (stat.isDirectory()) {
        if (!file.startsWith('.') && file !== 'node_modules' && file !== 'dist' && file !== 'build') {
          this.scanDirectory(filePath);
        }
      } else if (stat.isFile()) {
        this.analyzeFile(filePath);
      }
    });
  }
}

export default ErrorHandler;

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);
  const command = args[0] || 'check';
  const targetPath = args[1] || './src';
  
  const handler = new ErrorHandler({
    minimumCoverage: 80
  });
  
  console.log('🛡️ cuihua-error-handler starting...\n');
  
  if (command === 'check') {
    // Analyze
    if (fs.existsSync(targetPath)) {
      const stat = fs.statSync(targetPath);
      if (stat.isDirectory()) {
        handler.scanDirectory(targetPath);
      } else {
        handler.analyzeFile(targetPath);
      }
    } else {
      console.error(`Error: ${targetPath} not found`);
      process.exit(1);
    }
    
    // Show report
    console.log(handler.generateReport());
    
    // Exit code based on coverage
    const coverage = handler.stats.functionsAnalyzed > 0
      ? Math.round((handler.stats.withErrorHandling / handler.stats.functionsAnalyzed) * 100)
      : 100;
    
    if (coverage < handler.options.minimumCoverage) {
      process.exit(1);
    }
    
  } else if (command === 'generate') {
    // Generate error handling for specific function
    const functionName = args[2];
    
    if (!functionName) {
      console.error('Usage: node error-handler.js generate <file> <functionName>');
      process.exit(1);
    }
    
    handler.analyzeFile(targetPath);
    const fn = handler.functions.find(f => f.name === functionName);
    
    if (!fn) {
      console.error(`Function ${functionName} not found`);
      process.exit(1);
    }
    
    const code = handler.generateErrorHandling(fn);
    console.log('✨ Generated error handling:\n');
    console.log(code);
  }
}
