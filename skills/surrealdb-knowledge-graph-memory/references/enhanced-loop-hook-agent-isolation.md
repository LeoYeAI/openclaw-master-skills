# Enhanced Loop Hook — Agent Isolation Patch

Patches `src/agents/enhanced-loop-hook.ts` to extract the active agent's ID from the session key and pass it to `memory_inject`, so each agent's auto-injection is silently scoped to its own fact pool.

## What it does

- Imports `parseAgentSessionKey` from `session-key-utils`
- Adds `agentId` param to `injectMemoryContext()` (defaults to `"main"`)
- Appends `agent_id='<agentId>'` to the `mcporter` call args
- Extracts `agentId` from the session key at both injection call sites

## Apply

```bash
git apply references/enhanced-loop-hook-agent-isolation.md.patch
# or manually apply the diff below
```

## Diff

```diff
diff --git a/src/agents/enhanced-loop-hook.ts b/src/agents/enhanced-loop-hook.ts
index 3c16cf9b9..4fda9b04d 100644
--- a/src/agents/enhanced-loop-hook.ts
+++ b/src/agents/enhanced-loop-hook.ts
@@ -18,6 +18,7 @@ import { promisify } from "node:util";
 import { loadConfig } from "../config/config.js";
 import { emitAgentEvent } from "../infra/agent-events.js";
 import { createSubsystemLogger } from "../logging/subsystem.js";
+import { parseAgentSessionKey } from "../sessions/session-key-utils.js";
 import { resolveOpenClawAgentDir } from "./agent-paths.js";
 import { ensureAuthProfileStore } from "./auth-profiles.js";
 import { resolveApiKeyForProvider } from "./model-auth.js";
@@ -45,6 +46,7 @@ interface MemoryInjectResult {
 async function injectMemoryContext(
   query: string,
   config: EnhancedLoopConfig["memory"],
+  agentId: string = "main",
 ): Promise<string | null> {
   if (!config.autoInject) {
     log.debug("Memory injection disabled in config");
@@ -90,6 +92,7 @@ async function injectMemoryContext(
       `max_episodes:${config.maxEpisodes}`,
       `confidence_threshold:${config.episodeConfidenceThreshold}`,
       `include_relations:${config.includeRelations}`,
+      `agent_id='${agentId.replace(/'/g, "")}'`,
     ].join(" ");
 
     const cmd = `${mcporterPath} call surrealdb-memory.memory_inject ${args}`;
@@ -585,9 +588,13 @@ IMPORTANT: Update the step "status" values as you complete work. When you finish
         });
         if (config.memory?.autoInject && userGoal) {
           try {
-            const memoryContext = await injectMemoryContext(userGoal, config.memory);
+            const agentId = parseAgentSessionKey(sessionId)?.agentId ?? "main";
+            const memoryContext = await injectMemoryContext(userGoal, config.memory, agentId);
             if (memoryContext) {
-              log.info("Memory context injected into prompt", { length: memoryContext.length });
+              log.info("Memory context injected into prompt", {
+                length: memoryContext.length,
+                agentId,
+              });
               const existingPrompt = runParams.extraSystemPrompt || "";
               (runParams as { extraSystemPrompt?: string }).extraSystemPrompt =
                 existingPrompt + "\n\n" + memoryContext;
@@ -784,7 +791,12 @@ Current goal: ${userGoal}
       // Memory context injection from knowledge graph
       if (config.memory?.autoInject && userGoal) {
         try {
-          const memoryContext = await injectMemoryContext(userGoal, config.memory);
+          const sessionId =
+            (params as { sessionKey?: string; sessionId?: string }).sessionKey ??
+            (params as { sessionKey?: string; sessionId?: string }).sessionId ??
+            "default";
+          const agentId = parseAgentSessionKey(sessionId)?.agentId ?? "main";
+          const memoryContext = await injectMemoryContext(userGoal, config.memory, agentId);
           if (memoryContext) {
             const existingPrompt = runParams.extraSystemPrompt || "";
             (runParams as { extraSystemPrompt?: string }).extraSystemPrompt =
```
