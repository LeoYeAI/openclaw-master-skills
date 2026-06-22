-- BrainX V5 Migration: Add missing tables to schema
-- Auto-generated from live DB inspection

-- Table: brainx_advisories
 CREATE TABLE IF NOT EXISTS brainx_advisories (+
   id TEXT NOT NULL,                           +
   agent TEXT,                                 +
   tool TEXT,                                  +
   action_context JSONB,                       +
   advisory_text TEXT NOT NULL,                +
   source_memory_ids TEXT[],                   +
   confidence REAL DEFAULT 0.5,                +
   was_followed BOOLEAN,                       +
   outcome TEXT,                               +
   created_at TIMESTAMPTZ DEFAULT now()        +
 );                                            +
 


-- Table: brainx_distillation_log
 CREATE TABLE IF NOT EXISTS brainx_distillation_log (+
   id TEXT NOT NULL,                                 +
   session_file TEXT NOT NULL,                       +
   memories_created INTEGER DEFAULT 0,               +
   memories_skipped INTEGER DEFAULT 0,               +
   processed_at TIMESTAMPTZ DEFAULT now()            +
 );                                                  +
 


-- Table: brainx_eidos_cycles
 CREATE TABLE IF NOT EXISTS brainx_eidos_cycles (+
   id TEXT NOT NULL,                             +
   agent TEXT,                                   +
   tool TEXT,                                    +
   project TEXT,                                 +
   context JSONB,                                +
   prediction TEXT NOT NULL,                     +
   predicted_outcome TEXT,                       +
   actual_outcome TEXT,                          +
   accuracy REAL,                                +
   evaluation_notes TEXT,                        +
   learning_memory_id TEXT,                      +
   status TEXT DEFAULT 'predicted'::text,        +
   created_at TIMESTAMPTZ DEFAULT now(),         +
   evaluated_at TIMESTAMPTZ,                     +
   distilled_at TIMESTAMPTZ                      +
 );                                              +
 


-- Add feedback_score column (exists in DB, missing from v3-schema.sql)
ALTER TABLE brainx_memories ADD COLUMN IF NOT EXISTS feedback_score INTEGER DEFAULT 0;
