/**
 * Cost Optimizer — 工具函数库
 *
 * 提供任务分类、token 估算、模型路由、上下文压缩、消耗报告等核心功能。
 * 支持 OpenClaw 和 Claude Code 双平台。
 */

// ============================================================
// 类型定义
// ============================================================

/** 任务优先级，P0 最便宜，P4 最贵 */
export type TaskPriority = "P0" | "P1" | "P2" | "P3" | "P4";

/** 任务分类结果 */
export interface TaskCategory {
  /** 优先级等级 */
  priority: TaskPriority;
  /** 分类名称 */
  name: string;
  /** 匹配的关键词 */
  matchedKeywords: string[];
  /** 复杂度评分 0-10 */
  complexityScore: number;
  /** 分类置信度 0-1 */
  confidence: number;
}

/** 支持的模型 */
export type ModelId =
  | "deepseek/v3"
  | "gemini-2.0-flash"
  | "claude-haiku-4-5"
  | "claude-sonnet-4-6"
  | "claude-opus-4-6";

/** 模型定价（每百万 tokens，美元） */
export interface ModelPricing {
  inputPerMillion: number;
  outputPerMillion: number;
  /** 综合成本估算（假设 input:output = 4:1） */
  blendedPerMillion: number;
}

/** 模型路由选择结果 */
export interface ModelChoice {
  /** 推荐模型 */
  model: ModelId;
  /** 备选模型（降级用） */
  fallback: ModelId;
  /** 选择原因 */
  reason: string;
  /** 预估每次调用成本（美元） */
  estimatedCostPerCall: number;
  /** 相比默认模型（opus）的节省百分比 */
  savingsPercent: number;
}

/** 对话消息 */
export interface Message {
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  /** 工具调用相关信息 */
  toolCall?: {
    name: string;
    result?: string;
  };
  /** 时间戳 */
  timestamp?: string;
}

/** 压缩后的上下文 */
export interface CompressedContext {
  /** 压缩后的消息列表 */
  messages: Message[];
  /** 关键决策摘要 */
  keyDecisions: string[];
  /** 活跃文件列表 */
  activeFiles: Array<{ path: string; summary: string }>;
  /** 待处理事项 */
  pendingTodos: string[];
  /** 压缩统计 */
  stats: {
    originalTokens: number;
    compressedTokens: number;
    compressionRatio: number;
    turnsPreserved: number;
    turnsSummarized: number;
  };
}

/** 单条使用记录 */
export interface UsageEntry {
  timestamp: string;
  session_id: string;
  model: ModelId;
  input_tokens: number;
  output_tokens: number;
  task_type: string;
  cost_usd: number;
  routed: boolean;
  original_model: ModelId | null;
}

/** 使用报告 */
export interface UsageReport {
  /** 时间范围 */
  period: { start: string; end: string };
  /** 总计 */
  totals: {
    tokens: number;
    inputTokens: number;
    outputTokens: number;
    cost: number;
    sessions: number;
  };
  /** 按模型分类 */
  byModel: Record<
    string,
    { tokens: number; cost: number; percentage: number }
  >;
  /** 按任务类型分类 */
  byTaskType: Record<
    string,
    { count: number; avgTokens: number; totalCost: number; percentage: number }
  >;
  /** 每日明细 */
  daily: Array<{ date: string; tokens: number; cost: number }>;
  /** 节省建议 */
  recommendations: string[];
}

/** 节省估算 */
export interface SavingsEstimate {
  /** 实际成本 */
  actualCost: number;
  /** 优化后预估成本 */
  optimizedCost: number;
  /** 节省金额 */
  savedAmount: number;
  /** 节省百分比 */
  savedPercent: number;
  /** 各优化项的贡献 */
  breakdown: Array<{
    optimization: string;
    savedAmount: number;
    description: string;
  }>;
}

// ============================================================
// 常量
// ============================================================

/** 模型定价表（截至 2026-03） */
const MODEL_PRICING: Record<ModelId, ModelPricing> = {
  "deepseek/v3": {
    inputPerMillion: 0.07,
    outputPerMillion: 0.14,
    blendedPerMillion: 0.084,
  },
  "gemini-2.0-flash": {
    inputPerMillion: 0.10,
    outputPerMillion: 0.40,
    blendedPerMillion: 0.16,
  },
  "claude-haiku-4-5": {
    inputPerMillion: 0.80,
    outputPerMillion: 4.00,
    blendedPerMillion: 1.44,
  },
  "claude-sonnet-4-6": {
    inputPerMillion: 3.00,
    outputPerMillion: 15.00,
    blendedPerMillion: 5.40,
  },
  "claude-opus-4-6": {
    inputPerMillion: 15.00,
    outputPerMillion: 75.00,
    blendedPerMillion: 27.00,
  },
};

