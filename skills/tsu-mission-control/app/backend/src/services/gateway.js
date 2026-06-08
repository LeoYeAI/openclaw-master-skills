import WebSocket from "ws";
import { getDb } from "../db.js";
import { broadcast } from "./events.js";
import { setGatewaySender } from "./dispatcher.js";

let ws = null;
let reconnectTimer = null;
let msgId = 0;

const GATEWAY_URL = process.env.OPENCLAW_GATEWAY_URL || "ws://127.0.0.1:18789";
const GATEWAY_TOKEN = process.env.OPENCLAW_GATEWAY_TOKEN || "";

export function startGatewaySync() {
  if (!GATEWAY_URL) {
    console.log("[gateway] No OPENCLAW_GATEWAY_URL set — skipping live sync");
    return;
  }
  connect();
}

function connect() {
  if (ws) return;
  console.log(`[gateway] Connecting to ${GATEWAY_URL}...`);

  try {
    const headers = {};
    if (GATEWAY_TOKEN) headers["Authorization"] = `Bearer ${GATEWAY_TOKEN}`;

    ws = new WebSocket(GATEWAY_URL, { headers });
  } catch (err) {
    console.error("[gateway] Connection error:", err.message);
    scheduleReconnect();
    return;
  }

  ws.on("open", () => {
    console.log("[gateway] Connected");
    // Send hello / connect handshake (protocol v3)
    send("connect", {
      minProtocol: 2,
      maxProtocol: 3,
      client: {
        id: "mission-control",
        displayName: "Mission Control",
        version: "1.0.0",
        platform: "node",
        mode: "ui",
      },
    });
  });

  ws.on("message", (raw) => {
    try {
      const msg = JSON.parse(String(raw));
      handleMessage(msg);
    } catch {}
  });

  ws.on("close", () => {
    console.log("[gateway] Disconnected");
    ws = null;
    scheduleReconnect();
  });

  ws.on("error", (err) => {
    console.error("[gateway] Error:", err.message);
    try { ws.close(); } catch {}
    ws = null;
    scheduleReconnect();
  });
}

function send(method, params) {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  const id = `mc-${++msgId}`;
  ws.send(JSON.stringify({ type: "req", id, method, params }));
}

function handleMessage(msg) {
  const db = getDb();

  // Handle hello-ok response — sync initial presence
  if (msg.type === "res" && msg.payload?.type === "hello-ok") {
    console.log("[gateway] Handshake OK, protocol:", msg.payload.protocol);
    const presence = msg.payload.snapshot?.presence || [];
    syncPresence(presence);

    // Share the send function with the dispatcher for outbound events
    setGatewaySender(send);

    // Request health check
    send("health", {});
    return;
  }

  // Handle presence events (agent comes online / goes offline)
  if (msg.type === "event" && msg.event === "presence") {
    syncPresence(msg.payload?.presence || []);
    return;
  }

  // Handle agent events (task started, completed, etc.)
  if (msg.type === "event" && msg.event === "agent") {
    const { agentId, state, sessionKey, model } = msg.payload || {};
    if (agentId) {
      db.prepare(`
        INSERT INTO agents (id, display_name, status, model, last_heartbeat)
        VALUES (?, ?, ?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
          status = excluded.status,
          model = COALESCE(excluded.model, agents.model),
          last_heartbeat = datetime('now')
      `).run(agentId, agentId, state || "busy", model || "");

      broadcast("agent:updated", { id: agentId, status: state, model });
    }
    return;
  }

  // Handle health events
  if (msg.type === "event" && msg.event === "health") {
    broadcast("system:health", msg.payload);
    return;
  }

  // Handle tick (periodic heartbeat from gateway)
  if (msg.type === "event" && msg.event === "tick") {
    broadcast("system:tick", { ts: msg.payload?.ts });
    return;
  }
}

function syncPresence(presenceList) {
  const db = getDb();
  for (const p of presenceList) {
    const agentId = p.agentId || p.id || "main";
    const status = p.state === "active" ? "online" :
                   p.state === "busy" ? "busy" : "idle";

    db.prepare(`
      INSERT INTO agents (id, display_name, status, last_heartbeat)
      VALUES (?, ?, ?, datetime('now'))
      ON CONFLICT(id) DO UPDATE SET
        status = excluded.status,
        last_heartbeat = datetime('now')
    `).run(agentId, p.displayName || agentId, status);
  }
  broadcast("agents:synced", { count: presenceList.length });
}

function scheduleReconnect() {
  if (reconnectTimer) return;
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null;
    connect();
  }, 5000);
}

export function getGatewayStatus() {
  return {
    connected: ws?.readyState === WebSocket.OPEN,
    url: GATEWAY_URL,
  };
}
