#!/usr/bin/env node

/**
 * Update an email forward
 * Usage: node update-email-forward.js <domain> <mailbox> <destination> [destination2]...
 * Examples:
 *   node update-email-forward.js example.com hello newemail@example.com
 *   node update-email-forward.js example.com contact support@example.com sales@example.com
 */

import { updateEmailForward, getEmailForward, sanitizeDomain, sanitizeRecordName } from './gandi-api.js';

const [,, rawDomain, rawMailbox, ...destinations] = process.argv;

if (!rawDomain || !rawMailbox || destinations.length === 0) {
  console.error('❌ Usage: node update-email-forward.js <domain> <mailbox> <destination> [destination2]...');
  console.error('');
  console.error('Examples:');
  console.error('  node update-email-forward.js example.com hello newemail@example.com');
  console.error('  node update-email-forward.js example.com contact support@example.com sales@example.com');
  console.error('');
  console.error('This replaces all existing destinations with the new ones.');
  process.exit(1);
}

// Sanitize inputs for security
let domain, mailbox;
try {
  domain = sanitizeDomain(rawDomain);
  mailbox = sanitizeRecordName(rawMailbox);
} catch (error) {
  console.error(`❌ Invalid input: ${error.message}`);
  process.exit(1);
}

// Validate email addresses
function isValidEmail(email) {
  return email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
}

async function main() {
  try {
    // Validate destination emails
    const invalidEmails = destinations.filter(email => !isValidEmail(email));
    if (invalidEmails.length > 0) {
      console.error('❌ Invalid email address(es):');
      invalidEmails.forEach(email => console.error(`   - ${email}`));
      process.exit(1);
    }
    
    const sourceDisplay = mailbox === '@' ? '@ (catch-all)' : mailbox;
    console.log(`🔄 Updating email forward for ${sourceDisplay}@${domain}...`);
    console.log('');
    
    // Get current forward
    let currentForward;
    try {
      currentForward = await getEmailForward(domain, mailbox);
      console.log('Current destinations:');
      currentForward.destinations.forEach(dest => {
        console.log(`   → ${dest}`);
      });
      console.log('');
      console.log('New destinations:');
      destinations.forEach(dest => {
        console.log(`   → ${dest}`);
      });
      console.log('');
    } catch (error) {
      if (error.statusCode === 404) {
        console.error('❌ Email forward not found!');
        console.error('');
        console.error('💡 To create a new forward:');
        console.error(`   node add-email-forward.js ${domain} ${mailbox} ${destinations.join(' ')}`);
        process.exit(1);
      }
      throw error;
    }
    
    // Update the forward
    await updateEmailForward(domain, mailbox, destinations);
    
    console.log('✅ Email forward updated successfully!');
    console.log('');
    console.log('📋 Updated forward:');
    console.log(`   From: ${sourceDisplay}@${domain}`);
    console.log(`   To:`);
    destinations.forEach(dest => {
      console.log(`   → ${dest}`);
    });
    console.log('');
    console.log('⏱️  Changes should be active immediately.');
    console.log('');
    console.log('💡 To list all forwards:');
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
