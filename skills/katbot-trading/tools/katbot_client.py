"""
katbot_client.py — Katbot.ai API client for agents and CLI tools.

Supports two configuration modes:
1. Environment variables (for OpenClaw skills)
2. .env file (for tubman-bobtail-py CLI usage)

Features:
- SIWE authentication with JWT refresh
- Portfolio management (CRUD, tokens, timeseries, chain info)
- Agent management (CRUD, assignment, invitations)
- Recommendation workflow (request, poll, execute, response)
- Trade execution and position closing
- Conversation history management
- User and subscription info

IMPORTANT: ALWAYS include X-Agent-Private-Key header for Hyperliquid portfolio calls.
See MEMORY.md Katbot/Tubman Client Rule for details.

Portfolio types:
  HL_PAPER   — paper trading on Hyperliquid (no real funds, was "PAPER")
  HYPERLIQUID — live trading on Hyperliquid (agent key required)
"""
import base64
import json
import os
import time
import requests
from pathlib import Path
from eth_account import Account
from eth_account.messages import encode_defunct

# Configuration: support both env vars and .env file
BASE_URL = os.getenv("KATBOT_BASE_URL")
IDENTITY_DIR = os.getenv("KATBOT_IDENTITY_DIR")

# If not set via env vars, try loading from .env file (tubman-bobtail-py mode)
ENV_FILE = None

# 1. (user homedir)/katbot_client.env
# 2. (openclaw_home)/katbot_identity/katbot_client.env
if not BASE_URL or not IDENTITY_DIR:
    env_candidates = [
        Path(__file__).parent.parent.parent / "env" / "local" / "katbot_client.env",
        Path(__file__).parent.parent / "env" / "local" / "katbot_client.env",
        Path(__file__).parent / "katbot_client.env",
        Path.home() / "katbot_client.env",
    ]

    # Add the second candidate only if OPENCLAW_HOME is defined
    openclaw_home = os.environ.get("OPENCLAW_HOME")
    if openclaw_home:
        env_candidates.append(Path(openclaw_home) / "katbot_identity" / "katbot_client.env")


    for candidate in env_candidates:
        if candidate.exists():
            ENV_FILE = candidate
            break

    if ENV_FILE and ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"')
                    if key == "KATBOT_BASE_URL" and not BASE_URL:
                        BASE_URL = val
                    elif key == "KATBOT_IDENTITY_DIR" and not IDENTITY_DIR:
                        IDENTITY_DIR = val
                    elif key == "CHAIN_ID" and not os.getenv("CHAIN_ID"):
                        os.environ["CHAIN_ID"] = val
                    # WALLET_PRIVATE_KEY and KATBOT_HL_AGENT_PRIVATE_KEY are intentionally
                    # NOT loaded from .env files — private keys must be supplied via
                    # environment variables or the identity directory only.

# Default fallbacks
if not BASE_URL:
    BASE_URL = os.getenv("KATBOT_BASE_URL", "https://api.katbot.ai")
if not IDENTITY_DIR:
    IDENTITY_DIR = os.getenv("KATBOT_IDENTITY_DIR", os.path.expanduser("~/.openclaw/workspace/katbot-identity"))

# File paths
TOKEN_FILE = os.path.join(IDENTITY_DIR, "katbot_token.json")
SECRETS_FILE = os.path.join(IDENTITY_DIR, "katbot_secrets.json")
CONFIG_FILE = os.path.join(IDENTITY_DIR, "katbot_config.json")

# Load keys from env vars or secrets file
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")
AGENT_PRIVATE_KEY = os.getenv("KATBOT_HL_AGENT_PRIVATE_KEY")

# If agent key not in env, try loading from secrets file
if not AGENT_PRIVATE_KEY and os.path.exists(SECRETS_FILE):
    try:
        with open(SECRETS_FILE) as f:
            secrets = json.load(f)
            AGENT_PRIVATE_KEY = secrets.get("agent_private_key")
    except Exception:
        pass  # Fail silently if file is corrupt or unreadable

CHAIN_ID = int(os.getenv("CHAIN_ID", "42161"))


def get_config() -> dict:
    """Load configuration from the identity file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _jwt_expiry(token: str) -> float:
    """Decode JWT payload (no signature verification) and return exp as a Unix timestamp.
    Returns 0 if the token is malformed or has no exp claim."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return 0
        # Add padding so base64 decodes cleanly
        payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return float(payload.get("exp", 0))
    except Exception:
        return 0


def _token_is_valid(token: str, margin_seconds: int = 60) -> bool:
    """Return True if the token exists and won't expire within margin_seconds."""
    if not token:
        return False
    exp = _jwt_expiry(token)
    if exp == 0:
        return False  # can't determine expiry — treat as invalid
    return time.time() < (exp - margin_seconds)


