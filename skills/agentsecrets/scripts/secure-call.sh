#!/usr/bin/env bash
# SECURITY MANIFEST
# =================
# Environment variables accessed: None
# External endpoints called: User-specified URL (first argument)
# Local files read: OS keychain (via agentsecrets binary, not directly)
# Local files written: ~/.agentsecrets/proxy.log (audit trail, key names only)
# Network: Outbound HTTPS to first argument URL only
# =================

set -euo pipefail

# Usage: secure-call.sh <url> [--method METHOD] [--bearer KEY] [--header Name=KEY] ...
# Passes all arguments directly to agentsecrets call.
# This wrapper exists to provide the SECURITY MANIFEST for ClawHub scanning.

if ! command -v agentsecrets &>/dev/null; then
    echo "ERROR: agentsecrets not installed. Run: pip install agentsecrets"
    exit 1
fi

# Validate at least a URL is provided
if [ $# -lt 1 ]; then
    echo "Usage: secure-call.sh --url <URL> --bearer <KEY_NAME> [options]"
    echo ""
    echo "All arguments are passed to 'agentsecrets call'."
    echo "Run 'agentsecrets call --help' for full options."
    exit 1
fi

# Sanitize: reject arguments containing shell metacharacters
for arg in "$@"; do
    if [[ "$arg" =~ [\;\|\&\$\`\(] ]]; then
        echo "ERROR: Invalid character detected in argument. Aborting for safety."
        exit 1
    fi
done

# Pass through to agentsecrets call
exec agentsecrets call "$@"
