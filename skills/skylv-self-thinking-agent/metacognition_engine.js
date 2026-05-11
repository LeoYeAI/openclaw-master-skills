/**
 * metacognition_engine.js — AI Agent 元认知引擎
 * 
 * 元认知 = "思考自己的思考"
 * Agent 能够反思自己的决策过程，识别偏差，自我纠正。
 * 
 * Usage: node metacognition_engine.js <command> [args...]
 */

const fs = require('fs');

// ── 认知偏差类型 ───────────────────────────────────────────────────────────────
const BIASES = {
  confirmation_bias: {
    name: '确认偏误',
    description: '倾向于寻找支持现有观点的信息',
    detection: (reasoning, action) => {
      const seeking = /only|just|merely|simply|exactly/gi;
      const matches = (reasoning.match(seeking) || []).length;
      return matches > 2 ? 0.7 : 0.2;
    }
  },
  anchoring_bias: {
    name: '锚定效应',
    description: '过度依赖第一个获得的信息',
    detection: (reasoning, action) => {
      const anchors = /first|initial|original|starting/gi;
      const matches = (reasoning.match(anchors) || []).length;
      return matches > 1 ? 0.6 : 0.1;
    }
  },
  availability_heuristic: {
    name: '可得性启发',
    description: '基于容易回忆的信息做判断',
    detection: (reasoning, action) => {
      const recent = /recently|just now|last time|remember/gi;
      const matches = (reasoning.match(recent) || []).length;
      return matches > 1 ? 0.5 : 0.1;
    }
  },
  overconfidence: {
    name: '过度自信',
    description: '高估自己的判断准确性',
    detection: (reasoning, action) => {
      const confident = /definitely|certainly|obviously|surely|must/gi;
      const matches = (reasoning.match(confident) || []).length;
      return matches > 2 ? 0.8 : 0.2;
    }
  },
  sunk_cost_fallacy: {
    name: '沉没成本谬误',
    description: '因为已投入而继续坚持错误决策',
    detection: (reasoning, action) => {
      const sunk = /already|spent|invested|committed|so far/gi;
      const matches = (reasoning.match(sunk) || []).length;
      return matches > 1 ? 0.6 : 0.1;
    }
  },
  framing_effect: {
    name: '框架效应',
    description: '决策受问题表述方式影响',
    detection: (reasoning, action) => {
      const frames = /if we look at it this way|from this perspective|alternatively/gi;
      const matches = (reasoning.match(frames) || []).length;
      return matches > 0 ? 0.4 : 0.1;
    }
  }
};

// ── 元认知分析 ─────────────────────────────────────────────────────────────────
function analyzeReasoning(reasoning, action = '') {
  const biases = [];
  const warnings = [];
  const suggestions = [];
  
  for (const [key, bias] of Object.entries(BIASES)) {
    const score = bias.detection(reasoning, action);
    if (score > 0.5) {
      biases.push({ key, name: bias.name, score, description: bias.description });
    }
  }
  
  // 生成警告
  if (biases.length > 0) {
    warnings.push(`⚠️ 检测到 ${biases.length} 个潜在认知偏差`);
    for (const b of biases) {
      warnings.push(`  - ${b.name} (${Math.round(b.score * 100)}%): ${b.description}`);
    }
  }
  
  // 生成建议
  if (biases.find(b => b.key === 'confirmation_bias')) {
    suggestions.push('考虑寻找反对意见，验证假设');
  }
  if (biases.find(b => b.key === 'overconfidence')) {
    suggestions.push('评估不确定性，使用概率表达');
  }
  if (biases.find(b => b.key === 'sunk_cost_fallacy')) {
    suggestions.push('基于未来价值做决策，忽略已投入成本');
  }
  if (biases.find(b => b.key === 'anchoring_bias')) {
    suggestions.push('收集更多信息，不要过度依赖初始数据');
  }
  
  return { biases, warnings, suggestions };
}

