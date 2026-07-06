#!/usr/bin/env node
/**
 * 邮件发送模块
 * 基于 nodemailer
 */

const nodemailer = require('nodemailer');
const path = require('path');
const fs = require('fs');

// 配置文件路径（只存非敏感信息）
const configPath = path.join(__dirname, 'config.json');

// 从当前技能目录的 .env 加载邮箱配置
function loadEnvConfig() {
  const envPath = path.join(__dirname, '.env');
  if (!fs.existsSync(envPath)) {
    return null;
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
    return env;
  } catch (error) {
    console.error('环境变量文件读取失败:', error.message);
    return null;
  }
}

// 加载配置
function loadConfig() {
  if (!fs.existsSync(configPath)) {
    return null;
  }
  try {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    return config;
  } catch (error) {
    console.error('配置文件解析失败:', error.message);
    return null;
  }
}

// 创建邮件发送器
function createTransporter() {
  const envConfig = loadEnvConfig();
  if (!envConfig || !envConfig.SMTP_HOST || !envConfig.SMTP_USER || !envConfig.SMTP_PASS) {
    throw new Error('邮箱配置未找到，请复制 .env.example 为 .env 并填写邮箱配置');
  }

  const host = envConfig.SMTP_HOST;
  const port = parseInt(envConfig.SMTP_PORT || '465');
  const secure = envConfig.SMTP_SECURE === 'true';
  const user = envConfig.SMTP_USER;
  const password = envConfig.SMTP_PASS;

  return nodemailer.createTransport({
    host: host,
    port: port,
    secure: secure,
    auth: {
      user: user,
      pass: password
    }
  });
}

// 发送邮件
async function sendWeeklyReport(subject, html, recipient, cc = null) {
  const envConfig = loadEnvConfig();
  if (!envConfig || !envConfig.SMTP_FROM) {
    throw new Error('发件人邮箱配置未找到，请检查 imap-smtp-email/.env 文件');
  }

  const transporter = createTransporter();
  const from = envConfig.SMTP_FROM;

  console.log('📧 准备发送邮件...');
  console.log(`   收件人: ${recipient}`);
  if (cc) {
    console.log(`   抄送: ${cc}`);
  }
  console.log(`   标题: ${subject}`);

  try {
    const mailOptions = {
      from: from,
      to: recipient,
      subject: subject,
      html: html
    };

    if (cc) {
      mailOptions.cc = cc;
    }

    const info = await transporter.sendMail(mailOptions);

    console.log('✅ 邮件发送成功');
    console.log(`   Message ID: ${info.messageId}`);

    return info;
  } catch (error) {
    console.error('❌ 邮件发送失败:', error.message);
    throw error;
  }
}

// 验证配置
function validateConfig(config) {
  // 邮箱配置现在从 .env 读取，不在这里验证
  // 只验证 report 配置
  if (!config.report || !config.report.name || !config.report.position) {
    throw new Error('缺少报告配置（name 或 position）');
  }

  return true;
}

module.exports = {
  loadEnvConfig,
  loadConfig,
  createTransporter,
  sendWeeklyReport,
  validateConfig
};