def _refresh_access_token(refresh_token: str) -> str | None:
    """Exchange a refresh token for a new access token and refresh token.
    Both tokens are saved to disk. Returns the new access token, or None if refresh fails."""
    if not refresh_token:
        return None
    try:
        r = requests.post(
            f"{BASE_URL}/refresh",
            json={"refresh_token": refresh_token},
            timeout=15,
        )
        if r.status_code != 200:
            return None
        data = r.json()
        new_access = data.get("access_token", "")
        new_refresh = data.get("refresh_token", "")
        if not new_access or not new_refresh:
            return None
        os.makedirs(IDENTITY_DIR, exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            json.dump({"access_token": new_access, "refresh_token": new_refresh}, f, indent=2)
        try:
            os.chmod(TOKEN_FILE, 0o600)
        except Exception:
            pass
        return new_access
    except Exception:
        return None


def authenticate() -> str:
    """Perform SIWE login and return a fresh JWT. Saves token to disk."""
    if not WALLET_PRIVATE_KEY:
        raise ValueError(
            "\n❌ Session expired and WALLET_PRIVATE_KEY not set.\n"
            "   Please re-run the onboarding script to refresh your session:\n"
            "   python3 skills/katbot-trading/tools/katbot_onboard.py"
        )

    account = Account.from_key(WALLET_PRIVATE_KEY)
    address = account.address

    # Step 1: Get nonce
    r = requests.get(f"{BASE_URL}/get-nonce/{address}?chain_id={CHAIN_ID}")
    r.raise_for_status()
    message_text = r.json()["message"]

    # Step 2: Sign
    signable = encode_defunct(text=message_text)
    signed = Account.sign_message(signable, WALLET_PRIVATE_KEY)
    signature = signed.signature.hex()

    # Step 3: Login
    r = requests.post(f"{BASE_URL}/login", json={"address": address, "signature": signature, "chain_id": CHAIN_ID})
    r.raise_for_status()
    token_data = r.json()

    os.makedirs(IDENTITY_DIR, exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)
    try:
        os.chmod(TOKEN_FILE, 0o600)
    except Exception:
        pass

    return token_data["access_token"]


def get_token() -> str:
    """Return a valid access token, using refresh or re-auth as needed.

    Token resolution order:
    1. Use the saved access token if it is not yet expired.
    2. If expired, call POST /refresh with the saved refresh token.
       The API rotates the refresh token on every call, so both tokens are
       written to disk immediately before returning — the old refresh token
       is invalid the moment the response arrives.
    3. If refresh fails (token expired, revoked, or missing), fall back to
       full SIWE re-authentication via POST /login.
    """
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE) as f:
                data = json.load(f)
        except Exception:
            data = {}

        access_token = data.get("access_token", "")
        refresh_token = data.get("refresh_token", "")

        if _token_is_valid(access_token):
            return access_token

        # Access token expired — attempt refresh regardless of refresh token
        # expiry (refresh tokens may be opaque and lack a decodable exp claim).
        if refresh_token:
            new_token = _refresh_access_token(refresh_token)
            if new_token:
                return new_token

    return authenticate()


def _auth(token: str, agent_key: str = None) -> dict:
    """Build auth headers with optional agent private key.

    CRITICAL: ALWAYS include X-Agent-Private-Key for Hyperliquid portfolio calls.
    The API requires this header for all Hyperliquid portfolio endpoints.
    """
    headers = {"Authorization": f"Bearer {token}"}
    # Always include agent key if available - required for Hyperliquid portfolios
    if agent_key:
        headers["X-Agent-Private-Key"] = agent_key
    elif AGENT_PRIVATE_KEY:
        headers["X-Agent-Private-Key"] = AGENT_PRIVATE_KEY
    return headers


def _require_agent_key() -> str:
    """Require agent private key to be available, raising clear error if not."""
    if AGENT_PRIVATE_KEY:
        return AGENT_PRIVATE_KEY
    raise ValueError(
        "\n❌ KATBOT_HL_AGENT_PRIVATE_KEY not set.\n"
        "   Required for Hyperliquid portfolio operations.\n"
        "   Set via environment variable or in secrets file:\n"
        f"   {SECRETS_FILE}"
    )


# ============================================================================
# PORTFOLIO MANAGEMENT
# ============================================================================


def list_portfolios(token: str) -> list:
    """List all portfolios for the authenticated user."""
    r = requests.get(f"{BASE_URL}/portfolio", headers=_auth(token))
    r.raise_for_status()
    return r.json()


def create_portfolio(token: str, name: str, portfolio_type: str = "HL_PAPER",
                     agent_private_key: str = None, amount: float = None,
                     is_testnet: bool = True, primary_agent_id: int = None,
                     arbitrum_rpc_url: str = None) -> dict:
    """Create a new portfolio.

    Args:
        token: JWT access token
        name: Portfolio name
        portfolio_type: "HL_PAPER" (paper trading) or "HYPERLIQUID" (live trading).
                        Note: the old "PAPER" value has been renamed to "HL_PAPER".
        agent_private_key: Optional agent private key (for HYPERLIQUID type)
        amount: Initial USD balance for paper portfolios (ignored for HYPERLIQUID)
        is_testnet: Use Hyperliquid testnet (default True for safety)
        primary_agent_id: ID of the agent to assign as primary to this portfolio
        arbitrum_rpc_url: Arbitrum RPC URL for Hyperliquid portfolio

    Returns:
        Created PortfolioInfo dict with id, name, type, agent_address, etc.
    """
    payload = {
        "name": name,
        "portfolio_type": portfolio_type,
        "is_testnet": is_testnet,
    }

    key = agent_private_key or AGENT_PRIVATE_KEY
    if key:
        payload["agent_private_key"] = key
    if amount is not None:
        payload["amount"] = amount
    if primary_agent_id is not None:
        payload["primary_agent_id"] = primary_agent_id
    if arbitrum_rpc_url is not None:
        payload["arbitrum_rpc_url"] = arbitrum_rpc_url

    r = requests.post(f"{BASE_URL}/portfolio", json=payload, headers=_auth(token))
    r.raise_for_status()
    return r.json()


