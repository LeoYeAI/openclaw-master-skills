from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING
from urllib.request import Request, urlopen
from urllib.error import URLError

from .base import DeployVerifier, VerificationResult

if TYPE_CHECKING:
    from shiploop.config import DeployConfig

logger = logging.getLogger("shiploop.deploy.vercel")

POLL_INTERVAL = 10
MAX_RETRIES = 3


class Verifier(DeployVerifier):
    async def verify(
        self,
        commit_hash: str,
        config: DeployConfig,
        site_url: str,
    ) -> VerificationResult:
        start = time.monotonic()
        timeout = config.timeout
        deploy_header = config.deploy_header or "x-vercel-deployment-url"

        deadline = start + timeout
        last_error = ""

        while time.monotonic() < deadline:
            for route in config.routes:
                url = site_url.rstrip("/") + route
                try:
                    result = await asyncio.to_thread(self._check_url, url, deploy_header, config.marker)
                    if result.success:
                        result.duration_seconds = time.monotonic() - start
                        return result
                    last_error = result.details
                except Exception as e:
                    last_error = str(e)

            await asyncio.sleep(POLL_INTERVAL)

        return VerificationResult(
            success=False,
            details=f"Timed out after {timeout}s. Last error: {last_error}",
            duration_seconds=time.monotonic() - start,
        )

    def _check_url(self, url: str, deploy_header: str, marker: str | None) -> VerificationResult:
        req = Request(url, method="GET")
        req.add_header("User-Agent", "shiploop/4.0.0")

        try:
            with urlopen(req, timeout=15) as resp:
                status = resp.status
                headers = {k.lower(): v for k, v in resp.getheaders()}
                body = resp.read(8192).decode(errors="replace")
        except URLError as e:
            return VerificationResult(success=False, details=f"Request failed: {e}")

        if status != 200:
            return VerificationResult(success=False, details=f"HTTP {status} for {url}")

        deploy_url = headers.get(deploy_header.lower())

        if marker and marker not in body:
            return VerificationResult(
                success=False,
                deploy_url=deploy_url,
                details=f"Marker '{marker}' not found in response body",
            )

        return VerificationResult(
            success=True,
            deploy_url=deploy_url or url,
            details=f"HTTP 200 OK",
        )
