#!/usr/bin/env node

/**
 * Check SSL Certificates
 * Probes all Gandi domains for SSL/TLS certificates
 * Shows which domains have SSL and which don't
 */

import { listDomains } from './gandi-api.js';
import tls from 'tls';

/**
 * Check if a domain has SSL and get certificate info
 */
async function checkSSL(domain) {
  return new Promise((resolve) => {
    const options = {
      host: domain,
      port: 443,
      servername: domain,
      rejectUnauthorized: false, // Don't fail on self-signed/expired
      timeout: 5000
    };

    const socket = tls.connect(options, () => {
      try {
        const cert = socket.getPeerCertificate();
        
        if (!cert || Object.keys(cert).length === 0) {
          socket.destroy();
          resolve({
            domain,
            hasSSL: false,
            error: 'No certificate found'
          });
          return;
        }

        // Parse certificate information
        const validFrom = new Date(cert.valid_from);
        const validTo = new Date(cert.valid_to);
        const now = new Date();
        const daysUntilExpiry = Math.ceil((validTo - now) / (1000 * 60 * 60 * 24));
        const isValid = now >= validFrom && now <= validTo;
        
        // Parse issuer
        let issuer = 'Unknown';
        if (cert.issuer) {
          if (cert.issuer.O) {
            issuer = cert.issuer.O;
          } else if (cert.issuer.CN) {
            issuer = cert.issuer.CN;
          }
        }
        
        // Simplify common issuer names
        if (issuer.includes('Let\'s Encrypt') || issuer.includes('R3') || issuer.includes('R10')) {
          issuer = 'Let\'s Encrypt';
        } else if (issuer.includes('Google')) {
          issuer = 'Google Trust Services';
        } else if (issuer.includes('Cloudflare')) {
          issuer = 'Cloudflare';
        } else if (issuer.includes('DigiCert')) {
          issuer = 'DigiCert';
        } else if (issuer.includes('Sectigo')) {
          issuer = 'Sectigo';
        } else if (issuer.includes('Gandi')) {
          issuer = 'Gandi';
        }

        socket.destroy();
        resolve({
          domain,
          hasSSL: true,
          issuer,
          validFrom,
          validTo,
          daysUntilExpiry,
          isValid,
          subject: cert.subject?.CN || domain,
          altNames: cert.subjectaltname?.split(', ').map(n => n.replace('DNS:', '')) || []
        });
      } catch (error) {
        socket.destroy();
        resolve({
          domain,
          hasSSL: false,
          error: error.message
        });
      }
    });

    socket.on('error', (error) => {
      resolve({
        domain,
        hasSSL: false,
        error: error.message
      });
    });

    socket.on('timeout', () => {
      socket.destroy();
      resolve({
        domain,
        hasSSL: false,
        error: 'Connection timeout'
      });
    });

    socket.setTimeout(5000);
  });
}

console.log('🔒 Checking SSL certificates for all Gandi domains...\n');

try {
  const domains = await listDomains();
  
  if (!domains || domains.length === 0) {
    console.log('No domains found.');
    process.exit(0);
  }

  console.log(`Probing ${domains.length} domains... (this may take a minute)\n`);

  // Check all domains concurrently (with some throttling)
  const batchSize = 10;
  const results = [];
  
  for (let i = 0; i < domains.length; i += batchSize) {
    const batch = domains.slice(i, i + batchSize);
    const batchResults = await Promise.all(
      batch.map(d => checkSSL(d.fqdn))
    );
    results.push(...batchResults);
  }

  // Segment results
  const withoutSSL = results.filter(r => !r.hasSSL);
  const withSSL = results.filter(r => r.hasSSL);
  const expired = withSSL.filter(r => !r.isValid && r.daysUntilExpiry < 0);
  const expiringSoon = withSSL.filter(r => r.isValid && r.daysUntilExpiry < 30);

  // Display results
  console.log('═'.repeat(70));
  console.log('RESULTS');
  console.log('═'.repeat(70));
  console.log('');

  // Critical: No SSL
  if (withoutSSL.length > 0) {
    console.log('⚠️  DOMAINS WITHOUT SSL (CRITICAL)');
    console.log('─'.repeat(70));
    withoutSSL.forEach((r, i) => {
      console.log(`${i + 1}. ${r.domain}`);
      console.log(`   Error: ${r.error}`);
      console.log('');
    });
  }

  // Critical: Expired
  if (expired.length > 0) {
    console.log('❌ EXPIRED SSL CERTIFICATES');
    console.log('─'.repeat(70));
    expired.forEach((r, i) => {
      console.log(`${i + 1}. ${r.domain}`);
      console.log(`   Issuer: ${r.issuer}`);
      console.log(`   Expired: ${r.validTo.toDateString()} (${Math.abs(r.daysUntilExpiry)} days ago)`);
      console.log('');
    });
  }

  // Warning: Expiring soon
  if (expiringSoon.length > 0) {
    console.log('⚠️  SSL CERTIFICATES EXPIRING SOON (<30 days)');
    console.log('─'.repeat(70));
    expiringSoon.forEach((r, i) => {
      console.log(`${i + 1}. ${r.domain}`);
      console.log(`   Issuer: ${r.issuer}`);
      console.log(`   Expires: ${r.validTo.toDateString()} (${r.daysUntilExpiry} days)`);
      console.log('');
    });
  }

  // Good: SSL working
  if (withSSL.length > 0) {
    console.log('✅ DOMAINS WITH VALID SSL');
    console.log('─'.repeat(70));
    
    // Group by issuer
    const byIssuer = {};
    withSSL.filter(r => r.isValid && r.daysUntilExpiry >= 30).forEach(r => {
      if (!byIssuer[r.issuer]) {
        byIssuer[r.issuer] = [];
      }
      byIssuer[r.issuer].push(r);
    });

    Object.keys(byIssuer).sort().forEach(issuer => {
      console.log(`\n${issuer}:`);
      byIssuer[issuer].forEach(r => {
        console.log(`  • ${r.domain}`);
        console.log(`    Expires: ${r.validTo.toDateString()} (${r.daysUntilExpiry} days)`);
      });
    });
    console.log('');
  }

  // Summary
  console.log('═'.repeat(70));
  console.log('SUMMARY');
  console.log('═'.repeat(70));
  console.log(`Total domains: ${domains.length}`);
  console.log(`With SSL: ${withSSL.length}`);
  console.log(`Without SSL: ${withoutSSL.length}`);
  if (expired.length > 0) {
    console.log(`Expired: ${expired.length} ⚠️`);
  }
  if (expiringSoon.length > 0) {
    console.log(`Expiring soon: ${expiringSoon.length} ⚠️`);
  }
  
  // Issuer breakdown
  if (withSSL.length > 0) {
    console.log('\nCertificate Issuers:');
    const issuerCounts = {};
    withSSL.forEach(r => {
      issuerCounts[r.issuer] = (issuerCounts[r.issuer] || 0) + 1;
    });
    Object.entries(issuerCounts)
      .sort((a, b) => b[1] - a[1])
      .forEach(([issuer, count]) => {
        console.log(`  ${issuer}: ${count}`);
      });
  }

} catch (error) {
  console.log('❌ Error:', error.message);
  
  if (error.statusCode === 401 || error.statusCode === 403) {
    console.log('\n💡 Authentication error. Run: node test-auth.js');
  }
  
  process.exit(1);
}
