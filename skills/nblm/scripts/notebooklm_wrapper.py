#!/usr/bin/env python3
"""
NotebookLM Wrapper - Thin async wrapper over notebooklm-py.
Handles auth loading, token refresh, and browser fallback for uploads.
"""

import asyncio
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Any, List

from notebooklm import NotebookLMClient

from config import (
    GOOGLE_AUTH_FILE,
    NOTEBOOKLM_TOKEN_STALENESS_DAYS,
    DEFAULT_SESSION_ID,
)


class NotebookLMError(Exception):
    """Base exception for NotebookLM wrapper errors."""

    def __init__(self, message: str, code: str = "UNKNOWN", recovery: str = ""):
        self.message = message
        self.code = code
        self.recovery = recovery
        super().__init__(message)


class NotebookLMAuthError(NotebookLMError):
    """Raised when authentication fails or tokens are invalid."""

    def __init__(self, message: str, recovery: str = ""):
        super().__init__(
            message,
            code="AUTH_ERROR",
            recovery=recovery or "Run: python scripts/run.py auth_manager.py setup",
        )


class NotebookLMWrapper:
    """Thin async wrapper over notebooklm-py with auth loading and fallback."""

    def __init__(self, auth_file: Optional[Path] = None, account_index: Optional[int] = None):
        """Initialize wrapper with optional account selection.

        Args:
            auth_file: Explicit auth file path (overrides account_index)
            account_index: Account index to use (defaults to active account)
        """
        if auth_file:
            self.auth_file = auth_file
        elif account_index is not None:
            from account_manager import AccountManager
            account_mgr = AccountManager()
            account = account_mgr.get_account_by_index(account_index)
            if account:
                self.auth_file = account.file_path
            else:
                raise ValueError(f"Account not found: {account_index}")
        else:
            # Use active account
            from account_manager import AccountManager
            account_mgr = AccountManager()
            active_auth_file = account_mgr.get_active_auth_file()
            self.auth_file = active_auth_file or GOOGLE_AUTH_FILE

        self._client: Optional[NotebookLMClient] = None
        self._auth_data: Optional[dict] = None

    async def __aenter__(self) -> "NotebookLMWrapper":
        """Load auth and initialize notebooklm-py client."""
        # Use from_storage() which handles token extraction internally
        self._client = await NotebookLMClient.from_storage(str(self.auth_file))
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up client resources."""
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)
            self._client = None

    def _load_auth_file(self) -> dict:
        """Load auth data from file."""
        if not self.auth_file.exists():
            raise NotebookLMAuthError(
                "Auth file not found",
                recovery="Run: python scripts/run.py auth_manager.py setup",
            )
        try:
            return json.loads(self.auth_file.read_text())
        except json.JSONDecodeError as e:
            raise NotebookLMAuthError(f"Invalid auth file: {e}")

    def _is_token_stale(self) -> bool:
        """Check if tokens are older than staleness threshold."""
        if not self._auth_data:
            return True
        extracted_at = self._auth_data.get("extracted_at")
        if not extracted_at:
            return True
        try:
            timestamp = datetime.fromisoformat(extracted_at.replace("Z", "+00:00"))
            age = datetime.now(timezone.utc) - timestamp
            return age > timedelta(days=NOTEBOOKLM_TOKEN_STALENESS_DAYS)
        except (ValueError, TypeError):
            return True

    @staticmethod
    def _is_auth_error(error: Exception) -> bool:
        """Check if an exception indicates an auth error."""
        message = str(error).lower()
        return any(
            token in message
            for token in ("401", "403", "unauthorized", "not authenticated", "invalid token")
        )

    async def _with_retry(self, coro_func, max_retries: int = 1):
        """Execute coroutine with token refresh retry on auth errors."""
        try:
            return await coro_func()
        except Exception as e:
            if self._is_auth_error(e) and max_retries > 0:
                await self._refresh_tokens()
                return await self._with_retry(coro_func, max_retries - 1)
            raise NotebookLMError(str(e), code="API_ERROR")

    async def _refresh_tokens(self):
        """Refresh tokens using agent-browser."""
        # Import here to avoid circular dependency
        from auth_manager import AuthManager

        auth_manager = AuthManager()
        # This is synchronous but we call it from async context
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, auth_manager.refresh_notebooklm_tokens)

        # Recreate client with fresh tokens using from_storage
        if self._client:
            await self._client.__aexit__(None, None, None)
        self._client = await NotebookLMClient.from_storage(str(self.auth_file))
        await self._client.__aenter__()

    # === Notebooks API ===

    async def create_notebook(self, name: str) -> dict:
        """Create a new notebook. Falls back to browser on failure."""
        async def _create():
            notebook = await self._client.notebooks.create(name)
            return {
                "id": notebook.id,
                "title": notebook.title,
            }
        try:
            return await self._with_retry(_create)
        except NotebookLMError:
            # Fallback to browser creation
            return await self._fallback_create_notebook(name)

    async def list_notebooks(self) -> List[dict]:
        """List all notebooks."""
        async def _list():
            notebooks = await self._client.notebooks.list()
            return [
                {
                    "id": nb.id,
                    "title": nb.title,
                }
                for nb in notebooks
            ]
        return await self._with_retry(_list)

    async def delete_notebook(self, notebook_id: str) -> bool:
        """Delete a notebook."""
        async def _delete():
            await self._client.notebooks.delete(notebook_id)
            return True
        return await self._with_retry(_delete)

    async def rename_notebook(self, notebook_id: str, new_title: str) -> dict:
        """Rename a notebook."""
        async def _rename():
            notebook = await self._client.notebooks.rename(notebook_id, new_title)
            return {
                "id": notebook.id,
                "title": notebook.title,
            }
        return await self._with_retry(_rename)

    async def get_notebook_summary(self, notebook_id: str) -> str:
        """Get AI-generated summary for a notebook."""
        async def _summary():
            return await self._client.notebooks.summary(notebook_id)
        return await self._with_retry(_summary)

    async def get_notebook_description(self, notebook_id: str) -> dict:
        """Get AI-generated description and suggested topics."""
        async def _description():
            desc = await self._client.notebooks.description(notebook_id)
            return {
                "summary": desc.summary,
                "suggested_topics": [t.question for t in desc.suggested_topics] if hasattr(desc, 'suggested_topics') else [],
            }
        return await self._with_retry(_description)

    # === Sources API ===

    async def add_file(self, notebook_id: str, file_path: Path) -> dict:
        """Upload a file to a notebook. Falls back to browser on failure."""
        async def _add():
            source = await self._client.sources.add_file(notebook_id, file_path)
            return {
                "source_id": source.id,
                "title": source.title,
                "source_type": source.source_type,
            }

        try:
            return await self._with_retry(_add)
        except NotebookLMError:
            # Fallback to browser upload
            return await self._fallback_upload(notebook_id, file_path)

    async def add_url(self, notebook_id: str, url: str) -> dict:
        """Add a URL source to a notebook."""
        async def _add():
            source = await self._client.sources.add_url(notebook_id, url)
            return {
                "source_id": source.id,
                "title": source.title,
                "source_type": source.source_type,
            }
        return await self._with_retry(_add)

    async def add_youtube(self, notebook_id: str, url: str) -> dict:
        """Add a YouTube video source to a notebook."""
        async def _add():
            source = await self._client.sources.add_youtube(notebook_id, url)
            return {
                "source_id": source.id,
                "title": source.title,
                "source_type": source.source_type,
            }
        return await self._with_retry(_add)

    async def add_text(self, notebook_id: str, title: str, content: str) -> dict:
        """Add text content as a source to a notebook."""
        async def _add():
            source = await self._client.sources.add_text(notebook_id, title, content)
            return {
                "source_id": source.id,
                "title": source.title,
                "source_type": source.source_type,
            }
        return await self._with_retry(_add)

    async def list_sources(self, notebook_id: str) -> List[dict]:
        """List all sources in a notebook."""
        async def _list():
            sources = await self._client.sources.list(notebook_id)
            return [
                {
                    "source_id": src.id,
                    "title": src.title,
                    "source_type": src.source_type,
                    "is_ready": src.is_ready,
                }
                for src in sources
            ]
        return await self._with_retry(_list)

    async def get_source(self, notebook_id: str, source_id: str) -> dict:
        """Get details of a specific source."""
        async def _get():
            source = await self._client.sources.get(notebook_id, source_id)
            return {
                "source_id": source.id,
                "title": source.title,
                "source_type": source.source_type,
                "is_ready": source.is_ready,
            }
        return await self._with_retry(_get)

    async def delete_source(self, notebook_id: str, source_id: str) -> bool:
        """Delete a source from a notebook."""
        async def _delete():
            await self._client.sources.delete(notebook_id, source_id)
            return True
        return await self._with_retry(_delete)

    async def rename_source(self, notebook_id: str, source_id: str, new_title: str) -> dict:
        """Rename a source."""
        async def _rename():
            source = await self._client.sources.rename(notebook_id, source_id, new_title)
            return {
                "source_id": source.id,
                "title": source.title,
            }
        return await self._with_retry(_rename)

    async def refresh_source(self, notebook_id: str, source_id: str) -> dict:
        """Refresh a URL source to re-fetch content."""
        async def _refresh():
            source = await self._client.sources.refresh(notebook_id, source_id)
            return {
                "source_id": source.id,
                "title": source.title,
            }
        return await self._with_retry(_refresh)

    async def get_source_fulltext(self, notebook_id: str, source_id: str) -> dict:
        """Get full indexed text content of a source."""
        async def _fulltext():
            fulltext = await self._client.sources.get_fulltext(notebook_id, source_id)
            return {
                "char_count": fulltext.char_count,
                "content": fulltext.content,
            }
        return await self._with_retry(_fulltext)

    async def get_source_guide(self, notebook_id: str, source_id: str) -> dict:
        """Get AI-generated summary and keywords for a source."""
        async def _guide():
            guide = await self._client.sources.get_guide(notebook_id, source_id)
            return guide
        return await self._with_retry(_guide)

    # === Chat API ===

    async def chat(self, notebook_id: str, message: str) -> dict:
        """Send a chat message to a notebook and get a response. Falls back to browser on failure."""
        async def _chat():
            from notebooklm import ChatMode

            # Set mode to DETAILED for comprehensive answers (not quick search)
            await self._client.chat.set_mode(notebook_id, ChatMode.DETAILED)

            # Use client.chat.ask() - chat is a ChatAPI object, not callable
            response = await self._client.chat.ask(notebook_id, message)
            return {
                "text": response.answer,  # AskResult uses 'answer' not 'text'
                "citations": response.references if hasattr(response, "references") else [],
                "conversation_id": response.conversation_id if hasattr(response, "conversation_id") else None,
            }
        try:
            return await self._with_retry(_chat)
        except NotebookLMError:
            # Fallback to browser-based chat
            return await self._fallback_chat(notebook_id, message)

    # === Audio/Podcast API ===

    async def generate_audio(
        self,
        notebook_id: str,
        instructions: str = "",
        audio_format: str = "DEEP_DIVE",
        audio_length: str = "DEFAULT",
    ) -> dict:
        """Generate audio podcast from notebook content."""
        async def _generate():
            from notebooklm import AudioFormat, AudioLength

            format_map = {
                "DEEP_DIVE": AudioFormat.DEEP_DIVE,
                "BRIEF": AudioFormat.BRIEF,
                "CRITIQUE": AudioFormat.CRITIQUE,
                "DEBATE": AudioFormat.DEBATE,
            }
            length_map = {
                "SHORT": AudioLength.SHORT,
                "DEFAULT": AudioLength.DEFAULT,
                "LONG": AudioLength.LONG,
            }

            status = await self._client.artifacts.generate_audio(
                notebook_id,
                audio_format=format_map.get(audio_format.upper(), AudioFormat.DEEP_DIVE),
                audio_length=length_map.get(audio_length.upper(), AudioLength.DEFAULT),
                instructions=instructions or None,
            )
            return {
                "task_id": status.task_id,
                "status": "started",
            }
        return await self._with_retry(_generate)

    async def wait_for_audio(
        self,
        notebook_id: str,
        task_id: str,
        timeout: int = 600,
        poll_interval: int = 10,
    ) -> dict:
        """Wait for audio generation to complete."""
        async def _wait():
            final = await self._client.artifacts.wait_for_completion(
                notebook_id,
                task_id,
                timeout=timeout,
                poll_interval=poll_interval,
            )
            return {
                "is_complete": final.is_complete,
                "is_failed": getattr(final, 'is_failed', False),
                "url": getattr(final, 'url', None),
                "error": getattr(final, 'error', None),
            }
        return await self._with_retry(_wait)

    async def download_audio(
        self,
        notebook_id: str,
        output_path: str,
        artifact_id: str = None,
    ) -> str:
        """Download generated audio file."""
        async def _download():
            path = await self._client.artifacts.download_audio(
                notebook_id,
                output_path,
                artifact_id=artifact_id,
            )
            return str(path)
        return await self._with_retry(_download)

    async def list_artifacts(self, notebook_id: str, artifact_type: str = None) -> List[dict]:
        """List all artifacts in a notebook.

        Args:
            notebook_id: The notebook ID
            artifact_type: Optional filter - 'audio', 'video', 'slide-deck', 'infographic'
        """
        async def _list():
            artifacts = await self._client.artifacts.list(notebook_id)
            result = []
            for artifact in artifacts:
                # Handle different possible attribute names from the API
                art_type = getattr(artifact, 'artifact_type', None) or getattr(artifact, 'type', None) or getattr(artifact, 'status_str', 'unknown')
                item = {
                    "artifact_id": artifact.id,
                    "type": art_type,
                    "title": getattr(artifact, 'title', None),
                    "status": getattr(artifact, 'status', None) or getattr(artifact, 'status_str', None),
                    "is_completed": getattr(artifact, 'is_completed', False),
                    "created_at": getattr(artifact, 'created_at', None),
                    "url": getattr(artifact, 'url', None),
                }
                if artifact_type is None or str(art_type).lower() == artifact_type.lower():
                    result.append(item)
            return result
        return await self._with_retry(_list)

    async def get_artifact(self, notebook_id: str, artifact_id: str) -> dict:
        """Get details of a specific artifact."""
        async def _get():
            artifact = await self._client.artifacts.get(notebook_id, artifact_id)
            art_type = getattr(artifact, 'artifact_type', None) or getattr(artifact, 'type', None) or getattr(artifact, 'status_str', 'unknown')
            return {
                "artifact_id": artifact.id,
                "type": art_type,
                "title": getattr(artifact, 'title', None),
                "status": getattr(artifact, 'status', None) or getattr(artifact, 'status_str', None),
                "is_complete": getattr(artifact, 'is_completed', False),
                "is_failed": getattr(artifact, 'is_failed', False),
                "url": getattr(artifact, 'url', None),
                "error": getattr(artifact, 'error', None),
                "created_at": getattr(artifact, 'created_at', None),
            }
        return await self._with_retry(_get)

    async def delete_artifact(self, notebook_id: str, artifact_id: str) -> bool:
        """Delete an artifact from a notebook."""
        async def _delete():
            await self._client.artifacts.delete(notebook_id, artifact_id)
            return True
        return await self._with_retry(_delete)

    # === Slide Deck / Infographic API ===

    async def generate_slide_deck(
        self,
        notebook_id: str,
        instructions: str = "",
        slide_format: str = "DETAILED_DECK",
        slide_length: str = "DEFAULT",
    ) -> dict:
        """Generate slide deck from notebook content.

        Args:
            notebook_id: The notebook ID
            instructions: Custom instructions for the slide deck
            slide_format: DETAILED_DECK or PRESENTER_SLIDES
            slide_length: SHORT or DEFAULT
        """
        async def _generate():
            from notebooklm.rpc.types import SlideDeckFormat, SlideDeckLength

            format_map = {
                "DETAILED_DECK": SlideDeckFormat.DETAILED_DECK,
                "PRESENTER_SLIDES": SlideDeckFormat.PRESENTER_SLIDES,
            }
            length_map = {
                "SHORT": SlideDeckLength.SHORT,
                "DEFAULT": SlideDeckLength.DEFAULT,
            }

            status = await self._client.artifacts.generate_slide_deck(
                notebook_id,
                slide_format=format_map.get(slide_format.upper(), SlideDeckFormat.DETAILED_DECK),
                slide_length=length_map.get(slide_length.upper(), SlideDeckLength.DEFAULT),
                instructions=instructions or None,
            )
            return {
                "task_id": status.task_id,
                "status": "started",
            }
        return await self._with_retry(_generate)

    async def generate_infographic(
        self,
        notebook_id: str,
        instructions: str = "",
        orientation: str = "LANDSCAPE",
        detail_level: str = "STANDARD",
    ) -> dict:
        """Generate infographic from notebook content.

        Args:
            notebook_id: The notebook ID
            instructions: Custom instructions for the infographic
            orientation: LANDSCAPE, PORTRAIT, or SQUARE
            detail_level: CONCISE, STANDARD, or DETAILED
        """
        async def _generate():
            from notebooklm.rpc.types import InfographicOrientation, InfographicDetail

            orientation_map = {
                "LANDSCAPE": InfographicOrientation.LANDSCAPE,
                "PORTRAIT": InfographicOrientation.PORTRAIT,
                "SQUARE": InfographicOrientation.SQUARE,
            }
            detail_map = {
                "CONCISE": InfographicDetail.CONCISE,
                "STANDARD": InfographicDetail.STANDARD,
                "DETAILED": InfographicDetail.DETAILED,
            }

            status = await self._client.artifacts.generate_infographic(
                notebook_id,
                orientation=orientation_map.get(orientation.upper(), InfographicOrientation.LANDSCAPE),
                detail_level=detail_map.get(detail_level.upper(), InfographicDetail.STANDARD),
                instructions=instructions or None,
            )
            return {
                "task_id": status.task_id,
                "status": "started",
            }
        return await self._with_retry(_generate)

    async def download_slide_deck(
        self,
        notebook_id: str,
        output_path: str,
        artifact_id: str = None,
    ) -> str:
        """Download generated slide deck as PDF."""
        async def _download():
            path = await self._client.artifacts.download_slide_deck(
                notebook_id,
                output_path,
                artifact_id=artifact_id,
            )
            return str(path)
        return await self._with_retry(_download)

    async def download_infographic(
        self,
        notebook_id: str,
        output_path: str,
        artifact_id: str = None,
    ) -> str:
        """Download generated infographic as PNG."""
        async def _download():
            path = await self._client.artifacts.download_infographic(
                notebook_id,
                output_path,
                artifact_id=artifact_id,
            )
            return str(path)
        return await self._with_retry(_download)

    async def get_audio_status(self, notebook_id: str, task_id: str) -> dict:
        """Get status of an audio generation task."""
        async def _status():
            status = await self._client.artifacts.poll_status(notebook_id, task_id)
            return {
                "task_id": task_id,
                "status": getattr(status, 'status', 'unknown'),
                "is_complete": getattr(status, 'is_complete', False),
                "is_failed": getattr(status, 'is_failed', False),
                "progress": getattr(status, 'progress', None),
                "url": getattr(status, 'url', None),
                "error": getattr(status, 'error', None),
            }
        return await self._with_retry(_status)

    async def download_artifact(
        self,
        notebook_id: str,
        artifact_id: str,
        output_path: str,
        artifact_type: str = "audio",
    ) -> str:
        """Download any artifact type to local path.

        Args:
            notebook_id: The notebook ID
            artifact_id: The artifact ID
            output_path: Local path to save the file
            artifact_type: 'audio', 'video', 'slide-deck', 'infographic'
        """
        async def _download():
            download_methods = {
                "audio": self._client.artifacts.download_audio,
                "video": self._client.artifacts.download_video,
                "slide-deck": self._client.artifacts.download_slide_deck,
                "infographic": self._client.artifacts.download_infographic,
            }
            method = download_methods.get(artifact_type)
            if not method:
                raise NotebookLMError(
                    f"Unknown artifact type: {artifact_type}",
                    code="INVALID_TYPE",
                    recovery="Use: audio, video, slide-deck, or infographic",
                )
            path = await method(notebook_id, output_path, artifact_id=artifact_id)
            return str(path)
        return await self._with_retry(_download)

    # === Browser Fallback ===

    async def _fallback_create_notebook(self, name: str) -> dict:
        """Create notebook via browser automation when API fails."""
        from agent_browser_client import AgentBrowserClient, AgentBrowserError
        from auth_manager import AuthManager

        loop = asyncio.get_event_loop()

        def _browser_create():
            auth = AuthManager()
            client = AgentBrowserClient(session_id=DEFAULT_SESSION_ID)

            try:
                client.connect()
                auth.restore_auth("google", client=client)

                # Navigate to NotebookLM home
                print("   🌐 Creating notebook via browser...")
                client.navigate("https://notebooklm.google.com")

                import time
                time.sleep(3)

                # Get snapshot and find create notebook button
                snapshot = client.snapshot()
                create_ref = self._find_button_ref(snapshot, ["create", "new notebook", "new"])

                if not create_ref:
                    raise NotebookLMError(
                        "Create notebook button not found",
                        code="ELEMENT_NOT_FOUND",
                        recovery="Check if NotebookLM page loaded correctly",
                    )

                client.click(create_ref)
                time.sleep(2)

                # Get current URL to extract notebook ID
                snapshot = client.snapshot()
                # Look for notebook URL pattern in the page or get from navigation
                # The notebook ID appears in URL after creation

                # Wait for notebook to be created and page to update
                time.sleep(3)

                # Try to get the notebook ID from the URL
                current_url = client.evaluate("window.location.href")
                notebook_id = None
                if current_url and "notebook/" in current_url:
                    parts = current_url.split("notebook/")
                    if len(parts) > 1:
                        notebook_id = parts[1].split("/")[0].split("?")[0]

                if not notebook_id:
                    # Generate a placeholder - we'll get the real ID from the URL later
                    import uuid
                    notebook_id = str(uuid.uuid4())

                auth.save_auth("google", client=client)

                return {
                    "id": notebook_id,
                    "title": name,
                    "created_via": "browser_fallback",
                }

            except AgentBrowserError as e:
                raise NotebookLMError(e.message, code=e.code, recovery=e.recovery)
            finally:
                client.disconnect()

        return await loop.run_in_executor(None, _browser_create)

    async def _fallback_upload(self, notebook_id: str, file_path: Path) -> dict:
        """Upload file via browser automation when API fails."""
        from agent_browser_client import AgentBrowserClient, AgentBrowserError
        from auth_manager import AuthManager

        loop = asyncio.get_event_loop()

        def _browser_upload():
            auth = AuthManager()
            client = AgentBrowserClient(session_id=DEFAULT_SESSION_ID)

            try:
                client.connect()
                auth.restore_auth("google", client=client)

                # Navigate to notebook
                notebook_url = f"https://notebooklm.google.com/notebook/{notebook_id}"
                print(f"   🌐 Navigating to notebook for upload...")
                client.navigate(notebook_url)

                # Wait for page load
                import time
                time.sleep(3)

                # Get snapshot and find add source button
                snapshot = client.snapshot()
                add_ref = self._find_button_ref(snapshot, ["add source", "add sources", "add"])

                if not add_ref:
                    raise NotebookLMError(
                        "Add source button not found",
                        code="ELEMENT_NOT_FOUND",
                        recovery="Check if notebook page loaded correctly",
                    )

                print(f"   📎 Clicking add source button...")
                client.click(add_ref)
                time.sleep(2)

                # Get new snapshot and find upload/file option
                snapshot = client.snapshot()
                upload_ref = self._find_button_ref(snapshot, ["upload", "file", "pdf", "document"])

                if upload_ref:
                    client.click(upload_ref)
                    time.sleep(1)
                    snapshot = client.snapshot()

                # Find file input ref in snapshot
                file_input_ref = self._find_file_input_ref(snapshot)

                if not file_input_ref:
                    raise NotebookLMError(
                        "File input not found",
                        code="ELEMENT_NOT_FOUND",
                        recovery="Retry after page loads completely",
                    )

                # Upload file using agent-browser upload command with ref
                print(f"   📤 Uploading {file_path.name}...")
                client.upload(file_input_ref, [str(file_path)])

                # Wait for upload to process
                print(f"   ⏳ Waiting for upload to complete...")
                time.sleep(10)

                auth.save_auth("google", client=client)

                return {
                    "source_id": None,  # Unknown from browser upload
                    "title": file_path.name,
                    "uploaded_via": "browser_fallback",
                }

            except AgentBrowserError as e:
                raise NotebookLMError(e.message, code=e.code, recovery=e.recovery)
            finally:
                client.disconnect()

        return await loop.run_in_executor(None, _browser_upload)

    async def _fallback_chat(self, notebook_id: str, message: str) -> dict:
        """Chat via browser automation when API fails."""
        from agent_browser_client import AgentBrowserClient, AgentBrowserError
        from auth_manager import AuthManager

        loop = asyncio.get_event_loop()

        def _browser_chat():
            auth = AuthManager()
            client = AgentBrowserClient(session_id=DEFAULT_SESSION_ID)

            try:
                client.connect()
                auth.restore_auth("google", client=client)

                # Navigate to notebook
                notebook_url = f"https://notebooklm.google.com/notebook/{notebook_id}"
                print(f"   🌐 Navigating to notebook...")
                client.navigate(notebook_url)

                import time
                time.sleep(3)

                # Get snapshot and find query input
                print("   ⏳ Finding query input...")
                snapshot = client.snapshot()
                input_ref = self._find_textbox_ref(snapshot)

                if not input_ref:
                    raise NotebookLMError(
                        "Query input not found",
                        code="ELEMENT_NOT_FOUND",
                        recovery="Check if notebook page loaded correctly",
                    )

                # Type the question
                print("   ⌨️ Typing question...")
                client.fill(input_ref, message)
                time.sleep(0.5)

                # Press Enter to submit
                client.press_key("Enter")

                # Wait for response
                print("   ⏳ Waiting for answer...")
                time.sleep(10)  # Initial wait

                # Poll for response (up to 60 seconds)
                answer = None
                for _ in range(12):  # 12 * 5 = 60 seconds max
                    snapshot = client.snapshot()
                    answer = self._extract_chat_response(snapshot)
                    if answer and len(answer) > 50:  # Got substantial response
                        break
                    time.sleep(5)

                if not answer:
                    raise NotebookLMError(
                        "No response received",
                        code="TIMEOUT",
                        recovery="Try again or check if notebook has sources",
                    )

                print("   ✅ Got answer!")
                auth.save_auth("google", client=client)

                return {
                    "text": answer,
                    "citations": [],
                    "via": "browser_fallback",
                }

            except AgentBrowserError as e:
                raise NotebookLMError(e.message, code=e.code, recovery=e.recovery)
            finally:
                client.disconnect()

        return await loop.run_in_executor(None, _browser_chat)

    @staticmethod
    def _find_textbox_ref(snapshot: str) -> Optional[str]:
        """Find textbox/input ref for chat in snapshot."""
        for line in snapshot.splitlines():
            lower = line.lower()
            # Look for textbox or input elements related to chat
            if ("textbox" in lower or "textarea" in lower) and ("ask" in lower or "query" in lower or "question" in lower or "chat" in lower):
                match = re.search(r'\[ref=(\w+)\]', line)
                if match:
                    return match.group(1)
        # Fallback: look for any textbox
        for line in snapshot.splitlines():
            if "textbox" in line.lower():
                match = re.search(r'\[ref=(\w+)\]', line)
                if match:
                    return match.group(1)
        return None

    @staticmethod
    def _extract_chat_response(snapshot: str) -> Optional[str]:
        """Extract the latest chat response from snapshot."""
        lines = snapshot.splitlines()
        # Look for response content - typically in a section after the input
        response_lines = []
        in_response = False

        for line in lines:
            lower = line.lower()
            # Skip input areas
            if "textbox" in lower or "button" in lower:
                if in_response and response_lines:
                    break  # End of response section
                continue
            # Look for text content
            if line.strip() and not line.startswith('[') and len(line.strip()) > 20:
                # Clean up the line (remove refs if any)
                clean_line = re.sub(r'\[ref=\w+\]', '', line).strip()
                if clean_line:
                    response_lines.append(clean_line)
                    in_response = True

        if response_lines:
            return '\n'.join(response_lines)
        return None

    @staticmethod
    def _find_file_input_ref(snapshot: str) -> Optional[str]:
        """Find file input ref in snapshot."""
        for line in snapshot.splitlines():
            lower = line.lower()
            # Look for file input or upload-related elements
            if "file" in lower and ("input" in lower or "upload" in lower):
                match = re.search(r'\[ref=(\w+)\]', line)
                if match:
                    return match.group(1)
        # Fallback: look for any input that might be file-related
        for line in snapshot.splitlines():
            if "input" in line.lower() and "type" not in line.lower():
                match = re.search(r'\[ref=(\w+)\]', line)
                if match:
                    return match.group(1)
        return None

    @staticmethod
    def _find_button_ref(snapshot: str, keywords: List[str]) -> Optional[str]:
        """Find button ref in snapshot matching keywords."""
        for line in snapshot.splitlines():
            lower = line.lower()
            if "button" not in lower:
                continue
            if not any(keyword in lower for keyword in keywords):
                continue
            match = re.search(r'\[ref=(\w+)\]', line)
            if match:
                return match.group(1)
        return None