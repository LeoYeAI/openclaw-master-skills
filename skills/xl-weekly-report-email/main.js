#!/usr/bin/env node
/**
 * 周报生成和发送主模块
 */

const { sendWeeklyReport, validateConfig, loadConfig } = require('./mailer');
const { isConfigured, generateSetupGuide, getSetupQuestions } = require('./setup');
const path = require('path');
const fs = require('fs');

// 6个部分的提示信息（仅用于展示给用户，不导出）
// 注意：这些只是提示和示例，实际发送时使用用户填写的内容
const sections = [
  {
    key: 'section1',
    title: '一、关键阻碍 / 上期问题进展',
    description: '列出上周遗留问题或当前最大的阻碍因素的跟进情况。',
    format: '[问题描述][当前状态]：进展详情',
    example: '1. [测试环境资源不足][已解决]：已申请新服务器，问题解决，进度已恢复。\n2. [数据接口延迟问题][跟进中]：已联系数据负责人，承诺本周五前修复，目前正在联调。'
  },
  {
    key: 'section2',
    title: '二、本周进展描述（业务研发支撑 & 数据治理 & 日常维护）',
    description: '列出本周具体的产出，建议按项目或模块分类。',
    format: '[项目 xxx] 子项目名 + 项目状态 (Done/Doing 进度 X%/ Delay/ Suspend) + 进度详情/阶段成果/阻塞原因',
    example: '1. [项目 A] 画像标签开发 (Doing 80%)\n   完成了用户活跃度标签的逻辑重构，性能提升 30%。\n   正在与业务方进行数据验收。'
  },
  {
    key: 'section3',
    title: '三、遇到的问题及解决方案',
    description: '这里重点写本周遇到的技术难点或业务卡点，以及你打算怎么解决。',
    format: '问题描述：...\n解决方案：...',
    example: '1. 问题描述：需求频繁变更，导致开发返工。\n   解决方案：已与产品经理约定，后续需求变更需通过 TAPD 更新 PRD 并邮件周知。'
  },
  {
    key: 'section4',
    title: '四、下周计划/目标',
    description: '按优先级列出下周的核心产出承诺。',
    format: '按行列出，每项一个计划',
    example: '1. 本地化部署方面，协助数据开发完成所有流程调度的可用性修复。\n2. 跟进科金中行项目，保证项目稳定推进。'
  },
  {
    key: 'section5',
    title: '五、看到的问题&建议（非必选）',
    description: '着眼于团队协作、流程、架构等宏观问题。',
    format: '自由发挥',
    example: '平台组人员架构问题：目前血缘系统只有一位后端外包人员负责...'
  },
  {
    key: 'section6',
    title: '六、想说的话（心得体会/GET 技能/共鸣句子/个人思考）（非必选）',
    description: '自由发挥区',
    format: '自由发挥',
    example: '本周学到了很多新技能，感谢同事们的帮助...'
  }
];

