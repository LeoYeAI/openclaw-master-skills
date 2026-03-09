diff --git a/src/gateway/server-methods/sessions.ts b/src/gateway/server-methods/sessions.ts
index af072f494..8f14ec902 100644
--- a/src/gateway/server-methods/sessions.ts
+++ b/src/gateway/server-methods/sessions.ts
@@ -407,13 +407,7 @@ export const sessionsHandlers: GatewayRequestHandlers = {
       return;
     }
 
-    const maxLines =
-      typeof p.maxLines === "number" && Number.isFinite(p.maxLines)
-        ? Math.max(1, Math.floor(p.maxLines))
-        : 400;
-
     const { cfg, target, storePath } = resolveGatewaySessionTargetFromKey(key);
-    // Lock + read in a short critical section; transcript work happens outside.
     const compactTarget = await updateSessionStore(storePath, (store) => {
       const { entry, primaryKey } = migrateAndPruneSessionStoreKey({ cfg, key, store });
       return { entry, primaryKey };
@@ -421,80 +415,74 @@ export const sessionsHandlers: GatewayRequestHandlers = {
     const entry = compactTarget.entry;
     const sessionId = entry?.sessionId;
     if (!sessionId) {
-      respond(
-        true,
-        {
-          ok: true,
-          key: target.canonicalKey,
-          compacted: false,
-          reason: "no sessionId",
-        },
-        undefined,
-      );
-      return;
-    }
-
-    const filePath = resolveSessionTranscriptCandidates(
-      sessionId,
-      storePath,
-      entry?.sessionFile,
-      target.agentId,
-    ).find((candidate) => fs.existsSync(candidate));
-    if (!filePath) {
-      respond(
-        true,
-        {
-          ok: true,
-          key: target.canonicalKey,
-          compacted: false,
-          reason: "no transcript",
-        },
-        undefined,
-      );
+      respond(true, { ok: true, key: target.canonicalKey, compacted: false, reason: "no sessionId" }, undefined);
       return;
     }
 
-    const raw = fs.readFileSync(filePath, "utf-8");
-    const lines = raw.split(/\r?\n/).filter((l) => l.trim().length > 0);
-    if (lines.length <= maxLines) {
-      respond(
-        true,
-        {
-          ok: true,
-          key: target.canonicalKey,
-          compacted: false,
-          kept: lines.length,
-        },
-        undefined,
-      );
-      return;
+    // Use the real LLM-based compaction engine (same as /compact command)
+    const { compactEmbeddedPiSession } = await import("../../agents/pi-embedded.js");
+    const { isEmbeddedPiRunActive, abortEmbeddedPiRun: abortRun, waitForEmbeddedPiRunEnd: waitEnd } =
+      await import("../../agents/pi-embedded.js");
+    const { resolveSessionFilePath, resolveSessionFilePathOptions } = await import("../../config/sessions.js");
+    const { resolveSessionAgentId } = await import("../../routing/session-key.js");
+
+    // Abort any active run first
+    if (isEmbeddedPiRunActive(sessionId)) {
+      abortRun(sessionId);
+      await waitEnd(sessionId, 15_000);
     }
 
-    const archived = archiveFileOnDisk(filePath, "bak");
-    const keptLines = lines.slice(-maxLines);
-    fs.writeFileSync(filePath, `${keptLines.join("\n")}\n`, "utf-8");
+    const agentId = target.agentId || resolveSessionAgentId({ sessionKey: key, config: cfg });
+    const { provider, model } = resolveSessionModelRef(cfg, entry, agentId);
+    const sessionFile = resolveSessionFilePath(
+      sessionId,
+      entry,
+      resolveSessionFilePathOptions({ agentId, storePath }),
+    );
+    const workspaceDir = cfg.workspace?.dir || process.env.OPENCLAW_WORKSPACE || `${process.env.HOME}/.openclaw/workspace`;
 
-    await updateSessionStore(storePath, (store) => {
-      const entryKey = compactTarget.primaryKey;
-      const entryToUpdate = store[entryKey];
-      if (!entryToUpdate) {
-        return;
-      }
-      delete entryToUpdate.inputTokens;
-      delete entryToUpdate.outputTokens;
-      delete entryToUpdate.totalTokens;
-      delete entryToUpdate.totalTokensFresh;
-      entryToUpdate.updatedAt = Date.now();
+    const result = await compactEmbeddedPiSession({
+      sessionId,
+      sessionKey: key,
+      sessionFile,
+      workspaceDir,
+      config: cfg,
+      skillsSnapshot: entry?.skillsSnapshot,
+      provider,
+      model,
+      trigger: "manual",
+      senderIsOwner: true,
+      customInstructions: typeof p.instructions === "string" ? p.instructions : undefined,
     });
 
+    // Update token counts after compaction
+    if (result.ok && result.compacted) {
+      await updateSessionStore(storePath, (store) => {
+        const entryToUpdate = store[compactTarget.primaryKey];
+        if (!entryToUpdate) return;
+        if (result.result?.tokensAfter != null) {
+          entryToUpdate.totalTokens = result.result.tokensAfter;
+          entryToUpdate.totalTokensFresh = result.result.tokensAfter;
+        } else {
+          delete entryToUpdate.inputTokens;
+          delete entryToUpdate.outputTokens;
+          delete entryToUpdate.totalTokens;
+          delete entryToUpdate.totalTokensFresh;
+        }
+        entryToUpdate.compactionCount = (entryToUpdate.compactionCount ?? 0) + 1;
+        entryToUpdate.updatedAt = Date.now();
+      });
+    }
+
     respond(
       true,
       {
         ok: true,
         key: target.canonicalKey,
-        compacted: true,
-        archived,
-        kept: keptLines.length,
+        compacted: result.compacted ?? false,
+        tokensBefore: result.result?.tokensBefore,
+        tokensAfter: result.result?.tokensAfter,
+        reason: result.reason,
       },
       undefined,
     );
