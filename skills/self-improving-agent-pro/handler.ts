/**
 * Self-Improving Agent - OpenClaw Local Skill
 * 
 * This is a LOCAL skill that runs inside the OpenClaw agent.
 * It processes learning events locally without external API calls.
 * 
 * Use when: (1) A command fails, (2) User corrects output, (3) New pattern discovered
 */

// ─── Types ───────────────────────────────────────────────────

type EventType = 'error' | 'correction' | 'learning' | 'pattern';
type Severity = 'low' | 'medium' | 'high' | 'critical';

interface LearningEvent {
  type: EventType;
  context: string;
  detail: string;
  severity?: Severity;
  tags?: string[];
  previous_attempt?: string;
  corrected_output?: string;
}

interface ProcessedEntry {
  id: string;
  timestamp: string;
  type: EventType;
  severity: Severity;
  context: string;
  detail: string;
  tags: string[];
  actionable_insight: string;
  suggested_rule: string | null;
  previous_attempt: string | null;
  corrected_output: string | null;
}

interface BatchSummary {
  total: number;
  by_type: Record<string, number>;
  by_severity: Record<string, number>;
  top_tags: Array<{ tag: string; count: number }>;
  patterns_detected: string[];
  recommendations: string[];
}

// ─── Core Logic ──────────────────────────────────────────────

const VALID_TYPES: EventType[] = ['error', 'correction', 'learning', 'pattern'];
const VALID_SEVERITIES: Severity[] = ['low', 'medium', 'high', 'critical'];

