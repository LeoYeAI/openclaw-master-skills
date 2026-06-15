/**
 * Smart PR Review — GitHub Webhook 处理器
 *
 * 接收 GitHub PR opened/synchronize 事件，解析 diff，
 * 调用 skill 执行审查，通过 GitHub API 发布 review 评论。
 *
 * 运行环境: Node.js + Hono
 * 环境变量:
 *   GITHUB_TOKEN        — GitHub API 访问令牌（需要 repo 权限）
 *   GITHUB_WEBHOOK_SECRET — Webhook 签名验证密钥
 *   PORT                — 服务端口（默认 3000）
 *   MAX_DIFF_SIZE       — 最大 diff 大小，字节（默认 500KB）
 *   REVIEW_LANGUAGE     — 输出语言 zh|en（默认 zh）
 */

import { Hono } from "hono";
import { serve } from "@hono/node-server";
import { createHmac, timingSafeEqual } from "node:crypto";

// ============================================================
// 类型定义
// ============================================================

/** GitHub Webhook PR 事件 payload */
interface PullRequestEvent {
  action: "opened" | "synchronize" | "reopened";
  number: number;
  pull_request: {
    number: number;
    title: string;
    body: string | null;
    html_url: string;
    diff_url: string;
    head: { sha: string; ref: string };
    base: { sha: string; ref: string };
    user: { login: string };
    additions: number;
    deletions: number;
    changed_files: number;
  };
  repository: {
    full_name: string;
    owner: { login: string };
    name: string;
  };
}

/** PR 文件变更信息 */
interface PullRequestFile {
  sha: string;
  filename: string;
  status: "added" | "removed" | "modified" | "renamed" | "copied" | "changed" | "unchanged";
  additions: number;
  deletions: number;
  changes: number;
  patch?: string;
}

/** Review 评论请求体 */
interface CreateReviewRequest {
  owner: string;
  repo: string;
  pull_number: number;
  body: string;
  event: "APPROVE" | "REQUEST_CHANGES" | "COMMENT";
}

/** 审查结果 */
interface ReviewResult {
  summary: string;
  verdict: "APPROVE" | "REQUEST_CHANGES" | "COMMENT";
  body: string;
}

/** Diff 分片 */
interface DiffChunk {
  files: PullRequestFile[];
  totalSize: number;
  chunkIndex: number;
  totalChunks: number;
}

// ============================================================
// 配置
// ============================================================

const CONFIG = {
  githubToken: process.env.GITHUB_TOKEN ?? "",
  webhookSecret: process.env.GITHUB_WEBHOOK_SECRET ?? "",
  port: parseInt(process.env.PORT ?? "3000", 10),
  maxDiffSize: parseInt(process.env.MAX_DIFF_SIZE ?? "512000", 10), // 500KB
  reviewLanguage: (process.env.REVIEW_LANGUAGE ?? "zh") as "zh" | "en",
  githubApiBase: "https://api.github.com",
  maxRetries: 3,
  retryDelayMs: 1000,
} as const;

// ============================================================
// GitHub API 客户端
// ============================================================

class GitHubClient {
  private token: string;
  private baseUrl: string;

  constructor(token: string, baseUrl: string = CONFIG.githubApiBase) {
    this.token = token;
    this.baseUrl = baseUrl;
  }

  /** 发送 GitHub API 请求，带重试 */
  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
    retries: number = CONFIG.maxRetries
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const headers: Record<string, string> = {
      Authorization: `Bearer ${this.token}`,
      Accept: "application/vnd.github.v3+json",
      "Content-Type": "application/json",
      "X-GitHub-Api-Version": "2022-11-28",
    };

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const response = await fetch(url, {
          method,
          headers,
          body: body ? JSON.stringify(body) : undefined,
        });

        // 速率限制处理
        if (response.status === 403) {
          const rateLimitRemaining = response.headers.get("x-ratelimit-remaining");
          if (rateLimitRemaining === "0") {
            const resetTime = parseInt(response.headers.get("x-ratelimit-reset") ?? "0", 10);
            const waitMs = Math.max(0, resetTime * 1000 - Date.now()) + 1000;
            console.warn(`[GitHub API] 速率限制，等待 ${waitMs}ms`);
            await this.sleep(Math.min(waitMs, 60000));
            continue;
          }
        }

