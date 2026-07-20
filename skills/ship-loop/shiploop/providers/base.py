from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from shiploop.config import DeployConfig


class VerificationResult(BaseModel):
    success: bool
    deploy_url: str | None = None
    details: str = ""
    duration_seconds: float = 0


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
