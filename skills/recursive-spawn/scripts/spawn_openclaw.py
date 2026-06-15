"""
spawn_openclaw.py — Openclaw sub-instance spawner (multi-provider via LiteLLM)

Drop this file anywhere in your project. Set the SKILL_MD_PATH constant to the
absolute path of your installed openclaw-spawner/SKILL.md, or pass skill_md= at
call time. All other configuration is handled here.

PROVIDER SETUP
--------------
This spawner uses LiteLLM, which supports 100+ providers. Pass any LiteLLM model
string as the `model=` argument. Set the corresponding API key env var for your
chosen provider before calling:

    Provider      model= string                        env var
    ─────────────────────────────────────────────────────────────────────────
    Anthropic     "anthropic/claude-opus-4-6"          ANTHROPIC_API_KEY
    OpenAI        "openai/gpt-4o"                      OPENAI_API_KEY
    Gemini        "gemini/gemini-2.0-flash"             GEMINI_API_KEY
    Groq          "groq/llama-3.3-70b-versatile"       GROQ_API_KEY
    Mistral       "mistral/mistral-large-latest"        MISTRAL_API_KEY
    Azure OpenAI  "azure/<deployment>"                  AZURE_API_KEY + AZURE_API_BASE
    AWS Bedrock   "bedrock/anthropic.claude-..."        AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY
    Ollama        "ollama/llama3"                       (no key needed)

    Full list: https://docs.litellm.ai/docs/providers

TOOL FORMAT
-----------
Tools must use OpenAI-style function definitions (LiteLLM normalises these for
each provider automatically):

    tools = [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a file from disk.",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            },
        }
    ]

SECURITY NOTES
--------------
Credential:   Set the provider-specific API key env var. Never embed keys in
              payloads or progress snapshots.

Filesystem:   Passing tools= to a child agent grants that child those capabilities.
              File-access tools allow children to read/write arbitrary paths.
              Only pass tools you would trust the parent to use directly.

Snapshots:    progress_so_far is sent to the provider API and injected into the
              child's context. Sanitize snapshots before spawning — strip secrets,
              tokens, and personal data.

BREAKING CHANGES FROM ANTHROPIC-ONLY VERSION
--------------------------------------------
1. spawn_openclaw_async no longer takes a `client` as its first positional arg.
   Old: spawn_openclaw_async(client, payload, depth=1)
   New: spawn_openclaw_async(payload, depth=1, model="...")
2. Tools must be in OpenAI function-call format (see TOOL FORMAT above).
3. client= parameter removed from spawn_openclaw (sync).
4. New model= parameter on both functions (default: "anthropic/claude-opus-4-6").
"""

import json
import os
import pathlib
from typing import Optional

import litellm
from litellm.exceptions import APIError

# Suppress LiteLLM's verbose success logs; keep warnings and errors.
litellm.suppress_debug_info = True

# ── Configuration ─────────────────────────────────────────────────────────────

# Default model — override per-call with model= argument.
# Any LiteLLM model string works: "openai/gpt-4o", "gemini/gemini-2.0-flash", etc.
MODEL = "anthropic/claude-opus-4-6"
MAX_TOKENS = 8192
MAX_DEPTH = 3  # Maximum nesting depth: parent=0, child=1, grandchild=2, etc.

# Default path to SKILL.md — override with skill_md= or skill_path= at call time.
SKILL_MD_PATH = pathlib.Path(__file__).parent.parent / "SKILL.md"

_REQUIRED_KEYS = {"main_task_title", "progress_so_far", "sub_task"}


# ── Internal helpers ──────────────────────────────────────────────────────────

def _validate_payload(payload: dict) -> None:
    """Raise ValueError if payload is missing required keys or is not JSON-serializable."""
    missing = _REQUIRED_KEYS - payload.keys()
    if missing:
        raise ValueError(
            f"spawn_openclaw: payload missing required keys: {sorted(missing)}. "
            f"Required: {sorted(_REQUIRED_KEYS)}"
        )
    try:
        json.dumps(payload)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"spawn_openclaw: payload contains non-JSON-serializable value: {exc}"
        ) from exc


def _load_skill(skill_md: Optional[str], skill_path: Optional[pathlib.Path]) -> str:
    """Return SKILL.md content, loading from disk if not provided directly."""
    if skill_md is not None:
        return skill_md
    path = skill_path or SKILL_MD_PATH
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise FileNotFoundError(
            f"SKILL.md not found or unreadable at {path}. "
            "Pass skill_md='...' or skill_path=pathlib.Path('/your/path/SKILL.md')."
        ) from exc