        if (!response.ok) {
          const errorBody = await response.text();
          throw new Error(
            `GitHub API ${method} ${path} 返回 ${response.status}: ${errorBody}`
          );
        }

        return (await response.json()) as T;
      } catch (error) {
        if (attempt === retries) throw error;
        const delay = CONFIG.retryDelayMs * Math.pow(2, attempt - 1);
        console.warn(
          `[GitHub API] 请求失败 (${attempt}/${retries})，${delay}ms 后重试:`,
          error instanceof Error ? error.message : error
        );
        await this.sleep(delay);
      }
    }

    throw new Error("不可达: 重试循环异常退出");
  }

  /** 获取 PR 变更文件列表（自动分页） */
  async getPullRequestFiles(
    owner: string,
    repo: string,
    pullNumber: number
  ): Promise<PullRequestFile[]> {
    const allFiles: PullRequestFile[] = [];
    let page = 1;
    const perPage = 100;

    while (true) {
      const files = await this.request<PullRequestFile[]>(
        "GET",
        `/repos/${owner}/${repo}/pulls/${pullNumber}/files?per_page=${perPage}&page=${page}`
      );
      allFiles.push(...files);
      if (files.length < perPage) break;
      page++;
    }

    return allFiles;
  }

  /** 获取 PR 原始 diff */
  async getPullRequestDiff(
    owner: string,
    repo: string,
    pullNumber: number
  ): Promise<string> {
    const url = `${this.baseUrl}/repos/${owner}/${repo}/pulls/${pullNumber}`;
    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${this.token}`,
        Accept: "application/vnd.github.v3.diff",
        "X-GitHub-Api-Version": "2022-11-28",
      },
    });

    if (!response.ok) {
      throw new Error(`获取 PR diff 失败: ${response.status}`);
    }

    return response.text();
  }

  /** 提交 PR review */
  async createReview(params: CreateReviewRequest): Promise<void> {
    await this.request(
      "POST",
      `/repos/${params.owner}/${params.repo}/pulls/${params.pull_number}/reviews`,
      {
        body: params.body,
        event: params.event,
      }
    );
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// ============================================================
// Webhook 签名验证
// ============================================================

/** 验证 GitHub webhook 请求签名 */
function verifyWebhookSignature(
  payload: string,
  signature: string | null,
  secret: string
): boolean {
  if (!signature || !secret) return false;

  const expectedPrefix = "sha256=";
  if (!signature.startsWith(expectedPrefix)) return false;

  const sig = signature.slice(expectedPrefix.length);
  const hmac = createHmac("sha256", secret);
  hmac.update(payload, "utf8");
  const digest = hmac.digest("hex");

  // 使用 timingSafeEqual 防止时序攻击
  try {
    return timingSafeEqual(
      Buffer.from(sig, "hex"),
      Buffer.from(digest, "hex")
    );
  } catch {
    return false;
  }
}

// ============================================================
// Diff 分片器
// ============================================================

/**
 * 将大 PR 的文件列表分片，确保每片 patch 总大小不超过阈值。
 * 分片策略：按文件粒度切割，单个文件超大时独占一片。
 */
function chunkDiffFiles(
  files: PullRequestFile[],
  maxChunkSize: number = CONFIG.maxDiffSize
): DiffChunk[] {
  if (files.length === 0) return [];

  const chunks: DiffChunk[] = [];
  let currentFiles: PullRequestFile[] = [];
  let currentSize = 0;

  for (const file of files) {
    const patchSize = file.patch ? Buffer.byteLength(file.patch, "utf8") : 0;

    // 单个文件就超过阈值，独占一片
    if (patchSize > maxChunkSize) {
      // 先把当前积累的文件打包
      if (currentFiles.length > 0) {
        chunks.push({
          files: currentFiles,
          totalSize: currentSize,
          chunkIndex: chunks.length,
          totalChunks: 0, // 最后回填
        });
        currentFiles = [];
        currentSize = 0;
      }
      chunks.push({
        files: [file],
        totalSize: patchSize,
        chunkIndex: chunks.length,
        totalChunks: 0,
      });
      continue;
    }

    // 加入当前文件后超过阈值，先打包当前组
    if (currentSize + patchSize > maxChunkSize && currentFiles.length > 0) {
      chunks.push({
        files: currentFiles,
        totalSize: currentSize,
        chunkIndex: chunks.length,
        totalChunks: 0,
      });
      currentFiles = [];
      currentSize = 0;
    }

    currentFiles.push(file);
    currentSize += patchSize;
  }

  // 最后一组
  if (currentFiles.length > 0) {
    chunks.push({
      files: currentFiles,
      totalSize: currentSize,
      chunkIndex: chunks.length,
      totalChunks: 0,
    });
  }

  // 回填 totalChunks
  for (const chunk of chunks) {
    chunk.totalChunks = chunks.length;
  }

  return chunks;
}

// ============================================================
// 审查 Prompt 构建
// ============================================================

/** 构建发送给 AI 的审查 prompt */
function buildReviewPrompt(
  prTitle: string,
  prBody: string | null,
  diff: string,
  chunkInfo?: { index: number; total: number },
  options: { focus?: string; strict?: boolean; lang?: string } = {}
): string {
  const lang = options.lang ?? CONFIG.reviewLanguage;
  const langInstruction = lang === "en"
    ? "Output the review in English."
    : "用中文输出审查结果。";

  const focusInstruction = options.focus && options.focus !== "all"
    ? `\n**聚焦维度**: 重点审查 ${options.focus} 相关问题，其他维度快速扫描。`
    : "";

  const strictInstruction = options.strict
    ? "\n**严格模式**: 已启用。缺少测试 → MUST FIX，any 类型 → SHOULD FIX，缺少错误处理 → MUST FIX。"
    : "";

  const chunkNote = chunkInfo
    ? `\n> 注意: 这是大 PR 的第 ${chunkInfo.index + 1}/${chunkInfo.total} 片审查。请只审查当前片段的代码。`
    : "";

  return `
你是一个有立场的资深 Code Reviewer。请按照 Smart PR Review 标准审查以下变更。
${langInstruction}${focusInstruction}${strictInstruction}${chunkNote}

## PR 信息
- **标题**: ${prTitle}
- **描述**: ${prBody ?? "(无描述)"}

## 变更内容 (Diff)
\`\`\`diff
${diff}
\`\`\`

## 审查要求
1. 按六层审查维度逐一检查
2. 执行 Devil's Advocate 思考
3. 用标准格式输出（MUST FIX / SHOULD FIX / SUGGESTION / What's Good / Verdict）
4. 引用具体行号和代码片段
5. 对 MUST FIX 问题必须给出替代方案代码
6. 不做橡皮图章 — 有问题就直说
`.trim();
}

