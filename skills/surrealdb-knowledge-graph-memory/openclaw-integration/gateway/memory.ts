import { spawn, exec } from "node:child_process";
import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";
import { promisify } from "node:util";

import type { GatewayRequestHandlers } from "./types.js";

const execAsync = promisify(exec);

const SURREALDB_PORT = 8000;
const DATA_DIR = path.join(os.homedir(), ".openclaw", "memory");
const DB_FILE = path.join(DATA_DIR, "knowledge.db");

// Find skill directory (search common locations)
function findSkillDir(): string | null {
  const candidates = [
    path.join(os.homedir(), ".openclaw", "workspace", "skills", "surrealdb-memory"),
    path.join(os.homedir(), "openclaw", "skills", "surrealdb-memory"),
    path.join(os.homedir(), "openclaw-workspace", "skills", "surrealdb-memory"),
    path.join(os.homedir(), ".openclaw", "skills", "surrealdb-memory"),
  ];

  for (const dir of candidates) {
    if (fs.existsSync(path.join(dir, "SKILL.md"))) {
      return dir;
    }
  }
  return null;
}

function which(cmd: string): string | null {
  const paths = (process.env.PATH || "").split(path.delimiter);
  const extensions = process.platform === "win32" ? [".exe", ".cmd", ".bat", ""] : [""];

  for (const dir of paths) {
    for (const ext of extensions) {
      const fullPath = path.join(dir, cmd + ext);
      try {
        fs.accessSync(fullPath, fs.constants.X_OK);
        return fullPath;
      } catch {
        // Not found, continue
      }
    }
  }

  // Also check common install locations
  const extraPaths = [
    path.join(os.homedir(), ".surrealdb", "surreal"),
    "/usr/local/bin/surreal",
  ];

  for (const fullPath of extraPaths) {
    try {
      fs.accessSync(fullPath, fs.constants.X_OK);
      return fullPath;
    } catch {
      // Not found, continue
    }
  }

  return null;
}

async function checkSurrealDbInstalled(): Promise<{
  installed: boolean;
  path: string | null;
  version: string | null;
}> {
  const surrealPath = which("surreal");
  if (!surrealPath) {
    return { installed: false, path: null, version: null };
  }

  try {
    const { stdout } = await execAsync(`"${surrealPath}" version`, { timeout: 5000 });
    const version = stdout.trim().split("\n")[0] || "unknown";
    return { installed: true, path: surrealPath, version };
  } catch (e) {
    return { installed: true, path: surrealPath, version: `error: ${e}` };
  }
}

async function checkSurrealDbRunning(): Promise<{
  running: boolean;
  port: number;
  error?: string;
}> {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3000);

    const response = await fetch(`http://localhost:${SURREALDB_PORT}/health`, {
      signal: controller.signal,
    });
    clearTimeout(timeout);

    return { running: response.ok, port: SURREALDB_PORT };
  } catch (e) {
    return {
      running: false,
      port: SURREALDB_PORT,
      error: e instanceof Error ? e.message : String(e),
    };
  }
}

async function checkSchemaInitialized(): Promise<{
  initialized: boolean;
  error?: string;
}> {
  try {
    const surrealPath = which("surreal");
    if (!surrealPath) {
      return { initialized: false, error: "surreal not found" };
    }

    const { stdout } = await execAsync(
      `echo "INFO FOR DB;" | "${surrealPath}" sql --conn http://localhost:${SURREALDB_PORT} --user root --pass root --ns openclaw --db memory`,
      { timeout: 10000 }
    );

    const hasFact = stdout.includes("fact");
    return { initialized: hasFact };
  } catch (e) {
    return {
      initialized: false,
      error: e instanceof Error ? e.message : String(e),
    };
  }
}

function checkPythonDeps(): {
  ok: boolean;
  dependencies: Record<string, boolean>;
} {
  // For now, just check if Python is available
  const pythonPath = which("python3") || which("python");
  return {
    ok: !!pythonPath,
    dependencies: {
      python: !!pythonPath,
      surrealdb: false, // Would need to run pip list to check
      openai: false,
      yaml: false,
    },
  };
}

