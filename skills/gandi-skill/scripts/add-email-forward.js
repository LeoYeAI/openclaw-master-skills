#!/usr/bin/env node

/**
 * Create an email forward
 * Usage: node add-email-forward.js <domain> <mailbox> <destination> [destination2] [destination3]...
 * Examples:
 *   node add-email-forward.js example.com hello you@example.com
 *   node add-email-forward.js example.com contact support@example.com sales@example.com
 *   node add-email-forward.js example.com @ catchall@example.com  # Catch-all
 */

import { createEmailForward, getEmailForward, sanitizeDomain, sanitizeRecordName } from './gandi-api.js';

const [,, rawDomain, rawMailbox, ...destinations] = process.argv;

if (!rawDomain || !rawMailbox || destinations.length === 0) {
  console.error('❌ Usage: node add-email-forward.js <domain> <mailbox> <destination> [destination2]...');
  console.error('');
  console.error('Examples:');
  console.error('  node add-email-forward.js example.com hello you@example.com');
  console.error('  node add-email-forward.js example.com contact support@example.com sales@example.com');
  console.error('  node add-email-forward.js example.com @ catchall@example.com  # Catch-all');
  console.error('');
  console.error('Mailbox:');
  console.error('  - Use @ for catch-all (forwards all unmatched emails)');
  console.error('  - Use specific name (hello, contact, support, etc.)');
  console.error('');
  console.error('Destinations:');
  console.error('  - One or more email addresses to forward to');
  console.error('  - Multiple destinations = email sent to all');
  process.exit(1);
}

// Sanitize inputs for security
let domain, mailbox;
try {
  domain = sanitizeDomain(rawDomain);
  mailbox = sanitizeRecordName(rawMailbox); // Mailbox names follow same rules as DNS records
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
    console.log(`📧 Creating email forward for ${sourceDisplay}@${domain}...`);
    console.log(`   Forwarding to: ${destinations.join(', ')}`);
    console.log('');
    
    // Check if forward already exists
    try {
      const existing = await getEmailForward(domain, mailbox);
      console.error('❌ Email forward already exists!');
      console.error(`   Current destinations: ${existing.destinations.join(', ')}`);
      console.error('');
      console.error('💡 To update this forward:');
      console.error(`   node update-email-forward.js ${domain} ${mailbox} ${destinations.join(' ')}`);
      console.error('');
      console.error('💡 To delete and recreate:');
      console.error(`   node delete-email-forward.js ${domain} ${mailbox}`);
      process.exit(1);
    } catch (error) {
      if (error.statusCode !== 404) {
        throw error;
      }
      // Forward doesn't exist, proceed with creation
    }
    
    // Create the forward
    const result = await createEmailForward(domain, mailbox, destinations);
    
    console.log('✅ Email forward created successfully!');
    console.log('');
    console.log('📋 Forward details:');
    console.log(`   From: ${sourceDisplay}@${domain}`);
    console.log(`   To:`);
    destinations.forEach(dest => {
      console.log(`   → ${dest}`);
    });
    console.log('');
    console.log('⏱️  Email forwarding should be active immediately.');
    console.log('   Test by sending an email to ' + (mailbox === '@' ? 'any address' : mailbox) + '@' + domain);
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
      console.error(`   Domain ${domain} not found or email service not enabled.`);
      console.error('   Enable Gandi Mail service in your domain settings.');
    } else if (error.statusCode === 409) {
      console.error('   Email forward already exists. Use update-email-forward.js instead.');
    } else if (error.response) {
      console.error('   API response:', JSON.stringify(error.response, null, 2));
    }
    
    process.exit(1);
  }
}

main();
