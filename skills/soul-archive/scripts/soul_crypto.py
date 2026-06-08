#!/usr/bin/env python3
"""
🔐 Soul Archive Encryption Module

Provides transparent encryption/decryption for soul archive data files.

Algorithm: AES-256-GCM (authenticated encryption)
Key derivation: PBKDF2-HMAC-SHA256 (600,000 iterations)
Each file has its own random IV (nonce), stored alongside the ciphertext.

Encrypted file format (binary):
  [16 bytes salt][12 bytes nonce][N bytes ciphertext+tag]

Usage:
  from soul_crypto import SoulCrypto

  crypto = SoulCrypto(password="user_password", salt=b"...")
  # or
  crypto = SoulCrypto.from_config(config_dict, password="user_password")

  encrypted = crypto.encrypt_json({"key": "value"})
  decrypted = crypto.decrypt_json(encrypted)

  crypto.encrypt_file(Path("data.json"))  # in-place encrypt
  crypto.decrypt_file(Path("data.json"))  # in-place decrypt

Cross-platform: uses only Python standard library + cryptography package
"""

import base64
import getpass
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Optional, Union


# ============================================================
# Constants
# ============================================================

SALT_SIZE = 16          # 128-bit salt
NONCE_SIZE = 12         # 96-bit nonce (GCM standard)
KEY_SIZE = 32           # 256-bit key
KDF_ITERATIONS = 600_000  # OWASP 2023 recommendation for PBKDF2-SHA256
ENCRYPTED_MARKER = b"SOUL"  # Magic bytes to identify encrypted files


# ============================================================
# Core Crypto Class
# ============================================================

