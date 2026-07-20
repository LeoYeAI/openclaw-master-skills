from __future__ import annotations

from enum import Enum


class Verdict(str, Enum):
    SUCCESS = "success"
    PREFLIGHT_FAIL = "preflight_fail"
    AGENT_FAIL = "agent_fail"
    DEPLOY_FAIL = "deploy_fail"
    REPAIR_SUCCESS = "repair_success"
    REPAIR_EXHAUSTED = "repair_exhausted"
    META_SUCCESS = "meta_success"
    META_EXHAUSTED = "meta_exhausted"
    BUDGET_EXCEEDED = "budget_exceeded"
    CONVERGED = "converged"       # same error signature twice in a row
    NO_CHANGES = "no_changes"     # agent ran but produced no file changes
    UNKNOWN = "unknown"


class Action(str, Enum):
    SHIP = "ship"
    REPAIR = "repair"
    META = "meta"
    FAIL = "fail"
    RETRY = "retry"
    PAUSE_AND_ALERT = "pause_and_alert"


# Default routing table — maps every Verdict to a concrete Action
DEFAULT_ROUTES: dict[Verdict, Action] = {
    Verdict.SUCCESS: Action.SHIP,
    Verdict.PREFLIGHT_FAIL: Action.REPAIR,
    Verdict.AGENT_FAIL: Action.FAIL,
    Verdict.DEPLOY_FAIL: Action.RETRY,
    Verdict.REPAIR_SUCCESS: Action.SHIP,
    Verdict.REPAIR_EXHAUSTED: Action.META,
    Verdict.META_SUCCESS: Action.SHIP,
    Verdict.META_EXHAUSTED: Action.FAIL,
    Verdict.BUDGET_EXCEEDED: Action.FAIL,
    Verdict.CONVERGED: Action.META,   # skip remaining repairs, jump to meta
    Verdict.NO_CHANGES: Action.FAIL,
    Verdict.UNKNOWN: Action.PAUSE_AND_ALERT,
}


class VerdictRouter:
    """Configurable verdict→action router.

    Operators can override specific routes via the `router` section of
    SHIPLOOP.yml.  All other verdicts fall back to DEFAULT_ROUTES.

    Example override in SHIPLOOP.yml:
        router:
          agent_fail: retry      # retry instead of failing immediately
          deploy_fail: fail       # never retry deploys
    """

    def __init__(self, routes: dict[Verdict, Action] | None = None):
        self.routes: dict[Verdict, Action] = {**DEFAULT_ROUTES, **(routes or {})}

    def route(self, verdict: Verdict) -> Action:
        """Return the action to take for the given verdict."""
        return self.routes.get(verdict, Action.PAUSE_AND_ALERT)

    @classmethod
    def from_config(cls, router_config: dict[str, str] | None) -> VerdictRouter:
        """Build a router from the SHIPLOOP.yml `router:` section.

        Silently ignores unknown verdict/action names so a bad config
        doesn't crash the pipeline.
        """
        if not router_config:
            return cls()

        overrides: dict[Verdict, Action] = {}
        for verdict_str, action_str in router_config.items():
            try:
                v = Verdict(verdict_str)
                a = Action(action_str)
                overrides[v] = a
            except ValueError:
                pass  # unknown verdict or action — skip silently

        return cls(routes=overrides)