def get_portfolio(token: str, portfolio_id: int, window: str = None, require_agent: bool = True) -> dict:
    """Get portfolio state.

    For timeseries data use get_portfolio_timeseries() instead.

    Args:
        token: JWT access token
        portfolio_id: Portfolio ID to query
        window: (deprecated) Use get_portfolio_timeseries() for timeseries data
        require_agent: If True (default), raises error if agent key not available.
                      Set to False for paper portfolios that don't need agent key.

    Returns:
        PortfolioInfo dict with portfolio state, positions, PnL metrics, etc.

    Raises:
        ValueError: If require_agent=True and KATBOT_HL_AGENT_PRIVATE_KEY not set
        HTTPError: If API returns error (e.g., 400 for missing agent key on Hyperliquid)
    """
    agent_key = _require_agent_key() if require_agent else AGENT_PRIVATE_KEY

    params = {}
    if window is not None:
        params["window"] = window

    r = requests.get(
        f"{BASE_URL}/portfolio/{portfolio_id}",
        params=params,
        headers=_auth(token, agent_key)
    )
    r.raise_for_status()
    return r.json()


def update_portfolio(token: str, portfolio_id: int,
                     name: str = None,
                     tokens_selected: list = None,
                     max_history_messages: int = None) -> dict:
    """Update portfolio settings (name, tokens, history limit).

    Args:
        token: Auth token
        portfolio_id: Portfolio ID
        name: New portfolio name (optional)
        tokens_selected: List of token symbols (e.g., ["BTC", "ETH", "SOL"])
        max_history_messages: Conversation history limit

    Returns:
        Updated PortfolioInfo dict
    """
    payload = {}
    if name is not None:
        payload["name"] = name
    if tokens_selected is not None:
        payload["tokens_selected"] = tokens_selected
    if max_history_messages is not None:
        payload["max_history_messages"] = max_history_messages

    r = requests.put(f"{BASE_URL}/portfolio/{portfolio_id}",
                     json=payload, headers=_auth(token))
    r.raise_for_status()
    return r.json()


def delete_portfolio(token: str, portfolio_id: int,
                     agent_private_key: str = None,
                     user_master_address: str = None) -> dict:
    """Delete a portfolio and all its associated data.

    Args:
        token: JWT access token
        portfolio_id: Portfolio ID to delete
        agent_private_key: Agent private key (for Hyperliquid portfolios)
        user_master_address: Master wallet address

    Returns:
        Dict with success status and message
    """
    params = {}
    if user_master_address:
        params["user_master_address"] = user_master_address
    key = agent_private_key or AGENT_PRIVATE_KEY
    if key:
        params["agent_private_key"] = key

    r = requests.delete(f"{BASE_URL}/portfolio/{portfolio_id}",
                        params=params, headers=_auth(token))
    r.raise_for_status()
    return r.json()


def get_portfolio_tokens(token: str, portfolio_id: int) -> list:
    """Get available trading token symbols for a portfolio.

    Returns:
        List of symbol strings (e.g., ["BTC", "ETH", "SOL"])
    """
    r = requests.get(f"{BASE_URL}/portfolio/{portfolio_id}/tokens", headers=_auth(token))
    r.raise_for_status()
    return r.json()


def get_portfolio_chain_info(token: str, portfolio_id: int) -> dict:
    """Get chain information for a portfolio.

    Returns:
        Dict with portfolio_id, chain_id, is_testnet, network_name
    """
    r = requests.get(f"{BASE_URL}/portfolio/{portfolio_id}/chain-info", headers=_auth(token))
    r.raise_for_status()
    return r.json()


def get_portfolio_timeseries(token: str, portfolio_id: int,
                              granularity: str,
                              limit: int = 100,
                              window: str = "24H",
                              agent_private_key: str = None) -> dict:
    """Get timeseries data for a portfolio.

    Args:
        token: JWT access token
        portfolio_id: Portfolio ID
        granularity: Data granularity string (e.g., "1m", "5m", "15m", "1h", "4h", "1d", "1w", "1M")
        limit: Maximum number of data points (default 100)
        window: Time window (e.g., "24H", "7D", "30D", default "24H")
        agent_private_key: Agent private key (required for HYPERLIQUID portfolios)

    Returns:
        Dict with timeseries list, portfolio_id, granularity, window, limit
    """
    key = agent_private_key or AGENT_PRIVATE_KEY
    r = requests.get(
        f"{BASE_URL}/portfolio/{portfolio_id}/timeseries",
        params={"granularity": granularity, "limit": limit, "window": window},
        headers=_auth(token, key)
    )
    r.raise_for_status()
    return r.json()


