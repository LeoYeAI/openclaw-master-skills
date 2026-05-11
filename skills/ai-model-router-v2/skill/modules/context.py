#!/usr/bin/env python3
"""
Context Manager - Track conversations across model switches

Optional module - only imported if enable_context=True
Keeps core router small.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class ContextManager:
    """Lightweight conversation context tracking"""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.contexts_file = config_dir / "contexts.json"
        self.contexts: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        """Load contexts from disk"""
        if self.contexts_file.exists():
            try:
                with open(self.contexts_file) as f:
                    self.contexts = json.load(f)
            except Exception:
                self.contexts = {}

    def _save(self):
        """Save contexts to disk"""
        with open(self.contexts_file, "w") as f:
            json.dump(self.contexts, f, indent=2)

    def get_or_create(self, message: str, conv_id: Optional[str] = None) -> str:
        """Get existing or create new conversation"""
        if conv_id and conv_id in self.contexts:
            return conv_id

        # Create new ID
        content = f"{message}_{datetime.now().isoformat()}"
        new_id = hashlib.sha256(content.encode()).hexdigest()[:12]

        self.contexts[new_id] = {
            "id": new_id,
            "started_at": datetime.now().isoformat(),
            "messages": [],
            "transitions": 0,
            "last_model": "",
        }
        self._save()
        return new_id

    def add_message(self, conv_id: str, role: str, content: str,
                   model_used: str, model_type: str):
        """Add a message to conversation"""
        if conv_id not in self.contexts:
            return

        ctx = self.contexts[conv_id]

        # Track transitions
        if ctx["last_model"] and ctx["last_model"] != model_used:
            ctx["transitions"] += 1

        ctx["last_model"] = model_used
        ctx["messages"].append({
            "role": role,
            "content": content[:200],  # Truncate for storage
            "model": model_used,
            "type": model_type,
            "time": datetime.now().isoformat(),
        })
        self._save()

    def get_context(self, conv_id: str) -> Optional[Dict]:
        """Get conversation context"""
        if conv_id not in self.contexts:
            return None

        ctx = self.contexts[conv_id]
        return {
            "conversation_id": conv_id,
            "started_at": ctx["started_at"],
            "message_count": len(ctx["messages"]),
            "transitions": ctx["transitions"],
            "last_model": ctx["last_model"],
            "messages": ctx["messages"][-10:],  # Last 10 messages
        }

    def list_all(self) -> list:
        """List all conversations"""
        return [
            {
                "id": cid,
                "messages": len(ctx["messages"]),
                "transitions": ctx["transitions"],
            }
            for cid, ctx in self.contexts.items()
        ]
