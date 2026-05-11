#!/usr/bin/env node

/**
 * Disable DNSSEC for a domain
 * 
 * ⚠️  WARNING: Disabling DNSSEC removes cryptographic authentication!
 * 
 * Usage:
 *   node dnssec-disable.js <domain> [--confirm]
 * 
 * Examples:
 *   node dnssec-disable.js example.com
 *   node dnssec-disable.js example.com --confirm
 */

import {
  getDomain,
  getDnssecKeys,
  disableDnssec
} from './gandi-api.js';
import readline from 'readline';

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 1) {
  console.error('Usage: node dnssec-disable.js <domain> [--confirm]');
  console.error('');
  console.error('⚠️  WARNING: Disabling DNSSEC removes cryptographic authentication!');
  console.error('');
  console.error('Examples:');
  console.error('  node dnssec-disable.js example.com');
  console.error('  node dnssec-disable.js example.com --confirm');
  process.exit(1);
}

const domain = args[0];
const autoConfirm = args.includes('--confirm');

// Prompt for confirmation
function confirm(message) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    rl.question(message, (answer) => {
      rl.close();
      resolve(answer.toLowerCase() === 'yes');
    });
  });
}

// Main function
async function main() {
  try {
    console.log(`🔍 Checking DNSSEC status for ${domain}...`);
    console.log('');
    
    // Get domain info
    let domainInfo;
    try {
      domainInfo = await getDomain(domain);
    } catch (err) {
      if (err.statusCode === 404) {
        console.error(`❌ Domain ${domain} not found in your account`);
        process.exit(1);
      }
      throw err;
    }
    
    // Check if DNSSEC is enabled
    let existingKeys;
    try {
      existingKeys = await getDnssecKeys(domain);
    } catch (err) {
      if (err.statusCode === 404) {
        console.log('ℹ️  DNSSEC is already disabled for this domain.');
        console.log('   No action needed.');
        return;
      }
      throw err;
    }
    
    if (!existingKeys || existingKeys.length === 0) {
      console.log('ℹ️  DNSSEC is already disabled for this domain.');
      console.log('   No keys found.');
      return;
    }
    
    console.log('✅ DNSSEC: Currently ENABLED');
    console.log(`   ${existingKeys.length} key(s) found`);
    console.log('');
    
    // Show what will be deleted
    console.log('📋 Keys to be deleted:');
    existingKeys.forEach((key, index) => {
      const keyType = key.flags === 256 ? 'ZSK' : key.flags === 257 ? 'KSK' : 'Unknown';
      console.log(`   ${index + 1}. Key #${key.id || key.uuid} (${keyType})`);
    });
    console.log('');
    
    // Warning and confirmation
    if (!autoConfirm) {
      console.log('═══════════════════════════════════════════════════════');
      console.log('         ⚠️  DNSSEC DISABLEMENT WARNING ⚠️');
      console.log('═══════════════════════════════════════════════════════');
      console.log('');
      console.log('Disabling DNSSEC will:');
      console.log('  • Remove cryptographic authentication from DNS');
      console.log('  • Delete all DNSSEC keys');
      console.log('  • Require DS record removal at registrar');
      console.log('');
      console.log('⚠️  IMPORTANT: After disabling, you MUST:');
      console.log('  1. Remove DS records from your domain registrar');
      console.log('  2. Wait 24-48 hours for DS record removal to propagate');
      console.log('  3. Verify DNSSEC is fully disabled');
      console.log('');
      console.log('⚠️  WARNING: If DS records remain at the registrar after');
      console.log('   disabling DNSSEC, DNS validation will FAIL and your');
      console.log('   domain will be unreachable for DNSSEC-enabled resolvers!');
      console.log('');
      console.log('═══════════════════════════════════════════════════════');
      console.log('');
      
      const confirmed = await confirm('Type "yes" to disable DNSSEC (or anything else to cancel): ');
      
      if (!confirmed) {
        console.log('❌ DNSSEC disablement cancelled.');
        process.exit(0);
      }
      console.log('');
    }
    
    console.log('⏳ Disabling DNSSEC...');
    console.log('');
    
    // Disable DNSSEC (delete all keys)
    const result = await disableDnssec(domain);
    
    if (!result.success) {
      console.error('⚠️  Some keys could not be deleted:');
      result.results.filter(r => !r.success).forEach(r => {
        console.error(`   - Key ${r.key}: ${r.error}`);
      });
      console.log('');
      console.log('💡 Check current status:');
      console.log(`   node dnssec-status.js ${domain}`);
      process.exit(1);
    }
    
    console.log('✅ DNSSEC disabled successfully!');
    console.log(`   Deleted ${existingKeys.length} key(s)`);
    console.log('');
    console.log('═══════════════════════════════════════════════════════');
    console.log('       📝 CRITICAL: REMOVE DS RECORDS NOW!');
    console.log('═══════════════════════════════════════════════════════');
    console.log('');
    console.log('You MUST now remove DS records from your domain registrar:');
    console.log('');
    console.log('1. Log in to your domain registrar');
    console.log('2. Find DNSSEC settings');
    console.log('3. DELETE all DS records');
    console.log('4. Wait 24-48 hours for propagation');
    console.log('');
    console.log('⚠️  FAILURE TO REMOVE DS RECORDS WILL BREAK DNS!');
    console.log('   If DS records remain at the registrar, DNSSEC validation');
    console.log('   will fail and your domain will be unreachable.');
    console.log('');
    console.log('═══════════════════════════════════════════════════════');
    console.log('');
    console.log('📊 Next steps:');
    console.log('');
    console.log('1. Remove DS records from your registrar (CRITICAL!)');
    console.log('2. Wait 24-48 hours for DS record removal to propagate');
    console.log('3. Verify DNSSEC is disabled:');
    console.log(`   dig ${domain} +dnssec`);
    console.log('   (Should not show RRSIG records)');
    console.log('');
    console.log('4. Use online validators to confirm:');
    console.log('   https://dnssec-debugger.verisignlabs.com/');
    console.log(`   https://dnsviz.net/d/${domain}/dnssec/`);
    console.log('');
    console.log('🎉 DNSSEC disablement complete (pending DS record removal)!');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.statusCode === 401) {
      console.error('');
      console.error('Authentication failed. Check your API token.');
    } else if (error.statusCode === 403) {
      console.error('');
      console.error('Permission denied. Ensure your API token has LiveDNS: write scope.');
    } else if (error.statusCode === 404) {
      console.error('');
      console.error('Domain or DNSSEC keys not found.');
    } else if (error.response) {
      console.error('API response:', JSON.stringify(error.response, null, 2));
    }
    
    process.exit(1);
  }
}

main();