def approve_builder_fee(token: str, portfolio_id: int,
                         action: dict, signature: dict, nonce: int) -> dict:
    """Broadcast a user-signed approveBuilderFee action to Hyperliquid.

    The frontend constructs and signs the EIP-712 approveBuilderFee action.
    This endpoint forwards it to Hyperliquid and records approval in the database.

    Args:
        token: JWT access token
        portfolio_id: Portfolio ID (must be HYPERLIQUID type)
        action: Full action dict (type, builder, maxFeeRate, nonce, etc.)
        signature: {r, s, v} signature from MetaMask signTypedData
        nonce: Millisecond timestamp used as nonce

    Returns:
        Dict with status, result, and portfolio_id
    """
    payload = {"action": action, "signature": signature, "nonce": nonce}
    r = requests.post(f"{BASE_URL}/portfolio/{portfolio_id}/approve-builder-fee",
                      json=payload, headers=_auth(token))
    r.raise_for_status()
    return r.json()


def validate_hyperliquid(token: str, agent_private_key: str = None,
                          is_testnet: bool = True) -> dict:
    """Validate a Hyperliquid connection using an agent private key.

    Args:
        token: JWT access token
        agent_private_key: Agent private key to validate
        is_testnet: Use testnet (default True for safety)

    Returns:
        Dict with status, validation details, and user_address
    """
    key = agent_private_key or AGENT_PRIVATE_KEY
    payload = {"agent_private_key": key, "is_testnet": is_testnet}
    r = requests.post(f"{BASE_URL}/portfolio/validate-hyperliquid",
                      json=payload, headers=_auth(token))
    r.raise_for_status()
    return r.json()


# ============================================================================
# RECOMMENDATIONS
# ============================================================================


def request_recommendation(token: str, portfolio_id: int, message: str,
                             agent_id: int = None) -> dict:
    """Submit a recommendation request to the agent (async, returns ticket).

    Args:
        token: JWT access token
        portfolio_id: Portfolio ID
        message: Prompt/message for the agent
        agent_id: Optional specific agent ID to use. If None, uses the portfolio's
                  primary agent.

    Returns:
        Dict with ticket_id and status
    """
    payload = {
        "portfolio_id": portfolio_id,
        "message": message,
    }
    if agent_id is not None:
        payload["agent_id"] = agent_id
    if AGENT_PRIVATE_KEY:
        payload["agent_private_key"] = AGENT_PRIVATE_KEY
    r = requests.post(f"{BASE_URL}/agent/recommendation/message", json=payload, headers=_auth(token))
    r.raise_for_status()
    return r.json()


def poll_recommendation(token: str, ticket_id: str, max_wait: int = 60) -> dict:
    """Poll until recommendation is ready or timeout.

    Returns:
        Dict with ticket_id, status, done, response, error
    """
    deadline = time.time() + max_wait
    while time.time() < deadline:
        r = requests.get(f"{BASE_URL}/agent/recommendation/poll/{ticket_id}", headers=_auth(token))
        r.raise_for_status()
        data = r.json()
        if data.get("done") or data.get("status") in ("COMPLETED", "complete", "FAILED"):
            return data
        time.sleep(2)
    raise TimeoutError(f"Recommendation not ready after {max_wait}s")


def submit_recommendation_response(token: str, portfolio_id: int,
                                    recommendation: dict,
                                    agent_id: int = None,
                                    pack_goals: str = None,
                                    agent_private_key: str = None) -> dict:
    """Submit a foreign agent's recommendation for analysis (async, returns ticket).

    Used by openclaw to analyze a recommendation from another agent/katpack.

    Args:
        token: JWT access token
        portfolio_id: Portfolio ID
        recommendation: ForeignRecommendationContext dict with agent_name, symbol,
                        action, confidence, entry_price, take_profit_pct, stop_loss_pct,
                        rationale, katbot_portfolio_id
        agent_id: Optional specific agent to use
        pack_goals: Katpack goals/description
        agent_private_key: Agent private key for Hyperliquid operations

    Returns:
        Dict with ticket_id and status
    """
    payload = {
        "portfolio_id": portfolio_id,
        "recommendation": recommendation,
    }
    if agent_id is not None:
        payload["agent_id"] = agent_id
    if pack_goals is not None:
        payload["pack_goals"] = pack_goals
    key = agent_private_key or AGENT_PRIVATE_KEY
    if key:
        payload["agent_private_key"] = key

    r = requests.post(f"{BASE_URL}/agent/recommendation/response",
                      json=payload, headers=_auth(token))
    r.raise_for_status()
    return r.json()


