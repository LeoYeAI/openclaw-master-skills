diff --git a/ui/src/ui/views/chat.ts b/ui/src/ui/views/chat.ts
index 1ef922452..61528b488 100644
--- a/ui/src/ui/views/chat.ts
+++ b/ui/src/ui/views/chat.ts
@@ -508,6 +508,18 @@ function buildChatItems(props: ChatProps): Array<ChatItem | MessageGroup> {
       continue;
     }
 
+    // Hide NO_REPLY / silent reply messages from the chat display
+    if (normalized.role === "assistant") {
+      const fullText = normalized.content
+        .filter((c) => c.type === "text" && c.text)
+        .map((c) => c.text!.trim())
+        .join("")
+        .trim();
+      if (fullText === "NO_REPLY" || fullText === "HEARTBEAT_OK") {
+        continue;
+      }
+    }
+
     items.push({
       kind: "message",
       key: messageKey(msg, i),
