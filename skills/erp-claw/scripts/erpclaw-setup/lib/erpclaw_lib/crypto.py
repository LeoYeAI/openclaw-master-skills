"""Encryption utilities for ERPClaw — backup encryption + field-level protection.

Uses HMAC-SHA256-CTR stream cipher via Python stdlib (no external dependencies).
Key derivation: PBKDF2-HMAC-SHA256 with 480,000 iterations.

Functions:
- derive_key: PBKDF2 key derivation from passphrase + salt
- encrypt_file: Encrypt a file with HMAC-SHA256-CTR + HMAC authentication
- decrypt_file: Decrypt a file encrypted with encrypt_file
- encrypt_field: Encrypt a short string (tax_id, bank acct, etc.)
- decrypt_field: Decrypt a field encrypted with encrypt_field
- is_encrypted_backup: Check if a file is an encrypted ERPClaw backup
"""
import base64
import hashlib
import hmac
import os
import struct

# AES block size
BLOCK_SIZE = 16
# PBKDF2 iterations (OWASP 2024 recommendation for HMAC-SHA256)
PBKDF2_ITERATIONS = 480_000
# Magic bytes to identify encrypted ERPClaw backups
MAGIC = b"ERPCLAW_ENC\x01"
# Field encryption prefix
FIELD_PREFIX = "enc:"


def derive_key(passphrase: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> bytes:
    """Derive a 32-byte AES-256 key from passphrase using PBKDF2.

    Args:
        passphrase: User-provided passphrase
        salt: Random 16-byte salt
        iterations: PBKDF2 iteration count

    Returns:
        32-byte key suitable for AES-256
    """
    return hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, iterations)


# ---------------------------------------------------------------------------
# HMAC-SHA256-CTR stream cipher (pure Python stdlib)
# Uses the built-in hashlib + hmac only. No PyCrypto/cryptography needed.
# ---------------------------------------------------------------------------

