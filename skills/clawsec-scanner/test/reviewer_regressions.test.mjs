#!/usr/bin/env node

/**
 * Regression tests for Baz review findings on PR #101.
 *
 * These tests enforce:
 * - execCommand supports cwd and runs tools in the target directory
 * - scan_dependencies chooses pip-audit invocation correctly when requirements.txt is absent
 * - runner.sh preserves DAST findings even when dast_runner exits non-zero
 */

import fs from "node:fs/promises";
import path from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { pass, fail, report, exitWithResults, createTempDir } from "./lib/test_harness.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SKILL_ROOT = path.resolve(__dirname, "..");
const SCRIPTS_DIR = path.join(SKILL_ROOT, "scripts");
const { execCommand } = await import(path.join(SKILL_ROOT, "lib", "utils.mjs"));

/**
 * @param {string} cmd
 * @param {string[]} args
 * @param {{cwd?: string, env?: NodeJS.ProcessEnv}} [options]
 * @returns {Promise<{code: number, stdout: string, stderr: string}>}
 */
async function runProcess(cmd, args, options = {}) {
  return new Promise((resolve) => {
    const proc = spawn(cmd, args, {
      cwd: options.cwd,
      env: options.env,
      stdio: ["ignore", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (chunk) => {
      stdout += String(chunk);
    });
    proc.stderr.on("data", (chunk) => {
      stderr += String(chunk);
    });

    proc.on("close", (code) => {
      resolve({ code: code ?? 1, stdout, stderr });
    });
  });
}

/**
 * @param {string} filePath
 * @param {string} content
 */
async function writeExecutable(filePath, content) {
  await fs.writeFile(filePath, content, "utf8");
  await fs.chmod(filePath, 0o755);
}

async function testExecCommandRespectsCwd() {
  const testName = "execCommand: respects cwd option";
  const tmp = await createTempDir();
  try {
    const result = await execCommand("node", ["-e", "process.stdout.write(process.cwd())"], {
      cwd: tmp.path,
    });

    const expectedPath = await fs.realpath(tmp.path);
    const actualPath = await fs.realpath(result.stdout.trim());

    if (actualPath === expectedPath) {
      pass(testName);
    } else {
      fail(testName, `Expected cwd ${expectedPath}, got ${actualPath}`);
    }
  } catch (error) {
    fail(testName, error);
  } finally {
    await tmp.cleanup();
  }
}

async function testScanDependenciesUsesTargetCwdAndSmartPipArgs() {
  const testName = "scan_dependencies: runs npm in target cwd and avoids -r when requirements.txt missing";

  const tmp = await createTempDir();
  try {
    const targetDir = path.join(tmp.path, "target");
    const binDir = path.join(tmp.path, "bin");
    const npmLogPath = path.join(tmp.path, "npm.log");
    const pipLogPath = path.join(tmp.path, "pip.log");

    await fs.mkdir(targetDir, { recursive: true });
    await fs.mkdir(binDir, { recursive: true });

    await fs.writeFile(path.join(targetDir, "package-lock.json"), "{}\n", "utf8");
    await fs.writeFile(path.join(targetDir, "pyproject.toml"), "[project]\nname='demo'\nversion='0.1.0'\n", "utf8");

    await writeExecutable(
      path.join(binDir, "npm"),
      `#!/usr/bin/env node
const fs = require("node:fs");
const logPath = process.env.CLAWSEC_TEST_NPM_LOG;
fs.appendFileSync(logPath, JSON.stringify({ cwd: process.cwd(), args: process.argv.slice(2) }) + "\\n");
process.stdout.write(JSON.stringify({ vulnerabilities: {} }));
`,
    );

    await writeExecutable(
      path.join(binDir, "pip-audit"),
      `#!/usr/bin/env node
const fs = require("node:fs");
const logPath = process.env.CLAWSEC_TEST_PIP_LOG;
fs.appendFileSync(logPath, JSON.stringify({ cwd: process.cwd(), args: process.argv.slice(2) }) + "\\n");
process.stdout.write(JSON.stringify({ dependencies: [] }));
`,
    );

    const env = {
      ...process.env,
      PATH: `${binDir}:${process.env.PATH}`,
      CLAWSEC_TEST_NPM_LOG: npmLogPath,
      CLAWSEC_TEST_PIP_LOG: pipLogPath,
    };

    const result = await runProcess(
      "node",
      [path.join(SCRIPTS_DIR, "scan_dependencies.mjs"), "--target", targetDir, "--format", "json"],
      { cwd: SKILL_ROOT, env },
    );

    if (result.code !== 0) {
      fail(testName, `scan_dependencies exited ${result.code}: ${result.stderr}`);
      return;
    }

    const npmLog = JSON.parse((await fs.readFile(npmLogPath, "utf8")).trim());
    const pipLog = JSON.parse((await fs.readFile(pipLogPath, "utf8")).trim());

    const expectedTargetPath = await fs.realpath(targetDir);
    const actualNpmCwd = await fs.realpath(npmLog.cwd);
    const npmCwdOk = actualNpmCwd === expectedTargetPath;
    const pipArgsOk = !pipLog.args.includes("-r");

    if (npmCwdOk && pipArgsOk) {
      pass(testName);
    } else {
      fail(
        testName,
        `npm cwd=${actualNpmCwd}, expected=${expectedTargetPath}; pip args=${JSON.stringify(pipLog.args)}`,
      );
    }
  } catch (error) {
    fail(testName, error);
  } finally {
    await tmp.cleanup();
  }
}

async function testRunnerPreservesDastReportOnNonZeroExit() {
  const testName = "runner.sh: preserves DAST findings when dast_runner exits 1";

  const tmp = await createTempDir();
  try {
    const targetDir = path.join(tmp.path, "target");
    const binDir = path.join(tmp.path, "bin");

    await fs.mkdir(targetDir, { recursive: true });
    await fs.mkdir(binDir, { recursive: true });

    await writeExecutable(
      path.join(binDir, "node"),
      `#!/usr/bin/env bash
set -euo pipefail

script="\${1:-}"
target="."
while [[ $# -gt 0 ]]; do
  if [[ "$1" == "--target" ]]; then
    target="\${2:-.}"
    break
  fi
  shift
done

if [[ "$script" == *"scan_dependencies.mjs" ]] || [[ "$script" == *"sast_analyzer.mjs" ]]; then
  cat <<JSON
{"scan_id":"test-scan","timestamp":"2026-03-09T00:00:00.000Z","target":"$target","vulnerabilities":[],"summary":{"critical":0,"high":0,"medium":0,"low":0,"info":0}}
JSON
  exit 0
fi

if [[ "$script" == *"dast_runner.mjs" ]]; then
  cat <<JSON
{"scan_id":"test-scan","timestamp":"2026-03-09T00:00:00.000Z","target":"$target","vulnerabilities":[{"id":"DAST-001","source":"dast","severity":"high","package":"N/A","version":"N/A","title":"DAST finding","description":"Synthetic high severity finding","references":[],"discovered_at":"2026-03-09T00:00:00.000Z"}],"summary":{"critical":0,"high":1,"medium":0,"low":0,"info":0}}
JSON
  exit 1
fi

echo "Unexpected node invocation: $*" >&2
exit 2
`,
    );

    const env = {
      ...process.env,
      PATH: `${binDir}:${process.env.PATH}`,
    };

    const result = await runProcess(
      "bash",
      [path.join(SCRIPTS_DIR, "runner.sh"), "--target", targetDir, "--format", "json"],
      { cwd: SKILL_ROOT, env },
    );

    if (result.code !== 0) {
      fail(testName, `runner.sh exited ${result.code}: ${result.stderr}`);
      return;
    }

    const merged = JSON.parse(result.stdout.trim());
    const hasDastFinding = Array.isArray(merged.vulnerabilities)
      && merged.vulnerabilities.some((v) => v.id === "DAST-001" && v.source === "dast" && v.severity === "high");

    if (hasDastFinding && merged.summary.high >= 1) {
      pass(testName);
    } else {
      fail(testName, `Expected DAST high finding to be preserved. Output: ${result.stdout}`);
    }
  } catch (error) {
    fail(testName, error);
  } finally {
    await tmp.cleanup();
  }
}

async function main() {
  await testExecCommandRespectsCwd();
  await testScanDependenciesUsesTargetCwdAndSmartPipArgs();
  await testRunnerPreservesDastReportOnNonZeroExit();

  report();
  exitWithResults();
}

await main();
