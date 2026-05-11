#!/usr/bin/env node

/**
 * Restore DNS zone from a snapshot
 * Usage: node restore-snapshot.js <domain> <snapshot-id> [--force]
 */

import { restoreSnapshot, listSnapshots } from './gandi-api.js';
import readline from 'readline';

const args = process.argv.slice(2);
const force = args.includes('--force');
const [domain, snapshotId] = args.filter(arg => !arg.startsWith('--'));

if (!domain || !snapshotId) {
  console.error('❌ Usage: node restore-snapshot.js <domain> <snapshot-id> [--force]');
  console.error('');
  console.error('Examples:');
  console.error('  node restore-snapshot.js example.com abc123-def456-ghi789');
  console.error('  node restore-snapshot.js example.com abc123-def456-ghi789 --force');
  console.error('');
  console.error('Options:');
  console.error('  --force    Skip confirmation prompt');
  console.error('');
  console.error('💡 To list available snapshots:');
  console.error('   node list-snapshots.js ' + (domain || '<domain>'));
  process.exit(1);
}

async function confirmRestore(snapshot) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    console.log('');
    console.log('⚠️  WARNING: This will REPLACE all current DNS records!');
    console.log(`   Restoring snapshot: "${snapshot.name}"`);
    console.log(`   Created: ${new Date(snapshot.created_at).toLocaleString()}`);
    if (snapshot.zone_data) {
      console.log(`   Will restore ${snapshot.zone_data.length} record(s)`);
    }
    console.log('');
    
    rl.question('Are you sure you want to restore? Type "restore" to confirm: ', (answer) => {
      rl.close();
      resolve(answer.toLowerCase() === 'restore');
    });
  });
}

async function main() {
  try {
    console.log(`🔍 Finding snapshot for ${domain}...`);
    console.log('');
    
    // Get snapshot details
    const snapshots = await listSnapshots(domain);
    const snapshot = snapshots.find(s => (s.uuid || s.id) === snapshotId);
    
    if (!snapshot) {
      console.error(`❌ Snapshot not found: ${snapshotId}`);
      console.error('');
      console.error('💡 List available snapshots with:');
      console.error(`   node list-snapshots.js ${domain}`);
      process.exit(1);
    }
    
    console.log('📋 Snapshot details:');
    console.log(`   ID: ${snapshot.uuid || snapshot.id}`);
    console.log(`   Name: ${snapshot.name}`);
    console.log(`   Created: ${new Date(snapshot.created_at).toLocaleString()}`);
    if (snapshot.zone_data) {
      console.log(`   Records: ${snapshot.zone_data.length}`);
    }
    
    // Confirm restoration (unless --force)
    if (!force) {
      const confirmed = await confirmRestore(snapshot);
      if (!confirmed) {
        console.log('');
        console.log('❌ Restoration cancelled.');
        process.exit(0);
      }
    }
    
    // Restore the snapshot
    console.log('');
    console.log('🔄 Restoring DNS zone from snapshot...');
    await restoreSnapshot(domain, snapshotId);
    
    console.log('✅ DNS zone restored successfully!');
    console.log('');
    console.log('⏱️  DNS propagation may take a few minutes.');
    console.log('   Verify with: node list-dns.js ' + domain);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.statusCode === 401) {
      console.error('   Authentication failed. Check your API token.');
    } else if (error.statusCode === 403) {
      console.error('   Permission denied. Ensure your token has LiveDNS write access.');
    } else if (error.statusCode === 404) {
      console.error(`   Domain ${domain} or snapshot not found.`);
    } else if (error.response) {
      console.error('   API response:', JSON.stringify(error.response, null, 2));
    }
    
    process.exit(1);
  }
}

main();
