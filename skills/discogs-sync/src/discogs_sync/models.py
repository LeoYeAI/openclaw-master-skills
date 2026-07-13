"""Data models for discogs-sync."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SyncActionType(Enum):
    ADD = "add"
    REMOVE = "remove"
    SKIP = "skip"
    ERROR = "error"


@dataclass
class InputRecord:
    """A single record parsed from an input file."""

    artist: str
    album: str
    format: str | None = None
    year: int | None = None
    notes: str | None = None
    line_number: int | None = None

    def display_name(self) -> str:
        return f"{self.artist} - {self.album}"


@dataclass
class SearchResult:
    """Result of a Discogs search for a single input record."""

    input_record: InputRecord
    release_id: int | None = None
    master_id: int | None = None
    title: str | None = None
    artist: str | None = None
    year: int | None = None
    format: str | None = None
    country: str | None = None
    score: float = 0.0
    matched: bool = False
    error: str | None = None


@dataclass
class SyncAction:
    """A single sync action taken during a sync operation."""

    action: SyncActionType
    input_record: InputRecord | None = None
    release_id: int | None = None
    master_id: int | None = None
    title: str | None = None
    artist: str | None = None
    reason: str | None = None
    error: str | None = None


@dataclass
class SyncReport:
    """Summary of a sync operation."""

    actions: list[SyncAction] = field(default_factory=list)
    total_input: int = 0
    added: int = 0
    removed: int = 0
    skipped: int = 0
    errors: int = 0

    def add_action(self, action: SyncAction) -> None:
        self.actions.append(action)
        match action.action:
            case SyncActionType.ADD:
                self.added += 1
            case SyncActionType.REMOVE:
                self.removed += 1
            case SyncActionType.SKIP:
                self.skipped += 1
            case SyncActionType.ERROR:
                self.errors += 1

    @property
    def success(self) -> bool:
        return self.errors == 0

    @property
    def exit_code(self) -> int:
        if self.errors == 0:
            return 0
        if self.added > 0 or self.removed > 0 or self.skipped > 0:
            return 1  # partial failure
        return 2  # complete failure

    def to_dict(self) -> dict:
        return {
            "summary": {
                "total_input": self.total_input,
                "added": self.added,
                "removed": self.removed,
                "skipped": self.skipped,
                "errors": self.errors,
            },
            "actions": [
                {
                    "action": a.action.value,
                    "artist": a.artist or (a.input_record.artist if a.input_record else None),
                    "title": a.title or (a.input_record.album if a.input_record else None),
                    "release_id": a.release_id,
                    "master_id": a.master_id,
                    "reason": a.reason,
                    "error": a.error,
                }
                for a in self.actions
            ],
        }


@dataclass
class MarketplaceResult:
    """Marketplace stats for a single release version."""

    master_id: int | None = None
    release_id: int | None = None
    title: str | None = None
    artist: str | None = None
    format: str | None = None
    country: str | None = None
    year: int | None = None
    num_for_sale: int = 0
    lowest_price: float | None = None
    currency: str = "USD"
    price_suggestions: dict[str, float] | None = None
    label: str | None = None
    catno: str | None = None
    format_details: str | None = None
    community_have: int | None = None
    community_want: int | None = None

    def to_dict(self) -> dict:
        d = {
            "master_id": self.master_id,
            "release_id": self.release_id,
            "title": self.title,
            "artist": self.artist,
            "format": self.format,
            "country": self.country,
            "year": self.year,
            "num_for_sale": self.num_for_sale,
            "lowest_price": self.lowest_price,
            "currency": self.currency,
        }
        if self.price_suggestions is not None:
            d["price_suggestions"] = self.price_suggestions
        if self.label is not None:
            d["label"] = self.label
        if self.catno is not None:
            d["catno"] = self.catno
        if self.format_details is not None:
            d["format_details"] = self.format_details
        if self.community_have is not None:
            d["community_have"] = self.community_have
        if self.community_want is not None:
            d["community_want"] = self.community_want
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "MarketplaceResult":
        return cls(
            master_id=d.get("master_id"),
            release_id=d.get("release_id"),
            title=d.get("title"),
            artist=d.get("artist"),
            format=d.get("format"),
            country=d.get("country"),
            year=d.get("year"),
            num_for_sale=d.get("num_for_sale", 0),
            lowest_price=d.get("lowest_price"),
            currency=d.get("currency", "USD"),
            price_suggestions=d.get("price_suggestions"),
            label=d.get("label"),
            catno=d.get("catno"),
            format_details=d.get("format_details"),
            community_have=d.get("community_have"),
            community_want=d.get("community_want"),
        )


@dataclass
class WantlistItem:
    """An item in the user's wantlist."""

    release_id: int
    master_id: int | None = None
    title: str | None = None
    artist: str | None = None
    format: str | None = None
    year: int | None = None
    notes: str | None = None

    @classmethod
    def from_dict(cls, d: dict) -> "WantlistItem":
        return cls(
            release_id=d["release_id"],
            master_id=d.get("master_id"),
            title=d.get("title"),
            artist=d.get("artist"),
            format=d.get("format"),
            year=d.get("year"),
            notes=d.get("notes"),
        )

    def to_dict(self) -> dict:
        return {
            "release_id": self.release_id,
            "master_id": self.master_id,
            "title": self.title,
            "artist": self.artist,
            "format": self.format,
            "year": self.year,
            "notes": self.notes,
        }


@dataclass
class CollectionItem:
    """An item in the user's collection."""

    instance_id: int
    release_id: int
    master_id: int | None = None
    folder_id: int = 1
    title: str | None = None
    artist: str | None = None
    format: str | None = None
    year: int | None = None

    @classmethod
    def from_dict(cls, d: dict) -> "CollectionItem":
        return cls(
            instance_id=d["instance_id"],
            release_id=d["release_id"],
            master_id=d.get("master_id"),
            folder_id=d.get("folder_id", 1),
            title=d.get("title"),
            artist=d.get("artist"),
            format=d.get("format"),
            year=d.get("year"),
        )

    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "release_id": self.release_id,
            "master_id": self.master_id,
            "folder_id": self.folder_id,
            "title": self.title,
            "artist": self.artist,
            "format": self.format,
            "year": self.year,
        }
