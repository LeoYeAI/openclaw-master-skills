#!/usr/bin/env python3
"""
NBLM CLI - Unified command-line interface for NotebookLM operations.
Routes all /nblm commands through NotebookLMWrapper.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from notebooklm_wrapper import NotebookLMWrapper, NotebookLMError
from notebook_manager import NotebookLibrary


def get_active_notebook_id() -> str:
    """Get the active notebook's real NotebookLM ID."""
    library = NotebookLibrary()
    active = library.get_active_notebook()
    if not active:
        raise ValueError("No active notebook. Run: /nblm activate <id>")

    url = active.get("url", "")
    if "notebook/" in url:
        parts = url.split("notebook/")
        if len(parts) > 1:
            return parts[1].split("/")[0].split("?")[0]
    raise ValueError(f"Cannot extract notebook ID from URL: {url}")


async def cmd_notebooks(args):
    """List all notebooks from NotebookLM API."""
    async with NotebookLMWrapper() as wrapper:
        notebooks = await wrapper.list_notebooks()
        print(json.dumps({"notebooks": notebooks}, indent=2, ensure_ascii=False))


async def cmd_create(args):
    """Create a new notebook."""
    async with NotebookLMWrapper() as wrapper:
        result = await wrapper.create_notebook(args.name)
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def cmd_delete(args):
    """Delete a notebook."""
    notebook_id = args.id or get_active_notebook_id()
    async with NotebookLMWrapper() as wrapper:
        await wrapper.delete_notebook(notebook_id)
        print(json.dumps({"success": True, "deleted": notebook_id}))


async def cmd_rename(args):
    """Rename a notebook."""
    from notebook_manager import NotebookLibrary

    notebook_id = args.id or get_active_notebook_id()
    async with NotebookLMWrapper() as wrapper:
        result = await wrapper.rename_notebook(notebook_id, args.name)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        library = NotebookLibrary()
        library.update_notebook(notebook_id, name=result.get('title', args.name))
        print(f"✅ Updated local library: {result.get('title', args.name)}")


async def cmd_summary(args):
    """Get notebook summary."""
    notebook_id = args.id or get_active_notebook_id()
    async with NotebookLMWrapper() as wrapper:
        summary = await wrapper.get_notebook_summary(notebook_id)
        print(summary)


async def cmd_describe(args):
    """Get notebook description and suggested topics."""
    notebook_id = args.id or get_active_notebook_id()
    async with NotebookLMWrapper() as wrapper:
        desc = await wrapper.get_notebook_description(notebook_id)
        print(json.dumps(desc, indent=2, ensure_ascii=False))


async def cmd_sources(args):
    """List sources in a notebook."""
    notebook_id = args.id or get_active_notebook_id()
    async with NotebookLMWrapper() as wrapper:
        sources = await wrapper.list_sources(notebook_id)
        print(json.dumps({"sources": sources}, indent=2, ensure_ascii=False))


async def cmd_upload_url(args):
    """Add a URL source."""
    notebook_id = args.notebook_id or get_active_notebook_id()
    async with NotebookLMWrapper() as wrapper:
        result = await wrapper.add_url(notebook_id, args.url)
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def cmd_upload_youtube(args):
    """Add a YouTube source."""
    notebook_id = args.notebook_id or get_active_notebook_id()
    async with NotebookLMWrapper() as wrapper:
        result = await wrapper.add_youtube(notebook_id, args.url)
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def cmd_upload_text(args):
    """Add text as a source."""
    notebook_id = args.notebook_id or get_active_notebook_id()
    content = args.content or sys.stdin.read()
    async with NotebookLMWrapper() as wrapper:
        result = await wrapper.add_text(notebook_id, args.title, content)
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def cmd_source_text(args):
    """Get full text of a source."""
    notebook_id = args.notebook_id or get_active_notebook_id()
    async with NotebookLMWrapper() as wrapper:
        result = await wrapper.get_source_fulltext(notebook_id, args.source_id)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(result["content"])


