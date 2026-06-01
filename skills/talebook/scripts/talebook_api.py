#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
talebook_api.py — Talebook REST API Client

Usage:
    python3 talebook_api.py <tool-name> '<json-args>'

Environment Variables:
    TALEBOOK_HOST       Server URL with port (e.g., http://192.168.1.2:8082)
    TALEBOOK_USER       Login username
    TALEBOOK_PASSWORD   Login password

Authentication:
    Automatically signs in via /api/user/sign_in before each tool invocation.
    Session cookies (user_id, lt) are maintained throughout the script lifecycle.
    If err=user.need_login is received, the script re-authenticates once and retries.
"""

import json
import os
import sys
import urllib.parse
from typing import Any, Dict, Optional


# ============================================================================
# Constants
# ============================================================================

REQUIRED_ENV_VARS = ["TALEBOOK_HOST", "TALEBOOK_USER", "TALEBOOK_PASSWORD"]

ERROR_MESSAGES = {
    "env_missing": {
        "status": "error",
        "message": "TALEBOOK_HOST is not set. Please configure TALEBOOK_HOST (e.g. http://192.168.31.102:8082), TALEBOOK_USER and TALEBOOK_PASSWORD."
    },
    "auth_missing": {
        "status": "error",
        "message": "TALEBOOK_USER or TALEBOOK_PASSWORD is not set. Authentication is required."
    }
}


# ============================================================================
# TalebookAPI Class
# ============================================================================

class TalebookAPI:
    """Main API client for Talebook REST API."""

    def __init__(self, host: str, username: str, password: str):
        """
        Initialize Talebook API client.

        Args:
            host: Server URL with port (e.g., http://127.0.0.1:8082)
            username: Login username
            password: Login password
        """
        self.host = host.rstrip('/')
        self.username = username
        self.password = password
        self.session_cookies = {}

        # Try importing requests
        try:
            import requests
            self.requests = requests
        except ImportError:
            self._print_error("Python 'requests' library is required. Install with: pip3 install requests")
            sys.exit(1)

    def _print_error(self, message: str) -> None:
        """Print error to stderr."""
        print(json.dumps({"status": "error", "message": message}), file=sys.stderr)

    def sign_in(self) -> None:
        """Authenticate with the server and store session cookies."""
        url = f"{self.host}/api/user/sign_in"
        # Use form-encoded data (not JSON) as required by the server
        data = f"username={self.username}&password={self.password}"

        try:
            resp = self.requests.post(
                url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            resp.raise_for_status()
            result = resp.json()

            if result.get("err") != "ok":
                self._print_error(f"Login failed: {json.dumps(result)}")
                sys.exit(1)

            # Store cookies for subsequent requests
            self.session_cookies.update(resp.cookies.get_dict())

        except Exception as e:
            self._print_error(f"Login failed: {str(e)}")
            sys.exit(1)

    def _call_api(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """
        Internal method to call API endpoints.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g., /api/user/info)
            **kwargs: Additional arguments for requests (data, json, files, etc.)

        Returns:
            Parsed JSON response
        """
        url = f"{self.host}{path}"
        kwargs.setdefault('cookies', self.session_cookies)
        kwargs.setdefault('timeout', 30)

        try:
            resp = self.requests.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _call_with_auto_relogin(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """
        Call API and automatically re-authenticate if session expired.

        Args:
            method: HTTP method
            path: API path
            **kwargs: Additional arguments for requests

        Returns:
            Parsed JSON response
        """
        result = self._call_api(method, path, **kwargs)

        if result.get("err") == "user.need_login":
            self.sign_in()
            result = self._call_api(method, path, **kwargs)

        return result

    # ========================================================================
    # Tool Methods
    # ========================================================================

    def get_user_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get current user info and system statistics."""
        return self._call_with_auto_relogin("GET", "/api/user/info")

    def library_stats(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get library statistics: total, ebook, physical book counts."""
        return self._call_with_auto_relogin("GET", "/api/library/stats")

    def reading_stats(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get current user's reading statistics."""
        return self._call_with_auto_relogin("GET", "/api/reading/stats")

    def search_books(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search books by keyword (title or author).

        Args:
            name (str, required): Search keyword
            num (int, optional): Results per page (default: 20)
            page (int, optional): Page number (default: 1)
        """
        name = args.get("name", "")
        num = args.get("num", 20)
        page = args.get("page", 1)
        start = (page - 1) * num

        encoded_name = urllib.parse.quote(name)
        return self._call_with_auto_relogin(
            "GET",
            f"/api/search?name={encoded_name}&num={num}&start={start}"
        )

    def search_by_category(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search books by category.

        Args:
            category (str, required): Category name
            num (int, optional): Results per page (default: 20)
            page (int, optional): Page number (default: 1)
        """
        category = args.get("category", "")
        num = args.get("num", 20)
        page = args.get("page", 1)
        start = (page - 1) * num

        query = urllib.parse.quote(f'#category:="{category}"')
        return self._call_with_auto_relogin(
            "GET",
            f"/api/search?name={query}&num={num}&start={start}"
        )

    def get_book(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed book information.

        Args:
            book_id (int, required): Book ID
        """
        book_id = args.get("book_id")
        if not book_id:
            return {"status": "error", "message": "book_id is required"}

        return self._call_with_auto_relogin("GET", f"/api/book/{book_id}")

    def edit_book(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit book metadata.

        Args:
            book_id (int, required): Book ID
            title (str, optional): Book title
            authors (array/string, optional): Author list
            tags (array/string, optional): Tag list
            publisher (str, optional): Publisher
            isbn (str, optional): ISBN
            series (str, optional): Series name
            rating (number, optional): Rating (0-10)
            languages (array, optional): Language codes
            pubdate (str, optional): Publication date
            comments (str, optional): Book description
            category (str, optional): Custom category
            book_count (int, optional): Physical book count
            book_type (int, optional): 0=ebook, 1=physical
        """
        book_id = args.get("book_id")
        if not book_id:
            return {"status": "error", "message": "book_id is required"}

        body = {k: v for k, v in args.items() if k != "book_id"}
        return self._call_with_auto_relogin(
            "POST",
            f"/api/book/{book_id}/edit",
            json=body
        )

    def book_fill(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Auto-fill book info from online sources (admin only).

        Args:
            idlist (array or "all", required): Book ID array or "all"
        """
        idlist = args.get("idlist")
        if not idlist:
            return {
                "status": "error",
                "message": 'idlist is required: an array of book IDs or "all"'
            }

        return self._call_with_auto_relogin(
            "POST",
            "/api/admin/book/fill",
            json={"idlist": idlist}
        )

    def mailto(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send book to email as attachment.

        Args:
            book_id (int, required): Book ID
            email (str, required): Target email address
        """
        book_id = args.get("book_id")
        email = args.get("email", "")

        if not book_id:
            return {"status": "error", "message": "book_id is required"}
        if not email:
            return {"status": "error", "message": "email is required"}

        return self._call_with_auto_relogin(
            "POST",
            f"/api/book/{book_id}/mailto",
            json={"email": email}
        )

    def send_to_device(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send book to reading device via WiFi.

        Args:
            book_id (int, required): Book ID
            device_type (str, required): Device type (kindle/duokan/ireader/etc.)
            device_url (str, required for non-kindle): Device WiFi address
            mailbox (str, required for kindle): Kindle email address
        """
        book_id = args.get("book_id")
        if not book_id:
            return {"status": "error", "message": "book_id is required"}

        body = {k: v for k, v in args.items() if k != "book_id"}
        return self._call_with_auto_relogin(
            "POST",
            f"/api/book/{book_id}/send_to_device",
            json=body
        )

    def categories(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get all custom categories and book counts."""
        return self._call_with_auto_relogin("GET", "/api/categories")

    def list_authors(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get all authors and book counts.

        Args:
            show (str, optional): Pass "all" to show all authors
        """
        show = args.get("show", "")
        path = "/api/author?show=all" if show == "all" else "/api/author"
        return self._call_with_auto_relogin("GET", path)

    def get_author_books(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get books by specific author (paginated).

        Args:
            author_name (str, required): Author name
            num (int, optional): Results per page (default: 20)
            page (int, optional): Page number (default: 1)
        """
        author = args.get("author_name", "")
        num = args.get("num", 20)
        page = args.get("page", 1)
        start = (page - 1) * num

        author_enc = urllib.parse.quote(author)
        return self._call_with_auto_relogin(
            "GET",
            f"/api/author/{author_enc}?num={num}&start={start}"
        )

    def book_upload(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload ebook file to library.

        Args:
            file_path (str, required): Absolute path to local file
        """
        file_path = args.get("file_path", "")
        if not file_path:
            return {"status": "error", "message": "file_path is required"}

        if not os.path.isfile(file_path):
            return {"status": "error", "message": f"File not found: {file_path}"}

        try:
            with open(file_path, 'rb') as f:
                files = {'ebook': f}
                return self._call_with_auto_relogin(
                    "POST",
                    "/api/book/upload",
                    files=files
                )
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def book_add_by_isbn(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add physical book by ISBN.

        Args:
            isbn (str, required): ISBN number
        """
        isbn = args.get("isbn", "")
        if not isbn:
            return {"status": "error", "message": "isbn is required"}

        return self._call_with_auto_relogin(
            "POST",
            "/api/book/add",
            json={"isbn": isbn}
        )

    def wants(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mark/unmark book as "want to read".

        Args:
            book_id (int, required): Book ID
            wants (bool, optional): true=mark, false=unmark (default: true)
        """
        book_id = args.get("book_id")
        if not book_id:
            return {"status": "error", "message": "book_id is required"}

        wants_val = args.get("wants", True)
        return self._call_with_auto_relogin(
            "POST",
            f"/api/book/{book_id}/wants",
            json={"wants": wants_val}
        )

    def list_wants(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get current user's want-to-read book list."""
        return self._call_with_auto_relogin("GET", "/api/wants")

    def favorite(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mark/unmark book as favorite.

        Args:
            book_id (int, required): Book ID
            favorite (bool, optional): true=favorite, false=unfavorite (default: true)
        """
        book_id = args.get("book_id")
        if not book_id:
            return {"status": "error", "message": "book_id is required"}

        fav_val = args.get("favorite", True)
        return self._call_with_auto_relogin(
            "POST",
            f"/api/book/{book_id}/favorite",
            json={"favorite": fav_val}
        )

    def list_favorites(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get current user's favorite book list."""
        return self._call_with_auto_relogin("GET", "/api/favorites")

    def reading(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set book reading state.

        Args:
            book_id (int, required): Book ID
            read_state (int, required): 0=unread, 1=reading, 2=finished
        """
        book_id = args.get("book_id")
        if not book_id:
            return {"status": "error", "message": "book_id is required"}

        read_state = args.get("read_state", 1)
        return self._call_with_auto_relogin(
            "POST",
            f"/api/book/{book_id}/readstate",
            json={"read_state": read_state}
        )

    def list_reading(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get current user's reading book list."""
        return self._call_with_auto_relogin("GET", "/api/reading")

    def read_done(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mark book as finished reading.

        Args:
            book_id (int, required): Book ID
        """
        book_id = args.get("book_id")
        if not book_id:
            return {"status": "error", "message": "book_id is required"}

        return self._call_with_auto_relogin(
            "POST",
            f"/api/book/{book_id}/readstate",
            json={"read_state": 2}
        )

    def list_read_done(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get current user's finished book list."""
        return self._call_with_auto_relogin("GET", "/api/read-done")

    # ========================================================================
    # Tool Dispatcher
    # ========================================================================

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name.

        Args:
            tool_name: Name of the tool to execute
            args: Tool arguments as dict

        Returns:
            Tool execution result
        """
        tool_method = getattr(self, tool_name, None)

        if tool_method is None or not callable(tool_method):
            available_tools = [
                "get_user_info", "library_stats", "reading_stats",
                "search_books", "search_by_category", "get_book", "edit_book",
                "book_fill", "mailto", "send_to_device", "categories",
                "list_authors", "get_author_books", "book_upload",
                "book_add_by_isbn", "wants", "list_wants", "favorite",
                "list_favorites", "reading", "list_reading", "read_done",
                "list_read_done"
            ]
            return {
                "status": "error",
                "message": f"Unknown tool: {tool_name}. Available tools: {', '.join(available_tools)}"
            }

        return tool_method(args)


# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    """Command-line entry point."""
    # Check arguments
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "Usage: talebook_api.py <tool-name> '<json-args>'"
        }), file=sys.stderr)
        sys.exit(1)

    tool_name = sys.argv[1]
    args_json = sys.argv[2] if len(sys.argv) > 2 else "{}"

    # Parse arguments
    try:
        args = json.loads(args_json)
    except json.JSONDecodeError as e:
        print(json.dumps({
            "status": "error",
            "message": f"Invalid JSON arguments: {str(e)}"
        }), file=sys.stderr)
        sys.exit(1)

    # Check environment variables
    host = os.environ.get("TALEBOOK_HOST", "")
    username = os.environ.get("TALEBOOK_USER", "")
    password = os.environ.get("TALEBOOK_PASSWORD", "")

    if not host:
        print(json.dumps(ERROR_MESSAGES["env_missing"]), file=sys.stderr)
        sys.exit(1)

    if not username or not password:
        print(json.dumps(ERROR_MESSAGES["auth_missing"]), file=sys.stderr)
        sys.exit(1)

    # Create API client and execute
    api = TalebookAPI(host, username, password)
    api.sign_in()
    result = api.execute_tool(tool_name, args)

    # Output result
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
