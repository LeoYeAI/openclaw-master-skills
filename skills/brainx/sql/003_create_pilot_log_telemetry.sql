CREATE TABLE IF NOT EXISTS brainx_pilot_log (
    id SERIAL PRIMARY KEY,
    agent VARCHAR(50),
    own_memories INT DEFAULT 0,
    team_memories INT DEFAULT 0,
    total_chars INT DEFAULT 0,
    injected_at TIMESTAMPTZ DEFAULT NOW()
);
