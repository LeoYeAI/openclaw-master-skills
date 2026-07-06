"""
Cryptographic primitives for OpenClaw Messaging.

This module provides:
- Ed25519 signing keypair generation and operations
- X25519 encryption keypair generation
- Hybrid encryption (X25519 + AES-256-GCM)
- Key serialization/deserialization

All cryptographic operations are centralized here for easy auditing.
"""

import os
import base64
import json
from typing import Tuple, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


# Constants
AES_KEY_SIZE = 32  # 256 bits
AES_NONCE_SIZE = 12  # 96 bits for GCM
HKDF_INFO = b"openclaw-messaging-v1"


class CryptoError(Exception):
    """Base exception for cryptographic operations."""
    pass


class SignatureError(CryptoError):
    """Raised when signature verification fails."""
    pass


class DecryptionError(CryptoError):
    """Raised when decryption fails."""
    pass


# =============================================================================
# Key Generation
# =============================================================================

def generate_signing_keypair() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """
    Generate an Ed25519 signing keypair.

    Returns:
        Tuple of (private_key, public_key)
    """
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def generate_encryption_keypair() -> Tuple[X25519PrivateKey, X25519PublicKey]:
    """
    Generate an X25519 encryption keypair.

    Returns:
        Tuple of (private_key, public_key)
    """
    private_key = X25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


# =============================================================================
# Key Serialization
# =============================================================================

def serialize_private_signing_key(key: Ed25519PrivateKey) -> bytes:
    """Serialize Ed25519 private key to raw bytes."""
    return key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )


def serialize_public_signing_key(key: Ed25519PublicKey) -> bytes:
    """Serialize Ed25519 public key to raw bytes."""
    return key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )


def serialize_private_encryption_key(key: X25519PrivateKey) -> bytes:
    """Serialize X25519 private key to raw bytes."""
    return key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )


def serialize_public_encryption_key(key: X25519PublicKey) -> bytes:
    """Serialize X25519 public key to raw bytes."""
    return key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )


def deserialize_private_signing_key(data: bytes) -> Ed25519PrivateKey:
    """Deserialize Ed25519 private key from raw bytes."""
    return Ed25519PrivateKey.from_private_bytes(data)


def deserialize_public_signing_key(data: bytes) -> Ed25519PublicKey:
    """Deserialize Ed25519 public key from raw bytes."""
    return Ed25519PublicKey.from_public_bytes(data)


def deserialize_private_encryption_key(data: bytes) -> X25519PrivateKey:
    """Deserialize X25519 private key from raw bytes."""
    return X25519PrivateKey.from_private_bytes(data)


def deserialize_public_encryption_key(data: bytes) -> X25519PublicKey:
    """Deserialize X25519 public key from raw bytes."""
    return X25519PublicKey.from_public_bytes(data)


# =============================================================================
# Base64 Encoding Helpers
# =============================================================================

def bytes_to_b64(data: bytes) -> str:
    """Encode bytes to URL-safe base64 string."""
    return base64.urlsafe_b64encode(data).decode('ascii')


def b64_to_bytes(data: str) -> bytes:
    """Decode URL-safe base64 string to bytes."""
    return base64.urlsafe_b64decode(data.encode('ascii'))


def public_signing_key_to_b64(key: Ed25519PublicKey) -> str:
    """Convert Ed25519 public key to base64 string."""
    return bytes_to_b64(serialize_public_signing_key(key))


def public_encryption_key_to_b64(key: X25519PublicKey) -> str:
    """Convert X25519 public key to base64 string."""
    return bytes_to_b64(serialize_public_encryption_key(key))


def b64_to_public_signing_key(data: str) -> Ed25519PublicKey:
    """Convert base64 string to Ed25519 public key."""
    return deserialize_public_signing_key(b64_to_bytes(data))


def b64_to_public_encryption_key(data: str) -> X25519PublicKey:
    """Convert base64 string to X25519 public key."""
    return deserialize_public_encryption_key(b64_to_bytes(data))


# =============================================================================
# Signing Operations
# =============================================================================

def sign(private_key: Ed25519PrivateKey, message: bytes) -> bytes:
    """
    Sign a message using Ed25519.

    Args:
        private_key: Ed25519 private key
        message: Message bytes to sign

    Returns:
        64-byte signature
    """
    return private_key.sign(message)


def sign_json(private_key: Ed25519PrivateKey, data: dict) -> str:
    """
    Sign a JSON-serializable dict and return base64 signature.

    The dict is serialized with sorted keys and no whitespace for
    deterministic signing.

    Args:
        private_key: Ed25519 private key
        data: Dict to sign

    Returns:
        Base64-encoded signature
    """
    # ensure_ascii=False keeps unicode as-is (matches Node.js JSON.stringify)
    message = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    signature = sign(private_key, message)
    return bytes_to_b64(signature)


def verify(public_key: Ed25519PublicKey, message: bytes, signature: bytes) -> bool:
    """
    Verify an Ed25519 signature.

    Args:
        public_key: Ed25519 public key
        message: Original message bytes
        signature: Signature to verify

    Returns:
        True if signature is valid

    Raises:
        SignatureError: If verification fails
    """
    try:
        public_key.verify(signature, message)
        return True
    except Exception as e:
        raise SignatureError(f"Signature verification failed: {e}")