async function getFullHealth() {
  const [binary, server, schema] = await Promise.all([
    checkSurrealDbInstalled(),
    checkSurrealDbRunning(),
    checkSchemaInitialized(),
  ]);

  return {
    timestamp: new Date().toISOString(),
    surrealdb_binary: binary,
    surrealdb_server: server,
    schema,
    python_deps: checkPythonDeps(),
    data_dir: {
      path: DATA_DIR,
      exists: fs.existsSync(DATA_DIR),
    },
  };
}

async function getStats() {
  try {
    const surrealPath = which("surreal");
    if (!surrealPath) {
      return { error: "surreal not found" };
    }

    // NOTE: Use `archived != true` not `archived = false`.
    // Facts with no explicit archived field have archived = NONE, which != false in SurrealDB.
    const queries = [
      "SELECT count() FROM fact WHERE archived != true GROUP ALL;",
      "SELECT count() FROM entity GROUP ALL;",
      "SELECT count() FROM relates_to GROUP ALL;",
      "SELECT count() FROM episode GROUP ALL;",
      "SELECT count() FROM fact WHERE archived = true GROUP ALL;",
      "SELECT math::mean(confidence) AS avg FROM fact WHERE archived != true GROUP ALL;",
    ].join("\n");

    const { stdout } = await execAsync(
      `echo "${queries}" | "${surrealPath}" sql --conn http://localhost:${SURREALDB_PORT} --user root --pass root --ns openclaw --db memory`,
      { timeout: 15000 }
    );

    // Parse all count values by position (not by checking if current value === 0,
    // which breaks when a table legitimately has 0 rows).
    const countValues = [...stdout.matchAll(/count:\s*(\d+)/g)].map((m) => parseInt(m[1], 10));
    const avgMatch = stdout.match(/avg:\s*([\d.]+)/);

    const [facts = 0, entities = 0, relationships = 0, episodes = 0, archived = 0] = countValues;
    const avg_confidence = avgMatch ? parseFloat(avgMatch[1]) : 0;

    return {
      facts,
      entities,
      relationships,
      episodes,
      archived,
      avg_confidence,
      by_source: [],
    };
  } catch (e) {
    return { error: e instanceof Error ? e.message : String(e) };
  }
}

async function installSurrealDb(): Promise<{
  success: boolean;
  stdout?: string;
  stderr?: string;
  error?: string;
}> {
  try {
    const { stdout, stderr } = await execAsync(
      "curl -sSf https://install.surrealdb.com | sh",
      { timeout: 300000 }
    );
    return { success: true, stdout, stderr };
  } catch (e) {
    return {
      success: false,
      error: e instanceof Error ? e.message : String(e),
    };
  }
}

async function installPythonDeps(): Promise<{
  success: boolean;
  stdout?: string;
  stderr?: string;
  error?: string;
}> {
  try {
    const skillDir = findSkillDir();
    if (skillDir && fs.existsSync(path.join(skillDir, ".venv"))) {
      // Use existing venv
      const { stdout, stderr } = await execAsync(
        `source "${path.join(skillDir, ".venv", "bin", "activate")}" && pip install surrealdb openai pyyaml`,
        { timeout: 120000, shell: "/bin/bash" }
      );
      return { success: true, stdout, stderr };
    }

    // Try pip with --user
    const { stdout, stderr } = await execAsync(
      "pip3 install --user surrealdb openai pyyaml || pip install --user surrealdb openai pyyaml",
      { timeout: 120000, shell: "/bin/bash" }
    );
    return { success: true, stdout, stderr };
  } catch (e) {
    return {
      success: false,
      error: e instanceof Error ? e.message : String(e),
    };
  }
}

async function startSurrealDb(): Promise<{
  success: boolean;
  pid?: number;
  error?: string;
}> {
  try {
    // Ensure data dir exists
    fs.mkdirSync(DATA_DIR, { recursive: true });

    const surrealPath = which("surreal") || path.join(os.homedir(), ".surrealdb", "surreal");

    const child = spawn(
      surrealPath,
      ["start", "--bind", "127.0.0.1:8000", "--user", "root", "--pass", "root", `file:${DB_FILE}`],
      {
        detached: true,
        stdio: "ignore",
      }
    );

    child.unref();

    // Wait a bit for startup
    await new Promise((r) => setTimeout(r, 3000));

    // Check if it started
    const running = await checkSurrealDbRunning();
    if (running.running) {
      return { success: true, pid: child.pid };
    }

    return { success: false, error: "Server did not start" };
  } catch (e) {
    return {
      success: false,
      error: e instanceof Error ? e.message : String(e),
    };
  }
}

