const chalk = require('chalk');
const fs = require('fs-extra');
const path = require('path');

/**
 * Check if current directory is a Next.js project
 */
async function isNextProject(dir = process.cwd()) {
  const packageJsonPath = path.join(dir, 'package.json');
  if (!(await fs.pathExists(packageJsonPath))) {
    return false;
  }
  const packageJson = await fs.readJson(packageJsonPath);
  return packageJson.dependencies?.next !== undefined;
}

/**
 * Check if Supabase is configured
 */
async function isSupabaseConfigured(dir = process.cwd()) {
  const envPath = path.join(dir, '.env.local');
  if (!(await fs.pathExists(envPath))) {
    return false;
  }
  const envContent = await fs.readFile(envPath, 'utf-8');
  return envContent.includes('NEXT_PUBLIC_SUPABASE_URL') && 
         envContent.includes('NEXT_PUBLIC_SUPABASE_ANON_KEY');
}

/**
 * Get Supabase credentials from .env.local
 */
async function getSupabaseCredentials(dir = process.cwd()) {
  const envPath = path.join(dir, '.env.local');
  if (!(await fs.pathExists(envPath))) {
    return null;
  }
  const envContent = await fs.readFile(envPath, 'utf-8');
  const getUrl = () => {
    const match = envContent.match(/NEXT_PUBLIC_SUPABASE_URL=(.+)/);
    return match ? match[1].trim() : null;
  };
  const getKey = () => {
    const match = envContent.match(/NEXT_PUBLIC_SUPABASE_ANON_KEY=(.+)/);
    return match ? match[1].trim() : null;
  };
  return {
    url: getUrl(),
    anonKey: getKey()
  };
}

/**
 * Validate project structure
 */
async function validateProject(dir = process.cwd()) {
  const errors = [];
  if (!(await isNextProject(dir))) {
    errors.push('Not a Next.js project. Run this command in a Next.js project directory.');
  }
  if (!(await isSupabaseConfigured(dir))) {
    errors.push('Supabase not configured. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in .env.local');
  }
  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Print success message
 */
function printSuccess(message) {
  console.log(chalk.green.bold('✅ ' + message));
}

/**
 * Print error message
 */
function printError(message) {
  console.log(chalk.red.bold('❌ ' + message));
}

/**
 * Print info message
 */
function printInfo(message) {
  console.log(chalk.cyan('ℹ️ ' + message));
}

module.exports = {
  isNextProject,
  isSupabaseConfigured,
  getSupabaseCredentials,
  validateProject,
  printSuccess,
  printError,
  printInfo
};