/** 降级链 */
const DEGRADATION_CHAIN: ModelId[] = [
  "claude-opus-4-6",
  "claude-sonnet-4-6",
  "claude-haiku-4-5",
  "gemini-2.0-flash",
  "deepseek/v3",
];

/** 关键词到优先级的映射 */
const KEYWORD_MAP: Record<TaskPriority, string[]> = {
  P0: [
    "heartbeat", "ping", "status", "health", "alive", "cron", "schedule",
    "心跳", "检查状态", "是否在线",
  ],
  P1: [
    "list", "find", "search", "grep", "count", "ls", "pwd", "which", "where",
    "找到", "搜索", "列出", "有几个",
  ],
  P2: [
    "read", "cat", "format", "lint", "fix typo", "rename", "move",
    "complete", "autocomplete", "suggest", "snippet",
    "读取", "格式化", "补全", "重命名",
  ],
  P3: [
    "write", "create", "implement", "generate", "test", "debug", "explain",
    "refactor", "fix bug", "add feature",
    "写", "创建", "实现", "生成", "测试", "调试",
  ],
  P4: [
    "architect", "design", "plan", "review", "migrate",
    "从零开始", "重新设计", "全面重构",
  ],
};

/** 优先级对应的默认模型 */
const PRIORITY_MODEL_MAP: Record<TaskPriority, ModelId> = {
  P0: "deepseek/v3",
  P1: "gemini-2.0-flash",
  P2: "claude-haiku-4-5",
  P3: "claude-sonnet-4-6",
  P4: "claude-opus-4-6",
};

/** 优先级对应的备选模型 */
const PRIORITY_FALLBACK_MAP: Record<TaskPriority, ModelId> = {
  P0: "gemini-2.0-flash",
  P1: "claude-haiku-4-5",
  P2: "gemini-2.0-flash",
  P3: "claude-haiku-4-5",
  P4: "claude-sonnet-4-6",
};

// ============================================================
// 核心函数
// ============================================================

/**
 * 任务分类 — 分析 prompt 并返回分类结果
 *
 * 通过关键词匹配 + 复杂度评分确定任务优先级。
 * 优先级越低（P0）使用越便宜的模型。
 */
export function classifyTask(prompt: string): TaskCategory {
  const lowerPrompt = prompt.toLowerCase();
  const matchResults: Record<TaskPriority, string[]> = {
    P0: [], P1: [], P2: [], P3: [], P4: [],
  };

  // 关键词匹配
  for (const [priority, keywords] of Object.entries(KEYWORD_MAP)) {
    for (const kw of keywords) {
      if (lowerPrompt.includes(kw.toLowerCase())) {
        matchResults[priority as TaskPriority].push(kw);
      }
    }
  }

  // 复杂度评分
  const complexityScore = calculateComplexity(prompt);

  // 确定优先级：取匹配关键词最多的最低优先级（最便宜）
  // 但如果复杂度高，向上调整
  let bestPriority: TaskPriority = "P3"; // 默认中等
  let bestMatches: string[] = [];
  let maxMatches = 0;

  // 从低到高扫描，优先选便宜的
  const priorities: TaskPriority[] = ["P0", "P1", "P2", "P3", "P4"];
  for (const p of priorities) {
    if (matchResults[p].length > maxMatches) {
      maxMatches = matchResults[p].length;
      bestPriority = p;
      bestMatches = matchResults[p];
    }
  }

  // 复杂度修正：高复杂度任务不应使用低成本模型
  if (complexityScore >= 9 && (bestPriority === "P0" || bestPriority === "P1" || bestPriority === "P2")) {
    bestPriority = "P4";
  } else if (complexityScore >= 6 && (bestPriority === "P0" || bestPriority === "P1")) {
    bestPriority = "P3";
  }

  // 无关键词匹配时，基于复杂度决定
  if (maxMatches === 0) {
    if (complexityScore <= 2) bestPriority = "P1";
    else if (complexityScore <= 5) bestPriority = "P2";
    else if (complexityScore <= 8) bestPriority = "P3";
    else bestPriority = "P4";
  }

  // 置信度：基于关键词匹配数量和复杂度评分一致性
  const confidence = Math.min(1.0, 0.3 + maxMatches * 0.15 + (complexityScore > 0 ? 0.2 : 0));

  const priorityNames: Record<TaskPriority, string> = {
    P0: "heartbeat_status",
    P1: "simple_query",
    P2: "file_ops_completion",
    P3: "code_generation",
    P4: "complex_architecture",
  };

  return {
    priority: bestPriority,
    name: priorityNames[bestPriority],
    matchedKeywords: bestMatches,
    complexityScore,
    confidence,
  };
}

