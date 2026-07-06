import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { loadGlobalConfig, buildEvalConfig } from "./config.js";
import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";

vi.mock("node:fs");
vi.mock("node:os");

describe("config", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("loadGlobalConfig", () => {
    it("should return default config if no file found", () => {
      (fs.existsSync as any).mockReturnValue(false);
      (os.homedir as any).mockReturnValue("/home/user");
      
      const config = loadGlobalConfig();
      expect(config.concurrency).toBe(4); // Default is 4
    });

    it("should load from specific path if provided", () => {
      (fs.readFileSync as any).mockReturnValue('{"concurrency": 10}');
      
      const config = loadGlobalConfig("custom.json");
      expect(config.concurrency).toBe(10);
    });

    it("should try current directory config files", () => {
      (fs.existsSync as any).mockImplementation((p: string) => p.includes("eval-skills.config.json"));
      (fs.readFileSync as any).mockReturnValue('{"concurrency": 2}');
      
      const config = loadGlobalConfig();
      expect(config.concurrency).toBe(2);
    });
  });

  describe("buildEvalConfig", () => {
    it("should merge cli opts with global config", () => {
      const globalConfig = { concurrency: 5, timeoutMs: 1000, outputDir: "out", defaultFormats: ["json"] };
      const opts = {
          skills: ["s1"],
          benchmark: "b1",
          concurrency: 10,
          timeout: 2000,
          outputDir: "custom_out",
          format: ["md"],
          exitOnFail: true,
          minCompletion: 0.9,
      };

      const evalConfig = buildEvalConfig(opts, globalConfig as any);
      
      expect(evalConfig.concurrency).toBe(10);
      expect(evalConfig.timeoutMs).toBe(2000);
      expect(evalConfig.output.dir).toBe("custom_out");
      expect(evalConfig.output.formats).toEqual(["md"]);
      expect(evalConfig.exitOnFail?.minCompletionRate).toBe(0.9);
    });
  });
});
