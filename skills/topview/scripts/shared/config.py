"""Load Topview API credentials.

Priority order:
1. Environment variables TOPVIEW_UID + TOPVIEW_API_KEY  (CI / backwards compat)
2. Credential file ~/.topview/credentials.json           (set by auth.py login)
3. Error — prompts user to run auth.py login
"""

import json
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

CRED_FILE = Path.home() / ".topview" / "credentials.json"


def _load_from_file() -> dict | None:
    """Read uid and api_key from the local credentials file, or return None."""
    if not CRED_FILE.exists():
        return None
    try:
        data = json.loads(CRED_FILE.read_text())
        uid = data.get("uid", "").strip()
        api_key = data.get("api_key", "").strip()
        if uid and api_key:
            return {"uid": uid, "api_key": api_key}
    except (json.JSONDecodeError, OSError):
        pass
    return None


def load_config() -> dict:
    """Return a dict with uid and api_key, or exit with a helpful error message."""
    # Priority 1: environment variables
    uid = os.environ.get("TOPVIEW_UID", "").strip()
    api_key = os.environ.get("TOPVIEW_API_KEY", "").strip()

    if uid and api_key:
        return {"uid": uid, "api_key": api_key}

    # Priority 2: credential file set by auth.py login
    creds = _load_from_file()
    if creds:
        return creds

    # Priority 3: error with actionable message
    missing_env = []
    if not uid:
        missing_env.append("TOPVIEW_UID")
    if not api_key:
        missing_env.append("TOPVIEW_API_KEY")

    print(
        "Error: Topview credentials not found.\n\n"
        "Option 1 — Log in with the auth module (recommended):\n"
        "  python scripts/auth.py login   # opens browser for authorization\n"
        "  python scripts/auth.py poll    # saves credentials after approval\n\n"
        "Option 2 — Set environment variables manually (for CI/scripting):\n"
        '  export TOPVIEW_UID="<your-topview-uid>"\n'
        '  export TOPVIEW_API_KEY="<your-api-key>"\n',
        file=sys.stderr,
    )
    sys.exit(1)
