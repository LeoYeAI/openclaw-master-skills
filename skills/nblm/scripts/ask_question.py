#!/usr/bin/env python3
"""
NotebookLM Question Interface
Uses agent-browser for token-efficient browser automation
"""

import argparse
import asyncio
import json
import os
import sys
import time
import re
from typing import Optional
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))

from auth_manager import AuthManager
from account_manager import AccountManager
from notebook_manager import NotebookLibrary
from agent_browser_client import AgentBrowserClient, AgentBrowserError
from notebooklm_wrapper import NotebookLMWrapper, NotebookLMError


# Follow-up reminder for comprehensive research
FOLLOW_UP_REMINDER = (
    "\n\n---\n"
    "**Is that ALL you need to know?** "
    "You can ask another question! Review the user's original request. "
    "If anything is unclear or missing, ask a comprehensive follow-up question "
    "(each question opens a fresh context)."
)

PENDING_PHRASES = (
    "thinking",
    "loading",
    "getting the gist",
    "gathering the facts",
    "consulting your sources",
    "scanning the text",
    "reading your inputs",
)
PENDING_LINE_RE = re.compile(
    r"^(?:thinking|loading|getting the gist|gathering the facts|consulting your sources|scanning the text|reading your inputs)(?:[\s.!?]*)$|^[A-Za-z][A-Za-z\s'’]{0,60}\.{3,}$",
    re.IGNORECASE
)


def find_input_ref(client: AgentBrowserClient, snapshot: str) -> str:
    """Find the query input element ref"""
    # Prefer the main chat input; skip disabled fields.
    for line in snapshot.split('\n'):
        line_lower = line.lower()
        if "textbox" in line_lower and "query box" in line_lower and "disabled" not in line_lower:
            match = re.search(r'\[ref=(\w+)\]', line)
            if match:
                return match.group(1)

    # Try common patterns for NotebookLM input
    for hint in ("ask", "query", "message", "chat"):
        input_ref = client.find_ref_by_role(snapshot, "textbox", hint)
        if input_ref:
            return input_ref

    # Fallback: find any enabled textbox
    for line in snapshot.split('\n'):
        line_lower = line.lower()
        if "textbox" in line_lower and "disabled" not in line_lower:
            match = re.search(r'\[ref=(\w+)\]', line)
            if match:
                return match.group(1)

    return None


def wait_for_answer(client: AgentBrowserClient, question: str, timeout: int = 120) -> str:
    """Wait for NotebookLM answer to stabilize"""
    deadline = time.time() + timeout
    last_snapshot = None
    stable_count = 0
    last_answer = None
    stable_answer_count = 0

    while time.time() < deadline:
        snapshot = client.snapshot()
        snapshot_lower = snapshot.lower()
        answer = extract_answer(snapshot, question)
        filtered_answer = ""
        if answer and answer != snapshot:
            filtered_answer = _strip_pending_lines(answer)
        question_only = _is_question_only_answer(filtered_answer, question)
        has_answer = bool(filtered_answer) and not question_only

        # Check if still thinking
        pending_in_snapshot = False
        if answer and answer != snapshot:
            if question_only or (not has_answer and _answer_has_pending_line(answer)):
                pending_in_snapshot = True
        if not pending_in_snapshot:
            pending_in_snapshot = any(marker in snapshot_lower for marker in PENDING_PHRASES)
        if pending_in_snapshot and not has_answer:
            time.sleep(1)
            continue

        if has_answer:
            if filtered_answer == last_answer:
                stable_answer_count += 1
                if stable_answer_count >= 2:
                    return filtered_answer
            else:
                last_answer = filtered_answer
                stable_answer_count = 0
        else:
            stable_answer_count = 0

        # Check for stability
        if snapshot == last_snapshot:
            stable_count += 1
            if stable_count >= 3:
                final_answer = extract_answer(snapshot, question)
                filtered_final = _strip_pending_lines(final_answer) if final_answer != snapshot else ""
                return filtered_final or final_answer
        else:
            stable_count = 0
            last_snapshot = snapshot

        time.sleep(1)

    raise AgentBrowserError(
        code="TIMEOUT",
        message=f"No response within {timeout} seconds",
        recovery="Try again or check if notebook is accessible"
    )


def _strip_pending_lines(answer: str) -> str:
    """Remove placeholder status lines from a candidate answer."""
    if not answer:
        return ""
    lines = [line.strip() for line in answer.splitlines() if line.strip()]
    filtered = [line for line in lines if not PENDING_LINE_RE.match(line)]
    return "\n".join(filtered).strip()


def _answer_has_pending_line(answer: str) -> bool:
    """Return True if the answer contains a pending status line."""
    if not answer:
        return False
    for line in answer.splitlines():
        stripped = line.strip()
        if stripped and PENDING_LINE_RE.match(stripped):
            return True
    return False


def _is_question_only_answer(answer: str, question: str) -> bool:
    """Return True if the answer only echoes the question."""
    if not answer:
        return False
    question_norm = question.strip().lower()
    if not question_norm:
        return False
    lines = [line.strip() for line in answer.splitlines() if line.strip()]
    if not lines:
        return False
    return all(line.lower() == question_norm for line in lines)