async function initSchema(): Promise<{
  success: boolean;
  stdout?: string;
  stderr?: string;
  error?: string;
}> {
  try {
    const skillDir = findSkillDir();
    if (!skillDir) {
      return { success: false, error: "surrealdb-memory skill not found" };
    }

    // Try v2 schema first, fall back to v1
    let schemaFile = path.join(skillDir, "scripts", "schema-v2.sql");
    if (!fs.existsSync(schemaFile)) {
      schemaFile = path.join(skillDir, "scripts", "schema.sql");
    }
    if (!fs.existsSync(schemaFile)) {
      return { success: false, error: "schema file not found" };
    }

    const surrealPath = which("surreal") || path.join(os.homedir(), ".surrealdb", "surreal");

    try {
      const { stdout, stderr } = await execAsync(
        `"${surrealPath}" import --conn http://localhost:${SURREALDB_PORT} --user root --pass root --ns openclaw --db memory "${schemaFile}"`,
        { timeout: 30000 }
      );
      return { success: true, stdout, stderr };
    } catch (importError) {
      // If import fails due to existing tables, try the Python migration for v2
      const migrateScript = path.join(skillDir, "scripts", "migrate-v2.py");
      if (fs.existsSync(migrateScript)) {
        const venvPython = path.join(skillDir, ".venv", "bin", "python3");
        const pythonCmd = fs.existsSync(venvPython) ? venvPython : "python3";
        try {
          const { stdout: migrateOut } = await execAsync(`"${pythonCmd}" "${migrateScript}"`, { timeout: 60000 });
          return { success: true, stdout: migrateOut };
        } catch {
          // Fall through to schema check
        }
      }
      
      // Check if schema is actually there
      const checkResult = await checkSchemaInitialized();
      if (checkResult.initialized) {
        return { success: true, stdout: "Schema already initialized" };
      }
      throw importError;
    }
  } catch (e) {
    const errorMsg = e instanceof Error ? e.message : String(e);
    // Consider "already exists" as success
    if (errorMsg.includes("already exists")) {
      return { success: true, stdout: "Schema already exists" };
    }
    return {
      success: false,
      error: errorMsg,
    };
  }
}

async function autoRepair(): Promise<{
  success: boolean;
  steps: Array<{ step: string; result: unknown }>;
}> {
  const steps: Array<{ step: string; result: unknown }> = [];

  // 1. Check/install binary
  const binary = await checkSurrealDbInstalled();
  if (!binary.installed) {
    steps.push({ step: "install_binary", result: await installSurrealDb() });
  } else {
    steps.push({ step: "install_binary", result: { skipped: true, reason: "already installed" } });
  }

  // 2. Check/start server
  const server = await checkSurrealDbRunning();
  if (!server.running) {
    steps.push({ step: "start_server", result: await startSurrealDb() });
    await new Promise((r) => setTimeout(r, 2000));
  } else {
    steps.push({ step: "start_server", result: { skipped: true, reason: "already running" } });
  }

  // 3. Check/init schema
  const schema = await checkSchemaInitialized();
  if (!schema.initialized) {
    steps.push({ step: "init_schema", result: await initSchema() });
  } else {
    steps.push({ step: "init_schema", result: { skipped: true, reason: "already initialized" } });
  }

  // Final health check
  const finalHealth = await getFullHealth();
  const success =
    finalHealth.surrealdb_binary.installed &&
    finalHealth.surrealdb_server.running &&
    finalHealth.schema.initialized;

  return { success, steps };
}

async function runMaintenance(
  operation: string
): Promise<{ success: boolean; [key: string]: unknown }> {
  try {
    const surrealPath = which("surreal");
    if (!surrealPath) {
      return { success: false, error: "surreal not found" };
    }

    let query = "";
    switch (operation) {
      case "decay":
        query =
          "UPDATE fact SET confidence = confidence * 0.95 WHERE last_accessed < time::now() - 30d AND archived = false;";
        break;
      case "prune":
        query =
          "DELETE FROM fact WHERE confidence < 0.2 AND last_confirmed < time::now() - 30d;";
        break;
      case "full":
        query = `
          UPDATE fact SET confidence = confidence * 0.95 WHERE last_accessed < time::now() - 30d AND archived = false;
          DELETE FROM fact WHERE confidence < 0.2 AND last_confirmed < time::now() - 30d;
        `;
        break;
      default:
        return { success: false, error: `Unknown operation: ${operation}` };
    }

    const { stdout } = await execAsync(
      `echo "${query}" | "${surrealPath}" sql --conn http://localhost:${SURREALDB_PORT} --user root --pass root --ns openclaw --db memory`,
      { timeout: 60000 }
    );

    return { success: true, operation, output: stdout };
  } catch (e) {
    return {
      success: false,
      error: e instanceof Error ? e.message : String(e),
    };
  }
}

