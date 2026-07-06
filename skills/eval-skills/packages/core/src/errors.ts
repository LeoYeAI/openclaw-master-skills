/**
 * eval-skills 错误码体系
 */
export enum EvalSkillsErrorCode {
  // Skill 相关
  SKILL_NOT_FOUND = "E1001",
  SKILL_SCHEMA_INVALID = "E1002",
  SKILL_INVOKE_TIMEOUT = "E1003",
  SKILL_INVOKE_FAILED = "E1004",

  // Adapter 相关
  ADAPTER_NOT_FOUND = "E2001",
  ADAPTER_AUTH_FAILED = "E2002",
  ADAPTER_CONN_FAILED = "E2003",

  // Benchmark 相关
  BENCHMARK_NOT_FOUND = "E3001",
  BENCHMARK_SCHEMA_ERR = "E3002",

  // 评测相关
  EVAL_PARTIAL_FAIL = "E4001",
  EVAL_THRESHOLD_FAIL = "E4002",
  EVAL_NO_TASKS = "E4003",

  // 配置相关
  CONFIG_INVALID = "E5001",
  CONFIG_LLM_MISSING = "E5002",

  // 安全相关
  SECURITY_VIOLATION = "E6001",
}

/**
 * eval-skills 自定义错误类
 */
export class EvalSkillsError extends Error {
  public readonly code: EvalSkillsErrorCode;
  public readonly details?: Record<string, unknown>;

  constructor(
    code: EvalSkillsErrorCode,
    message: string,
    details?: Record<string, unknown>,
  ) {
    super(`[${code}] ${message}`);
    this.name = "EvalSkillsError";
    this.code = code;
    this.details = details;
  }

  toJSON() {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      details: this.details,
    };
  }
}