/**
 * Token 估算 — 基于字符数快速估算 token 数量
 *
 * 使用经验公式：
 * - 英文：约 4 字符/token
 * - 中文：约 2 字符/token（每个汉字约 1.5-2 tokens）
 * - 代码：约 3.5 字符/token
 * - 混合内容取加权平均
 */
export function estimateTokens(text: string): number {
  if (!text) return 0;

  // 统计中文字符数
  const chineseChars = (text.match(/[\u4e00-\u9fff\u3400-\u4dbf]/g) || []).length;
  // 统计代码特征字符（花括号、分号、箭头等）
  const codeChars = (text.match(/[{};()=><!&|?:\/\\@#$%^*~`]/g) || []).length;
  const totalChars = text.length;
  const nonChineseChars = totalChars - chineseChars;

  // 代码占比
  const codeRatio = Math.min(1, codeChars / Math.max(1, totalChars) * 5);

  // 中文部分：约 1.5 tokens/字符
  const chineseTokens = chineseChars * 1.5;
  // 非中文部分：英文 ~4 字符/token，代码 ~3.5 字符/token
  const avgCharsPerToken = 4 - codeRatio * 0.5; // 代码多则每 token 字符少
  const nonChineseTokens = nonChineseChars / avgCharsPerToken;

  return Math.ceil(chineseTokens + nonChineseTokens);
}

/**
 * 模型路由 — 根据任务分类和上下文大小选择最优模型
 *
 * 综合考虑任务复杂度、上下文大小和成本，
 * 选择满足质量要求的最便宜模型。
 */
export function routeModel(
  category: TaskCategory,
  contextSize: number
): ModelChoice {
  let targetPriority = category.priority;

  // 上下文大小修正：超大上下文可能需要更强的模型来处理
  if (contextSize > 100000 && targetPriority !== "P4") {
    // 上下文超过 100k，至少用 P3
    const priorityOrder: TaskPriority[] = ["P0", "P1", "P2", "P3", "P4"];
    const currentIndex = priorityOrder.indexOf(targetPriority);
    if (currentIndex < 3) {
      targetPriority = "P3";
    }
  }

  const model = PRIORITY_MODEL_MAP[targetPriority];
  const fallback = PRIORITY_FALLBACK_MAP[targetPriority];
  const pricing = MODEL_PRICING[model];
  const opusPricing = MODEL_PRICING["claude-opus-4-6"];

  // 估算每次调用成本（假设平均 5k tokens）
  const avgTokens = 5000;
  const estimatedCost = (avgTokens / 1_000_000) * pricing.blendedPerMillion;
  const opusCost = (avgTokens / 1_000_000) * opusPricing.blendedPerMillion;
  const savingsPercent = Math.round(((opusCost - estimatedCost) / opusCost) * 100);

  const reasons: string[] = [];
  if (category.matchedKeywords.length > 0) {
    reasons.push(`关键词匹配: [${category.matchedKeywords.join(", ")}]`);
  }
  reasons.push(`复杂度: ${category.complexityScore}/10`);
  if (contextSize > 0) {
    reasons.push(`上下文: ${contextSize} tokens`);
  }

  return {
    model,
    fallback,
    reason: reasons.join(", "),
    estimatedCostPerCall: Math.round(estimatedCost * 1_000_000) / 1_000_000,
    savingsPercent,
  };
}

/**
 * 上下文压缩 — 在 token 预算内压缩对话历史
 *
 * 保留最近几轮完整对话，历史部分提取摘要，
 * 工具调用结果只保留关键输出。
 */
export function compressContext(
  messages: Message[],
  budget: number
): CompressedContext {
  const keepRecentTurns = 5;
  const totalTokens = messages.reduce((sum, m) => sum + estimateTokens(m.content), 0);

  // 分离最近的和历史的消息
  const recentMessages = messages.slice(-keepRecentTurns * 2); // 每轮 2 条（user + assistant）
  const oldMessages = messages.slice(0, -keepRecentTurns * 2);

  const compressedMessages: Message[] = [];
  const keyDecisions: string[] = [];
  const activeFiles: Array<{ path: string; summary: string }> = [];
  const pendingTodos: string[] = [];

  // 压缩历史消息
  for (const msg of oldMessages) {
    if (msg.role === "tool" && msg.toolCall) {
      // 工具调用结果：只保留关键信息
      const summary = compressToolResult(msg);
      compressedMessages.push({
        role: "system",
        content: summary,
      });

      // 提取文件路径
      const filePaths = extractFilePaths(msg.content);
      for (const fp of filePaths) {
        if (!activeFiles.find((f) => f.path === fp)) {
          activeFiles.push({ path: fp, summary: "已在历史对话中引用" });
        }
      }
    } else if (msg.role === "assistant") {
      // 助手回复：提取关键决策
      const decisions = extractDecisions(msg.content);
      keyDecisions.push(...decisions);

      // 提取待办事项
      const todos = extractTodos(msg.content);
      pendingTodos.push(...todos);

      // 生成一句话摘要
      const summary = summarizeMessage(msg.content);
      compressedMessages.push({
        role: "assistant",
        content: `[摘要] ${summary}`,
      });
    } else if (msg.role === "user") {
      // 用户消息：保留关键请求
      const summary = summarizeMessage(msg.content);
      compressedMessages.push({
        role: "user",
        content: `[摘要] ${summary}`,
      });
    }
  }

  // 完整保留最近的消息
  compressedMessages.push(...recentMessages);

  const compressedTokens = compressedMessages.reduce(
    (sum, m) => sum + estimateTokens(m.content),
    0
  );

  return {
    messages: compressedMessages,
    keyDecisions: [...new Set(keyDecisions)],
    activeFiles,
    pendingTodos: [...new Set(pendingTodos)],
    stats: {
      originalTokens: totalTokens,
      compressedTokens,
      compressionRatio:
        totalTokens > 0
          ? Math.round(((totalTokens - compressedTokens) / totalTokens) * 100)
          : 0,
      turnsPreserved: keepRecentTurns,
      turnsSummarized: Math.floor(oldMessages.length / 2),
    },
  };
}

/** JSONL 解析结果 */
export interface ParseResult {
  entries: UsageEntry[];
  /** 解析失败被跳过的行数 */
  skippedLines: number;
  /** 解析失败的行号列表（用于诊断） */
  skippedLineNumbers: number[];
}

/**
 * 安全解析 JSONL 使用日志 — 跳过损坏行并报告
 *
 * 逐行解析，单行 JSON 损坏不影响其余有效数据。
 * 返回解析成功的条目及跳过的行数统计。
 */
export function parseUsageLog(rawContent: string): ParseResult {
  const lines = rawContent.split("\n").filter((l) => l.trim().length > 0);
  const entries: UsageEntry[] = [];
  const skippedLineNumbers: number[] = [];

  for (let i = 0; i < lines.length; i++) {
    try {
      const entry = JSON.parse(lines[i]) as UsageEntry;
      // 基本字段校验：必须有 timestamp 和 model
      if (entry.timestamp && entry.model) {
        entries.push(entry);
      } else {
        skippedLineNumbers.push(i + 1);
      }
    } catch {
      skippedLineNumbers.push(i + 1);
    }
  }

  return {
    entries,
    skippedLines: skippedLineNumbers.length,
    skippedLineNumbers: skippedLineNumbers.slice(0, 20), // 最多保留前 20 个行号
  };
}

/**
 * 消耗报告生成 — 从使用日志生成统计报告
 *
 * 读取 JSONL 格式的使用日志，按模型、任务类型、日期聚合，
 * 并生成节省建议。
 */
export function generateUsageReport(entries: UsageEntry[]): UsageReport {
  if (entries.length === 0) {
    return emptyReport();
  }

  // 时间范围
  const timestamps = entries.map((e) => e.timestamp).sort();
  const period = { start: timestamps[0], end: timestamps[timestamps.length - 1] };

  // 总计
  const totals = {
    tokens: 0,
    inputTokens: 0,
    outputTokens: 0,
    cost: 0,
    sessions: new Set<string>(),
  };
  const byModel: Record<string, { tokens: number; cost: number; percentage: number }> = {};
  const byTaskType: Record<string, { count: number; avgTokens: number; totalCost: number; totalTokens: number; percentage: number }> = {};
  const dailyMap: Record<string, { tokens: number; cost: number }> = {};

  for (const entry of entries) {
    const entryTokens = entry.input_tokens + entry.output_tokens;
    totals.tokens += entryTokens;
    totals.inputTokens += entry.input_tokens;
    totals.outputTokens += entry.output_tokens;
    totals.cost += entry.cost_usd;
    totals.sessions.add(entry.session_id);

    // 按模型聚合
    const modelKey = entry.model;
    if (!byModel[modelKey]) {
      byModel[modelKey] = { tokens: 0, cost: 0, percentage: 0 };
    }
    byModel[modelKey].tokens += entryTokens;
    byModel[modelKey].cost += entry.cost_usd;

    // 按任务类型聚合
    const taskKey = entry.task_type || "other";
    if (!byTaskType[taskKey]) {
      byTaskType[taskKey] = { count: 0, avgTokens: 0, totalCost: 0, totalTokens: 0, percentage: 0 };
    }
    byTaskType[taskKey].count += 1;
    byTaskType[taskKey].totalTokens += entryTokens;
    byTaskType[taskKey].totalCost += entry.cost_usd;

    // 按日期聚合
    const dateKey = entry.timestamp.slice(0, 10);
    if (!dailyMap[dateKey]) {
      dailyMap[dateKey] = { tokens: 0, cost: 0 };
    }
    dailyMap[dateKey].tokens += entryTokens;
    dailyMap[dateKey].cost += entry.cost_usd;
  }

  // 计算百分比
  for (const key of Object.keys(byModel)) {
    byModel[key].percentage = totals.cost > 0 ? Math.round((byModel[key].cost / totals.cost) * 100) : 0;
    byModel[key].cost = round2(byModel[key].cost);
  }

  const byTaskTypeResult: Record<string, { count: number; avgTokens: number; totalCost: number; percentage: number }> = {};
  for (const key of Object.keys(byTaskType)) {
    const t = byTaskType[key];
    byTaskTypeResult[key] = {
      count: t.count,
      avgTokens: t.count > 0 ? Math.round(t.totalTokens / t.count) : 0,
      totalCost: round2(t.totalCost),
      percentage: totals.cost > 0 ? Math.round((t.totalCost / totals.cost) * 100) : 0,
    };
  }

  // 日期排序
  const daily = Object.entries(dailyMap)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, data]) => ({
      date,
      tokens: data.tokens,
      cost: round2(data.cost),
    }));

  // 生成节省建议
  const recommendations = generateRecommendations(byModel, byTaskTypeResult, totals.cost);

  return {
    period,
    totals: {
      tokens: totals.tokens,
      inputTokens: totals.inputTokens,
      outputTokens: totals.outputTokens,
      cost: round2(totals.cost),
      sessions: totals.sessions.size,
    },
    byModel,
    byTaskType: byTaskTypeResult,
    daily,
    recommendations,
  };
}

