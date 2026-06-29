#!/bin/bash
# load-credentials.sh - Inject secrets to file/env/systemd targets
# Usage: ./load-credentials.sh <secrets.json>

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SECRETS_FILE="${1:-}"
BACKUP_DIR="$HOME/.amcp/backups/$(date +%Y%m%d-%H%M%S)"
AGENT_NAME="${AGENT_NAME:-ClaudiusThePirateEmperor}"
SYSTEMD_ENV_FILE="$HOME/.config/openclaw/env"

if [ -z "$SECRETS_FILE" ] || [ ! -f "$SECRETS_FILE" ]; then
  echo "Usage: $0 <secrets.json>"
  exit 1
fi

# Validate JSON before processing
if ! python3 -c "import json; json.load(open('$SECRETS_FILE'))" 2>/dev/null; then
  echo "ERROR: $SECRETS_FILE is not valid JSON"
  exit 1
fi

mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$SYSTEMD_ENV_FILE")"

[ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "🔄 [$AGENT_NAME] Injecting secrets..."

echo "=== Inject Secrets ==="
echo "Source: $SECRETS_FILE"
echo "Backup: $BACKUP_DIR"

# Process secrets with Python (bash-interpolated heredoc so $SECRETS_FILE etc. resolve)
python3 << PYEOF
import json
import os
import shutil
from pathlib import Path

secrets = json.load(open("$SECRETS_FILE"))
backup_dir = "$BACKUP_DIR"
systemd_env_file = "$SYSTEMD_ENV_FILE"

modified_files = set()
env_lines = []
systemd_env_lines = []
services_to_reload = set()

for secret in secrets:
    key = secret["key"]
    value = secret["value"]
    targets = secret.get("targets", [])
    
    for target in targets:
        kind = target["kind"]
        
        if kind == "file":
            path = os.path.expanduser(target["path"])
            json_path = target.get("jsonPath", "")
            
            if not os.path.exists(path):
                print(f"[SKIP] File not found: {path}")
                continue
            
            # Backup if not already backed up
            if path not in modified_files:
                backup_path = os.path.join(backup_dir, os.path.basename(path))
                shutil.copy2(path, backup_path)
                print(f"[BACKUP] {path} -> {backup_path}")
                modified_files.add(path)
            
            # Update JSON file
            with open(path) as f:
                data = json.load(f)
            
            # Navigate to jsonPath and set value
            parts = json_path.split(".")
            obj = data
            for part in parts[:-1]:
                if part not in obj:
                    obj[part] = {}
                obj = obj[part]
            obj[parts[-1]] = value
            
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            
            print(f"[FILE] {key} -> {path}:{json_path}")
        
        elif kind == "env":
            name = target.get("name", key)
            env_lines.append(f'export {name}="{value}"')
            print(f"[ENV] {name}")
        
        elif kind == "systemd":
            service = target.get("service", "openclaw-gateway")
            name = target.get("name", key)
            systemd_env_lines.append(f'{name}="{value}"')
            services_to_reload.add(service)
            print(f"[SYSTEMD] {name} -> {systemd_env_file}")

# Write env vars to bashrc if any
if env_lines:
    bashrc = os.path.expanduser("~/.bashrc")
    marker_start = "# AMCP-SECRETS-START"
    marker_end = "# AMCP-SECRETS-END"
    
    if bashrc not in modified_files:
        backup_path = os.path.join(backup_dir, ".bashrc")
        if os.path.exists(bashrc):
            shutil.copy2(bashrc, backup_path)
            print(f"[BACKUP] {bashrc} -> {backup_path}")
    
    content = ""
    if os.path.exists(bashrc):
        with open(bashrc) as f:
            content = f.read()
    
    if marker_start in content:
        start = content.index(marker_start)
        end = content.index(marker_end) + len(marker_end)
        content = content[:start] + content[end:]
    
    amcp_section = f"\n{marker_start}\n" + "\n".join(env_lines) + f"\n{marker_end}\n"
    content = content.rstrip() + amcp_section
    
    with open(bashrc, "w") as f:
        f.write(content)
    
    print(f"[ENV] Updated ~/.bashrc with {len(env_lines)} vars")

# Write systemd EnvironmentFile
if systemd_env_lines:
    os.makedirs(os.path.dirname(systemd_env_file), exist_ok=True)
    
    if os.path.exists(systemd_env_file):
        backup_path = os.path.join(backup_dir, "openclaw-env")
        shutil.copy2(systemd_env_file, backup_path)
        print(f"[BACKUP] {systemd_env_file} -> {backup_path}")
    
    with open(systemd_env_file, "w") as f:
        f.write("# AMCP-managed systemd environment\n")
        f.write("# DO NOT EDIT - managed by load-credentials.sh\n")
        f.write("\n".join(systemd_env_lines) + "\n")
    
    os.chmod(systemd_env_file, 0o600)
    
    print(f"[SYSTEMD] Wrote {len(systemd_env_lines)} vars to {systemd_env_file}")
    
    # Write services list for bash
    with open("/tmp/amcp-reload-services.txt", "w") as f:
        f.write("\n".join(services_to_reload))

print(f"\nInjected {len(secrets)} secrets")
PYEOF

# Reload systemd services if needed
if [ -f /tmp/amcp-reload-services.txt ]; then
  echo ""
  echo "=== Reloading systemd services ==="
  while read -r service; do
    if [ -n "$service" ]; then
      echo "Reloading: $service"
      # Try user service first, then system
      if systemctl --user is-active "$service" &>/dev/null; then
        systemctl --user daemon-reload
        systemctl --user restart "$service" && echo "  ✓ Restarted (user)" || echo "  ✗ Failed"
      elif systemctl is-active "$service" &>/dev/null; then
        sudo systemctl daemon-reload 2>/dev/null || true
        sudo systemctl restart "$service" && echo "  ✓ Restarted (system)" || echo "  ✗ Failed (may need sudo)"
      else
        echo "  ⚠ Service not active, skipping"
      fi
    fi
  done < /tmp/amcp-reload-services.txt
  rm -f /tmp/amcp-reload-services.txt
fi

[ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "✅ [$AGENT_NAME] Secrets injected"

echo ""
echo "=== Done ==="
echo ""
echo "NOTE: For systemd services to read the EnvironmentFile, ensure your service has:"
echo "  EnvironmentFile=%h/.config/openclaw/env"
echo ""
