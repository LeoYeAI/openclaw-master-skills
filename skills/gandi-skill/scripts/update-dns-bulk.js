#!/usr/bin/env node

/**
 * Bulk update DNS records from JSON file or stdin
 * Usage: node update-dns-bulk.js <domain> <records.json>
 *        cat records.json | node update-dns-bulk.js <domain>
 * 
 * JSON format:
 * [
 *   {
 *     "rrset_name": "@",
 *     "rrset_type": "A",
 *     "rrset_ttl": 10800,
 *     "rrset_values": ["192.168.1.1"]
 *   },
 *   {
 *     "rrset_name": "www",
 *     "rrset_type": "CNAME",
 *     "rrset_ttl": 10800,
 *     "rrset_values": ["@"]
 *   }
 * ]
 */

import { 
  replaceDnsRecords, 
  listDnsRecords, 
  createSnapshot, 
  validateRecordValue,
  sanitizeDomain,
  sanitizeRecordName,
  sanitizeTTL
} from './gandi-api.js';
import fs from 'fs';
import readline from 'readline';

const args = process.argv.slice(2);
const skipSnapshot = args.includes('--no-snapshot');
const force = args.includes('--force');
const [rawDomain, jsonFile] = args.filter(arg => !arg.startsWith('--'));

if (!rawDomain) {
  console.error('❌ Usage: node update-dns-bulk.js <domain> [records.json] [--no-snapshot] [--force]');
  console.error('');
  console.error('Examples:');
  console.error('  node update-dns-bulk.js example.com records.json');
  console.error('  cat records.json | node update-dns-bulk.js example.com');
  console.error('  node update-dns-bulk.js example.com records.json --no-snapshot --force');
  console.error('');
  console.error('Options:');
  console.error('  --no-snapshot  Skip automatic snapshot creation');
  console.error('  --force        Skip confirmation prompt');
  console.error('');
  console.error('⚠️  WARNING: This replaces ALL DNS records for the domain!');
  console.error('   Records not in the JSON file will be deleted.');
  console.error('   Use --no-snapshot with caution.');
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

async function readInput() {
  if (jsonFile && jsonFile !== '-') {
    // Read from file
    return fs.readFileSync(jsonFile, 'utf8');
  } else {
    // Read from stdin
    const chunks = [];
    for await (const chunk of process.stdin) {
      chunks.push(chunk);
    }
    return Buffer.concat(chunks).toString('utf8');
  }
}

async function confirmReplace(oldCount, newCount) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    console.log('');
    console.log('⚠️  WARNING: This will REPLACE all DNS records!');
    console.log(`   Current records: ${oldCount}`);
    console.log(`   New records: ${newCount}`);
    console.log(`   Records removed: ${Math.max(0, oldCount - newCount)}`);
    console.log('');
    
    rl.question('Are you absolutely sure? Type "replace" to confirm: ', (answer) => {
      rl.close();
      resolve(answer.toLowerCase() === 'replace');
    });
  });
}

function validateRecords(records) {
  const errors = [];
  
  if (!Array.isArray(records)) {
    return ['Records must be an array'];
  }
  
  records.forEach((record, index) => {
    if (!record.rrset_name) {
      errors.push(`Record ${index + 1}: Missing rrset_name`);
    } else {
      // Sanitize record name for security
      try {
        record.rrset_name = sanitizeRecordName(record.rrset_name);
      } catch (error) {
        errors.push(`Record ${index + 1}: Invalid rrset_name - ${error.message}`);
      }
    }
    
    if (!record.rrset_type) {
      errors.push(`Record ${index + 1}: Missing rrset_type`);
    }
    
    if (!record.rrset_values || !Array.isArray(record.rrset_values) || record.rrset_values.length === 0) {
      errors.push(`Record ${index + 1}: Missing or empty rrset_values array`);
    }
    
    // Validate each value
    if (record.rrset_values) {
      record.rrset_values.forEach((value, valueIndex) => {
        const validation = validateRecordValue(record.rrset_type, value);
        if (!validation.valid) {
          errors.push(`Record ${index + 1}, value ${valueIndex + 1}: ${validation.error}`);
        }
      });
    }
    
    // Validate and sanitize TTL if provided
    if (record.rrset_ttl !== undefined) {
      try {
        record.rrset_ttl = sanitizeTTL(record.rrset_ttl);
      } catch (error) {
        errors.push(`Record ${index + 1}: ${error.message}`);
      }
    }
  });
  
  return errors;
}

async function main() {
  try {
    console.log(`📥 Reading DNS records for ${domain}...`);
    
    // Read input JSON
    const inputJson = await readInput();
    let records;
    
    try {
      records = JSON.parse(inputJson);
    } catch (error) {
      console.error('❌ Invalid JSON:', error.message);
      process.exit(1);
    }
    
    // Validate records
    const errors = validateRecords(records);
    if (errors.length > 0) {
      console.error('❌ Validation errors:');
      errors.forEach(err => console.error(`   - ${err}`));
      process.exit(1);
    }
    
    // Get current records for comparison
    console.log('🔍 Fetching current DNS records...');
    const currentRecords = await listDnsRecords(domain);
    
    console.log('');
    console.log('📊 Comparison:');
    console.log(`   Current records: ${currentRecords.length}`);
    console.log(`   New records: ${records.length}`);
    console.log('');
    
    // Show what will change
    console.log('📋 New DNS configuration:');
    records.forEach(record => {
      console.log(`   ${record.rrset_name.padEnd(20)} ${record.rrset_type.padEnd(6)} → ${record.rrset_values.join(', ')}`);
    });
    
    // Create snapshot before making changes (unless --no-snapshot)
    if (!skipSnapshot) {
      console.log('');
      console.log('💾 Creating safety snapshot...');
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const snapshotName = `Before bulk update ${timestamp}`;
      
      try {
        await createSnapshot(domain, snapshotName);
        console.log(`✅ Snapshot created: "${snapshotName}"`);
      } catch (error) {
        console.error('⚠️  Failed to create snapshot:', error.message);
        console.error('   Continuing anyway...');
      }
    }
    
    // Confirm replacement (unless --force)
    if (!force) {
      const confirmed = await confirmReplace(currentRecords.length, records.length);
      if (!confirmed) {
        console.log('');
        console.log('❌ Bulk update cancelled.');
        process.exit(0);
      }
    }
    
    // Replace all records
    console.log('');
    console.log('🔄 Replacing DNS records...');
    await replaceDnsRecords(domain, records);
    
    console.log('✅ DNS records updated successfully!');
    console.log('');
    console.log('⏱️  DNS propagation may take a few minutes.');
    console.log('   Verify with: node list-dns.js ' + domain);
    
    if (!skipSnapshot) {
      console.log('');
      console.log('💡 To restore previous configuration:');
      console.log('   node list-snapshots.js ' + domain);
      console.log('   node restore-snapshot.js ' + domain + ' <snapshot-id>');
    }
    
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
