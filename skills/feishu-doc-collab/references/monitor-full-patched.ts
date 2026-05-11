import type { ClawdbotConfig, RuntimeEnv, HistoryEntry } from "openclaw/plugin-sdk";
import * as Lark from "@larksuiteoapi/node-sdk";
import * as http from "http";
import type { ResolvedFeishuAccount } from "./types.js";
import { resolveFeishuAccount, listEnabledFeishuAccounts } from "./accounts.js";
import { handleFeishuMessage, type FeishuMessageEvent, type FeishuBotAddedEvent } from "./bot.js";
import { createFeishuWSClient, createEventDispatcher } from "./client.js";
import { probeFeishu } from "./probe.js";
import { getFeishuRuntime } from "./runtime.js";

export type MonitorFeishuOpts = {
  config?: ClawdbotConfig;
  runtime?: RuntimeEnv;
  abortSignal?: AbortSignal;
  accountId?: string;
};

// Per-account WebSocket clients, HTTP servers, and bot info
const wsClients = new Map<string, Lark.WSClient>();
const httpServers = new Map<string, http.Server>();
const botOpenIds = new Map<string, string>();

// [feishu-doc-collab] Debounce map: fileToken → last trigger timestamp (ms)
// Prevents rapid-fire hook triggers when a single edit causes multiple events
const _editDebounce = new Map<string, number>();
const EDIT_DEBOUNCE_MS = 30_000; // 30 seconds between triggers for the same file

async function fetchBotOpenId(account: ResolvedFeishuAccount): Promise<string | undefined> {
  try {
    const result = await probeFeishu(account);
    return result.ok ? result.botOpenId : undefined;
  } catch {
    return undefined;
  }
}

/**
 * Register common event handlers on an EventDispatcher.
 * When fireAndForget is true (webhook mode), message handling is not awaited
 * to avoid blocking the HTTP response (Lark requires <3s response).
 */