// ============================================================
// Webhook 处理器
// ============================================================

/** 处理 PR webhook 事件的核心逻辑 */
async function handlePullRequestEvent(
  event: PullRequestEvent,
  github: GitHubClient
): Promise<void> {
  const { pull_request: pr, repository } = event;
  const owner = repository.owner.login;
  const repo = repository.name;
  const prNumber = pr.number;

  console.log(
    `[Review] 开始审查 PR #${prNumber}: ${pr.title} (${owner}/${repo})`
  );
  console.log(
    `[Review] 变更统计: +${pr.additions} -${pr.deletions}, ${pr.changed_files} 文件`
  );

  // 获取 PR 文件列表和 diff
  const [files, diff] = await Promise.all([
    github.getPullRequestFiles(owner, repo, prNumber),
    github.getPullRequestDiff(owner, repo, prNumber),
  ]);

  // 过滤二进制和生成文件
  const reviewableFiles = files.filter((f) => {
    const ignoredExtensions = [
      ".lock", ".sum", ".min.js", ".min.css",
      ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
      ".woff", ".woff2", ".ttf", ".eot",
      ".map", ".snap",
    ];
    const ignoredPaths = [
      "node_modules/", "vendor/", "dist/", "build/",
      ".next/", "__pycache__/", ".git/",
      "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
      "go.sum", "Cargo.lock", "Gemfile.lock", "poetry.lock",
    ];
    return (
      !ignoredExtensions.some((ext) => f.filename.endsWith(ext)) &&
      !ignoredPaths.some((p) => f.filename.includes(p))
    );
  });

  if (reviewableFiles.length === 0) {
    console.log("[Review] 无可审查的文件，跳过");
    return;
  }

  // 分片处理大 PR
  const chunks = chunkDiffFiles(reviewableFiles);
  console.log(
    `[Review] ${reviewableFiles.length} 个可审查文件，分为 ${chunks.length} 片`
  );

  // 为每个分片构建 prompt（实际调用 AI 审查需要集成具体的 AI 服务）
  const reviewPrompts = chunks.map((chunk, index) => {
    const chunkDiff = chunk.files
      .map((f) => f.patch ?? "")
      .filter(Boolean)
      .join("\n\n");

    return buildReviewPrompt(
      pr.title,
      pr.body,
      chunkDiff,
      chunks.length > 1 ? { index, total: chunks.length } : undefined
    );
  });

  // 合并审查结果
  // 注意: 此处需要接入实际的 AI 服务来执行审查
  // 以下为框架代码，展示如何将审查结果发布到 GitHub
  const reviewResult = await executeReview(reviewPrompts);

  // 发布审查评论到 GitHub
  await github.createReview({
    owner,
    repo,
    pull_number: prNumber,
    body: reviewResult.body,
    event: reviewResult.verdict,
  });

  console.log(
    `[Review] PR #${prNumber} 审查完成，verdict: ${reviewResult.verdict}`
  );
}

