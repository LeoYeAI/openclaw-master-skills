#!/usr/bin/env node
/**
 * 上海图书馆登录获取认证信息
 *
 * 使用方法:
 *   node login.js [--profile 名称] [--profile-dir 目录] [--auth-file 文件]
 */

const fs = require('fs');
const path = require('path');
const { resolveProfileFile, normalizeProfileName, getDefaultProfileDir } = require('./lib/profile_store');

function printUsage() {
  console.log('使用方法:');
  console.log('  node login.js [--profile 名称] [--profile-dir 目录] [--auth-file 文件]');
  console.log('');
  console.log('示例:');
  console.log('  node login.js');
  console.log('  node login.js --profile user1');
  console.log('  node login.js --profile user1 --profile-dir ~/.config/shlibrary-seat-booking');
  console.log('  node login.js --auth-file ~/.config/shlibrary-seat-booking/profiles/user1.json');
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

async function main() {
  try {
    const success = await runLoginCli();
    process.exit(success ? 0 : 1);
  } catch (error) {
    console.error('\n💥 错误:', error.message);
    process.exit(1);
  }
}

async function runLoginCli(authContext = null) {
  const resolvedAuthContext = authContext || parseArgs(process.argv.slice(2));
  const authFile = resolveProfileFile(resolvedAuthContext).filePath;

  console.log('========================================');
  console.log('上海图书馆登录获取认证信息');
  console.log('========================================');
  console.log(`目标文件: ${authFile}`);
  console.log('');
  console.log('将通过浏览器辅助完成以下步骤:');
  console.log('1. 打开登录页面');
  console.log('2. 你手动输入用户名、密码和验证码');
  console.log('3. 登录成功后脚本自动检测并继续');
  console.log('4. 自动调用 queryAuthInfo');
  console.log('5. 保存 accessToken / sign / timestamp 到认证文件');
  console.log('');
  console.log('⚠️ 注意: 需要人工协助完成登录');
  console.log('========================================\n');

  console.log('🚀 启动浏览器登录流程...\n');
  const { runCli: runLoginAndGetAuthCli } = require('./login_and_get_auth_node');
  const success = await runLoginAndGetAuthCli(resolvedAuthContext);
  if (!success) {
    console.error('\n❌ 浏览器登录失败');
    return false;
  }

  console.log('\n✅ 认证信息获取成功！');
  console.log(`已保存到: ${authFile}`);

  if (fs.existsSync(authFile)) {
    try {
      const auth = JSON.parse(fs.readFileSync(authFile, 'utf8'));
      console.log('\n📋 认证信息预览:');
      console.log(`  accessToken: ${auth.accessToken?.substring(0, 10)}...`);
      console.log(`  sign: ${auth.sign?.substring(0, 10)}...`);
      console.log(`  timestamp: ${auth.timestamp}`);
    } catch (error) {
      console.error('\n⚠️ 警告: 无法读取保存的认证文件');
    }
  }

  return true;
}

module.exports = {
  parseArgs,
  printUsage,
  runLoginCli
};

if (require.main === module) {
  main();
}