function registerEventHandlers(
  eventDispatcher: Lark.EventDispatcher,
  context: {
    cfg: ClawdbotConfig;
    accountId: string;
    runtime?: RuntimeEnv;
    chatHistories: Map<string, HistoryEntry[]>;
    fireAndForget?: boolean;
  },
) {
  const { cfg, accountId, runtime, chatHistories, fireAndForget } = context;
  const log = runtime?.log ?? console.log;
  const error = runtime?.error ?? console.error;

  eventDispatcher.register({
    "im.message.receive_v1": async (data) => {
      try {
        const event = data as unknown as FeishuMessageEvent;
        const promise = handleFeishuMessage({
          cfg,
          event,
          botOpenId: botOpenIds.get(accountId),
          runtime,
          chatHistories,
          accountId,
        });
        if (fireAndForget) {
          promise.catch((err) => {
            error(`feishu[${accountId}]: error handling message: ${String(err)}`);
          });
        } else {
          await promise;
        }
      } catch (err) {
        error(`feishu[${accountId}]: error handling message: ${String(err)}`);
      }
    },
    "im.message.message_read_v1": async () => {
      // Ignore read receipts
    },
    "im.chat.member.bot.added_v1": async (data) => {
      try {
        const event = data as unknown as FeishuBotAddedEvent;
        log(`feishu[${accountId}]: bot added to chat ${event.chat_id}`);
      } catch (err) {
        error(`feishu[${accountId}]: error handling bot added event: ${String(err)}`);
      }
    },
    "im.chat.member.bot.deleted_v1": async (data) => {
      try {
        const event = data as unknown as { chat_id: string };
        log(`feishu[${accountId}]: bot removed from chat ${event.chat_id}`);
      } catch (err) {
        error(`feishu[${accountId}]: error handling bot removed event: ${String(err)}`);
      }
    },
    "drive.file.edit_v1": async (data) => {
      try {
        const fs = await import("fs");
        fs.appendFileSync("/tmp/feishu-events.log", `${new Date().toISOString()} drive.file.edit_v1 handler triggered! data=${JSON.stringify(data).slice(0,500)}\n`);
        const event = data as unknown as {
          file_token?: string;
          file_type?: string;
          operator_id?: { open_id?: string; union_id?: string; user_id?: string };
        };
        const fileToken = event.file_token ?? "unknown";
        const fileType = event.file_type ?? "unknown";
        const operatorId = event.operator_id?.open_id ?? event.operator_id?.user_id ?? "unknown";

        log(`feishu[${accountId}]: drive.file.edit event: file=${fileToken}, type=${fileType}, operator=${operatorId}`);

        // Skip edits made by our own bot to avoid loops
        const myBotOpenId = botOpenIds.get(accountId);
        if (myBotOpenId && operatorId === myBotOpenId) {
          log(`feishu[${accountId}]: skipping own edit on file ${fileToken}`);
          return;
        }

        // [feishu-doc-collab] Debounce: skip if same file was triggered within EDIT_DEBOUNCE_MS
        const now = Date.now();
        const lastTrigger = _editDebounce.get(fileToken);
        if (lastTrigger && (now - lastTrigger) < EDIT_DEBOUNCE_MS) {
          log(`feishu[${accountId}]: debounce skip edit on ${fileToken} (${now - lastTrigger}ms since last trigger)`);
          return;
        }
        _editDebounce.set(fileToken, now);

        // Inject as system event into main session so the agent can react
        try {
          const core = getFeishuRuntime();
          const eventText = `[Document Edit Event] Feishu document ${fileToken} was edited. (processed via /hooks/agent isolated session)`;
          core.system.enqueueSystemEvent(eventText, {
            sessionKey: `agent:main:main`,
            contextKey: `feishu:drive:edit:${fileToken}:${Date.now()}`,
          });
          log(`feishu[${accountId}]: injected drive.file.edit system event for file ${fileToken}`);
          
          // Trigger isolated agent turn via /hooks/agent endpoint
          try {
            const fs2 = await import("fs");
            const cfgRaw = fs2.readFileSync(`${process.env.HOME || "/root"}/.openclaw/openclaw.json`, "utf-8");
            const cfgJson = JSON.parse(cfgRaw);
            const hooksToken = cfgJson?.hooks?.token;
            const port = cfgJson?.gateway?.port ?? 18789;
            if (hooksToken) {
              const agentMessage = `[Document Edit Event] Feishu document (token: ${fileToken}, type: ${fileType}) was edited.

INSTRUCTIONS — follow exactly:
1. Read DOC_PROTOCOL.md from workspace for the message format specification.
2. Read the document: feishu_doc(action=read, doc_token=${fileToken})
3. Find the LAST message block (delimited by ---). Parse its header line: sender, receiver, status.
4. Decision logic:
   - If status is 🔴 (editing) or missing → do NOTHING, reply NO_REPLY
   - If sender is yourself (妙妙) → do NOTHING, reply NO_REPLY  
   - If receiver is not your name (妙妙) and not "all" → do NOTHING, reply NO_REPLY
   - If status is 🟢 (complete) AND receiver is you or "all" → process the message
5. If processing: compose your reply in the protocol format and append it:
   feishu_doc(action=append, doc_token=${fileToken}, content="---\\n> **妙妙** → **{sender}** | 🟢 完成\\n\\n{your reply}\\n")
6. If not processing: reply NO_REPLY`;
              const resp = await fetch(`http://127.0.0.1:${port}/hooks/agent`, {
                method: "POST",
                headers: { "Content-Type": "application/json", "Authorization": `Bearer ${hooksToken}` },
                body: JSON.stringify({ message: agentMessage }),
              });
              if (resp.ok) {
                log(`feishu[${accountId}]: triggered /hooks/agent for doc edit on ${fileToken}`);
              } else {
                const body = await resp.text().catch(() => "");
                log(`feishu[${accountId}]: /hooks/agent returned ${resp.status}: ${body.slice(0,200)}`);
              }
            } else {
              log(`feishu[${accountId}]: hooks.token not configured, cannot trigger agent`);
            }
          } catch (wakeErr) {
            log(`feishu[${accountId}]: agent trigger failed (non-fatal): ${String(wakeErr)}`);
          }
        } catch (err) {
          error(`feishu[${accountId}]: failed to inject drive.file.edit system event: ${String(err)}`);
        }
      } catch (err) {
        error(`feishu[${accountId}]: error handling drive.file.edit event: ${String(err)}`);
      }
    },
    "drive.file.bitable_record_changed_v1": async (data) => {
      try {
        const fs = await import("fs");
        fs.appendFileSync("/tmp/feishu-events.log", `${new Date().toISOString()} drive.file.bitable_record_changed_v1 data=${JSON.stringify(data).slice(0,800)}\n`);
        const event = data as unknown as {
          file_token?: string;
          table_id?: string;
          operator_id?: { open_id?: string; union_id?: string; user_id?: string };
          action_list?: Array<{
            record_id: string;
            action: string;
            before_value?: Array<{ field_id: string; field_value: string }>;
            after_value?: Array<{ field_id: string; field_value: string }>;
          }>;
        };
        const fileToken = event.file_token ?? "unknown";
        const tableId = event.table_id ?? "unknown";
        const operatorId = event.operator_id?.open_id ?? "unknown";

        log(`feishu[${accountId}]: bitable record changed: file=${fileToken}, table=${tableId}, operator=${operatorId}`);

        // Skip changes made by our own bot
        const myBotOpenId = botOpenIds.get(accountId);
        if (myBotOpenId && operatorId === myBotOpenId) {
          log(`feishu[${accountId}]: skipping own bitable record change on ${fileToken}`);
          return;
        }

        // [feishu-doc-collab] Debounce: skip if same file was triggered within EDIT_DEBOUNCE_MS
        {
          const now = Date.now();
          const debounceKey = `bitable:${fileToken}:${tableId}`;
          const lastTrigger = _editDebounce.get(debounceKey);
          if (lastTrigger && (now - lastTrigger) < EDIT_DEBOUNCE_MS) {
            log(`feishu[${accountId}]: debounce skip bitable change on ${fileToken} (${now - lastTrigger}ms since last trigger)`);
            return;
          }
          _editDebounce.set(debounceKey, now);
        }

        // Trigger isolated agent turn via /hooks/agent
        try {
          const fs2 = await import("fs");
          const cfgRaw = fs2.readFileSync(`${process.env.HOME || "/root"}/.openclaw/openclaw.json`, "utf-8");
          const cfgJson = JSON.parse(cfgRaw);
          const hooksToken = cfgJson?.hooks?.token;
          const port = cfgJson?.gateway?.port ?? 18789;
          if (hooksToken) {
            const actionSummary = (event.action_list ?? []).map(a => `record=${a.record_id} action=${a.action}`).join("; ");
            const agentMessage = `[Bitable Record Changed] 多维表格记录变更事件:
- app_token: ${fileToken}
- table_id: ${tableId}
- operator: ${operatorId}
- changes: ${actionSummary}

请检查协作任务看板 (app_token: N6k0bL1Cga8OExsKzAAcXTpEnHd, table_id: tblE8V0SjVQVKB3e) 的最新状态变更，如有需要处理的任务请执行。`;
            const resp = await fetch(`http://127.0.0.1:${port}/hooks/agent`, {
              method: "POST",
              headers: { "Content-Type": "application/json", "Authorization": `Bearer ${hooksToken}` },
              body: JSON.stringify({ message: agentMessage }),
            });
            if (resp.ok) {
              log(`feishu[${accountId}]: triggered /hooks/agent for bitable record change on ${fileToken}`);
            } else {
              const body = await resp.text().catch(() => "");
              log(`feishu[${accountId}]: /hooks/agent returned ${resp.status}: ${body.slice(0,200)}`);
            }
          }
        } catch (wakeErr) {
          log(`feishu[${accountId}]: agent trigger for bitable change failed (non-fatal): ${String(wakeErr)}`);
        }
      } catch (err) {
        error(`feishu[${accountId}]: error handling bitable record changed event: ${String(err)}`);
      }
    },
    "drive.file.bitable_field_changed_v1": async (data) => {
      try {
        const fs = await import("fs");
        fs.appendFileSync("/tmp/feishu-events.log", `${new Date().toISOString()} drive.file.bitable_field_changed_v1 data=${JSON.stringify(data).slice(0,500)}\n`);
        log(`feishu[${accountId}]: bitable field changed event received`);
        // Field structure changes are less frequent, just log for now
      } catch (err) {
        error(`feishu[${accountId}]: error handling bitable field changed event: ${String(err)}`);
      }
    },
  });
}