function reflectOnDecision(reasoning, action, outcome = null) {
  const analysis = analyzeReasoning(reasoning, action);
  
  const reflection = {
    timestamp: new Date().toISOString(),
    reasoning_quality: analysis.biases.length === 0 ? 'good' : analysis.biases.length < 3 ? 'moderate' : 'needs_attention',
    biases_detected: analysis.biases,
    self_correction: analysis.suggestions.length > 0,
    alternative_approaches: []
  };
  
  // 如果提供了结果，评估决策效果
  if (outcome) {
    reflection.outcome = outcome;
    reflection.would_i_decide_differently = analysis.biases.length > 2;
  }
  
  return reflection;
}

function generateAlternativeApproaches(reasoning) {
  const approaches = [];
  
  // 基于检测到的偏差生成替代方案
  const analysis = analyzeReasoning(reasoning);
  
  if (analysis.biases.length === 0) {
    approaches.push('当前推理过程无明显偏差');
  } else {
    approaches.push('## 替代思考角度\n');
    for (const b of analysis.biases) {
      switch (b.key) {
        case 'confirmation_bias':
          approaches.push('- 反向思考：如果我的假设是错的，会有什么证据？');
          break;
        case 'overconfidence':
          approaches.push('- 概率思考：这个结论有多大概率是正确的？');
          break;
        case 'anchoring_bias':
          approaches.push('- 重新评估：如果忽略初始信息，结论会改变吗？');
          break;
        case 'sunk_cost_fallacy':
          approaches.push('- 零基思考：如果从零开始，我会做同样的决策吗？');
          break;
      }
    }
  }
  
  return approaches;
}

// ── 命令处理 ───────────────────────────────────────────────────────────────────
function cmdAnalyze(file) {
  if (!file || !fs.existsSync(file)) {
    console.error('Usage: metacognition_engine.js analyze <file>');
    process.exit(1);
  }
  
  const content = fs.readFileSync(file, 'utf8');
  const analysis = analyzeReasoning(content);
  
  console.log('\n## 元认知分析\n');
  
  if (analysis.biases.length === 0) {
    console.log('✓ 未检测到明显认知偏差');
  } else {
    console.log(`⚠️ 检测到 ${analysis.biases.length} 个潜在认知偏差：\n`);
    for (const b of analysis.biases) {
      console.log(`- **${b.name}** (${Math.round(b.score * 100)}%)`);
      console.log(`  ${b.description}`);
    }
    
    console.log('\n## 建议的自我纠正\n');
    for (const s of analysis.suggestions) {
      console.log(`- ${s}`);
    }
  }
}

function cmdReflect(reasoning, action) {
  if (!reasoning) {
    console.error('Usage: metacognition_engine.js reflect "<reasoning>" "<action>"');
    process.exit(1);
  }
  
  const reflection = reflectOnDecision(reasoning, action || '');
  
  console.log('\n## 决策反思\n');
  console.log(`推理质量: ${reflection.reasoning_quality}`);
  
  if (reflection.biases_detected.length > 0) {
    console.log('\n检测到的偏差:');
    for (const b of reflection.biases_detected) {
      console.log(`  - ${b.name}`);
    }
  }
  
  if (reflection.self_correction) {
    console.log('\n需要自我纠正: 是');
  }
}

function cmdBiases() {
  console.log('\n## 认知偏差类型\n');
  console.log('偏差名称'.padEnd(20) + '描述');
  console.log('─'.repeat(60));
  for (const [key, bias] of Object.entries(BIASES)) {
    console.log(bias.name.padEnd(20) + bias.description);
  }
}

// ── Main ───────────────────────────────────────────────────────────────────────
const [,, cmd, ...args] = process.argv;

const COMMANDS = {
  analyze: () => cmdAnalyze(args[0]),
  reflect: () => cmdReflect(args[0], args[1]),
  biases: cmdBiases,
  help: () => {
    console.log(`metacognition_engine.js — AI Agent Metacognition Engine

Usage: node metacognition_engine.js <command> [args...]

Commands:
  analyze <file>           Analyze reasoning for cognitive biases
  reflect "<reasoning>"    Reflect on a decision
  biases                   List all cognitive bias types

Examples:
  node metacognition_engine.js analyze reasoning.txt
  node metacognition_engine.js reflect "I'm definitely sure this is correct"
  node metacognition_engine.js biases
`);
  }
};

if (!cmd || !COMMANDS[cmd]) {
  COMMANDS.help();
  process.exit(0);
}

COMMANDS[cmd]();
