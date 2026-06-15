/**
 * web-autopilot: Login Helper
 * Supports both automatic (headless) and manual (headed) login.
 * 
 * Auto-login flow:
 *   1. Read encrypted credentials from credentials.enc
 *   2. Launch headless browser → navigate to SSO
 *   3. Fill login form → submit
 *   4. Follow redirect chain until app domain reached
 *   5. Capture cookies/tokens → save session
 * 
 * Manual fallback:
 *   If auto-login fails or no credentials stored, opens headed browser
 *   for user to complete login manually.
 */

import { Session, DEFAULT_SESSION_DIR } from './session';
import { getCredential, Credential } from './credentials';

// ─── Types ───────────────────────────────────────────────────────────────────

export interface LoginOptions {
  loginUrl: string;        // SSO login page URL
  appDomain: string;       // Target app domain (e.g. app.example.com)
  timeoutMs?: number;      // Max wait time (default 3 min)
  sessionDir?: string;
  headless?: boolean;      // Force headless (default: auto-detect)
  appForwardUrl?: string;  // Optional: direct URL to navigate to app after SSO login
  appId?: string;          // Optional: SSO portal app ID for forward
  onToken?: (token: string, staffId?: string, staffName?: string) => void;  // Callback for token-based auth
}

// ─── Auto Login ──────────────────────────────────────────────────────────────

async function tryAutoLogin(options: LoginOptions): Promise<Session | null> {
  const { loginUrl, appDomain, timeoutMs = 3 * 60 * 1000, sessionDir = DEFAULT_SESSION_DIR } = options;
  const loginDomain = new URL(loginUrl).hostname;
  const cred = getCredential(loginDomain);
  if (!cred) {
    console.log('ℹ️  No stored credentials for', loginDomain);
    return null;
  }

  console.log(`🔄 Auto-login: ${cred.username} @ ${loginDomain}`);

  const pw = require('playwright');
  const browser = await pw.chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 }, ignoreHTTPSErrors: true });

  try {
    const page = await context.newPage();

    // Step 1: Navigate to SSO login page
    await page.goto(loginUrl, { waitUntil: 'domcontentloaded', timeout: 30_000 });
    await page.waitForTimeout(2000);

    // Step 2: Try API-based login first (faster, more reliable)
    const apiLoginSuccess = await tryApiLogin(page, context, loginDomain, cred);
    if (!apiLoginSuccess) {
      // Step 2b: Fall back to form-based login
      const formSuccess = await tryFormLogin(page, cred);
      if (!formSuccess) {
        console.log('⚠️  Auto-login failed: could not fill login form');
        await browser.close();
        return null;
      }
    }

    // Step 3: Wait for SSO redirect to complete
    await page.waitForTimeout(3000);

    // Step 4: If app not reached yet, try navigating to app via SSO portal
    const currentUrl = page.url();
    if (!currentUrl.includes(appDomain)) {
      if (options.appForwardUrl) {
        await page.goto(options.appForwardUrl, { waitUntil: 'domcontentloaded', timeout: 30_000 });
      } else if (options.appId) {
        const forwardUrl = `${loginUrl.replace(/\/+$/, '')}/api/sso/app/forward?appId=${options.appId}`;
        await page.goto(forwardUrl, { waitUntil: 'domcontentloaded', timeout: 30_000 });
      }
      await page.waitForTimeout(3000);
    }

    // Step 5: Wait until we land on the app domain
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
      const url = page.url();
      if (url.includes(appDomain)) break;
      // Check all pages in context (SSO may open new tabs)
      const pages = context.pages();
      const appPage = pages.find((p: any) => p.url().includes(appDomain));
      if (appPage) break;
      await page.waitForTimeout(1000);
    }

    // Step 6: Collect cookies from all pages
    const allCookies = await context.cookies();

    // Step 7: Check for token-based auth (e.g., accessToken in URL query)
    const pages = context.pages();
    for (const p of pages) {
      const url = p.url();
      if (url.includes(appDomain) && url.includes('accessToken=')) {
        const u = new URL(url);
        const token = u.searchParams.get('accessToken') || '';
        if (token && options.onToken) {
          options.onToken(token);
        }
      }
    }

    await browser.close();

    // Save session
    const session = new Session(appDomain, loginUrl, sessionDir);
    session.importCookies(allCookies.map((c: any) => ({ name: c.name, value: c.value, domain: c.domain })));
    session.save();
    console.log(`✅ Auto-login successful. Cookies: ${allCookies.length}`);
    return session;

  } catch (err: any) {
    console.log(`⚠️  Auto-login error: ${err.message}`);
    await browser.close();
    return null;
  }
}

/** Try logging in via direct API call (SSO REST API style) */
async function tryApiLogin(page: any, context: any, loginDomain: string, cred: Credential): Promise<boolean> {
  if (!cred.loginApiPath) return false;

  try {
    const loginApiUrl = `https://${loginDomain}${cred.loginApiPath}?_=${Date.now()}`;
    const body: any = {};

    if (cred.authType) {
      // SSO API format: { authType, credential: { username, password } }
      body.authType = cred.authType;
      body.credential = { username: cred.username, password: cred.password };
    } else {
      body.username = cred.username;
      body.password = cred.password;
    }

    if (cred.extraFields) {
      Object.assign(body, cred.extraFields);
    }

    const response = await page.evaluate(async (params: { url: string; body: any }) => {
      const resp = await fetch(params.url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params.body),
        credentials: 'include',
      });
      return { status: resp.status, ok: resp.ok };
    }, { url: loginApiUrl, body });

    if (response.ok) {
      console.log('  ✅ API login successful');
      // Follow the standard SSO redirect
      await page.goto(`https://${loginDomain}/api/sso/login`, { waitUntil: 'domcontentloaded', timeout: 15_000 }).catch(() => {});
      return true;
    }
    console.log(`  ⚠️ API login returned ${response.status}`);
    return false;
  } catch (err: any) {
    console.log(`  ⚠️ API login failed: ${err.message}`);
    return false;
  }
}