class SoulCrypto:
    """
    Handles AES-256-GCM encryption/decryption for soul archive data.

    Uses PBKDF2-HMAC-SHA256 for key derivation from password + salt.
    Each encrypt operation generates a fresh random nonce.
    """

    def __init__(self, password: str, salt: bytes):
        """
        Initialize with password and salt.

        Args:
            password: User's password string
            salt: 16-byte salt (stored in config.json)
        """
        self._key = self._derive_key(password, salt)
        self._salt = salt

    @staticmethod
    def generate_salt() -> bytes:
        """Generate a cryptographically secure random salt."""
        return os.urandom(SALT_SIZE)

    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        """Derive a 256-bit key from password using PBKDF2-HMAC-SHA256."""
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations=KDF_ITERATIONS,
            dklen=KEY_SIZE
        )

    @classmethod
    def from_config(cls, config: dict, password: str) -> "SoulCrypto":
        """
        Create SoulCrypto from config.json data.

        Args:
            config: The config dict (must have encryption_salt)
            password: User's password
        """
        salt_b64 = config.get("encryption_salt")
        if not salt_b64:
            raise ValueError("config.json 中缺少 encryption_salt 字段")
        salt = base64.b64decode(salt_b64)
        return cls(password=password, salt=salt)

    def verify_password(self, config: dict) -> bool:
        """
        Verify password against stored verification hash.

        Args:
            config: config dict with encryption_verify field
        Returns:
            True if password is correct
        """
        verify_b64 = config.get("encryption_verify")
        if not verify_b64:
            return True  # No verification hash stored, skip check
        verify_data = base64.b64decode(verify_b64)
        # verify_data = encrypt("soul-archive-verify")
        try:
            plaintext = self._decrypt_bytes(verify_data)
            return plaintext == b"soul-archive-verify"
        except Exception:
            return False

    def create_verify_token(self) -> str:
        """Create a verification token for password validation."""
        encrypted = self._encrypt_bytes(b"soul-archive-verify")
        return base64.b64encode(encrypted).decode("ascii")

    # ---- Low-level encrypt/decrypt ----

    def _encrypt_bytes(self, plaintext: bytes) -> bytes:
        """
        Encrypt bytes using AES-256-GCM.

        Returns: nonce (12 bytes) + ciphertext + tag (16 bytes)
        """
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            _require_cryptography()
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        nonce = os.urandom(NONCE_SIZE)
        aesgcm = AESGCM(self._key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext

    def _decrypt_bytes(self, data: bytes) -> bytes:
        """
        Decrypt bytes encrypted with _encrypt_bytes.

        Args:
            data: nonce (12 bytes) + ciphertext + tag
        Returns:
            Decrypted plaintext bytes
        """
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            _require_cryptography()
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        if len(data) < NONCE_SIZE + 16:  # nonce + minimum tag
            raise ValueError("加密数据格式错误：数据太短")

        nonce = data[:NONCE_SIZE]
        ciphertext = data[NONCE_SIZE:]
        aesgcm = AESGCM(self._key)
        return aesgcm.decrypt(nonce, ciphertext, None)

    # ---- JSON-level encrypt/decrypt ----

    def encrypt_json(self, data: dict) -> bytes:
        """
        Encrypt a dict as JSON → UTF-8 bytes → AES-256-GCM.

        Returns: MARKER(4) + nonce(12) + ciphertext+tag
        """
        plaintext = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        encrypted = self._encrypt_bytes(plaintext)
        return ENCRYPTED_MARKER + encrypted

    def decrypt_json(self, data: bytes) -> dict:
        """
        Decrypt bytes back to a dict.

        Args:
            data: MARKER(4) + nonce(12) + ciphertext+tag
        Returns:
            Decrypted dict
        """
        if not data.startswith(ENCRYPTED_MARKER):
            raise ValueError("不是有效的加密数据（缺少 SOUL 标记）")
        encrypted = data[len(ENCRYPTED_MARKER):]
        plaintext = self._decrypt_bytes(encrypted)
        return json.loads(plaintext.decode("utf-8"))

    # ---- File-level encrypt/decrypt ----

    def encrypt_file(self, path: Path) -> None:
        """
        Encrypt a JSON file in-place.
        If file is already encrypted, skip it.
        """
        raw = path.read_bytes()
        if raw.startswith(ENCRYPTED_MARKER):
            return  # Already encrypted
        # Parse to validate it's valid JSON first
        try:
            data = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return  # Not a JSON file, skip
        encrypted = self.encrypt_json(data)
        path.write_bytes(encrypted)

    def decrypt_file(self, path: Path) -> dict:
        """
        Read and decrypt a file, return the dict.
        If file is not encrypted (plain JSON), just parse it.
        Does NOT modify the file on disk.
        """
        raw = path.read_bytes()
        if raw.startswith(ENCRYPTED_MARKER):
            return self.decrypt_json(raw)
        else:
            # Plain text JSON — just parse it
            return json.loads(raw.decode("utf-8"))

    def encrypt_file_save(self, path: Path, data: dict) -> None:
        """
        Encrypt a dict and write to file.
        """
        encrypted = self.encrypt_json(data)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encrypted)

    # ---- JSONL support ----

    def encrypt_jsonl_line(self, record: dict) -> bytes:
        """Encrypt a single JSONL record. Returns base64-encoded line + newline."""
        plaintext = json.dumps(record, ensure_ascii=False).encode("utf-8")
        encrypted = self._encrypt_bytes(plaintext)
        return base64.b64encode(ENCRYPTED_MARKER + encrypted) + b"\n"

    def decrypt_jsonl_line(self, line: bytes) -> dict:
        """Decrypt a single JSONL line (base64 encoded)."""
        line = line.strip()
        if not line:
            raise ValueError("空行")
        try:
            # Try base64 decode first (encrypted line)
            raw = base64.b64decode(line)
            if raw.startswith(ENCRYPTED_MARKER):
                return self.decrypt_json(raw)
        except Exception:
            pass
        # Fallback: plain text JSON line
        return json.loads(line.decode("utf-8"))

    def append_encrypted_jsonl(self, path: Path, record: dict) -> None:
        """Append an encrypted record to a JSONL file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "ab") as f:
            f.write(self.encrypt_jsonl_line(record))

    def read_encrypted_jsonl(self, path: Path) -> list:
        """Read all records from an encrypted JSONL file."""
        records = []
        if not path.exists():
            return records
        with open(path, "rb") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(self.decrypt_jsonl_line(line))
                except Exception:
                    # Try plain JSON fallback
                    try:
                        records.append(json.loads(line.decode("utf-8")))
                    except Exception:
                        continue
        return records


# ============================================================
# Utility Functions
# ============================================================

def is_file_encrypted(path: Path) -> bool:
    """Check if a file is encrypted (starts with SOUL marker)."""
    if not path.exists():
        return False
    with open(path, "rb") as f:
        header = f.read(len(ENCRYPTED_MARKER))
    return header == ENCRYPTED_MARKER


def is_jsonl_encrypted(path: Path) -> bool:
    """Check if a JSONL file has encrypted lines."""
    if not path.exists():
        return False
    with open(path, "rb") as f:
        first_line = f.readline().strip()
    if not first_line:
        return False
    try:
        raw = base64.b64decode(first_line)
        return raw.startswith(ENCRYPTED_MARKER)
    except Exception:
        return False


def prompt_password(confirm: bool = False) -> str:
    """
    Interactively prompt user for password.

    Args:
        confirm: If True, ask for password twice to confirm
    Returns:
        Password string
    """
    # Check environment variable first
    env_pw = os.environ.get("SOUL_PASSWORD")
    if env_pw:
        return env_pw

    password = getpass.getpass("🔐 请输入灵魂存档密码: ")
    if not password:
        print("❌ 密码不能为空")
        sys.exit(1)

    if confirm:
        password2 = getpass.getpass("🔐 请再次输入密码确认: ")
        if password != password2:
            print("❌ 两次输入的密码不一致")
            sys.exit(1)

    return password


def get_crypto_from_config(config: dict, password: str = None) -> Optional[SoulCrypto]:
    """
    Get a SoulCrypto instance from config, or None if encryption is disabled.

    Args:
        config: config.json dict
        password: Password string. If None, will prompt interactively.
    Returns:
        SoulCrypto instance or None
    """
    if not config.get("encryption"):
        return None

    if password is None:
        password = prompt_password()

    crypto = SoulCrypto.from_config(config, password)

    # Verify password
    if not crypto.verify_password(config):
        print("❌ 密码错误")
        sys.exit(1)

    return crypto


def _require_cryptography():
    """Check if cryptography package is installed, give helpful error if not."""
    try:
        import cryptography  # noqa: F401
    except ImportError:
        print("❌ 加密功能需要安装 cryptography 包:")
        print("   pip install cryptography")
        print()
        print("   或者: pip3 install cryptography")
        sys.exit(1)


# ============================================================
# Encrypt/Decrypt entire soul archive
# ============================================================

# Files that should be encrypted (contain sensitive data)
SENSITIVE_FILES = [
    "identity/basic_info.json",
    "identity/personality.json",
    "style/language.json",
    "style/communication.json",
    "memory/semantic/topics.json",
    "memory/semantic/knowledge.json",
    "memory/emotional/patterns.json",
    "relationships/people.json",
]

# JSONL files that should be encrypted
SENSITIVE_JSONL = [
    "soul_changelog.jsonl",
]

# Files that stay plain text (not sensitive)
PLAIN_FILES = [
    "config.json",
    "profile.json",
]


def encrypt_archive(soul_dir: Path, crypto: SoulCrypto) -> list:
    """
    Encrypt all sensitive files in a soul archive.

    Returns list of encrypted file paths.
    """
    encrypted = []

    # Encrypt JSON files
    for rel_path in SENSITIVE_FILES:
        fpath = soul_dir / rel_path
        if fpath.exists() and not is_file_encrypted(fpath):
            crypto.encrypt_file(fpath)
            encrypted.append(str(rel_path))

    # Encrypt JSONL files
    for rel_path in SENSITIVE_JSONL:
        fpath = soul_dir / rel_path
        if fpath.exists() and not is_jsonl_encrypted(fpath):
            _encrypt_jsonl_file(fpath, crypto)
            encrypted.append(str(rel_path))

    # Encrypt episodic memory JSONL files
    ep_dir = soul_dir / "memory" / "episodic"
    if ep_dir.exists():
        for jl in ep_dir.glob("*.jsonl"):
            if not is_jsonl_encrypted(jl):
                _encrypt_jsonl_file(jl, crypto)
                encrypted.append(str(jl.relative_to(soul_dir)))

    return encrypted


def decrypt_archive(soul_dir: Path, crypto: SoulCrypto) -> list:
    """
    Decrypt all encrypted files in a soul archive back to plain text.

    Returns list of decrypted file paths.
    """
    decrypted = []

    # Decrypt JSON files
    for rel_path in SENSITIVE_FILES:
        fpath = soul_dir / rel_path
        if fpath.exists() and is_file_encrypted(fpath):
            data = crypto.decrypt_file(fpath)
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            decrypted.append(str(rel_path))

    # Decrypt JSONL files
    for rel_path in SENSITIVE_JSONL:
        fpath = soul_dir / rel_path
        if fpath.exists() and is_jsonl_encrypted(fpath):
            _decrypt_jsonl_file(fpath, crypto)
            decrypted.append(str(rel_path))

    # Decrypt episodic memory JSONL files
    ep_dir = soul_dir / "memory" / "episodic"
    if ep_dir.exists():
        for jl in ep_dir.glob("*.jsonl"):
            if is_jsonl_encrypted(jl):
                _decrypt_jsonl_file(jl, crypto)
                decrypted.append(str(jl.relative_to(soul_dir)))

    return decrypted


def _encrypt_jsonl_file(path: Path, crypto: SoulCrypto) -> None:
    """Encrypt a plain JSONL file in-place."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    with open(path, "wb") as f:
        for record in records:
            f.write(crypto.encrypt_jsonl_line(record))


def _decrypt_jsonl_file(path: Path, crypto: SoulCrypto) -> None:
    """Decrypt an encrypted JSONL file in-place back to plain text."""
    records = crypto.read_encrypted_jsonl(path)
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
