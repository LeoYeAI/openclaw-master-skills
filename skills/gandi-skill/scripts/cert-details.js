#!/usr/bin/env node

/**
 * View detailed SSL certificate information
 * 
 * Usage:
 *   node cert-details.js <certificate-id>
 * 
 * Examples:
 *   node cert-details.js abc123-uuid
 */

import { getCertificate } from './gandi-api.js';

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 1) {
  console.error('Usage: node cert-details.js <certificate-id>');
  console.error('');
  console.error('Examples:');
  console.error('  node cert-details.js abc123-uuid');
  console.error('');
  console.error('💡 To list all certificates:');
  console.error('   node list-certificates.js');
  process.exit(1);
}

const certId = args[0];

// Format date nicely
function formatDate(dateString) {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// Main function
async function main() {
  try {
    console.log(`🔒 Fetching certificate details...`);
    console.log('');
    
    const cert = await getCertificate(certId);
    
    console.log('📋 Certificate Details:');
    console.log('');
    console.log('═'.repeat(70));
    
    // Basic info
    console.log(`Common Name: ${cert.cn || 'N/A'}`);
    
    if (cert.id || cert.uuid) {
      console.log(`ID: ${cert.id || cert.uuid}`);
    }
    
    if (cert.status) {
      const statusEmoji = {
        'valid': '✅',
        'pending': '⏳',
        'expired': '❌',
        'revoked': '🚫'
      };
      console.log(`Status: ${statusEmoji[cert.status] || '❓'} ${cert.status.toUpperCase()}`);
    }
    
    console.log('');
    
    // Subject Alternative Names
    if (cert.alt_names && cert.alt_names.length > 0) {
      console.log('Subject Alternative Names (SANs):');
      cert.alt_names.forEach(san => {
        console.log(`  • ${san}`);
      });
      console.log('');
    }
    
    // Dates
    if (cert.dates) {
      console.log('Dates:');
      if (cert.dates.created_at) {
        console.log(`  Created: ${formatDate(cert.dates.created_at)}`);
      }
      if (cert.dates.valid_from) {
        console.log(`  Valid From: ${formatDate(cert.dates.valid_from)}`);
      }
      if (cert.dates.valid_to) {
        console.log(`  Valid Until: ${formatDate(cert.dates.valid_to)}`);
        
        // Calculate expiry
        const validTo = new Date(cert.dates.valid_to);
        const now = new Date();
        const daysUntilExpiry = Math.ceil((validTo - now) / (1000 * 60 * 60 * 24));
        
        if (daysUntilExpiry < 0) {
          console.log(`  ❌ EXPIRED ${Math.abs(daysUntilExpiry)} days ago`);
        } else if (daysUntilExpiry < 30) {
          console.log(`  ⚠️  Expires in ${daysUntilExpiry} days`);
        } else {
          console.log(`  ✅ ${daysUntilExpiry} days remaining`);
        }
      }
      console.log('');
    }
    
    // Certificate details
    if (cert.package) {
      console.log(`Certificate Type: ${cert.package}`);
    }
    
    if (cert.dcv_method) {
      console.log(`Validation Method: ${cert.dcv_method.toUpperCase()}`);
    }
    
    if (cert.auto_renew !== undefined) {
      console.log(`Auto-renewal: ${cert.auto_renew ? '✅ Enabled' : '❌ Disabled'}`);
    }
    
    if (cert.key_size) {
      console.log(`Key Size: ${cert.key_size} bits`);
    }
    
    if (cert.signature_algorithm) {
      console.log(`Signature Algorithm: ${cert.signature_algorithm}`);
    }
    
    console.log('');
    
    // Additional info
    if (cert.csr) {
      console.log('CSR: Present');
    }
    
    if (cert.crt) {
      console.log('Certificate: Issued');
    }
    
    if (cert.chain) {
      console.log('Certificate Chain: Present');
    }
    
    console.log('');
    console.log('═'.repeat(70));
    
    // Actions
    console.log('');
    console.log('💡 Actions:');
    
    if (cert.status === 'valid') {
      console.log('   • Certificate is valid and active');
    } else if (cert.status === 'pending') {
      console.log('   • Certificate is pending validation');
      console.log('   • Complete domain validation to issue certificate');
    } else if (cert.status === 'expired') {
      console.log('   ⚠️  Certificate has expired!');
      console.log('   • Request a new certificate: node request-certificate.js');
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.statusCode === 401) {
      console.error('');
      console.error('Authentication failed. Check your API token.');
    } else if (error.statusCode === 403) {
      console.error('');
      console.error('Permission denied. Check token scopes.');
    } else if (error.statusCode === 404) {
      console.error('');
      console.error('Certificate not found. Check the certificate ID.');
      console.error('');
      console.error('💡 To list all certificates:');
      console.error('   node list-certificates.js');
    } else if (error.response) {
      console.error('API response:', JSON.stringify(error.response, null, 2));
    }
    
    process.exit(1);
  }
}

main();