def poll_recommendation_response(token: str, ticket_id: str, max_wait: int = 60) -> dict:
    """Poll until recommendation response analysis is ready or timeout.

    Returns:
        Dict with ticket_id, status, done, response (markdown analysis), error
    """
    deadline = time.time() + max_wait
    while time.time() < deadline:
        r = requests.get(f"{BASE_URL}/agent/recommendation/response/poll/{ticket_id}",
                         headers=_auth(token))
        r.raise_for_status()
        data = r.json()
        if data.get("done") or data.get("status") in ("COMPLETED", "complete", "FAILED"):
            return data
        time.sleep(2)
    raise TimeoutError(f"Recommendation response not ready after {max_wait}s")


def get_recommendations(token: str, portfolio_id: int) -> list:
    """Get existing recommendations for a portfolio."""
    r = requests.get(f"{BASE_URL}/portfolio/{portfolio_id}/recommendation", headers=_auth(token))
    r.raise_for_status()
    return r.json()


def execute_recommendation(token: str, portfolio_id: int, rec_id: int,
                            execute_onchain: bool = False,
                            user_master_address: str = None) -> dict:
    """Execute an existing recommendation by ID."""
    payload = {"recommendation_id": rec_id}
    if execute_onchain is not None:
        payload["execute_onchain"] = execute_onchain
    if AGENT_PRIVATE_KEY:
        payload["agent_private_key"] = AGENT_PRIVATE_KEY
    if user_master_address:
        payload["user_master_address"] = user_master_address
    r = requests.post(f"{BASE_URL}/portfolio/{portfolio_id}/execute",
                      json=payload, headers=_auth(token))
    r.raise_for_status()
    return r.json()


# ============================================================================
# TRADES & POSITIONS
# ============================================================================


def close_position(token: str, portfolio_id: int, symbol: str,
                   user_master_address: str = None,
                   reason: str = "API position closure",
                   execute_onchain: bool = False) -> dict:
    """Close an open position by symbol.

    Args:
        token: JWT access token
        portfolio_id: Portfolio ID
        symbol: Token symbol (e.g., "ETH", "BTC")
        user_master_address: Master wallet address for Hyperliquid agent approval
        reason: Reason for closing the position (default "API position closure")
        execute_onchain: Whether to execute on-chain (default False)

    Returns:
        ClosePositionResponse dict with success, message, symbol, exit_price, pnl_usd
    """
    payload = {
        "symbol": symbol,
        "reason": reason,
        "execute_onchain": execute_onchain,
    }
    if user_master_address:
        payload["user_master_address"] = user_master_address
    if AGENT_PRIVATE_KEY:
        payload["agent_private_key"] = AGENT_PRIVATE_KEY
    r = requests.post(f"{BASE_URL}/portfolio/{portfolio_id}/close-position",
                      json=payload, headers=_auth(token))
    r.raise_for_status()
    return r.json()


def list_trades(token: str, portfolio_id: int,
                agent_private_key: str = None,
                user_master_address: str = None) -> list:
    """List all trades for a portfolio.

    Args:
        token: JWT access token
        portfolio_id: Portfolio ID
        agent_private_key: Agent private key (for Hyperliquid portfolios)
        user_master_address: Master wallet address

    Returns:
        List of trade dicts
    """
    params = {}
    if user_master_address:
        params["user_master_address"] = user_master_address
    key = agent_private_key or AGENT_PRIVATE_KEY
    if key:
        params["agent_private_key"] = key
    r = requests.get(f"{BASE_URL}/portfolio/{portfolio_id}/trade",
                     params=params, headers=_auth(token))
    r.raise_for_status()
    return r.json()


def get_position_events(token: str, portfolio_id: int,
                         limit: int = 20,
                         event_type: str = None,
                         agent_private_key: str = None,
                         user_master_address: str = None) -> list:
    """Return position lifecycle events for a portfolio.

    Event types: TP_HIT, SL_HIT, LIQUIDATED, MANUAL_CLOSE

    Args:
        token: JWT access token
        portfolio_id: Portfolio ID
        limit: Max events to return (default 20, max 200)
        event_type: Filter by event type (optional)
        agent_private_key: Required for HYPERLIQUID portfolios
        user_master_address: Master wallet address

    Returns:
        List of position event dicts
    """
    params = {"limit": limit}
    if event_type:
        params["event_type"] = event_type
    if user_master_address:
        params["user_master_address"] = user_master_address
    key = agent_private_key or AGENT_PRIVATE_KEY
    r = requests.get(f"{BASE_URL}/portfolio/{portfolio_id}/events",
                     params=params, headers=_auth(token, key))
    r.raise_for_status()
    return r.json()


# ============================================================================
# AGENT MANAGEMENT
# ============================================================================


def list_agents(token: str) -> list:
    """List all agents belonging to the authenticated user.

    Returns:
        List of AgentInfo dicts (id, name, max_history_messages, avatar_url, etc.)
    """
    r = requests.get(f"{BASE_URL}/agents", headers=_auth(token))
    r.raise_for_status()
    return r.json()