function generateId(): string {
  return `sia_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

function inferSeverity(event: LearningEvent): Severity {
  if (event.severity && VALID_SEVERITIES.includes(event.severity)) return event.severity;
  const text = `${event.context} ${event.detail}`.toLowerCase();
  if (text.includes('crash') || text.includes('data loss') || text.includes('security')) return 'critical';
  if (text.includes('fail') || text.includes('error') || text.includes('broken')) return 'high';
  if (text.includes('wrong') || text.includes('incorrect') || text.includes('unexpected')) return 'medium';
  return 'low';
}

function extractTags(event: LearningEvent): string[] {
  const tags = new Set<string>(event.tags || []);
  const text = `${event.context} ${event.detail}`.toLowerCase();
  const autoTags: Record<string, string[]> = {
    'api': ['api', 'endpoint', 'rest', 'http', 'fetch'],
    'auth': ['auth', 'token', 'permission', 'unauthorized', 'forbidden'],
    'parsing': ['parse', 'json', 'xml', 'format', 'schema'],
    'timeout': ['timeout', 'slow', 'latency', 'deadline'],
    'config': ['config', 'env', 'setting', 'variable'],
    'logic': ['logic', 'condition', 'branch', 'loop', 'algorithm'],
    'io': ['file', 'disk', 'read', 'write', 'path'],
    'network': ['network', 'connection', 'dns', 'socket'],
  };
  for (const [tag, keywords] of Object.entries(autoTags)) {
    if (keywords.some(k => text.includes(k))) tags.add(tag);
  }
  tags.add(event.type);
  return Array.from(tags);
}

function generateInsight(event: LearningEvent): string {
  switch (event.type) {
    case 'error':
      return `Error detected in "${event.context}": ${event.detail}. Consider adding error handling or input validation for this scenario.`;
    case 'correction':
      return event.previous_attempt
        ? `Output was corrected from "${truncate(event.previous_attempt, 80)}" to "${truncate(event.corrected_output || event.detail, 80)}". Update the approach for "${event.context}" to match the corrected behavior.`
        : `Correction applied in "${event.context}": ${event.detail}. Incorporate this feedback into future responses.`;
    case 'learning':
      return `New learning captured for "${event.context}": ${event.detail}. This should be applied to similar future tasks.`;
    case 'pattern':
      return `Recurring pattern identified in "${event.context}": ${event.detail}. Consider creating a reusable rule or template.`;
    default:
      return `Event in "${event.context}": ${event.detail}.`;
  }
}

function generateRule(event: LearningEvent): string | null {
  if (event.type === 'correction' && event.previous_attempt && event.corrected_output) {
    return `WHEN context matches "${truncate(event.context, 60)}" AND output resembles "${truncate(event.previous_attempt, 60)}" THEN prefer "${truncate(event.corrected_output, 60)}"`;
  }
  if (event.type === 'pattern') {
    return `WHEN context matches "${truncate(event.context, 60)}" THEN apply: ${truncate(event.detail, 100)}`;
  }
  if (event.type === 'error') {
    return `WHEN operating in "${truncate(event.context, 60)}" THEN guard against: ${truncate(event.detail, 100)}`;
  }
  return null;
}

function truncate(s: string, max: number): string {
  return s.length > max ? s.slice(0, max - 3) + '...' : s;
}

function processEvent(event: LearningEvent): ProcessedEntry {
  return {
    id: generateId(),
    timestamp: new Date().toISOString(),
    type: event.type,
    severity: inferSeverity(event),
    context: event.context,
    detail: event.detail,
    tags: extractTags(event),
    actionable_insight: generateInsight(event),
    suggested_rule: generateRule(event),
    previous_attempt: event.previous_attempt || null,
    corrected_output: event.corrected_output || null,
  };
}

function buildSummary(entries: ProcessedEntry[]): BatchSummary {
  const byType: Record<string, number> = {};
  const bySeverity: Record<string, number> = {};
  const tagCounts: Record<string, number> = {};

  for (const e of entries) {
    byType[e.type] = (byType[e.type] || 0) + 1;
    bySeverity[e.severity] = (bySeverity[e.severity] || 0) + 1;
    for (const t of e.tags) {
      tagCounts[t] = (tagCounts[t] || 0) + 1;
    }
  }

  const contextCounts: Record<string, number> = {};
  for (const e of entries) {
    contextCounts[e.context] = (contextCounts[e.context] || 0) + 1;
  }
  const patterns = Object.entries(contextCounts)
    .filter(([, count]) => count >= 2)
    .map(([ctx, count]) => `"${ctx}" appeared ${count} times — likely a recurring issue`);

  const recommendations: string[] = [];
  if ((bySeverity['critical'] || 0) > 0) {
    recommendations.push('Critical issues detected — prioritize immediate fixes');
  }
  if ((bySeverity['high'] || 0) >= 2) {
    recommendations.push('Multiple high-severity events — consider a systematic review');
  }
  if (entries.filter(e => e.type === 'correction').length >= 2) {
    recommendations.push('Multiple corrections recorded — update base prompts or rules to prevent recurrence');
  }
  if (patterns.length > 0) {
    recommendations.push('Recurring contexts detected — create dedicated handling rules');
  }
  if (entries.some(e => e.suggested_rule)) {
    recommendations.push('Suggested rules generated — review and add to agent configuration');
  }

  const topTags = Object.entries(tagCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([tag, count]) => ({ tag, count }));

  return {
    total: entries.length,
    by_type: byType,
    by_severity: bySeverity,
    top_tags: topTags,
    patterns_detected: patterns,
    recommendations,
  };
}

// ─── Main Entry Point (OpenClaw compatible) ──────────────────

/**
 * Main function called by OpenClaw agent
 * @param input - Single event or batch of events
 * @returns Processed entries with insights and rules
 */
export async function run(input: LearningEvent | { events: LearningEvent[] }): Promise<{
  entries: ProcessedEntry[];
  summary: BatchSummary | null;
}> {
  // Support single event or batch
  const events: LearningEvent[] = 'events' in input && Array.isArray(input.events)
    ? input.events
    : [input as LearningEvent];

  if (events.length === 0) {
    throw new Error('Invalid input: provide either a single event {type, context, detail} or {events: [...]}');
  }

  // Validate each event
  for (let i = 0; i < events.length; i++) {
    const e = events[i];
    if (!e.type || !VALID_TYPES.includes(e.type)) {
      throw new Error(`Event ${i}: invalid type "${e.type}". Must be one of: ${VALID_TYPES.join(', ')}`);
    }
    if (!e.context || typeof e.context !== 'string') {
      throw new Error(`Event ${i}: "context" is required and must be a string`);
    }
    if (!e.detail || typeof e.detail !== 'string') {
      throw new Error(`Event ${i}: "detail" is required and must be a string`);
    }
  }

  // Process
  const entries = events.map(processEvent);
  const summary = entries.length > 1 ? buildSummary(entries) : null;

  return { entries, summary };
}

// Default export for compatibility
export default run;
