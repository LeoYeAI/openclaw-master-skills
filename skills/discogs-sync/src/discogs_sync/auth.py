"""Authentication flows for Discogs (personal token and OAuth 1.0a)."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import click
import discogs_client

from .config import get_tokens, save_tokens, save_user_token
from .exceptions import AuthenticationError

USER_AGENT = "DiscogsSyncTool/0.1"
CALLBACK_URL = "http://127.0.0.1:8080/callback"


def run_token_auth_flow() -> dict:
    """Run the personal access token authentication flow.

    Prompts for a token, validates it via client.identity(), and stores it.
    Returns dict with user_token and username.
    """
    token = click.prompt("Enter your Discogs personal access token")

    client = discogs_client.Client(USER_AGENT, user_token=token)

    try:
        identity = client.identity()
        username = identity.username
    except Exception as e:
        raise AuthenticationError(f"Token validation failed: {e}") from e

    save_user_token(token, username)

    return {"user_token": token, "username": username}


def run_auth_flow(consumer_key: str | None = None, consumer_secret: str | None = None) -> dict:
    """Run the full OAuth 1.0a flow interactively.

    Returns dict with access_token, access_token_secret, username.
    """
    if not consumer_key:
        consumer_key = click.prompt("Enter your Discogs consumer key")
    if not consumer_secret:
        consumer_secret = click.prompt("Enter your Discogs consumer secret")

    client = discogs_client.Client(USER_AGENT, consumer_key=consumer_key, consumer_secret=consumer_secret)

    try:
        token, secret, authorize_url = client.get_authorize_url(callback_url=CALLBACK_URL)
    except Exception as e:
        raise AuthenticationError(f"Failed to get authorization URL: {e}") from e

    click.echo(f"\nOpen this URL in your browser to authorize:\n\n  {authorize_url}\n")
    click.echo("After authorizing, you'll be redirected to a localhost URL.")
    callback_input = click.prompt("Paste the full callback URL here")

    verifier = _parse_verifier(callback_input)
    if not verifier:
        raise AuthenticationError(
            "Could not parse oauth_verifier from the URL. "
            "Make sure you paste the full callback URL."
        )

    try:
        access_token, access_secret = client.get_access_token(verifier)
    except Exception as e:
        raise AuthenticationError(f"Failed to get access token: {e}") from e

    # Fetch username
    try:
        identity = client.identity()
        username = identity.username
    except Exception:
        username = None

    save_tokens(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_secret,
        username=username,
    )

    return {
        "access_token": access_token,
        "access_token_secret": access_secret,
        "username": username,
    }


def _parse_verifier(callback_input: str) -> str | None:
    """Extract oauth_verifier from a callback URL or raw verifier string."""
    callback_input = callback_input.strip()

    # If it looks like a URL, parse the query string
    if callback_input.startswith("http"):
        parsed = urlparse(callback_input)
        params = parse_qs(parsed.query)
        verifiers = params.get("oauth_verifier", [])
        return verifiers[0] if verifiers else None

    # Otherwise treat as raw verifier code
    return callback_input if callback_input else None


def check_auth() -> dict | None:
    """Check if we have valid stored tokens. Returns token dict or None."""
    return get_tokens()
