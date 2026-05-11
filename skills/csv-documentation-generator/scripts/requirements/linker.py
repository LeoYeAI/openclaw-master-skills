"""Git Linker module for CSV Documentation Generator

Links requirements to commits for traceability.
"""

import re
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class CommitLink:
    """Represents a link between a commit and requirements"""

    commit_hash: str
    commit_message: str
    requirements: List[str]
    linked_at: str
    author: Optional[str] = None


class GitLinker:
    """Link requirements to git commits"""

    # Pattern to extract requirement IDs from commit messages
    REQUIREMENT_PATTERN = (
        r"\b(URS-\d{3}|FS-\d{3}|TS-\d{3}|IQ-\d{3}|OQ-\d{3}|PQ-\d{3}|RA-\d{3})\b"
    )

    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path or Path.cwd()
        self.requirements_db = self._load_requirements_db()

    def _load_requirements_db(self) -> Dict[str, Any]:
        """Load requirements database"""
        db_path = self.project_path / "requirements.json"
        if db_path.exists():
            with open(db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"commit_links": []}

    def _save_commit_links(self):
        """Save commit links to database"""
        db_path = self.project_path / "requirements.json"
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(self.requirements_db, f, indent=2, ensure_ascii=False)

    def _get_commit_info(self, commit_hash: str) -> Dict[str, Any]:
        """Get commit information"""
        try:
            result = subprocess.run(
                ["git", "show", commit_hash, "--format=%H%n%an%n%ae%n%B", "-s"],
                capture_output=True,
                text=True,
                cwd=self.project_path,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                return {
                    "hash": lines[0] if len(lines) > 0 else commit_hash,
                    "author": lines[1] if len(lines) > 1 else None,
                    "email": lines[2] if len(lines) > 2 else None,
                    "message": lines[3] if len(lines) > 3 else "",
                }
        except Exception:
            pass

        return {"hash": commit_hash, "author": None, "email": None, "message": ""}

    def extract_requirements_from_message(self, message: str) -> List[str]:
        """Extract requirement IDs from a commit message"""
        matches = re.findall(self.REQUIREMENT_PATTERN, message, re.IGNORECASE)
        return list(set(matches))  # Remove duplicates

    def link_commit(
        self, commit_hash: str, requirements: List[str] = None
    ) -> CommitLink:
        """Link a commit to requirements

        If requirements is None, extracts from commit message.
        """
        commit_info = self._get_commit_info(commit_hash)

        if not requirements:
            requirements = self.extract_requirements_from_message(
                commit_info["message"]
            )

        link = CommitLink(
            commit_hash=commit_info["hash"],
            commit_message=commit_info["message"].split("\n")[0],  # First line only
            requirements=requirements,
            linked_at=datetime.now().isoformat(),
            author=commit_info["author"],
        )

        self.requirements_db.setdefault("commit_links", []).append(asdict(link))
        self._save_commit_links()

        return link

    def unlink_commit(self, commit_hash: str) -> bool:
        """Remove link for a commit"""
        links = self.requirements_db.get("commit_links", [])
        initial_len = len(links)
        self.requirements_db["commit_links"] = [
            link for link in links if link.get("commit_hash") != commit_hash
        ]

        if len(self.requirements_db["commit_links"]) < initial_len:
            self._save_commit_links()
            return True
        return False

    def get_links_for_requirement(self, requirement_id: str) -> List[CommitLink]:
        """Get all commits linked to a requirement"""
        links = []
        for link_data in self.requirements_db.get("commit_links", []):
            if requirement_id in link_data.get("requirements", []):
                links.append(CommitLink(**link_data))
        return links

    def get_links_for_commit(self, commit_hash: str) -> Optional[CommitLink]:
        """Get links for a specific commit"""
        for link_data in self.requirements_db.get("commit_links", []):
            if link_data.get("commit_hash") == commit_hash:
                return CommitLink(**link_data)
        return None

    def get_all_links(self) -> List[CommitLink]:
        """Get all commit links"""
        return [
            CommitLink(**link_data)
            for link_data in self.requirements_db.get("commit_links", [])
        ]

    def link_last_commit(self, requirements: List[str] = None) -> Optional[CommitLink]:
        """Link the last git commit"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_path,
            )
            if result.returncode == 0:
                commit_hash = result.stdout.strip()
                return self.link_commit(commit_hash, requirements)
        except Exception:
            pass
        return None

    def get_recent_commits(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent commits with their linked requirements"""
        try:
            result = subprocess.run(
                ["git", "log", f"-{count}", "--format=%H%n%s"],
                capture_output=True,
                text=True,
                cwd=self.project_path,
            )
            if result.returncode == 0:
                commits = []
                lines = result.stdout.strip().split("\n")
                for i in range(0, len(lines) - 1, 2):
                    if i + 1 < len(lines):
                        commit_hash = lines[i]
                        message = lines[i + 1]
                        reqs = self.extract_requirements_from_message(message)
                        commits.append(
                            {
                                "hash": commit_hash,
                                "message": message,
                                "requirements": reqs,
                                "linked": reqs
                                in [
                                    link.get("requirements")
                                    for link in self.requirements_db.get(
                                        "commit_links", []
                                    )
                                ],
                            }
                        )
                return commits
        except Exception:
            pass
        return []

    def get_traceability_matrix(self) -> List[Dict[str, Any]]:
        """Get requirement-to-commit traceability matrix"""
        matrix = []

        for req in self.requirements_db.get("requirements", []):
            req_id = req.get("id")
            links = self.get_links_for_requirement(req_id)

            matrix.append(
                {
                    "requirement_id": req_id,
                    "requirement_type": req.get("type"),
                    "requirement_description": req.get("description", "")[:50],
                    "priority": req.get("priority"),
                    "status": req.get("status"),
                    "commits": [
                        {"hash": link.commit_hash[:8], "message": link.commit_message}
                        for link in links
                    ],
                    "commit_count": len(links),
                }
            )

        return matrix
