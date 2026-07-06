#!/usr/bin/env node
/**
 * 测试脚本 - 验证技能功能
 */

const { checkSkillReady, generateWeeklyReport } = require('./main');
const { loadConfig, validateConfig } = require('./mailer');

async function test() {
  console.log('=== 周报技能测试 ===\n');

  // 1. 检查技能就绪状态
  console.log('1️⃣ 检查技能就绪状态...');
  const readyStatus = checkSkillReady();

  if (!readyStatus.ready) {
    console.log(`❌ 技能未就绪：${readyStatus.reason}`);
    if (readyStatus.guide) {
      console.log('\n' + readyStatus.guide);
    }
    if (readyStatus.error) {
      console.log(`错误：${readyStatus.error}`);
    }
    return false;
  }

  console.log('✅ 技能已就绪\n');

  // 2. 加载配置
  console.log('2️⃣ 加载配置...');
  const config = loadConfig();
  console.log('✅ 配置加载成功');
  console.log(`   邮箱：${config.email.user}`);
  console.log(`   姓名：${config.report.name}`);
  console.log(`   职位：${config.report.position}`);
  console.log(`   收件人：${config.report.recipient}\n`);

  // 3. 验证配置
  console.log('3️⃣ 验证配置...');
  try {
    validateConfig(config);
    console.log('✅ 配置验证通过\n');
  } catch (error) {
    console.log(`❌ 配置验证失败：${error.message}\n`);
    return false;
  }

  // 4. 测试生成报告（不发送）
  console.log('4️⃣ 测试生成报告...');
  const testContent = {
    section1: '1. [测试问题][已解决]：已解决测试问题。',
    section2: '1. [测试项目] 测试任务 (Done)\n   完成测试任务。',
    section3: '1. 问题描述：测试问题描述。\n   解决方案：测试解决方案。',
    section4: '1. 测试计划1\n2. 测试计划2',
    section5: '测试建议内容',
    section6: '测试心得内容'
  };

  try {
    const report = generateWeeklyReport(testContent);
    console.log('✅ 报告生成成功');
    console.log(`   标题：${report.subject}`);
    console.log(`   时间范围：${report.weekInfo.startDate} - ${report.weekInfo.endDateDisplay}`);
    console.log(`   HTML 长度：${report.body.length} 字符\n`);
  } catch (error) {
    console.log(`❌ 报告生成失败：${error.message}\n`);
    return false;
  }

  console.log('=== 所有测试通过 ✅ ===\n');
  return true;
}

// 运行测试
test().then(success => {
  process.exit(success ? 0 : 1);
}).catch(error => {
  console.error('测试失败：', error);
  process.exit(1);
});