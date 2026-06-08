/**
 * capability-evolver — Pure Logic Skill (Local)
 * Local skill by Claw0x - runs entirely in your OpenClaw agent
 * 
 * Meta-skill that allows AI agents to inspect runtime history, identify failures
 * or inefficiencies, and generate actionable improvement recommendations.
 * No external API calls, no API key required. Complete privacy.
 *
 * Actions:
 *   analyze  — 分析日志，检测 pattern，计算健康评分，生成建议
 *   evolve   — 基于分析结果，按策略生成结构化改进方案
 *   status   — 返回 skill 运行状态
 */

// ─── Types ───────────────────────────────────────────────────

type EvolveAction = 'analyze' | 'evolve' | 'status';
type EvolveStrategy = 'balanced' | 'innovate' | 'harden' | 'repair-only' | 'auto';

interface Input {
  action: EvolveAction;
  strategy?: EvolveStrategy;
  review_mode?: boolean;
  logs?: LogEntry[];
  target_file?: string;
  input?: any;
}

interface LogEntry {
  timestamp: string;
  level: 'error' | 'warn' | 'info' | 'debug';
  message: string;
  context?: string;
  stack?: string;
}

interface PatternEntry {
  type: 'error' | 'regression' | 'inefficiency' | 'drift';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  occurrences: number;
  first_seen: string;
  last_seen: string;
  affected_files: string[];
}

interface AnalysisResult {
  patterns: PatternEntry[];
  health_score: number;
  recommendations: string[];
  summary: {
    total_logs: number;
    error_count: number;
    warn_count: number;
    unique_patterns: number;
    critical_count: number;
  };
}

interface EvolutionProposal {
  evolution_id: string;
  strategy: EvolveStrategy;
  recommendations: Array<{
    priority: 'immediate' | 'high' | 'medium' | 'low';
    category: 'error-handling' | 'performance' | 'stability' | 'architecture' | 'monitoring';
    description: string;
    affected_files: string[];
    suggested_approach: string;
  }>;
  risk_assessment: {
    level: 'low' | 'medium' | 'high';
    factors: string[];
  };
  estimated_improvement: string;
}

// ─── Validation ──────────────────────────────────────────────

const VALID_ACTIONS: EvolveAction[] = ['analyze', 'evolve', 'status'];
const VALID_STRATEGIES: EvolveStrategy[] = ['balanced', 'innovate', 'harden', 'repair-only', 'auto'];

function validateRequest(input: any): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!input.action || !VALID_ACTIONS.includes(input.action)) {
    errors.push(`"action" must be one of: ${VALID_ACTIONS.join(', ')}`);
  }

  if (input.strategy && !VALID_STRATEGIES.includes(input.strategy)) {
    errors.push(`"strategy" must be one of: ${VALID_STRATEGIES.join(', ')}`);
  }

  if ((input.action === 'analyze' || input.action === 'evolve') &&
      (!input.logs || !Array.isArray(input.logs) || input.logs.length === 0)) {
    errors.push('"logs" array is required for analyze/evolve actions');
  }

  return { valid: errors.length === 0, errors };
}


// ─── Analyze: 纯本地日志分析引擎 ────────────────────────────

