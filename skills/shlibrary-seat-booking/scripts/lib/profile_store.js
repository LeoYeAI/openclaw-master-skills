const os = require('os');
const path = require('path');

const DEFAULT_PROFILE_DIR_RELATIVE = path.join('.config', 'shlibrary-seat-booking');

function expandHomeDir(inputPath) {
  if (!inputPath) {
    return inputPath;
  }

  const homeDir = os.homedir();
  if (inputPath === '~') {
    return homeDir;
  }
  if (inputPath.startsWith(`~${path.sep}`)) {
    return path.join(homeDir, inputPath.slice(2));
  }
  if (inputPath.startsWith('~/')) {
    return path.join(homeDir, inputPath.slice(2));
  }
  return inputPath;
}

function getDefaultProfileDir() {
  return path.join(os.homedir(), DEFAULT_PROFILE_DIR_RELATIVE);
}

function normalizeProfileName(profileName) {
  const normalized = String(profileName || '').trim();
  if (!normalized) {
    throw new Error('profile 名称不能为空');
  }
  if (!/^[A-Za-z0-9_-]+$/.test(normalized)) {
    throw new Error('profile 名称只允许字母、数字、下划线和短横线');
  }
  return normalized;
}

function resolveProfileFile(authContext = {}) {
  const authFile = String(authContext.authFile || '').trim();
  if (authFile) {
    return {
      filePath: path.resolve(expandHomeDir(authFile)),
      source: 'auth-file',
      profileName: authContext.profileName ? normalizeProfileName(authContext.profileName) : null
    };
  }

  const profileName = authContext.profileName
    ? normalizeProfileName(authContext.profileName)
    : 'default';
  const profileDir = authContext.profileDir
    ? path.resolve(expandHomeDir(String(authContext.profileDir).trim()))
    : getDefaultProfileDir();

  return {
    filePath: path.join(profileDir, 'profiles', `${profileName}.json`),
    source: authContext.profileDir ? 'profile-dir' : 'default-profile-dir',
    profileName
  };
}

function describeAuthContext(authContext = {}) {
  if (authContext.authFile) {
    return `认证文件 ${path.resolve(expandHomeDir(authContext.authFile))}`;
  }

  if (authContext.profileName) {
    return `profile ${normalizeProfileName(authContext.profileName)}`;
  }

  return '默认账号';
}

module.exports = {
  DEFAULT_PROFILE_DIR_RELATIVE,
  expandHomeDir,
  getDefaultProfileDir,
  normalizeProfileName,
  resolveProfileFile,
  describeAuthContext
};