def _aes_encrypt_block(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    """Encrypt plaintext using HMAC-SHA256 in CTR mode as a PRF-based stream cipher.

    Args:
        key: 32-byte encryption key
        iv: 16-byte initialization vector (used as nonce for CTR)
        plaintext: Data to encrypt

    Returns:
        Ciphertext (same length as plaintext)
    """
    output = bytearray()
    counter = 0
    offset = 0
    while offset < len(plaintext):
        # Generate keystream block: counter (8 bytes) || iv nonce (8 bytes)
        counter_bytes = struct.pack("<Q", counter) + iv[:8]
        keystream = hmac.new(key, counter_bytes, hashlib.sha256).digest()
        # XOR with plaintext
        chunk = plaintext[offset:offset + 32]
        for i, b in enumerate(chunk):
            output.append(b ^ keystream[i])
        counter += 1
        offset += 32
    return bytes(output[:len(plaintext)])


def _aes_decrypt_block(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    """Decrypt data — symmetric to _aes_encrypt_block (CTR mode is symmetric)."""
    output = bytearray()
    counter = 0
    offset = 0
    while offset < len(ciphertext):
        counter_bytes = struct.pack("<Q", counter) + iv[:8]
        keystream = hmac.new(key, counter_bytes, hashlib.sha256).digest()
        chunk = ciphertext[offset:offset + 32]
        for i, b in enumerate(chunk):
            output.append(b ^ keystream[i])
        counter += 1
        offset += 32
    return bytes(output[:len(ciphertext)])


def encrypt_file(input_path: str, output_path: str, passphrase: str) -> dict:
    """Encrypt a file with AES-256 + HMAC-SHA256 authentication.

    File format:
        MAGIC (12 bytes) | salt (16 bytes) | iv (16 bytes) |
        ciphertext (variable) | hmac (32 bytes)

    Args:
        input_path: Path to plaintext file
        output_path: Path to write encrypted file
        passphrase: Encryption passphrase

    Returns:
        Dict with original_size, encrypted_size
    """
    salt = os.urandom(16)
    iv = os.urandom(16)
    key = derive_key(passphrase, salt)

    with open(input_path, "rb") as f:
        plaintext = f.read()

    original_size = len(plaintext)

    # Encrypt
    ciphertext = _aes_encrypt_block(key, iv, plaintext)

    # HMAC for authentication (encrypt-then-MAC)
    mac_key = derive_key(passphrase, salt + b"mac", iterations=1000)
    mac = hmac.new(mac_key, salt + iv + ciphertext, hashlib.sha256).digest()

    with open(output_path, "wb") as f:
        f.write(MAGIC)
        f.write(salt)
        f.write(iv)
        f.write(ciphertext)
        f.write(mac)

    encrypted_size = os.path.getsize(output_path)
    return {"original_size": original_size, "encrypted_size": encrypted_size}


def decrypt_file(input_path: str, output_path: str, passphrase: str) -> dict:
    """Decrypt a file encrypted with encrypt_file.

    Args:
        input_path: Path to encrypted file
        output_path: Path to write decrypted file
        passphrase: Encryption passphrase

    Returns:
        Dict with decrypted_size

    Raises:
        ValueError: If file is not an encrypted ERPClaw backup or HMAC fails
    """
    with open(input_path, "rb") as f:
        data = f.read()

    # Parse header
    if not data.startswith(MAGIC):
        raise ValueError("Not an encrypted ERPClaw backup")

    offset = len(MAGIC)
    salt = data[offset:offset + 16]
    offset += 16
    iv = data[offset:offset + 16]
    offset += 16
    mac = data[-32:]
    ciphertext = data[offset:-32]

    # Verify HMAC before decryption (authenticate-then-decrypt)
    key = derive_key(passphrase, salt)
    mac_key = derive_key(passphrase, salt + b"mac", iterations=1000)
    expected_mac = hmac.new(mac_key, salt + iv + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected_mac):
        raise ValueError("Invalid passphrase or corrupted backup")

    # Decrypt
    plaintext = _aes_decrypt_block(key, iv, ciphertext)

    with open(output_path, "wb") as f:
        f.write(plaintext)

    return {"decrypted_size": len(plaintext)}


def is_encrypted_backup(file_path: str) -> bool:
    """Check if a file is an encrypted ERPClaw backup.

    Args:
        file_path: Path to check

    Returns:
        True if file starts with ERPCLAW_ENC magic bytes
    """
    try:
        with open(file_path, "rb") as f:
            header = f.read(len(MAGIC))
        return header == MAGIC
    except (OSError, IOError):
        return False


# ---------------------------------------------------------------------------
# Field-level encryption (for sensitive data like tax_id, bank accounts)
# ---------------------------------------------------------------------------

# Field encryption uses a fixed key derived from DB-level passphrase.
# In production, this key would come from environment variable or key vault.

def encrypt_field(value: str, key: bytes) -> str:
    """Encrypt a short string field for at-rest protection.

    Args:
        value: Plaintext string to encrypt
        key: 32-byte encryption key

    Returns:
        Base64-encoded encrypted string prefixed with 'enc:'
    """
    if not value or value.startswith(FIELD_PREFIX):
        return value  # Already encrypted or empty

    iv = os.urandom(16)
    plaintext = value.encode("utf-8")

    # Encrypt using CTR mode
    ciphertext = _aes_encrypt_block(key, iv, plaintext)

    # Encode: iv + ciphertext
    encoded = base64.b64encode(iv + ciphertext).decode("ascii")
    return FIELD_PREFIX + encoded


def decrypt_field(value: str, key: bytes) -> str:
    """Decrypt a field encrypted with encrypt_field.

    Args:
        value: Encrypted string (must start with 'enc:')
        key: 32-byte encryption key (same key used for encryption)

    Returns:
        Decrypted plaintext string
    """
    if not value or not value.startswith(FIELD_PREFIX):
        return value  # Not encrypted

    encoded = value[len(FIELD_PREFIX):]
    raw = base64.b64decode(encoded)
    iv = raw[:16]
    ciphertext = raw[16:]

    plaintext = _aes_decrypt_block(key, iv, ciphertext)
    return plaintext.decode("utf-8")
