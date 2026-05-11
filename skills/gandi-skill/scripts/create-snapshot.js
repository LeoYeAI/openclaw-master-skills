#!/usr/bin/env node

/**
 * Create a DNS zone snapshot
 * Usage: node create-snapshot.js <domain> [name]
 */

import { createSnapshot } from './gandi-api.js';

const args = process.argv.slice(2);
const [domain, ...nameParts] = args;
const name = nameParts.join(' ') || `Manual snapshot ${new Date().toISOString()}`;

if (!domain) {
  console.error('❌ Usage: node create-snapshot.js <domain> [name]');
  console.error('');
  console.error('Examples:');
  console.error('  node create-snapshot.js example.com');
  console.error('  node create-snapshot.js example.com "Before migration"');
  console.error('  node create-snapshot.js example.com Before big changes');
  process.exit(1);
}

async function main() {
  try {
    console.log(`📸 Creating snapshot for ${domain}...`);
    console.log(`   Name: "${name}"`);
    console.log('');
    
    const snapshot = await createSnapshot(domain, name);
    
    console.log('✅ Snapshot created successfully!');
    console.log('');
    console.log('📋 Snapshot details:');
    console.log(`   ID: ${snapshot.uuid || snapshot.id}`);
    console.log(`   Name: ${snapshot.name}`);
    console.log(`   Created: ${new Date(snapshot.created_at).toLocaleString()}`);
    if (snapshot.zone_data) {
      console.log(`   Records: ${snapshot.zone_data.length}`);
    }
    console.log('');
    console.log('💡 To restore this snapshot later:');
    console.log(`   node restore-snapshot.js ${domain} ${snapshot.uuid || snapshot.id}`);
    console.log('');
    console.log('💡 To list all snapshots:');
    console.log(`   node list-snapshots.js ${domain}`);
    
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