def create_agent(token: str, name: str, max_history_messages: int = 10) -> dict:
    """Create a new agent.

    Args:
        token: JWT access token
        name: Agent slug name (lowercase letters, numbers, hyphens; a 6-char suffix
              is appended automatically by the server)
        max_history_messages: Conversation history retention limit (1-100)

    Returns:
        AgentInfo dict with id, name, avatar_url, etc.
    """
    payload = {"name": name, "max_history_messages": max_history_messages}
    r = requests.post(f"{BASE_URL}/agents", json=payload, headers=_auth(token))
    r.raise_for_status()
    return r.json()


def get_agent(token: str, agent_id: int) -> dict:
    """Get details for a specific agent.

    Returns:
        AgentInfo dict
    """
    r = requests.get(f"{BASE_URL}/agents/{agent_id}", headers=_auth(token))
    r.raise_for_status()
    return r.json()


def update_agent(token: str, agent_id: int,
                  name: str = None,
                  max_history_messages: int = None,
                  avatar_seed: str = None) -> dict:
    """Update an existing agent.

    Args:
        token: JWT access token
        agent_id: Agent ID to update
        name: New slug name (optional)
        max_history_messages: Updated history limit (optional, 1-100)
        avatar_seed: Seed string for avatar generation (optional)

    Returns:
        Updated AgentInfo dict
    """
    payload = {}
    if name is not None:
        payload["name"] = name
    if max_history_messages is not None:
        payload["max_history_messages"] = max_history_messages
    if avatar_seed is not None:
        payload["avatar_seed"] = avatar_seed
    r = requests.put(f"{BASE_URL}/agents/{agent_id}", json=payload, headers=_auth(token))
    r.raise_for_status()
    return r.json()


def delete_agent(token: str, agent_id: int) -> dict:
    """Delete an agent. Only agents with 0 active primary portfolio assignments can be deleted.

    Returns:
        Dict with success status
    """
    r = requests.delete(f"{BASE_URL}/agents/{agent_id}", headers=_auth(token))
    r.raise_for_status()
    return r.json()


def search_agents(token: str, q: str, portfolio_id: int = None) -> list:
    """Search agents by name across all users (for invite flow).

    Args:
        token: JWT access token
        q: Search query (minimum 3 characters)
        portfolio_id: If provided, filters out agents already assigned or invited

    Returns:
        List of AgentInfo dicts (up to 10 results)
    """
    params = {"q": q}
    if portfolio_id is not None:
        params["portfolio_id"] = portfolio_id
    r = requests.get(f"{BASE_URL}/agents/search", params=params, headers=_auth(token))
    r.raise_for_status()
    return r.json()


# ============================================================================
# PORTFOLIO-AGENT ASSIGNMENTS
# ============================================================================


def get_portfolio_agent(token: str, portfolio_id: int) -> dict:
    """Get the active primary agent assignment for a portfolio.

    Returns:
        PortfolioAgentAssignmentInfo dict with id, portfolio_id, agent_id, role, agent info
    """
    r = requests.get(f"{BASE_URL}/portfolio/{portfolio_id}/agent", headers=_auth(token))
    r.raise_for_status()
    return r.json()


def list_portfolio_agents(token: str, portfolio_id: int) -> list:
    """List all active agent assignments for a portfolio (primary and observers).

    Returns:
        List of PortfolioAgentAssignmentInfo dicts
    """
    r = requests.get(f"{BASE_URL}/portfolio/{portfolio_id}/agents", headers=_auth(token))
    r.raise_for_status()
    return r.json()


def assign_agent(token: str, portfolio_id: int, agent_id: int,
                  role: str = "primary") -> dict:
    """Assign an agent to a portfolio.

    For role "primary": deactivates the existing primary agent and sets this one.
    For role "observer": adds the agent without affecting the existing primary.

    Args:
        token: JWT access token
        portfolio_id: Portfolio ID
        agent_id: Agent ID to assign
        role: "primary" or "observer" (default "primary")

    Returns:
        PortfolioAgentAssignmentInfo dict
    """
    payload = {"agent_id": agent_id, "role": role}
    r = requests.post(f"{BASE_URL}/portfolio/{portfolio_id}/agent",
                      json=payload, headers=_auth(token))
    r.raise_for_status()
    return r.json()


def unassign_agent(token: str, portfolio_id: int, agent_id: int) -> dict:
    """Deactivate a specific agent assignment from a portfolio.

    Returns:
        Dict with success status
    """
    r = requests.delete(f"{BASE_URL}/portfolio/{portfolio_id}/agent/{agent_id}",
                        headers=_auth(token))
    r.raise_for_status()
    return r.json()


# ============================================================================
# AGENT OBSERVER INVITATIONS
# ============================================================================


def create_agent_invitation(token: str, portfolio_id: int, agent_id: int) -> dict:
    """Invite an agent (owned by another user) to observe this portfolio.

    Args:
        token: JWT access token
        portfolio_id: Portfolio ID (must be owned by caller)
        agent_id: ID of the agent to invite as observer

    Returns:
        AgentObserverInviteInfo dict
    """
    payload = {"agent_id": agent_id, "role": "observer"}
    r = requests.post(f"{BASE_URL}/portfolio/{portfolio_id}/agent-invitations",
                      json=payload, headers=_auth(token))
    r.raise_for_status()
    return r.json()