/**
 * 节省估算 — 比较实际使用与优化后的成本差异
 *
 * 逐条分析使用记录，模拟如果启用智能路由后各条记录会使用哪个模型，
 * 计算总体节省。
 */
export function calculateSavings(
  entries: UsageEntry[]
): SavingsEstimate {
  let actualCost = 0;
  let optimizedCost = 0;

  const breakdownMap: Record<string, { saved: number; description: string }> = {
    routing: { saved: 0, description: "智能模型路由：低复杂度任务使用便宜模型" },
    heartbeat: { saved: 0, description: "Heartbeat 优化：减少频率 + 使用最低成本模型" },
    context: { saved: 0, description: "上下文压缩：减少每次调用的 token 数" },
  };

  for (const entry of entries) {
    actualCost += entry.cost_usd;

    // 模拟路由后的成本
    const category = classifyTask(entry.task_type);
    const routedModel = PRIORITY_MODEL_MAP[category.priority];
    const routedPricing = MODEL_PRICING[routedModel];
    const routedCost =
      (entry.input_tokens / 1_000_000) * routedPricing.inputPerMillion +
      (entry.output_tokens / 1_000_000) * routedPricing.outputPerMillion;

    optimizedCost += routedCost;

    // 分类节省来源
    if (entry.task_type === "heartbeat") {
      breakdownMap.heartbeat.saved += entry.cost_usd - routedCost;
    } else {
      breakdownMap.routing.saved += entry.cost_usd - routedCost;
    }
  }

  // 上下文压缩节省估算：假设能减少 30% 的 token
  const contextSavings = optimizedCost * 0.3;
  optimizedCost *= 0.7;
  breakdownMap.context.saved = contextSavings;

  const savedAmount = actualCost - optimizedCost;
  const savedPercent =
    actualCost > 0 ? Math.round((savedAmount / actualCost) * 100) : 0;

  return {
    actualCost: round2(actualCost),
    optimizedCost: round2(optimizedCost),
    savedAmount: round2(savedAmount),
    savedPercent,
    breakdown: Object.entries(breakdownMap).map(([optimization, data]) => ({
      optimization,
      savedAmount: round2(data.saved),
      description: data.description,
    })),
  };
}