function handleAnalyze(logs: LogEntry[]): AnalysisResult {
  const patterns: PatternEntry[] = [];
  const errorMap = new Map<string, { count: number; first: string; last: string; files: Set<string> }>();

  for (const log of logs) {
    if (log.level === 'error' || log.level === 'warn') {
      const key = log.message.slice(0, 100);
      const existing = errorMap.get(key);
      if (existing) {
        existing.count++;
        existing.last = log.timestamp;
        if (log.context) existing.files.add(log.context);
      } else {
        errorMap.set(key, {
          count: 1,
          first: log.timestamp,
          last: log.timestamp,
          files: new Set(log.context ? [log.context] : []),
        });
      }
    }
  }

  for (const [msg, data] of errorMap) {
    const severity = data.count >= 10 ? 'critical' : data.count >= 5 ? 'high' : data.count >= 2 ? 'medium' : 'low';
    patterns.push({
      type: data.count >= 3 ? 'regression' : 'error',
      severity,
      description: msg,
      occurrences: data.count,
      first_seen: data.first,
      last_seen: data.last,
      affected_files: Array.from(data.files),
    });
  }

  // Detect inefficiency patterns (info logs with timing hints)
  const slowOps = logs.filter(l => l.level === 'info' && /(\d{4,})ms|slow|timeout/i.test(l.message));
  if (slowOps.length >= 2) {
    patterns.push({
      type: 'inefficiency',
      severity: slowOps.length >= 5 ? 'high' : 'medium',
      description: `${slowOps.length} slow operations detected in logs`,
      occurrences: slowOps.length,
      first_seen: slowOps[0].timestamp,
      last_seen: slowOps[slowOps.length - 1].timestamp,
      affected_files: [...new Set(slowOps.map(l => l.context).filter(Boolean) as string[])],
    });
  }

  const totalLogs = logs.length;
  const errorCount = logs.filter(l => l.level === 'error').length;
  const warnCount = logs.filter(l => l.level === 'warn').length;
  const healthScore = Math.max(0, Math.round(
    100 - (errorCount / Math.max(totalLogs, 1)) * 100 - (warnCount / Math.max(totalLogs, 1)) * 30
  ));

  const criticalCount = patterns.filter(p => p.severity === 'critical').length;

  // Generate recommendations
  const recommendations: string[] = [];
  if (criticalCount > 0) {
    recommendations.push('Critical patterns detected — prioritize immediate fixes before any new development');
  }
  if (patterns.filter(p => p.type === 'regression').length >= 2) {
    recommendations.push('Multiple regressions found — add regression tests and consider "harden" strategy');
  }
  if (healthScore > 80 && patterns.length < 3) {
    recommendations.push('System is healthy — safe to pursue "innovate" strategy for capability expansion');
  }
  if (healthScore < 50) {
    recommendations.push('Low health score — enable review_mode and focus on stability before adding features');
  }
  if (patterns.some(p => p.type === 'inefficiency')) {
    recommendations.push('Performance bottlenecks detected — profile slow operations and add caching where applicable');
  }

  // File-specific recommendations
  const hotFiles = patterns
    .flatMap(p => p.affected_files)
    .reduce((acc, f) => { acc[f] = (acc[f] || 0) + 1; return acc; }, {} as Record<string, number>);
  const topHotFiles = Object.entries(hotFiles).sort((a, b) => b[1] - a[1]).slice(0, 3);
  if (topHotFiles.length > 0) {
    recommendations.push(`Hot files (most issues): ${topHotFiles.map(([f, c]) => `${f} (${c})`).join(', ')}`);
  }

  return {
    patterns: patterns.sort((a, b) => b.occurrences - a.occurrences).slice(0, 50),
    health_score: healthScore,
    recommendations,
    summary: { total_logs: totalLogs, error_count: errorCount, warn_count: warnCount, unique_patterns: patterns.length, critical_count: criticalCount },
  };
}


// ─── Evolve: 基于分析结果生成结构化改进方案 ─────────────────