def list_portfolio_invitations(token: str, portfolio_id: int) -> list:
    """List all agent invitations (pending, accepted, rejected) for a portfolio.

    Returns:
        List of AgentObserverInviteInfo dicts
    """
    r = requests.get(f"{BASE_URL}/portfolio/{portfolio_id}/agent-invitations",
                     headers=_auth(token))
    r.raise_for_status()
    return r.json()


def list_pending_invitations(token: str) -> list:
    """List all pending invitations for agents owned by the authenticated user.

    Returns:
        List of AgentObserverInviteInfo dicts
    """
    r = requests.get(f"{BASE_URL}/agents/invitations/pending", headers=_auth(token))
    r.raise_for_status()
    return r.json()


def respond_to_invitation(token: str, agent_id: int, invitation_id: int,
                           action: str) -> dict:
    """Accept or reject a pending agent observer invitation.

    Args:
        token: JWT access token
        agent_id: ID of the agent (must be owned by caller)
        invitation_id: Invitation ID to respond to
        action: "accepted" or "rejected"

    Returns:
        Updated AgentObserverInviteInfo dict
    """
    payload = {"action": action}
    r = requests.post(f"{BASE_URL}/agents/{agent_id}/invitations/{invitation_id}/respond",
                      json=payload, headers=_auth(token))
    r.raise_for_status()
    return r.json()


def list_observer_portfolios(token: str) -> list:
    """Return portfolios that the authenticated user observes via an accepted agent invitation.

    Returns:
        List of PortfolioInfo dicts with observer_role="observer"
    """
    r = requests.get(f"{BASE_URL}/agents/observer-portfolios", headers=_auth(token))
    r.raise_for_status()
    return r.json()


# ============================================================================
# CONVERSATION HISTORY
# ============================================================================


def get_conversation(token: str, portfolio_id: int) -> dict:
    """Get conversation history for a portfolio.

    Returns:
        Dict with portfolio_id, portfolio_name, exists, message_count,
        last_interaction, created_at, conversation list
    """
    r = requests.get(f"{BASE_URL}/portfolio/{portfolio_id}/conversation",
                     headers=_auth(token))
    r.raise_for_status()
    return r.json()


def delete_conversation(token: str, portfolio_id: int) -> dict:
    """Clear conversation history for a portfolio (preserves portfolio state).

    Returns:
        Dict with portfolio_id, portfolio_name, success, message
    """
    r = requests.delete(f"{BASE_URL}/portfolio/{portfolio_id}/conversation",
                        headers=_auth(token))
    r.raise_for_status()
    return r.json()


# ============================================================================
# USER & SUBSCRIPTION
# ============================================================================


def get_user(token: str) -> dict:
    """Get user info including subscription and feature usage.

    Returns:
        GetUserResponse dict with sub, id, is_whitelisted, subscription, plan,
        feature_usage
    """
    r = requests.get(f"{BASE_URL}/user", headers=_auth(token))
    r.raise_for_status()
    return r.json()


def get_plans() -> list:
    """Get all available subscription plans (no auth required).

    Returns:
        List of PlanResponse dicts sorted by price ascending
    """
    r = requests.get(f"{BASE_URL}/plans")
    r.raise_for_status()
    return r.json()


# ============================================================================
# CLI entry point
# ============================================================================

