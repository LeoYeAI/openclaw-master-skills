// Simple in-process event bus for Server-Sent Events
// Every mutation (task move, agent status change, etc.) emits an event here.
// Connected SSE clients receive it instantly — no polling needed.

const listeners = new Set();

export function addListener(res) {
  listeners.add(res);
  res.on("close", () => listeners.delete(res));
}

export function broadcast(event, data) {
  const payload = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
  for (const res of listeners) {
    res.write(payload);
  }
}

export function getListenerCount() {
  return listeners.size;
}
