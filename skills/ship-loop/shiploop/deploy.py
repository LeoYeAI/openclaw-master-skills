from __future__ import annotations

import importlib
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import DeployConfig

from .providers.base import DeployVerifier, VerificationResult

logger = logging.getLogger("shiploop.deploy")

PROVIDER_MAP = {
    "vercel": "shiploop.providers.vercel",
    "netlify": "shiploop.providers.netlify",
    "custom": "shiploop.providers.custom",
}


def get_verifier(config: DeployConfig) -> DeployVerifier:
    provider = config.provider.lower()
    module_path = PROVIDER_MAP.get(provider)
    if not module_path:
        raise ValueError(f"Unknown deploy provider: {provider}. Available: {list(PROVIDER_MAP.keys())}")

    try:
        module = importlib.import_module(module_path)
        verifier_class = getattr(module, "Verifier")
        return verifier_class(config)
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Failed to load provider '{provider}': {e}") from e


async def verify_deployment(
    config: DeployConfig,
    commit_hash: str,
    site_url: str,
) -> VerificationResult:
    verifier = get_verifier(config)
    return await verifier.verify(commit_hash, config, site_url)