def main():
    """CLI entry point for katbot_client.py script."""
    import sys

    # Reload env if running as CLI
    env = {}
    if ENV_FILE and ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    env[key.strip()] = val.strip().strip('"')
    env.update(os.environ)  # Allow env var overrides

    if len(sys.argv) < 2:
        print("Usage: katbot_client.py <action> [args]")
        print("Actions:")
        print("  portfolio-state         Get portfolio state")
        print("  execute <rec_id>        Execute a recommendation")
        print("  close-position <sym>    Close position by symbol")
        print("  recommendations         List recommendations")
        print("  request-recommendation [msg]  Request a new recommendation")
        print("  poll-recommendation <ticket_id>  Poll for recommendation result")
        print("  update-portfolio --tokens BTC,ETH [--name Name]  Update portfolio")
        print("  list-agents             List all agents")
        print("  get-agent <agent_id>    Get agent details")
        print("  list-portfolio-agents   List agents assigned to portfolio")
        print("  assign-agent <agent_id> [--role primary|observer]  Assign agent to portfolio")
        print("  conversation            Get conversation history")
        print("  clear-conversation      Clear conversation history")
        print("  user                    Get user info and subscription")
        print("  plans                   List subscription plans")
        print("  tokens                  Get available trading tokens")
        print("  chain-info              Get portfolio chain info")
        sys.exit(1)

    action = sys.argv[1]
    portfolio_id = env.get("PORTFOLIO_ID")

    token = get_token()

    if action == "portfolio-state":
        if not portfolio_id:
            print("ERROR: PORTFOLIO_ID must be set")
            sys.exit(1)
        result = get_portfolio(token, int(portfolio_id))
        print(json.dumps(result, indent=2, default=str))

    elif action == "execute":
        if not portfolio_id:
            print("ERROR: PORTFOLIO_ID must be set")
            sys.exit(1)
        recommendation_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not recommendation_id:
            print("ERROR: recommendation_id required")
            sys.exit(1)
        result = execute_recommendation(
            token, int(portfolio_id), int(recommendation_id),
            execute_onchain=False,
            user_master_address=env.get("WALLET_ADDRESS")
        )
        print(json.dumps(result, indent=2, default=str))

    elif action == "close-position":
        if not portfolio_id:
            print("ERROR: PORTFOLIO_ID must be set")
            sys.exit(1)
        symbol = sys.argv[2] if len(sys.argv) > 2 else None
        if not symbol:
            print("ERROR: symbol required (e.g., ETH)")
            sys.exit(1)
        result = close_position(token, int(portfolio_id), symbol,
                                user_master_address=env.get("WALLET_ADDRESS"))
        print(json.dumps(result, indent=2, default=str))

    elif action == "recommendations":
        if not portfolio_id:
            print("ERROR: PORTFOLIO_ID must be set")
            sys.exit(1)
        result = get_recommendations(token, int(portfolio_id))
        print(json.dumps(result, indent=2, default=str))

    elif action == "request-recommendation":
        if not portfolio_id:
            print("ERROR: PORTFOLIO_ID must be set")
            sys.exit(1)
        message = sys.argv[2] if len(sys.argv) > 2 else "Analyze portfolio tokens and generate recommendations based on the current market."
        result = request_recommendation(token, int(portfolio_id), message)
        print(json.dumps(result, indent=2, default=str))

    elif action == "poll-recommendation":
        ticket_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not ticket_id:
            print("ERROR: ticket_id required")
            sys.exit(1)
        result = poll_recommendation(token, ticket_id)
        print(json.dumps(result, indent=2, default=str))

    elif action == "update-portfolio":
        if not portfolio_id:
            print("ERROR: PORTFOLIO_ID must be set")
            sys.exit(1)
        tokens_arg = None
        name_arg = None
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--tokens" and i + 1 < len(sys.argv):
                tokens_arg = sys.argv[i + 1].split(",")
                i += 2
            elif sys.argv[i] == "--name" and i + 1 < len(sys.argv):
                name_arg = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        if not tokens_arg and not name_arg:
            print("Usage: update-portfolio --tokens BTC,ETH,SOL [--name \"New Name\"]")
            sys.exit(1)

        result = update_portfolio(token, int(portfolio_id), name=name_arg, tokens_selected=tokens_arg)
        print(json.dumps(result, indent=2, default=str))

    elif action == "list-agents":
        result = list_agents(token)
        print(json.dumps(result, indent=2, default=str))

    elif action == "get-agent":
        agent_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not agent_id:
            print("ERROR: agent_id required")
            sys.exit(1)
        result = get_agent(token, int(agent_id))
        print(json.dumps(result, indent=2, default=str))

    elif action == "list-portfolio-agents":
        if not portfolio_id:
            print("ERROR: PORTFOLIO_ID must be set")
            sys.exit(1)
        result = list_portfolio_agents(token, int(portfolio_id))
        print(json.dumps(result, indent=2, default=str))

    elif action == "assign-agent":
        if not portfolio_id:
            print("ERROR: PORTFOLIO_ID must be set")
            sys.exit(1)
        agent_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not agent_id:
            print("ERROR: agent_id required")
            sys.exit(1)
        role = "primary"
        if "--role" in sys.argv:
            role_idx = sys.argv.index("--role")
            if role_idx + 1 < len(sys.argv):
                role = sys.argv[role_idx + 1]
        result = assign_agent(token, int(portfolio_id), int(agent_id), role=role)
        print(json.dumps(result, indent=2, default=str))

    elif action == "conversation":
        if not portfolio_id:
            print("ERROR: PORTFOLIO_ID must be set")
            sys.exit(1)
        result = get_conversation(token, int(portfolio_id))
        print(json.dumps(result, indent=2, default=str))

    elif action == "clear-conversation":
        if not portfolio_id:
            print("ERROR: PORTFOLIO_ID must be set")
            sys.exit(1)
        result = delete_conversation(token, int(portfolio_id))
        print(json.dumps(result, indent=2, default=str))

    elif action == "user":
        result = get_user(token)
        print(json.dumps(result, indent=2, default=str))

    elif action == "plans":
        result = get_plans()
        print(json.dumps(result, indent=2, default=str))

    elif action == "tokens":
        if not portfolio_id:
            print("ERROR: PORTFOLIO_ID must be set")
            sys.exit(1)
        result = get_portfolio_tokens(token, int(portfolio_id))
        print(json.dumps(result, indent=2, default=str))

    elif action == "chain-info":
        if not portfolio_id:
            print("ERROR: PORTFOLIO_ID must be set")
            sys.exit(1)
        result = get_portfolio_chain_info(token, int(portfolio_id))
        print(json.dumps(result, indent=2, default=str))

    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
