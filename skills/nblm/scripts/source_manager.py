#!/usr/bin/env python3
"""
Unified source ingestion for NotebookLM.
"""

import argparse
import asyncio
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Union

from agent_browser_client import AgentBrowserClient
from auth_manager import AuthManager
from config import DEFAULT_SESSION_ID
from notebook_manager import NotebookLibrary, extract_notebook_id
from notebooklm_wrapper import NotebookLMWrapper, NotebookLMError
from sync_manager import SyncManager
from zlibrary.downloader import ZLibraryDownloader
from zlibrary import epub_converter
from account_manager import AccountManager


def _resolve_notebook_target(args, file_title: str) -> tuple[Optional[str], bool]:
    """Resolve which notebook to use based on CLI args.

    Returns:
        (notebook_id, create_new) tuple:
        - (id, False) = use existing notebook with given ID (real NotebookLM UUID)
        - (None, True) = create new notebook
        - Raises SystemExit if invalid combination
    """
    library = NotebookLibrary()

    # Explicit notebook ID takes priority
    if args.notebook_id:
        return (args.notebook_id, False)

    # --use-active flag
    if args.use_active:
        active = library.get_active_notebook()
        if not active:
            print("❌ No active notebook set.", file=sys.stderr)
            print("   Set one with: python scripts/run.py notebook_manager.py activate --id <id>", file=sys.stderr)
            print("   Or use --create-new to create a new notebook", file=sys.stderr)
            raise SystemExit(1)
        print(f"📓 Using active notebook: \"{active.get('name', 'Unnamed')}\"")

        # Extract real NotebookLM UUID from URL (not library ID)
        url = active.get("url")
        if url:
            real_uuid = extract_notebook_id(url)
            if real_uuid:
                return (real_uuid, False)

        # Fallback: if no URL or extraction failed, use library ID (may not be UUID)
        return (active.get("id"), False)

    # --create-new flag
    if args.create_new:
        print(f"📓 Will create new notebook: \"{file_title}\"")
        return (None, True)

    # Neither flag provided - show error with options
    active = library.get_active_notebook()
    print("❌ No notebook specified. Please choose one of:", file=sys.stderr)
    print(file=sys.stderr)
    if active:
        print(f"  --use-active    Upload to active notebook: \"{active.get('name', 'Unnamed')}\"", file=sys.stderr)
    print(f"  --create-new    Create new notebook named after the file", file=sys.stderr)
    print(f"  --notebook-id   Specify notebook ID explicitly", file=sys.stderr)
    raise SystemExit(1)


