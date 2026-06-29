# Athlete Assessment Commands

Use these CLI commands to generate assessment data. Raw SQL access remains available via `query` for advanced use.

This works on any Node.js version (uses built-in SQLite on Node 22.5+, falls back to CLI otherwise).

## Current Form

```bash
npx -y endurance-coach@latest stats --weeks 8 --longest-weeks 12
```

Includes weekly volume, longest recent sessions, and average session duration.

Options:

- `--weeks N` (default: 8)
- `--longest-weeks N` (default: 12)
- `--json`

## Training Load Trend

```bash
npx -y endurance-coach@latest training-load --weeks 12
```

Options:

- `--weeks N` (default: 12)
- `--json`

## Athletic Foundation

```bash
npx -y endurance-coach@latest foundation --top-weeks 5
```

Includes race history, lifetime peaks, peak training weeks, and training history depth.

Options:

- `--top-weeks N` (default: 5)
- `--json`

## Strength Signals

```bash
npx -y endurance-coach@latest strength --months 6 --long-months 12 --easy-hr-max 145 --long-minutes 60 --years 2
```

Includes efficiency, aerobic strength, dormant skills, and historical peaks.

Options:

- `--months N` (default: 6)
- `--long-months N` (default: 12)
- `--easy-hr-max N` (default: 145)
- `--long-minutes N` (default: 60)
- `--years N` (default: 2)
- `--json`

## Schedule Preferences

```bash
npx -y endurance-coach@latest schedule-preferences --ride-minutes 90 --run-minutes 60
```

Options:

- `--ride-minutes N` (default: 90)
- `--run-minutes N` (default: 60)
- `--json`

## HR / Zone Data

```bash
npx -y endurance-coach@latest hr-zones --weeks 8 --distribution-weeks 12
```

Options:

- `--weeks N` (default: 8)
- `--distribution-weeks N` (default: 12)
- `--json`

## Activity Details (Laps/Analysis)

```bash
npx -y endurance-coach@latest activity <id> --laps
```

Fetches lap data from Strava for detailed interval analysis and pacing consistency.

## Advanced: Raw SQL

```bash
npx -y endurance-coach@latest query "SELECT * FROM weekly_volume LIMIT 5" --json
```

## Schema Reference

See @reference/schema.md for a one-line-per-table schema overview.