/**
 * 执行 AI 审查
 *
 * 支持两种模式（通过 REVIEW_PROVIDER 环境变量切换）：
 * - "anthropic"（默认）: 调用 Anthropic Messages API
 * - "openclaw": 通过 OpenClaw SDK 调用 skill（需要额外配置）
 *
 * 环境变量:
 *   ANTHROPIC_API_KEY   — Anthropic API 密钥
 *   REVIEW_MODEL        — 模型 ID（默认 claude-sonnet-4-20250514）
 *   REVIEW_PROVIDER     — "anthropic" | "openclaw"（默认 anthropic）
 *   REVIEW_MAX_TOKENS   — 单次审查最大 token（默认 4096）
 */
async function executeReview(prompts: string[]): Promise<ReviewResult> {
  const provider = process.env.REVIEW_PROVIDER ?? "anthropic";

  if (provider === "anthropic") {
    return executeReviewWithAnthropic(prompts);
  }

  // OpenClaw 或其他 provider 的集成入口
  console.warn(`[Review] 不支持的 provider: ${provider}，回退到 anthropic`);
  return executeReviewWithAnthropic(prompts);
}

/**
 * 使用 Anthropic Messages API 执行审查
 * 直接调用 REST API，无需额外 SDK 依赖
 */
async function executeReviewWithAnthropic(prompts: string[]): Promise<ReviewResult> {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    console.error("[Review] ANTHROPIC_API_KEY 未设置");
    return {
      summary: "审查服务未配置",
      verdict: "COMMENT",
      body: "⚠️ Smart PR Review: ANTHROPIC_API_KEY 环境变量未设置，无法执行 AI 审查。请参考部署文档配置 API 密钥。",
    };
  }

  const model = process.env.REVIEW_MODEL ?? "claude-sonnet-4-20250514";
  const maxTokens = parseInt(process.env.REVIEW_MAX_TOKENS ?? "4096", 10);

  // 逐片审查（串行执行，避免速率限制）
  const chunkResults: string[] = [];

  for (let i = 0; i < prompts.length; i++) {
    const prompt = prompts[i];
    console.log(`[Review] 执行审查片段 ${i + 1}/${prompts.length}...`);

    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": apiKey,
          "anthropic-version": "2023-06-01",
        },
        body: JSON.stringify({
          model,
          max_tokens: maxTokens,
          messages: [{ role: "user", content: prompt }],
        }),
      });

      if (!response.ok) {
        const errorBody = await response.text();
        console.error(`[Review] Anthropic API 返回 ${response.status}: ${errorBody}`);
        chunkResults.push(`> ⚠️ 片段 ${i + 1} 审查失败: API 返回 ${response.status}`);
        continue;
      }

      const data = (await response.json()) as {
        content: Array<{ type: string; text?: string }>;
      };

      const text = data.content
        .filter((block) => block.type === "text" && block.text)
        .map((block) => block.text!)
        .join("\n");

      chunkResults.push(text);
    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
      console.error(`[Review] 片段 ${i + 1} 审查异常:`, msg);
      chunkResults.push(`> ⚠️ 片段 ${i + 1} 审查异常: ${msg}`);
    }
  }

  // 合并多片审查结果
  const mergedBody = prompts.length === 1
    ? chunkResults[0]
    : chunkResults.map((r, i) => `<!-- chunk ${i + 1} -->\n${r}`).join("\n\n---\n\n");

  // 从审查内容中提取 verdict
  const verdict = extractVerdict(mergedBody);

  return {
    summary: `AI 审查完成（${prompts.length} 片）`,
    verdict,
    body: mergedBody,
  };
}