// 计算日期相关逻辑
function calculateWeekInfo() {
  const now = new Date();

  // 转换为东八区时间
  const utcTime = now.getTime() + (now.getTimezoneOffset() * 60000);
  const shanghaiTime = new Date(utcTime + (8 * 3600000));

  // 获取当前是周几 (0=周日，1=周一，..., 6=周六)
  const dayOfWeek = shanghaiTime.getDay();

  // 计算ISO周数
  const { execSync } = require('child_process');
  const dateStr = shanghaiTime.toISOString().split('T')[0];
  const isoWeekNumber = parseInt(execSync(`python3 -c "from datetime import datetime; d = datetime.fromisoformat('${dateStr}'); print(d.isocalendar()[1])"`, { encoding: 'utf-8' }).trim());

  // 计算本周四
  const thisThursday = new Date(shanghaiTime);
  if (dayOfWeek === 4) {
    // 今天就是周四
  } else if (dayOfWeek > 4) {
    // 周五、周六、周日：本周四已经过了
    const daysBack = dayOfWeek - 4;
    thisThursday.setDate(shanghaiTime.getDate() - daysBack);
  } else {
    // 周一、周二、周三：本周四还没到
    const daysForward = 4 - dayOfWeek;
    thisThursday.setDate(shanghaiTime.getDate() + daysForward);
  }

  // 计算截止日期和时间范围
  // 周四/周四之前（周一到周四）：
  //   - 截止日期 = 本周周四
  //   - 时间范围 = 上周四 到 本周三
  //   - 周数 = ISO周数 - 1
  // 周五/周六/周日：
  //   - 截止日期 = 下周周四
  //   - 时间范围 = 本周四 到 下周三
  //   - 周数 = ISO周数

  let endDate, startDate, endDateDisplay, reportWeekNumber;
  
  if (dayOfWeek <= 4) {
    // 周一、周二、周三、周四
    endDate = new Date(thisThursday);
    startDate = new Date(thisThursday);
    startDate.setDate(thisThursday.getDate() - 7);
    endDateDisplay = new Date(thisThursday);
    endDateDisplay.setDate(thisThursday.getDate() - 1);
    reportWeekNumber = isoWeekNumber - 1;
  } else {
    // 周五、周六、周日
    const nextThursday = new Date(thisThursday);
    nextThursday.setDate(thisThursday.getDate() + 7);
    endDate = nextThursday;
    startDate = thisThursday;
    endDateDisplay = new Date(nextThursday);
    endDateDisplay.setDate(nextThursday.getDate() - 1);
    reportWeekNumber = isoWeekNumber;
  }

  // 格式化日期
  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}${month}${day}`;
  };

  const formatDisplayDate = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    return `${year}年${month}月${day}日`;
  };

  return {
    weekNumber: reportWeekNumber,
    endDate: formatDate(endDate),
    startDate: formatDisplayDate(startDate),
    endDateDisplay: formatDisplayDate(endDateDisplay)
  };
}

// 生成邮件标题
function generateSubject(weekInfo, config) {
  const { name, position, company } = config.report;

  // 如果配置了公司名称，则加上；否则不加
  if (company && company.trim()) {
    return `${company} - ${position}${name} - ${weekInfo.weekNumber}周周报 - ${weekInfo.endDate}`;
  } else {
    return `${position}${name} - ${weekInfo.weekNumber}周周报 - ${weekInfo.endDate}`;
  }
}

// 解析函数 - 正文(一)：遗留问题/阻碍因素跟进
function parseSection1(text) {
  return text.split('\n').filter(line => line.trim()).map((line, idx) => {
    // 匹配格式：[问题描述][当前状态]：进展详情
    const match = line.match(/\[([^\]]+)\]\[(.+?)\]：(.+)/);
    if (match) {
      const [, desc, status, detail] = match;

      // 判断状态样式：'已解决'和'Done'用绿色样式，其他都用蓝色样式
      const statusClass = (status.includes('已解决') || status.toLowerCase().includes('done')) ? 'status-done' : 'status-progress';
      const icon = statusClass === 'status-done' ? '✓' : '→';

      return `<div class="item">
          <div class="item-title">
            <span class="item-icon">${icon}</span>
            <span>${desc}</span>
            <span class="status-badge ${statusClass}">${status}</span>
          </div>
          <div class="item-detail">${detail}</div>
        </div>`;
    }
    // 没按格式写，就直接展示，不报错
    return `<div class="item">${line}</div>`;
  }).join('\n');
}

// 解析函数 - 正文(二)：本周具体产出
function parseSection2(text) {
  const lines = text.split('\n').filter(line => line.trim());
  let result = '';
  let currentItem = null;

  // 处理状态样式
  function getStatusStyles(status) {
    if (!status) return [];

    const parts = status.split('/').map(s => s.trim());
    const result = [];

    for (const part of parts) {
      let statusClass = 'status-progress'; // 默认蓝色样式
      let displayText = part;

      if (part.toLowerCase().includes('done')) {
        statusClass = 'status-done'; // 绿色
      } else if (part.toLowerCase().includes('delay')) {
        statusClass = 'status-delay'; // 红色
      } else if (part.toLowerCase().includes('suspend')) {
        statusClass = 'status-suspend'; // 灰色
      }
      // 其他状态（Doing进度X%等）用蓝色样式

      result.push({ class: statusClass, text: displayText });
    }

    return result;
  }

  for (const line of lines) {
    // 匹配格式：[项目名] 任务名 (状态)
    const match = line.match(/^\d+\.\s*\[([^\]]+)\]\s*(.+?)\s*(?:\(([^)]+)\))?$/)
              || line.match(/^\[([^\]]+)\]\s*(.+?)\s*(?:\(([^)]+)\))?$/);

    if (match) {
      if (currentItem) {
        result += currentItem + '</div>\n';
      }
      const [, project, name, status] = match;
      const icon = '📦';

      let statusBadges = '';
      if (status) {
        const statusStyles = getStatusStyles(status);
        statusBadges = statusStyles.map(s => `<span class="status-badge ${s.class}">${s.text}</span>`).join(' ');
      }

      currentItem = `<div class="item">
          <div class="item-title">
            <span class="item-icon">${icon}</span>
            <span>${project || ''} ${name}</span>
            ${statusBadges}
          </div>`;
    } else if (currentItem) {
      currentItem += `<div class="item-detail">${line.trim()}</div>`;
    } else {
      // 没按格式写，就直接展示，不报错
      result += `<div class="item">${line}</div>\n`;
    }
  }

  if (currentItem) {
    result += currentItem + '</div>\n';
  }

  return result;
}

// 解析函数 - 正文(三)：技术难点/业务卡点
function parseSection3(text) {
  const lines = text.split('\n').filter(line => line.trim());
  let result = '';
  let currentProblem = '';
  let hasFormat = false;

  for (const line of lines) {
    if (line.includes('问题描述：') || line.includes('问题描述:')) {
      hasFormat = true;
      if (currentProblem) {
        result += currentProblem + '\n';
      }
      currentProblem = `<div class="problem-item">
        <div class="problem-desc">${line}</div>`;
    } else if (line.includes('解决方案：') || line.includes('解决方案:')) {
      hasFormat = true;
      if (currentProblem) {
        currentProblem += `<div class="solution-text">${line}</div>
        </div>`;
      }
    } else if (currentProblem) {
      currentProblem += `<div class="solution-text">${line}</div>`;
    }
  }

  if (currentProblem) {
    result += currentProblem;
  }

  // 如果没有按格式写，就直接展示
  if (!hasFormat) {
    return `<div class="text-content">${text.replace(/\n/g, '<br>')}</div>`;
  }

  return result || `<div class="text-content">${text.replace(/\n/g, '<br>')}</div>`;
}

function parseSection4(text) {
  return text.split('\n').filter(line => line.trim()).map((line, idx) => {
    const num = idx + 1;
    const content = line.replace(/^\d+\./, '').trim();
    return `<div class="plan-item">
        <span class="plan-number">${num}</span>
        <span>${content}</span>
      </div>`;
  }).join('\n');
}

// 生成HTML邮件
function generateHTMLBody(weekInfo, content) {
  // 验证 content 参数
  if (!content || typeof content !== 'object') {
    throw new Error('generateHTMLBody: content 参数无效');
  }

  // 调试日志：打印实际使用的内容摘要
  const contentPreview = Object.entries(content)
    .map(([key, value]) => {
      const valueStr = String(value || '');
      return `${key}: ${valueStr.length > 50 ? valueStr.substring(0, 50) + '...' : valueStr}`;
    })
    .join('; ');
  console.log('📝 生成周报内容预览:', contentPreview);

  const { startDate, endDateDisplay } = weekInfo;

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Microsoft YaHei', '微软雅黑', 'Segoe UI', Arial, sans-serif;
      line-height: 1.7;
      color: #2c3e50;
      background-color: #f5f7fa;
      padding: 20px;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
      background: #ffffff;
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
      overflow: hidden;
    }
    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #ffffff;
      padding: 25px 30px;
    }
    .header h1 {
      font-size: 20px;
      font-weight: 600;
      margin-bottom: 8px;
      letter-spacing: 0.5px;
    }
    .time-range {
      font-size: 14px;
      opacity: 0.95;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .time-range-icon {
      font-size: 16px;
    }
    .content { padding: 30px; }
    .section { margin-bottom: 30px; }
    .section-title {
      font-size: 15px;
      font-weight: 600;
      color: #1a1a1a;
      margin-bottom: 15px;
      padding-left: 12px;
      border-left: 4px solid #667eea;
      background: linear-gradient(to right, #f8f9ff, transparent);
      padding-top: 8px;
      padding-bottom: 8px;
      border-radius: 0 6px 6px 0;
    }
    .status-badge {
      display: inline-block;
      padding: 2px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.3px;
    }
    .status-done {
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      color: #ffffff;
    }
    .status-progress {
      background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
      color: #ffffff;
    }
    .status-delay {
      background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
      color: #ffffff;
    }
    .status-suspend {
      background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
      color: #ffffff;
    }
    .item {
      margin-bottom: 15px;
      padding: 12px;
      background: #f8f9ff;
      border-radius: 8px;
      border-left: 3px solid #667eea;
    }
    .item-title {
      font-weight: 600;
      color: #1a1a1a;
      margin-bottom: 8px;
      display: flex;
      align-items: flex-start;
      gap: 8px;
      flex-wrap: wrap;
    }
    .item-icon {
      color: #667eea;
      font-size: 14px;
      margin-top: 2px;
    }
    .item-detail {
      margin-left: 20px;
      margin-top: 6px;
      color: #4a5568;
      font-size: 14px;
    }
    .item-detail:before {
      content: "• ";
      color: #667eea;
      font-weight: 600;
    }
    .problem-item {
      margin-bottom: 18px;
      padding: 15px;
      background: #fffbeb;
      border-radius: 8px;
      border-left: 3px solid #f59e0b;
    }
    .problem-desc, .problem-solution {
      margin-bottom: 8px;
    }
    .label {
      font-weight: 600;
      color: #2c3e50;
    }
    .solution-text {
      margin-left: 20px;
      color: #4a5568;
      padding-left: 15px;
      border-left: 2px solid #f59e0b;
    }
    .plan-item {
      padding: 10px 15px;
      margin-bottom: 8px;
      background: #f0fdf4;
      border-radius: 6px;
      border-left: 3px solid #10b981;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .plan-number {
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      color: #ffffff;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 600;
      flex-shrink: 0;
    }
    .optional-empty {
      color: #94a3b8;
      font-style: italic;
      padding: 15px;
      background: #f8fafc;
      border-radius: 6px;
      text-align: center;
      font-size: 14px;
    }
    .text-content {
      padding: 15px;
      background: #f8f9ff;
      border-radius: 8px;
      border-left: 3px solid #667eea;
      color: #2c3e50;
      font-size: 14px;
      line-height: 1.8;
      white-space: pre-wrap;
    }
    .footer {
      text-align: center;
      padding: 20px;
      background: #f8fafc;
      color: #94a3b8;
      font-size: 12px;
      border-top: 1px solid #e2e8f0;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📊 周报</h1>
      <div class="time-range">
        <span class="time-range-icon">📅</span>
        <span><strong>时间范围：</strong>${startDate} - ${endDateDisplay}</span>
      </div>
    </div>

    <div class="content">
      <div class="section">
        <div class="section-title">一、关键阻碍 / 上期问题进展</div>
        ${content.section1 ? parseSection1(content.section1) : '<div class="optional-empty">（此项暂无内容）</div>'}
      </div>

      <div class="section">
        <div class="section-title">二、本周进展描述（业务研发支撑 & 数据治理 & 日常维护）</div>
        ${content.section2 ? parseSection2(content.section2) : '<div class="optional-empty">（此项暂无内容）</div>'}
      </div>

      <div class="section">
        <div class="section-title">三、遇到的问题及解决方案</div>
        ${content.section3 ? parseSection3(content.section3) : '<div class="optional-empty">（此项暂无内容）</div>'}
      </div>

      <div class="section">
        <div class="section-title">四、下周计划/目标</div>
        ${content.section4 ? parseSection4(content.section4) : '<div class="optional-empty">（此项暂无内容）</div>'}
      </div>

      <div class="section">
        <div class="section-title">五、看到的问题&建议（非必选）</div>
        ${content.section5 ? `<div class="text-content">${content.section5}</div>` : '<p class="optional-empty">（此项暂无内容）</p>'}
      </div>

      <div class="section">
        <div class="section-title">六、想说的话（心得体会/GET 技能/共鸣句子/个人思考）（非必选）</div>
        ${content.section6 ? `<div class="text-content">${content.section6}</div>` : '<p class="optional-empty">（此项暂无内容）</p>'}
      </div>
    </div>

    <div class="footer">
      <p>📧 周报自动生成 | OpenClaw</p>
    </div>
  </div>
</body>
</html>
  `.trim();
}

