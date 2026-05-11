#!/usr/bin/env node

/**
 * Check DNSSEC status for a domain
 * 
 * Usage:
 *   node dnssec-status.js <domain>
 * 
 * Examples:
 *   node dnssec-status.js example.com
 */

import {
  getDnssecKeys,
  getDomain
} from './gandi-api.js';

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 1) {
  console.error('Usage: node dnssec-status.js <domain>');
  console.error('');
  console.error('Examples:');
  console.error('  node dnssec-status.js example.com');
  process.exit(1);
}

const domain = args[0];

// Format date nicely
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
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
      console.log('⚠️  Warning: Domain does not appear to use Gandi LiveDNS');
      console.log('   DNSSEC management requires Gandi LiveDNS');
      console.log('');
      console.log('Current nameservers:');
      domainInfo.nameservers?.forEach(ns => console.log(`   - ${ns}`));
      console.log('');
    }
    
    // Get DNSSEC keys
    let keys;
    try {
      keys = await getDnssecKeys(domain);
    } catch (err) {
      if (err.statusCode === 404) {
        console.log('❌ DNSSEC: DISABLED');
        console.log('');
        console.log('DNSSEC is not enabled for this domain.');
        console.log('');
        console.log('💡 To enable DNSSEC:');
        console.log(`   node dnssec-enable.js ${domain}`);
        console.log('');
        console.log('⚠️  IMPORTANT: DNSSEC is complex and can break DNS if misconfigured!');
        console.log('   Read the documentation before enabling.');
        return;
      }
      throw err;
    }
    
    // Check if DNSSEC is enabled
    if (!keys || keys.length === 0) {
      console.log('❌ DNSSEC: DISABLED');
      console.log('');
      console.log('No DNSSEC keys found for this domain.');
      console.log('');
      console.log('💡 To enable DNSSEC:');
      console.log(`   node dnssec-enable.js ${domain}`);
      return;
    }
    
    // DNSSEC is enabled
    console.log('✅ DNSSEC: ENABLED');
    console.log('');
    console.log(`📋 DNSSEC Keys (${keys.length} total):`);
    console.log('');
    
    keys.forEach((key, index) => {
      console.log(`${index + 1}. Key #${key.id || key.uuid || 'unknown'}`);
      
      if (key.algorithm) {
        const algoNames = {
          5: 'RSASHA1',
          7: 'RSASHA1-NSEC3-SHA1',
          8: 'RSASHA256',
          10: 'RSASHA512',
          13: 'ECDSAP256SHA256',
          14: 'ECDSAP384SHA384',
          15: 'ED25519',
          16: 'ED448'
        };
        const algoName = algoNames[key.algorithm] || `Unknown (${key.algorithm})`;
        console.log(`   Algorithm: ${key.algorithm} (${algoName})`);
      }
      
      if (key.flags !== undefined) {
        const flagType = key.flags === 256 ? 'ZSK (Zone Signing Key)' : 
                        key.flags === 257 ? 'KSK (Key Signing Key)' : 
                        `Unknown (${key.flags})`;
        console.log(`   Flags: ${key.flags} (${flagType})`);
      }
      
      if (key.public_key) {
        console.log(`   Public Key: ${key.public_key.substring(0, 60)}...`);
      }
      
      if (key.ds) {
        console.log(`   DS Record: ${key.ds}`);
      }
      
      if (key.created_at) {
        console.log(`   Created: ${formatDate(key.created_at)}`);
      }
      
      console.log('');
    });
    
    // Show DS records if available
    const dsRecords = keys.filter(k => k.ds).map(k => k.ds);
    if (dsRecords.length > 0) {
      console.log('📝 DS Records for Registry:');
      console.log('');
      console.log('These DS records should be submitted to your domain registrar:');
      console.log('');
      dsRecords.forEach((ds, index) => {
        console.log(`${index + 1}. ${ds}`);
      });
      console.log('');
      console.log('⚠️  IMPORTANT: DS records must be added at your registrar for DNSSEC to work!');
      console.log('   Without DS records at the registry, DNSSEC validation will fail.');
      console.log('');
    }
    
    console.log('🔍 DNSSEC Validation:');
    console.log('');
    console.log('To verify DNSSEC is working correctly:');
    console.log(`   dig ${domain} +dnssec`);
    console.log(`   dig ${domain} DS`);
    console.log('');
    console.log('Or use online validators:');
    console.log('   https://dnssec-debugger.verisignlabs.com/');
    console.log(`   https://dnsviz.net/d/${domain}/dnssec/`);
    console.log('');
    console.log('💡 To disable DNSSEC:');
    console.log(`   node dnssec-disable.js ${domain} --confirm`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.statusCode === 401) {
      console.error('');
      console.error('Authentication failed. Check your API token.');
    } else if (error.statusCode === 403) {
      console.error('');
      console.error('Permission denied. Ensure your API token has LiveDNS: read scope.');
    } else if (error.response) {
      console.error('API response:', JSON.stringify(error.response, null, 2));
    }
    
    process.exit(1);
  }
}

main();
