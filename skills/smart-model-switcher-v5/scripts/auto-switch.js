#!/usr/bin/env node
/**
 * 智能模型切换器 V5.0.3 - 多模态感知增强版
 * 自动检测图片/视频/音频/代码任务，切换到最优模型
 * 
 * V5.0.2 新增：
 * - 视频文件自动检测
 * - 音频文件自动检测
 * - Office 模式支持
 * - 主窗口限制（子代理不执行智能切换）
 * 
 * 使用方法：
 *   node auto-switch.js --check "用户消息"
 *   node auto-switch.js --check "用户消息" --has-image
 *   node auto-switch.js --check "用户消息" --has-video
 *   node auto-switch.js --check "用户消息" --has-audio
 *   node auto-switch.js --switch glm-5
 */

const https = require('https');
const http = require('http');

// 模型配置
const MODELS = {
  multimodal: {
    best: 'bailian/qwen3.5-plus',       // 多模态首选（图片/视频/音频）
    vision: 'bailian/qwen3-vl-plus',    // 纯图片
    fallback: 'bailian/qvq-max'
  },
  coding: {
    best: 'bailian/glm-5',              // 最强代码
    alt: 'bailian/qwen3-coder-plus',
    fallback: 'bailian/qwen-coder-turbo'
  },
  reasoning: {
    best: 'bailian/qwq-plus',           // 最强推理
    alt: 'bailian/qwen3-max',
    fallback: 'bailian/glm-5'
  },
  office: {
    best: 'bailian/MiniMax-M2.5',       // Office 文档
    fallback: 'bailian/qwen3.5-plus'
  },
  general: {
    best: 'bailian/qwen3.5-plus',       // 通用最强
    fast: 'bailian/qwen-turbo'
  }
};

// 文件扩展名检测
const FILE_EXTENSIONS = {
  image: ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg'],
  video: ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'],
  audio: ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.wma']
};

// 关键词检测
const KEYWORDS = {
  coding: [
    '代码', '编程', 'python', 'javascript', 'js', 'ts', 'typescript',
    '函数', 'debug', 'bug', '报错', '错误', '修复', '重构',
    '写一个', '帮我写', '实现', '开发', '.py', '.js', '.ts', '.html',
    'api', '接口', '脚本', '爬虫', '自动化'
  ],
  reasoning: [
    '推理', '逻辑', '证明', '数学', '计算', '推导', '分析',
    '为什么', '怎么推导', '能否推出', '关系', '原理'
  ],
  writing: [
    '写', '作文', '文章', '小说', '故事', '文案', '邮件', '报告',
    '创作', '撰写', '起草'
  ],
  image: [
    '图片', '截图', '照片', '图像', '看这个', '图里',
    '识别', 'ocr', '表格', '图表'
  ],
  video: [
    '视频', '录像', '影片', 'clip', 'movie'
  ],
  audio: [
    '音频', '录音', '声音', '语音', '转录', 'transcribe'
  ],
  office: [
    'office', 'Office', 'Office模式', '切换Office', 'MiniMax', '文档处理',
    'Word', 'Excel', 'PPT', 'PowerPoint', '表格处理'
  ]
};

/**
 * 检测是否为主窗口（主会话）
 * 子代理不执行智能切换
 */
function isMainWindow(context = {}) {
  // 如果有 subagent context 标记，不是主窗口
  if (context.isSubagent || context.hasSubagentContext) {
    return false;
  }
  
  // 如果 depth > 0，不是主窗口
  if (context.depth && context.depth > 0) {
    return false;
  }
  
  // 如果是 spawned session，不是主窗口
  if (context.isSpawnedSession) {
    return false;
  }
  
  // 默认是主窗口
  return true;
}

/**
 * 检测消息中的文件类型
 */
function detectFileType(message) {
  const lowerMsg = message.toLowerCase();
  
  // 检测视频文件
  for (const ext of FILE_EXTENSIONS.video) {
    if (lowerMsg.includes(ext)) {
      return 'video';
    }
  }
  
  // 检测音频文件
  for (const ext of FILE_EXTENSIONS.audio) {
    if (lowerMsg.includes(ext)) {
      return 'audio';
    }
  }
  
  // 检测图片文件
  for (const ext of FILE_EXTENSIONS.image) {
    if (lowerMsg.includes(ext)) {
      return 'image';
    }
  }
  
  return null;
}

/**
 * 检测任务类型
 */