def extract_answer(snapshot: str, question: str) -> str:
    """Extract the latest answer from accessibility snapshot"""
    lines = [line.rstrip() for line in snapshot.split('\n') if line.strip()]
    question_lower = question.lower()
    start_idx = None

    def normalize(line: str) -> str:
        return line.lstrip('- ').lstrip().lstrip("'").strip()

    for idx, line in enumerate(lines):
        normalized = normalize(line)
        if normalized.lower().startswith('heading ') and question_lower in normalized.lower():
            start_idx = idx

    if start_idx is None:
        return snapshot

    def extract_text(line: str) -> Optional[str]:
        normalized = normalize(line)
        if normalized.startswith(("button", "link", "textbox", "contentinfo")):
            return None
        if normalized.startswith(("text:", "paragraph:", "strong:", "code:")) and ':' in normalized:
            value = normalized.split(':', 1)[1].strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            value = value.replace('\\\"', '"').replace('\\n', ' ')
            value = re.sub(r'\\[ref=[^\\]]+\\]', '', value)
            value = re.sub(r'\\[nth=[^\\]]+\\]', '', value)
            return value.strip()
        if normalized.startswith("heading"):
            if 'heading "' in normalized:
                value = normalized.split('heading "', 1)[1]
                if '"' in value:
                    value = value.rsplit('"', 1)[0]
                value = value.replace('\\\"', '"')
                value = re.sub(r'\\[ref=[^\\]]+\\]', '', value)
                value = re.sub(r'\\[nth=[^\\]]+\\]', '', value)
                return value.strip()
        if ':' in normalized:
            return normalized.split(':', 1)[1].strip()
        return None

    answer_lines = []
    for line in lines[start_idx + 1:]:
        normalized = normalize(line)
        if normalized.lower().startswith('textbox "query box"') or normalized.lower().startswith('contentinfo'):
            break
        if normalized.lower().startswith('heading ') and question_lower in normalized.lower():
            break
        text = extract_text(line)
        if text:
            cleaned = text.strip()
            if cleaned.startswith(". "):
                cleaned = cleaned[2:].lstrip()
            cleaned = re.sub(r'\[ref=[^\]]+\]', '', cleaned)
            cleaned = re.sub(r'\[nth=[^\]]+\]', '', cleaned)
            if cleaned in {".", ",", ";", ":"}:
                continue
            answer_lines.append(cleaned)

    return '\n'.join(answer_lines).strip() or snapshot


def _extract_notebook_id_from_url(notebook_url: str) -> Optional[str]:
    if not notebook_url:
        return None
    parsed = urlparse(notebook_url)
    if not parsed.path:
        return None
    parts = [part for part in parsed.path.split("/") if part]
    if "notebook" in parts:
        idx = parts.index("notebook")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return None


async def ask_notebooklm_api_async(question: str, notebook_url: str, account_index: int = None) -> dict:
    """Query NotebookLM via API.

    Args:
        question: The question to ask
        notebook_url: The notebook URL
        account_index: Optional account index to use (defaults to active)
    """
    notebook_id = _extract_notebook_id_from_url(notebook_url)
    if not notebook_id:
        return {
            "status": "error",
            "error": {
                "code": "NOTEBOOK_ID_MISSING",
                "message": "Notebook ID could not be parsed from URL",
                "recovery": "Provide --notebook-id or a valid NotebookLM URL",
            },
        }

    try:
        async with NotebookLMWrapper(account_index=account_index) as client:
            response = await client.chat(notebook_id, question)
            answer = response.get("text", "")
            return {
                "status": "success",
                "question": question,
                "answer": answer + FOLLOW_UP_REMINDER,
                "notebook_url": notebook_url,
            }
    except NotebookLMError as e:
        return {
            "status": "error",
            "error": {
                "code": e.code,
                "message": e.message,
                "recovery": e.recovery,
            },
        }


async def ask_notebooklm_async(question: str, notebook_url: str, show_browser: bool = False) -> dict:
    """Ask a question to NotebookLM - API first, browser fallback."""
    auth = AuthManager()
    account_mgr = AccountManager()

    # Check authentication
    if not auth.is_authenticated("google"):
        return {
            "status": "error",
            "error": {
                "code": "AUTH_REQUIRED",
                "message": "Not authenticated with Google",
                "recovery": "Run: python scripts/run.py auth_manager.py setup"
            }
        }

    # Determine which account to use based on notebook
    library = NotebookLibrary()
    notebook_id = _extract_notebook_id_from_url(notebook_url)
    account_index = None

    # Find notebook in library to get its account
    for nb in library.notebooks.values():
        if notebook_id and notebook_id in nb.get('url', ''):
            account_index = nb.get('account_index')
            if account_index:
                account = account_mgr.get_account_by_index(account_index)
                if account:
                    active = account_mgr.get_active_account()
                    if active and active.index != account_index:
                        print(f"📧 Notebook belongs to [{account.index}] {account.email}")
            break

    print(f"💬 Asking: {question[:80]}{'...' if len(question) > 80 else ''}")
    print(f"📚 Notebook: {notebook_url[:60]}...")

    # Try API first (unless show_browser is explicitly requested)
    if not show_browser:
        print("🔌 Trying API...")
        result = await ask_notebooklm_api_async(question, notebook_url, account_index)
        if result["status"] == "success":
            print("✅ Got answer via API!")
            return result
        print(f"⚠️ API failed: {result['error']['message']}, falling back to browser...")

    # Fall back to browser
    return _ask_via_browser_sync(question, notebook_url, show_browser, auth)


