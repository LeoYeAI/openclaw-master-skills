"""
Tunee model parsing and cache utilities.
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone

from .api_util import API_MODELS, request_tunee_api

CACHE_FILE = os.path.join(os.path.expanduser("~"), ".tunee", "models.json")
TTL_SECONDS = 86400  # 24 hours

# Only Text-to-Music is supported; Music-to-Music (reference audio, custom vocals, etc.) is not yet supported
SUPPORTED_MUSIC_TYPE = ("Text-to-Music", )

# bizType: lyrics = vocals (Song), instrumental = Instrumental
BIZ_TYPE_SONG = "Song"
BIZ_TYPE_INSTRUMENTAL = "Instrumental"



@dataclass
class Capability:
    """Model capability (e.g. Text-to-Music)."""

    id: str
    name: str
    description: str
    gen_type: str  # e.g. Text-to-Music
    music_type: str  # Song / Instrumental
    action: str
    credits_show: str

    def to_dict(self) -> dict:
        """Serialize to cache-compatible dict."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "gen_type": self.gen_type,
            "music_type": self.music_type,
            "action": self.action,
            "credits_show": self.credits_show,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Capability":
        """Parse from dict; compatible with API field names and cache format (gen_type/music_type)."""
        id = d.get("id") or ""
        name = d.get("name") or ""
        description = d.get("description") or ""
        gen_type = d.get("gen_type") or ""
        music_type = d.get("music_type") or ""
        action = d.get("action") or ""
        credits_show = d.get("credits_show") or ""
        return cls(
            id=id,
            name=name,
            description=description,
            gen_type=gen_type,
            music_type=music_type,
            action=action,
            credits_show=credits_show,
        )


@dataclass
class Model:
    """Tunee music generation model."""

    id: str
    name: str
    description: str
    capabilities: list[Capability]
    tags: list[str]

    def to_dict(self) -> dict:
        """Serialize to cache-compatible dict."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "capabilities": [c.to_dict() for c in self.capabilities],
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Model":
        """Parse from dict."""
        caps = d.get("capabilities") or []
        return cls(
            id=d.get("id", ""),
            name=d.get("name", "unknown"),
            description=d.get("description", ""),
            capabilities=[Capability.from_dict(c) for c in caps if isinstance(c, dict)],
            tags=d.get("tags") or [],
        )


def model_supports_biz_type(model: Model, biz_type: str) -> bool:
    """Check if model has Text-to-Music capability for the given bizType."""
    return any(c.music_type == biz_type for c in model.capabilities)


def get_models_by_biz_type(models: list[Model], biz_type: str) -> list[Model]:
    """Return models that support the given bizType."""
    return [m for m in models if model_supports_biz_type(m, biz_type)]


def _parse_capability(c: dict) -> Capability:
    """Parse a single capability entry."""
    return Capability(
        id=c.get("id") or "-",
        name=c.get("name") or "",
        description=c.get("description") or "",
        gen_type=c.get("gen_type") or "",
        music_type=c.get("music_type") or "",
        action=c.get("action") or "",
        credits_show=c.get("creditsShow") or "-",
    )


def parse_models(data: dict) -> list[Model]:
    """Parse model list from response; compatible with multiple structures. Keep only Text-to-Music models."""
    models = data.get("models") or []
    result: list[Model] = []
    for m in models:
        id = m.get("id") or "-"
        name = m.get("name") or "-"
        desc = m.get("description") or ""
        raw_caps = m.get("capabilities") or []
        all_caps = [_parse_capability(c) for c in raw_caps if isinstance(c, dict)]
        t2m_caps = [c for c in all_caps if c.gen_type in SUPPORTED_MUSIC_TYPE]
        if not t2m_caps:
            continue
        result.append(
            Model(
                id=id ,
                name=name,
                description=desc,
                capabilities=t2m_caps,
                tags=m.get("tags") or [],
            )
        )
    return result


def load_models_cache() -> tuple[list[Model] | None, bool]:
    """Load model cache. Returns (models, True) if valid, else (None, False)."""
    if not os.path.isfile(CACHE_FILE):
        return None, False
    try:
        with open(CACHE_FILE, encoding="utf-8") as f:
            data = json.load(f)
        updated_str = data.get("updated_at")
        ttl = data.get("ttl_seconds", TTL_SECONDS)
        models_data = data.get("models")
        if not updated_str or not isinstance(models_data, list):
            return None, False
        updated = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
        if (datetime.now(timezone.utc) - updated).total_seconds() >= ttl:
            return None, False
        return [Model.from_dict(m) for m in models_data], True
    except (json.JSONDecodeError, ValueError, OSError):
        return None, False


def save_models_cache(models: list[Model], ttl_seconds: int = TTL_SECONDS) -> None:
    """Write model list to user directory cache."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "ttl_seconds": ttl_seconds,
                "models": [m.to_dict() for m in models],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


def fetch_models(access_key: str) -> tuple[list[Model], dict]:
    """Request model list from API. Returns (models, raw_data). Raises TuneeAPIError on failure."""
    resp = request_tunee_api(
        API_MODELS, access_key, {"modelTypeList": ["music"]}, timeout=30
    )
    return parse_models(resp.data), resp.raw
