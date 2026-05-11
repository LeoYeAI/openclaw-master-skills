#!/usr/bin/env python3
"""
Model Router Core - Compact routing engine
Minimal, readable, extensible.

Design principles from model-router-premium:
- Keep decision logic small and deterministic
- Default to cheapest/fastest for simple tasks
- Escalate to stronger models when complex

New features retained:
- Privacy detection
- Local model auto-detection
- Context tracking (optional)
"""

import json
import os
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Literal, Callable


@dataclass
class Model:
    """Model definition"""
    id: str
    name: str
    provider: str
    type: str  # "local" or "cloud"
    cost_score: float = 1.0  # lower = cheaper
    power_score: float = 50.0  # higher = more capable
    capabilities: list = None
    requires_api_key: bool = False
    api_key_env: str = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = ["chat", "general"]


@dataclass
class RouteResult:
    """Routing decision result"""
    model_id: str
    model_name: str
    model_type: str
    reason: str
    confidence: float
    complexity_score: int = 0
    privacy_detected: list = None
    context_id: str = None
    is_switch: bool = False
    previous_model: str = None

    def __post_init__(self):
        if self.privacy_detected is None:
            self.privacy_detected = []


class RouterCore:
    """
    Core routing engine - minimal and readable.

    Inspired by model-router-premium:
    - Simple scoring logic
    - Cost-aware routing
    - Capability matching

    Enhanced with:
    - Privacy detection
    - Local model detection
    """

    # Privacy patterns (sensitive data)
    PRIVACY_PATTERNS = [
        r"sk-[a-zA-Z0-9_-]{15,}",  # Stripe, API keys
        r"api[_-]?key\s*[:=]\s*['\"]?[a-zA-Z0-9_-]{10,}",
        r"password\s*[:=]\s*['\"]?.{6,}",
        r"secret\s*[:=]\s*['\"]?.{10,}",
        r"bearer\s+[a-zA-Z0-9_-]{20,}",
        r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Z|a-z]{2,}\b",  # email
    ]

    # Complexity patterns (from model-router-premium + additions)
    COMPLEX_PATTERNS = {
        # Very high complexity (+10)
        "microservices": 10, "architecture": 10, "scalable": 10,
        "multi-step": 10, "comprehensive": 10, "end-to-end": 10,
        # High complexity (+5)
        "design": 5, "implement": 5, "optimize": 5,
        "explain": 3, "analyze": 3, "compare": 3,
        # Simple (-3)
        "syntax": -3, "example": -3, "what is": -3,
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or Path.home() / ".model-router" / "models.json"
        self.config_dir = Path(self.config_path).parent
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.models = []
        self.primary_id = None
        self.secondary_id = None

        # Optional modules (loaded on demand)
        self._context = None
        self._detector = None

        self._load_config()

    @property
    def context(self):
        """Lazy load context module"""
        if self._context is None:
            try:
                from modules.context import ContextManager
                self._context = ContextManager(self.config_dir)
            except ImportError:
                self._context = False
        return self._context

    @property
    def detector(self):
        """Lazy load detector module"""
        if self._detector is None:
            from modules.detector import ModelDetector
            self._detector = ModelDetector()
        return self._detector

    def _load_config(self):
        """Load model configuration"""
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                config = json.load(f)
                self.primary_id = config.get("primary_model", {}).get("id")
                self.secondary_id = config.get("secondary_model", {}).get("id")
                self.models = [self._dict_to_model(m) for m in config.get("models", [])]
        else:
            # Auto-detect local models if no config
            self._auto_detect()

    def _auto_detect(self):
        """Auto-detect available models"""
        try:
            from modules.detector import ModelDetector
            detector = ModelDetector()
            local_models = detector.detect_local()
            cloud_models = detector.get_cloud_registry()

            self.models = local_models + cloud_models

            # Set defaults
            if local_models:
                self.primary_id = local_models[0].id
            if cloud_models:
                self.secondary_id = cloud_models[0].id
        except ImportError:
            # Fallback models (always available)
            self.models = [
                Model("ollama:llama3:8b", "Llama 3 8B", "Ollama", "local", 0, 35),
                Model("anthropic:claude-haiku-4", "Claude Haiku 4", "Anthropic", "cloud", 3, 60, requires_api_key=True, api_key_env="ANTHROPIC_API_KEY"),
            ]
            self.primary_id = self.models[0].id
            self.secondary_id = self.models[1].id

        # Ensure we always have primary and secondary set
        if not self.primary_id and self.models:
            self.primary_id = self.models[0].id
        if not self.secondary_id and len(self.models) > 1:
            self.secondary_id = self.models[1].id
        elif not self.secondary_id and self.models:
            self.secondary_id = self.models[0].id

    def _dict_to_model(self, d: dict) -> Model:
        """Convert dict to Model"""
        return Model(
            id=d.get("id", ""),
            name=d.get("name", ""),
            provider=d.get("provider", ""),
            type=d.get("type", "cloud"),
            cost_score=d.get("cost_score", 1.0),
            power_score=d.get("power_score", 50.0),
            capabilities=d.get("capabilities", []),
            requires_api_key=d.get("requires_api_key", False),
            api_key_env=d.get("api_key_env"),
        )

    def get_model(self, model_id: str) -> Optional[Model]:
        """Get model by ID"""
        for m in self.models:
            if m.id == model_id:
                return m
        return None

    def check_privacy(self, text: str) -> tuple[bool, list]:
        """Check for sensitive data"""
        detected = []
        for pattern in self.PRIVACY_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(pattern)
        return len(detected) > 0, detected

    def score_complexity(self, text: str) -> int:
        """
        Score task complexity.
        Returns 0-50+ (higher = more complex)

        Based on model-router-premium heuristics:
        - Length: longer = more complex
        - Keywords: complex words add points
        """
        text_lower = text.lower()
        score = 0

        # Length scoring (from model-router-premium)
        length = len(text)
        if length > 200:
            score += 3
        elif length > 80:
            score += 2
        elif length > 40:
            score += 1

        # Keyword scoring (simplified)
        for keyword, points in self.COMPLEX_PATTERNS.items():
            if keyword in text_lower:
                score += points

        return max(0, score)

    def route(
        self,
        task: str,
        force: Optional[Literal["primary", "secondary"]] = None,
        conversation_id: Optional[str] = None,
        enable_context: bool = True
    ) -> RouteResult:
        """
        Route a task to the appropriate model.

        Args:
            task: The user's task/request
            force: Force primary or secondary model
            conversation_id: Continue existing conversation
            enable_context: Use context tracking

        Returns:
            RouteResult with selected model and reasoning
        """
        # Privacy check - always routes to primary (usually local)
        has_privacy, privacy_detected = self.check_privacy(task)
        if has_privacy:
            primary = self.get_model(self.primary_id)
            if primary:
                return RouteResult(
                    model_id=primary.id,
                    model_name=primary.name,
                    model_type="primary",
                    reason=f"privacy_detected:{len(privacy_detected)}_patterns",
                    confidence=1.0,
                    privacy_detected=privacy_detected,
                )

        # Forced model
        if force == "primary":
            m = self.get_model(self.primary_id)
            return RouteResult(m.id, m.name, "primary", "forced", 1.0)
        if force == "secondary":
            m = self.get_model(self.secondary_id)
            return RouteResult(m.id, m.name, "secondary", "forced", 1.0)

        # Score complexity
        complexity = self.score_complexity(task)

        # Get context if available
        context_data = None
        previous_model = None
        is_switch = False

        if enable_context and self.context and conversation_id:
            context_data = self.context.get_context(conversation_id)
            if context_data:
                previous_model = context_data.get("last_model")

        # Decision: primary vs secondary
        # Threshold at 5 (simpler than model-router-premium's 3)
        threshold = 5

        primary = self.get_model(self.primary_id)
        secondary = self.get_model(self.secondary_id)

        if not primary or not secondary:
            # Fallback - use any available model
            if self.models:
                m = self.models[0]
                return RouteResult(
                    m.id, m.name, m.type, "no_config", 0.5,
                    complexity_score=complexity
                )
            # Last resort - create default model
            return RouteResult(
                model_id="ollama:llama3:8b",
                model_name="Llama 3 8B",
                model_type="primary",
                reason="auto_detected_fallback",
                confidence=0.5,
                complexity_score=complexity
            )

        if complexity < threshold:
            selected = primary
            selected_type = "primary"
            reason = f"simple_task(score={complexity})"
        else:
            selected = secondary
            selected_type = "secondary"
            reason = f"complex_task(score={complexity})"

            # Check switch
            if previous_model and previous_model != selected.id:
                is_switch = True
                reason += f",switch_from:{previous_model}"

        # Calculate confidence
        if selected_type == "primary":
            confidence = max(0.5, (threshold - complexity) / threshold)
        else:
            confidence = min(1.0, (complexity - threshold) / 20 + 0.5)

        return RouteResult(
            model_id=selected.id,
            model_name=selected.name,
            model_type=selected_type,
            reason=reason,
            confidence=confidence,
            complexity_score=complexity,
            context_id=conversation_id,
            is_switch=is_switch,
            previous_model=previous_model,
        )

    def record_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        model_id: str,
        model_type: str
    ):
        """Record a message in context (if enabled)"""
        if self.context:
            self.context.add_message(
                conv_id=conversation_id,
                role=role,
                content=content,
                model_used=model_id,
                model_type=model_type,
            )

    def get_conversation(self, conversation_id: str):
        """Get conversation context"""
        if self.context:
            return self.context.get_context(conversation_id)
        return None

    def list_models(self) -> list:
        """List all available models"""
        return [asdict(m) for m in self.models]

    def get_status(self) -> dict:
        """Get router status"""
        return {
            "primary_id": self.primary_id,
            "secondary_id": self.secondary_id,
            "model_count": len(self.models),
            "context_enabled": bool(self.context),
            "config_path": str(self.config_path),
        }


def main():
    """Simple CLI"""
    import argparse

    p = argparse.ArgumentParser(description="Model Router - Compact & Fast")
    p.add_argument("task", nargs="*", help="Task to route")
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument("--force", choices=["primary", "secondary"])
    p.add_argument("--list", action="store_true", help="List models")
    p.add_argument("--status", action="store_true", help="Show status")

    args = p.parse_args()

    router = RouterCore()

    if args.list:
        for m in router.models:
            print(f"{m.id:30} {m.name:20} [{m.type}]")
        return

    if args.status:
        status = router.get_status()
        for k, v in status.items():
            print(f"{k}: {v}")
        return

    if not args.task:
        p.print_help()
        return

    task = " ".join(args.task)
    result = router.route(task, force=args.force)

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        symbol = "1️⃣" if result.model_type == "primary" else "2️⃣"
        print(f"{symbol} {result.model_name}")
        print(f"   Reason: {result.reason}")
        print(f"   Confidence: {result.confidence:.0%}")


if __name__ == "__main__":
    main()
