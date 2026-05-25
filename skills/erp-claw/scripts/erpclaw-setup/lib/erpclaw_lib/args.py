"""Safe argument parser for ERPClaw skill scripts.

Replaces argparse.ArgumentParser with a version that outputs JSON errors
instead of printing to stderr and exiting with code 2. This ensures the
AI agent always gets machine-readable feedback when flags are wrong.
"""
import argparse
import json
import sys


class SafeArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that outputs JSON errors instead of stderr + exit(2).

    When argparse encounters invalid flags or missing required args, the
    default behavior is to print a message to stderr and call sys.exit(2).
    In OpenClaw's pipeline, stderr is invisible to the AI agent — it only
    sees stdout JSON. This subclass overrides error() to produce a JSON
    error response with the list of valid flags, so the agent can
    self-correct on retry.
    """

    def error(self, message):
        """Output JSON error with valid flags instead of stderr + exit(2)."""
        valid_flags = sorted(set(
            opt for action in self._actions
            for opt in action.option_strings
            if opt.startswith("--")
        ))

        # Extract valid action choices if --action has choices=
        action_choices = []
        for action in self._actions:
            if "--action" in action.option_strings and action.choices:
                action_choices = sorted(action.choices)
                break

        data = {"status": "error", "message": message}
        if action_choices:
            data["valid_actions"] = action_choices
        data["valid_flags"] = valid_flags

        print(json.dumps(data, indent=2))
        sys.exit(1)


def check_unknown_args(parser, unknown):
    """Reject unknown flags with a JSON error listing valid flags.

    Call this after parser.parse_known_args() to catch typos like
    --start-date (should be --start-of-care). Without this, unknown
    flags are silently ignored and the action fails with a confusing
    "missing required field" error.
    """
    if not unknown:
        return

    valid_flags = sorted(set(
        opt for action in parser._actions
        for opt in action.option_strings
        if opt.startswith("--")
    ))

    data = {
        "status": "error",
        "message": f"Unknown flags: {', '.join(unknown)}. Check flag names and try again.",
        "valid_flags": valid_flags,
    }
    print(json.dumps(data, indent=2))
    sys.exit(1)