// ============================================================
// 辅助函数
// ============================================================

/** 计算 prompt 的复杂度评分 (0-10) */
function calculateComplexity(prompt: string): number {
  let score = 0;

  // 长度因子：长 prompt 通常更复杂
  const tokens = estimateTokens(prompt);
  if (tokens > 2000) score += 3;
  else if (tokens > 500) score += 2;
  else if (tokens > 100) score += 1;

  // 多步骤指示词
  const multiStepPatterns = [
    /(?:first|then|next|after|finally|步骤|第[一二三四五六七八九十]步)/gi,
    /(?:1\.|2\.|3\.|\d+\))/g,
  ];
  for (const pattern of multiStepPatterns) {
    const matches = prompt.match(pattern);
    if (matches && matches.length >= 3) score += 2;
    else if (matches && matches.length >= 2) score += 1;
  }

  // 代码相关复杂度
  const codePatterns = prompt.match(/```/g);
  if (codePatterns && codePatterns.length >= 4) score += 2;
  else if (codePatterns && codePatterns.length >= 2) score += 1;

  // 多文件操作
  const fileRefs = prompt.match(/(?:[\w-]+\/)+[\w.-]+\.\w+/g);
  if (fileRefs && fileRefs.length >= 5) score += 2;
  else if (fileRefs && fileRefs.length >= 2) score += 1;

  // 架构/设计关键词
  const architectureKeywords = /(?:architect|design|system|infrastructure|migration|refactor|重构|架构|设计|迁移)/gi;
  if (architectureKeywords.test(prompt)) score += 1;

  return Math.min(10, score);
}

/** 压缩工具调用结果 */
function compressToolResult(msg: Message): string {
  const toolName = msg.toolCall?.name || "unknown";
  const content = msg.content;
  const contentTokens = estimateTokens(content);

  // 短结果不压缩
  if (contentTokens < 100) {
    return `[${toolName}] ${content}`;
  }

  // 提取文件路径
  const paths = extractFilePaths(content);
  const pathInfo = paths.length > 0 ? `文件: ${paths.slice(0, 3).join(", ")}` : "";

  // 提取行数（如果是文件读取）
  const lineMatch = content.match(/(\d+)\s*行/);
  const lineInfo = lineMatch ? `${lineMatch[1]} 行` : "";

  // 提取错误信息
  const errorMatch = content.match(/(?:error|Error|ERROR|失败|failed)[^\n]*/);
  const errorInfo = errorMatch ? `错误: ${errorMatch[0]}` : "";

  // 取首尾各 3 行
  const lines = content.split("\n");
  const preview =
    lines.length > 10
      ? [...lines.slice(0, 3), `... (${lines.length - 6} 行省略)`, ...lines.slice(-3)].join("\n")
      : content;

  return `[${toolName}] ${[pathInfo, lineInfo, errorInfo].filter(Boolean).join(", ")} | 原始 ${contentTokens} tokens → 已压缩\n${preview}`;
}

/** 从文本中提取文件路径 */
function extractFilePaths(text: string): string[] {
  const pathPattern = /(?:\/[\w.-]+)+\.[\w]+/g;
  const matches = text.match(pathPattern) || [];
  return [...new Set(matches)];
}

/** 从助手回复中提取关键决策 */
function extractDecisions(text: string): string[] {
  const decisions: string[] = [];
  const patterns = [
    /(?:决定|选择|采用|使用|确认)[：:]\s*(.+)/g,
    /(?:I'll|Let's|We should|Going to)\s+(.+?)(?:\.|$)/gi,
  ];
  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(text)) !== null) {
      decisions.push(match[1].trim().slice(0, 100));
    }
  }
  return decisions.slice(0, 5);
}

/** 从文本中提取待办事项 */
function extractTodos(text: string): string[] {
  const todos: string[] = [];
  const patterns = [
    /(?:TODO|FIXME|待办|还需要|接下来)[：:]\s*(.+)/gi,
    /- \[ \]\s*(.+)/g,
  ];
  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(text)) !== null) {
      todos.push(match[1].trim().slice(0, 100));
    }
  }
  return todos.slice(0, 10);
}

/** 生成消息的一句话摘要（取首行或前 80 字符） */
function summarizeMessage(text: string): string {
  const firstLine = text.split("\n").find((l) => l.trim().length > 0) || "";
  if (firstLine.length <= 80) return firstLine;
  return firstLine.slice(0, 77) + "...";
}

/** 生成节省建议 */
function generateRecommendations(
  byModel: Record<string, { tokens: number; cost: number; percentage: number }>,
  byTaskType: Record<string, { count: number; avgTokens: number; totalCost: number; percentage: number }>,
  totalCost: number
): string[] {
  const recs: string[] = [];

  // 检查是否大量使用高成本模型
  const opusData = byModel["claude-opus-4-6"];
  if (opusData && opusData.percentage > 50) {
    recs.push(
      `Opus 占比 ${opusData.percentage}%（$${opusData.cost}）。启用智能路由后，预计 60-70% 的 Opus 调用可降级到 Sonnet 或更低。`
    );
  }

  // 检查 heartbeat 成本
  const hbData = byTaskType["heartbeat"];
  if (hbData && hbData.totalCost > 5) {
    recs.push(
      `Heartbeat 消耗 $${hbData.totalCost}（${hbData.percentage}%）。使用 deepseek/v3 + 精简内容 + 延长间隔可将成本降至 $${round2(hbData.totalCost * 0.05)}。`
    );
  }

  // 检查简单任务是否使用了昂贵模型
  const simpleTypes = ["status_check", "simple_query", "file_read"];
  for (const t of simpleTypes) {
    if (byTaskType[t] && byTaskType[t].totalCost > 2) {
      recs.push(
        `"${t}" 类任务消耗 $${byTaskType[t].totalCost}，建议路由到 Haiku 或 Gemini Flash。`
      );
    }
  }

  // 通用建议
  if (totalCost > 10) {
    recs.push("启用上下文自动压缩（50k token 阈值），可额外节省 20-30% token 消耗。");
  }

  if (recs.length === 0) {
    recs.push("当前消耗较低，暂无额外优化建议。");
  }

  return recs;
}

/** 生成空报告 */
function emptyReport(): UsageReport {
  return {
    period: { start: "", end: "" },
    totals: { tokens: 0, inputTokens: 0, outputTokens: 0, cost: 0, sessions: 0 },
    byModel: {},
    byTaskType: {},
    daily: [],
    recommendations: ["暂无使用数据。开始使用后，日志将记录到 ~/.openclaw/usage-log.jsonl。"],
  };
}

/** 四舍五入到 2 位小数 */
function round2(n: number): number {
  return Math.round(n * 100) / 100;
}

// ============================================================
// ASCII 图表工具
// ============================================================

/** 生成 ASCII 柱状图 */
export function renderAsciiBarChart(
  daily: Array<{ date: string; cost: number }>,
  width: number = 20
): string {
  if (daily.length === 0) return "(无数据)";

  const maxCost = Math.max(...daily.map((d) => d.cost));
  const lines: string[] = [];

  for (const day of daily) {
    const date = day.date.slice(5); // MM-DD
    const barLength = maxCost > 0 ? Math.round((day.cost / maxCost) * width) : 0;
    const bar = "█".repeat(barLength) + "░".repeat(width - barLength);
    lines.push(`${date}  | $${day.cost.toFixed(2).padStart(6)} | ${bar}`);
  }

  const totalCost = daily.reduce((s, d) => s + d.cost, 0);
  const avgCost = totalCost / daily.length;
  lines.push(`${"".padStart(7)}+---------+${"─".repeat(width)}`);
  lines.push(`${"".padStart(9)}总计: $${totalCost.toFixed(2)}  日均: $${avgCost.toFixed(2)}`);

  return lines.join("\n");
}