def _build_messages(skill_md: str, depth: int, has_tools: bool, payload_str: str) -> list:
    """Build the messages list (system + user) for a child at the given depth."""
    may_spawn = (depth + 1) < MAX_DEPTH
    spawn_rule = (
        f"You MAY spawn further Openclaw sub-instances at depth {depth + 1} "
        f"(limit is {MAX_DEPTH - 1}) ONLY if sub_task explicitly permits it."
        if may_spawn
        else f"You are at maximum depth ({depth}). "
             "Do NOT spawn further sub-instances under any circumstances."
    )
    output_rule = (
        "3. Write all output to the file path(s) specified in sub_task.\n"
        if has_tools
        else "3. Return all output in your completion summary text — you have no file tools.\n"
    )
    system_content = (
        "You are an Openclaw agent — an autonomous sub-instance spawned by a parent Openclaw agent.\n\n"
        "You have full access to the openclaw-spawner skill:\n"
        f"<skill>\n{skill_md}\n</skill>\n\n"
        "Rules:\n"
        "1. Complete ONLY the `sub_task` in the payload you receive.\n"
        "2. Do not attempt work outside your sub_task.\n"
        f"{output_rule}"
        f"4. {spawn_rule}\n"
        "5. When done, reply with a brief completion summary (what you did, where results are).\n"
        "6. If you encounter an unrecoverable error, reply with a JSON object: "
        '{"error": "<description>", "partial_results": "<path or null>"}.'
    )
    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": payload_str},
    ]


def _extract_text(response) -> str:
    """Extract the text reply from a LiteLLM response, or return a JSON error string."""
    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError):
        return json.dumps({"error": "Unexpected response structure from provider", "partial_results": None})
    if content is None:
        # Model returned a tool_call with no accompanying text.
        return json.dumps({
            "error": (
                "Child responded with a tool call but no text. "
                "This spawner makes a single API call and does not run a tool loop. "
                "Use _build_messages() and manage turns yourself for tool-execution."
            ),
            "partial_results": None,
        })
    return content


def _provider_from_model(model: str) -> str:
    """Return the provider prefix from a LiteLLM model string (e.g. 'anthropic' from 'anthropic/...')."""
    return model.split("/")[0] if "/" in model else model


# ── Sync spawner ──────────────────────────────────────────────────────────────

def spawn_openclaw(
    payload: dict,
    *,
    depth: int = 1,
    model: str = MODEL,
    tools: Optional[list] = None,
    skill_md: Optional[str] = None,
    skill_path: Optional[pathlib.Path] = None,
    **litellm_kwargs,
) -> str:
    """
    Spawn a child Openclaw instance synchronously.

    Args:
        payload:    Dict with keys main_task_title, progress_so_far, sub_task.
        depth:      Current spawn depth (1 = direct child of root). Enforces MAX_DEPTH.
        model:      LiteLLM model string. Default: "anthropic/claude-opus-4-6".
                    Examples:
                      "openai/gpt-4o"                  (requires OPENAI_API_KEY)
                      "gemini/gemini-2.0-flash"          (requires GEMINI_API_KEY)
                      "groq/llama-3.3-70b-versatile"    (requires GROQ_API_KEY)
                      "ollama/llama3"                   (requires Ollama running locally)
                    Full list: https://docs.litellm.ai/docs/providers
        tools:      Tool definitions in OpenAI function-call format. LiteLLM translates
                    these to each provider's native format automatically.
                    Without tools, the child can only return results in its summary text.

                    IMPORTANT: This spawner makes a single API call. If the child invokes
                    a tool, _extract_text returns a JSON error. Use _build_messages() and
                    manage conversation turns yourself for a full tool-execution loop.
        skill_md:   Raw SKILL.md text. If omitted, loaded from skill_path / SKILL_MD_PATH.
        skill_path: Path to SKILL.md. Overrides SKILL_MD_PATH if provided.
        **litellm_kwargs: Any extra kwargs forwarded to litellm.completion(), e.g.:
                      temperature=0
                      api_base="http://localhost:11434"  (Ollama custom base URL)
                      api_key="sk-..."                   (override env var)

    Returns:
        Child's completion summary string, or a JSON error string on API/response failure.

    Raises:
        ValueError:        depth >= MAX_DEPTH, missing payload keys, non-serializable payload.
        FileNotFoundError: SKILL.md not found at the expected path.
    """
    _validate_payload(payload)
    if depth >= MAX_DEPTH:
        raise ValueError(
            f"spawn_openclaw: depth {depth} >= MAX_DEPTH={MAX_DEPTH}. "
            "Increase MAX_DEPTH or flatten your task tree."
        )

    skill = _load_skill(skill_md, skill_path)
    payload_str = json.dumps(payload, indent=2)
    messages = _build_messages(skill, depth, has_tools=tools is not None, payload_str=payload_str)

    call_kwargs: dict = dict(
        model=model,
        messages=messages,
        max_tokens=MAX_TOKENS,
        **litellm_kwargs,
    )
    if tools is not None:
        call_kwargs["tools"] = tools

    try:
        response = litellm.completion(**call_kwargs)
        return _extract_text(response)
    except APIError as exc:
        return json.dumps({
            "error": f"Provider API error ({_provider_from_model(model)}): {exc}",
            "partial_results": None,
        })
    except Exception as exc:  # noqa: BLE001 — surface unexpected errors as JSON, never raise
        return json.dumps({"error": f"Unexpected error: {exc}", "partial_results": None})


