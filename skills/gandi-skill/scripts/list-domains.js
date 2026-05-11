#!/usr/bin/env node

/**
 * List Domains
 * Shows all domains in your Gandi account
 */

import { listDomains } from './gandi-api.js';

console.log('🌐 Listing your Gandi domains...\n');

try {
  const domains = await listDomains();
  
  if (!domains || domains.length === 0) {
    console.log('No domains found in your account.');
    console.log('\nYou can register domains at: https://www.gandi.net');
    process.exit(0);
  }
  
  console.log(`Found ${domains.length} domain${domains.length === 1 ? '' : 's'}:\n`);
  
  domains.forEach((domain, index) => {
    console.log(`${index + 1}. ${domain.fqdn}`);
    
    if (domain.fqdn_unicode !== domain.fqdn) {
      console.log(`   Unicode: ${domain.fqdn_unicode}`);
    }
    
    // Status
    if (domain.status && domain.status.length > 0) {
      console.log(`   Status: ${domain.status.join(', ')}`);
    }
    
    // Expiration
    if (domain.dates && domain.dates.registry_ends_at) {
      const expiresAt = new Date(domain.dates.registry_ends_at);
      const now = new Date();
      const daysUntilExpiry = Math.ceil((expiresAt - now) / (1000 * 60 * 60 * 24));
      
      console.log(`   Expires: ${expiresAt.toDateString()} (${daysUntilExpiry} days)`);
      
      if (daysUntilExpiry < 30) {
        console.log(`   ⚠️  Expires soon!`);
      }
    }
    
    // Auto-renewal (can be boolean or object depending on API response)
    if (domain.autorenew !== undefined) {
      const enabled = typeof domain.autorenew === 'boolean' 
        ? domain.autorenew 
        : domain.autorenew.enabled;
      const status = enabled ? '✅ Enabled' : '❌ Disabled';
      console.log(`   Auto-renew: ${status}`);
    }
    
    // Services
    if (domain.services && domain.services.length > 0) {
      const serviceNames = domain.services
        .map(s => {
          if (s === 'gandilivedns') return 'LiveDNS';
          if (s === 'mailboxv2') return 'Email';
          return s;
        })
        .join(', ');
      console.log(`   Services: ${serviceNames}`);
    }
    
    // Organization
    if (domain.sharing_space && domain.sharing_space.name) {
      console.log(`   Organization: ${domain.sharing_space.name}`);
    }
    
    console.log('');
  });
  
  // Summary
  const expiringSoon = domains.filter(d => {
    if (!d.dates || !d.dates.registry_ends_at) return false;
    const expiresAt = new Date(d.dates.registry_ends_at);
    const now = new Date();
    const days = Math.ceil((expiresAt - now) / (1000 * 60 * 60 * 24));
    return days < 30;
  });
  
  if (expiringSoon.length > 0) {
    console.log(`⚠️  ${expiringSoon.length} domain${expiringSoon.length === 1 ? '' : 's'} expiring within 30 days!`);
  }
  
  const withoutAutorenew = domains.filter(d => {
    if (d.autorenew === undefined) return true; // No autorenew data = disabled
    const enabled = typeof d.autorenew === 'boolean' 
      ? d.autorenew 
      : d.autorenew.enabled;
    return !enabled;
  });
  if (withoutAutorenew.length > 0) {
    console.log(`💡 ${withoutAutorenew.length} domain${withoutAutorenew.length === 1 ? '' : 's'} without auto-renewal`);
  }
  
} catch (error) {
  console.log('❌ Error:', error.message);
  
  if (error.statusCode === 401 || error.statusCode === 403) {
    console.log('\n💡 Authentication error. Run: node test-auth.js');
  }
  
  process.exit(1);
}