type MonitorAccountParams = {
  cfg: ClawdbotConfig;
  account: ResolvedFeishuAccount;
  runtime?: RuntimeEnv;
  abortSignal?: AbortSignal;
};

/**
 * Monitor a single Feishu account.
 */
async function monitorSingleAccount(params: MonitorAccountParams): Promise<void> {
  const { cfg, account, runtime, abortSignal } = params;
  const { accountId } = account;
  const log = runtime?.log ?? console.log;

  // Fetch bot open_id
  const botOpenId = await fetchBotOpenId(account);
  botOpenIds.set(accountId, botOpenId ?? "");
  log(`feishu[${accountId}]: bot open_id resolved: ${botOpenId ?? "unknown"}`);

  const connectionMode = account.config.connectionMode ?? "websocket";
  const eventDispatcher = createEventDispatcher(account);
  const chatHistories = new Map<string, HistoryEntry[]>();

  registerEventHandlers(eventDispatcher, {
    cfg,
    accountId,
    runtime,
    chatHistories,
    fireAndForget: connectionMode === "webhook",
  });

  if (connectionMode === "webhook") {
    return monitorWebhook({ params, accountId, eventDispatcher });
  }

  return monitorWebSocket({ params, accountId, eventDispatcher });
}

type ConnectionParams = {
  params: MonitorAccountParams;
  accountId: string;
  eventDispatcher: Lark.EventDispatcher;
};

