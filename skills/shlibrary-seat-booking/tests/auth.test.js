const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const auth = require('../scripts/lib/auth');

function applyStubbedModules(stubs) {
  const previousEntries = [];

  for (const [modulePath, exportsValue] of Object.entries(stubs)) {
    const resolvedPath = require.resolve(modulePath);
    previousEntries.push([resolvedPath, require.cache[resolvedPath]]);
    require.cache[resolvedPath] = {
      id: resolvedPath,
      filename: resolvedPath,
      loaded: true,
      exports: exportsValue
    };
  }

  return () => {
    for (const [resolvedPath, previousEntry] of previousEntries.reverse()) {
      if (previousEntry) {
        require.cache[resolvedPath] = previousEntry;
      } else {
        delete require.cache[resolvedPath];
      }
    }
  };
}

function loadFreshAuthWithStubs(stubs = {}) {
  const authModulePath = require.resolve('../scripts/lib/auth');
  const previousAuthEntry = require.cache[authModulePath];
  delete require.cache[authModulePath];
  const restoreStubs = applyStubbedModules(stubs);
  const freshAuth = require('../scripts/lib/auth');

  const restore = () => {
    delete require.cache[authModulePath];
    restoreStubs();
    if (previousAuthEntry) {
      require.cache[authModulePath] = previousAuthEntry;
    }
  };

  return { freshAuth, restore };
}

test('getAuth reads auth from file', () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'shlibrary-auth-'));
  const authFile = path.join(tempDir, 'default.json');
  fs.writeFileSync(authFile, JSON.stringify({
    accessToken: 'file-token',
    sign: 'file-sign',
    timestamp: 'file-ts'
  }));

  const result = auth.getAuth({ authFile });
  assert.deepEqual(result, {
    accessToken: 'file-token',
    sign: 'file-sign',
    timestamp: 'file-ts',
    xEncode: null
  });
});

test('hasAnyEnvAuth remains false because auth env vars are unsupported', () => {
  assert.equal(auth.hasAnyEnvAuth(), false);
});

test('ensureValidAuth calls login flow when auth is missing and probe succeeds after refresh', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'shlibrary-auth-'));
  const authFile = path.join(tempDir, 'default.json');
  fs.writeFileSync(authFile, JSON.stringify({
    accessToken: 'file-token',
    sign: 'file-sign',
    timestamp: 'file-ts'
  }));

  const loginCalls = [];
  let requestCount = 0;

  const { freshAuth, restore } = loadFreshAuthWithStubs({
    '../scripts/lib/http': {
      getResultMessage: (result) => result?.resultStatus?.message || result?.resultStatus?.msg || '',
      request: async () => {
        requestCount += 1;
        if (requestCount === 1) {
          return { resultStatus: { code: 101, message: '获取用户信息时出现异常' } };
        }
        return { resultStatus: { code: 0, message: '操作成功。' } };
      }
    },
    '../scripts/login': {
      runLoginCli: async (authContext) => {
        loginCalls.push(authContext);
        return true;
      }
    }
  });

  try {
    await freshAuth.ensureValidAuth({ authFile });
  } finally {
    restore();
  }

  assert.equal(requestCount, 2);
  assert.deepEqual(loginCalls, [{ profileName: null, profileDir: null, authFile }]);
});

test('ensureValidAuth throws when login flow reports failure', async () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'shlibrary-auth-'));
  const authFile = path.join(tempDir, 'default.json');
  fs.writeFileSync(authFile, JSON.stringify({
    accessToken: 'file-token',
    sign: 'file-sign',
    timestamp: 'file-ts'
  }));

  const { freshAuth, restore } = loadFreshAuthWithStubs({
    '../scripts/lib/http': {
      getResultMessage: (result) => result?.resultStatus?.message || result?.resultStatus?.msg || '',
      request: async () => ({ resultStatus: { code: 101, message: '获取用户信息时出现异常' } })
    },
    '../scripts/login': {
      runLoginCli: async () => false
    }
  });

  try {
    await assert.rejects(
      freshAuth.ensureValidAuth({ authFile }),
      /登录流程失败/
    );
  } finally {
    restore();
  }
});