def verify_json(public_key: Ed25519PublicKey, data: dict, signature_b64: str) -> bool:
    """
    Verify a signature over a JSON-serializable dict.

    Args:
        public_key: Ed25519 public key
        data: Dict that was signed
        signature_b64: Base64-encoded signature

    Returns:
        True if signature is valid

    Raises:
        SignatureError: If verification fails
    """
    # ensure_ascii=False keeps unicode as-is (matches Node.js JSON.stringify)
    message = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    signature = b64_to_bytes(signature_b64)
    return verify(public_key, message, signature)


# =============================================================================
# Hybrid Encryption (X25519 + AES-256-GCM)
# =============================================================================

def _derive_key(shared_secret: bytes, salt: Optional[bytes] = None) -> bytes:
    """
    Derive an AES key from a shared secret using HKDF.

    Args:
        shared_secret: The ECDH shared secret
        salt: Optional salt (uses zeros if not provided)

    Returns:
        32-byte AES key
    """
    if salt is None:
        salt = b'\x00' * 32

    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=AES_KEY_SIZE,
        salt=salt,
        info=HKDF_INFO,
    )
    return hkdf.derive(shared_secret)


def encrypt(recipient_public_key: X25519PublicKey, plaintext: bytes) -> dict:
    """
    Encrypt data using hybrid encryption (X25519 + AES-256-GCM).

    Process:
    1. Generate ephemeral X25519 keypair
    2. Compute shared secret via ECDH
    3. Derive AES key from shared secret
    4. Encrypt with AES-256-GCM

    Args:
        recipient_public_key: Recipient's X25519 public key
        plaintext: Data to encrypt

    Returns:
        Dict containing:
        - ephemeral_public_key: Base64-encoded ephemeral public key
        - nonce: Base64-encoded nonce
        - ciphertext: Base64-encoded ciphertext (includes auth tag)
    """
    # Generate ephemeral keypair
    ephemeral_private = X25519PrivateKey.generate()
    ephemeral_public = ephemeral_private.public_key()

    # Compute shared secret
    shared_secret = ephemeral_private.exchange(recipient_public_key)

    # Derive AES key
    aes_key = _derive_key(shared_secret)

    # Generate random nonce
    nonce = os.urandom(AES_NONCE_SIZE)

    # Encrypt with AES-GCM
    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    return {
        'ephemeral_public_key': public_encryption_key_to_b64(ephemeral_public),
        'nonce': bytes_to_b64(nonce),
        'ciphertext': bytes_to_b64(ciphertext),
    }


def decrypt(
    recipient_private_key: X25519PrivateKey,
    ephemeral_public_key_b64: str,
    nonce_b64: str,
    ciphertext_b64: str
) -> bytes:
    """
    Decrypt data using hybrid encryption (X25519 + AES-256-GCM).

    Args:
        recipient_private_key: Recipient's X25519 private key
        ephemeral_public_key_b64: Base64-encoded sender's ephemeral public key
        nonce_b64: Base64-encoded nonce
        ciphertext_b64: Base64-encoded ciphertext

    Returns:
        Decrypted plaintext bytes

    Raises:
        DecryptionError: If decryption fails
    """
    try:
        # Deserialize inputs
        ephemeral_public_key = b64_to_public_encryption_key(ephemeral_public_key_b64)
        nonce = b64_to_bytes(nonce_b64)
        ciphertext = b64_to_bytes(ciphertext_b64)

        # Compute shared secret
        shared_secret = recipient_private_key.exchange(ephemeral_public_key)

        # Derive AES key
        aes_key = _derive_key(shared_secret)

        # Decrypt with AES-GCM
        aesgcm = AESGCM(aes_key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)

        return plaintext
    except Exception as e:
        raise DecryptionError(f"Decryption failed: {e}")


def encrypt_json(recipient_public_key: X25519PublicKey, data: dict) -> dict:
    """
    Encrypt a JSON-serializable dict.

    Args:
        recipient_public_key: Recipient's X25519 public key
        data: Dict to encrypt

    Returns:
        Encryption result dict (ephemeral_public_key, nonce, ciphertext)
    """
    plaintext = json.dumps(data, sort_keys=True).encode('utf-8')
    return encrypt(recipient_public_key, plaintext)


def decrypt_json(
    recipient_private_key: X25519PrivateKey,
    encrypted: dict
) -> dict:
    """
    Decrypt to a JSON dict.

    Args:
        recipient_private_key: Recipient's X25519 private key
        encrypted: Dict with ephemeral_public_key, nonce, ciphertext

    Returns:
        Decrypted dict

    Raises:
        DecryptionError: If decryption fails
    """
    plaintext = decrypt(
        recipient_private_key,
        encrypted['ephemeral_public_key'],
        encrypted['nonce'],
        encrypted['ciphertext']
    )
    return json.loads(plaintext.decode('utf-8'))


# =============================================================================
# Challenge-Response Helpers
# =============================================================================

def generate_challenge() -> str:
    """Generate a random challenge for registration."""
    return bytes_to_b64(os.urandom(32))


def sign_challenge(private_key: Ed25519PrivateKey, challenge: str) -> str:
    """Sign a challenge string."""
    return bytes_to_b64(sign(private_key, challenge.encode('utf-8')))


def verify_challenge(public_key: Ed25519PublicKey, challenge: str, signature_b64: str) -> bool:
    """
    Verify a signed challenge.

    Returns:
        True if valid

    Raises:
        SignatureError: If verification fails
    """
    signature = b64_to_bytes(signature_b64)
    return verify(public_key, challenge.encode('utf-8'), signature)
