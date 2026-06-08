import Database from "better-sqlite3";
import { readFileSync, mkdirSync, readdirSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DB_PATH = process.env.MC_DB_PATH || join(__dirname, "..", "data", "mission-control.db");

let db;

export function getDb() {
  if (db) return db;

  mkdirSync(dirname(DB_PATH), { recursive: true });
  db = new Database(DB_PATH);
  db.pragma("journal_mode = WAL");
  db.pragma("foreign_keys = ON");

  // Run all migrations in order
  const migrationsDir = join(__dirname, "..", "migrations");
  const files = readdirSync(migrationsDir).filter(f => f.endsWith(".sql")).sort();
  for (const file of files) {
    const sql = readFileSync(join(migrationsDir, file), "utf-8");
    db.exec(sql);
  }

  console.log(`[db] SQLite initialized at ${DB_PATH} (${files.length} migrations)`);
  return db;
}
