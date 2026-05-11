"""Wahoo OAuth2 token management.

Loads client credentials from env (WAHOO_CLIENT_ID, WAHOO_CLIENT_SECRET,
WAHOO_REDIRECT_URI), persists tokens to ~/.openclaw/secrets/wahoo_tokens.json
(mode 0600), and auto-refreshes the access token when the API returns 401.
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

OAUTH_AUTHORIZE_URL = "https://api.wahooligan.com/oauth/authorize"
OAUTH_TOKEN_URL = "https://api.wahooligan.com/oauth/token"

DEFAULT_SCOPES = "workouts_read offline_data user_read"
DEFAULT_REDIRECT_URI = "https://localhost:8080/"

TOKENS_PATH = Path(os.path.expanduser("~/.openclaw/secrets/wahoo_tokens.json"))
DEFAULT_ENV_FILE = Path(os.path.expanduser("~/.openclaw/secrets/wahoo.env"))


class WahooAuthError(RuntimeError):
    pass


def _maybe_load_dotenv() -> None:
    """Populate WAHOO_* env vars from ~/.openclaw/secrets/wahoo.env (or
    $WAHOO_ENV_FILE) if they aren't already set. No-op if the file is missing
    or all needed vars are already in os.environ. Lets agents (e.g. Puck)
    invoke the skill without having to source the env file in their shell.
    """
    if os.environ.get("WAHOO_CLIENT_ID") and os.environ.get("WAHOO_CLIENT_SECRET"):
        return
    env_path = Path(
        os.environ.get("WAHOO_ENV_FILE", str(DEFAULT_ENV_FILE))
    ).expanduser()
    if not env_path.exists():
        return
    try:
        text = env_path.read_text()
    except OSError:
        return
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if key.startswith("WAHOO_") and key not in os.environ:
            os.environ[key] = value


def _client_credentials() -> tuple[str, str, str, str]:
    _maybe_load_dotenv()
    client_id = os.environ.get("WAHOO_CLIENT_ID")
    client_secret = os.environ.get("WAHOO_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise WahooAuthError(
            "Set WAHOO_CLIENT_ID and WAHOO_CLIENT_SECRET in env, in "
            "~/.openclaw/secrets/wahoo.env, or in ~/.clawdbot/clawdbot.json"
        )
    redirect_uri = os.environ.get("WAHOO_REDIRECT_URI", DEFAULT_REDIRECT_URI)
    scopes = os.environ.get("WAHOO_SCOPES", DEFAULT_SCOPES)
    return client_id, client_secret, redirect_uri, scopes


def authorize_url() -> str:
    client_id, _, redirect_uri, scopes = _client_credentials()
    qs = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scopes,
            "response_type": "code",
        }
    )
    return f"{OAUTH_AUTHORIZE_URL}?{qs}"


def _post_form(url: str, data: dict) -> dict:
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise WahooAuthError(f"OAuth HTTP {e.code}: {detail}") from None
    return payload


def exchange_code(code: str) -> dict:
    client_id, client_secret, redirect_uri, _ = _client_credentials()
    payload = _post_form(
        OAUTH_TOKEN_URL,
        {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        },
    )
    _save_tokens(payload)
    return payload


def refresh(refresh_token: Optional[str] = None) -> dict:
    client_id, client_secret, _, _ = _client_credentials()
    if refresh_token is None:
        tokens = load_tokens()
        refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        raise WahooAuthError(
            "No refresh_token on file — re-run scripts/oauth_setup.py"
        )
    payload = _post_form(
        OAUTH_TOKEN_URL,
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    _save_tokens(payload)
    return payload


def _save_tokens(payload: dict) -> None:
    TOKENS_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = dict(payload)
    if "expires_in" in record:
        record["expires_at"] = int(time.time()) + int(record["expires_in"])
    with open(TOKENS_PATH, "w") as f:
        json.dump(record, f, indent=2)
    os.chmod(TOKENS_PATH, 0o600)


def load_tokens() -> dict:
    if not TOKENS_PATH.exists():
        return {}
    with open(TOKENS_PATH) as f:
        return json.load(f)


def access_token() -> str:
    """Return a valid access token, refreshing if expired."""
    env_token = os.environ.get("WAHOO_ACCESS_TOKEN")
    if env_token and not TOKENS_PATH.exists():
        return env_token
    tokens = load_tokens()
    token = tokens.get("access_token")
    expires_at = tokens.get("expires_at", 0)
    if not token:
        raise WahooAuthError(
            "No access_token on file — run scripts/oauth_setup.py"
        )
    if expires_at and expires_at - 60 < time.time():
        tokens = refresh(tokens.get("refresh_token"))
        token = tokens["access_token"]
    return token


def _redacted_status() -> dict:
    """Return token-file metadata without exposing token values."""
    t = load_tokens()
    if not t:
        return {"present": False, "path": str(TOKENS_PATH)}
    expires_at = t.get("expires_at")
    return {
        "present": True,
        "path": str(TOKENS_PATH),
        "has_access_token": bool(t.get("access_token")),
        "has_refresh_token": bool(t.get("refresh_token")),
        "expires_at": expires_at,
        "expires_in_s": (expires_at - int(time.time())) if expires_at else None,
        "scope": t.get("scope"),
        "token_type": t.get("token_type"),
    }


if __name__ == "__main__":
    # Never dump raw tokens to stdout/logs. Print redacted status only.
    print(json.dumps(_redacted_status(), indent=2))
