#!/usr/bin/env node

/**
 * List SSL/TLS certificates managed by Gandi
 * 
 * Note: This lists certificates requested/managed through Gandi's certificate API,
 * not external certificates. Use check-ssl.js to probe actual certificate status.
 * 
 * Usage:
 *   node list-certificates.js
 */

import { listCertificates } from './gandi-api.js';

// Format date nicely
function formatDate(dateString) {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
}

// Main function
async function main() {
  try {
    console.log('🔒 Listing SSL/TLS certificates managed by Gandi...');
    console.log('');
    
    const certificates = await listCertificates();
    
    if (!certificates || certificates.length === 0) {
      console.log('📭 No certificates found.');
      console.log('');
      console.log('💡 This lists certificates managed through Gandi\'s certificate API.');
      console.log('   External certificates or Let\'s Encrypt certificates managed');
      console.log('   outside of Gandi won\'t appear here.');
      console.log('');
      console.log('📊 To check actual SSL status of your domains:');
      console.log('   node check-ssl.js');
      console.log('');
      console.log('💡 To request a new certificate:');
      console.log('   node request-certificate.js example.com');
      return;
    }
    
    console.log(`📋 Certificates (${certificates.length} total):`);
    console.log('');
    
    certificates.forEach((cert, index) => {
      console.log(`${index + 1}. ${cert.cn || 'Unknown CN'}`);
      
      if (cert.id || cert.uuid) {
        console.log(`   ID: ${cert.id || cert.uuid}`);
      }
      
      if (cert.status) {
        const statusEmoji = {
          'valid': '✅',
          'pending': '⏳',
          'expired': '❌',
          'revoked': '🚫'
        };
        console.log(`   Status: ${statusEmoji[cert.status] || '❓'} ${cert.status.toUpperCase()}`);
      }
      
      if (cert.alt_names && cert.alt_names.length > 0) {
        console.log(`   SANs: ${cert.alt_names.join(', ')}`);
      }
      
      if (cert.dates) {
        if (cert.dates.created_at) {
          console.log(`   Created: ${formatDate(cert.dates.created_at)}`);
        }
        if (cert.dates.valid_from) {
          console.log(`   Valid From: ${formatDate(cert.dates.valid_from)}`);
        }
        if (cert.dates.valid_to) {
          console.log(`   Expires: ${formatDate(cert.dates.valid_to)}`);
          
          // Calculate days until expiry
          const validTo = new Date(cert.dates.valid_to);
          const now = new Date();
          const daysUntilExpiry = Math.ceil((validTo - now) / (1000 * 60 * 60 * 24));
          
          if (daysUntilExpiry < 0) {
            console.log(`   ❌ Expired ${Math.abs(daysUntilExpiry)} days ago`);
          } else if (daysUntilExpiry < 30) {
            console.log(`   ⚠️  Expires in ${daysUntilExpiry} days`);
          } else {
            console.log(`   ✅ ${daysUntilExpiry} days remaining`);
          }
        }
      }
      
      if (cert.package) {
        console.log(`   Type: ${cert.package}`);
      }
      
      if (cert.dcv_method) {
        console.log(`   Validation: ${cert.dcv_method}`);
      }
      
      if (cert.auto_renew !== undefined) {
        console.log(`   Auto-renew: ${cert.auto_renew ? '✅ Enabled' : '❌ Disabled'}`);
      }
      
      console.log('');
    });
    
    console.log('💡 To view certificate details:');
    console.log('   node cert-details.js <certificate-id>');
    console.log('');
    console.log('💡 To request a new certificate:');
    console.log('   node request-certificate.js example.com');
    console.log('');
    console.log('📊 To check actual SSL status of all domains:');
    console.log('   node check-ssl.js');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.statusCode === 401) {
      console.error('');
      console.error('Authentication failed. Check your API token.');
    } else if (error.statusCode === 403) {
      console.error('');
      console.error('Permission denied. Possible causes:');
      console.error('  - API token lacks required scopes');
      console.error('  - Certificate management not available for your account');
      console.error('');
      console.error('💡 This feature may require a Gandi SSL certificate subscription.');
    } else if (error.statusCode === 404) {
      console.error('');
      console.error('Certificate API endpoint not found.');
      console.error('This feature may not be available or may require different permissions.');
    } else if (error.response) {
      console.error('API response:', JSON.stringify(error.response, null, 2));
    }
    
    process.exit(1);
  }
}

main();
