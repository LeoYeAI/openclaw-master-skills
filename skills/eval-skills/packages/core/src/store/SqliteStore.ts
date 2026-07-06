import { createRequire } from "module";
import type { Skill, TaskResult, SkillCompletionReport } from "../types/index.js";
import path from "node:path";
import fs from "node:fs";

const require = createRequire(import.meta.url);
let Database: any;

// Mock Database class
class MockDatabase {
  constructor(_path: string) {}
  prepare() { 
    return { 
      run: () => {}, 
      get: () => undefined, 
      all: () => [] 
    }; 
  }
  exec() {}
  close() {}
}

try {
  Database = require("better-sqlite3");
} catch (e) {
  console.warn("⚠️  better-sqlite3 not found or failed to load. SqliteStore will be non-functional.");
  Database = MockDatabase;
}

/**
 * SQLite-based store for Skills and Evaluation Results.
 * 
 * Handles persistence for:
 * - Skills (metadata)
 * - Evaluations (metadata + summary)
 * - Task Results (individual task execution records)
 */
export class SqliteStore {
  private db: any;

  constructor(dbPath: string, DatabaseClass?: any) {
    // Ensure directory exists
    const dir = path.dirname(dbPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    try {
        const DB = DatabaseClass || Database;
        this.db = new DB(dbPath);
        this.initSchema();
    } catch (e) {
        console.error("Failed to initialize SQLite database (fallback to in-memory mock):", (e as Error).message);
        // Fallback to mock if instantiation fails (e.g. native binding error)
        this.db = new MockDatabase(dbPath); 
    }
  }

  private initSchema() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS skills (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        version TEXT NOT NULL,
        data JSON NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS evaluations (
        id TEXT PRIMARY KEY,
        skill_id TEXT NOT NULL,
        benchmark_id TEXT NOT NULL,
        summary JSON,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(skill_id) REFERENCES skills(id)
      );

      CREATE TABLE IF NOT EXISTS task_results (
        eval_id TEXT NOT NULL,
        task_id TEXT NOT NULL,
        skill_id TEXT NOT NULL,
        run_id INTEGER NOT NULL DEFAULT 1,
        status TEXT NOT NULL,
        score REAL NOT NULL,
        latency_ms INTEGER NOT NULL,
        data JSON NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (eval_id, task_id, run_id),
        FOREIGN KEY(eval_id) REFERENCES evaluations(id)
      );
      
      CREATE INDEX IF NOT EXISTS idx_task_results_eval_id ON task_results(eval_id);
      CREATE INDEX IF NOT EXISTS idx_evaluations_skill_id ON evaluations(skill_id);
      CREATE INDEX IF NOT EXISTS idx_evaluations_benchmark_id ON evaluations(benchmark_id);
      CREATE INDEX IF NOT EXISTS idx_task_results_skill_id ON task_results(skill_id);
      CREATE INDEX IF NOT EXISTS idx_evaluations_timestamp ON evaluations(timestamp);
    `);
  }

  /**
   * Save or update a skill
   */
  saveSkill(skill: Skill): void {
    const stmt = this.db.prepare(`
      INSERT INTO skills (id, name, version, data, updated_at)
      VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
      ON CONFLICT(id) DO UPDATE SET
        name = excluded.name,
        version = excluded.version,
        data = excluded.data,
        updated_at = CURRENT_TIMESTAMP
    `);
    
    stmt.run(skill.id, skill.name, skill.version, JSON.stringify(skill));
  }

  /**
   * Get a skill by ID
   */
  getSkill(id: string): Skill | undefined {
    const row = this.db.prepare("SELECT data FROM skills WHERE id = ?").get(id) as { data: string } | undefined;
    if (!row) return undefined;
    return JSON.parse(row.data);
  }

  /**
   * Find the latest evaluation for a skill and benchmark
   */
  findLatestEvaluation(skillId: string, benchmarkId: string): { id: string } | undefined {
    return this.db.prepare(`
      SELECT id FROM evaluations 
      WHERE skill_id = ? AND benchmark_id = ? 
      ORDER BY timestamp DESC LIMIT 1
    `).get(skillId, benchmarkId) as { id: string } | undefined;
  }

  /**
   * Get evaluation by ID
   */
  getEvaluation(id: string): any | undefined {
      return this.db.prepare("SELECT * FROM evaluations WHERE id = ?").get(id);
  }

  /**
   * Start a new evaluation session (or get existing if resuming)
   * 
   * For resume, we might want to find the latest evaluation for this skill+benchmark
   * that matches certain criteria, but for simplicity, we'll assume the caller
   * manages the eval ID or we generate a new one.
   */
  createEvaluation(id: string, skillId: string, benchmarkId: string): void {
    const stmt = this.db.prepare(`
      INSERT INTO evaluations (id, skill_id, benchmark_id)
      VALUES (?, ?, ?)
      ON CONFLICT(id) DO NOTHING
    `);
    stmt.run(id, skillId, benchmarkId);
  }

  /**
   * Update evaluation summary
   */
  updateEvaluationSummary(id: string, summary: any): void {
    const stmt = this.db.prepare(`
      UPDATE evaluations SET summary = ? WHERE id = ?
    `);
    stmt.run(JSON.stringify(summary), id);
  }

  /**
   * Save a task result
   */
  saveTaskResult(evalId: string, result: TaskResult): void {
    const runId = result.runId ?? 1;
    const stmt = this.db.prepare(`
      INSERT INTO task_results (eval_id, task_id, run_id, skill_id, status, score, latency_ms, data)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(eval_id, task_id, run_id) DO UPDATE SET
        status = excluded.status,
        score = excluded.score,
        latency_ms = excluded.latency_ms,
        data = excluded.data
    `);
    
    stmt.run(
      evalId,
      result.taskId,
      runId,
      result.skillId,
      result.status,
      result.score,
      result.latencyMs,
      JSON.stringify(result)
    );
  }

  /**
   * Get all task results for an evaluation
   */
  getTaskResults(evalId: string): TaskResult[] {
    const rows = this.db.prepare("SELECT data FROM task_results WHERE eval_id = ?").all(evalId) as { data: string }[];
    return rows.map(row => JSON.parse(row.data));
  }

  /**
   * Check if a task has been completed in an evaluation
   */
  hasTaskResult(evalId: string, taskId: string, runId: number = 1): boolean {
    const row = this.db.prepare("SELECT 1 FROM task_results WHERE eval_id = ? AND task_id = ? AND run_id = ?").get(evalId, taskId, runId);
    return !!row;
  }
  
  /**
   * Close the database connection
   */
  close() {
    this.db.close();
  }
}
