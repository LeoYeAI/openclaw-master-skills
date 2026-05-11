#!/usr/bin/env node

/**
 * Register a new domain via Gandi Domain API
 * 
 * ⚠️  WARNING: Domain registration costs real money and is NON-REFUNDABLE!
 * 
 * Usage:
 *   node register-domain.js <domain> [options]
 * 
 * Options:
 *   --years <n>              Registration duration (1-10 years, default: 1)
 *   --contact <file>         JSON file with contact info (optional if setup-contact.js run)
 *   --auto-renew             Enable auto-renewal
 *   --purge-contact          Delete saved contact after registration (privacy option)
 *   --dry-run                Check availability and show cost without registering
 * 
 * Examples:
 *   node register-domain.js example.com --dry-run
 *   node register-domain.js example.com --years 1 --auto-renew  (uses saved contact)
 *   node register-domain.js example.com --years 2 --contact owner.json  (custom contact)
 *   node register-domain.js example.com --years 1 --purge-contact  (delete contact after)
 * 
 * Setup:
 *   node setup-contact.js    Save contact info for reuse (run once)
 *   node delete-contact.js   Delete saved contact manually
 */

import {
  checkAvailability,
  registerDomain,
  validateContact,
  setAutoRenewal,
  loadSavedContact
} from './gandi-api.js';
import fs from 'fs';
import path from 'path';
import os from 'os';
import readline from 'readline';

const CONTACT_FILE = path.join(os.homedir(), '.config', 'gandi', 'contact.json');

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 1) {
  console.error('Usage: node register-domain.js <domain> [options]');
  console.error('');
  console.error('Options:');
  console.error('  --years <n>              Registration duration (1-10 years, default: 1)');
  console.error('  --contact <file>         JSON file with contact info (optional if setup-contact.js run)');
  console.error('  --auto-renew             Enable auto-renewal');
  console.error('  --purge-contact          Delete saved contact after registration (privacy option)');
  console.error('  --dry-run                Check and show cost without registering');
  console.error('');
  console.error('⚠️  WARNING: Domain registration costs real money and is NON-REFUNDABLE!');
  console.error('');
  console.error('Examples:');
  console.error('  node register-domain.js example.com --dry-run');
  console.error('  node register-domain.js example.com --years 1 --auto-renew  (uses saved contact)');
  console.error('  node register-domain.js example.com --years 2 --contact owner.json  (custom)');
  console.error('  node register-domain.js example.com --years 1 --purge-contact  (delete after)');
  console.error('');
  console.error('Setup (run once):');
  console.error('  node setup-contact.js    Save contact info for reuse');
  console.error('  node delete-contact.js   Delete saved contact manually');
  console.error('');
  console.error('Contact JSON format (if not using setup-contact.js):');
  console.error('  {');
  console.error('    "given": "John",');
  console.error('    "family": "Doe",');
  console.error('    "email": "john@example.com",');
  console.error('    "streetaddr": "123 Main St",');
  console.error('    "city": "Paris",');
  console.error('    "state": "US-CA",');
  console.error('    "zip": "75001",');
  console.error('    "country": "US",');
  console.error('    "phone": "+1.5551234567",');
  console.error('    "type": "individual"');
  console.error('  }');
  process.exit(1);
}

const domain = args[0];
let years = 1;
let contactFile = null;
let autoRenew = false;
let dryRun = false;
let purgeContact = false;

// Parse options
for (let i = 1; i < args.length; i++) {
  if (args[i] === '--years' && args[i + 1]) {
    years = parseInt(args[i + 1], 10);
    i++;
  } else if (args[i] === '--contact' && args[i + 1]) {
    contactFile = args[i + 1];
    i++;
  } else if (args[i] === '--auto-renew') {
    autoRenew = true;
  } else if (args[i] === '--dry-run') {
    dryRun = true;
  } else if (args[i] === '--purge-contact') {
    purgeContact = true;
  }
}

