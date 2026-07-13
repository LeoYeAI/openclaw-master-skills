#!/usr/bin/env bash
#
# Flirting Bots Webhook Receiver
#
# A lightweight webhook receiver that listens for Flirting Bots events,
# verifies HMAC-SHA256 signatures, and writes payloads to a spool directory
# for OpenClaw to pick up.
#
# Usage:
#   FLIRTINGBOTS_WEBHOOK_SECRET="your-secret" ./webhook-server.sh [port]
#
# Defaults to port 9876. Events are written to ~/.flirtingbots/events/.
#
# Requirements: python3, openssl

set -euo pipefail

PORT="${1:-9876}"
EVENTS_DIR="${HOME}/.flirtingbots/events"
SECRET="${FLIRTINGBOTS_WEBHOOK_SECRET:-}"

if [ -z "$SECRET" ]; then
  echo "Error: FLIRTINGBOTS_WEBHOOK_SECRET is not set" >&2
  exit 1
fi

mkdir -p "$EVENTS_DIR"

echo "Flirting Bots webhook receiver listening on port $PORT"
echo "Events will be written to $EVENTS_DIR"
echo "Press Ctrl+C to stop."

# Use Python's http.server for a simple, reliable HTTP listener
python3 -c "
import http.server
import json
import hmac
import hashlib
import os
import sys
from datetime import datetime

PORT = int(sys.argv[1])
EVENTS_DIR = sys.argv[2]
SECRET = sys.argv[3]

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        # Verify signature (header name is a legacy artifact)
        signature = self.headers.get('X-FlirtingClaws-Signature', '')
        expected = hmac.new(
            SECRET.encode(), body, hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{\"error\": \"Invalid signature\"}')
            print(f'  -> Rejected: invalid signature')
            return

        # Parse and write event
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{\"error\": \"Invalid JSON\"}')
            return

        event_type = self.headers.get('X-FlirtingClaws-Event', 'unknown')
        known_events = {'new_match', 'new_message', 'match_accepted', 'spark_detected', 'handoff', 'conversation_ended', 'queue_exhausted'}
        if event_type not in known_events:
            print(f'  -> Warning: unknown event type: {event_type}')
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
        filename = f'{timestamp}_{event_type}.json'
        filepath = os.path.join(EVENTS_DIR, filename)

        with open(filepath, 'w') as f:
            json.dump(payload, f, indent=2)

        print(f'  -> {event_type}: {payload.get(\"matchId\", \"?\")} -> {filename}')

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{\"ok\": true}')

    def log_message(self, format, *args):
        # Suppress default access log; we print our own
        pass

server = http.server.HTTPServer(('0.0.0.0', PORT), WebhookHandler)
print(f'Listening on 0.0.0.0:{PORT}...')
try:
    server.serve_forever()
except KeyboardInterrupt:
    print('\nShutting down.')
    server.server_close()
" "$PORT" "$EVENTS_DIR" "$SECRET"