// 生成完整报告
function generateWeeklyReport(content) {
  const config = loadConfig();
  if (!config) {
    throw new Error('配置未找到，请先运行配置');
  }

  const weekInfo = calculateWeekInfo();
  const subject = generateSubject(weekInfo, config);
  const htmlBody = generateHTMLBody(weekInfo, content);

  return {
    subject,
    body: htmlBody,
    weekInfo,
    contentType: 'text/html'
  };
}

// 生成并发送周报
async function generateAndSendReport(content, additionalCc = null, tempFilePath = null) {
  const config = loadConfig();
  if (!config) {
    throw new Error('配置未找到，请先运行配置');
  }

  const report = generateWeeklyReport(content);
  const recipient = config.report.recipient;

  // 合并抄送人（配置的抄送 + 额外的抄送）
  let cc = null;
  const configuredCc = config.report.cc || null;
  const additionalCcList = parseEmailList(additionalCc);
  const configuredCcList = parseEmailList(configuredCc);

  const allCcList = [...configuredCcList, ...additionalCcList];

  if (allCcList.length > 0) {
    // 去重
    const uniqueCcList = [...new Set(allCcList)];
    cc = uniqueCcList.join(',');
    console.log(`📋 最终抄送人: ${cc}`);
  }

  const result = await sendWeeklyReport(report.subject, report.body, recipient, cc);

  // 发送成功后清理临时文件
  if (result && tempFilePath) {
    cleanupTempFile(tempFilePath);
  }

  return result;
}

