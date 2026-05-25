"""Puzle Reading Client SDK

Provides a Python interface to Puzle's reading analysis platform.
Supports creating readings from URLs, HTML content, and local files,
plus semantic search and listing.

Requirements: requests (pip install requests)
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

# Token storage location: ~/.config/puzle/config.json
CONFIG_DIR = Path.home() / ".config" / "puzle"
CONFIG_FILE = CONFIG_DIR / "config.json"
ENV_TOKEN_KEY = "PUZLE_TOKEN"
ENV_BASE_URL_KEY = "PUZLE_BASE_URL"
DEFAULT_BASE_URL = "https://read-web-test.puzle.com.cn/api/v1"


class PuzleAPIError(Exception):
    """API call returned a non-2xx response."""

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"PuzleAPIError({code}): {message}")


class PuzleTimeoutError(Exception):
    """Polling timed out waiting for reading to complete."""


@dataclass
class ReadingResult:
    """Lightweight result returned immediately after creating a reading."""

    reading_id: int
    resource_type: str  # "link" | "file"
    status: str
    task_id: int
    web_url: str  # e.g. "https://read.puzle.com.cn/read/42?type=link&task_id=100"
    puzle_id: int | None = None


class PuzleReadingClient:
    """Client for the Puzle Reading API.

    Token resolution order:
    1. Explicit ``token`` argument
    2. Environment variable ``PUZLE_TOKEN``
    3. Config file ``~/.config/puzle/config.json``

    If no token is found, raises ``ValueError``.
    """

    def __init__(
        self,
        token: str | None = None,
        base_url: str | None = None,
    ) -> None:
        resolved_token = token or self.load_token()
        if not resolved_token:
            raise ValueError(
                "No Puzle token found. Provide token= argument, "
                f"set {ENV_TOKEN_KEY} environment variable, "
                "or run PuzleReadingClient.save_token('your-token')."
            )
        resolved_base_url = (
            base_url or os.environ.get(ENV_BASE_URL_KEY) or self._load_config().get("base_url") or DEFAULT_BASE_URL
        )
        self._base_url = resolved_base_url.rstrip("/")
        # Derive web host from API base URL: "https://host/api/v1" → "https://host"
        self._web_host = self._base_url.split("/api/")[0]
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {resolved_token}",
                "Content-Type": "application/json",
            }
        )

    # ------------------------------------------------------------------
    # Token management
    # ------------------------------------------------------------------

    @staticmethod
    def save_token(token: str, base_url: str | None = None) -> Path:
        """Save token to ~/.config/puzle/config.json for future use.

        Returns the path to the config file.
        """
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config: dict[str, str] = {}
        if CONFIG_FILE.exists():
            try:
                config = json.loads(CONFIG_FILE.read_text())
            except (json.JSONDecodeError, OSError):
                config = {}
        config["token"] = token
        if base_url is not None:
            config["base_url"] = base_url
        CONFIG_FILE.write_text(json.dumps(config, indent=2))
        CONFIG_FILE.chmod(0o600)  # owner-only read/write
        return CONFIG_FILE

    @staticmethod
    def load_token() -> str | None:
        """Load token from environment variable or config file.

        Resolution order:
        1. PUZLE_TOKEN environment variable
        2. ~/.config/puzle/config.json → "token" field
        """
        env_token = os.environ.get(ENV_TOKEN_KEY)
        if env_token:
            return env_token
        config = PuzleReadingClient._load_config()
        return config.get("token")

    @staticmethod
    def _load_config() -> dict[str, str]:
        if CONFIG_FILE.exists():
            try:
                return json.loads(CONFIG_FILE.read_text())
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    @staticmethod
    def token_is_configured() -> bool:
        """Check whether a token is available (env var or config file)."""
        return PuzleReadingClient.load_token() is not None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Send an HTTP request and return parsed JSON. Raises PuzleAPIError on failure."""
        url = f"{self._base_url}{path}"
        resp = self._session.request(method, url, **kwargs)
        if not resp.ok:
            try:
                body = resp.json()
                code = body.get("code", resp.status_code)
                message = body.get("message", resp.text)
            except Exception:
                code = resp.status_code
                message = resp.text
            raise PuzleAPIError(code=code, message=message)
        return resp.json()

    def _to_reading_result(self, item: dict[str, Any]) -> ReadingResult:
        reading_id = item["id"]
        resource_type = item["resource_type"]
        task_id = item["task_id"]
        return ReadingResult(
            reading_id=reading_id,
            resource_type=resource_type,
            status=item["status"],
            task_id=task_id,
            web_url=f"{self._web_host}/read/{reading_id}?type={resource_type}&task_id={task_id}",
            puzle_id=item.get("puzle_id"),
        )

    # ------------------------------------------------------------------
    # Create readings
    # ------------------------------------------------------------------

    def create_reading_from_url(self, url: str) -> ReadingResult:
        """Create a reading from a URL.

        Processing is async — call ``wait_for_reading()`` to get the full content.
        """
        data = self._request("POST", "/reading/link", json={"url": url})
        return self._to_reading_result(data["data"])

    def create_reading_from_html(
        self,
        url: str,
        title: str,
        content: str,
        text_content: str,
        *,
        excerpt: str | None = None,
        byline: str | None = None,
        site_name: str | None = None,
        published_time: str | None = None,
    ) -> ReadingResult:
        """Create a reading from pre-fetched HTML content.

        Internally performs two API calls:
        1. Save content to obtain a link_id
        2. Create a reading with that link_id

        This skips the fetching phase, so processing is faster than URL-based creation.
        """
        # Step 1: save content
        payload: dict[str, Any] = {
            "url": url,
            "title": title,
            "content": content,
            "text_content": text_content,
        }
        for key, value in [
            ("excerpt", excerpt),
            ("byline", byline),
            ("site_name", site_name),
            ("published_time", published_time),
        ]:
            if value is not None:
                payload[key] = value

        save_data = self._request("POST", "/link/save-content", json=payload)
        link_id = save_data["data"]["id"]

        # Step 2: create reading from saved link
        data = self._request("POST", "/reading/link", json={"link_id": link_id})
        return self._to_reading_result(data["data"])

    def create_reading_from_file(self, file_path: str) -> ReadingResult:
        """Create a reading from a local file.

        Internally performs three steps:
        1. Request a pre-signed upload URL from the server
        2. Upload file binary to S3
        3. Create a reading from the uploaded file

        Supported file types: PDF, TXT, MD, CSV, JPG, PNG, WebP, GIF, MP3, WAV
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_bytes = path.read_bytes()
        content_hash = hashlib.md5(file_bytes).hexdigest()
        file_size = len(file_bytes)
        filename = path.name

        # Step 1: get pre-signed upload URL
        upload_data = self._request(
            "POST",
            "/file/upload-url",
            json={
                "filename": filename,
                "content_hash": content_hash,
                "file_size_bytes": file_size,
            },
        )
        upload_info = upload_data["data"]
        upload_url: str = upload_info["upload_url"]
        file_key: str = upload_info["file_key"]

        # Step 2: upload binary to S3
        put_resp = requests.put(
            upload_url,
            data=file_bytes,
            headers={"Content-Type": "application/octet-stream"},
        )
        if not put_resp.ok:
            raise PuzleAPIError(
                code=put_resp.status_code,
                message=f"S3 upload failed: {put_resp.text}",
            )

        # Step 3: create reading from uploaded file
        data = self._request(
            "POST",
            "/reading/file/from-upload",
            json={
                "file_key": file_key,
                "filename": filename,
                "content_hash": content_hash,
            },
        )
        return self._to_reading_result(data["data"])

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get_reading_detail(self, reading_id: int, resource_type: str) -> dict[str, Any]:
        """Get full reading detail including content (when status is done).

        Routes to the correct endpoint based on resource_type:
        - "link" → GET /reading/link/{id}
        - "file" → GET /reading/file/{id}
        """
        if resource_type == "link":
            return self._request("GET", f"/reading/link/{reading_id}")
        elif resource_type == "file":
            return self._request("GET", f"/reading/file/{reading_id}")
        else:
            raise ValueError(f"Unknown resource_type: {resource_type!r}. Expected 'link' or 'file'.")

    def wait_for_reading(
        self,
        reading_id: int,
        resource_type: str,
        *,
        poll_interval: float = 3.0,
        timeout: float = 120.0,
    ) -> dict[str, Any]:
        """Poll until reading processing completes.

        Returns the full detail dict when status becomes "done".
        Raises PuzleAPIError if status becomes "fail".
        Raises PuzleTimeoutError if timeout is exceeded.
        """
        start = time.monotonic()
        while True:
            detail = self.get_reading_detail(reading_id, resource_type)
            status = detail["data"]["status"]
            if status == "done":
                return detail
            if status == "fail":
                raise PuzleAPIError(
                    code=500,
                    message=f"Reading {reading_id} processing failed",
                )
            elapsed = time.monotonic() - start
            if elapsed > timeout:
                raise PuzleTimeoutError(
                    f"Reading {reading_id} did not complete within {timeout}s (last status: {status})"
                )
            time.sleep(poll_interval)

    def list_readings(self, page: int = 1, page_size: int = 10) -> dict[str, Any]:
        """List readings with pagination.

        Returns a mixed list of link and file readings, sorted by last_modify_time desc.
        """
        return self._request(
            "GET",
            "/reading/items",
            params={"page": page, "page_size": page_size},
        )

    def search(
        self,
        query: str,
        *,
        reading_ids: list[int] | None = None,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """RAG semantic search across readings.

        Args:
            query: Natural language search query.
            reading_ids: Optional list of reading IDs to restrict search scope.
            top_k: Maximum number of results to return (default 5).

        Returns dict with items containing: reading_id, reading_title,
        resource_type, chunk_text, score.
        """
        payload: dict[str, Any] = {"query": query, "top_k": top_k}
        if reading_ids is not None:
            payload["reading_ids"] = reading_ids
        return self._request("POST", "/reading/search", json=payload)
