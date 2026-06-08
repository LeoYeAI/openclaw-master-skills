/**
 * notifications.js — Browser notification service for Mission Control
 *
 * Requests permission on first use, then fires desktop notifications
 * when actionable items arrive in the Inbox (reviews, approvals, requests).
 * Also provides an in-app toast system for when the tab is focused.
 */

let permissionGranted = false;
let toastContainer = null;

// ── Permission ──────────────────────────────────────
export async function requestNotificationPermission() {
  if (!("Notification" in window)) return false;
  if (Notification.permission === "granted") {
    permissionGranted = true;
    return true;
  }
  if (Notification.permission === "denied") return false;

  const result = await Notification.requestPermission();
  permissionGranted = result === "granted";
  return permissionGranted;
}

// ── Desktop notification ────────────────────────────
export function notify(title, options = {}) {
  // Always show in-app toast
  showToast(title, options.body, options.type || "info");

  // Desktop notification only if tab is not focused
  if (!document.hasFocus() && permissionGranted && "Notification" in window) {
    try {
      const n = new Notification(title, {
        body: options.body || "",
        icon: options.icon || "/favicon.svg",
        tag: options.tag || "mc-" + Date.now(),
        silent: false,
      });

      // Focus tab when clicked
      n.onclick = () => {
        window.focus();
        n.close();
        if (options.onClick) options.onClick();
      };

      // Auto-close after 8 seconds
      setTimeout(() => n.close(), 8000);
    } catch (err) {
      console.warn("[notifications] Desktop notification failed:", err.message);
    }
  }
}

// ── Event-specific notifications ────────────────────
export function notifyInboxItem(event, payload) {
  switch (event) {
    case "review:submitted":
      notify("Review submitted", {
        body: `${payload.submitted_by || "Agent"} submitted "${payload.task_title || "task"}" for review`,
        type: "review",
        tag: "review-" + (payload.review?.id || Date.now()),
      });
      break;

    case "approval:created":
      notify("Approval needed", {
        body: payload.title || "An agent needs your approval",
        type: "approval",
        tag: "approval-" + (payload.id || Date.now()),
      });
      break;

    case "request:submitted":
      notify("New request", {
        body: payload.title || "A new project request was submitted",
        type: "request",
        tag: "request-" + (payload.id || Date.now()),
      });
      break;

    case "task:stalled":
      notify("Stalled task", {
        body: `"${payload.task?.title || "Task"}" has stalled`,
        type: "warning",
        tag: "stall-" + (payload.task?.id || Date.now()),
      });
      break;

    case "task:failed":
      notify("Task failed", {
        body: `"${payload.task_title || "Task"}" failed: ${payload.reason || "unknown"}`,
        type: "error",
        tag: "fail-" + Date.now(),
      });
      break;

    case "library:published":
      notify("Document published", {
        body: `"${payload.title || "Document"}" added to the Library`,
        type: "info",
        tag: "doc-" + (payload.id || Date.now()),
      });
      break;

    case "agent:error":
      notify("Agent error", {
        body: `${payload.agentId || "Agent"}: ${payload.error || "Unknown error"}`,
        type: "error",
        tag: "agent-error-" + Date.now(),
      });
      break;
  }
}

// ── In-app toast system ─────────────────────────────
const TOAST_COLORS = {
  info: { bg: "rgba(99,102,241,0.15)", border: "rgba(99,102,241,0.3)", text: "#818cf8" },
  review: { bg: "rgba(168,85,247,0.15)", border: "rgba(168,85,247,0.3)", text: "#c084fc" },
  approval: { bg: "rgba(245,158,11,0.15)", border: "rgba(245,158,11,0.3)", text: "#fbbf24" },
  request: { bg: "rgba(59,130,246,0.15)", border: "rgba(59,130,246,0.3)", text: "#60a5fa" },
  warning: { bg: "rgba(245,158,11,0.15)", border: "rgba(245,158,11,0.3)", text: "#fbbf24" },
  error: { bg: "rgba(239,68,68,0.15)", border: "rgba(239,68,68,0.3)", text: "#f87171" },
  success: { bg: "rgba(16,185,129,0.15)", border: "rgba(16,185,129,0.3)", text: "#34d399" },
};

function ensureToastContainer() {
  if (toastContainer && document.body.contains(toastContainer)) return toastContainer;

  toastContainer = document.createElement("div");
  toastContainer.id = "mc-toasts";
  toastContainer.style.cssText = "position:fixed;top:60px;right:16px;z-index:9999;display:flex;flex-direction:column;gap:8px;pointer-events:none;max-width:380px";
  document.body.appendChild(toastContainer);
  return toastContainer;
}

function showToast(title, body, type = "info") {
  const container = ensureToastContainer();
  const colors = TOAST_COLORS[type] || TOAST_COLORS.info;

  const toast = document.createElement("div");
  toast.style.cssText = `
    background:${colors.bg};
    border:1px solid ${colors.border};
    border-radius:10px;
    padding:12px 16px;
    pointer-events:auto;
    cursor:pointer;
    backdrop-filter:blur(12px);
    animation:mc-toast-in 0.3s ease;
    transition:opacity 0.3s, transform 0.3s;
    box-shadow:0 4px 24px rgba(0,0,0,0.4);
  `;

  toast.innerHTML = `
    <div style="font-size:12px;font-weight:600;color:${colors.text};margin-bottom:${body ? "3px" : "0"}">${escapeText(title)}</div>
    ${body ? `<div style="font-size:11px;color:#94a3b8;line-height:1.4">${escapeText(body)}</div>` : ""}
  `;

  toast.onclick = () => dismissToast(toast);
  container.appendChild(toast);

  // Auto-dismiss after 5 seconds
  setTimeout(() => dismissToast(toast), 5000);
}

function dismissToast(toast) {
  toast.style.opacity = "0";
  toast.style.transform = "translateX(20px)";
  setTimeout(() => toast.remove(), 300);
}

function escapeText(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// ── Inject toast animation CSS ──────────────────────
if (typeof document !== "undefined") {
  const style = document.createElement("style");
  style.textContent = `@keyframes mc-toast-in { from { opacity:0; transform:translateX(20px); } to { opacity:1; transform:translateX(0); } }`;
  document.head.appendChild(style);
}
