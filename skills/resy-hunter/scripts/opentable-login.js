#!/usr/bin/env node
// opentable-login.js — Manual login flow for OpenTable
// Usage: node opentable-login.js
//
// Opens a VISIBLE browser window to OpenTable's login page.
// Log in manually (email + OTP). The script detects when login
// is complete and saves session cookies for headless reuse.
//
// Session saved to: ~/.openclaw/data/resy-hunter/opentable-session.json

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const DATA_DIR = path.join(process.env.HOME, '.openclaw/data/resy-hunter');
const SESSION_FILE = path.join(DATA_DIR, 'opentable-session.json');

async function main() {
  fs.mkdirSync(DATA_DIR, { recursive: true });

  console.log('🔐 Opening OpenTable login page...');
  console.log('   Log in with your email and complete the OTP verification.');
  console.log('   The browser will close automatically when login is detected.\n');

  const browser = await chromium.launch({
    headless: false,
    args: ['--no-sandbox'],
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
  });

  const page = await context.newPage();

  // Navigate to profile page — will redirect to login if not authenticated
  await page.goto('https://www.opentable.com/my/profile', {
    waitUntil: 'domcontentloaded',
    timeout: 30000,
  });

  console.log('⏳ Waiting for you to log in (5 minute timeout)...');

  let loggedIn = false;
  const maxWait = 300000; // 5 minutes
  const startTime = Date.now();

  while (!loggedIn && (Date.now() - startTime) < maxWait) {
    await page.waitForTimeout(2000);

    loggedIn = await page.evaluate(() => {
      const url = window.location.href;
      // Detect successful login: on profile page, or see avatar/sign-out elements
      const onProfile = url.includes('/my/') && !url.includes('login') && !url.includes('signin');
      const hasAvatar = !!(
        document.querySelector('[data-test="user-avatar"]') ||
        document.querySelector('[class*="avatar"]') ||
        document.querySelector('[class*="profile-icon"]')
      );
      const hasSignOut = !!(
        document.querySelector('a[href*="logout"]') ||
        document.querySelector('[data-test="sign-out"]')
      );
      return onProfile || hasAvatar || hasSignOut;
    });

    // Also check if we navigated away from login page
    if (!loggedIn) {
      const currentUrl = page.url();
      if (!currentUrl.includes('login') && !currentUrl.includes('signin') && !currentUrl.includes('auth')) {
        // Give it a moment to settle
        await page.waitForTimeout(2000);
        loggedIn = true;
      }
    }
  }

  if (!loggedIn) {
    console.log('❌ Login timed out (5 minutes). Try again.');
    await browser.close();
    process.exit(1);
  }

  // Save session
  await context.storageState({ path: SESSION_FILE });
  console.log(`\n✅ Login successful! Session saved.`);
  console.log(`   Path: ${SESSION_FILE}`);
  console.log('   Future OpenTable checks will use this session automatically.');

  await browser.close();
}

main().catch(err => {
  console.error(`❌ Error: ${err.message}`);
  process.exit(1);
});
