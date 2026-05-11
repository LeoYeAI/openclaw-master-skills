#!/usr/bin/env node

/**
 * List DNS zone snapshots
 * Usage: node list-snapshots.js <domain>
 */

import { listSnapshots, sanitizeDomain } from './gandi-api.js';

const [,, rawDomain] = process.argv;

if (!rawDomain) {
  console.error('❌ Usage: node list-snapshots.js <domain>');
  console.error('');
  console.error('Example:');
  console.error('  node list-snapshots.js example.com');
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

async function main() {
  try {
    console.log(`📸 Fetching snapshots for ${domain}...`);
    console.log('');
    
    const snapshots = await listSnapshots(domain);
    
    if (!snapshots || snapshots.length === 0) {
      console.log('ℹ️  No snapshots found for this domain.');
      console.log('');
      console.log('💡 Create a snapshot with:');
      console.log(`   node create-snapshot.js ${domain} "Snapshot name"`);
      return;
    }
    
    console.log(`Found ${snapshots.length} snapshot(s):\n`);
    
    snapshots.forEach((snapshot, index) => {
      const createdDate = new Date(snapshot.created_at);
      const isAutomatic = snapshot.automatic ? ' (automatic)' : '';
      
      console.log(`${index + 1}. ${snapshot.name}${isAutomatic}`);
      console.log(`   ID: ${snapshot.uuid || snapshot.id}`);
      console.log(`   Created: ${createdDate.toLocaleString()}`);
      console.log(`   Records: ${snapshot.zone_data?.length || 'unknown'}`);
      console.log('');
    });
    
    console.log('💡 To restore a snapshot:');
    console.log(`   node restore-snapshot.js ${domain} <snapshot-id>`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.statusCode === 401) {
      console.error('   Authentication failed. Check your API token.');
    } else if (error.statusCode === 403) {
      console.error('   Permission denied. Ensure your token has LiveDNS read access.');
    } else if (error.statusCode === 404) {
      console.error(`   Domain ${domain} not found or not using Gandi LiveDNS.`);
    } else if (error.response) {
      console.error('   API response:', JSON.stringify(error.response, null, 2));
    }
    
    process.exit(1);
  }
}

main();
