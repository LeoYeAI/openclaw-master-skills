#!/usr/bin/env node

/**
 * Setup default contact information for domain registration
 * 
 * Saves contact info to ~/.config/gandi/contact.json for reuse in:
 * - Domain registration
 * - Domain renewal
 * - Domain transfers
 * 
 * Usage:
 *   node setup-contact.js
 */

import fs from 'fs';
import path from 'path';
import os from 'os';
import readline from 'readline';

const CONFIG_DIR = path.join(os.homedir(), '.config', 'gandi');
const CONTACT_FILE = path.join(CONFIG_DIR, 'contact.json');

// US state codes (ISO 3166-2 format)
const US_STATES = {
  'AL': 'US-AL', 'AK': 'US-AK', 'AZ': 'US-AZ', 'AR': 'US-AR', 'CA': 'US-CA',
  'CO': 'US-CO', 'CT': 'US-CT', 'DE': 'US-DE', 'FL': 'US-FL', 'GA': 'US-GA',
  'HI': 'US-HI', 'ID': 'US-ID', 'IL': 'US-IL', 'IN': 'US-IN', 'IA': 'US-IA',
  'KS': 'US-KS', 'KY': 'US-KY', 'LA': 'US-LA', 'ME': 'US-ME', 'MD': 'US-MD',
  'MA': 'US-MA', 'MI': 'US-MI', 'MN': 'US-MN', 'MS': 'US-MS', 'MO': 'US-MO',
  'MT': 'US-MT', 'NE': 'US-NE', 'NV': 'US-NV', 'NH': 'US-NH', 'NJ': 'US-NJ',
  'NM': 'US-NM', 'NY': 'US-NY', 'NC': 'US-NC', 'ND': 'US-ND', 'OH': 'US-OH',
  'OK': 'US-OK', 'OR': 'US-OR', 'PA': 'US-PA', 'RI': 'US-RI', 'SC': 'US-SC',
  'SD': 'US-SD', 'TN': 'US-TN', 'TX': 'US-TX', 'UT': 'US-UT', 'VT': 'US-VT',
  'VA': 'US-VA', 'WA': 'US-WA', 'WV': 'US-WV', 'WI': 'US-WI', 'WY': 'US-WY',
  'DC': 'US-DC'
};

function prompt(question, defaultValue = '') {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    const displayQuestion = defaultValue 
      ? `${question} [${defaultValue}]: `
      : `${question}: `;
    
    rl.question(displayQuestion, (answer) => {
      rl.close();
      resolve(answer.trim() || defaultValue);
    });
  });
}

function validateEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

function validatePhone(phone) {
  // International format: +1.5551234567
  const regex = /^\+\d{1,3}\.\d{6,15}$/;
  return regex.test(phone);
}

function formatPhone(phone) {
  // Convert common formats to Gandi format
  // +1-513-410-1823 → +1.5134101823
  // (513) 410-1823 → +1.5134101823 (assumes US)
  
  // Remove all non-digit characters except leading +
  let cleaned = phone.replace(/[^\d+]/g, '');
  
  // If no country code, assume +1 (US)
  if (!cleaned.startsWith('+')) {
    cleaned = '+1' + cleaned;
  }
  
  // Split into country code and number
  const match = cleaned.match(/^(\+\d{1,3})(\d+)$/);
  if (match) {
    return `${match[1]}.${match[2]}`;
  }
  
  return phone; // Return original if can't parse
}

function formatState(state, country) {
  if (country === 'US') {
    const upperState = state.toUpperCase();
    // Check if already in ISO format
    if (upperState.startsWith('US-')) {
      return upperState;
    }
    // Convert abbreviation to ISO format
    if (US_STATES[upperState]) {
      return US_STATES[upperState];
    }
  }
  return state;
}

