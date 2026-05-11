#!/usr/bin/env node

/**
 * Manage DNS zone snapshots
 * 
 * Usage:
 *   node manage-snapshots.js <domain> list
 *   node manage-snapshots.js <domain> create <name>
 *   node manage-snapshots.js <domain> restore <snapshot-id> [--confirm]
 * 
 * Examples:
 *   node manage-snapshots.js example.com list
 *   node manage-snapshots.js example.com create "Before DNS migration"
 *   node manage-snapshots.js example.com restore abc123 --confirm
 */

import {
  listSnapshots,
  createSnapshot,
  restoreSnapshot,
  listDnsRecords
} from './gandi-api.js';
import readline from 'readline';

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 2) {
  console.error('Usage: node manage-snapshots.js <domain> <action> [options]');
  console.error('');
  console.error('Actions:');
  console.error('  list                    - List all snapshots');
  console.error('  create <name>           - Create a new snapshot');
  console.error('  restore <id> [--confirm] - Restore from snapshot');
  console.error('');
  console.error('Examples:');
  console.error('  node manage-snapshots.js example.com list');
  console.error('  node manage-snapshots.js example.com create "Before migration"');
  console.error('  node manage-snapshots.js example.com restore abc123 --confirm');
  process.exit(1);
}

const domain = args[0];
const action = args[1];

// Prompt for confirmation
function confirm(message) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    rl.question(message, (answer) => {
      rl.close();
      resolve(answer.toLowerCase().startsWith('y'));
    });
  });
}

// List snapshots
async function listAction() {
  console.log(`📸 Snapshots for ${domain}`);
  console.log('');
  
  try {
    const snapshots = await listSnapshots(domain);
    
    if (!snapshots || snapshots.length === 0) {
      console.log('No snapshots found.');
      console.log('');
      console.log('💡 Create a snapshot with:');
      console.log(`   node manage-snapshots.js ${domain} create "My snapshot"`);
      return;
    }
    
    console.log(`Found ${snapshots.length} snapshot(s):`);
    console.log('');
    
    snapshots.forEach((snapshot, index) => {
      console.log(`${index + 1}. ${snapshot.name || 'Unnamed snapshot'}`);
      console.log(`   ID: ${snapshot.id || snapshot.uuid}`);
      if (snapshot.created_at) {
        const date = new Date(snapshot.created_at);
        console.log(`   Created: ${date.toLocaleString()}`);
      }
      if (snapshot.automatic !== undefined) {
        console.log(`   Type: ${snapshot.automatic ? 'Automatic' : 'Manual'}`);
      }
      console.log('');
    });
    
    console.log('💡 To restore a snapshot:');
    console.log(`   node manage-snapshots.js ${domain} restore <snapshot-id> --confirm`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    if (error.statusCode === 404) {
      console.error('Domain not found or not using Gandi LiveDNS.');
    }
    process.exit(1);
  }
}

// Create snapshot
async function createAction(name) {
  if (!name) {
    console.error('❌ Error: Snapshot name required');
    console.error('Usage: node manage-snapshots.js <domain> create <name>');
    process.exit(1);
  }
  
  console.log(`📸 Creating snapshot for ${domain}`);
  console.log(`   Name: ${name}`);
  console.log('');
  
  try {
    const snapshot = await createSnapshot(domain, name);
    console.log('✅ Snapshot created successfully!');
    console.log(`   ID: ${snapshot.id || snapshot.uuid || 'N/A'}`);
    console.log('');
    console.log('💡 To restore this snapshot later:');
    console.log(`   node manage-snapshots.js ${domain} restore ${snapshot.id || snapshot.uuid} --confirm`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    if (error.statusCode === 403) {
      console.error('Permission denied. Ensure your API token has LiveDNS: write scope.');
    } else if (error.statusCode === 404) {
      console.error('Domain not found or not using Gandi LiveDNS.');
    }
    process.exit(1);
  }
}

// Restore snapshot
async function restoreAction(snapshotId, autoConfirm) {
  if (!snapshotId) {
    console.error('❌ Error: Snapshot ID required');
    console.error('Usage: node manage-snapshots.js <domain> restore <snapshot-id> [--confirm]');
    console.error('');
    console.error('💡 List available snapshots:');
    console.error(`   node manage-snapshots.js ${domain} list`);
    process.exit(1);
  }
  
  console.log(`🔄 Restoring ${domain} from snapshot`);
  console.log(`   Snapshot ID: ${snapshotId}`);
  console.log('');
  
  try {
    // Show current DNS records
    console.log('📋 Current DNS records will be replaced...');
    const currentRecords = await listDnsRecords(domain);
    console.log(`   Currently: ${currentRecords.length} record(s)`);
    console.log('');
    
    // Warn about replacement
    console.log('⚠️  WARNING: This will REPLACE all current DNS records!');
    console.log('All changes made after the snapshot was created will be lost.');
    console.log('');
    
    // Confirm restore
    if (!autoConfirm) {
      const confirmed = await confirm('Are you sure you want to restore this snapshot? (yes/no): ');
      
      if (!confirmed) {
        console.log('❌ Restore cancelled.');
        process.exit(0);
      }
      console.log('');
    }
    
    // Restore the snapshot
    console.log('🔄 Restoring...');
    await restoreSnapshot(domain, snapshotId);
    
    console.log('✅ Snapshot restored successfully!');
    console.log('');
    console.log('⏱️  DNS Propagation:');
    console.log('   - Gandi nameservers: immediate');
    console.log('   - Local cache: ~5 minutes');
    console.log('   - Global: 24-48 hours (worst case)');
    console.log('');
    console.log('🔍 Verify your DNS records:');
    console.log(`   node list-dns.js ${domain}`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    if (error.statusCode === 403) {
      console.error('Permission denied. Ensure your API token has LiveDNS: write scope.');
    } else if (error.statusCode === 404) {
      console.error('Snapshot or domain not found.');
    }
    process.exit(1);
  }
}

// Main function
async function main() {
  try {
    switch (action) {
      case 'list':
        await listAction();
        break;
        
      case 'create':
        const name = args.slice(2).join(' ');
        await createAction(name);
        break;
        
      case 'restore':
        const snapshotId = args[2];
        const autoConfirm = args.includes('--confirm');
        await restoreAction(snapshotId, autoConfirm);
        break;
        
      default:
        console.error(`❌ Unknown action: ${action}`);
        console.error('Valid actions: list, create, restore');
        process.exit(1);
    }
    
  } catch (error) {
    console.error('❌ Unexpected error:', error.message);
    process.exit(1);
  }
}

main();
