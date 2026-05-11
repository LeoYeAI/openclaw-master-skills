"""First-class project management for Palaia (ADR-008).

Projects are optional containers for grouping related entries.
They are stored in .palaia/projects.json and add a 'project' field
to entry frontmatter.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from palaia.scope import validate_scope


class Project:
    """A project container."""

    def __init__(
        self,
        name: str,
        description: str = "",
        default_scope: str = "team",
        created_at: str | None = None,
        members: list[str] | None = None,
        owner: str | None = None,
    ):
        self.name = name
        self.description = description
        self.default_scope = default_scope
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.members = members or []
        self.owner = owner

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "default_scope": self.default_scope,
            "created_at": self.created_at,
            "members": self.members,
            "owner": self.owner,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            default_scope=data.get("default_scope", "team"),
            created_at=data.get("created_at"),
            members=data.get("members", []),
            owner=data.get("owner"),
        )


class ProjectManager:
    """Manages projects stored in .palaia/projects.json."""

    def __init__(self, palaia_root: Path):
        self.root = palaia_root
        self.projects_file = palaia_root / "projects.json"

    def _load(self) -> dict[str, dict]:
        """Load projects from disk."""
        if not self.projects_file.exists():
            return {}
        try:
            with open(self.projects_file, "r") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return {}
            return data
        except (json.JSONDecodeError, OSError):
            return {}

    def _save(self, data: dict[str, dict]) -> None:
        """Save projects to disk."""
        with open(self.projects_file, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create(
        self,
        name: str,
        description: str = "",
        default_scope: str = "team",
        owner: str | None = None,
    ) -> Project:
        """Create a new project."""
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty.")

        # Validate scope
        if not validate_scope(default_scope):
            raise ValueError(f"Invalid scope: '{default_scope}'.")

        data = self._load()
        if name in data:
            raise ValueError(f"Project '{name}' already exists.")

        project = Project(name=name, description=description, default_scope=default_scope, owner=owner)
        data[name] = project.to_dict()
        self._save(data)
        return project

    def list(self) -> list[Project]:
        """List all projects."""
        data = self._load()
        return [Project.from_dict(v) for v in data.values()]

    def get(self, name: str) -> Project | None:
        """Get a project by name."""
        data = self._load()
        if name not in data:
            return None
        return Project.from_dict(data[name])

    def ensure(self, name: str, default_scope: str = "team") -> Project:
        """Get a project by name, creating it if it doesn't exist.

        This is the recommended way to reference projects from CLI commands
        that accept --project. It avoids the user having to manually create
        projects before using them.
        """
        project = self.get(name)
        if project is not None:
            return project
        return self.create(name=name, default_scope=default_scope)

    def delete(self, name: str, store=None) -> bool:
        """Delete a project. Entries keep their content but lose the project tag."""
        data = self._load()
        if name not in data:
            return False

        del data[name]
        self._save(data)

        # Remove project tag from entries
        if store is not None:
            self._strip_project_from_entries(name, store)

        return True

    def set_scope(self, name: str, scope: str) -> Project:
        """Change a project's default scope."""
        if not validate_scope(scope):
            raise ValueError(f"Invalid scope: '{scope}'.")

        data = self._load()
        if name not in data:
            raise ValueError(f"Project '{name}' not found.")

        data[name]["default_scope"] = scope
        self._save(data)
        return Project.from_dict(data[name])

    def set_owner(self, name: str, owner: str) -> Project:
        """Set or change a project's owner."""
        data = self._load()
        if name not in data:
            raise ValueError(f"Project '{name}' not found.")

        data[name]["owner"] = owner
        self._save(data)
        return Project.from_dict(data[name])

    def clear_owner(self, name: str) -> Project:
        """Remove a project's owner."""
        data = self._load()
        if name not in data:
            raise ValueError(f"Project '{name}' not found.")

        data[name]["owner"] = None
        self._save(data)
        return Project.from_dict(data[name])

    def get_contributors(self, name: str, store) -> list[str]:
        """Get distinct agent names from all entries of a project."""
        entries = self.get_project_entries(name, store)
        agents = set()
        for meta, _body, _tier in entries:
            agent = meta.get("agent")
            if agent:
                agents.add(agent)
        return sorted(agents)

    def _strip_project_from_entries(self, project_name: str, store) -> int:
        """Remove project tag from all entries belonging to a project."""
        from palaia.entry import parse_entry, serialize_entry

        count = 0
        for tier in ("hot", "warm", "cold"):
            tier_dir = store.root / tier
            if not tier_dir.exists():
                continue
            for p in tier_dir.glob("*.md"):
                try:
                    text = p.read_text(encoding="utf-8")
                    meta, body = parse_entry(text)
                    if meta.get("project") == project_name:
                        del meta["project"]
                        new_text = serialize_entry(meta, body)
                        store.write_raw(str(p.relative_to(store.root)), new_text)
                        count += 1
                except (OSError, UnicodeDecodeError):
                    continue
        return count

    def get_project_entries(self, name: str, store) -> list[tuple[dict, str, str]]:
        """Get all entries belonging to a project."""
        from palaia.entry import parse_entry

        results = []
        for tier in ("hot", "warm", "cold"):
            tier_dir = store.root / tier
            if not tier_dir.exists():
                continue
            for p in sorted(tier_dir.glob("*.md")):
                try:
                    text = p.read_text(encoding="utf-8")
                    meta, body = parse_entry(text)
                    if meta.get("project") == name:
                        results.append((meta, body, tier))
                except (OSError, UnicodeDecodeError):
                    continue
        return results