def ask_notebooklm(question: str, notebook_url: str, show_browser: bool = False) -> dict:
    """Sync wrapper for ask_notebooklm_async."""
    return asyncio.run(ask_notebooklm_async(question, notebook_url, show_browser))


def _ask_via_browser_sync(question: str, notebook_url: str, show_browser: bool, auth: AuthManager) -> dict:
    """
    Ask a question to NotebookLM via browser automation.

    Returns:
        dict with status, answer, and optional error
    """
    client = AgentBrowserClient(session_id="notebooklm", headed=show_browser)

    try:
        client.connect()
    except AgentBrowserError as e:
        return {
            "status": "error",
            "error": e.to_dict(),
        }

    try:
        auth.restore_auth("google", client=client)

        # Navigate to notebook
        client.navigate(notebook_url)
        time.sleep(2)  # Allow page to load

        # Get initial snapshot
        snapshot = client.snapshot()

        # Check if auth is needed
        if client.check_auth(snapshot):
            return {
                "status": "error",
                "error": {
                    "code": "AUTH_REQUIRED",
                    "message": "Google login required",
                    "recovery": "Run: python scripts/run.py auth_manager.py setup"
                },
                "snapshot": snapshot[:500]
            }

        # Find input element
        print("⏳ Finding query input...")
        input_ref = find_input_ref(client, snapshot)

        if not input_ref:
            return {
                "status": "error",
                "error": {
                    "code": "ELEMENT_NOT_FOUND",
                    "message": "Cannot find query input on page",
                    "recovery": "Check notebook URL or view snapshot for diagnosis"
                },
                "snapshot": snapshot[:500]
            }

        # Type question and submit
        print("⌨️ Typing question...")
        client.fill(ref=input_ref, text=question)
        client.press_key("Enter")

        # Wait for answer
        print("⏳ Waiting for answer...")
        time.sleep(2)  # Initial wait

        answer = wait_for_answer(client, question, timeout=120)

        print("✅ Got answer!")
        auth.save_auth("google", client=client)

        return {
            "status": "success",
            "question": question,
            "answer": answer + FOLLOW_UP_REMINDER,
            "notebook_url": notebook_url
        }

    except AgentBrowserError as e:
        return {
            "status": "error",
            "error": e.to_dict()
        }
    finally:
        client.disconnect()


def main():
    parser = argparse.ArgumentParser(description='Ask NotebookLM a question')

    parser.add_argument('--question', required=True, help='Question to ask')
    parser.add_argument('--notebook-url', help='NotebookLM notebook URL')
    parser.add_argument('--notebook-id', help='Notebook ID from library')
    parser.add_argument('--show-browser', action='store_true', help='Show browser window')

    args = parser.parse_args()

    # Resolve notebook URL
    notebook_url = args.notebook_url

    if not notebook_url and args.notebook_id:
        library = NotebookLibrary()
        notebook = library.get_notebook(args.notebook_id)
        if notebook:
            notebook_url = notebook['url']
        else:
            print(f"❌ Notebook '{args.notebook_id}' not found")
            return 1

    if not notebook_url:
        library = NotebookLibrary()
        active = library.get_active_notebook()
        if active:
            notebook_url = active['url']
            print(f"📚 Using active notebook: {active['name']}")
        else:
            notebooks = library.list_notebooks()
            if notebooks:
                print("\n📚 Available notebooks:")
                for nb in notebooks:
                    mark = " [ACTIVE]" if nb.get('id') == library.active_notebook_id else ""
                    print(f"  {nb['id']}: {nb['name']}{mark}")
                print("\nSpecify with --notebook-id or set active:")
                print("python scripts/run.py notebook_manager.py activate --id ID")
            else:
                print("❌ No notebooks in library. Add one first:")
                print("python scripts/run.py notebook_manager.py add --url URL --name NAME --description DESC --topics TOPICS")
            return 1

    # Ask the question
    result = ask_notebooklm(
        question=args.question,
        notebook_url=notebook_url,
        show_browser=args.show_browser
    )

    if result["status"] == "success":
        print()
        print("=" * 60)
        print(f"Question: {args.question}")
        print("=" * 60)
        print()
        print(result["answer"])
        print()
        print("=" * 60)
        return 0
    else:
        error = result["error"]
        print()
        print(f"❌ [{error['code']}]: {error['message']}")
        print(f"🔧 Recovery: {error['recovery']}")
        if result.get("snapshot"):
            print(f"📄 Page state:\n{result['snapshot']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