# ── Async spawner ─────────────────────────────────────────────────────────────

async def spawn_openclaw_async(
    payload: dict,
    *,
    depth: int = 1,
    model: str = MODEL,
    tools: Optional[list] = None,
    skill_md: Optional[str] = None,
    skill_path: Optional[pathlib.Path] = None,
    **litellm_kwargs,
) -> str:
    """
    Async variant of spawn_openclaw.

    NOTE: Unlike the previous Anthropic-only version, this function no longer takes
    a `client` as its first positional argument. LiteLLM manages connections internally.

    Args:
        payload:    Dict with keys main_task_title, progress_so_far, sub_task.
        depth:      Current spawn depth. Enforces MAX_DEPTH.
        model:      LiteLLM model string (see spawn_openclaw for examples).
        tools:      Tool definitions in OpenAI function-call format.
                    NOTE: Single API call — tool invocation returns a JSON error.
                    Manage turns yourself for a full tool-execution loop.
        skill_md:   Raw SKILL.md text override.
        skill_path: Path to SKILL.md override.
        **litellm_kwargs: Forwarded to litellm.acompletion().

    Returns:
        Child's completion summary string, or a JSON error string on failure.

    Raises:
        ValueError:        depth >= MAX_DEPTH, missing payload keys, non-serializable payload.
        FileNotFoundError: SKILL.md not found.

    Usage (parallel-gather):
        results = await asyncio.gather(
            *[spawn_openclaw_async(p, model="openai/gpt-4o") for p in payloads],
            return_exceptions=True,
        )

    Usage (fire-and-forget):
        task = asyncio.create_task(
            spawn_openclaw_async(payload, model="groq/llama-3.3-70b-versatile")
        )
        await do_parent_work()
        summary = await task
    """
    _validate_payload(payload)
    if depth >= MAX_DEPTH:
        raise ValueError(
            f"spawn_openclaw_async: depth {depth} >= MAX_DEPTH={MAX_DEPTH}."
        )

    skill = _load_skill(skill_md, skill_path)
    payload_str = json.dumps(payload, indent=2)
    messages = _build_messages(skill, depth, has_tools=tools is not None, payload_str=payload_str)

    call_kwargs: dict = dict(
        model=model,
        messages=messages,
        max_tokens=MAX_TOKENS,
        **litellm_kwargs,
    )
    if tools is not None:
        call_kwargs["tools"] = tools

    try:
        response = await litellm.acompletion(**call_kwargs)
        return _extract_text(response)
    except APIError as exc:
        return json.dumps({
            "error": f"Provider API error ({_provider_from_model(model)}): {exc}",
            "partial_results": None,
        })
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": f"Unexpected error: {exc}", "partial_results": None})


# ── Public helpers ────────────────────────────────────────────────────────────

def is_error(summary: str) -> bool:
    """Returns True if the child's summary is an error JSON object."""
    try:
        obj = json.loads(summary)
        return isinstance(obj, dict) and "error" in obj
    except (json.JSONDecodeError, TypeError):
        return False


def read_result(path: str) -> Optional[str]:
    """
    Safely read a child's result file.
    Returns None on any filesystem error (missing file, permission denied, etc.).
    Always check with `if result is not None` — an empty string is a valid result.
    """
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


# ── Example ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    payload = {
        "main_task_title": "Refactor authentication module",
        "progress_so_far": (
            "## Progress Snapshot\n"
            "**Completed:**\n- Audited existing auth flow\n- Identified 3 outdated JWT helpers\n\n"
            "**Artifacts produced:**\n- `/tmp/audit_report.md`: full list of issues\n\n"
            "**Decisions made:**\n- Use PyJWT 2.x API; drop legacy HS256 fallback\n\n"
            "**Pending (child handles):**\n- Rewrite auth/jwt_helpers.py per audit report"
        ),
        "sub_task": (
            "Rewrite `/src/auth/jwt_helpers.py` using PyJWT 2.x. "
            "Read `/tmp/audit_report.md` for the full list of issues to fix. "
            "Output the rewritten file to `/tmp/jwt_helpers_new.py` and write a "
            "one-paragraph summary of changes to `/tmp/jwt_helpers_changes.md`."
        ),
    }

    # Swap model= to use a different provider — set the matching API key env var.
    # e.g. model="openai/gpt-4o"            → requires OPENAI_API_KEY
    #      model="gemini/gemini-2.0-flash"    → requires GEMINI_API_KEY
    #      model="ollama/llama3"             → requires Ollama running locally (no key)
    try:
        summary = spawn_openclaw(payload, depth=1, model="anthropic/claude-opus-4-6")
    except (ValueError, FileNotFoundError) as exc:
        print("Configuration error:", exc)
        raise

    if is_error(summary):
        print("Child failed:", summary)
    else:
        print("Child completed:", summary)
        result = read_result("/tmp/jwt_helpers_changes.md")
        if result is not None:
            print("Changes summary:", result)
        else:
            print("WARNING: child did not write expected result file.")
