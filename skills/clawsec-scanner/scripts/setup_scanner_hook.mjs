#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HOOK_NAME = "clawsec-scanner-hook";
const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const SCANNER_DIR = path.resolve(SCRIPT_DIR, "..");
const SOURCE_HOOK_DIR = path.join(SCANNER_DIR, "hooks", HOOK_NAME);
const HOOKS_ROOT = path.join(os.homedir(), ".openclaw", "hooks");
const TARGET_HOOK_DIR = path.join(HOOKS_ROOT, HOOK_NAME);

function sh(cmd, args) {
  const result = spawnSync(cmd, args, {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });

  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    const details = (result.stderr || result.stdout || "").trim();
    throw new Error(`${cmd} ${args.join(" ")} failed${details ? `: ${details}` : ""}`);
  }

  return result.stdout;
}

function requireOpenClawCli() {
  try {
    sh("openclaw", ["--version"]);
  } catch (error) {
    throw new Error(
      "openclaw CLI is required. Install OpenClaw and ensure `openclaw` is available in PATH. " +
        `Original error: ${String(error)}`,
      { cause: error },
    );
  }
}

function assertSourceHookExists() {
  const requiredFiles = [
    "HOOK.md",
    "handler.ts",
  ];
  for (const file of requiredFiles) {
    const fullPath = path.join(SOURCE_HOOK_DIR, file);
    if (!fs.existsSync(fullPath)) {
      throw new Error(`Missing required hook file: ${fullPath}`);
    }
  }

  // Verify lib files exist in parent skill directory
  const requiredLibFiles = [
    "lib/utils.mjs",
    "lib/report.mjs",
    "lib/types.ts",
  ];
  for (const file of requiredLibFiles) {
    const fullPath = path.join(SCANNER_DIR, file);
    if (!fs.existsSync(fullPath)) {
      throw new Error(`Missing required lib file: ${fullPath}`);
    }
  }

  // Verify scanner scripts exist
  const requiredScripts = [
    "scripts/runner.sh",
    "scripts/scan_dependencies.mjs",
    "scripts/sast_analyzer.mjs",
    "scripts/dast_runner.mjs",
    "scripts/dast_hook_executor.mjs",
    "scripts/query_cve_databases.mjs",
  ];
  for (const file of requiredScripts) {
    const fullPath = path.join(SCANNER_DIR, file);
    if (!fs.existsSync(fullPath)) {
      throw new Error(`Missing required scanner script: ${fullPath}`);
    }
  }
}

function installHookFiles() {
  fs.mkdirSync(HOOKS_ROOT, { recursive: true });
  fs.rmSync(TARGET_HOOK_DIR, { recursive: true, force: true });
  fs.cpSync(SOURCE_HOOK_DIR, TARGET_HOOK_DIR, { recursive: true });

  // Copy lib files to hook directory
  const targetLibDir = path.join(TARGET_HOOK_DIR, "lib");
  const sourceLibDir = path.join(SCANNER_DIR, "lib");
  fs.mkdirSync(targetLibDir, { recursive: true });
  fs.cpSync(sourceLibDir, targetLibDir, { recursive: true });

  // Copy scanner scripts to hook directory
  const targetScriptsDir = path.join(TARGET_HOOK_DIR, "scripts");
  const sourceScriptsDir = path.join(SCANNER_DIR, "scripts");
  fs.mkdirSync(targetScriptsDir, { recursive: true });
  fs.cpSync(sourceScriptsDir, targetScriptsDir, { recursive: true });
}

function enableHook() {
  sh("openclaw", ["hooks", "enable", HOOK_NAME]);
}

function main() {
  assertSourceHookExists();
  requireOpenClawCli();
  installHookFiles();
  enableHook();

  process.stdout.write(`Installed hook files to: ${TARGET_HOOK_DIR}\n`);
  process.stdout.write(`Enabled hook: ${HOOK_NAME}\n`);
  process.stdout.write("Restart your OpenClaw gateway process so the hook is loaded.\n");
  process.stdout.write("After restart, run /new once to trigger an immediate vulnerability scan.\n");
}

try {
  main();
} catch (error) {
  process.stderr.write(`${String(error)}\n`);
  process.exit(1);
}
