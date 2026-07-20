---
title: Adding a Deploy Provider
description: How to contribute a new deployment verification provider
---

Ship Loop uses a plugin system for deploy verification. Adding a new provider is one of the easiest ways to contribute.

## 1. Create the Provider

Create a new file at `shiploop/providers/your_provider.py`:

```python
from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

from .base import DeployVerifier, VerificationResult

if TYPE_CHECKING:
    from shiploop.config import DeployConfig


class YourProviderVerifier(DeployVerifier):
    async def verify(
        self,
        commit_hash: str,
        config: DeployConfig,
        site_url: str,
    ) -> VerificationResult:
        start = time.monotonic()
        timeout = config.timeout

        while time.monotonic() - start < timeout:
            try:
                # Your verification logic here
                # Check if the deployment is live and serving
                # the correct version

                return VerificationResult(
                    success=True,
                    deploy_url=site_url,
                    details="Deployment verified",
                    duration_seconds=time.monotonic() - start,
                )
            except Exception:
                await asyncio.sleep(10)

        return VerificationResult(
            success=False,
            details=f"Timed out after {timeout}s",
            duration_seconds=time.monotonic() - start,
        )
```

## 2. The Base Class

Your provider must subclass `DeployVerifier` from `shiploop/providers/base.py`:

```python
class DeployVerifier(ABC):
    def __init__(self, config: DeployConfig):
        self.deploy_config = config

    @abstractmethod
    async def verify(
        self,
        commit_hash: str,
        config: DeployConfig,
        site_url: str,
    ) -> VerificationResult: ...
```

The `VerificationResult` model:

```python
class VerificationResult(BaseModel):
    success: bool
    deploy_url: str | None = None
    details: str = ""
    duration_seconds: float = 0
```

## 3. Register the Provider

Add your provider to `shiploop/deploy.py` so it's loaded when `provider: your_provider` is set in config.

## 4. Add Tests

Create `tests/test_your_provider.py` with at least:
- A test for successful verification
- A test for timeout handling
- A test for error handling

## 5. Update Docs

Add your provider to the [Deploy Providers](/ship-loop/reference/providers/) reference page.

## Existing Providers for Reference

- `shiploop/providers/vercel.py` — HTTP polling + header verification
- `shiploop/providers/netlify.py` — HTTP polling + header verification  
- `shiploop/providers/custom.py` — External script execution

## Tips

- Use `asyncio.sleep()` for polling intervals (don't block the event loop)
- Return partial information in `details` even on failure (helps debugging)
- Track `duration_seconds` for the budget reporter
- Don't add external dependencies if possible (keep Ship Loop light)
