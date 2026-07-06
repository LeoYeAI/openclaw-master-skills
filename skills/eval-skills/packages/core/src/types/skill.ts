import type { JSONSchema } from "./common.js";

/**
 * Adapter 协议类型
 */
export type AdapterType = "http" | "subprocess" | "mcp";

/**
 * Benchmark 结果摘要（嵌入 Skill 元数据）
 */
export interface BenchmarkResultSummary {
  benchmarkId: string;
  completionRate: number;
  compositeScore: number;
  timestamp: string;
}

/**
 * Skill 元数据定义
 * 代表一个可独立调用的 AI 能力单元
 */
export interface Skill {
  /** 全局唯一标识，如 "web_search_v1" */
  id: string;
  /** 人类可读名称 */
  name: string;
  /** 语义版本号 */
  version: string;
  /** 描述 */
  description: string;
  /** 标签分类 */
  tags: string[];
  /** 调用参数 JSON Schema */
  inputSchema: JSONSchema;
  /** 输出结果 JSON Schema */
  outputSchema: JSONSchema;
  /** Adapter 协议类型 */
  adapterType: AdapterType;
  /** HTTP URL / 可执行文件路径 / MCP Tool ID */
  entrypoint: string;
  /** Skill 所在目录的绝对路径 (Local Skill) */
  rootPath?: string;
  /** 扩展元数据 */
  metadata: {
    author?: string;
    license?: string;
    homepage?: string;
    benchmarkResults?: BenchmarkResultSummary[];
    [key: string]: unknown; // Allow arbitrary metadata properties
  };
}
