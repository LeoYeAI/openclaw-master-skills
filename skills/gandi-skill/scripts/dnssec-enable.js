#!/usr/bin/env node

/**
 * Enable DNSSEC for a domain
 * 
 * ⚠️  WARNING: DNSSEC is complex and can break DNS if misconfigured!
 * 
 * Usage:
 *   node dnssec-enable.js <domain> [options]
 * 
 * Options:
 *   --dry-run    Check status without enabling
 * 
 * Examples:
 *   node dnssec-enable.js example.com --dry-run
 *   node dnssec-enable.js example.com
 */

import {
  getDomain,
  getDnssecKeys,
  enableDnssec
} from './gandi-api.js';
import readline from 'readline';

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 1) {
  console.error('Usage: node dnssec-enable.js <domain> [options]');
  console.error('');
  console.error('Options:');
  console.error('  --dry-run    Check status without enabling');
  console.error('');
  console.error('⚠️  WARNING: DNSSEC is complex and can break DNS if misconfigured!');
  console.error('');
  console.error('Examples:');
  console.error('  node dnssec-enable.js example.com --dry-run');
  console.error('  node dnssec-enable.js example.com');
  process.exit(1);
}

const domain = args[0];
const dryRun = args.includes('--dry-run');

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
    
    // Check if domain uses LiveDNS
    const usesLiveDns = domainInfo.nameservers?.some(ns => ns.includes('gandi.net'));
    
    if (!usesLiveDns) {
      console.error('❌ Error: Domain does not use Gandi LiveDNS');
      console.error('');
      console.error('DNSSEC management requires Gandi LiveDNS nameservers.');
      console.error('');
      console.error('Current nameservers:');
      domainInfo.nameservers?.forEach(ns => console.error(`   - ${ns}`));
      console.error('');
      console.error('💡 To use Gandi LiveDNS:');
      console.error('   1. Update nameservers to Gandi\'s servers');
      console.error('   2. Wait for DNS propagation');
      console.error('   3. Then enable DNSSEC');
      process.exit(1);
    }
    
    // Check if DNSSEC is already enabled
    let existingKeys;
    try {
      existingKeys = await getDnssecKeys(domain);
    } catch (err) {
      if (err.statusCode !== 404) {
        throw err;
      }
      existingKeys = [];
    }
    
    if (existingKeys && existingKeys.length > 0) {
      console.log('⚠️  DNSSEC is already enabled for this domain!');
      console.log('');
      console.log(`   ${existingKeys.length} key(s) found`);
      console.log('');
      console.log('💡 To view DNSSEC status:');
      console.log(`   node dnssec-status.js ${domain}`);
      console.log('');
      console.log('💡 To disable and re-enable DNSSEC:');
      console.log(`   node dnssec-disable.js ${domain} --confirm`);
      console.log(`   node dnssec-enable.js ${domain}`);
      return;
    }
    
    console.log('❌ DNSSEC: Currently DISABLED');
    console.log('');
    
    // If dry-run, stop here
    if (dryRun) {
      console.log('🏁 Dry run complete. No changes made.');
      console.log('');
      console.log('💡 To enable DNSSEC, run without --dry-run:');
      console.log(`   node dnssec-enable.js ${domain}`);
      return;
    }
    
    // Show warnings and information
    console.log('═══════════════════════════════════════════════════════');
    console.log('           ⚠️  DNSSEC ENABLEMENT WARNING ⚠️');
    console.log('═══════════════════════════════════════════════════════');
    console.log('');
    console.log('DNSSEC (Domain Name System Security Extensions) adds');
    console.log('cryptographic authentication to DNS responses.');
    console.log('');
    console.log('⚠️  IMPORTANT CONSIDERATIONS:');
    console.log('');
    console.log('1. COMPLEXITY:');
    console.log('   DNSSEC is complex and requires careful management.');
    console.log('   Misconfiguration can break DNS resolution entirely.');
    console.log('');
    console.log('2. DS RECORDS REQUIRED:');
    console.log('   After enabling, you MUST submit DS records to your');
    console.log('   domain registrar. Without them, DNSSEC validation fails.');
    console.log('');
    console.log('3. TTL CONSIDERATIONS:');
    console.log('   Lower your DNS TTLs before enabling (to 300-600s).');
    console.log('   This allows faster rollback if something goes wrong.');
    console.log('');
    console.log('4. MONITORING:');
    console.log('   After enabling, monitor DNS resolution carefully.');
    console.log('   Use DNSSEC validators to check configuration.');
    console.log('');
    console.log('5. KEY MANAGEMENT:');
    console.log('   DNSSEC keys need periodic rotation (every 1-3 months).');
    console.log('   Gandi handles automatic key rotation, but you should monitor.');
    console.log('');
    console.log('═══════════════════════════════════════════════════════');
    console.log('');
    console.log('💡 Recommended workflow:');
    console.log('   1. Lower DNS TTLs to 300-600 seconds');
    console.log('   2. Wait for old TTL to expire (old TTL × 2)');
    console.log('   3. Enable DNSSEC (this script)');
    console.log('   4. Get DS records from dnssec-status.js');
    console.log('   5. Submit DS records to your registrar');
    console.log('   6. Wait 24-48 hours for DS propagation');
    console.log('   7. Verify with DNSSEC validators');
    console.log('   8. Raise TTLs back to normal (10800s)');
    console.log('');
    
    // Require explicit "yes" confirmation
    const confirmed = await confirm('Type "yes" to enable DNSSEC (or anything else to cancel): ');
    
    if (!confirmed) {
      console.log('❌ DNSSEC enablement cancelled.');
      process.exit(0);
    }
    
    console.log('');
    console.log('⏳ Enabling DNSSEC...');
    console.log('');
    
    // Enable DNSSEC
    await enableDnssec(domain);
    
    // Wait a moment for keys to be generated
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Fetch the generated keys
    let keys;
    try {
      keys = await getDnssecKeys(domain);
    } catch (err) {
      console.log('⚠️  DNSSEC enabled, but could not retrieve keys immediately.');
      console.log('   Keys may take a moment to generate.');
      console.log('');
      console.log('💡 Check status with:');
      console.log(`   node dnssec-status.js ${domain}`);
      return;
    }
    
    console.log('✅ DNSSEC enabled successfully!');
    console.log('');
    console.log(`📋 Generated ${keys.length} key(s)`);
    console.log('');
    
    // Show DS records
    const dsRecords = keys.filter(k => k.ds).map(k => k.ds);
    if (dsRecords.length > 0) {
      console.log('═══════════════════════════════════════════════════════');
      console.log('        📝 CRITICAL: SUBMIT THESE DS RECORDS');
      console.log('═══════════════════════════════════════════════════════');
      console.log('');
      console.log('You MUST submit these DS records to your domain registrar:');
      console.log('');
      dsRecords.forEach((ds, index) => {
        console.log(`${index + 1}. ${ds}`);
      });
      console.log('');
      console.log('═══════════════════════════════════════════════════════');
      console.log('');
      console.log('⚠️  WITHOUT DS RECORDS, DNSSEC VALIDATION WILL FAIL!');
      console.log('   This will break DNS resolution for DNSSEC-enabled resolvers.');
      console.log('');
      console.log('📋 How to submit DS records:');
      console.log('   1. Log in to your domain registrar');
      console.log('   2. Find DNSSEC settings (may be under advanced DNS)');
      console.log('   3. Add the DS record(s) above');
      console.log('   4. Wait 24-48 hours for propagation');
      console.log('');
    } else {
      console.log('⚠️  No DS records returned. Check status:');
      console.log(`   node dnssec-status.js ${domain}`);
      console.log('');
    }
    
    console.log('📊 Next steps:');
    console.log('');
    console.log('1. Submit DS records to your registrar (CRITICAL!)');
    console.log('2. Wait 24-48 hours for DS record propagation');
    console.log('3. Verify DNSSEC with online validators:');
    console.log('   https://dnssec-debugger.verisignlabs.com/');
    console.log(`   https://dnsviz.net/d/${domain}/dnssec/`);
    console.log('');
    console.log('4. Monitor DNS resolution for issues');
    console.log('5. Check status anytime with:');
    console.log(`   node dnssec-status.js ${domain}`);
    console.log('');
    console.log('🎉 DNSSEC enablement complete (pending DS record submission)!');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.statusCode === 401) {
      console.error('');
      console.error('Authentication failed. Check your API token.');
    } else if (error.statusCode === 403) {
      console.error('');
      console.error('Permission denied. Ensure your API token has LiveDNS: write scope.');
    } else if (error.statusCode === 409 || error.statusCode === 422) {
      console.error('');
      console.error('DNSSEC enablement failed. Possible reasons:');
      console.error('  - TLD does not support DNSSEC');
      console.error('  - Domain not using Gandi LiveDNS');
      console.error('  - Domain configuration issues');
      if (error.response) {
        console.error('Details:', JSON.stringify(error.response, null, 2));
      }
    } else if (error.response) {
      console.error('API response:', JSON.stringify(error.response, null, 2));
    }
    
    process.exit(1);
  }
}

main();
