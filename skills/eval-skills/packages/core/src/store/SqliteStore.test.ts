import { SqliteStore } from "./SqliteStore.js";
import type { Skill, TaskResult } from "../types/index.js";
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { tmpdir } from "node:os";
import Database from "better-sqlite3";

// Mock better-sqlite3
const mockPrepare = vi.fn();
const mockRun = vi.fn();
const mockGet = vi.fn();
const mockAll = vi.fn();
const mockExec = vi.fn();
const mockClose = vi.fn();

vi.mock("better-sqlite3", () => {
  return {
    default: vi.fn().mockImplementation(() => ({
      prepare: mockPrepare.mockImplementation(() => ({
        run: mockRun,
        get: mockGet,
        all: mockAll,
      })),
      exec: mockExec,
      close: mockClose,
    })),
  };
});

describe("SqliteStore", () => {
  let store: SqliteStore;
  let tmpDir: string;
  let dbPath: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(tmpdir(), "sqlite-store-test-"));
    dbPath = path.join(tmpDir, "test.db");
    
    // Pass the mocked Database constructor
    store = new SqliteStore(dbPath, Database);
    
    vi.clearAllMocks();
  });

  afterEach(() => {
    store.close();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it("should save and retrieve skills", () => {
    const skill: Skill = {
      id: "s1",
      name: "Skill 1",
      version: "1.0",
      description: "desc",
      tags: [],
      adapterType: "http",
      entrypoint: "url",
      inputSchema: {},
      outputSchema: {},
      metadata: {},
    };

    // Mock get return
    mockGet.mockReturnValue({ data: JSON.stringify(skill) });

    store.saveSkill(skill);
    expect(mockPrepare).toHaveBeenCalledWith(expect.stringContaining("INSERT INTO skills"));
    expect(mockRun).toHaveBeenCalled();

    const retrieved = store.getSkill("s1");
    expect(retrieved).toEqual(skill);
  });

  it("should create evaluation and save task results", () => {
    store.createEvaluation("eval-1", "s1", "bench-1");
    expect(mockPrepare).toHaveBeenCalledWith(expect.stringContaining("INSERT INTO evaluations"));
    
    const result: TaskResult = {
      taskId: "t1",
      skillId: "s1",
      status: "pass",
      score: 1.0,
      latencyMs: 100,
      scorerType: "exact",
    };

    // Mock hasTaskResult return
    mockGet.mockReturnValue({ "1": 1 }); // SELECT 1 FROM ...
    
    // Mock getTaskResults return
    mockAll.mockReturnValue([{ data: JSON.stringify(result) }]);

    store.saveTaskResult("eval-1", result);
    expect(mockPrepare).toHaveBeenCalledWith(expect.stringContaining("INSERT INTO task_results"));

    const results = store.getTaskResults("eval-1");
    
    expect(results).toHaveLength(1);
    expect(results[0]).toEqual(result);
    
    // Test hasTaskResult
    mockGet.mockReturnValueOnce({ "1": 1 });
    expect(store.hasTaskResult("eval-1", "t1")).toBe(true);
    
    mockGet.mockReturnValueOnce(undefined);
    expect(store.hasTaskResult("eval-1", "t2")).toBe(false);
  });
});
