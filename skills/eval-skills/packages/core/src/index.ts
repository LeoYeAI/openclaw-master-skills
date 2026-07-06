// @eval-skills/core - AI Agent Skill 评测框架核心引擎

export const VERSION = "0.1.0";

// === 类型导出 ===
export type {
  JSONSchema,
  Skill,
  AdapterType,
  BenchmarkResultSummary,
  Task,
  ExpectedOutput,
  EvaluatorConfig,
  TaskResult,
  TaskStatus,
  Benchmark,
  BenchmarkMeta,
  ScoringMethod,
  BenchmarkDomain,
  SkillCompletionReport,
  ReportSummary,
  LatencyStats,
  TokenCost,
  ReportFormat,
  SelectStrategy,
  SkillAdapter,
  AdapterResponse,
  InvokeOptions,
  HealthCheckResult,
  EvalRunConfig,
  GlobalConfig,
} from "./types/index.js";

export { DEFAULT_GLOBAL_CONFIG } from "./types/index.js";

// === 遥测 ===
export { withSpan } from "./telemetry/OTelTracer.js";

// === 错误处理 ===
export { EvalSkillsError, EvalSkillsErrorCode } from "./errors.js";

// === 存储层 ===
export { SkillStore, McpRegistry } from "./registry/index.js";
export type { SkillListFilters } from "./registry/index.js";
export { BenchmarkRegistry } from "./benchmarks/index.js";
export { SqliteStore } from "./store/SqliteStore.js";

// === Adapter 层 ===
export { BaseAdapter, HttpAdapter, SubprocessAdapter, McpAdapter, AdapterRegistry } from "./adapters/index.js";
export type { HttpAdapterConfig, SubprocessAdapterConfig } from "./adapters/index.js";

// === 评分器 ===
export type { Scorer, ScorerResult } from "./evaluator/scorers/index.js";
export {
  ExactMatchScorer,
  ContainsScorer,
  JsonSchemaScorer,
  RegexScorer,
  LlmJudgeScorer,
  CustomScorer,
  ScorerFactory,
} from "./evaluator/scorers/index.js";
export type { ExactMatchOptions } from "./evaluator/scorers/index.js";
export type { ContainsOptions } from "./evaluator/scorers/index.js";
export type { LlmJudgeOptions } from "./evaluator/scorers/index.js";

// === 评测引擎 ===
export { TaskExecutor } from "./evaluator/index.js";
export type { TaskExecutorOptions, TaskItem } from "./evaluator/index.js";
export { ReportBuilder } from "./evaluator/index.js";
export { EvaluationEngine, OnDemandEvaluator } from "./evaluator/index.js";
export type { OnDemandConfig } from "./evaluator/index.js";

// === 发现 / 创建 / 筛选 ===
export { SkillFinder, EmbeddingSearcher } from "./finder/index.js";
export type { FindOptions, FindResult, EmbeddingConfig, SearchCandidate, SearchResult } from "./finder/index.js";
export { SkillCreator } from "./creator/index.js";
export type { CreateOptions, CreateResult, TemplateType } from "./creator/index.js";
export { SkillSelector } from "./selector/index.js";
export type { SelectedSkill, SelectResult } from "./selector/index.js";

// === 报告生成 ===
export { JsonReporter, MarkdownReporter, HtmlReporter, DiffReporter, CsvReporter, ReporterFactory } from "./reporters/index.js";
export type { IReporter } from "./reporters/index.js";

// === 工具 ===
export { logger } from "./utils/logger.js";

// === 运行时校验 ===
export { validateSkill, validateBenchmark, SkillSchema, BenchmarkSchema } from "./validation.js";

// === 沙箱 ===
export {
  SandboxFactory,
  ProcessSandbox,
  DockerSandbox,
  SandboxExecutor,
  SandboxMonitor,
  DEFAULT_SANDBOX_CONFIG,
  DEV_SANDBOX_CONFIG,
} from "./sandbox/index.js";
export type {
  SandboxConfig,
  ResourceLimits,
  FilesystemPolicy,
  EnvPolicy,
  DockerSandboxConfig,
  NetworkPolicy,
  NetworkAllowEntry,
  SandboxResult,
  ResourceUsageStats,
  SandboxViolation,
  ViolationType,
  JsonRpcRequest,
  ParsedCommand,
  SkillViolationStats,
  MonitorConfig,
} from "./sandbox/index.js";
