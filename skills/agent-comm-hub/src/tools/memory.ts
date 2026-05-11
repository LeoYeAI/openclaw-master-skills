/**
 * memory.ts — MCP 工具：记忆存储模块
 * 包含：store_memory, recall_memory, list_memories, delete_memory, search_memories
 * 来源：tools.ts 第 665-849 + 2253-2317 行
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import {
  storeMemory as storeMemoryFromService,
  recallMemory,
  listMemories,
  deleteMemory as deleteMemoryFromService,
} from "../memory.js";
import { auditLog, type AuthContext } from "../security.js";
import { requireAuth, mcpFail, mcpError } from "../utils.js";

export function registerMemoryTools(server: McpServer, authContext?: AuthContext): void {

  // ────────────────────────────────────────────────────
  // Tool 14: store_memory (Phase 1 Week 2)
  // 存储记忆 — member 及以上
  // ────────────────────────────────────────────────────
  server.tool(
    "store_memory",
    "存储一条记忆到 Hub。支持 private（仅自己可见）、group（组内可见）、collective（全局可见）三种范围。存储后可通过 recall_memory 全文搜索召回。",
    {
      content: z.string().describe("记忆内容（最多 10000 字符）"),
      title:   z.string().optional().describe("记忆标题（最多 500 字符）"),
      scope:   z.enum(["private", "group", "collective"]).optional()
                .default("private").describe("可见范围"),
      tags:    z.array(z.string()).optional().describe("标签列表，如 ['work', 'important']"),
      source_task_id: z.string().optional().describe("关联任务 ID（用于溯源追踪）"),
    },
    async ({ content, title, scope, tags, source_task_id }) => {
      const ctx = requireAuth(authContext, "store_memory");

      // Phase 2 Day 4: collective/group 写入自动记录 source_agent_id
      const sourceAgentId = scope === "collective" || scope === "group" ? ctx.agentId : undefined;

      const result = storeMemoryFromService(ctx.agentId, content, {
        title,
        scope,
        tags,
        source_agent_id: sourceAgentId,
        source_task_id,
      });

      if (!result.ok) {
        return mcpFail(result.error, "store_memory");
      }

      auditLog("tool_store_memory", ctx.agentId, result.memory.id,
        `scope=${scope}, source_agent=${sourceAgentId ?? "none"}, task=${source_task_id ?? "none"}, tags=${tags ? JSON.stringify(tags) : "none"}`);

      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            success:   true,
            memory_id: result.memory.id,
            scope:     result.memory.scope,
            source_agent_id: result.memory.source_agent_id,
            source_task_id:  result.memory.source_task_id,
            note:      scope === "collective"
              ? "🌐 全局记忆已存储，所有 Agent 可搜索到（已记录写入者溯源）"
              : scope === "group"
                ? "👥 组内记忆已存储，组内 Agent 可搜索到（已记录写入者溯源）"
                : "🔒 私有记忆已存储，仅自己可见",
          }, null, 2),
        }],
      };
    }
  );

  // ────────────────────────────────────────────────────
  // Tool 15: recall_memory (Phase 1 Week 2)
  // 全文搜索召回记忆 — member 及以上
  // ────────────────────────────────────────────────────
  server.tool(
    "recall_memory",
    "通过关键词全文搜索召回记忆。搜索范围包括自己的私有记忆、组内共享记忆和全局记忆。使用 FTS5 引擎，支持多关键词、短语搜索。",
    {
      query: z.string().describe("搜索关键词（如 'Agent 通信协议 错误修复'）"),
      scope: z.enum(["private", "group", "collective", "all"]).optional()
             .default("all").describe("搜索范围"),
      limit: z.number().min(1).max(50).optional().default(10)
             .describe("最大返回数量"),
    },
    async ({ query, scope, limit }) => {
      const ctx = requireAuth(authContext, "recall_memory");

      const results = recallMemory(query, ctx.agentId, { scope, limit });

      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            query,
            scope,
            results: results.map(m => ({
              id:                m.id,
              title:             m.title,
              content:           m.content,
              scope:             m.scope,
              tags:              m.tags ? JSON.parse(m.tags) : [],
              agent_id:          m.agent_id,
              source_agent_id:   m.source_agent_id,
              source_task_id:    m.source_task_id,
              source_trust_score: (m as any).source_trust_score ?? null,
              created_at:        m.created_at,
            })),
            count: results.length,
            queried_by: ctx.agentId,
          }, null, 2),
        }],
      };
    }
  );

  // ────────────────────────────────────────────────────
  // Tool 16: list_memories (Phase 1 Week 2)
  // 列出记忆 — member 及以上
  // ────────────────────────────────────────────────────
  server.tool(
    "list_memories",
    "列出可访问的记忆列表。按创建时间倒序排列。可按 scope 筛选。",
    {
      scope:  z.enum(["private", "group", "collective", "all"]).optional()
              .default("all").describe("可见范围筛选"),
      limit:  z.number().min(1).max(50).optional().default(20)
              .describe("最大返回数量"),
      offset: z.number().min(0).optional().default(0)
              .describe("分页偏移量"),
    },
    async ({ scope, limit, offset }) => {
      const ctx = requireAuth(authContext, "list_memories");

      const results = listMemories(ctx.agentId, { scope, limit, offset });

      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            memories: results.map(m => ({
              id:                m.id,
              title:             m.title,
              content:           m.content,
              scope:             m.scope,
              tags:              m.tags ? JSON.parse(m.tags) : [],
              agent_id:          m.agent_id,
              source_agent_id:   m.source_agent_id,
              source_task_id:    m.source_task_id,
              source_trust_score: (m as any).source_trust_score ?? null,
              created_at:        m.created_at,
              updated_at:        m.updated_at,
            })),
            count: results.length,
            queried_by: ctx.agentId,
          }, null, 2),
        }],
      };
    }
  );

  // ────────────────────────────────────────────────────
  // Tool 17: delete_memory (Phase 1 Week 2)
  // 删除记忆 — 仅限自己（admin 可删除任何）
  // ────────────────────────────────────────────────────
  server.tool(
    "delete_memory",
    "删除一条记忆。仅能删除自己的私有记忆（admin 可删除任何记忆）。",
    {
      memory_id: z.string().describe("要删除的记忆 ID"),
    },
    async ({ memory_id }) => {
      const ctx = requireAuth(authContext, "delete_memory");

      const result = deleteMemoryFromService(memory_id, ctx.agentId, ctx.role);

      if (!result.ok) {
        return mcpFail(result.error, "delete_memory");
      }

      auditLog("tool_delete_memory", ctx.agentId, memory_id);

      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            success:    true,
            memory_id,
            note:       "记忆已永久删除",
          }, null, 2),
        }],
      };
    }
  );

  // ────────────────────────────────────────────────────
  // Tool S2: search_memories — member 及以上
  // ────────────────────────────────────────────────────
  server.tool(
    "search_memories",
    "全文搜索记忆内容。使用 FTS5 引擎，支持多关键词、短语搜索。可按可见范围和标签筛选。",
    {
      query: z.string().describe("搜索关键词（如 '通信协议 错误修复'）"),
      scope: z.enum(["private", "group", "collective", "all"]).optional()
             .default("all").describe("可见范围筛选"),
      tags:  z.array(z.string()).optional().describe("标签筛选（如 ['work', 'important']）"),
      limit: z.number().min(1).max(50).optional().default(10).describe("最大返回数量"),
    },
    async ({ query, scope, tags, limit }) => {
      const ctx = requireAuth(authContext, "search_memories");

      try {
        // 复用已有的 recallMemory（FTS5 引擎）
        let results = recallMemory(query, ctx.agentId, { scope, limit });

        // 按 tags 过滤（recallMemory 不直接支持 tags 参数）
        if (tags && tags.length > 0) {
          results = results.filter(m => {
            if (!m.tags) return false;
            try {
              const parsedTags: string[] = JSON.parse(m.tags);
              return tags.some(t => parsedTags.includes(t));
            } catch {
              return false;
            }
          });
        }

        return {
          content: [{
            type: "text",
            text: JSON.stringify({
              query,
              scope,
              tags:  tags ?? null,
              memories: results.map(m => ({
                id:                m.id,
                title:             m.title,
                content:           m.content,
                scope:             m.scope,
                tags:              m.tags ? JSON.parse(m.tags) : [],
                agent_id:          m.agent_id,
                source_agent_id:   m.source_agent_id,
                source_task_id:    m.source_task_id,
                source_trust_score: (m as any).source_trust_score ?? null,
                created_at:        m.created_at,
              })),
              count:      results.length,
              queried_by: ctx.agentId,
            }, null, 2),
          }],
        };
      } catch (err: unknown) {
        return mcpError(err, "search_memories");
      }
    }
  );

}