// Validate years
if (isNaN(years) || years < 1 || years > 10) {
  console.error('❌ Error: Years must be between 1 and 10');
  process.exit(1);
}

// Prompt for confirmation
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

// Main function
async function main() {
  try {
    console.log('🔍 Checking domain availability...');
    console.log('');
    
    // Check availability
    const availability = await checkAvailability([domain]);
    const domainInfo = availability.products?.[0];
    
    if (!domainInfo) {
      console.error('❌ Error: Could not retrieve domain information');
      process.exit(1);
    }
    
    // Check if available
    if (domainInfo.status !== 'available') {
      console.error(`❌ Domain ${domain} is NOT available for registration`);
      console.error(`   Status: ${domainInfo.status}`);
      
      if (domainInfo.status === 'unavailable') {
        console.error('   This domain is already registered.');
      } else if (domainInfo.status === 'pending') {
        console.error('   This domain has a pending registration.');
      }
      
      process.exit(1);
    }
    
    console.log(`✅ ${domain} is AVAILABLE!`);
    console.log('');
    
    // Show pricing
    const prices = domainInfo.prices || [];
    const yearPrice = prices.find(p => p.duration_unit === 'y' && p.min_duration === years);
    const price1Year = prices.find(p => p.duration_unit === 'y' && p.min_duration === 1);
    
    if (!yearPrice && !price1Year) {
      console.error('❌ Error: Pricing information not available');
      process.exit(1);
    }
    
    const registrationPrice = yearPrice || price1Year;
    const pricePerYear = registrationPrice.price_after_taxes;
    const currency = registrationPrice.currency;
    const totalCost = years * pricePerYear;
    
    console.log('💰 Pricing:');
    console.log(`   ${years} year(s): ${totalCost.toFixed(2)} ${currency}`);
    if (years > 1) {
      console.log(`   (${pricePerYear.toFixed(2)} ${currency} per year)`);
    }
    console.log('');
    
    if (domainInfo.discount) {
      console.log(`   💡 Discount applied: ${domainInfo.discount.message}`);
      console.log('');
    }
    
    // If dry-run, stop here
    if (dryRun) {
      console.log('🏁 Dry run complete. No registration performed.');
      console.log('');
      console.log('💡 To register this domain, run without --dry-run and provide contact info:');
      console.log(`   node register-domain.js ${domain} --years ${years} --contact owner.json`);
      return;
    }
    
    // Load and validate contact information
    let contact;
    
    if (contactFile) {
      // Load from specified file
      try {
        const contactData = fs.readFileSync(contactFile, 'utf8');
        contact = JSON.parse(contactData);
      } catch (err) {
        console.error(`❌ Error reading contact file: ${err.message}`);
        process.exit(1);
      }
    } else {
      // Try to load saved contact
      contact = loadSavedContact();
      
      if (!contact) {
        console.error('❌ Error: No contact information found');
        console.error('');
        console.error('Option 1: Setup default contact (recommended)');
        console.error('   node setup-contact.js');
        console.error('');
        console.error('Option 2: Provide contact file for this registration');
        console.error(`   node register-domain.js ${domain} --contact owner.json`);
        console.error('');
        console.error('Contact JSON format:');
        console.error('   {"given":"John","family":"Doe","email":"john@example.com",...}');
        process.exit(1);
      }
      
      console.log('📋 Using saved contact information');
      console.log('');
    }
    
    // Validate contact
    const validation = validateContact(contact);
    if (!validation.valid) {
      console.error('❌ Invalid contact information:');
      validation.errors.forEach(err => console.error(`   - ${err}`));
      console.error('');
      console.error('Required fields:');
      console.error('  given, family, email, streetaddr, city, zip, country, phone, type');
      process.exit(1);
    }
    
    console.log('📋 Contact Information:');
    console.log(`   Name: ${contact.given} ${contact.family}`);
    console.log(`   Email: ${contact.email}`);
    console.log(`   Address: ${contact.streetaddr}, ${contact.city}, ${contact.zip}`);
    console.log(`   Country: ${contact.country}`);
    console.log(`   Phone: ${contact.phone}`);
    console.log(`   Type: ${contact.type}`);
    if (contact.orgname) {
      console.log(`   Organization: ${contact.orgname}`);
    }
    console.log('');
    
    // Show registration summary
    console.log('═══════════════════════════════════════════════════════');
    console.log('                 REGISTRATION SUMMARY');
    console.log('═══════════════════════════════════════════════════════');
    console.log(`   Domain: ${domain}`);
    console.log(`   Duration: ${years} year(s)`);
    console.log(`   Auto-renewal: ${autoRenew ? 'ENABLED' : 'DISABLED'}`);
    console.log(`   TOTAL COST: ${totalCost.toFixed(2)} ${currency}`);
    console.log('═══════════════════════════════════════════════════════');
    console.log('');
    console.log('⚠️  WARNING: DOMAIN REGISTRATION IS NON-REFUNDABLE!');
    console.log('⚠️  You will be charged immediately.');
    console.log('⚠️  This action cannot be undone.');
    console.log('');
    
    // Require explicit "yes" confirmation
    const confirmed = await confirm('Type "yes" to confirm registration: ');
    
    if (!confirmed) {
      console.log('❌ Registration cancelled.');
      process.exit(0);
    }
    
    console.log('');
    console.log('⏳ Registering domain...');
    console.log('');
    
    // Register the domain
    const result = await registerDomain(domain, years, contact);
    
    console.log('✅ Domain registration initiated successfully!');
    console.log('');
    
    if (result.id) {
      console.log(`   Operation ID: ${result.id}`);
    }
    
    if (result.message) {
      console.log(`   Message: ${result.message}`);
    }
    
    console.log('');
    console.log('📧 You should receive a confirmation email shortly.');
    console.log('');
    
    // Set auto-renewal if requested
    if (autoRenew) {
      console.log('⚙️  Enabling auto-renewal...');
      try {
        await setAutoRenewal(domain, true, 1);
        console.log('✅ Auto-renewal enabled');
      } catch (err) {
        console.warn('⚠️  Could not enable auto-renewal:', err.message);
        console.warn('   You can enable it later using configure-autorenew.js');
      }
      console.log('');
    }
    
    // Purge contact if requested or preferred
    const shouldPurge = purgeContact || (contact._purgeAfterUse === true);
    if (shouldPurge && !contactFile) {
      // Only purge if using saved contact (not custom contact file)
      try {
        if (fs.existsSync(CONTACT_FILE)) {
          fs.unlinkSync(CONTACT_FILE);
          console.log('🗑️  Contact information deleted (privacy preference)');
          console.log('');
        }
      } catch (err) {
        console.warn('⚠️  Could not delete contact file:', err.message);
        console.log('');
      }
    }
    
    console.log('🎉 Registration complete!');
    console.log('');
    console.log('📝 Next steps:');
    console.log('   1. Wait for confirmation email');
    console.log('   2. Configure DNS records if needed');
    console.log(`   3. Check domain status: node list-domains.js`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.statusCode === 401) {
      console.error('');
      console.error('Authentication failed. Check your API token.');
    } else if (error.statusCode === 403) {
      console.error('');
      console.error('Permission denied. Ensure your API token has Domain: write scope.');
      console.error('Create a new token at: https://admin.gandi.net/organizations/account/pat');
    } else if (error.statusCode === 402) {
      console.error('');
      console.error('Payment failed. Check your Gandi account balance or payment method.');
    } else if (error.statusCode === 409) {
      console.error('');
      console.error('Domain is no longer available. It may have been registered by someone else.');
    } else if (error.statusCode === 422) {
      console.error('');
      console.error('Validation failed. Check contact information and TLD requirements.');
      if (error.response) {
        console.error('Details:', JSON.stringify(error.response, null, 2));
      }
    } else if (error.response) {
      console.error('API response:', JSON.stringify(error.response, null, 2));
    }
    
    process.exit(1);
  }
}

main();