async function monitorWebSocket({
  params,
  accountId,
  eventDispatcher,
}: ConnectionParams): Promise<void> {
  const { account, runtime, abortSignal } = params;
  const log = runtime?.log ?? console.log;
  const error = runtime?.error ?? console.error;

  log(`feishu[${accountId}]: starting WebSocket connection...`);

  const wsClient = createFeishuWSClient(account);
  wsClients.set(accountId, wsClient);

  return new Promise((resolve, reject) => {
    const cleanup = () => {
      wsClients.delete(accountId);
      botOpenIds.delete(accountId);
    };

    const handleAbort = () => {
      log(`feishu[${accountId}]: abort signal received, stopping`);
      cleanup();
      resolve();
    };

    if (abortSignal?.aborted) {
      cleanup();
      resolve();
      return;
    }

    abortSignal?.addEventListener("abort", handleAbort, { once: true });

    try {
      wsClient.start({ eventDispatcher });
      log(`feishu[${accountId}]: WebSocket client started`);
    } catch (err) {
      cleanup();
      abortSignal?.removeEventListener("abort", handleAbort);
      reject(err);
    }
  });
}

async function monitorWebhook({
  params,
  accountId,
  eventDispatcher,
}: ConnectionParams): Promise<void> {
  const { account, runtime, abortSignal } = params;
  const log = runtime?.log ?? console.log;
  const error = runtime?.error ?? console.error;

  const port = account.config.webhookPort ?? 3000;
  const path = account.config.webhookPath ?? "/feishu/events";

  log(`feishu[${accountId}]: starting Webhook server on port ${port}, path ${path}...`);

  const server = http.createServer();
  server.on("request", Lark.adaptDefault(path, eventDispatcher, { autoChallenge: true }));
  httpServers.set(accountId, server);

  return new Promise((resolve, reject) => {
    const cleanup = () => {
      server.close();
      httpServers.delete(accountId);
      botOpenIds.delete(accountId);
    };

    const handleAbort = () => {
      log(`feishu[${accountId}]: abort signal received, stopping Webhook server`);
      cleanup();
      resolve();
    };

    if (abortSignal?.aborted) {
      cleanup();
      resolve();
      return;
    }

    abortSignal?.addEventListener("abort", handleAbort, { once: true });

    server.listen(port, () => {
      log(`feishu[${accountId}]: Webhook server listening on port ${port}`);
    });

    server.on("error", (err) => {
      error(`feishu[${accountId}]: Webhook server error: ${err}`);
      abortSignal?.removeEventListener("abort", handleAbort);
      reject(err);
    });
  });
}

/**
 * Main entry: start monitoring for all enabled accounts.
 */
export async function monitorFeishuProvider(opts: MonitorFeishuOpts = {}): Promise<void> {
  const cfg = opts.config;
  if (!cfg) {
    throw new Error("Config is required for Feishu monitor");
  }

  const log = opts.runtime?.log ?? console.log;

  // If accountId is specified, only monitor that account
  if (opts.accountId) {
    const account = resolveFeishuAccount({ cfg, accountId: opts.accountId });
    if (!account.enabled || !account.configured) {
      throw new Error(`Feishu account "${opts.accountId}" not configured or disabled`);
    }
    return monitorSingleAccount({
      cfg,
      account,
      runtime: opts.runtime,
      abortSignal: opts.abortSignal,
    });
  }

  // Otherwise, start all enabled accounts
  const accounts = listEnabledFeishuAccounts(cfg);
  if (accounts.length === 0) {
    throw new Error("No enabled Feishu accounts configured");
  }

  log(
    `feishu: starting ${accounts.length} account(s): ${accounts.map((a) => a.accountId).join(", ")}`,
  );

  // Start all accounts in parallel
  await Promise.all(
    accounts.map((account) =>
      monitorSingleAccount({
        cfg,
        account,
        runtime: opts.runtime,
        abortSignal: opts.abortSignal,
      }),
    ),
  );
}

/**
 * Stop monitoring for a specific account or all accounts.
 */
export function stopFeishuMonitor(accountId?: string): void {
  if (accountId) {
    wsClients.delete(accountId);
    const server = httpServers.get(accountId);
    if (server) {
      server.close();
      httpServers.delete(accountId);
    }
    botOpenIds.delete(accountId);
  } else {
    wsClients.clear();
    for (const server of httpServers.values()) {
      server.close();
    }
    httpServers.clear();
    botOpenIds.clear();
  }
}