function handleEvolve(logs: LogEntry[], strategy: EvolveStrategy, targetFile?: string): EvolutionProposal {
  const analysis = handleAnalyze(logs);
  const evolutionId = `evo_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;

  // Auto-select strategy based on health
  const effectiveStrategy = strategy === 'auto'
    ? (analysis.health_score < 40 ? 'repair-only' : analysis.health_score < 70 ? 'harden' : 'balanced')
    : strategy;

  const recommendations: EvolutionProposal['recommendations'] = [];

  // Generate recommendations based on patterns and strategy
  for (const pattern of analysis.patterns) {
    // Filter by target file if specified
    if (targetFile && !pattern.affected_files.includes(targetFile) && pattern.affected_files.length > 0) continue;

    if (pattern.severity === 'critical' || effectiveStrategy === 'repair-only') {
      recommendations.push({
        priority: 'immediate',
        category: 'error-handling',
        description: `Fix: ${pattern.description}`,
        affected_files: pattern.affected_files,
        suggested_approach: pattern.type === 'regression'
          ? 'Add regression test, then fix the root cause. Check recent changes to affected files.'
          : 'Add try-catch or input validation. Review error boundary coverage.',
      });
    }

    if (pattern.type === 'inefficiency' && effectiveStrategy !== 'repair-only') {
      recommendations.push({
        priority: 'medium',
        category: 'performance',
        description: `Optimize: ${pattern.description}`,
        affected_files: pattern.affected_files,
        suggested_approach: 'Profile the slow path, add caching, or batch operations where possible.',
      });
    }

    if (pattern.type === 'regression' && (effectiveStrategy === 'harden' || effectiveStrategy === 'balanced')) {
      recommendations.push({
        priority: 'high',
        category: 'stability',
        description: `Stabilize: ${pattern.description} (${pattern.occurrences} occurrences)`,
        affected_files: pattern.affected_files,
        suggested_approach: 'Write targeted tests for this scenario. Add monitoring/alerting for early detection.',
      });
    }
  }

  // Strategy-specific additions
  if (effectiveStrategy === 'innovate' && analysis.health_score > 70) {
    recommendations.push({
      priority: 'low',
      category: 'architecture',
      description: 'System is stable — consider adding new capabilities or refactoring for extensibility',
      affected_files: [],
      suggested_approach: 'Identify the most-called code paths and optimize or extend them.',
    });
  }

  if (effectiveStrategy === 'harden') {
    recommendations.push({
      priority: 'high',
      category: 'monitoring',
      description: 'Add structured logging and health checks to detect issues earlier',
      affected_files: analysis.patterns.flatMap(p => p.affected_files).filter((v, i, a) => a.indexOf(v) === i).slice(0, 5),
      suggested_approach: 'Add error rate metrics, latency tracking, and automated alerting thresholds.',
    });
  }

  // Risk assessment
  const criticalPatterns = analysis.patterns.filter(p => p.severity === 'critical');
  const riskLevel = criticalPatterns.length >= 3 ? 'high' : criticalPatterns.length >= 1 ? 'medium' : 'low';

  return {
    evolution_id: evolutionId,
    strategy: effectiveStrategy,
    recommendations: recommendations.slice(0, 20),
    risk_assessment: {
      level: riskLevel,
      factors: criticalPatterns.map(p => p.description).slice(0, 5),
    },
    estimated_improvement: `Health score: ${analysis.health_score} → ~${Math.min(100, analysis.health_score + (recommendations.length * 5))} (if all recommendations applied)`,
  };
}

// ─── Status: Skill 运行状态 ──────────────────────────────────

function handleStatus(): any {
  return {
    skill: 'capability-evolver',
    version: '2.0.0',
    mode: 'self-hosted',
    engine: 'pure-logic',
    supported_actions: VALID_ACTIONS,
    supported_strategies: VALID_STRATEGIES,
    upstream_dependency: 'none',
    limits: {
      max_logs_per_request: 10000,
      max_patterns_returned: 50,
      max_recommendations: 20,
    },
  };
}


// ─── Main Entry Point ────────────────────────────────────────

/**
 * Main function called by OpenClaw agent
 * @param input - Evolution request
 * @returns Analysis results or evolution proposal
 */
export async function run(input: Input): Promise<any> {
  // Merge input.input into input for compatibility
  const mergedInput = { ...input, ...(input.input || {}) };
  
  const reqValidation = validateRequest(mergedInput);
  if (!reqValidation.valid) {
    throw new Error(`Invalid request: ${reqValidation.errors.join(', ')}`);
  }

  try {
    const startTime = Date.now();
    let result: any;

    switch (mergedInput.action) {
      case 'analyze':
        result = handleAnalyze(mergedInput.logs!);
        break;
      case 'evolve':
        result = handleEvolve(mergedInput.logs!, mergedInput.strategy || 'auto', mergedInput.target_file);
        break;
      case 'status':
        result = handleStatus();
        break;
    }

    const latencyMs = Date.now() - startTime;

    return {
      action: mergedInput.action,
      ...result,
      _meta: {
        skill: 'capability-evolver',
        version: '2.0.0',
        mode: 'local',
        latency_ms: latencyMs,
        strategy: mergedInput.strategy || 'auto',
      }
    };
  } catch (error: any) {
    throw new Error(error.message || 'Processing failed');
  }
}

// Default export for compatibility
export default run;
