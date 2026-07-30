const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const login = require('../scripts/login');

function withStubbedModule(modulePath, exportsValue, fn) {
  const resolvedPath = require.resolve(modulePath);
  const previousEntry = require.cache[resolvedPath];
  require.cache[resolvedPath] = {
    id: resolvedPath,
    filename: resolvedPath,
    loaded: true,
    exports: exportsValue
  };

  const restore = () => {
    if (previousEntry) {
      require.cache[resolvedPath] = previousEntry;
    } else {
      delete require.cache[resolvedPath];
    }
  };

  try {
    const result = fn();
    if (result && typeof result.then === 'function') {
      return result.finally(restore);
    }
    restore();
    return result;
  } catch (error) {
    restore();
    throw error;
  }
}

test('runLoginCli delegates to login_and_get_auth runner with the same auth context', async () => {
  const authFileDir = fs.mkdtempSync(path.join(os.tmpdir(), 'shlibrary-login-'));
  const authFile = path.join(authFileDir, 'profile.json');
  fs.writeFileSync(authFile, JSON.stringify({
    accessToken: 'token-1234567890',
    sign: 'sign-1234567890',
    timestamp: 'ts-123'
  }));

  const runnerCalls = [];

  await withStubbedModule('../scripts/login_and_get_auth_node', {
    runCli: async (authContext) => {
      runnerCalls.push(authContext);
      return true;
    }
  }, async () => {
    const result = await login.runLoginCli({ authFile });
    assert.equal(result, true);
  });

  assert.deepEqual(runnerCalls, [{ authFile }]);
});

test('runLoginCli returns false when delegated runner fails', async () => {
  const authFileDir = fs.mkdtempSync(path.join(os.tmpdir(), 'shlibrary-login-'));
  const authFile = path.join(authFileDir, 'profile.json');

  await withStubbedModule('../scripts/login_and_get_auth_node', {
    runCli: async () => false
  }, async () => {
    const result = await login.runLoginCli({ authFile });
    assert.equal(result, false);
  });
});
