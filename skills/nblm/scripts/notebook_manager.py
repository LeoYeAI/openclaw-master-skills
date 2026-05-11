#!/usr/bin/env python3
"""
Notebook Library Management for NotebookLM
Manages a library of NotebookLM notebooks with metadata
Based on the MCP server implementation
"""

import asyncio
import json
import argparse
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from account_manager import AccountManager


def _normalize_id(text: str) -> str:
    """
    Normalize text for use as notebook ID.
    Converts smart quotes to ASCII, normalizes Unicode, lowercases, replaces spaces.
    """
    # Unicode smart quotes to ASCII
    quote_map = {
        '\u2018': "'",  # LEFT SINGLE QUOTATION MARK
        '\u2019': "'",  # RIGHT SINGLE QUOTATION MARK
        '\u201c': '"',  # LEFT DOUBLE QUOTATION MARK
        '\u201d': '"',  # RIGHT DOUBLE QUOTATION MARK
        '\u2013': '-',  # EN DASH
        '\u2014': '-',  # EM DASH
        '\u2026': '...',  # HORIZONTAL ELLIPSIS
    }
    for unicode_char, ascii_char in quote_map.items():
        text = text.replace(unicode_char, ascii_char)

    # Normalize Unicode to ASCII-compatible form
    text = unicodedata.normalize('NFKC', text)

    # Lowercase and replace spaces/underscores
    return text.lower().replace(' ', '-').replace('_', '-')