// 解析邮箱列表（支持全角和半角逗号分隔）
function parseEmailList(emailStr) {
  if (!emailStr || typeof emailStr !== 'string') {
    return [];
  }

  // 替换全角逗号为半角逗号，然后按逗号分割
  const emails = emailStr.replace(/，/g, ',').split(',');

  // 过滤空白和无效邮箱
  return emails
    .map(email => email.trim())
    .filter(email => email && email.includes('@'));
}

// 检查技能是否就绪
function checkSkillReady() {
  if (!isConfigured()) {
    return {
      ready: false,
      reason: '未配置',
      guide: generateSetupGuide()
    };
  }

  const config = loadConfig();
  try {
    validateConfig(config);
    return {
      ready: true
    };
  } catch (error) {
    return {
      ready: false,
      reason: '配置无效',
      error: error.message
    };
  }
}

// 清理临时文件
function cleanupTempFile(filePath) {
  if (!filePath) {
    return false;
  }

  try {
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
      console.log('✅ 临时文件已删除:', filePath);
      return true;
    } else {
      console.log('⚠️  临时文件不存在:', filePath);
      return false;
    }
  } catch (error) {
    console.error('❌ 删除临时文件失败:', error.message);
    return false;
  }
}

// 导出
module.exports = {
  calculateWeekInfo,
  generateWeeklyReport,
  generateAndSendReport,
  checkSkillReady,
  getSetupQuestions,
  parseEmailList,
  cleanupTempFile
};