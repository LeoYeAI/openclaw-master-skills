#!/usr/bin/env node
/**
 * 上海图书馆登录获取认证信息 (Node.js版本)
 *
 * 使用方法:
 *   node login_and_get_auth_node.js [--profile 名称]
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const {
  resolveProfileFile,
  normalizeProfileName,
  getDefaultProfileDir
} = require('./lib/profile_store');

const LOGIN_URL = 'https://passport.library.sh.cn/oauth/authorize?response_type=code&scope=read%20write&client_id=1837178870&state=test&user_type=D0&relogin=true&redirect_uri=https%3A%2F%2Fwww.library.sh.cn%2Fweblogin';
const PORTAL_HOME_URL = 'https://www.library.sh.cn/';
const SERVICE_URL = 'https://www.library.sh.cn/service/seatyy';
const RESERVATION_OVERVIEW_URL = 'https://www.library.sh.cn/service/yuyue';
const REQUIRED_AUTH_FIELDS = ['accessToken', 'sign', 'timestamp'];

function printUsage() {
  console.log('使用方法:');
  console.log('  node login_and_get_auth_node.js [--profile 名称] [--profile-dir 目录] [--auth-file 文件]');
  console.log('');
  console.log('示例:');
  console.log('  node login_and_get_auth_node.js');
  console.log('  node login_and_get_auth_node.js --profile user1');
  console.log('  node login_and_get_auth_node.js --profile user1 --profile-dir ~/.config/shlibrary-seat-booking');
  console.log('  node login_and_get_auth_node.js --auth-file ~/.config/shlibrary-seat-booking/profiles/user1.json');
  console.log('');
  console.log(`默认 profile 根目录: ${path.join(getDefaultProfileDir(), 'profiles')}`);
}

function parseArgs(args) {
  let profileName = null;
  let profileDir = null;
  let authFile = null;

  for (let i = 0; i < args.length; i += 1) {
    const token = args[i];
    if (token === '--profile') {
      const candidate = args[i + 1];
      if (!candidate) {
        throw new Error('--profile 后面需要跟一个名称');
      }
      profileName = normalizeProfileName(candidate);
      i += 1;
      continue;
    }

    if (token === '--profile-dir') {
      const candidate = args[i + 1];
      if (!candidate) {
        throw new Error('--profile-dir 后面需要跟一个目录路径');
      }
      profileDir = String(candidate).trim();
      if (!profileDir) {
        throw new Error('profile-dir 不能为空');
      }
      i += 1;
      continue;
    }

    if (token === '--auth-file') {
      const candidate = args[i + 1];
      if (!candidate) {
        throw new Error('--auth-file 后面需要跟一个文件路径');
      }
      authFile = String(candidate).trim();
      if (!authFile) {
        throw new Error('auth-file 不能为空');
      }
      i += 1;
      continue;
    }

    if (token === '--help' || token === '-h') {
      printUsage();
      process.exit(0);
    }

    throw new Error(`无法识别参数: ${token}`);
  }

  return { profileName, profileDir, authFile };
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function validateAuth(auth) {
  const missing = REQUIRED_AUTH_FIELDS.filter((field) => {
    const value = auth?.[field];
    return typeof value !== 'string' || value.trim() === '';
  });
  return {
    valid: missing.length === 0,
    missing
  };
}

function saveAuthFile(outputFile, auth) {
  const outputDir = path.dirname(outputFile);
  fs.mkdirSync(outputDir, { recursive: true });
  fs.writeFileSync(outputFile, `${JSON.stringify(auth, null, 2)}\n`, 'utf8');
  fs.chmodSync(outputFile, 0o600);
}

function normalizeAuthPayload(payload) {
  if (payload?.code !== '200' || !payload?.data) {
    return null;
  }

  return {
    accessToken: String(payload.data.accessToken || '').trim(),
    sign: String(payload.data.sign || '').trim(),
    timestamp: String(payload.data.timestamp || '').trim()
  };
}

async function readPortalTokens(page) {
  return page.evaluate(() => {
    function readToken(key) {
      try {
        return window.localStorage.getItem(key) || window.sessionStorage.getItem(key) || '';
      } catch (error) {
        return '';
      }
    }

    return {
      aat: readToken('aat'),
      uat: readToken('uat')
    };
  });
}

async function fetchQueryAuthInfo(page, tokens = null) {
  return page.evaluate(async (injectedTokens) => {
    function readToken(key) {
      try {
        return window.localStorage.getItem(key) || window.sessionStorage.getItem(key) || '';
      } catch (error) {
        return '';
      }
    }

    const aat = injectedTokens?.aat || readToken('aat');
    const uat = injectedTokens?.uat || readToken('uat');

    if (!aat || !uat) {
      return {
        ok: false,
        reason: '未在 localStorage/sessionStorage 中找到 aat 或 uat'
      };
    }

    const response = await fetch('/st/oauth/queryAuthInfo', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json;charset=UTF-8'
      },
      body: JSON.stringify({ aat, uat })
    });

    const payload = await response.json();
    return {
      ok: true,
      payload
    };
  }, tokens);
}

async function warmUpReservationPortal(page, tokens = null) {
  return page.evaluate(async (injectedTokens) => {
    function readToken(key) {
      try {
        return window.localStorage.getItem(key) || window.sessionStorage.getItem(key) || '';
      } catch (error) {
        return '';
      }
    }

    const aat = injectedTokens?.aat || readToken('aat');
    const uat = injectedTokens?.uat || readToken('uat');

    if (!aat || !uat) {
      return {
        ok: false,
        reason: '未在 localStorage/sessionStorage 中找到 aat 或 uat'
      };
    }

    const headers = {
      'Content-Type': 'application/json;charset=UTF-8'
    };

    const [statusResponse, floorResponse] = await Promise.all([
      fetch('/st/subscribe/getYuyueSystemStatus', {
        method: 'POST',
        credentials: 'include',
        headers,
        body: JSON.stringify({ aat, uat })
      }),
      fetch('/st/subscribe/getFloorList', {
        method: 'POST',
        credentials: 'include',
        headers,
        body: JSON.stringify({
          apiVer: 'v2',
          libraryId: '1',
          page: 0,
          pagesize: 50,
          aat
        })
      })
    ]);

    return {
      ok: true,
      statusPayload: await statusResponse.json().catch(() => null),
      floorPayload: await floorResponse.json().catch(() => null)
    };
  }, tokens);
}

function createDeferred() {
  let resolve;
  let reject;
  const promise = new Promise((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

async function waitForCapturedAuth(state, timeoutMs = 10000) {
  if (state.capturedAuth) {
    return state.capturedAuth;
  }

  try {
    return await Promise.race([
      state.queryAuthInfoDeferred.promise,
      new Promise((resolve) => setTimeout(() => resolve(null), timeoutMs))
    ]);
  } catch (error) {
    return null;
  }
}

async function waitForLoginCompletion(page, timeoutMs = 5 * 60 * 1000) {
  await page.waitForURL(
    (url) => /https:\/\/(www|yuyue)\.library\.sh\.cn\//.test(String(url)),
    { timeout: timeoutMs }
  );
}

async function tryClickBookingEntry(page) {
  const locators = [
    page.getByRole('button', { name: /座位预约|立即预约|预约/ }).first(),
    page.getByRole('link', { name: /座位预约|立即预约|预约/ }).first(),
    page.locator('text=/3楼.*预约|预约.*3楼|阅读广场.*预约/').first(),
    page.locator('a:has-text("预约"), button:has-text("预约"), [role="button"]:has-text("预约")').first()
  ];

  for (const locator of locators) {
    try {
      if (await locator.isVisible({ timeout: 1000 })) {
        await locator.click({ timeout: 2500 });
        return true;
      }
    } catch (error) {
      // Ignore and continue with the next strategy.
    }
  }

  const clickedViaDom = await page.evaluate(() => {
    function isVisible(el) {
      if (!el) return false;
      const style = window.getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      return style.visibility !== 'hidden' &&
        style.display !== 'none' &&
        rect.width > 0 &&
        rect.height > 0;
    }

    function scoreText(text) {
      let score = 0;
      if (/座位预约/.test(text)) score += 8;
      if (/立即预约/.test(text)) score += 6;
      if (/预约/.test(text)) score += 4;
      if (/3楼|阅读广场|东馆/.test(text)) score += 3;
      return score;
    }

    const candidates = Array.from(document.querySelectorAll('a, button, [role="button"], div, span'))
      .map((el) => {
        const text = (el.textContent || '').replace(/\s+/g, '');
        return { el, text, score: scoreText(text) };
      })
      .filter(({ el, text, score }) => score > 0 && isVisible(el) && text.length <= 40)
      .sort((a, b) => b.score - a.score);

    const top = candidates[0];
    if (!top) {
      return false;
    }

    top.el.click();
    return true;
  });

  if (clickedViaDom) {
    await sleep(1200);
    return true;
  }

  return false;
}

async function tryClickPortalReservationEntry(page) {
  const targetedLocators = [
    page.locator('a[href*="/service/yuyue"], button[href*="/service/yuyue"]').first(),
    page.locator('a[href*="/service/seatyy"], button[href*="/service/seatyy"]').first(),
    page.getByRole('link', { name: /座位预约|预约/ }).first(),
    page.getByRole('button', { name: /座位预约|预约/ }).first()
  ];

  for (const locator of targetedLocators) {
    try {
      if (await locator.isVisible({ timeout: 1200 })) {
        await locator.click({ timeout: 2500 });
        await sleep(1500);
        return true;
      }
    } catch (error) {
      // Ignore and continue with the next strategy.
    }
  }

  const clickedViaDom = await page.evaluate(() => {
    function isVisible(el) {
      if (!el) return false;
      const style = window.getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      return style.visibility !== 'hidden' &&
        style.display !== 'none' &&
        rect.width > 0 &&
        rect.height > 0;
    }

    const candidates = Array.from(document.querySelectorAll('a, button, [role="button"], div, span'))
      .filter((el) => isVisible(el))
      .map((el) => {
        const text = (el.textContent || '').replace(/\s+/g, '');
        const href = typeof el.getAttribute === 'function' ? (el.getAttribute('href') || '') : '';
        let score = 0;
        if (/\/service\/yuyue|\/service\/seatyy/.test(href)) score += 10;
        if (/座位预约/.test(text)) score += 8;
        if (/预约/.test(text)) score += 4;
        if (/3楼|阅读广场|东馆/.test(text)) score += 2;
        return { el, score, text };
      })
      .filter((item) => item.score > 0 && item.text.length <= 60)
      .sort((a, b) => b.score - a.score);

    const top = candidates[0];
    if (!top) {
      return false;
    }

    top.el.click();
    return true;
  });

  if (clickedViaDom) {
    await sleep(1500);
    return true;
  }

  return false;
}

async function tryFetchAuthDirectly(page, state, label) {
  const tokens = state.portalTokens.aat && state.portalTokens.uat ? state.portalTokens : null;
  const result = await fetchQueryAuthInfo(page, tokens);
  if (!result.ok) {
    console.log(`ℹ️ ${label}无法直接调用 queryAuthInfo: ${result.reason}`);
    return null;
  }

  const auth = normalizeAuthPayload(result.payload);
  if (!auth) {
    console.log(`ℹ️ ${label}的 queryAuthInfo 返回了非成功结果`);
    return null;
  }

  state.capturedAuth = auth;
  state.queryAuthInfoDeferred.resolve(auth);
  console.log(`✅ 已通过${label}直接获取认证信息`);
  return auth;
}

async function waitForAuthAfterEnteringSeatPage(page, state, timeoutMs = 60000) {
  const deadline = Date.now() + timeoutMs;
  let clickAttempts = 0;
  let nextClickAt = Date.now();

  while (Date.now() < deadline) {
    if (state.capturedAuth) {
      return state.capturedAuth;
    }

    const auth = await waitForCapturedAuth(state, 5000);
    if (auth) {
      return auth;
    }

    if (Date.now() >= nextClickAt && clickAttempts < 3) {
      clickAttempts += 1;
      const clicked = await tryClickBookingEntry(page);
      nextClickAt = Date.now() + 5000;
      if (clicked) {
        console.log(`🔘 已尝试自动点击预约入口 (${clickAttempts}/3)，继续等待认证信息...`);
      } else {
        console.log(`🔍 暂未找到可点击的预约入口 (${clickAttempts}/3)，稍后重试...`);
      }
    }
  }

  return null;
}

async function waitForPortalTokens(page, state, timeoutMs = 10000) {
  const deadline = Date.now() + timeoutMs;

  while (Date.now() < deadline) {
    if (state.portalTokens.aat && state.portalTokens.uat) {
      return state.portalTokens;
    }

    const tokens = await readPortalTokens(page);
    if (tokens.aat && tokens.uat) {
      state.portalTokens = tokens;
      return tokens;
    }

    await sleep(500);
  }

  return null;
}

async function openReservationEntry(page, state) {
  console.log('🔄 等待门户首页初始化...');
  await page.goto(PORTAL_HOME_URL, {
    waitUntil: 'domcontentloaded',
    timeout: 15000
  });
  await sleep(2500);

  const homeTokens = await waitForPortalTokens(page, state, 8000);
  if (homeTokens) {
    console.log('✅ 已在门户首页拿到 aat / uat');
  } else {
    console.log('ℹ️ 门户首页暂未拿到完整 aat / uat，尝试主动点击座位预约入口');
  }

  const clickedFromHome = await tryClickPortalReservationEntry(page);
  if (clickedFromHome) {
    console.log('🔘 已在门户首页尝试点击座位预约入口');
    await sleep(2000);
  }

  const directAuthFromHome = await tryFetchAuthDirectly(page, state, '门户首页');
  if (directAuthFromHome) {
    return directAuthFromHome;
  }

  console.log('🔄 打开预约入口...');
  await page.goto(SERVICE_URL, {
    waitUntil: 'domcontentloaded',
    timeout: 15000
  });
  await sleep(1500);

  const tokens = await waitForPortalTokens(page, state, 3000);
  if (tokens.aat && tokens.uat) {
    console.log('✅ 已在 seatyy 页面拿到 aat / uat');
  } else {
    console.log('ℹ️ seatyy 页面暂未拿到完整 aat / uat，继续打开座位预约总览页');
  }

  const directAuth = await tryFetchAuthDirectly(page, state, 'seatyy 页面');
  if (directAuth) {
    return directAuth;
  }

  console.log('🔄 打开座位预约总览页...');
  await page.goto(RESERVATION_OVERVIEW_URL, {
    waitUntil: 'domcontentloaded',
    timeout: 15000
  });
  await sleep(2000);

  const overviewTokens = await waitForPortalTokens(page, state, 3000);
  if (overviewTokens) {
    console.log('✅ 已在座位预约总览页拿到 aat / uat');
  }

  const warmResult = await warmUpReservationPortal(page, overviewTokens);
  if (warmResult.ok) {
    const floorItems = warmResult.floorPayload?.data?.resultValue || [];
    const seatFloor = floorItems.find((item) => item?.webPath === '/pickSeat' && /3楼/.test(String(item?.floorName || '')));
    if (seatFloor) {
      console.log(`✅ 已主动加载预约入口数据：${seatFloor.floorName} ${seatFloor.webPath}`);
    } else {
      console.log('ℹ️ 已主动加载预约入口数据，但还没定位到 3 楼座位入口');
    }
  } else {
    console.log(`ℹ️ 主动加载预约入口数据失败: ${warmResult.reason}`);
  }

  return tryFetchAuthDirectly(page, state, '座位预约总览页');
}

async function loginAndGetAuth(outputFile) {
  const browser = await chromium.launch({
    headless: false,
    slowMo: 100
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 }
  });

  const page = await context.newPage();
  const state = {
    capturedAuth: null,
    queryAuthInfoDeferred: createDeferred(),
    portalTokens: {
      aat: '',
      uat: ''
    }
  };

  page.on('request', (request) => {
    try {
      const url = request.url();
      if (!/\/st\/(oauth\/queryAuthInfo|subscribe\/getYuyueSystemStatus|subscribe\/getFloorList)$/.test(url)) {
        return;
      }

      const postData = request.postData();
      if (!postData) {
        return;
      }

      const payload = JSON.parse(postData);
      if (payload?.aat && !state.portalTokens.aat) {
        state.portalTokens.aat = String(payload.aat);
      }
      if (payload?.uat && !state.portalTokens.uat) {
        state.portalTokens.uat = String(payload.uat);
      }
    } catch (error) {
      // Ignore malformed payloads.
    }
  });

  page.on('response', async (response) => {
    if (response.url() !== 'https://www.library.sh.cn/st/oauth/queryAuthInfo') {
      return;
    }

    try {
      const payload = await response.json();
      if (payload?.code === '200' && payload?.data) {
        state.capturedAuth = {
          accessToken: String(payload.data.accessToken || '').trim(),
          sign: String(payload.data.sign || '').trim(),
          timestamp: String(payload.data.timestamp || '').trim()
        };
        state.queryAuthInfoDeferred.resolve(state.capturedAuth);
        console.log('✅ 已捕获 queryAuthInfo 响应');
      }
    } catch (error) {
      console.log(`⚠️ 读取 queryAuthInfo 响应失败: ${error.message}`);
    }
  });

  try {
    console.log('🚀 启动浏览器...');
    console.log(`🌐 打开登录页: ${LOGIN_URL}`);
    await page.goto(LOGIN_URL, { waitUntil: 'domcontentloaded' });

    console.log('');
    console.log('请在浏览器中手动完成登录，包括验证码。');
    console.log('登录成功后脚本会自动检测并继续，无需回终端确认。');
    await waitForLoginCompletion(page);

    state.capturedAuth = await openReservationEntry(page, state);

    if (!state.capturedAuth) {
      console.log('⏳ 等待页面自动触发 queryAuthInfo...');
      state.capturedAuth = await waitForAuthAfterEnteringSeatPage(page, state, 20000);
    }

    if (!state.capturedAuth) {
      console.log('');
      console.log('⚠️ 页面还没有自动触发 queryAuthInfo。');
      console.log('请在浏览器里手动点击一次“预约”或进入座位预约入口，脚本会继续自动等待。');
      state.capturedAuth = await waitForAuthAfterEnteringSeatPage(page, state, 60000);
    }

    if (!state.capturedAuth) {
      console.log('🔍 直接调用 queryAuthInfo...');
      const result = await fetchQueryAuthInfo(page);
      if (!result.ok) {
        throw new Error(`调用 queryAuthInfo 失败: ${result.reason}`);
      }

      const payload = result.payload;
      if (payload?.code !== '200' || !payload?.data) {
        throw new Error(`queryAuthInfo 返回异常: ${JSON.stringify(payload)}`);
      }

      state.capturedAuth = {
        accessToken: String(payload.data.accessToken || '').trim(),
        sign: String(payload.data.sign || '').trim(),
        timestamp: String(payload.data.timestamp || '').trim()
      };
    }

    const validation = validateAuth(state.capturedAuth);
    if (!validation.valid) {
      throw new Error(`认证信息不完整，缺少: ${validation.missing.join(', ')}`);
    }

    saveAuthFile(outputFile, state.capturedAuth);

    console.log('');
    console.log(`✅ 认证信息已保存到: ${outputFile}`);
    console.log(`   accessToken: ${state.capturedAuth.accessToken.slice(0, 12)}...`);
    console.log(`   sign: ${state.capturedAuth.sign.slice(0, 12)}...`);
    console.log(`   timestamp: ${state.capturedAuth.timestamp}`);
    return true;
  } finally {
    console.log('');
    console.log('🔒 关闭浏览器...');
    await browser.close();
  }
}

async function main() {
  try {
    const success = await runCli();
    process.exit(success ? 0 : 1);
  } catch (error) {
    console.error('\n💥 错误:', error.message);
    process.exit(1);
  }
}

async function runCli(authContext = null) {
  const resolvedAuthContext = authContext || parseArgs(process.argv.slice(2));
  const outputFile = resolveProfileFile(resolvedAuthContext).filePath;

  console.log('========================================');
  console.log('上海图书馆登录获取认证信息 (Node.js)');
  console.log('========================================');
  console.log(`目标文件: ${outputFile}`);
  console.log('');
  console.log('当前流程:');
  console.log('1. 打开登录页面');
  console.log('2. 你手动完成用户名、密码、验证码登录');
  console.log('3. 脚本自动打开预约入口并调用 queryAuthInfo');
  console.log('4. 保存 accessToken / sign / timestamp 到 profile 文件');
  console.log('');
  console.log('ℹ️ x-encode 无需保存；book_seat.js 会在每次请求前动态生成');
  console.log('========================================\n');

  return loginAndGetAuth(outputFile);
}

module.exports = {
  parseArgs,
  printUsage,
  validateAuth,
  saveAuthFile,
  normalizeAuthPayload,
  loginAndGetAuth,
  runCli
};

if (require.main === module) {
  main();
}