/** 从审查输出中提取 verdict */
function extractVerdict(reviewBody: string): "APPROVE" | "REQUEST_CHANGES" | "COMMENT" {
  // 检查是否有 MUST FIX（意味着 REQUEST_CHANGES）
  const mustFixMatch = reviewBody.match(/MUST FIX \((\d+)/);
  if (mustFixMatch && parseInt(mustFixMatch[1], 10) > 0) {
    return "REQUEST_CHANGES";
  }

  // 检查 verdict 部分的标记
  if (/\[x\]\s*REQUEST.?CHANGES/i.test(reviewBody)) {
    return "REQUEST_CHANGES";
  }
  if (/\[x\]\s*APPROVE/i.test(reviewBody)) {
    return "APPROVE";
  }

  return "COMMENT";
}

// ============================================================
// Hono 应用
// ============================================================

const app = new Hono();

/** 健康检查 */
app.get("/health", (c) => {
  return c.json({ status: "ok", service: "smart-pr-review" });
});

/** GitHub Webhook 端点 */
app.post("/webhook/github", async (c) => {
  // 读取原始 body 用于签名验证
  const rawBody = await c.req.text();

  // 验证 webhook 签名
  const signature = c.req.header("x-hub-signature-256");
  if (CONFIG.webhookSecret) {
    if (!verifyWebhookSignature(rawBody, signature ?? null, CONFIG.webhookSecret)) {
      console.error("[Webhook] 签名验证失败");
      return c.json({ error: "签名验证失败" }, 401);
    }
  }

  // 检查事件类型
  const eventType = c.req.header("x-github-event");
  if (eventType !== "pull_request") {
    return c.json({ message: `忽略事件类型: ${eventType}` }, 200);
  }

  // 解析 payload
  let payload: PullRequestEvent;
  try {
    payload = JSON.parse(rawBody) as PullRequestEvent;
  } catch {
    return c.json({ error: "无效的 JSON payload" }, 400);
  }

  // 只处理 opened / synchronize / reopened 事件
  const supportedActions = ["opened", "synchronize", "reopened"];
  if (!supportedActions.includes(payload.action)) {
    return c.json({ message: `忽略 action: ${payload.action}` }, 200);
  }

  // 异步处理审查，立即返回 202
  const github = new GitHubClient(CONFIG.githubToken);

  // 不阻塞 webhook 响应
  handlePullRequestEvent(payload, github).catch((error) => {
    console.error("[Webhook] 审查处理失败:", error);
  });

  return c.json(
    {
      message: "审查已触发",
      pr: payload.pull_request.number,
      repo: payload.repository.full_name,
    },
    202
  );
});

// ============================================================
// 启动服务
// ============================================================

if (CONFIG.githubToken === "") {
  console.warn("⚠️  GITHUB_TOKEN 未设置，API 调用将失败");
}
if (CONFIG.webhookSecret === "") {
  console.warn("⚠️  GITHUB_WEBHOOK_SECRET 未设置，webhook 签名验证已禁用");
}

serve({ fetch: app.fetch, port: CONFIG.port }, (info) => {
  console.log(`🔍 Smart PR Review webhook 已启动: http://localhost:${info.port}`);
  console.log(`   健康检查: http://localhost:${info.port}/health`);
  console.log(`   Webhook:  http://localhost:${info.port}/webhook/github`);
});

// 导出供测试使用
export {
  app,
  verifyWebhookSignature,
  chunkDiffFiles,
  buildReviewPrompt,
  GitHubClient,
};
export type {
  PullRequestEvent,
  PullRequestFile,
  CreateReviewRequest,
  ReviewResult,
  DiffChunk,
};
