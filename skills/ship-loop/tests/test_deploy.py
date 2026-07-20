from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shiploop.config import DeployConfig
from shiploop.deploy import get_verifier, verify_deployment, PROVIDER_MAP
from shiploop.providers.base import DeployVerifier, VerificationResult
from shiploop.providers.custom import Verifier as CustomVerifier, _build_curated_env, ALLOWED_ENV_KEYS


class TestGetVerifier:
    def test_returns_vercel_verifier(self):
        config = DeployConfig(provider="vercel")
        verifier = get_verifier(config)
        assert isinstance(verifier, DeployVerifier)

    def test_returns_netlify_verifier(self):
        config = DeployConfig(provider="netlify")
        verifier = get_verifier(config)
        assert isinstance(verifier, DeployVerifier)

    def test_returns_custom_verifier(self):
        config = DeployConfig(provider="custom", script="echo ok")
        verifier = get_verifier(config)
        assert isinstance(verifier, CustomVerifier)

    def test_raises_for_unknown_provider(self):
        config = DeployConfig(provider="unknown")
        with pytest.raises(ValueError, match="Unknown deploy provider"):
            get_verifier(config)

    def test_case_insensitive_provider(self):
        config = DeployConfig(provider="Vercel")
        verifier = get_verifier(config)
        assert isinstance(verifier, DeployVerifier)


class TestCustomVerifier:
    @pytest.mark.asyncio
    async def test_requires_script_field(self):
        config = DeployConfig(provider="custom", script=None)
        verifier = CustomVerifier(config)
        result = await verifier.verify("abc123", config, "https://example.com")
        assert result.success is False
        assert "requires 'script'" in result.details

    @pytest.mark.asyncio
    async def test_successful_script(self):
        config = DeployConfig(provider="custom", script="echo ok", timeout=10)
        verifier = CustomVerifier(config)
        result = await verifier.verify("abc123", config, "https://example.com")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_failed_script(self):
        config = DeployConfig(provider="custom", script="exit 1", timeout=10)
        verifier = CustomVerifier(config)
        result = await verifier.verify("abc123", config, "https://example.com")
        assert result.success is False
        assert "exited 1" in result.details

    @pytest.mark.asyncio
    async def test_script_timeout(self):
        config = DeployConfig(provider="custom", script="sleep 10", timeout=1)
        verifier = CustomVerifier(config)
        result = await verifier.verify("abc123", config, "https://example.com")
        assert result.success is False
        assert "timed out" in result.details


class TestBuildCuratedEnv:
    def test_includes_shiploop_vars(self):
        env = _build_curated_env("abc123", "https://example.com")
        assert env["SHIPLOOP_COMMIT"] == "abc123"
        assert env["SHIPLOOP_SITE"] == "https://example.com"

    def test_only_includes_allowed_keys(self):
        with patch.dict("os.environ", {"PATH": "/usr/bin", "SECRET_KEY": "bad", "HOME": "/home/user"}):
            env = _build_curated_env("abc", "https://site.com")
        assert "PATH" in env
        assert "HOME" in env
        assert "SECRET_KEY" not in env

    def test_extra_env_overrides(self):
        env = _build_curated_env("abc", "https://site.com", extra_env={"CUSTOM": "val"})
        assert env["CUSTOM"] == "val"
