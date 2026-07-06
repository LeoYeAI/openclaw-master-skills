import { Command } from "commander";
import { loadGlobalConfig } from "../utils/config.js";
import { log } from "../utils/output.js";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import yaml from "js-yaml";

export function registerConfigCommand(program: Command): void {
  const config = program.command("config").description("Manage global configuration");

  config
    .command("list")
    .description("List all configuration values")
    .action(() => {
      try {
        const globalConfig = loadGlobalConfig();
        log.info("Current Configuration:");
        console.log(JSON.stringify(globalConfig, null, 2));
      } catch (error) {
        log.error(`Failed to load config: ${(error as Error).message}`);
      }
    });

  config
    .command("get <key>")
    .description("Get a specific configuration value")
    .action((key) => {
      try {
        const globalConfig = loadGlobalConfig();
        const value = key.split(".").reduce((obj: any, k: string) => obj && obj[k], globalConfig);
        if (value !== undefined) {
          console.log(value);
        } else {
          log.warn(`Key "${key}" not found.`);
        }
      } catch (error) {
        log.error(`Failed to get config: ${(error as Error).message}`);
      }
    });

  config
    .command("set <key> <value>")
    .description("Set a configuration value")
    .action((key, value) => {
      try {
        // Load existing config or create empty
        const configPath = path.join(os.homedir(), ".eval-skills", "config.yaml");
        let currentConfig: any = {};
        
        if (fs.existsSync(configPath)) {
            const fileContent = fs.readFileSync(configPath, "utf8");
            currentConfig = yaml.load(fileContent) || {};
        } else {
            // Ensure directory exists
            const configDir = path.dirname(configPath);
            if (!fs.existsSync(configDir)) {
                fs.mkdirSync(configDir, { recursive: true });
            }
        }

        // Set value (deep set)
        const keys = key.split(".");
        let current = currentConfig;
        for (let i = 0; i < keys.length - 1; i++) {
            if (!current[keys[i]]) current[keys[i]] = {};
            current = current[keys[i]];
        }
        
        // Try to parse value as JSON (for numbers, booleans, etc.)
        try {
            current[keys[keys.length - 1]] = JSON.parse(value);
        } catch {
            current[keys[keys.length - 1]] = value;
        }

        // Write back
        fs.writeFileSync(configPath, yaml.dump(currentConfig));
        log.success(`Configuration updated: ${key} = ${value}`);
        
      } catch (error) {
        log.error(`Failed to set config: ${(error as Error).message}`);
      }
    });
}
