import { describe, it, expect, vi, beforeEach } from "vitest";
import { log, printTable } from "./output.js";
import { logger } from "@eval-skills/core";

// Mock logger from core
vi.mock("@eval-skills/core", () => ({
  logger: {
    info: vi.fn(),
    error: vi.fn(),
    warn: vi.fn(),
    debug: vi.fn(),
  },
}));

describe("output utils", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(console, "log").mockImplementation(() => {});
    vi.spyOn(console, "error").mockImplementation(() => {});
  });

  it("should have log methods", () => {
    log.info("info");
    expect(console.log).toHaveBeenCalled();
    
    log.error("error");
    expect(console.error).toHaveBeenCalled();
  });

  it("should print table", () => {
    printTable(["Header 1", "Header 2"], [["Row 1 Col 1", "Row 1 Col 2"]]);
    expect(console.log).toHaveBeenCalled();
  });
  
  it("should support json output mode", () => {
      log.json = true;
      log.info("test");
      // Expect pino logger to be called, not console.log
      expect(logger.info).toHaveBeenCalledWith({}, "test");
      
      printTable(["H"], [["R"]]);
      // printTable still uses console.log for json mode in current implementation?
      // Let's check output.ts:
      // if (log.json) { console.log(JSON.stringify({ table: { headers, rows } })); return; }
      // Yes, printTable uses console.log directly for json output.
      expect(console.log).toHaveBeenCalledWith(expect.stringContaining('"table"'));
      
      log.json = false; // Reset
  });
});
