#!/bin/bash
# Run a low-frequency reconciliation watcher.
# Usage:
#   bash ~/skills/team-dispatch/scripts/watch.sh
#   INTERVAL=300 GRACE=20 bash ~/skills/team-dispatch/scripts/watch.sh
#   NOTIFY=0 bash ~/skills/team-dispatch/scripts/watch.sh  # 禁用通知

set -e

INTERVAL=${INTERVAL:-300}
GRACE=${GRACE:-20}
NOTIFY=${NOTIFY:-1}  # 默认开启通知

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

NOTIFY_ARG=""
if [ "$NOTIFY" = "1" ]; then
    NOTIFY_ARG="--notify"
else
    NOTIFY_ARG="--no-notify"
fi

echo "[$(date '+%Y-%m-%dT%H:%M:%S')] Watcher starting..."
echo "  INTERVAL=$INTERVAL, GRACE=$GRACE, NOTIFY=$NOTIFY"
echo "  SKILL_DIR=$SKILL_DIR"

python3 "$SKILL_DIR/scripts/watch.py" --interval "$INTERVAL" --grace "$GRACE" $NOTIFY_ARG
