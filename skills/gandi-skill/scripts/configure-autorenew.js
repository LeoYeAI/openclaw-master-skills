#!/usr/bin/env node

/**
 * Configure auto-renewal settings for a domain
 * 
 * Usage:
 *   node configure-autorenew.js <domain> <action> [options]
 * 
 * Actions:
 *   status         - Show current auto-renewal status
 *   enable         - Enable auto-renewal
 *   disable        - Disable auto-renewal
 * 
 * Options:
 *   --years <n>    - Auto-renewal duration (1-10 years, default: 1)
 * 
 * Examples:
 *   node configure-autorenew.js example.com status
 *   node configure-autorenew.js example.com enable
 *   node configure-autorenew.js example.com enable --years 2
 *   node configure-autorenew.js example.com disable
 */

import {
  getDomain,
  getAutoRenewal,
  setAutoRenewal
} from './gandi-api.js';

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 2) {
  console.error('Usage: node configure-autorenew.js <domain> <action> [options]');
  console.error('');
  console.error('Actions:');
  console.error('  status         - Show current auto-renewal status');
  console.error('  enable         - Enable auto-renewal');
  console.error('  disable        - Disable auto-renewal');
  console.error('');
  console.error('Options:');
  console.error('  --years <n>    - Auto-renewal duration (1-10 years, default: 1)');
  console.error('');
  console.error('Examples:');
  console.error('  node configure-autorenew.js example.com status');
  console.error('  node configure-autorenew.js example.com enable');
  console.error('  node configure-autorenew.js example.com enable --years 2');
  console.error('  node configure-autorenew.js example.com disable');
  process.exit(1);
}

const domain = args[0];
const action = args[1];
let years = 1;

// Parse options
for (let i = 2; i < args.length; i++) {
  if (args[i] === '--years' && args[i + 1]) {
    years = parseInt(args[i + 1], 10);
    i++;
  }
}

// Validate years
if (isNaN(years) || years < 1 || years > 10) {
  console.error('❌ Error: Years must be between 1 and 10');
  process.exit(1);
}

// Format date nicely
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
}

// Show status
async function showStatus() {
  console.log(`🔍 Checking auto-renewal status for ${domain}...`);
  console.log('');
  
  try {
    const domainInfo = await getDomain(domain);
    
    console.log(`📋 Domain: ${domain}`);
    console.log(`   Expires: ${formatDate(domainInfo.dates.registry_ends_at)}`);
    console.log('');
    
    if (domainInfo.autorenew && domainInfo.autorenew.enabled !== false) {
      console.log('✅ Auto-renewal: ENABLED');
      console.log(`   Duration: ${domainInfo.autorenew.duration || 1} year(s)`);
      if (domainInfo.autorenew.org_id) {
        console.log(`   Organization: ${domainInfo.autorenew.org_id}`);
      }
      console.log('');
      console.log('💡 The domain will automatically renew before expiration.');
      console.log('');
      console.log('To disable auto-renewal:');
      console.log(`   node configure-autorenew.js ${domain} disable`);
    } else {
      console.log('❌ Auto-renewal: DISABLED');
      console.log('');
      console.log('⚠️  Warning: Domain will NOT automatically renew!');
      console.log('   You must manually renew before expiration to prevent losing the domain.');
      console.log('');
      console.log('To enable auto-renewal:');
      console.log(`   node configure-autorenew.js ${domain} enable`);
    }
    
  } catch (error) {
    if (error.statusCode === 404) {
      console.error(`❌ Domain ${domain} not found in your account`);
    } else {
      throw error;
    }
    process.exit(1);
  }
}

// Enable auto-renewal
async function enableAutoRenew() {
  console.log(`⚙️  Enabling auto-renewal for ${domain}...`);
  console.log(`   Duration: ${years} year(s)`);
  console.log('');
  
  try {
    const result = await setAutoRenewal(domain, true, years);
    
    console.log('✅ Auto-renewal enabled successfully!');
    console.log('');
    console.log('📋 Settings:');
    console.log(`   Enabled: ${result.enabled !== false ? 'Yes' : 'No'}`);
    console.log(`   Duration: ${result.duration || years} year(s)`);
    if (result.org_id) {
      console.log(`   Organization: ${result.org_id}`);
    }
    console.log('');
    console.log('💡 Your domain will now automatically renew before expiration.');
    console.log('   You will be charged automatically when renewal occurs.');
    
  } catch (error) {
    if (error.statusCode === 404) {
      console.error(`❌ Domain ${domain} not found in your account`);
    } else if (error.statusCode === 403) {
      console.error('❌ Permission denied. Ensure your API token has Domain: write scope.');
    } else {
      throw error;
    }
    process.exit(1);
  }
}

// Disable auto-renewal
async function disableAutoRenew() {
  console.log(`⚙️  Disabling auto-renewal for ${domain}...`);
  console.log('');
  
  try {
    const result = await setAutoRenewal(domain, false, 1);
    
    console.log('✅ Auto-renewal disabled successfully!');
    console.log('');
    console.log('⚠️  Warning: Domain will NOT automatically renew!');
    console.log('   You must manually renew before expiration to prevent losing the domain.');
    console.log('');
    console.log('💡 To manually renew the domain:');
    console.log(`   node renew-domain.js ${domain}`);
    
  } catch (error) {
    if (error.statusCode === 404) {
      console.error(`❌ Domain ${domain} not found in your account`);
    } else if (error.statusCode === 403) {
      console.error('❌ Permission denied. Ensure your API token has Domain: write scope.');
    } else {
      throw error;
    }
    process.exit(1);
  }
}

// Main function
async function main() {
  try {
    switch (action.toLowerCase()) {
      case 'status':
        await showStatus();
        break;
        
      case 'enable':
        await enableAutoRenew();
        break;
        
      case 'disable':
        await disableAutoRenew();
        break;
        
      default:
        console.error(`❌ Unknown action: ${action}`);
        console.error('Valid actions: status, enable, disable');
        process.exit(1);
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.statusCode === 401) {
      console.error('');
      console.error('Authentication failed. Check your API token.');
    } else if (error.response) {
      console.error('API response:', JSON.stringify(error.response, null, 2));
    }
    
    process.exit(1);
  }
}

main();