class SourceManager:
    """Unified source ingestion for NotebookLM."""

    def __init__(
        self,
        auth_manager: Optional[AuthManager] = None,
        client: Optional[AgentBrowserClient] = None,
        downloader_cls=ZLibraryDownloader,
        converter=epub_converter,
    ):
        self.auth = auth_manager or AuthManager()
        self.client = client or AgentBrowserClient(session_id=DEFAULT_SESSION_ID)
        self.downloader_cls = downloader_cls
        self.converter = converter

    @staticmethod
    def _is_zlibrary_url(url: str) -> bool:
        domains = ["zlib.li", "z-lib.org", "zlibrary.org", "zh.zlib.li"]
        return any(domain in url for domain in domains)

    @staticmethod
    def _sanitize_title(file_path: Path) -> str:
        title = file_path.stem
        title = re.sub(r'_part\d+$', '', title)
        title = title.replace('_', ' ')
        title = re.sub(r'\[.*?\]', '', title)
        title = re.sub(r'\(.*?\)', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        if len(title) > 50:
            title = title[:50] + "..."
        return title

    @staticmethod
    def _extract_notebook_id_from_url(notebook_url: str) -> Optional[str]:
        if not notebook_url:
            return None
        match = re.search(r"/notebook/([^/?#]+)", notebook_url)
        if match:
            return match.group(1)
        return None

    async def _wait_for_sources_ready_async(
        self,
        wrapper: NotebookLMWrapper,
        notebook_id: str,
        source_ids: List[str],
    ) -> Optional[dict]:
        """Wait for sources to be ready using async wrapper."""
        if not source_ids:
            return None

        unique_ids = list(dict.fromkeys(source_ids))
        total = len(unique_ids)
        print(f"Waiting for NotebookLM to process {total} source(s)...", file=sys.stderr, flush=True)

        last_ready = None
        while True:
            sources = await wrapper.list_sources(notebook_id)
            status_by_id = {src["source_id"]: src for src in sources}

            ready_count = 0
            for source_id in unique_ids:
                source = status_by_id.get(source_id)
                if not source:
                    continue
                if source.get("is_ready"):
                    ready_count += 1

            if last_ready is None or ready_count != last_ready:
                print(f"Ready: {ready_count}/{total}", file=sys.stderr, flush=True)
                last_ready = ready_count

            if ready_count >= total:
                return None

            await asyncio.sleep(2)

    async def add_from_file(
        self,
        file_path: Union[Path, List[Path]],
        notebook_id: Optional[str] = None,
        source_label: str = "upload",
    ) -> dict:
        """Upload local file(s) to NotebookLM."""
        paths = file_path if isinstance(file_path, list) else [file_path]
        for path in paths:
            if not Path(path).exists():
                raise FileNotFoundError(f"File not found: {path}")

        title = self._sanitize_title(Path(paths[0]))
        created_notebook = False

        notebook_url = None
        resolved_notebook_id = notebook_id

        if not self.auth.is_authenticated("google"):
            return {
                "success": False,
                "error": "Google authentication required",
                "recovery": "Run: python scripts/run.py auth_manager.py setup",
            }

        async with NotebookLMWrapper() as wrapper:
            if not notebook_id:
                try:
                    result = await wrapper.create_notebook(title)
                    notebook_id = result["id"]
                    created_notebook = True
                    resolved_notebook_id = notebook_id
                except NotebookLMError as e:
                    return {
                        "success": False,
                        "error": e.message,
                        "recovery": e.recovery,
                    }
            else:
                library = NotebookLibrary()
                notebook = library.get_notebook(notebook_id)
                if notebook:
                    notebook_url = notebook.get("url")
                    resolved_notebook_id = self._extract_notebook_id_from_url(notebook_url) or notebook_id
                else:
                    is_uuid = bool(re.fullmatch(r"[a-f0-9-]{36}", notebook_id or "", re.IGNORECASE))
                    if not is_uuid:
                        return {
                            "success": False,
                            "error": f"Notebook '{notebook_id}' not found in library",
                            "recovery": "Run: python scripts/run.py notebook_manager.py list",
                        }

            if not notebook_url:
                notebook_url = f"https://notebooklm.google.com/notebook/{resolved_notebook_id}"

            # Upload files using the wrapper
            source_ids = []
            try:
                for path in paths:
                    result = await wrapper.add_file(resolved_notebook_id, Path(path))
                    if result.get("source_id"):
                        source_ids.append(result["source_id"])
            except NotebookLMError as e:
                return {
                    "success": False,
                    "error": e.message,
                    "recovery": e.recovery,
                }

            if created_notebook:
                try:
                    library = NotebookLibrary()
                    description = f"Imported from {source_label}: {title}"
                    library.add_notebook(
                        url=notebook_url,
                        name=title,
                        description=description,
                        topics=[source_label],
                        notebook_id=notebook_id,  # Use actual UUID from NotebookLM
                    )
                    library.select_notebook(notebook_id)
                    print(f"✅ Activated notebook: {title}")
                except Exception as e:
                    print(f"⚠️ Warning: Could not activate notebook: {e}")

            if not source_ids:
                return {"success": False, "error": "Upload failed"}

            # Wait for sources to be ready
            try:
                wait_error = await self._wait_for_sources_ready_async(wrapper, resolved_notebook_id, source_ids)
            except NotebookLMError as e:
                return {
                    "success": False,
                    "error": e.message,
                    "recovery": e.recovery,
                }
            if wait_error:
                return wait_error

        if len(paths) > 1:
            return {
                "success": True,
                "notebook_id": notebook_id,
                "source_ids": source_ids,
                "title": title,
                "chunks": len(paths)
            }

        return {
            "success": True,
            "notebook_id": notebook_id,
            "source_id": source_ids[0],
            "title": title
        }

    async def add_from_zlibrary(self, url: str, notebook_id: Optional[str] = None) -> dict:
        """Download from Z-Library and upload to NotebookLM."""
        if not self.auth.is_authenticated("zlibrary"):
            raise RuntimeError(
                "Z-Library authentication required. "
                "Run: python scripts/run.py auth_manager.py setup --service zlibrary"
            )

        self.client.connect()
        try:
            # Let restore_auth handle navigation - don't navigate here
            self.auth.restore_auth("zlibrary", client=self.client)
            downloader = self.downloader_cls(self.client)
            file_path, file_format = downloader.download(url)
            self.auth.save_auth("zlibrary", client=self.client)
        finally:
            self.client.disconnect()

        if file_format == "epub" or Path(file_path).suffix.lower() == ".epub":
            output_path = Path(tempfile.gettempdir()) / f"{Path(file_path).stem}.md"
            converted = self.converter.convert_epub_to_markdown(file_path, output_path)
            return await self.add_from_file(converted, notebook_id, source_label="zlibrary")

        return await self.add_from_file(Path(file_path), notebook_id, source_label="zlibrary")

    async def add_from_url(self, url: str, notebook_id: Optional[str] = None) -> dict:
        """Smart routing based on URL pattern."""
        if self._is_zlibrary_url(url):
            return await self.add_from_zlibrary(url, notebook_id)
        raise ValueError(f"Unsupported URL: {url}")


async def async_main():
    parser = argparse.ArgumentParser(description="Add sources to NotebookLM")
    parser.add_argument("command", choices=["add", "sync"], help="Command to run")
    parser.add_argument("--url", help="Source URL")
    parser.add_argument("--file", help="Local file path")
    parser.add_argument("--notebook-id", help="Existing notebook ID")
    parser.add_argument("--use-active", action="store_true",
                        help="Upload to currently active notebook")
    parser.add_argument("--create-new", action="store_true",
                        help="Create a new notebook for the upload")

    # Sync command arguments
    parser.add_argument("folder", nargs="?", help="Folder path to sync")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show sync plan without executing")
    parser.add_argument("--rebuild", action="store_true",
                        help="Force rebuild tracking file (re-hash all files)")

    args = parser.parse_args()

    # Validate mutually exclusive options
    if args.use_active and args.create_new:
        print("❌ Cannot use both --use-active and --create-new", file=sys.stderr)
        raise SystemExit(1)
    if args.notebook_id and (args.use_active or args.create_new):
        print("❌ Cannot use --notebook-id with --use-active or --create-new", file=sys.stderr)
        raise SystemExit(1)

    manager = SourceManager()

    if args.command == "add" and args.file:
        path = Path(args.file).resolve()
        if path.is_dir():
            args.command = "sync"
            args.folder = str(path)
            args.file = None

    if args.command == "add":
        if args.url:
            # For URLs, derive title from URL
            file_title = Path(args.url).stem or "Untitled"
            notebook_id, create_new = _resolve_notebook_target(args, file_title)
            result = await manager.add_from_url(args.url, notebook_id)
        elif args.file:
            file_title = Path(args.file).stem
            notebook_id, create_new = _resolve_notebook_target(args, file_title)
            result = await manager.add_from_file(Path(args.file), notebook_id)
        else:
            raise SystemExit("Provide --url or --file")

        print(json.dumps(result, indent=2))

    elif args.command == "sync":
        if not args.folder:
            print("❌ No folder specified.", file=sys.stderr)
            print("   Usage: python scripts/run.py source_manager.py sync <folder>", file=sys.stderr)
            raise SystemExit(1)

        folder_path = Path(args.folder).resolve()
        if not folder_path.is_dir():
            print(f"❌ Folder not found: {folder_path}", file=sys.stderr)
            raise SystemExit(1)

        # Resolve notebook target
        folder_name = folder_path.stem
        notebook_id, create_new = _resolve_notebook_target(args, folder_name)

        # Get active account
        account_mgr = AccountManager()
        active = account_mgr.get_active_account()
        if not active:
            print("❌ No active Google account.", file=sys.stderr)
            print("   Run: python scripts/run.py auth_manager.py accounts list", file=sys.stderr)
            raise SystemExit(1)

        # Create notebook if needed
        if create_new:
            async with NotebookLMWrapper() as wrapper:
                nb_result = await wrapper.create_notebook(folder_name)
                notebook_id = nb_result["id"]
            print(f"📓 Created new notebook: {folder_name}")

            library = NotebookLibrary()
            url = f"https://notebooklm.google.com/notebook/{notebook_id}"
            library.add_notebook(url=url, name=folder_name, description=f"Synced from {folder_name}", topics=[], notebook_id=notebook_id)
            library.select_notebook(notebook_id)
            print(f"✅ Activated notebook: {folder_name}")

        if not notebook_id:
            print("❌ No notebook specified and create-new not specified.", file=sys.stderr)
            raise SystemExit(1)

        # Create sync manager and run sync
        sync_mgr = SyncManager(str(folder_path))

        # Rebuild option - delete tracking file
        if args.rebuild and sync_mgr.tracking_file.exists():
            sync_mgr.tracking_file.unlink()
            print(f"🗑️ Cleared tracking file for rebuild")

        result = await sync_mgr.execute_sync(
            notebook_id=notebook_id,
            account_index=active.index,
            account_email=active.email,
            dry_run=args.dry_run,
        )

        print(json.dumps(result, indent=2))


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
