#!/usr/bin/env node

/**
 * List DNS Records
 * Shows DNS records for a domain
 * 
 * Usage: node list-dns.js <domain>
 */

import { listDnsRecords, getDomain, sanitizeDomain } from './gandi-api.js';

const rawDomain = process.argv[2];

if (!rawDomain) {
  console.log('Usage: node list-dns.js <domain>');
  console.log('Example: node list-dns.js example.com');
  process.exit(1);
}

// Sanitize domain input for security
let domain;
try {
  domain = sanitizeDomain(rawDomain);
} catch (error) {
  console.error(`❌ Invalid domain: ${error.message}`);
  process.exit(1);
}

console.log(`🔍 Fetching DNS records for ${domain}...\n`);

try {
  // First verify domain exists and uses LiveDNS
  let domainInfo;
  try {
    domainInfo = await getDomain(domain);
  } catch (error) {
    if (error.statusCode === 404) {
      console.log(`❌ Domain "${domain}" not found in your account.`);
      console.log('\n💡 Run: node list-domains.js');
      process.exit(1);
    }
    throw error;
  }
  
  // Check if using LiveDNS
  if (!domainInfo.services || !domainInfo.services.includes('gandilivedns')) {
    console.log(`⚠️  Domain "${domain}" is not using Gandi LiveDNS.`);
    console.log('\nCurrent services:', domainInfo.services?.join(', ') || 'none');
    console.log('\n💡 To use LiveDNS, attach it in Gandi admin panel.');
    process.exit(1);
  }
  
  // Get DNS records
  const records = await listDnsRecords(domain);
  
  if (!records || records.length === 0) {
    console.log('No DNS records found.');
    process.exit(0);
  }
  
  console.log(`Found ${records.length} DNS record${records.length === 1 ? '' : 's'}:\n`);
  
  // Group by type for better display
  const recordsByType = {};
  records.forEach(record => {
    if (!recordsByType[record.rrset_type]) {
      recordsByType[record.rrset_type] = [];
    }
    recordsByType[record.rrset_type].push(record);
  });
  
  // Display records grouped by type
  Object.keys(recordsByType).sort().forEach(type => {
    console.log(`\n${type} Records:`);
    console.log('─'.repeat(50));
    
    recordsByType[type].forEach(record => {
      const name = record.rrset_name === '@' ? '@ (root)' : record.rrset_name;
      const ttl = record.rrset_ttl || 10800;
      const ttlStr = formatTTL(ttl);
      
      console.log(`  ${name}`);
      console.log(`    TTL: ${ttlStr}`);
      
      if (record.rrset_values && record.rrset_values.length > 0) {
        record.rrset_values.forEach((value, index) => {
          const prefix = index === 0 ? '    →' : '     ';
          console.log(`${prefix} ${value}`);
        });
      }
      
      console.log('');
    });
  });
  
  // Summary
  console.log('\n' + '═'.repeat(50));
  console.log(`Total: ${records.length} record${records.length === 1 ? '' : 's'} across ${Object.keys(recordsByType).length} type${Object.keys(recordsByType).length === 1 ? '' : 's'}`);
  
  // Show nameservers from domain info
  if (domainInfo.nameservers && domainInfo.nameservers.length > 0) {
    console.log('\nNameservers:');
    domainInfo.nameservers.forEach(ns => {
      console.log(`  • ${ns}`);
    });
  }
  
} catch (error) {
  console.log('❌ Error:', error.message);
  
  if (error.statusCode === 401 || error.statusCode === 403) {
    console.log('\n💡 Authentication error. Run: node test-auth.js');
  } else if (error.statusCode === 404) {
    console.log('\n💡 Domain not found. Check spelling or run: node list-domains.js');
  }
  
  process.exit(1);
}

/**
 * Format TTL value in human-readable form
 */
function formatTTL(seconds) {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m (${seconds}s)`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h (${seconds}s)`;
  return `${Math.floor(seconds / 86400)}d (${seconds}s)`;
}
