#!/usr/bin/env node
/**
 * 配置引导模块
 * 首次使用时引导用户配置邮箱参数
 */

const path = require('path');
const fs = require('fs');

// 配置文件路径
const configPath = path.join(__dirname, 'config.json');

// 默认配置模板
// 注意：邮箱配置现在从 .env 读取
const defaultConfig = {
  report: {
    company: '',
    name: '',
    position: '',
    recipient: '',
    cc: ''
  }
};

// 预设SMTP服务器配置
const smtpPresets = {
  '腾讯企业邮箱': { host: 'smtp.exmail.qq.com', port: 465, secure: true },
  '阿里企业邮箱': { host: 'smtp.qiye.aliyun.com', port: 465, secure: true },
  '网易企业邮箱': { host: 'smtp.qiye.163.com', port: 465, secure: true },
  'Gmail': { host: 'smtp.gmail.com', port: 465, secure: true },
  'Outlook': { host: 'smtp-mail.outlook.com', port: 587, secure: false },
  '自定义': { host: '', port: 465, secure: true }
};

// .env 文件路径
const envPath = path.join(__dirname, '.env');

// 检查 .env 是否已配置
function isEnvConfigured() {
  if (!fs.existsSync(envPath)) {
    return false;
  }
  try {
    const envContent = fs.readFileSync(envPath, 'utf-8');
    const env = {};
    envContent.split('\n').forEach(line => {
      const match = line.match(/^([^#].+?)=(.*)$/);
      if (match) {
        env[match[1]] = match[2].trim();
      }
    });
    return !!(env.SMTP_HOST && env.SMTP_USER && env.SMTP_PASS);
  } catch (error) {
    return false;
  }
}

// 保存 .env 配置
function saveEnvConfig(smtpHost, smtpPort, smtpSecure, smtpUser, smtpPass, smtpFrom) {
  try {
    const envContent = `# SMTP 配置（发邮件）
SMTP_HOST=${smtpHost}
SMTP_PORT=${smtpPort}
SMTP_SECURE=${smtpSecure}
SMTP_USER=${smtpUser}
SMTP_PASS=${smtpPass}
SMTP_FROM=${smtpFrom}
`;
    fs.writeFileSync(envPath, envContent, 'utf-8');
    console.log('✅ 邮箱配置已保存到 .env');
    return true;
  } catch (error) {
    console.error('邮箱配置保存失败:', error.message);
    return false;
  }
}

// 保存配置
function saveConfig(config) {
  try {
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf-8');
    console.log('✅ 配置已保存到 config.json');
    return true;
  } catch (error) {
    console.error('配置保存失败:', error.message);
    return false;
  }
}

// 检查是否已配置（报告配置）
function isConfigured() {
  return fs.existsSync(configPath);
}

// 检查是否已配置（报告配置）
function isConfigured() {
  return fs.existsSync(configPath);
}

// 读取配置
function loadConfig() {
  if (!isConfigured()) {
    return null;
  }

  try {
    return JSON.parse(fs.readFileSync(configPath, 'utf-8'));
  } catch (error) {
    console.error('配置文件读取失败:', error.message);
    return null;
  }
}

// 保存配置
function saveConfig(config) {
  try {
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf-8');
    console.log('✅ 配置已保存到 config.json');
    return true;
  } catch (error) {
    console.error('配置保存失败:', error.message);
    return false;
  }
}

// 引导配置（返回配置问题列表，供外部使用）
function getSetupQuestions() {
  return [
    {
      key: 'email.preset',
      question: '请选择你的邮箱类型：',
      options: Object.keys(smtpPresets),
      default: '腾讯企业邮箱'
    },
    {
      key: 'email.smtp.host',
      question: 'SMTP服务器地址：',
      default: 'smtp.exmail.qq.com',
      skipIf: 'email.preset' // 如果选择了预设，这个可以跳过
    },
    {
      key: 'email.smtp.port',
      question: 'SMTP端口（通常是465或587）：',
      default: 465
    },
    {
      key: 'email.smtp.secure',
      question: '是否使用SSL加密（465端口选true，587端口选false）：',
      default: true
    },
    {
      key: 'email.user',
      question: '邮箱账号（完整地址）：',
      placeholder: 'your-email@example.com'
    },
    {
      key: 'email.password',
      question: '邮箱密码或授权码：',
      type: 'password'
    },
    {
      key: 'email.from',
      question: '发件人邮箱（通常与账号相同）：',
      placeholder: 'your-email@example.com'
    },
    {
      key: 'report.company',
      question: '组织/部门名称（可选，将显示在邮件标题开头）：',
      placeholder: 'XX公司'
    },
    {
      key: 'report.name',
      question: '你的姓名：'
    },
    {
      key: 'report.position',
      question: '你的职位：'
    },
    {
      key: 'report.recipient',
      question: '周报收件人邮箱：',
      placeholder: 'manager@example.com'
    },
    {
      key: 'report.cc',
      question: '周报抄送人邮箱（可选，多个邮箱用逗号分隔）：',
      placeholder: 'cc1@example.com, cc2@example.com'
    }
  ];
}

// 生成配置引导说明
function generateSetupGuide() {
  const questions = getSetupQuestions();

  let guide = '📋 周报技能首次配置\n\n';
  guide += '欢迎使用周报技能！首次使用需要配置报告参数。\n\n';
  guide += '⚠️ 邮箱配置请复制 .env.example 为 .env 并填写 SMTP 配置。\n\n';

  questions.forEach((q, index) => {
    guide += `${index + 1}. ${q.question}\n`;
    if (q.placeholder) {
      guide += `   示例：${q.placeholder}\n`;
    }
    guide += '\n';
  });

  return guide;
}

// 重置配置（重新配置）
function resetConfig() {
  if (fs.existsSync(configPath)) {
    // 备份旧配置
    const backupPath = configPath + '.backup';
    fs.copyFileSync(configPath, backupPath);
    console.log('已备份旧配置到 config.json.backup');
    fs.unlinkSync(configPath);
    console.log('已删除旧配置，可以重新配置');
  }
}

module.exports = {
  isConfigured,
  isEnvConfigured,
  loadConfig,
  saveConfig,
  saveEnvConfig,
  getSetupQuestions,
  generateSetupGuide,
  resetConfig,
  smtpPresets,
  defaultConfig
};