async def cmd_source_guide(args):
    """Get AI guide for a source."""
    notebook_id = args.notebook_id or get_active_notebook_id()
    async with NotebookLMWrapper() as wrapper:
        result = await wrapper.get_source_guide(notebook_id, args.source_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def cmd_source_rename(args):
    """Rename a source."""
    notebook_id = args.notebook_id or get_active_notebook_id()
    async with NotebookLMWrapper() as wrapper:
        result = await wrapper.rename_source(notebook_id, args.source_id, args.name)
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def cmd_source_refresh(args):
    """Refresh a URL source."""
    notebook_id = args.notebook_id or get_active_notebook_id()
    async with NotebookLMWrapper() as wrapper:
        result = await wrapper.refresh_source(notebook_id, args.source_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def cmd_source_delete(args):
    """Delete a source."""
    notebook_id = args.notebook_id or get_active_notebook_id()
    async with NotebookLMWrapper() as wrapper:
        await wrapper.delete_source(notebook_id, args.source_id)
        print(json.dumps({"success": True, "deleted": args.source_id}))


async def cmd_podcast(args):
    """Generate a podcast from notebook."""
    notebook_id = args.id or get_active_notebook_id()
    async with NotebookLMWrapper() as wrapper:
        print("🎙️ Starting podcast generation...")
        result = await wrapper.generate_audio(
            notebook_id,
            instructions=args.instructions or "",
            audio_format=args.format or "DEEP_DIVE",
            audio_length=args.length or "DEFAULT",
        )
        print(f"   Task ID: {result['task_id']}")

        if args.wait:
            print("⏳ Waiting for generation to complete...")
            final = await wrapper.wait_for_audio(
                notebook_id,
                result["task_id"],
                timeout=args.timeout or 600,
            )
            if final["is_complete"]:
                print("✅ Podcast ready!")
                if args.output:
                    path = await wrapper.download_audio(notebook_id, args.output, result["task_id"])
                    print(f"📥 Downloaded to: {path}")
                else:
                    print(f"   URL: {final.get('url', 'N/A')}")
            else:
                print(f"❌ Generation failed: {final.get('error', 'Unknown error')}")
        else:
            print(json.dumps(result, indent=2))


async def cmd_ask(args):
    """Ask a question to the notebook."""
    notebook_id = args.notebook_id or get_active_notebook_id()
    async with NotebookLMWrapper() as wrapper:
        result = await wrapper.chat(notebook_id, args.question)
        print(result["text"])


async def cmd_sync(args):
    """Sync a local folder to the notebook."""
    from sync_manager import SyncManager

    folder_path = str(Path(args.folder).resolve())
    notebook_id = args.notebook_id or get_active_notebook_id()

    # Get active account info
    from account_manager import AccountManager
    account_mgr = AccountManager()
    active_account = account_mgr.get_active_account()
    if not active_account:
        raise ValueError("No active Google account. Run: /nblm accounts switch")

    mgr = SyncManager(folder_path)
    result = await mgr.execute_sync(
        notebook_id=notebook_id,
        account_index=active_account.index,
        account_email=active_account.email,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="NBLM CLI - NotebookLM Command Line Interface")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Notebook commands
    subparsers.add_parser("notebooks", help="List all notebooks from API")

    p = subparsers.add_parser("create", help="Create a new notebook")
    p.add_argument("name", help="Notebook name")

    p = subparsers.add_parser("delete", help="Delete a notebook")
    p.add_argument("--id", help="Notebook ID (uses active if not specified)")

    p = subparsers.add_parser("rename", help="Rename a notebook")
    p.add_argument("name", help="New name")
    p.add_argument("--id", help="Notebook ID (uses active if not specified)")

    p = subparsers.add_parser("summary", help="Get notebook summary")
    p.add_argument("--id", help="Notebook ID (uses active if not specified)")

    p = subparsers.add_parser("describe", help="Get notebook description and topics")
    p.add_argument("--id", help="Notebook ID (uses active if not specified)")

    # Source commands
    p = subparsers.add_parser("sources", help="List sources in notebook")
    p.add_argument("--id", help="Notebook ID (uses active if not specified)")

    p = subparsers.add_parser("upload-url", help="Add URL source")
    p.add_argument("url", help="URL to add")
    p.add_argument("--notebook-id", help="Notebook ID")

    p = subparsers.add_parser("upload-youtube", help="Add YouTube source")
    p.add_argument("url", help="YouTube URL")
    p.add_argument("--notebook-id", help="Notebook ID")

    p = subparsers.add_parser("upload-text", help="Add text source")
    p.add_argument("title", help="Source title")
    p.add_argument("--content", help="Text content (or pipe from stdin)")
    p.add_argument("--notebook-id", help="Notebook ID")

    p = subparsers.add_parser("source-text", help="Get source full text")
    p.add_argument("source_id", help="Source ID")
    p.add_argument("--notebook-id", help="Notebook ID")
    p.add_argument("--json", action="store_true", help="Output as JSON")

    p = subparsers.add_parser("source-guide", help="Get source AI guide")
    p.add_argument("source_id", help="Source ID")
    p.add_argument("--notebook-id", help="Notebook ID")

    p = subparsers.add_parser("source-rename", help="Rename a source")
    p.add_argument("source_id", help="Source ID")
    p.add_argument("name", help="New name")
    p.add_argument("--notebook-id", help="Notebook ID")

    p = subparsers.add_parser("source-refresh", help="Refresh URL source")
    p.add_argument("source_id", help="Source ID")
    p.add_argument("--notebook-id", help="Notebook ID")

    p = subparsers.add_parser("source-delete", help="Delete a source")
    p.add_argument("source_id", help="Source ID")
    p.add_argument("--notebook-id", help="Notebook ID")

    # Podcast commands
    p = subparsers.add_parser("podcast", help="Generate podcast")
    p.add_argument("--id", help="Notebook ID")
    p.add_argument("--instructions", help="Custom instructions")
    p.add_argument("--format", choices=["DEEP_DIVE", "BRIEF", "CRITIQUE", "DEBATE"], default="DEEP_DIVE")
    p.add_argument("--length", choices=["SHORT", "DEFAULT", "LONG"], default="DEFAULT")
    p.add_argument("--wait", action="store_true", help="Wait for completion")
    p.add_argument("--output", help="Download path")
    p.add_argument("--timeout", type=int, default=600, help="Timeout in seconds")

    # Chat command
    p = subparsers.add_parser("ask", help="Ask a question")
    p.add_argument("question", help="Question to ask")
    p.add_argument("--notebook-id", help="Notebook ID")

    # Sync command
    p = subparsers.add_parser("sync", help="Sync a local folder to the notebook")
    p.add_argument("folder", help="Path to local folder to sync")
    p.add_argument("--notebook-id", help="Notebook ID")
    p.add_argument("--dry-run", action="store_true", help="Show plan without executing")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    cmd_map = {
        "notebooks": cmd_notebooks,
        "create": cmd_create,
        "delete": cmd_delete,
        "rename": cmd_rename,
        "summary": cmd_summary,
        "describe": cmd_describe,
        "sources": cmd_sources,
        "upload-url": cmd_upload_url,
        "upload-youtube": cmd_upload_youtube,
        "upload-text": cmd_upload_text,
        "source-text": cmd_source_text,
        "source-guide": cmd_source_guide,
        "source-rename": cmd_source_rename,
        "source-refresh": cmd_source_refresh,
        "source-delete": cmd_source_delete,
        "podcast": cmd_podcast,
        "ask": cmd_ask,
        "sync": cmd_sync,
    }

    try:
        asyncio.run(cmd_map[args.command](args))
        return 0
    except NotebookLMError as e:
        print(f"❌ [{e.code}]: {e.message}")
        if e.recovery:
            print(f"🔧 Recovery: {e.recovery}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