class NotebookLibrary:
    """Manages a collection of NotebookLM notebooks with metadata"""

    def __init__(self):
        """Initialize the notebook library"""
        # Store data within the skill directory
        skill_dir = Path(__file__).parent.parent
        self.data_dir = skill_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.library_file = self.data_dir / "library.json"
        self.notebooks: Dict[str, Dict[str, Any]] = {}
        self.active_notebook_id: Optional[str] = None

        # Load existing library
        self._load_library()

    def _load_library(self):
        """Load library from disk"""
        if self.library_file.exists():
            try:
                with open(self.library_file, 'r') as f:
                    data = json.load(f)
                    self.notebooks = data.get('notebooks', {})
                    self.active_notebook_id = data.get('active_notebook_id')
                    print(f"📚 Loaded library with {len(self.notebooks)} notebooks")
            except Exception as e:
                print(f"⚠️ Error loading library: {e}")
                self.notebooks = {}
                self.active_notebook_id = None
        else:
            self._save_library()

    def _save_library(self):
        """Save library to disk"""
        try:
            data = {
                'notebooks': self.notebooks,
                'active_notebook_id': self.active_notebook_id,
                'updated_at': datetime.now().isoformat()
            }
            with open(self.library_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving library: {e}")

    def add_notebook(
        self,
        url: str,
        name: str,
        description: str,
        topics: List[str],
        content_types: Optional[List[str]] = None,
        use_cases: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        notebook_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new notebook to the library

        Args:
            url: NotebookLM notebook URL
            name: Display name for the notebook
            description: What's in this notebook
            topics: Topics covered
            content_types: Types of content (optional)
            use_cases: When to use this notebook (optional)
            tags: Additional tags for organization (optional)
            notebook_id: Explicit notebook ID (optional, auto-generated from name if not provided)

        Returns:
            The created notebook object
        """
        # Use provided ID or generate from name
        if notebook_id is None:
            notebook_id = _normalize_id(name)

        # Check for duplicates
        if notebook_id in self.notebooks:
            raise ValueError(f"Notebook with ID '{notebook_id}' already exists")

        # Get active account for association
        account_mgr = AccountManager()
        active_account = account_mgr.get_active_account()

        # Create notebook object
        notebook = {
            'id': notebook_id,
            'url': url,
            'name': name,
            'description': description,
            'topics': topics,
            'content_types': content_types or [],
            'use_cases': use_cases or [],
            'tags': tags or [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'use_count': 0,
            'last_used': None,
            # Account association
            'account_index': active_account.index if active_account else None,
            'account_email': active_account.email if active_account else None,
        }

        # Add to library
        self.notebooks[notebook_id] = notebook

        # Set as active if it's the first notebook
        if len(self.notebooks) == 1:
            self.active_notebook_id = notebook_id

        self._save_library()

        print(f"✅ Added notebook: {name} ({notebook_id})")
        return notebook

    def remove_notebook(self, notebook_id: str) -> bool:
        """
        Remove a notebook from the library

        Args:
            notebook_id: ID of notebook to remove

        Returns:
            True if removed, False if not found
        """
        # Normalize input ID for matching
        normalized_input = _normalize_id(notebook_id)

        # Find matching ID
        match_id = None
        if notebook_id in self.notebooks:
            match_id = notebook_id
        else:
            for stored_id in self.notebooks:
                if _normalize_id(stored_id) == normalized_input:
                    match_id = stored_id
                    break

        if match_id:
            del self.notebooks[match_id]

            # Clear active if it was removed
            if self.active_notebook_id == match_id:
                self.active_notebook_id = None
                # Set new active if there are other notebooks
                if self.notebooks:
                    self.active_notebook_id = list(self.notebooks.keys())[0]

            self._save_library()
            print(f"✅ Removed notebook: {match_id}")
            return True

        print(f"⚠️ Notebook not found: {notebook_id}")
        return False

    def update_notebook(
        self,
        notebook_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        topics: Optional[List[str]] = None,
        content_types: Optional[List[str]] = None,
        use_cases: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update notebook metadata

        Args:
            notebook_id: ID of notebook to update
            Other args: Fields to update (None = keep existing)

        Returns:
            Updated notebook object
        """
        if notebook_id not in self.notebooks:
            raise ValueError(f"Notebook not found: {notebook_id}")

        notebook = self.notebooks[notebook_id]

        # Update fields if provided
        if name is not None:
            notebook['name'] = name
        if description is not None:
            notebook['description'] = description
        if topics is not None:
            notebook['topics'] = topics
        if content_types is not None:
            notebook['content_types'] = content_types
        if use_cases is not None:
            notebook['use_cases'] = use_cases
        if tags is not None:
            notebook['tags'] = tags
        if url is not None:
            notebook['url'] = url

        notebook['updated_at'] = datetime.now().isoformat()

        self._save_library()
        print(f"✅ Updated notebook: {notebook['name']}")
        return notebook

    def get_notebook(self, notebook_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific notebook by ID"""
        return self.notebooks.get(notebook_id)

    def list_notebooks(self) -> List[Dict[str, Any]]:
        """List all notebooks in the library"""
        return list(self.notebooks.values())

    def list_notebooks_for_account(self, account_index: int = None) -> List[Dict[str, Any]]:
        """List notebooks for a specific account or active account.

        Args:
            account_index: Account index to filter by. If None, uses active account.
        """
        account_mgr = AccountManager()

        if account_index is None:
            active = account_mgr.get_active_account()
            if active:
                account_index = active.index

        if account_index is None:
            # No account filtering - return all
            return self.list_notebooks()

        return [
            nb for nb in self.notebooks.values()
            if nb.get('account_index') == account_index
        ]

    def list_all_notebooks_grouped(self) -> Dict[str, List[Dict[str, Any]]]:
        """List all notebooks grouped by account."""
        account_mgr = AccountManager()
        accounts = account_mgr.list_accounts()

        result = {}
        for acc in accounts:
            key = f"[{acc.index}] {acc.email}"
            result[key] = [
                nb for nb in self.notebooks.values()
                if nb.get('account_index') == acc.index
            ]

        # Include unassigned notebooks
        unassigned = [
            nb for nb in self.notebooks.values()
            if nb.get('account_index') is None
        ]
        if unassigned:
            result["[?] Unassigned"] = unassigned

        return result

    def search_notebooks(self, query: str) -> List[Dict[str, Any]]:
        """
        Search notebooks by query

        Args:
            query: Search query (searches name, description, topics, tags)

        Returns:
            List of matching notebooks
        """
        query_lower = query.lower()
        results = []

        for notebook in self.notebooks.values():
            # Search in various fields
            searchable = [
                notebook['name'].lower(),
                notebook['description'].lower(),
                ' '.join(notebook['topics']).lower(),
                ' '.join(notebook['tags']).lower(),
                ' '.join(notebook.get('use_cases', [])).lower()
            ]

            if any(query_lower in field for field in searchable):
                results.append(notebook)

        return results

    def select_notebook(self, notebook_id: str) -> Dict[str, Any]:
        """
        Set a notebook as active

        Args:
            notebook_id: ID of notebook to activate

        Returns:
            The activated notebook
        """
        # Normalize input ID for matching
        normalized_input = _normalize_id(notebook_id)

        # Try exact match first, then normalized match
        match_id = None
        if notebook_id in self.notebooks:
            match_id = notebook_id
        else:
            # Find by normalized ID
            for stored_id in self.notebooks:
                if _normalize_id(stored_id) == normalized_input:
                    match_id = stored_id
                    break

        if match_id is None:
            raise ValueError(f"Notebook not found: {notebook_id}")

        self.active_notebook_id = match_id
        self._save_library()

        notebook = self.notebooks[match_id]
        print(f"✅ Activated notebook: {notebook['name']}")
        return notebook

    def get_active_notebook(self) -> Optional[Dict[str, Any]]:
        """Get the currently active notebook"""
        if self.active_notebook_id:
            return self.notebooks.get(self.active_notebook_id)
        return None

    def increment_use_count(self, notebook_id: str) -> Dict[str, Any]:
        """
        Increment usage counter for a notebook

        Args:
            notebook_id: ID of notebook that was used

        Returns:
            Updated notebook
        """
        if notebook_id not in self.notebooks:
            raise ValueError(f"Notebook not found: {notebook_id}")

        notebook = self.notebooks[notebook_id]
        notebook['use_count'] += 1
        notebook['last_used'] = datetime.now().isoformat()

        self._save_library()
        return notebook

    def get_stats(self) -> Dict[str, Any]:
        """Get library statistics"""
        total_notebooks = len(self.notebooks)
        total_topics = set()
        total_use_count = 0

        for notebook in self.notebooks.values():
            total_topics.update(notebook['topics'])
            total_use_count += notebook['use_count']

        # Find most used
        most_used = None
        if self.notebooks:
            most_used = max(
                self.notebooks.values(),
                key=lambda n: n['use_count']
            )

        return {
            'total_notebooks': total_notebooks,
            'total_topics': len(total_topics),
            'total_use_count': total_use_count,
            'active_notebook': self.get_active_notebook(),
            'most_used_notebook': most_used,
            'library_path': str(self.library_file)
        }


def extract_notebook_id(input_value: str) -> Optional[str]:
    """Extract notebook ID from URL or raw ID input."""
    # UUID pattern for notebook IDs
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

    # If it's a URL, extract the ID
    if 'notebooklm.google.com' in input_value:
        match = re.search(uuid_pattern, input_value)
        if match:
            return match.group(0)
        return None

    # Check if it's already a valid UUID
    if re.match(f'^{uuid_pattern}$', input_value):
        return input_value

    return None


async def discover_notebook_metadata(notebook_id: str) -> Dict[str, Any]:
    """Query notebook to discover its name, description, and topics."""
    from notebooklm_wrapper import NotebookLMWrapper, NotebookLMError

    result = {
        'name': 'Untitled',
        'description': '',
        'topics': []
    }

    async with NotebookLMWrapper() as wrapper:
        # Get notebook title from API
        print("   Fetching notebook info...")
        notebooks = await wrapper.list_notebooks()
        for nb in notebooks:
            if nb.get('id') == notebook_id:
                result['name'] = nb.get('title', 'Untitled')
                break

        # Query notebook content for description and topics
        print("   Analyzing notebook content...")
        try:
            question = (
                "What is this notebook about? Respond in this exact JSON format only, no other text:\n"
                '{"description": "one sentence description", "topics": ["topic1", "topic2", "topic3"]}'
            )
            response = await wrapper.chat(notebook_id, question)
            text = response.get('text', '')

            # Extract JSON from response
            json_match = re.search(r'\{[^{}]*"description"[^{}]*"topics"[^{}]*\}', text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                result['description'] = parsed.get('description', '')
                result['topics'] = parsed.get('topics', [])
            else:
                # Fallback: use the response as description
                result['description'] = text[:200] if text else ''
        except NotebookLMError as e:
            print(f"   ⚠️ Could not analyze content: {e.message}")
        except Exception as e:
            print(f"   ⚠️ Could not analyze content: {e}")

    return result


def main():
    """Command-line interface for notebook management"""
    parser = argparse.ArgumentParser(description='Manage NotebookLM library')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Add command - Smart Add with auto-discovery
    add_parser = subparsers.add_parser('add', help='Add a notebook (auto-discovers metadata)')
    add_parser.add_argument('identifier', nargs='?', help='Notebook ID or URL')
    add_parser.add_argument('--url', help='NotebookLM URL (alternative to positional)')
    add_parser.add_argument('--notebook-id', help='NotebookLM notebook ID (alternative to positional)')
    add_parser.add_argument('--name', help='Override auto-discovered name')
    add_parser.add_argument('--description', help='Override auto-discovered description')
    add_parser.add_argument('--topics', help='Override auto-discovered topics (comma-separated)')
    add_parser.add_argument('--tags', help='Additional tags (comma-separated)')

    # List command
    list_parser = subparsers.add_parser('list', help='List all notebooks')
    list_parser.add_argument('--all-accounts', action='store_true',
                             help='Show notebooks from all accounts')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search notebooks')
    search_parser.add_argument('--query', required=True, help='Search query')

    # Activate command
    activate_parser = subparsers.add_parser('activate', help='Set active notebook')
    activate_parser.add_argument('--id', required=True, help='Notebook ID')

    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove a notebook')
    remove_parser.add_argument('--id', required=True, help='Notebook ID')

    # Stats command
    subparsers.add_parser('stats', help='Show library statistics')

    args = parser.parse_args()

    # Initialize library
    library = NotebookLibrary()

    # Execute command
    if args.command == 'add':
        # Smart Add: auto-discover metadata from notebook
        input_value = args.identifier or args.url or args.notebook_id

        if not input_value:
            print("❌ Error: Provide a notebook ID or URL")
            print("   Usage: notebook_manager.py add <notebook-id-or-url>")
            return 1

        # Extract notebook ID from input
        notebook_id = extract_notebook_id(input_value)
        if not notebook_id:
            print(f"❌ Error: Cannot extract notebook ID from: {input_value}")
            return 1

        url = f"https://notebooklm.google.com/notebook/{notebook_id}"

        # Check for duplicates by URL
        for existing in library.notebooks.values():
            if notebook_id in existing.get('url', ''):
                print(f"❌ Error: Notebook already in library as '{existing['name']}' ({existing['id']})")
                return 1

        print(f"🔍 Discovering notebook metadata...")

        # Auto-discover metadata using async wrapper
        try:
            discovered = asyncio.run(discover_notebook_metadata(notebook_id))
        except Exception as e:
            print(f"❌ Error discovering metadata: {e}")
            return 1

        # Use discovered values, allow overrides
        name = args.name or discovered.get('name', 'Untitled')
        description = args.description or discovered.get('description', '')
        topics = [t.strip() for t in args.topics.split(',')] if args.topics else discovered.get('topics', [])
        tags = [t.strip() for t in args.tags.split(',')] if args.tags else []

        print(f"   Name: {name}")
        print(f"   Description: {description[:80]}{'...' if len(description) > 80 else ''}")
        print(f"   Topics: {', '.join(topics)}")

        notebook = library.add_notebook(
            url=url,
            name=name,
            description=description,
            topics=topics,
            tags=tags
        )
        print(json.dumps(notebook, indent=2))

    elif args.command == 'list':
        account_mgr = AccountManager()
        active = account_mgr.get_active_account()

        if hasattr(args, 'all_accounts') and args.all_accounts:
            # Show all notebooks grouped by account
            grouped = library.list_all_notebooks_grouped()
            print("\n📚 All Notebooks:")
            for account_key, notebooks in grouped.items():
                print(f"\n  {account_key}:")
                if notebooks:
                    for notebook in notebooks:
                        active_mark = " [ACTIVE]" if notebook['id'] == library.active_notebook_id else ""
                        print(f"      📓 {notebook['name']}{active_mark}")
                        print(f"         ID: {notebook['id']}")
                else:
                    print("      (no notebooks)")
        else:
            # Show notebooks for active account
            if active:
                print(f"\n📧 Active account: [{active.index}] {active.email}")
                notebooks = library.list_notebooks_for_account()
            else:
                notebooks = library.list_notebooks()

            if notebooks:
                print("\n📚 Notebook Library:")
                for notebook in notebooks:
                    active_mark = " [ACTIVE]" if notebook['id'] == library.active_notebook_id else ""
                    print(f"\n  📓 {notebook['name']}{active_mark}")
                    print(f"     ID: {notebook['id']}")
                    print(f"     Topics: {', '.join(notebook['topics'])}")
                    print(f"     Uses: {notebook['use_count']}")
            else:
                print("📚 No notebooks for this account. Add notebooks with: notebook_manager.py add")

    elif args.command == 'search':
        results = library.search_notebooks(args.query)
        if results:
            print(f"\n🔍 Found {len(results)} notebooks:")
            for notebook in results:
                print(f"\n  📓 {notebook['name']} ({notebook['id']})")
                print(f"     {notebook['description']}")
        else:
            print(f"🔍 No notebooks found for: {args.query}")

    elif args.command == 'activate':
        notebook = library.select_notebook(args.id)
        print(f"Now using: {notebook['name']}")

    elif args.command == 'remove':
        if library.remove_notebook(args.id):
            print("Notebook removed from library")

    elif args.command == 'stats':
        stats = library.get_stats()
        print("\n📊 Library Statistics:")
        print(f"  Total notebooks: {stats['total_notebooks']}")
        print(f"  Total topics: {stats['total_topics']}")
        print(f"  Total uses: {stats['total_use_count']}")
        if stats['active_notebook']:
            print(f"  Active: {stats['active_notebook']['name']}")
        if stats['most_used_notebook']:
            print(f"  Most used: {stats['most_used_notebook']['name']} ({stats['most_used_notebook']['use_count']} uses)")
        print(f"  Library path: {stats['library_path']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()