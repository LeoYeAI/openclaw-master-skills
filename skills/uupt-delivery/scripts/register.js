#!/usr/bin/env node

/**
 * 手机号注册/获取授权脚本
 * 用法:
 *   发送验证码: node register.js --mobile="手机号"
 *   完成授权:   node register.js --mobile="手机号" --smsCode="验证码"
 *   带图片验证: node register.js --mobile="手机号" --imageCode="图片验证码"
 */

const { getPublicIp, sendSmsCode, auth, getConfig } = require('../index');

// 解析命令行参数
function parseArgs() {
  const args = {};
  process.argv.slice(2).forEach(arg => {
    const match = arg.match(/^--(\w+)=(.+)$/);
    if (match) {
      args[match[1]] = match[2].replace(/^["']|["']$/g, '');
    }
  });
  return args;
}

async function main() {
  const args = parseArgs();
  
  if (!args.mobile) {
    console.log(`
📱 手机号注册/获取授权

用法:
  Step 1 - 发送验证码:
    node register.js --mobile="手机号"

  Step 2 - 完成授权:
    node register.js --mobile="手机号" --smsCode="短信验证码"

参数:
  --mobile     用户手机号（必填）
  --smsCode    短信验证码（第二步必填）
  --imageCode  图片验证码（当需要时）
  --ip         手动指定公网IP（可选，默认自动获取）

示例:
  node register.js --mobile="13800138000"
  node register.js --mobile="13800138000" --smsCode="123456"
  node register.js --mobile="13800138000" --imageCode="8523"
`);
    process.exit(1);
  }
  
  try {
    // 获取公网 IP
    let userIp = args.ip;
    if (!userIp) {
      console.log('🌐 正在获取公网 IP...');
      userIp = await getPublicIp();
      if (!userIp) {
        console.error('❌ 无法自动获取公网 IP，请使用 --ip 参数手动指定');
        process.exit(1);
      }
      console.log(`   公网 IP: ${userIp}`);
    }
    
    // 如果提供了短信验证码，执行授权流程
    if (args.smsCode) {
      console.log('\n🔐 正在完成商户授权...');
      const authResult = await auth({
        userMobile: args.mobile,
        userIp: userIp,
        smsCode: args.smsCode
      });
      
      if (authResult && authResult.body && authResult.body.openId) {
        console.log('\n[REGISTRATION_SUCCESS]');
        console.log(`✅ 注册成功！openId 已保存到配置文件。`);
        console.log(`   openId: ${authResult.body.openId}`);
      } else {
        console.log('\n[REGISTRATION_FAILED]');
        console.error('❌ 授权失败');
        if (authResult) {
          console.error(`   错误码: ${authResult.code}`);
          console.error(`   错误信息: ${authResult.msg}`);
        }
        console.log('\n💡 请重新发送验证码后重试');
        process.exit(1);
      }
      return;
    }
    
    // 否则，发送短信验证码
    console.log('\n📱 正在发送短信验证码...');
    const smsResult = await sendSmsCode({
      userMobile: args.mobile,
      userIp: userIp,
      imageCode: args.imageCode || ''
    });
    
    if (!smsResult) {
      console.error('❌ 发送验证码失败，请稍后重试');
      process.exit(1);
    }
    
    // 检查是否需要图片验证码
    if (smsResult.code === 88100106 || smsResult.code === '88100106') {
      console.log('\n[IMAGE_CAPTCHA_REQUIRED]');
      // msg 字段包含 base64 图片数据
      if (smsResult.msg) {
        console.log(`IMAGE_DATA=data:image/png;base64,${smsResult.msg}`);
      }
      console.log('\n⚠️ 需要图片验证码，请识别图片中的数字后重新运行:');
      console.log(`   node register.js --mobile="${args.mobile}" --imageCode="图片中的数字"`);
      process.exit(2);
    }
    
    if (smsResult.code === 1 || smsResult.code === '1') {
      console.log('\n[SMS_SENT]');
      console.log('✅ 验证码已发送，请查看手机短信。');
      console.log('\n📩 收到验证码后，请运行:');
      console.log(`   node register.js --mobile="${args.mobile}" --smsCode="收到的验证码"`);
    } else {
      console.error(`\n❌ 发送验证码失败: ${smsResult.msg || '未知错误'}`);
      process.exit(1);
    }
    
  } catch (error) {
    console.error('执行失败:', error.message);
    process.exit(1);
  }
}

main();
