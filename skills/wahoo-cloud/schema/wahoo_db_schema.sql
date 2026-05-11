-- Wahoo Workout Database Schema
-- Location: ~/.openclaw/workspace/training/wahoo.db

CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY,             -- Wahoo workout ID
    name TEXT,                          -- workout title
    starts TEXT,                        -- ISO8601 (UTC) start time
    minutes INTEGER,                    -- duration (Wahoo's coarse "minutes" field)
    workout_type_id INTEGER,            -- 0=run, 40=indoor cycle, 41=outdoor cycle, 42=mtb, 60=swim, ...
    plan_id INTEGER,
    route_id INTEGER,
    workout_token TEXT,
    created_at TEXT,
    updated_at TEXT,

    -- workout_summary fields (cast to numeric on read)
    distance_m REAL,
    duration_active_s REAL,
    duration_paused_s REAL,
    duration_total_s REAL,
    ascent_m REAL,
    cadence_avg REAL,
    calories REAL,
    heart_rate_avg REAL,
    power_avg REAL,
    power_np REAL,                      -- power_bike_np_last
    power_tss REAL,                     -- power_bike_tss_last
    speed_avg_ms REAL,
    work_j REAL,
    time_zone TEXT,

    -- FIT artifact tracking
    fit_url TEXT,                       -- workout_summary.file.url (CDN)
    fit_path TEXT,                      -- local download path
    fit_parsed_at TEXT,                 -- when we last parsed it

    -- FIT-derived (filled by fit_parser)
    fit_total_distance_m REAL,
    fit_total_elapsed_s REAL,
    fit_total_timer_s REAL,
    fit_total_ascent_m REAL,
    fit_total_descent_m REAL,
    fit_avg_power_w REAL,
    fit_max_power_w REAL,
    fit_normalized_power_w REAL,
    fit_avg_heart_rate REAL,
    fit_max_heart_rate REAL,
    fit_avg_cadence REAL,
    fit_max_cadence REAL,
    fit_avg_speed_ms REAL,
    fit_max_speed_ms REAL,
    fit_calories REAL,
    fit_record_count INTEGER,

    synced TEXT DEFAULT '0000-00-00',
    fetched_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_workouts_starts ON workouts(starts);
CREATE INDEX IF NOT EXISTS idx_workouts_type ON workouts(workout_type_id);
CREATE INDEX IF NOT EXISTS idx_workouts_synced ON workouts(synced);

CREATE TABLE IF NOT EXISTS sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    synced_at TEXT DEFAULT (datetime('now')),
    workouts_seen INTEGER,
    workouts_new INTEGER,
    fit_downloaded INTEGER,
    status TEXT DEFAULT 'OK'            -- OK, ERROR, PARTIAL
);
