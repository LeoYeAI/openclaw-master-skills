/// <reference types="node" />
/**
 * Install script: add security-input-validator-plugin to ~/.openclaw/openclaw.json,
 * and copy .openclaw-sec.example.yaml to .openclaw-sec.yaml in this project (if not exists).
 * Run from plugin dir: npx tsx install.ts
 */
import * as path from "path";
import * as fs from "fs";
import * as os from "os";

const homedir = process.env.HOME || os.homedir();
const OPENCLAW_DIR = path.join(homedir, ".openclaw");
const OPENCLAW_CONFIG_PATH = path.join(OPENCLAW_DIR, "openclaw.json");

const PLUGIN_ID = "security-input-validator-plugin";
const PLUGIN_DIR = path.resolve(__dirname);
const PROJECT_ROOT = path.join(PLUGIN_DIR, "..", "..");
const EXAMPLE_CONFIG_PATH = path.join(PROJECT_ROOT, ".openclaw-sec.example.yaml");
const PROJECT_CONFIG_PATH = path.join(PROJECT_ROOT, ".openclaw-sec.yaml");

function main() {
  let config: Record<string, unknown> = {};
  if (fs.existsSync(OPENCLAW_CONFIG_PATH)) {
    try {
      const raw = fs.readFileSync(OPENCLAW_CONFIG_PATH, "utf-8");
      config = JSON.parse(raw) as Record<string, unknown>;
    } catch (e) {
      console.error("Failed to parse openclaw.json:", e);
      process.exit(1);
    }
  }

  const plugins = (config.plugins as Record<string, unknown>) || {};
  const load = (plugins.load as Record<string, unknown>) || {};
  const paths = Array.isArray(load.paths) ? [...(load.paths as string[])] : [];
  const entries = { ...(plugins.entries as Record<string, unknown>) };

  if (!paths.includes(PLUGIN_DIR)) {
    paths.push(PLUGIN_DIR);
  }
  entries[PLUGIN_ID] = { enabled: true };

  config.plugins = {
    ...plugins,
    enabled: plugins.enabled !== undefined ? plugins.enabled : true,
    load: { ...load, paths },
    entries,
  };

  if (!fs.existsSync(OPENCLAW_DIR)) {
    fs.mkdirSync(OPENCLAW_DIR, { recursive: true });
  }
  fs.writeFileSync(
    OPENCLAW_CONFIG_PATH,
    JSON.stringify(config, null, 2),
    "utf-8"
  );
  console.log(`Updated ${OPENCLAW_CONFIG_PATH}`);
  console.log(`Plugin path added: ${PLUGIN_DIR}`);

  if (fs.existsSync(EXAMPLE_CONFIG_PATH) && !fs.existsSync(PROJECT_CONFIG_PATH)) {
    fs.copyFileSync(EXAMPLE_CONFIG_PATH, PROJECT_CONFIG_PATH);
    console.log(`Created ${PROJECT_CONFIG_PATH} from .openclaw-sec.example.yaml`);
  } else if (!fs.existsSync(EXAMPLE_CONFIG_PATH)) {
    console.warn(`Example config not found at ${EXAMPLE_CONFIG_PATH}, skip copying.`);
  }
}

main();
