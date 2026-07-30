const test = require('node:test');
const assert = require('node:assert/strict');
const os = require('node:os');
const path = require('node:path');

const {
  expandHomeDir,
  getDefaultProfileDir,
  normalizeProfileName,
  resolveProfileFile,
  describeAuthContext
} = require('../scripts/lib/profile_store');

test('expandHomeDir expands tilde-prefixed paths', () => {
  assert.equal(expandHomeDir('~/profiles/default.json'), path.join(os.homedir(), 'profiles/default.json'));
});

test('normalizeProfileName accepts safe names and rejects invalid ones', () => {
  assert.equal(normalizeProfileName('user_1-test'), 'user_1-test');
  assert.throws(() => normalizeProfileName('bad name'), /只允许字母、数字、下划线和短横线/);
});

test('resolveProfileFile uses default profile path when no args are passed', () => {
  assert.deepEqual(resolveProfileFile({}), {
    filePath: path.join(getDefaultProfileDir(), 'profiles', 'default.json'),
    source: 'default-profile-dir',
    profileName: 'default'
  });
});

test('resolveProfileFile respects authFile precedence', () => {
  const resolved = resolveProfileFile({
    profileName: 'user1',
    authFile: '~/custom/user1.json'
  });

  assert.deepEqual(resolved, {
    filePath: path.resolve(path.join(os.homedir(), 'custom/user1.json')),
    source: 'auth-file',
    profileName: 'user1'
  });
});

test('describeAuthContext reports auth file and profile names', () => {
  assert.match(describeAuthContext({ authFile: '~/x.json' }), /认证文件/);
  assert.equal(describeAuthContext({ profileName: 'user1' }), 'profile user1');
  assert.equal(describeAuthContext({}), '默认账号');
});
