#!/usr/bin/env node
/**
 * Check and auto-install missing dependencies
 * Run this before any script that requires npm packages
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import { existsSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const execAsync = promisify(exec);

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Check if a package is installed
 */
function isPackageInstalled(packageName) {
  try {
    // Try to resolve the package
    const packagePath = join(__dirname, 'node_modules', packageName);
    return existsSync(packagePath);
  } catch (e) {
    return false;
  }
}

/**
 * Install missing packages
 */
async function installPackages() {
  const packageJsonPath = join(__dirname, 'package.json');
  
  if (!existsSync(packageJsonPath)) {
    console.error('❌ package.json not found in scripts directory');
    return false;
  }
  
  console.log('📦 Installing missing dependencies...');
  console.log('   This may take a moment...');
  
  try {
    // Install dependencies
    await execAsync('npm install', {
      cwd: __dirname,
      env: { ...process.env, NODE_ENV: 'production' }
    });
    
    console.log('✅ Dependencies installed successfully!');
    return true;
  } catch (error) {
    console.error('❌ Failed to install dependencies:', error.message);
    console.error('   Please run manually: cd scripts && npm install');
    return false;
  }
}

/**
 * Check required dependencies
 */
export async function checkDependencies(required = ['ethers']) {
  const missing = [];
  
  for (const pkg of required) {
    if (!isPackageInstalled(pkg)) {
      missing.push(pkg);
    }
  }
  
  if (missing.length > 0) {
    console.log(`⚠️  Missing packages: ${missing.join(', ')}`);
    const success = await installPackages();
    
    if (!success) {
      console.error('❌ Cannot proceed without required dependencies');
      process.exit(1);
    }
    
    return true;
  }
  
  return true;
}

/**
 * CLI usage
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  const packages = process.argv.slice(2);
  const required = packages.length > 0 ? packages : ['ethers'];
  
  console.log('🔍 Checking dependencies...');
  const success = await checkDependencies(required);
  
  if (success) {
    console.log('✅ All dependencies are ready!');
    process.exit(0);
  } else {
    console.error('❌ Failed to setup dependencies');
    process.exit(1);
  }
}