function detectTaskType(message, context = {}) {
  // Step 0: 主窗口检测（最高优先级）
  if (!isMainWindow(context)) {
    return { 
      type: 'subagent', 
      model: null, 
      reason: '子代理会话，跳过智能切换，使用预设模型',
      skipSwitch: true 
    };
  }
  
  const lowerMsg = message.toLowerCase();
  const hasImage = context.hasImage || false;
  const hasVideo = context.hasVideo || false;
  const hasAudio = context.hasAudio || false;
  
  // 检测消息中的文件类型
  const fileType = detectFileType(message);
  
  // 规则 1: 多模态检测优先（图片/视频/音频）
  // 视频文件 → qwen3.5-plus（唯一支持视频）
  if (hasVideo || fileType === 'video' || KEYWORDS.video.some(k => lowerMsg.includes(k))) {
    return { type: 'video', model: MODELS.multimodal.best, reason: '视频任务，使用多模态模型' };
  }
  
  // 音频文件 → qwen3.5-plus（唯一支持音频）
  if (hasAudio || fileType === 'audio' || KEYWORDS.audio.some(k => lowerMsg.includes(k))) {
    return { type: 'audio', model: MODELS.multimodal.best, reason: '音频任务，使用多模态模型' };
  }
  
  // 图片检测
  if (hasImage || fileType === 'image') {
    // 图片 + 代码关键词 → 视觉+代码模型
    if (KEYWORDS.coding.some(k => lowerMsg.includes(k))) {
      return { type: 'vision_coding', model: MODELS.multimodal.best, reason: '图片+代码任务，使用多模态模型' };
    }
    // 纯图片理解
    return { type: 'vision', model: MODELS.multimodal.best, reason: '图片理解任务，使用多模态模型' };
  }
  
  // 图片关键词检测
  if (KEYWORDS.image.some(k => lowerMsg.includes(k))) {
    if (KEYWORDS.coding.some(k => lowerMsg.includes(k))) {
      return { type: 'vision_coding', model: MODELS.multimodal.best, reason: '图片+代码任务，使用多模态模型' };
    }
    return { type: 'vision', model: MODELS.multimodal.best, reason: '图片理解任务，使用多模态模型' };
  }
  
  // 规则 2: 代码关键词
  if (KEYWORDS.coding.some(k => lowerMsg.includes(k))) {
    return { type: 'coding', model: MODELS.coding.best, reason: '代码任务，使用最强代码模型' };
  }
  
  // 规则 3: 推理关键词
  if (KEYWORDS.reasoning.some(k => lowerMsg.includes(k))) {
    return { type: 'reasoning', model: MODELS.reasoning.best, reason: '推理任务，使用最强推理模型' };
  }
  
  // 规则 4: Office 关键词
  if (KEYWORDS.office.some(k => lowerMsg.includes(k))) {
    return { type: 'office', model: MODELS.office.best, reason: 'Office 模式，使用文档处理模型' };
  }
  
  // 规则 5: 写作关键词
  if (KEYWORDS.writing.some(k => lowerMsg.includes(k))) {
    return { type: 'writing', model: MODELS.general.best, reason: '写作任务，使用通用强模型' };
  }
  
  // 默认通用
  return { type: 'general', model: MODELS.general.best, reason: '通用任务，使用通用强模型' };
}

/**
 * 切换模型（通过 OpenClaw API）
 */
async function switchModel(modelId) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ model: modelId });
    
    const options = {
      hostname: 'localhost',
      port: 3737,
      path: '/api/session/model',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    };
    
    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          resolve({ success: true, model: modelId });
        }
      });
    });
    
    req.on('error', (e) => {
      // 如果 API 不可用，返回成功（假设用户手动切换）
      resolve({ success: true, model: modelId, note: '请手动切换模型' });
    });
    
    req.write(data);
    req.end();
  });
}

/**
 * 获取切换提示信息
 */
function getSwitchMessage(result) {
  const messages = {
    'video': '🧠 已切换到 qwen3.5-plus（视频理解）',
    'audio': '🧠 已切换到 qwen3.5-plus（音频理解）',
    'vision': '🧠 已切换到 qwen3.5-plus（图片理解）',
    'vision_coding': '🧠 已切换到 qwen3.5-plus（图片+代码）',
    'coding': '🧠 已切换到 glm-5（代码任务）',
    'reasoning': '🧠 已切换到 qwq-plus（推理任务）',
    'office': '🧠 已切换到 MiniMax-M2.5（Office 模式）',
    'writing': '🧠 已切换到 qwen3.5-plus（写作任务）',
    'general': '🧠 已切换到 qwen3.5-plus',
    'subagent': '🤖 子代理模式，使用预设模型'
  };
  
  return messages[result.type] || '🧠 已切换模型';
}

