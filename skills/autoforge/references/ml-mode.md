# ML Mode — Advanced Usage

Autonomous ML training: the agent modifies `train.py`, trains for N minutes, checks `val_bpb`, keeps or discards.

This mode extends autoforge beyond prompt/code/audit into real machine learning experimentation. The same TSV tracking, stop conditions, and reporting infrastructure applies.

## Prerequisites

- macOS with Apple Silicon (M1/M2/M3/M4) or Linux with GPU
- Python 3.10+ with `uv` package manager
- Git for experiment version control

## Setup (one-time)

```bash
# 1. Clone the macOS-optimized fork
git clone https://github.com/miolini/autoresearch-macos
cd autoresearch-macos

# 2. Install uv (if not present)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Install dependencies
uv sync

# 4. Prepare data (~2 min, one-time)
uv run prepare.py
```

## Starting an Experiment

```bash
# Create branch for this run
git checkout -b autoresearch/$(date +%b%d | tr '[:upper:]' '[:lower:]')

# Initialize results tracking
echo -e "commit\tval_bpb\tmemory_gb\tstatus\tdescription" > results.tsv

# Point your coding agent at the repo:
# "Read program.md and start a new experiment loop."
```

## Agent Instructions

```
Read program.md in this repo and start the experiment loop.
- Only modify train.py
- Execute each run with: uv run train.py > run.log 2>&1
- Extract metric: grep "^val_bpb:" run.log
- Log result in results.tsv
- On improvement (lower val_bpb): keep git commit
- On equal or worse result: git reset back
- LOOP FOREVER — do not ask whether to continue
```

## Expected Performance

| Hardware | Experiments/Hour |
|----------|-----------------|
| H100 | ~12 |
| M2/M3/M4 Max | ~2–4 |
| M1/M2 | ~1–2 |

## Hyperparameter Tips for Mac (smaller models)

For Apple Silicon, start with conservative settings:

- Dataset: TinyStories instead of full dataset
- `vocab_size`: 2048–4096 instead of 8192
- `DEPTH`: 4 instead of 8
- `MAX_SEQ_LEN`: 256–512
- `WINDOW_PATTERN`: only "L" (no "SSSL")
- `TOTAL_BATCH_SIZE`: 2^14 (~16K)

## Viewing Results

```bash
# Pretty-print results
cat results.tsv | column -t -s $'\t'

# Generate progress chart
python3 scripts/visualize.py results.tsv --title "ML Experiment"
```

## Preventing Sleep During Training

```bash
# macOS: prevent sleep while loop runs
caffeinate -i &
CAFE_PID=$!
# After the run: kill $CAFE_PID

# Linux: use systemd-inhibit or screen/tmux
systemd-inhibit --what=idle uv run train.py
```

## Integration with AutoForge

ML mode integrates with the standard autoforge infrastructure:

1. **TSV tracking** — Same format, `val_bpb` maps to `pass_rate` (inverted: lower is better)
2. **Reporting** — `report.sh` works unchanged, showing progress bars
3. **Stop conditions** — Same convergence rules apply (adapt for minimization)
4. **Visualization** — `visualize.py` charts the training curve

To adapt stop conditions for minimization (lower = better):
- `improved` = val_bpb is **lower** than previous best
- `retained` = val_bpb is equal
- `discard` = val_bpb is higher
