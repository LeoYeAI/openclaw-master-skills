"""
Shared HTTP client for OpenClaw Messaging.

Provides consistent error handling, authentication, and request formatting
for all client scripts.
"""

import json
import sys
from typing import Optional, Any
from urllib.parse import urljoin

import requests

from . import crypto
from .vault import Vault


# Default server URL
DEFAULT_SERVER_URL = "http://localhost:5000"

# Request timeout
DEFAULT_TIMEOUT = 30


class ClientError(Exception):
    """Base exception for client operations."""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class AuthenticationError(ClientError):
    """Raised when authentication fails."""
    pass


class ServerError(ClientError):
    """Raised when server returns an error."""
    pass


class NetworkError(ClientError):
    """Raised when network request fails."""
    pass


class RelayClient:
    """
    HTTP client for the ClawHub relay server.

    Handles authentication, request signing, and error handling.
    """

    def __init__(
        self,
        vault: Vault,
        server_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Initialize relay client.

        Args:
            vault: Vault instance for authentication
            server_url: Server URL (defaults to localhost:5000)
            timeout: Request timeout in seconds
        """
        self.vault = vault
        self.server_url = (server_url or DEFAULT_SERVER_URL).rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

    def _url(self, endpoint: str) -> str:
        """Build full URL for an endpoint."""
        return urljoin(self.server_url + '/', endpoint.lstrip('/'))

    def _handle_response(self, response: requests.Response) -> dict:
        """
        Handle HTTP response, raising appropriate exceptions.

        Args:
            response: requests Response object

        Returns:
            Parsed JSON response

        Raises:
            AuthenticationError: On 401/403
            ServerError: On 4xx/5xx errors
            ClientError: On other errors
        """
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {'error': response.text or 'Unknown error'}

        if response.status_code == 401:
            raise AuthenticationError(
                data.get('error', 'Authentication required'),
                status_code=401,
                response=data
            )
        elif response.status_code == 403:
            raise AuthenticationError(
                data.get('error', 'Access denied'),
                status_code=403,
                response=data
            )
        elif response.status_code >= 400:
            raise ServerError(
                data.get('error', f'Server error: {response.status_code}'),
                status_code=response.status_code,
                response=data
            )

        return data

    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[dict] = None,
        sign: bool = False,
        **kwargs
    ) -> dict:
        """
        Make an HTTP request.

        Args:
            method: HTTP method
            endpoint: API endpoint
            json_data: JSON body data
            sign: Whether to sign the request
            **kwargs: Additional arguments to requests

        Returns:
            Parsed JSON response

        Raises:
            NetworkError: On connection failure
            ClientError: On other errors
        """
        url = self._url(endpoint)

        headers = kwargs.pop('headers', {})
        headers['Content-Type'] = 'application/json'

        # Add authentication if signing required
        if sign and json_data:
            # Sign the request body
            signature = self.vault.sign(json_data)
            headers['X-Signature'] = signature
            headers['X-Vault-ID'] = self.vault.vault_id

        try:
            response = self.session.request(
                method,
                url,
                json=json_data,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection failed: {e}")
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timed out: {e}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request failed: {e}")

    def get(self, endpoint: str, **kwargs) -> dict:
        """Make a GET request."""
        return self._request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, data: Optional[dict] = None, sign: bool = False, **kwargs) -> dict:
        """Make a POST request."""
        return self._request('POST', endpoint, json_data=data, sign=sign, **kwargs)

    # =========================================================================
    # API Methods
    # =========================================================================

    def health(self) -> dict:
        """Check server health."""
        return self.get('/health')

    def get_challenge(self) -> dict:
        """
        Get a registration challenge from the server.

        Returns:
            Dict with 'challenge' key
        """
        return self.post('/register/challenge', data={
            'vault_id': self.vault.vault_id,
            'signing_public_key': self.vault.signing_public_key_b64,
            'encryption_public_key': self.vault.encryption_public_key_b64,
        })

    def register(self, challenge: str, signature: str, alias: Optional[str] = None) -> dict:
        """
        Complete registration with signed challenge.

        Args:
            challenge: The challenge string
            signature: Base64-encoded signature of the challenge
            alias: Optional alias to register

        Returns:
            Registration response
        """
        data = {
            'vault_id': self.vault.vault_id,
            'signing_public_key': self.vault.signing_public_key_b64,
            'encryption_public_key': self.vault.encryption_public_key_b64,
            'challenge': challenge,
            'challenge_signature': signature,
        }
        if alias:
            data['alias'] = alias
        return self.post('/register', data=data)

    def send_message(self, message: dict, signature: str, encrypted_payload: Optional[dict] = None) -> dict:
        """
        Send a message through the relay.

        Args:
            message: The message envelope and payload
            signature: Base64-encoded signature over envelope+payload
            encrypted_payload: Optional encrypted payload (replaces payload.body)

        Returns:
            Send response with message_id
        """
        data = {
            'message': message,
            'signature': signature,
        }
        if encrypted_payload:
            data['encrypted_payload'] = encrypted_payload

        return self.post('/send', data=data, sign=True)

    def receive(self, limit: int = 50) -> dict:
        """
        Receive unread messages.

        Args:
            limit: Maximum number of messages to retrieve

        Returns:
            Dict with 'messages' list
        """
        return self.get(f'/receive/{self.vault.vault_id}?limit={limit}')

    def acknowledge(self, message_id: str) -> dict:
        """
        Acknowledge receipt of a message.

        Args:
            message_id: ID of message to acknowledge

        Returns:
            Acknowledgment response
        """
        return self.post(f'/ack/{message_id}', data={
            'vault_id': self.vault.vault_id,
        }, sign=True)

    def list_agents(self, limit: int = 100) -> dict:
        """
        List registered agents.

        Args:
            limit: Maximum number of agents to return

        Returns:
            Dict with 'agents' list
        """
        return self.get(f'/agents?limit={limit}')

    def resolve_alias(self, alias: str) -> dict:
        """
        Resolve an alias to vault ID.

        Args:
            alias: Alias to resolve

        Returns:
            Dict with agent info
        """
        return self.get(f'/resolve/{alias}')

    def set_alias(self, alias: str) -> dict:
        """
        Set or update alias.

        Args:
            alias: New alias

        Returns:
            Updated alias info
        """
        return self.post('/alias', data={
            'vault_id': self.vault.vault_id,
            'alias': alias,
        }, sign=True)

    def get_conversation_log(self, conversation_id: str) -> dict:
        """
        Get conversation log.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation log
        """
        return self.get(f'/messages/{conversation_id}/log')

    def get_agent_logs(self, limit: int = 50) -> dict:
        """
        Get all conversation logs for this agent.

        Args:
            limit: Maximum conversations to return

        Returns:
            Dict with 'conversations' list
        """
        return self.get(f'/logs/{self.vault.vault_id}?limit={limit}')


def get_client(
    vault: Optional[Vault] = None,
    server_url: Optional[str] = None,
) -> RelayClient:
    """
    Get a configured RelayClient instance.

    Args:
        vault: Vault instance (creates default if not provided)
        server_url: Server URL

    Returns:
        Configured RelayClient
    """
    if vault is None:
        from .vault import get_default_vault
        vault = get_default_vault()
        vault.load()

    return RelayClient(vault, server_url)


# =============================================================================
# Output Helpers
# =============================================================================

def output_json(data: Any, file=sys.stdout):
    """Output data as JSON to stdout."""
    json.dump(data, file, indent=2)
    print(file=file)


def output_error(message: str, code: str = "error", file=sys.stderr):
    """Output error message to stderr in JSON format."""
    output_json({'error': message, 'code': code}, file=file)


def output_human(message: str, file=sys.stderr):
    """Output human-readable message to stderr."""
    print(message, file=file)