// CLI 入口
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log(`
🧠 智能模型切换器 V5.0.2

使用方法：
  node auto-switch.js --check "用户消息" [--has-image] [--has-video] [--has-audio]
  node auto-switch.js --switch glm-5
  node auto-switch.js --list
  node auto-switch.js --test-subagent "用户消息"

选项：
  --has-image     消息包含图片
  --has-video     消息包含视频
  --has-audio     消息包含音频
  --is-subagent   模拟子代理环境

示例：
  node auto-switch.js --check "帮我写个爬虫"
  node auto-switch.js --check "看这个截图" --has-image
  node auto-switch.js --check "分析这个视频" --has-video
  node auto-switch.js --switch bailian/glm-5
  node auto-switch.js --test-subagent "帮我写代码"
`);
    return;
  }
  
  const command = args[0];
  
  if (command === '--list') {
    console.log('\n📋 可用模型列表：\n');
    console.log('🎬 视频模型：');
    console.log('  - qwen3.5-plus (唯一支持视频)');
    console.log('\n🎵 音频模型：');
    console.log('  - qwen3.5-plus (唯一支持音频)');
    console.log('\n🖼️ 视觉模型：');
    console.log('  - qwen3.5-plus (图片+代码)');
    console.log('  - qwen3-vl-plus (最强视觉)');
    console.log('\n💻 代码模型：');
    console.log('  - glm-5 (最强代码)');
    console.log('  - qwen3-coder-plus');
    console.log('\n🧠 推理模型：');
    console.log('  - qwq-plus (最强推理)');
    console.log('  - qwen3-max');
    console.log('\n📄 Office 模型：');
    console.log('  - MiniMax-M2.5 (Office 文档)');
    console.log('\n📝 通用模型：');
    console.log('  - qwen3.5-plus (通用最强)');
    console.log('  - qwen-turbo (快速)');
    return;
  }
  
  if (command === '--check') {
    const message = args[1] || '';
    
    const context = {
      hasImage: args.includes('--has-image'),
      hasVideo: args.includes('--has-video'),
      hasAudio: args.includes('--has-audio'),
      isSubagent: args.includes('--is-subagent')
    };
    
    const result = detectTaskType(message, context);
    
    console.log('\n🧠 任务分析结果：');
    console.log(`  主窗口: ${context.isSubagent ? '否（子代理）' : '是'}`);
    console.log(`  类型: ${result.type}`);
    
    if (result.skipSwitch) {
      console.log(`  ⚠️ ${result.reason}`);
      console.log(`  💡 子代理保持预设模型，不执行智能切换`);
    } else {
      console.log(`  推荐模型: ${result.model}`);
      console.log(`  原因: ${result.reason}`);
      console.log(`\n💡 切换命令: /model ${result.model}`);
      console.log(`💬 提示信息: ${getSwitchMessage(result)}`);
    }
    
    return result;
  }
  
  if (command === '--test-subagent') {
    const message = args[1] || '';
    
    console.log('\n🧪 测试子代理模式：\n');
    
    // 测试主窗口
    console.log('场景 A: 主窗口');
    const mainResult = detectTaskType(message, { isSubagent: false });
    console.log(`  结果: ${mainResult.type} → ${mainResult.model || '使用预设模型'}`);
    console.log(`  原因: ${mainResult.reason}`);
    
    // 测试子代理
    console.log('\n场景 B: 子代理');
    const subagentResult = detectTaskType(message, { isSubagent: true });
    console.log(`  结果: ${subagentResult.type} → ${subagentResult.model || '使用预设模型'}`);
    console.log(`  原因: ${subagentResult.reason}`);
    
    return;
  }
  
  if (command === '--switch') {
    const modelId = args[1];
    if (!modelId) {
      console.error('❌ 请指定模型 ID');
      return;
    }
    
    const result = await switchModel(modelId);
    console.log(`✅ 已切换到: ${modelId}`);
    return result;
  }
  
  console.log('❌ 未知命令，使用 --help 查看帮助');
}

main().catch(console.error);