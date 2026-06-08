import "dotenv/config";
import express from "express";
import cors from "cors";
import { getDb } from "./db.js";
import { startGatewaySync, getGatewayStatus } from "./services/gateway.js";
import { getListenerCount } from "./services/events.js";
import { startStallDetector } from "./services/stall-detector.js";
import { sanitizeBody, errorMiddleware } from "./middleware.js";

import projectsRouter from "./routes/projects.js";
import tasksRouter from "./routes/tasks.js";
import agentsRouter from "./routes/agents.js";
import eventsRouter from "./routes/events.js";
import hooksRouter from "./routes/hooks.js";
import requestsRouter from "./routes/requests.js";
import costsRouter from "./routes/costs.js";
import approvalsRouter from "./routes/approvals.js";
import reviewsRouter from "./routes/reviews.js";
import inboxRouter from "./routes/inbox.js";
import libraryRouter from "./routes/library.js";
import dispatchRouter from "./routes/dispatch.js";

const app = express();
const PORT = parseInt(process.env.PORT || "8000");

// ── Middleware ─────────────────────────────────────────
app.use(cors({ origin: process.env.CORS_ORIGIN || "*", credentials: true }));
app.use(express.json({ limit: "5mb" }));
app.use(sanitizeBody);

app.use((req, res, next) => {
  if (req.path !== "/api/events/stream" && req.path !== "/api/health") {
    console.log(`[${req.method}] ${req.path}`);
  }
  next();
});

// ── Optional auth ─────────────────────────────────────
if (process.env.AUTH_MODE === "local" && process.env.LOCAL_AUTH_TOKEN) {
  const token = process.env.LOCAL_AUTH_TOKEN;
  app.use("/api", (req, res, next) => {
    if (req.path === "/events/stream" || req.path === "/health") return next();
    if (req.path.startsWith("/hooks/") && req.headers["x-hook-secret"] === process.env.HOOK_SECRET) return next();
    const auth = req.headers.authorization;
    if (!auth || auth !== `Bearer ${token}`) return res.status(401).json({ error: "Unauthorized" });
    next();
  });
}

// ── Routes ────────────────────────────────────────────
app.use("/api/projects", projectsRouter);
app.use("/api/tasks", tasksRouter);
app.use("/api/agents", agentsRouter);
app.use("/api/events", eventsRouter);
app.use("/api/hooks", hooksRouter);
app.use("/api/requests", requestsRouter);
app.use("/api/costs", costsRouter);
app.use("/api/approvals", approvalsRouter);
app.use("/api/reviews", reviewsRouter);
app.use("/api/inbox", inboxRouter);
app.use("/api/library", libraryRouter);
app.use("/api/dispatch", dispatchRouter);

// ── Health ────────────────────────────────────────────
app.get("/api/health", (req, res) => {
  const db = getDb();
  const gw = getGatewayStatus();
  const pendingApprovals = db.prepare("SELECT COUNT(*) as c FROM approvals WHERE status = 'pending'").get().c;
  const pendingRequests = db.prepare("SELECT COUNT(*) as c FROM project_requests WHERE status IN ('pending','triaging')").get().c;
  const pendingReviews = db.prepare("SELECT COUNT(*) as c FROM reviews WHERE status IN ('pending','in_review')").get().c;
  res.json({ status: "ok", uptime: process.uptime(), gateway: gw, sseClients: getListenerCount(), pendingApprovals, pendingRequests, pendingReviews, timestamp: new Date().toISOString() });
});

// ── Global error handler (must be after all routes) ──
app.use(errorMiddleware);

// ── Start ─────────────────────────────────────────────
getDb();
startGatewaySync();
startStallDetector();

app.listen(PORT, () => {
  console.log(`\n  Mission Control v2.0 — http://localhost:${PORT}/api\n  Routes: projects, tasks, agents, requests, approvals, costs, hooks, events\n`);
});
