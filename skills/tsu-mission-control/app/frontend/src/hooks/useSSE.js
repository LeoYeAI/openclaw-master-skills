import { useEffect, useRef, useCallback, useState } from "react";

export function useSSE(onEvent) {
  const [connected, setConnected] = useState(false);
  const sourceRef = useRef(null);
  const cbRef = useRef(onEvent);
  cbRef.current = onEvent;

  useEffect(() => {
    let es;
    let retryTimer;

    function connect() {
      es = new EventSource("/api/events/stream");
      sourceRef.current = es;

      es.onopen = () => setConnected(true);

      // Listen to all event types we care about
      const events = [
        "connected",
        "project:created", "project:updated", "project:deleted", "project:completed",
        "task:created", "task:updated", "task:deleted", "task:moved",
        "task:started", "task:completed", "task:failed", "task:progress", "task:review", "task:stalled",
        "agent:updated", "agent:heartbeat", "agent:idle", "agent:error", "agent:stale",
        "agents:synced",
        "system:health", "system:tick",
        "session.created", "session.ended",
        "request:submitted", "request:triaged", "request:converted", "request:deleted",
        "approval:created", "approval:approved", "approval:rejected",
        "review:submitted", "review:approved", "review:changes_requested", "review:rejected", "review:commented",
        "library:published", "library:updated", "library:deleted",
        "cost:recorded",
      ];

      for (const evt of events) {
        es.addEventListener(evt, (e) => {
          try {
            const data = JSON.parse(e.data);
            cbRef.current?.({ event: evt, data });
          } catch {}
        });
      }

      es.onerror = () => {
        setConnected(false);
        es.close();
        retryTimer = setTimeout(connect, 3000);
      };
    }

    connect();
    return () => {
      clearTimeout(retryTimer);
      es?.close();
    };
  }, []);

  return { connected };
}