/** Try logging in via form fill (fallback for non-API login pages) */
async function tryFormLogin(page: any, cred: Credential): Promise<boolean> {
  try {
    // Common username field selectors
    const usernameSelectors = [
      'input[name="username"]', 'input[name="userName"]', 'input[name="email"]',
      'input[name="account"]', 'input[name="loginName"]',
      'input[type="text"]:not([name="captcha"])',
      'input[type="email"]',
    ];
    // Common password field selectors
    const passwordSelectors = [
      'input[name="password"]', 'input[name="passwd"]',
      'input[type="password"]',
    ];

    let filled = false;
    for (const sel of usernameSelectors) {
      const el = await page.$(sel);
      if (el) {
        await el.fill(cred.username);
        filled = true;
        break;
      }
    }
    if (!filled) return false;

    for (const sel of passwordSelectors) {
      const el = await page.$(sel);
      if (el) {
        await el.fill(cred.password);
        break;
      }
    }

    // Submit: try button click, then Enter key
    const submitSelectors = [
      'button[type="submit"]', 'input[type="submit"]',
      'button:has-text("登录")', 'button:has-text("Login")', 'button:has-text("Sign in")',
      '.login-btn', '#login-btn', '.submit-btn',
    ];
    for (const sel of submitSelectors) {
      const btn = await page.$(sel);
      if (btn) {
        await btn.click();
        console.log('  ✅ Form login submitted');
        return true;
      }
    }
    // Fallback: press Enter on password field
    await page.keyboard.press('Enter');
    console.log('  ✅ Form login submitted (Enter key)');
    return true;
  } catch (err: any) {
    console.log(`  ⚠️ Form login failed: ${err.message}`);
    return false;
  }
}

// ─── Manual Login (Fallback) ─────────────────────────────────────────────────

async function doManualLogin(options: LoginOptions): Promise<Session> {
  const { loginUrl, appDomain, timeoutMs = 5 * 60 * 1000, sessionDir = DEFAULT_SESSION_DIR } = options;
  console.log(`\n🔐 Opening browser for manual login...\n   URL: ${loginUrl}\n`);

  const pw = require('playwright');
  const browser = await pw.chromium.launch({ headless: false });
  const context = await browser.newContext({ viewport: null, ignoreHTTPSErrors: true });
  const page = await context.newPage();
  await page.goto(loginUrl, { waitUntil: 'domcontentloaded', timeout: 30_000 });

  console.log('📋 Complete the login in the browser. Will auto-detect when done.\n');

  const loginDomain = new URL(loginUrl).hostname;

  // Auto-detect: wait until browser navigates away from login domain or reaches app domain
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    await page.waitForTimeout(2000);
    const pages = context.pages();
    for (const p of pages) {
      const url = p.url();
      if (url.includes(appDomain)) {
        console.log(`✅ Login detected (reached ${appDomain})`);
        // Handle token callback
        if (url.includes('accessToken=') && options.onToken) {
          const u = new URL(url);
          options.onToken(u.searchParams.get('accessToken') || '');
        }
        await page.waitForTimeout(2000); // Let cookies settle
        const allCookies = await context.cookies();
        await browser.close();
        const session = new Session(appDomain, loginUrl, sessionDir);
        session.importCookies(allCookies.map((c: any) => ({ name: c.name, value: c.value, domain: c.domain })));
        session.save();
        console.log(`✅ Session saved. Cookies: ${allCookies.length}`);
        return session;
      }
    }
  }

  // Timeout fallback: save whatever cookies we have
  const allCookies = await context.cookies();
  await browser.close();
  const session = new Session(appDomain, loginUrl, sessionDir);
  session.importCookies(allCookies.map((c: any) => ({ name: c.name, value: c.value, domain: c.domain })));
  session.save();
  return session;
}

// ─── Public API ──────────────────────────────────────────────────────────────

/**
 * Ensure a valid session exists. If expired:
 *   1. Try auto-login with stored credentials (headless)
 *   2. Fall back to manual login (headed browser)
 */
export async function doLogin(options: LoginOptions): Promise<Session> {
  // Try auto-login first
  const autoSession = await tryAutoLogin(options);
  if (autoSession) return autoSession;

  // Fall back to manual login
  return doManualLogin(options);
}

/** Backward compat */
export const doSSOLogin = (opts: { ssoUrl: string; appDomain: string; timeoutMs?: number; sessionDir?: string }) =>
  doLogin({ loginUrl: opts.ssoUrl, appDomain: opts.appDomain, timeoutMs: opts.timeoutMs, sessionDir: opts.sessionDir });

export async function ensureSession(appDomain: string, loginUrl: string, options: Partial<LoginOptions> = {}): Promise<Session> {
  const session = new Session(appDomain, loginUrl);
  if (!session.isExpired()) return session;
  return doLogin({ loginUrl, appDomain, ...options });
}
