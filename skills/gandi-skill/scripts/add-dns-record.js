#!/usr/bin/env node

/**
 * Add or update a DNS record
 * Usage: node add-dns-record.js <domain> <name> <type> <value> [ttl]
 * Examples:
 *   node add-dns-record.js example.com @ A 192.168.1.1
 *   node add-dns-record.js example.com www CNAME @ 300
 *   node add-dns-record.js example.com @ MX "10 mail.example.com." 10800
 */

import { 
  createDnsRecord, 
  validateRecordValue, 
  getDnsRecord,
  sanitizeDomain,
  sanitizeRecordName,
  sanitizeTTL
} from './gandi-api.js';

const [,, rawDomain, rawName, type, ...rest] = process.argv;

// Check required arguments
if (!rawDomain || !rawName || !type || rest.length === 0) {
  console.error('❌ Usage: node add-dns-record.js <domain> <name> <type> <value> [ttl]');
  console.error('');
  console.error('Examples:');
  console.error('  node add-dns-record.js example.com @ A 192.168.1.1');
  console.error('  node add-dns-record.js example.com www CNAME @ 300');
  console.error('  node add-dns-record.js example.com @ MX "10 mail.example.com." 10800');
  console.error('  node add-dns-record.js example.com @ TXT "v=spf1 include:_spf.google.com ~all"');
  console.error('');
  console.error('Record types: A, AAAA, CNAME, MX, TXT, NS, SRV, CAA, PTR');
  console.error('Name: Use @ for root domain, or subdomain name');
  console.error('TTL: Time to live in seconds (300-2592000, default: 10800)');
  process.exit(1);
}

// Sanitize inputs for security
let domain, name, ttl;
try {
  domain = sanitizeDomain(rawDomain);
  name = sanitizeRecordName(rawName);
} catch (error) {
  console.error(`❌ Invalid input: ${error.message}`);
  process.exit(1);
}

// Parse TTL (last argument might be TTL)
let value;
ttl = 10800; // Default 3 hours

if (rest.length > 1) {
  // Check if last arg is a number (TTL)
  const lastArg = rest[rest.length - 1];
  if (!isNaN(parseInt(lastArg))) {
    try {
      ttl = sanitizeTTL(parseInt(lastArg));
      value = rest.slice(0, -1).join(' ');
    } catch (error) {
      console.error(`❌ Invalid TTL: ${error.message}`);
      process.exit(1);
    }
  } else {
    value = rest.join(' ');
  }
} else {
  value = rest[0];
}

async function main() {
  try {
    console.log(`🔄 Adding/updating ${type} record for ${name}.${domain}...`);
    console.log(`   Value: ${value}`);
    console.log(`   TTL: ${ttl}s`);
    console.log('');
    
    // Validate record value
    const validation = validateRecordValue(type, value);
    if (!validation.valid) {
      console.error(`❌ Validation error: ${validation.error}`);
      process.exit(1);
    }
    
    // Check if record already exists
    let existingRecord = null;
    try {
      existingRecord = await getDnsRecord(domain, name, type);
      console.log('ℹ️  Record already exists, will be replaced:');
      console.log(`   Current value(s): ${existingRecord.rrset_values.join(', ')}`);
      console.log(`   Current TTL: ${existingRecord.rrset_ttl}s`);
      console.log('');
    } catch (error) {
      // Record doesn't exist, that's okay
      console.log('ℹ️  Creating new record...');
      console.log('');
    }
    
    // Create/update the record
    const result = await createDnsRecord(domain, name, type, [value], ttl);
    
    if (result.statusCode === 201) {
      console.log('✅ DNS record created successfully!');
    } else if (result.statusCode === 200) {
      console.log('✅ DNS record updated successfully!');
    } else {
      console.log(`✅ DNS record saved (status: ${result.statusCode})`);
    }
    
    console.log('');
    console.log('📋 Record details:');
    console.log(`   Domain: ${domain}`);
    console.log(`   Name: ${name}`);
    console.log(`   Type: ${type}`);
    console.log(`   Value: ${value}`);
    console.log(`   TTL: ${ttl}s (${Math.floor(ttl / 60)} minutes)`);
    console.log('');
    console.log('⏱️  DNS propagation may take a few minutes.');
    console.log('   Verify with: dig @ns1.gandi.net ' + (name === '@' ? domain : `${name}.${domain}`) + ' ' + type);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.statusCode === 401) {
      console.error('   Authentication failed. Check your API token.');
    } else if (error.statusCode === 403) {
      console.error('   Permission denied. Ensure your token has LiveDNS write access.');
    } else if (error.statusCode === 404) {
      console.error(`   Domain ${domain} not found or not using Gandi LiveDNS.`);
    } else if (error.response) {
      console.error('   API response:', JSON.stringify(error.response, null, 2));
    }
    
    process.exit(1);
  }
}

main();
