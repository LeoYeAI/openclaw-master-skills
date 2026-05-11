#!/usr/bin/env node

/**
 * Delete an email forward
 * Usage: node delete-email-forward.js <domain> <mailbox> [--force]
 * Examples:
 *   node delete-email-forward.js example.com old
 *   node delete-email-forward.js example.com @ --force  # Delete catch-all
 */

import { deleteEmailForward, getEmailForward } from './gandi-api.js';
import readline from 'readline';

const args = process.argv.slice(2);
const force = args.includes('--force');
const [domain, mailbox] = args.filter(arg => !arg.startsWith('--'));

if (!domain || !mailbox) {
  console.error('❌ Usage: node delete-email-forward.js <domain> <mailbox> [--force]');
  console.error('');
  console.error('Examples:');
  console.error('  node delete-email-forward.js example.com old');
  console.error('  node delete-email-forward.js example.com @ --force  # Delete catch-all');
  console.error('');
  console.error('Options:');
  console.error('  --force    Skip confirmation prompt');
  process.exit(1);
}

async function confirmDelete(forward) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    const sourceDisplay = mailbox === '@' ? '@ (catch-all)' : mailbox;
    console.log('');
    console.log('⚠️  Are you sure you want to delete this email forward?');
    console.log(`   From: ${sourceDisplay}@${domain}`);
    console.log(`   To: ${forward.destinations.join(', ')}`);
    console.log('');
    
    rl.question('Type "delete" to confirm: ', (answer) => {
      rl.close();
      resolve(answer.toLowerCase() === 'delete');
    });
  });
}

async function main() {
  try {
    const sourceDisplay = mailbox === '@' ? '@ (catch-all)' : mailbox;
    console.log(`🔍 Checking email forward for ${sourceDisplay}@${domain}...`);
    console.log('');
    
    // Get current forward
    let forward;
    try {
      forward = await getEmailForward(domain, mailbox);
    } catch (error) {
      if (error.statusCode === 404) {
        console.error(`❌ Email forward not found: ${sourceDisplay}@${domain}`);
        console.error('   The forward may have already been deleted.');
        console.error('');
        console.error('💡 To list all forwards:');
        console.error(`   node list-email-forwards.js ${domain}`);
        process.exit(1);
      }
      throw error;
    }
    
    // Show current forward
    console.log('📋 Email forward to be deleted:');
    console.log(`   From: ${sourceDisplay}@${domain}`);
    console.log(`   To:`);
    forward.destinations.forEach(dest => {
      console.log(`   → ${dest}`);
    });
    
    // Confirm deletion (unless --force)
    if (!force) {
      const confirmed = await confirmDelete(forward);
      if (!confirmed) {
        console.log('');
        console.log('❌ Deletion cancelled.');
        process.exit(0);
      }
    }
    
    // Delete the forward
    console.log('');
    console.log('🗑️  Deleting email forward...');
    await deleteEmailForward(domain, mailbox);
    
    console.log('✅ Email forward deleted successfully!');
    console.log('');
    console.log('⏱️  Changes should be active immediately.');
    console.log(`   Emails to ${sourceDisplay}@${domain} will no longer be forwarded.`);
    console.log('');
    console.log('💡 To list remaining forwards:');
    console.log(`   node list-email-forwards.js ${domain}`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.statusCode === 401) {
      console.error('   Authentication failed. Check your API token.');
    } else if (error.statusCode === 403) {
      console.error('   Permission denied. Ensure your token has Email write access.');
    } else if (error.statusCode === 404) {
      console.error(`   Domain ${domain} or forward not found.`);
    } else if (error.response) {
      console.error('   API response:', JSON.stringify(error.response, null, 2));
    }
    
    process.exit(1);
  }
}

main();