export const memoryHandlers: GatewayRequestHandlers = {
  "memory.health": async ({ respond }) => {
    try {
      const health = await getFullHealth();
      respond(true, health, undefined);
    } catch (e) {
      respond(true, { error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "memory.stats": async ({ respond }) => {
    try {
      const stats = await getStats();
      respond(true, stats, undefined);
    } catch (e) {
      respond(true, { error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "memory.repair": async ({ respond }) => {
    try {
      const result = await autoRepair();
      respond(true, result, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "memory.install.binary": async ({ respond }) => {
    try {
      const result = await installSurrealDb();
      respond(true, result, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "memory.install.python": async ({ respond }) => {
    try {
      const result = await installPythonDeps();
      respond(true, result, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "memory.install.start": async ({ respond }) => {
    try {
      const result = await startSurrealDb();
      respond(true, result, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "memory.install.schema": async ({ respond }) => {
    try {
      const result = await initSchema();
      respond(true, result, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "memory.maintenance": async ({ params, respond }) => {
    try {
      const operation = (params as { operation?: string })?.operation || "full";
      const result = await runMaintenance(operation);
      respond(true, result, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "memory.activity": async ({ respond }) => {
    try {
      // Return recent memory activity (extractions, queries, etc.)
      // For now, return empty activity until we implement activity tracking
      respond(true, {
        recentExtractions: [],
        recentQueries: [],
        lastExtraction: null,
        lastQuery: null,
      }, undefined);
    } catch (e) {
      respond(true, { error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "memory.extractionProgress": async ({ respond }) => {
    try {
      // Check for extraction progress file
      const progressFile = path.join(DATA_DIR, "extraction-progress.json");
      if (fs.existsSync(progressFile)) {
        const data = JSON.parse(fs.readFileSync(progressFile, "utf-8"));
        // Add running flag based on phase
        const running = data.phase !== "complete";
        respond(true, { ...data, running }, undefined);
      } else {
        respond(true, { running: false }, undefined);
      }
    } catch (e) {
      respond(true, { running: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },

  "memory.runExtraction": async ({ params, respond }) => {
    try {
      console.log("[memory.runExtraction] params:", JSON.stringify(params));
      const { full = false, reconcile = false, relations = false } = params as { 
        full?: boolean; 
        reconcile?: boolean;
        relations?: boolean;
      };
      console.log("[memory.runExtraction] parsed: full=", full, "reconcile=", reconcile, "relations=", relations);
      const skillDir = findSkillDir();
      if (!skillDir) {
        respond(true, { success: false, error: "surrealdb-memory skill not found" }, undefined);
        return;
      }

      const script = path.join(skillDir, "scripts", "extract-knowledge.py");
      if (!fs.existsSync(script)) {
        respond(true, { success: false, error: "extract-knowledge.py not found" }, undefined);
        return;
      }

      const venvPython = path.join(skillDir, ".venv", "bin", "python3");
      const pythonCmd = fs.existsSync(venvPython) ? venvPython : "python3";
      
      // Build command based on operation type
      let command: string;
      if (relations) {
        command = `"${pythonCmd}" "${script}" discover-relations`;
      } else if (reconcile) {
        command = `"${pythonCmd}" "${script}" reconcile`;
      } else {
        command = `"${pythonCmd}" "${script}" extract${full ? " --full" : ""}`;
      }

      const { stdout, stderr } = await execAsync(command, { timeout: 300000, cwd: skillDir });

      respond(true, { success: true, output: stdout, stderr, _debug: { command, relations, reconcile, full } }, undefined);
    } catch (e) {
      respond(true, { success: false, error: e instanceof Error ? e.message : String(e) }, undefined);
    }
  },
};
