"""
Vault management for OpenClaw Messaging.

The vault IS the identity. It stores:
- Agent's unique ID
- Ed25519 signing keypair
- X25519 encryption keypair
- Contact list (allow-list of agents that can message this agent)
- Message history

Default location: ~/.openclaw/vault/
"""

import os
import json
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from . import crypto


# Default vault location
DEFAULT_VAULT_DIR = Path.home() / ".openclaw" / "vault"

# File names within vault
IDENTITY_FILE = "identity.json"
SIGNING_KEY_FILE = "signing_key.bin"
ENCRYPTION_KEY_FILE = "encryption_key.bin"
CONTACTS_FILE = "contacts.json"
HISTORY_DIR = "history"
QUARANTINE_DIR = "quarantine"


class VaultError(Exception):
    """Base exception for vault operations."""
    pass


class VaultNotFoundError(VaultError):
    """Raised when vault doesn't exist."""
    pass


class VaultExistsError(VaultError):
    """Raised when trying to create vault that already exists."""
    pass


class Vault:
    """
    Manages an agent's local vault.

    The vault contains all cryptographic material and message history.
    """

    def __init__(self, vault_dir: Optional[Path] = None):
        """
        Initialize vault manager.

        Args:
            vault_dir: Path to vault directory. Defaults to ~/.openclaw/vault/
        """
        self.vault_dir = Path(vault_dir) if vault_dir else DEFAULT_VAULT_DIR
        self._identity: Optional[dict] = None
        self._signing_private_key = None
        self._encryption_private_key = None

    @property
    def exists(self) -> bool:
        """Check if vault exists."""
        return (self.vault_dir / IDENTITY_FILE).exists()

    @property
    def identity_path(self) -> Path:
        return self.vault_dir / IDENTITY_FILE

    @property
    def signing_key_path(self) -> Path:
        return self.vault_dir / SIGNING_KEY_FILE

    @property
    def encryption_key_path(self) -> Path:
        return self.vault_dir / ENCRYPTION_KEY_FILE

    @property
    def contacts_path(self) -> Path:
        return self.vault_dir / CONTACTS_FILE

    @property
    def history_path(self) -> Path:
        return self.vault_dir / HISTORY_DIR

    @property
    def quarantine_path(self) -> Path:
        return self.vault_dir / QUARANTINE_DIR

    def create(self, alias: Optional[str] = None) -> dict:
        """
        Create a new vault with fresh keypairs.

        Args:
            alias: Optional human-readable alias for this vault

        Returns:
            Identity dict with vault_id and public keys

        Raises:
            VaultExistsError: If vault already exists
        """
        if self.exists:
            raise VaultExistsError(f"Vault already exists at {self.vault_dir}")

        # Create directory structure
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.history_path.mkdir(exist_ok=True)
        self.quarantine_path.mkdir(exist_ok=True)

        # Generate keypairs
        signing_private, signing_public = crypto.generate_signing_keypair()
        encryption_private, encryption_public = crypto.generate_encryption_keypair()

        # Generate vault ID
        vault_id = f"vault_{uuid.uuid4().hex}"

        # Create identity
        identity = {
            'vault_id': vault_id,
            'alias': alias,
            'signing_public_key': crypto.public_signing_key_to_b64(signing_public),
            'encryption_public_key': crypto.public_encryption_key_to_b64(encryption_public),
            'created_at': datetime.now(timezone.utc).isoformat(),
        }

        # Save private keys (binary format)
        self._write_binary(self.signing_key_path, crypto.serialize_private_signing_key(signing_private))
        self._write_binary(self.encryption_key_path, crypto.serialize_private_encryption_key(encryption_private))

        # Set restrictive permissions on key files
        os.chmod(self.signing_key_path, 0o600)
        os.chmod(self.encryption_key_path, 0o600)

        # Save identity
        self._write_json(self.identity_path, identity)

        # Initialize empty contacts
        self._write_json(self.contacts_path, {'contacts': {}, 'quarantine_unknown': True})

        # Cache loaded data
        self._identity = identity
        self._signing_private_key = signing_private
        self._encryption_private_key = encryption_private

        return identity

    def load(self) -> dict:
        """
        Load an existing vault.

        Returns:
            Identity dict

        Raises:
            VaultNotFoundError: If vault doesn't exist
        """
        if not self.exists:
            raise VaultNotFoundError(f"No vault found at {self.vault_dir}")

        # Load identity
        self._identity = self._read_json(self.identity_path)

        # Load private keys
        signing_key_bytes = self._read_binary(self.signing_key_path)
        encryption_key_bytes = self._read_binary(self.encryption_key_path)

        self._signing_private_key = crypto.deserialize_private_signing_key(signing_key_bytes)
        self._encryption_private_key = crypto.deserialize_private_encryption_key(encryption_key_bytes)

        return self._identity

    def get_identity(self) -> dict:
        """
        Get vault identity, loading if necessary.

        Returns:
            Identity dict
        """
        if self._identity is None:
            self.load()
        return self._identity

    @property
    def vault_id(self) -> str:
        """Get vault ID."""
        return self.get_identity()['vault_id']

    @property
    def alias(self) -> Optional[str]:
        """Get vault alias."""
        return self.get_identity().get('alias')

    @property
    def signing_public_key_b64(self) -> str:
        """Get base64-encoded signing public key."""
        return self.get_identity()['signing_public_key']

    @property
    def encryption_public_key_b64(self) -> str:
        """Get base64-encoded encryption public key."""
        return self.get_identity()['encryption_public_key']

    def get_signing_private_key(self):
        """Get signing private key, loading if necessary."""
        if self._signing_private_key is None:
            self.load()
        return self._signing_private_key

    def get_encryption_private_key(self):
        """Get encryption private key, loading if necessary."""
        if self._encryption_private_key is None:
            self.load()
        return self._encryption_private_key

    def get_signing_public_key(self):
        """Get signing public key object."""
        return crypto.b64_to_public_signing_key(self.signing_public_key_b64)

    def get_encryption_public_key(self):
        """Get encryption public key object."""
        return crypto.b64_to_public_encryption_key(self.encryption_public_key_b64)

    # =========================================================================
    # Signing and Encryption
    # =========================================================================

    def sign(self, data: dict) -> str:
        """
        Sign a dict using the vault's signing key.

        Args:
            data: Dict to sign

        Returns:
            Base64-encoded signature
        """
        return crypto.sign_json(self.get_signing_private_key(), data)

    def decrypt(self, encrypted: dict) -> dict:
        """
        Decrypt data addressed to this vault.

        Args:
            encrypted: Dict with ephemeral_public_key, nonce, ciphertext

        Returns:
            Decrypted dict
        """
        return crypto.decrypt_json(self.get_encryption_private_key(), encrypted)

    # =========================================================================
    # Contact Management
    # =========================================================================

    def get_contacts(self) -> dict:
        """
        Get contacts configuration.

        Returns:
            Dict with 'contacts' and 'quarantine_unknown' keys
        """
        if not self.contacts_path.exists():
            return {'contacts': {}, 'quarantine_unknown': True}
        return self._read_json(self.contacts_path)

    def add_contact(
        self,
        vault_id: str,
        alias: Optional[str] = None,
        signing_public_key: Optional[str] = None,
        encryption_public_key: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> dict:
        """
        Add or update a contact.

        Args:
            vault_id: Contact's vault ID
            alias: Optional alias for the contact
            signing_public_key: Contact's signing public key (base64)
            encryption_public_key: Contact's encryption public key (base64)
            notes: Optional notes about this contact

        Returns:
            Updated contact entry
        """
        contacts_data = self.get_contacts()

        contact = contacts_data['contacts'].get(vault_id, {})
        contact.update({
            'vault_id': vault_id,
            'added_at': contact.get('added_at', datetime.now(timezone.utc).isoformat()),
            'updated_at': datetime.now(timezone.utc).isoformat(),
        })

        if alias is not None:
            contact['alias'] = alias
        if signing_public_key is not None:
            contact['signing_public_key'] = signing_public_key
        if encryption_public_key is not None:
            contact['encryption_public_key'] = encryption_public_key
        if notes is not None:
            contact['notes'] = notes

        contacts_data['contacts'][vault_id] = contact
        self._write_json(self.contacts_path, contacts_data)

        return contact

    def remove_contact(self, vault_id: str) -> bool:
        """
        Remove a contact.

        Args:
            vault_id: Contact's vault ID

        Returns:
            True if contact was removed, False if not found
        """
        contacts_data = self.get_contacts()
        if vault_id in contacts_data['contacts']:
            del contacts_data['contacts'][vault_id]
            self._write_json(self.contacts_path, contacts_data)
            return True
        return False

    def get_contact(self, vault_id: str) -> Optional[dict]:
        """
        Get a specific contact.

        Args:
            vault_id: Contact's vault ID

        Returns:
            Contact dict or None
        """
        return self.get_contacts()['contacts'].get(vault_id)

    def is_known_contact(self, vault_id: str) -> bool:
        """Check if a vault ID is a known contact."""
        return vault_id in self.get_contacts()['contacts']

    def set_quarantine_unknown(self, enabled: bool):
        """
        Set whether to quarantine messages from unknown senders.

        Args:
            enabled: True to quarantine, False to accept
        """
        contacts_data = self.get_contacts()
        contacts_data['quarantine_unknown'] = enabled
        self._write_json(self.contacts_path, contacts_data)

    def should_quarantine(self, sender_vault_id: str) -> bool:
        """
        Check if a message from this sender should be quarantined.

        Args:
            sender_vault_id: Sender's vault ID

        Returns:
            True if message should be quarantined
        """
        contacts_data = self.get_contacts()
        if not contacts_data.get('quarantine_unknown', True):
            return False
        return not self.is_known_contact(sender_vault_id)

    # =========================================================================
    # Message History
    # =========================================================================

    def save_message(self, message: dict, direction: str):
        """
        Save a message to history.

        Args:
            message: The message dict
            direction: 'sent' or 'received'
        """
        msg_id = message.get('envelope', {}).get('id', f"unknown_{uuid.uuid4().hex}")
        timestamp = datetime.now(timezone.utc).isoformat()

        history_entry = {
            'direction': direction,
            'saved_at': timestamp,
            'message': message,
        }

        # Save to history directory
        filename = f"{timestamp.replace(':', '-')}_{direction}_{msg_id}.json"
        filepath = self.history_path / filename
        self._write_json(filepath, history_entry)

    def save_to_quarantine(self, message: dict, reason: str):
        """
        Save a message to quarantine.

        Args:
            message: The message dict
            reason: Reason for quarantine
        """
        msg_id = message.get('envelope', {}).get('id', f"unknown_{uuid.uuid4().hex}")
        timestamp = datetime.now(timezone.utc).isoformat()

        quarantine_entry = {
            'reason': reason,
            'quarantined_at': timestamp,
            'message': message,
        }

        filename = f"{timestamp.replace(':', '-')}_{msg_id}.json"
        filepath = self.quarantine_path / filename
        self._write_json(filepath, quarantine_entry)

    def get_history(self, limit: int = 50) -> List[dict]:
        """
        Get recent message history.

        Args:
            limit: Maximum number of messages to return

        Returns:
            List of history entries, newest first
        """
        entries = []
        for filepath in sorted(self.history_path.glob("*.json"), reverse=True):
            if len(entries) >= limit:
                break
            try:
                entries.append(self._read_json(filepath))
            except Exception:
                continue
        return entries

    def get_quarantine(self, limit: int = 50) -> List[dict]:
        """
        Get quarantined messages.

        Args:
            limit: Maximum number of messages to return

        Returns:
            List of quarantine entries, newest first
        """
        entries = []
        for filepath in sorted(self.quarantine_path.glob("*.json"), reverse=True):
            if len(entries) >= limit:
                break
            try:
                entries.append(self._read_json(filepath))
            except Exception:
                continue
        return entries

    # =========================================================================
    # Server Registration State
    # =========================================================================

    def get_server_state(self, server_url: str) -> Optional[dict]:
        """
        Get registration state for a specific server.

        Args:
            server_url: The relay server URL

        Returns:
            Server state dict or None if not registered
        """
        identity = self.get_identity()
        servers = identity.get('servers', {})
        return servers.get(server_url)

    def set_server_state(self, server_url: str, state: dict):
        """
        Save registration state for a server.

        Args:
            server_url: The relay server URL
            state: State to save (e.g., registered_at, alias)
        """
        identity = self.get_identity()
        if 'servers' not in identity:
            identity['servers'] = {}
        identity['servers'][server_url] = state
        self._write_json(self.identity_path, identity)
        self._identity = identity

    def is_registered(self, server_url: str) -> bool:
        """Check if registered with a specific server."""
        state = self.get_server_state(server_url)
        return state is not None and state.get('registered', False)

    # =========================================================================
    # Helpers
    # =========================================================================

    def _write_json(self, path: Path, data: dict):
        """Write JSON to file."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def _read_json(self, path: Path) -> dict:
        """Read JSON from file."""
        with open(path, 'r') as f:
            return json.load(f)

    def _write_binary(self, path: Path, data: bytes):
        """Write binary data to file."""
        with open(path, 'wb') as f:
            f.write(data)

    def _read_binary(self, path: Path) -> bytes:
        """Read binary data from file."""
        with open(path, 'rb') as f:
            return f.read()

    def export_public_identity(self) -> dict:
        """
        Export public identity for sharing.

        Returns:
            Dict with vault_id and public keys (no private data)
        """
        identity = self.get_identity()
        return {
            'vault_id': identity['vault_id'],
            'alias': identity.get('alias'),
            'signing_public_key': identity['signing_public_key'],
            'encryption_public_key': identity['encryption_public_key'],
        }


def get_default_vault() -> Vault:
    """Get a Vault instance for the default location."""
    return Vault()


def ensure_vault() -> Vault:
    """
    Get the default vault, creating it if it doesn't exist.

    Returns:
        Loaded Vault instance
    """
    vault = get_default_vault()
    if not vault.exists:
        vault.create()
    else:
        vault.load()
    return vault
