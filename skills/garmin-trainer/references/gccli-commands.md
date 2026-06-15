# gccli Command Reference

All commands that the garmin-trainer skill uses. Always use `--json` when parsing output programmatically.

## Table of Contents

- [Data Gathering](#data-gathering)
- [Workout Creation — Running (Pace Mode)](#workout-creation--running-pace-mode)
- [Workout Creation — Running (HR Mode)](#workout-creation--running-hr-mode)
- [Workout Creation — Cycling (Always Power)](#workout-creation--cycling-always-power)
- [Workout Creation — Strength & Mobility](#workout-creation--strength--mobility)
- [Scheduling & Cleanup](#scheduling--cleanup)

## Data Gathering

### Events and existing schedule

```bash
gccli events list --json
gccli workouts schedule list --start <today> --end <today+84d> --json
```

### Recent training (last 4-6 weeks)

```bash
gccli activities list --limit 50 --json
gccli activities search --start-date <6-weeks-ago> --end-date <today> --json
```

### Current fitness and recovery

```bash
gccli health training-status --json
gccli health training-readiness --json
gccli health max-metrics --json
gccli health hrv --json
gccli health rhr --json
gccli health sleep --json
```

### Performance benchmarks

```bash
gccli health lactate-threshold
gccli health cycling-ftp
```

### Activity details (for key recent activities, last 2-3 per sport)

```bash
gccli activity splits <id> --json
gccli activity hr-zones <id> --json
```

## Workout Creation — Running (Pace Mode)

Pace targets use min:sec per km format.

### Easy run

```bash
gccli workouts create "W1 Easy Run 45min" --type run \
  --step "warmup:5m" \
  --step "run:35m@pace:5:30-6:00" \
  --step "cooldown:5m"
```

### Tempo run

```bash
gccli workouts create "W3 Tempo Run" --type run \
  --step "warmup:10m" \
  --step "run:20m@pace:4:40-4:55" \
  --step "cooldown:10m"
```

### Interval session

```bash
gccli workouts create "W5 5x1km Intervals" --type run \
  --step "warmup:10m" \
  --step "run:4m@pace:4:00-4:15" \
  --step "recovery:2m" \
  --step "run:4m@pace:4:00-4:15" \
  --step "recovery:2m" \
  --step "run:4m@pace:4:00-4:15" \
  --step "recovery:2m" \
  --step "run:4m@pace:4:00-4:15" \
  --step "recovery:2m" \
  --step "run:4m@pace:4:00-4:15" \
  --step "cooldown:10m"
```

### Long run

```bash
gccli workouts create "W4 Long Run 90min" --type run \
  --step "warmup:10m" \
  --step "run:70m@pace:5:20-5:50" \
  --step "cooldown:10m"
```

## Workout Creation — Running (HR Mode)

HR targets use bpm ranges.

### Easy run

```bash
gccli workouts create "W1 Easy Run 45min" --type run \
  --step "warmup:5m" \
  --step "run:35m@hr:130-145" \
  --step "cooldown:5m"
```

### Tempo run

```bash
gccli workouts create "W3 Tempo Run" --type run \
  --step "warmup:10m" \
  --step "run:20m@hr:160-172" \
  --step "cooldown:10m"
```

### Interval session

```bash
gccli workouts create "W5 5x1km Intervals" --type run \
  --step "warmup:10m" \
  --step "run:4m@hr:172-185" \
  --step "recovery:2m" \
  --step "run:4m@hr:172-185" \
  --step "recovery:2m" \
  --step "run:4m@hr:172-185" \
  --step "recovery:2m" \
  --step "run:4m@hr:172-185" \
  --step "recovery:2m" \
  --step "run:4m@hr:172-185" \
  --step "cooldown:10m"
```

### Long run

```bash
gccli workouts create "W4 Long Run 90min" --type run \
  --step "warmup:10m" \
  --step "run:70m@hr:135-150" \
  --step "cooldown:10m"
```

## Workout Creation — Cycling (Always Power)

Cycling always uses power targets in watts, regardless of the running target mode.

### Endurance ride

```bash
gccli workouts create "W2 Endurance Ride 2h" --type bike \
  --step "warmup:10m" \
  --step "run:100m@power:150-190" \
  --step "cooldown:10m"
```

### FTP intervals

```bash
gccli workouts create "W6 FTP Intervals 4x8min" --type bike \
  --step "warmup:15m" \
  --step "run:8m@power:240-260" \
  --step "recovery:4m" \
  --step "run:8m@power:240-260" \
  --step "recovery:4m" \
  --step "run:8m@power:240-260" \
  --step "recovery:4m" \
  --step "run:8m@power:240-260" \
  --step "cooldown:10m"
```

## Workout Creation — Strength & Mobility

### Strength session

```bash
gccli workouts create "W3 Strength: Full Body" --type strength \
  --step "warmup:5m" \
  --step "run:35m" \
  --step "cooldown:5m"
```

### Mobility / Yoga session

```bash
gccli workouts create "W3 Mobility & Stretching" --type yoga \
  --step "warmup:5m" \
  --step "run:20m" \
  --step "cooldown:5m"
```

## Scheduling & Cleanup

### Schedule a workout

After creating a workout, capture the workout ID from the JSON output, then:

```bash
gccli workouts schedule add <workout-id> <YYYY-MM-DD>
```

### List scheduled workouts

```bash
gccli workouts schedule list --start <today> --end <today+84d> --json
```

### Remove skill-managed workouts (W-prefix)

Remove automatically without confirmation — these are skill-created:

```bash
gccli workouts schedule remove <schedule-id> --force
```

### Naming convention

Prefix all workout names with the week number: `W1`, `W2`, ... `W12`.

Include the session purpose and key metric:
- `W3 Tempo Run 25min @4:45`
- `W5 Long Run 16km`
- `W8 FTP Intervals 5x6min`
- `W2 Strength: Full Body`
- `W4 Mobility & Stretching`