async function main() {
  console.log('🔧 Gandi Contact Setup\n');
  console.log('This will save your contact information for domain registration.');
  console.log('All information is stored locally at: ' + CONTACT_FILE);
  console.log('');
  
  // Check if contact file exists
  let existingContact = null;
  if (fs.existsSync(CONTACT_FILE)) {
    console.log('⚠️  Contact file already exists!\n');
    const overwrite = await prompt('Overwrite existing contact? (yes/no)', 'no');
    if (overwrite.toLowerCase() !== 'yes') {
      console.log('❌ Setup cancelled.');
      process.exit(0);
    }
    console.log('');
    
    // Load existing for defaults
    try {
      existingContact = JSON.parse(fs.readFileSync(CONTACT_FILE, 'utf8'));
    } catch (err) {
      // Ignore parse errors
    }
  }
  
  const contact = {};
  
  // Type
  console.log('📋 Contact Type');
  const typeInput = await prompt('Type (individual/company)', existingContact?.type || 'individual');
  contact.type = typeInput.toLowerCase();
  console.log('');
  
  // Name
  console.log('👤 Name');
  contact.given = await prompt('First name', existingContact?.given);
  contact.family = await prompt('Last name', existingContact?.family);
  console.log('');
  
  // Email
  console.log('📧 Email');
  let email;
  while (true) {
    email = await prompt('Email address', existingContact?.email);
    if (validateEmail(email)) {
      contact.email = email;
      break;
    }
    console.log('❌ Invalid email format. Please try again.');
  }
  console.log('');
  
  // Phone
  console.log('📞 Phone');
  console.log('   Format: +1.5551234567 (international with country code)');
  let phone;
  while (true) {
    const phoneInput = await prompt('Phone number', existingContact?.phone);
    phone = formatPhone(phoneInput);
    if (validatePhone(phone)) {
      contact.phone = phone;
      console.log(`   ✓ Formatted as: ${phone}`);
      break;
    }
    console.log('❌ Invalid phone format. Use international format: +1.5551234567');
  }
  console.log('');
  
  // Address
  console.log('🏠 Address');
  contact.streetaddr = await prompt('Street address', existingContact?.streetaddr);
  contact.city = await prompt('City', existingContact?.city);
  
  // Country
  const country = await prompt('Country (2-letter code, e.g., US)', existingContact?.country || 'US');
  contact.country = country.toUpperCase();
  
  // State (if applicable)
  if (contact.country === 'US') {
    console.log('   Format: 2-letter abbreviation (e.g., OH for Ohio)');
    const stateInput = await prompt('State', existingContact?.state?.replace('US-', ''));
    contact.state = formatState(stateInput, contact.country);
    console.log(`   ✓ Formatted as: ${contact.state}`);
  } else {
    const state = await prompt('State/Province (optional)', existingContact?.state || '');
    if (state) {
      contact.state = state;
    }
  }
  
  contact.zip = await prompt('ZIP/Postal code', existingContact?.zip);
  console.log('');
  
  // Summary
  console.log('═══════════════════════════════════════════════════════');
  console.log('📋 CONTACT SUMMARY');
  console.log('═══════════════════════════════════════════════════════');
  console.log(`   Name: ${contact.given} ${contact.family}`);
  console.log(`   Email: ${contact.email}`);
  console.log(`   Phone: ${contact.phone}`);
  console.log(`   Address: ${contact.streetaddr}`);
  console.log(`            ${contact.city}, ${contact.state || ''} ${contact.zip}`);
  console.log(`            ${contact.country}`);
  console.log(`   Type: ${contact.type}`);
  console.log('═══════════════════════════════════════════════════════');
  console.log('');
  
  const confirm = await prompt('Save this contact? (yes/no)', 'yes');
  if (confirm.toLowerCase() !== 'yes') {
    console.log('❌ Setup cancelled.');
    process.exit(0);
  }
  
  console.log('');
  console.log('🔒 Privacy Preference');
  console.log('');
  console.log('How should contact information be handled after domain registration?');
  console.log('');
  console.log('   RETAIN (recommended): Keep contact saved for future registrations');
  console.log('   PURGE: Delete contact automatically after each registration');
  console.log('');
  const purgeChoice = await prompt('Auto-purge after registration? (yes/no)', 'no');
  contact._purgeAfterUse = (purgeChoice.toLowerCase() === 'yes');
  
  console.log('');
  if (contact._purgeAfterUse) {
    console.log('   ✓ Contact will be deleted after each successful registration');
  } else {
    console.log('   ✓ Contact will be retained for reuse (delete manually with delete-contact.js)');
  }
  
  // Ensure config directory exists
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
  }
  
  // Save contact
  fs.writeFileSync(CONTACT_FILE, JSON.stringify(contact, null, 2), { mode: 0o600 });
  
  console.log('');
  console.log('✅ Contact saved successfully!');
  console.log('');
  console.log(`   Location: ${CONTACT_FILE}`);
  console.log(`   Permissions: 600 (owner read-write only)`);
  console.log('');
  console.log('💡 This contact will be used automatically for:');
  console.log('   • Domain registration (register-domain.js)');
  console.log('   • Domain renewal (renew-domain.js)');
  console.log('   • Domain transfers');
  console.log('');
  console.log('📝 To view or edit your contact:');
  console.log('   node view-contact.js');
  console.log('   node setup-contact.js  (re-run setup)');
  console.log('');
  console.log('🎉 Setup complete!');
}

main().catch(err => {
  console.error('❌ Error:', err.message);
  process.exit(1);
});
