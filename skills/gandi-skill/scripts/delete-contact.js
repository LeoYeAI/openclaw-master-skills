#!/usr/bin/env node

/**
 * Delete saved contact information
 * 
 * Usage:
 *   node delete-contact.js [--force]
 */

import fs from 'fs';
import path from 'path';
import os from 'os';
import readline from 'readline';

const CONFIG_DIR = path.join(os.homedir(), '.config', 'gandi');
const CONTACT_FILE = path.join(CONFIG_DIR, 'contact.json');

// Check for --force flag
const forceDelete = process.argv.includes('--force');

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

async function main() {
  console.log('🗑️  Delete Saved Contact\n');
  
  if (!fs.existsSync(CONTACT_FILE)) {
    console.log('✅ No contact file found.');
    console.log('');
    console.log(`   Location: ${CONTACT_FILE}`);
    console.log('   Status: Already deleted or never created');
    console.log('');
    return;
  }
  
  // Show what will be deleted
  let contact;
  try {
    contact = JSON.parse(fs.readFileSync(CONTACT_FILE, 'utf8'));
  } catch (err) {
    console.error('⚠️  Warning: Could not read contact file');
  }
  
  if (contact) {
    console.log('📋 Contact to be deleted:');
    console.log(`   Name: ${contact.given} ${contact.family}`);
    console.log(`   Email: ${contact.email}`);
    console.log(`   Location: ${CONTACT_FILE}`);
    console.log('');
  }
  
  // Confirm deletion unless --force
  if (!forceDelete) {
    const shouldDelete = await confirm('Delete this contact? (yes/no): ');
    if (!shouldDelete) {
      console.log('❌ Deletion cancelled.');
      return;
    }
  }
  
  // Delete the file
  try {
    fs.unlinkSync(CONTACT_FILE);
    console.log('');
    console.log('✅ Contact deleted successfully!');
    console.log('');
    console.log('💡 To set up contact again:');
    console.log('   node setup-contact.js');
    console.log('');
  } catch (err) {
    console.error('');
    console.error('❌ Error deleting contact:', err.message);
    process.exit(1);
  }
}

main().catch(err => {
  console.error('❌ Error:', err.message);
  process.exit(1);
});
