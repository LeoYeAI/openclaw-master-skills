# -*- coding: utf-8 -*-
"""
Microsoft To Do API Access Script
Access To Do lists and tasks using Microsoft Graph API
"""

# type: ignore  # Ignore missing type hints in msal library

import requests
import json
import os
import atexit
import argparse
import sys
import io

# --- Set default encoding to UTF-8 ---
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
if sys.stdin.encoding != 'utf-8':
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
# ------------------------------------

from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
import msal  # type: ignore


class MicrosoftTodoClient:
    """Microsoft To Do Client"""

    # Default client ID (built-in)
    DEFAULT_CLIENT_ID = "82faeadf-5106-4aa0-bb0d-2c94b300e92a"

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, tenant_id: str = "common", cache_file: Optional[str] = None, debug: bool = False):
        """
        Initialize the client

        Args:
            client_id: Azure application client ID (optional, uses built-in ID by default)
            client_secret: Client secret (optional, used for application flow)
            tenant_id: Tenant ID, default is "common"
            cache_file: Token cache file path (optional, default: ~/.mstodo_token_cache.json)
            debug: Enable debug mode to print API requests and responses (default: False)
        """
        self.client_id = client_id or self.DEFAULT_CLIENT_ID
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.scopes = ["Tasks.Read", "Tasks.ReadWrite"]
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
        self.access_token = None
        self.debug = debug

        # Set cache file path
        if cache_file is None:
            cache_file = os.path.join(Path.home(), ".mstodo_token_cache.json")
        self.cache_file = cache_file

        # Initialize token cache
        self.cache = msal.SerializableTokenCache()
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                self.cache.deserialize(f.read())

        # Register cache saving on exit
        atexit.register(self._save_cache)

    def _save_cache(self):
        """Save token cache to file"""
        if self.cache.has_state_changed:
            with open(self.cache_file, "w") as f:
                f.write(self.cache.serialize())

    def authenticate(self, force_refresh: bool = False):
        """
        Automatic authentication (prioritize cache, return False if no valid token)

        Args:
            force_refresh: Force re-authentication, ignore cache (default: False)

        Returns:
            True if authentication is successful, False if no valid token in cache
        """
        app = msal.PublicClientApplication(self.client_id, authority=self.authority, token_cache=self.cache)

        # If not forcing refresh, try to get token from cache first
        if not force_refresh:
            accounts = app.get_accounts()
            if accounts:
                # Try to silently acquire token
                result = app.acquire_token_silent(self.scopes, account=accounts[0])
                if result and "access_token" in result:
                    self.access_token = result["access_token"]
                    return True

        # No valid token found, return False and let caller handle it
        return False

    def get_device_code_flow(self) -> Optional[Dict[str, Any]]:
        """
        Get device code flow information (Step 1 login: Get verification code)

        Returns:
            Flow information containing user_code and device_code, or None if failed
        """
        app = msal.PublicClientApplication(self.client_id, authority=self.authority, token_cache=self.cache)

        flow = app.initiate_device_flow(scopes=self.scopes)

        if "user_code" not in flow:
            error_msg = flow.get("error", "Unknown error")
            error_desc = flow.get("error_description", "No details")
            print("\n✗ Cannot create device code flow")
            print(f"Error: {error_msg}")
            print(f"Description: {error_desc}")
            return None

        # Save flow information for step 2 use
        flow_cache_file = os.path.join(Path.home(), ".mstodo_device_flow.json")
        with open(flow_cache_file, "w") as f:
            json.dump(flow, f)

        # Only display information users need
        print(f"✓ Verification code generated")
        print(f"\nPlease visit the following link to log in:")
        print(f"{flow.get('verification_uri')}")
        print(f"\nEnter verification code: {flow.get('user_code')}")
        print(f"\nVerify with command: ms-todo-sync.py login verify")

        return flow

    def verify_device_code_flow(self) -> bool:
        """
        Verify device code flow (Step 2 login: Verify verification code)

        Returns:
            True if login is successful
        """
        flow_cache_file = os.path.join(Path.home(), ".mstodo_device_flow.json")

        if not os.path.exists(flow_cache_file):
            print("✗ No flow information found to verify")
            print("Please run first: ms-todo-sync.py login get")
            return False

        try:
            with open(flow_cache_file, "r") as f:
                flow = json.load(f)
        except Exception as e:
            print(f"✗ Failed to read flow information: {e}")
            return False

        app = msal.PublicClientApplication(self.client_id, authority=self.authority, token_cache=self.cache)

        # Wait for user to complete authentication
        result = app.acquire_token_by_device_flow(flow)

        if "access_token" in result:
            self.access_token = result["access_token"]
            self._save_cache()  # Save cache immediately
            print("✓ Authentication successful! Login information saved, you will be logged in automatically next time.")
            # Clear flow cache
            os.remove(flow_cache_file)
            return True
        else:
            print(f"✗ Authentication failed: {result.get('error_description')}")
            return False

    def logout(self):
        """
        Logout and clear cached tokens
        """
        self.access_token = None
        self.cache = msal.SerializableTokenCache()
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
            print("✓ Login information cleared")
        else:
            print("⚠️  No cached login information found")

    def is_authenticated(self) -> bool:
        """
        Check if authentication is successful

        Returns:
            True if authenticated
        """
        return self.access_token is not None

    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send API request"""
        if not self.access_token:
            raise ValueError("Not authenticated, please call authenticate method first")

        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}

        url = f"{self.graph_endpoint}{endpoint}"

        if self.debug:
            print(f"\n🔍 [DEBUG] API Request:")
            print(f"  Method: {method}")
            print(f"  URL: {url}")
            if data:
                print(f"  Request Body: {json.dumps(data, indent=2, ensure_ascii=False)}")

        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if self.debug:
            print(f"\n🔍 [DEBUG] API Response:")
            print(f"  Status Code: {response.status_code}")
            print(f"  Headers: {dict(response.headers)}")

        if response.status_code >= 400:
            # Try to parse error response
            try:
                error_data = response.json()
                if self.debug:
                    print(f"  Error Body: {json.dumps(error_data, indent=2, ensure_ascii=False)}\n")
            except:
                pass
        
        response.raise_for_status()

        if response.status_code == 204:  # No Content
            if self.debug:
                print(f"  Body: (No Content)\n")
            return {}

        response_data = response.json()
        if self.debug:
            print(f"  Body: {json.dumps(response_data, indent=2, ensure_ascii=False)}\n")
        
        return response_data

    # ==================== Task List Management ====================

    def get_task_lists(self) -> List[Dict[str, Any]]:
        """
        Get all task lists

        Returns:
            List containing all task list information
        """
        result = self._make_request("/me/todo/lists")
        return result.get("value", [])

    def create_task_list(self, display_name: str) -> Dict[str, Any]:
        """
        Create a new task list

        Args:
            display_name: List display name

        Returns:
            Created task list information
        """
        data = {"displayName": display_name}
        return self._make_request("/me/todo/lists", method="POST", data=data)

    def delete_task_list(self, list_id: str) -> bool:
        """
        Delete task list

        Args:
            list_id: Task list ID

        Returns:
            True if deletion is successful
        """
        self._make_request(f"/me/todo/lists/{list_id}", method="DELETE")
        return True

    # ==================== Task Management ====================

    def get_tasks(self, list_id: str) -> List[Dict[str, Any]]:
        """
        Get all tasks in a specified list

        Args:
            list_id: Task list ID

        Returns:
            List containing all task information
        """
        result = self._make_request(f"/me/todo/lists/{list_id}/tasks")
        return result.get("value", [])

    def create_task(
        self,
        list_id: str,
        title: str,
        body: Optional[str] = None,
        due_date: Optional[str] = None,
        start_date: Optional[str] = None,
        reminder_date: Optional[str] = None,
        importance: str = "normal",
        categories: Optional[List[str]] = None,
        recurrence: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new task

        Args:
            list_id: Task list ID
            title: Task title
            body: Task content/notes (optional)
            due_date: Due date, format: 2026-02-10T09:00:00 (optional)
            start_date: Start date, format: 2026-02-10T09:00:00 (optional, required for recurrence)
            reminder_date: Reminder date, format: 2026-02-10T09:00:00 (optional)
            importance: Importance level, optional values: low, normal, high (default: normal)
            categories: List of category tags (optional)
            recurrence: Recurrence pattern (optional)

        Returns:
            Created task information
        """
        data = {"title": title, "importance": importance}

        if body:
            data["body"] = {"content": body, "contentType": "text"}

        if start_date:
            data["startDateTime"] = {"dateTime": start_date, "timeZone": "UTC"}

        if due_date:
            data["dueDateTime"] = {"dateTime": due_date, "timeZone": "UTC"}

        if reminder_date:
            data["reminderDateTime"] = {"dateTime": reminder_date, "timeZone": "UTC"}

        if categories:
            data["categories"] = categories

        if recurrence:
            data["recurrence"] = recurrence

        return self._make_request(f"/me/todo/lists/{list_id}/tasks", method="POST", data=data)

    def update_task(
        self,
        list_id: str,
        task_id: str,
        title: Optional[str] = None,
        body: Optional[str] = None,
        due_date: Optional[str] = None,
        reminder_date: Optional[str] = None,
        importance: Optional[str] = None,
        status: Optional[str] = None,
        categories: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Update a task

        Args:
            list_id: Task list ID
            task_id: Task ID
            title: Task title (optional)
            body: Task content/notes (optional)
            due_date: Due date (optional)
            reminder_date: Reminder date (optional)
            importance: Importance level: low, normal, high (optional)
            status: Status: notStarted, inProgress, completed (optional)
            categories: List of category tags (optional)

        Returns:
            Updated task information
        """
        data = {}

        if title is not None:
            data["title"] = title

        if body is not None:
            data["body"] = {"content": body, "contentType": "text"}

        if due_date is not None:
            data["dueDateTime"] = {"dateTime": due_date, "timeZone": "UTC"}

        if reminder_date is not None:
            data["reminderDateTime"] = {"dateTime": reminder_date, "timeZone": "UTC"}

        if importance is not None:
            data["importance"] = importance

        if status is not None:
            data["status"] = status

        if categories is not None:
            data["categories"] = categories

        return self._make_request(f"/me/todo/lists/{list_id}/tasks/{task_id}", method="PATCH", data=data)

    def complete_task(self, list_id: str, task_id: str) -> Dict[str, Any]:
        """
        Mark task as completed

        Args:
            list_id: Task list ID
            task_id: Task ID

        Returns:
            Updated task information
        """
        return self.update_task(list_id, task_id, status="completed")

    def delete_task(self, list_id: str, task_id: str) -> bool:
        """
        Delete a task

        Args:
            list_id: Task list ID
            task_id: Task ID

        Returns:
            True if deletion is successful
        """
        self._make_request(f"/me/todo/lists/{list_id}/tasks/{task_id}", method="DELETE")
        return True

    # ==================== Helper Methods ====================

    def get_all_tasks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all tasks from all lists"""
        all_tasks = {}

        lists = self.get_task_lists()
        for task_list in lists:
            list_name = task_list.get("displayName")
            list_id = task_list.get("id")

            tasks = self.get_tasks(list_id)
            all_tasks[list_name] = tasks

        return all_tasks

    def get_default_list(self) -> Optional[Dict[str, Any]]:
        """
        Get the default task list (wellknownListName: defaultList)

        Returns:
            Default list information, returns None if not found
        """
        lists = self.get_task_lists()
        for task_list in lists:
            if task_list.get("wellknownListName") == "defaultList":
                return task_list
        # Fallback: return first list if no default found
        return lists[0] if lists else None

    def find_list_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find task list by name

        Args:
            name: List name

        Returns:
            Found list information, returns None if not found
        """
        lists = self.get_task_lists()
        for task_list in lists:
            if task_list.get("displayName") == name:
                return task_list
        return None

    def find_task_by_title(self, list_id: str, title: str) -> Optional[Dict[str, Any]]:
        """
        Find task by title

        Args:
            list_id: Task list ID
            title: Task title

        Returns:
            Found task information, returns None if not found
        """
        tasks = self.get_tasks(list_id)
        for task in tasks:
            if task.get("title") == title:
                return task
        return None

# ==================== Command Line Interface ====================


def _parse_recurrence(recurrence_str: str, start_date: datetime) -> Optional[Dict[str, Any]]:
    """
    Parse recurrence string to Microsoft Graph API recurrence object
    
    Supported formats:
    - daily: Repeat every day
    - weekdays: Repeat on weekdays (Mon-Fri)
    - weekly: Repeat every week
    - monthly: Repeat every month
    - daily:N: Repeat every N days
    - weekly:N: Repeat every N weeks
    - monthly:N: Repeat every N months
    
    Args:
        recurrence_str: Recurrence string
        start_date: Start date for recurrence (required)
    
    Returns:
        Recurrence object for Graph API, or None if invalid format
    """
    if not recurrence_str:
        return None
    
    parts = recurrence_str.lower().split(":")
    pattern_type = parts[0]
    interval = int(parts[1]) if len(parts) > 1 else 1
    
    # Base recurrence structure
    recurrence = {
        "pattern": {
            "interval": interval
        },
        "range": {
            "type": "noEnd",
            "startDate": start_date.strftime("%Y-%m-%d")
        }
    }
    
    # Map pattern types
    if pattern_type == "daily":
        recurrence["pattern"]["type"] = "daily"
    elif pattern_type == "weekdays":
        recurrence["pattern"]["type"] = "weekly"
        recurrence["pattern"]["daysOfWeek"] = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        recurrence["pattern"]["interval"] = 1
        recurrence["pattern"]["firstDayOfWeek"] = "sunday"
    elif pattern_type == "weekly":
        recurrence["pattern"]["type"] = "weekly"
        recurrence["pattern"]["daysOfWeek"] = [start_date.strftime("%A").lower()]
        recurrence["pattern"]["firstDayOfWeek"] = "sunday"
    elif pattern_type == "monthly":
        recurrence["pattern"]["type"] = "absoluteMonthly"
        recurrence["pattern"]["dayOfMonth"] = start_date.day
    else:
        print(f"❌ Invalid recurrence pattern: {pattern_type}")
        print("   Supported: daily, weekdays, weekly, monthly")
        print("   With interval: daily:2, weekly:3, monthly:2")
        return None
    
    return recurrence


def _error_list_not_found(list_name: str):
    """Helper function to display list not found error"""
    print(f"❌ List not found: {list_name}")


def _error_task_not_found(task_name: str):
    """Helper function to display task not found error"""
    print(f"❌ Task not found: {task_name}")


def _get_list_or_error(client, list_name: str) -> Optional[Dict[str, Any]]:
    """Find list by name, display error if not found"""
    task_list = client.find_list_by_name(list_name)
    if not task_list:
        _error_list_not_found(list_name)
    return task_list


def _get_task_or_error(client, list_id: str, task_name: str) -> Optional[Dict[str, Any]]:
    """Find task by title, display error if not found"""
    task = client.find_task_by_title(list_id, task_name)
    if not task:
        _error_task_not_found(task_name)
    return task


def cmd_lists(args, client):
    """List all task lists"""
    lists = client.get_task_lists()

    if not lists:
        print("No task lists found")
        return

    print(f"\n📋 Task Lists ({len(lists)} total):\n")
    for i, lst in enumerate(lists, 1):
        print(f"{i}. {lst['displayName']}")
        if args.verbose:
            print(f"   ID: {lst['id']}")
            print(f"   Created: {lst.get('createdDateTime', 'N/A')}")


def cmd_tasks(args, client):
    """List tasks in a specified list"""
    task_list = _get_list_or_error(client, args.list)
    if not task_list:
        return

    tasks = client.get_tasks(task_list["id"])

    # Filter completed tasks
    if not args.all:
        tasks = [t for t in tasks if t.get("status") != "completed"]

    if not tasks:
        print(f'\n📋 No tasks in list "{args.list}"')
        return

    print(f'\n📋 Tasks in list "{args.list}" ({len(tasks)} total):\n')

    for i, task in enumerate(tasks, 1):
        title = task.get("title", "Untitled")
        status = "[Completed]" if task.get("status") == "completed" else "[In Progress]"
        priority = task.get("importance", "normal")
        priority_icon = "⭐" if priority == "high" else ""

        print(f"{i}. {status} {title} {priority_icon}")

        if args.verbose:
            if task.get("body", {}).get("content"):
                print(f"   Notes: {task['body']['content'][:100]}")
            if task.get("dueDateTime"):
                print(f"   Due: {task['dueDateTime']['dateTime']}")
            if task.get("categories"):
                print(f"   Categories: {', '.join(task['categories'])}")


def cmd_add(args, client):
    """Add a new task"""
    # Determine which list to use
    if args.list:
        # User specified a list
        task_list = client.find_list_by_name(args.list)
        if not task_list:
            # Auto-create list if it doesn't exist
            task_list = client.create_task_list(args.list)
            print(f"✓ List created: {args.list}")
    else:
        # No list specified, use default list
        task_list = client.get_default_list()
        if not task_list:
            print("❌ No task lists found. Please create a list first.")
            return

    # Calculate due date (Microsoft To Do API only supports date, not time)
    due_date = None
    if args.due:
        # Handle relative dates like "2d" (2 days) or plain number
        if args.due.endswith("d"):
            try:
                days = int(args.due[:-1])
                due_datetime = datetime.now() + timedelta(days=days)
            except ValueError:
                print(f"❌ Invalid format for due date days: {args.due}")
                return
        elif args.due.isdigit():
            # Plain number means days
            days = int(args.due)
            due_datetime = datetime.now() + timedelta(days=days)
        else:
            # Assume it's a date string (YYYY-MM-DD)
            try:
                due_datetime = datetime.fromisoformat(args.due)
            except ValueError:
                print(f"❌ Invalid date format for due date: {args.due}")
                print("   Use YYYY-MM-DD, or relative format like '2d' or just '3'.")
                return
        
        # Format as date-only (API requirement: time is ignored)
        due_date = due_datetime.strftime("%Y-%m-%d") + "T00:00:00"

    # Calculate reminder date/time (supports precise time)
    reminder_date = None
    if args.reminder:
        # Handle relative times like "2d" (2 days) or "3h" (3 hours)
        if args.reminder.endswith("h"):
            try:
                hours = int(args.reminder[:-1])
                reminder_datetime = datetime.now() + timedelta(hours=hours)
            except ValueError:
                print(f"❌ Invalid format for reminder hours: {args.reminder}")
                return
        elif args.reminder.endswith("d"):
            try:
                days = int(args.reminder[:-1])
                reminder_datetime = datetime.now() + timedelta(days=days)
            except ValueError:
                print(f"❌ Invalid format for reminder days: {args.reminder}")
                return
        else:
            # Try to parse as datetime string
            # Support formats: YYYY-MM-DD HH:MM, YYYY-MM-DDTHH:MM:SS, YYYY-MM-DD
            try:
                # First try ISO format
                reminder_datetime = datetime.fromisoformat(args.reminder)
            except ValueError:
                # Try space-separated date and time: "2026-03-15 14:30"
                try:
                    reminder_datetime = datetime.strptime(args.reminder, "%Y-%m-%d %H:%M")
                except ValueError:
                    # Try date only: "2026-03-15" (will default to 09:00)
                    try:
                        date_only = datetime.strptime(args.reminder, "%Y-%m-%d")
                        reminder_datetime = date_only.replace(hour=9, minute=0, second=0)
                    except ValueError:
                        print(f"❌ Invalid datetime format for reminder: {args.reminder}")
                        print("   Supported formats:")
                        print("   - Relative: '3h' (3 hours), '2d' (2 days)")
                        print("   - Date+Time: '2026-12-31 14:30' or '2026-12-31T14:30:00'")
                        print("   - Date only: '2026-12-31' (defaults to 09:00)")
                        return
        
        reminder_date = reminder_datetime.isoformat()

    # Parse recurrence pattern and prepare start date
    recurrence = None
    start_date = None
    
    if args.recurrence:
        # For recurring tasks, we need both start date and due date
        # Use due date if provided, otherwise default to 7 days from start
        if due_date:
            start_datetime = datetime.fromisoformat(due_date.replace("T00:00:00", ""))
        else:
            start_datetime = datetime.now()
            # Set default due date to 7 days from start for recurring tasks
            due_date = (start_datetime + timedelta(days=7)).strftime("%Y-%m-%dT00:00:00")
        
        recurrence = _parse_recurrence(args.recurrence, start_datetime)
        if recurrence is None:
            return  # Error already printed in _parse_recurrence
        
        # Set start date for recurring tasks (required)
        start_date = start_datetime.strftime("%Y-%m-%dT09:00:00")

    # Create task
    task = client.create_task(
        list_id=task_list["id"],
        title=args.title,
        body=args.description,
        start_date=start_date,
        due_date=due_date,
        reminder_date=reminder_date,
        importance=args.priority,
        categories=args.tags.split(",") if args.tags else None,
        recurrence=recurrence,
    )

    print(f"\n✓ Task added: {task['title']}")
    if recurrence:
        print("  🔄 Recurring task created")
    if args.verbose:
        print(f"  ID: {task['id']}")
        print(f"  Priority: {task['importance']}")
        if task.get("startDateTime"):
            print(f"  Start date: {task['startDateTime']['dateTime']}")
        if task.get("dueDateTime"):
            print(f"  Due date: {task['dueDateTime']['dateTime']}")
        if task.get("reminderDateTime"):
            print(f"  Reminder: {task['reminderDateTime']['dateTime']}")
        if task.get("recurrence"):
            pattern = task['recurrence']['pattern']
            print(f"  Recurrence: {pattern.get('type', 'unknown')} (interval: {pattern.get('interval', 1)})")


def cmd_complete(args, client):
    """Mark task as completed"""
    # Determine which list to use
    if args.list:
        task_list = _get_list_or_error(client, args.list)
    else:
        task_list = client.get_default_list()
    
    if not task_list:
        print("❌ No task lists found")
        return

    task = _get_task_or_error(client, task_list["id"], args.title)
    if not task:
        return

    client.complete_task(task_list["id"], task["id"])
    print(f"✓ Task completed: {args.title}")


def cmd_delete(args, client):
    """Delete a task"""
    # Determine which list to use
    if args.list:
        task_list = _get_list_or_error(client, args.list)
    else:
        task_list = client.get_default_list()
    
    if not task_list:
        print("❌ No task lists found")
        return

    task = _get_task_or_error(client, task_list["id"], args.title)
    if not task:
        return

    if not args.yes:
        confirm = input(f'Confirm delete task "{args.title}"? (y/n): ')
        if confirm.lower() != "y":
            print("Cancelled")
            return

    client.delete_task(task_list["id"], task["id"])
    print(f"✓ Task deleted: {args.title}")


def cmd_search(args, client):
    """Search for tasks"""
    all_tasks = client.get_all_tasks()
    keyword = args.keyword.lower()

    results = []
    for list_name, tasks in all_tasks.items():
        for task in tasks:
            title = task.get("title", "").lower()
            body = task.get("body", {}).get("content", "").lower()

            if keyword in title or keyword in body:
                results.append((list_name, task))

    if not results:
        print(f'\n🔍 No tasks found containing "{args.keyword}"')
        return

    print(f"\n🔍 Search results ({len(results)} found):\n")

    for list_name, task in results:
        status = "[Completed]" if task.get("status") == "completed" else "[In Progress]"
        priority = "⭐" if task.get("importance") == "high" else ""
        print(f"{status} {task['title']} {priority}")
        print(f"   List: {list_name}")
        if args.verbose and task.get("body", {}).get("content"):
            print(f"   Notes: {task['body']['content'][:100]}")


def cmd_today(args, client):
    """View tasks due today"""
    all_tasks = client.get_all_tasks()
    today = datetime.now().date()

    today_tasks = []
    for list_name, tasks in all_tasks.items():
        for task in tasks:
            if task.get("status") == "completed":
                continue

            due_date = task.get("dueDateTime", {}).get("dateTime")
            if due_date:
                task_date = datetime.fromisoformat(due_date.replace("Z", "+00:00")).date()
                if task_date == today:
                    today_tasks.append((list_name, task))

    if not today_tasks:
        print("\n📅 No tasks due today")
        return

    print(f"\n📅 Tasks due today ({len(today_tasks)} total):\n")

    for list_name, task in today_tasks:
        priority = "⭐" if task.get("importance") == "high" else ""
        print(f"[In Progress] {task['title']} {priority}")
        print(f"   List: {list_name}")


def cmd_overdue(args, client):
    """View overdue tasks"""
    all_tasks = client.get_all_tasks()
    now = datetime.now()

    overdue_tasks = []
    for list_name, tasks in all_tasks.items():
        for task in tasks:
            if task.get("status") == "completed":
                continue

            due_date = task.get("dueDateTime", {}).get("dateTime")
            if due_date:
                task_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                if task_date < now:
                    overdue_tasks.append((list_name, task, (now - task_date).days))

    if not overdue_tasks:
        print("\n✓ No overdue tasks")
        return

    # Sort by overdue days
    overdue_tasks.sort(key=lambda x: x[2], reverse=True)

    print(f"\n⚠️  Overdue tasks ({len(overdue_tasks)} total):\n")

    for list_name, task, days in overdue_tasks:
        priority = "⭐" if task.get("importance") == "high" else ""
        print(f"[In Progress] {task['title']} {priority}")
        print(f"   List: {list_name}")
        print(f"   Overdue: {days} days")


def cmd_pending(args, client):
    """Display incomplete tasks from all lists"""
    all_tasks = client.get_all_tasks()

    pending_tasks = []
    for list_name, tasks in all_tasks.items():
        for task in tasks:
            if task.get("status") != "completed":
                pending_tasks.append((list_name, task))

    if not pending_tasks:
        print("\n✓ No incomplete tasks")
        return

    # Group by list display
    if args.group:
        print(f"\n📋 All incomplete tasks ({len(pending_tasks)} total):\n")
        current_list = None
        for list_name, task in pending_tasks:
            if current_list != list_name:
                current_list = list_name
                print(f"\n📂 {list_name}:")

            priority = "⭐" if task.get("importance") == "high" else ""
            print(f"  [In Progress] {task['title']} {priority}")

            if args.verbose:
                if task.get("dueDateTime"):
                    due = task["dueDateTime"]["dateTime"].replace("T", " ")
                    print(f"      Due: {due}")
                if task.get("body", {}).get("content"):
                    print(f"      Notes: {task['body']['content'][:50]}...")
    else:
        # Flat display
        print(f"\n📋 All incomplete tasks ({len(pending_tasks)} total):\n")
        for list_name, task in pending_tasks:
            priority = "⭐" if task.get("importance") == "high" else ""
            print(f"[In Progress] {task['title']} {priority}")
            print(f"   List: {list_name}")
            if args.verbose and task.get("dueDateTime"):
                due = task["dueDateTime"]["dateTime"].replace("T", " ")
                print(f"   Due: {due}")


def cmd_stats(args, client):
    """Display statistics"""
    all_tasks = client.get_all_tasks()

    total_lists = len(all_tasks)
    total_tasks = 0
    completed = 0
    pending = 0
    high_priority = 0
    overdue_count = 0

    now = datetime.now()

    for tasks in all_tasks.values():
        for task in tasks:
            total_tasks += 1

            if task.get("status") == "completed":
                completed += 1
            else:
                pending += 1

                if task.get("importance") == "high":
                    high_priority += 1

                due_date = task.get("dueDateTime", {}).get("dateTime")
                if due_date:
                    task_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                    if task_date < now:
                        overdue_count += 1

    print("\n📊 Task Statistics:\n")
    print(f"  Total lists: {total_lists}")
    print(f"  Total tasks: {total_tasks}")
    print(f"  Completed: {completed}")
    print(f"  Pending: {pending}")
    print(f"  High priority: {high_priority}")
    print(f"  Overdue: {overdue_count}")

    if total_tasks > 0:
        completion_rate = (completed / total_tasks) * 100
        print(f"\n  Completion rate: {completion_rate:.1f}%")


def cmd_export(args, client):
    """Export tasks"""
    all_tasks = client.get_all_tasks()

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_tasks, f, ensure_ascii=False, indent=2)

    print(f"✓ Tasks exported to: {args.output}")


def cmd_create_list(args, client):
    """Create a new list"""
    task_list = client.create_task_list(args.name)
    print(f"✓ List created: {task_list['displayName']}")
    if args.verbose:
        print(f"  ID: {task_list['id']}")


def cmd_delete_list(args, client):
    """Delete a list"""
    task_list = _get_list_or_error(client, args.name)
    if not task_list:
        return

    if not args.yes:
        confirm = input(f'Confirm delete list "{args.name}" and all its tasks? (y/n): ')
        if confirm.lower() != "y":
            print("Cancelled")
            return

    client.delete_task_list(task_list["id"])
    print(f"✓ List deleted: {args.name}")


def cmd_detail(args, client):
    """View task details"""
    # Determine which list to use
    if args.list:
        task_list = _get_list_or_error(client, args.list)
    else:
        task_list = client.get_default_list()
    
    if not task_list:
        print("❌ No task lists found")
        return

    tasks = client.get_tasks(task_list["id"])
    matched = [t for t in tasks if args.title.lower() in t.get("title", "").lower()]

    if not matched:
        _error_task_not_found(args.title)
        return

    # Select task (prefer incomplete tasks, use latest modified)
    if len(matched) > 1:
        pending = [t for t in matched if t.get("status") != "completed"]
        if pending:
            pending.sort(key=lambda x: x.get("lastModifiedDateTime", ""), reverse=True)
            task = pending[0]
            print(f"ℹ️  Found {len(matched)} matching tasks ({len(pending)} incomplete), showing latest incomplete")
        else:
            matched.sort(key=lambda x: x.get("lastModifiedDateTime", ""), reverse=True)
            task = matched[0]
            print(f"ℹ️  Found {len(matched)} matching tasks (all completed), showing latest completed")
    else:
        task = matched[0]

    # Display task details
    print("\n" + "=" * 60)
    print("📌 Task Details")
    print("=" * 60 + "\n")

    # Basic info
    print(f"📋 Title: {task.get('title', 'Untitled')}")
    status = "[Completed]" if task.get("status") == "completed" else "[In Progress]"
    print(f"🔖 Status: {status}")

    # Priority
    importance = task.get("importance", "normal")
    importance_map = {"high": "⭐ High", "normal": "Normal", "low": "Low"}
    print(f"⚡ Priority: {importance_map.get(importance, importance)}")

    # Dates
    if task.get("createdDateTime"):
        created = task["createdDateTime"].replace("T", " ").replace("Z", "")
        print(f"📅 Created: {created}")

    if task.get("lastModifiedDateTime"):
        modified = task["lastModifiedDateTime"].replace("T", " ").replace("Z", "")
        print(f"📝 Modified: {modified}")

    if task.get("dueDateTime"):
        due = task["dueDateTime"]["dateTime"].replace("T", " ")
        print(f"⏰ Due: {due}")

    if task.get("reminderDateTime"):
        reminder = task["reminderDateTime"]["dateTime"].replace("T", " ")
        print(f"🔔 Reminder: {reminder}")

    if task.get("completedDateTime"):
        completed = task["completedDateTime"]["dateTime"].replace("T", " ")
        print(f"✅ Completed: {completed}")

    # Notes
    if task.get("body", {}).get("content"):
        print(f"\n📝 Notes:\n{task['body']['content']}")

    # Categories
    if task.get("categories"):
        print(f"\n🏷️  Categories: {', '.join(task['categories'])}")

    # Recurrence info
    if task.get("recurrence"):
        pattern = task["recurrence"]["pattern"]
        pattern_type = pattern.get("type", "unknown")
        interval = pattern.get("interval", 1)
        
        print(f"\n🔄 Recurrence:")
        if pattern_type == "daily":
            if interval == 1:
                print("   Every day")
            else:
                print(f"   Every {interval} days")
        elif pattern_type == "weekly":
            days = pattern.get("daysOfWeek", [])
            if interval == 1:
                print(f"   Every week on {', '.join(days).title()}")
            else:
                print(f"   Every {interval} weeks on {', '.join(days).title()}")
        elif pattern_type == "absoluteMonthly":
            day = pattern.get("dayOfMonth", 1)
            if interval == 1:
                print(f"   Every month on day {day}")
            else:
                print(f"   Every {interval} months on day {day}")
        
        rec_range = task["recurrence"].get("range", {})
        range_type = rec_range.get("type")
        if range_type == "noEnd":
            print(f"   Start date: {rec_range.get('startDate', 'N/A')}")
            print("   No end date")
        elif range_type == "endDate":
            print(f"   Start: {rec_range.get('startDate', 'N/A')}")
            print(f"   End: {rec_range.get('endDate', 'N/A')}")

    # Technical info
    if args.verbose:
        print("\n" + "─" * 60)
        print("🔧 Technical Info")
        print("─" * 60)
        print(f"ID: {task.get('id', 'N/A')}")
        print(f"List ID: {task_list['id']}")
        if task.get("isReminderOn"):
            print(f"Reminder: {'On' if task['isReminderOn'] else 'Off'}")

    print("\n" + "=" * 60 + "\n")


def cmd_logout(args, client):
    """Logout and clear cached tokens"""
    client.logout()


def cmd_login_get(args, client):
    """Get authentication info (verification code and login link)"""
    client.get_device_code_flow()


def cmd_login_verify(args, client):
    """Verify device code and complete login"""
    if client.verify_device_code_flow():
        print("✓ You can now start using ms-todo-sync.py")
    else:
        sys.exit(1)


def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        prog="ms-todo-sync.py",
        description="Microsoft To Do command line tool",
        epilog='Example: ms-todo-sync.py add "Complete report" -l work -p high -d 3',
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed information")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (show API requests and responses)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List management
    subparsers.add_parser("lists", help="List all task lists")
    
    tasks_parser = subparsers.add_parser("tasks", help="List tasks in a list")
    tasks_parser.add_argument("list", help="List name")
    tasks_parser.add_argument("-a", "--all", action="store_true", help="Include completed tasks")

    # Task operations
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument("-l", "--list", help="List name (if not specified, uses your default list)")
    add_parser.add_argument("-d", "--due", help="Due date (e.g., '3' or '2d' for 2 days, '2026-12-31' for specific date). Note: Time is not supported for due dates.")
    add_parser.add_argument("-r", "--reminder",
                           help="Reminder time. Formats: '3h' (hours), '2d' (days), "
                                "'2026-12-31 14:30' (date+time), '2026-12-31T14:30:00' (ISO), "
                                "'2026-12-31' (date only, defaults to 09:00)")
    add_parser.add_argument("-R", "--recurrence",
                           help="Recurrence pattern. Formats: 'daily', 'weekdays', 'weekly', "
                                "'monthly', or with interval like 'daily:2' (every 2 days), "
                                "'weekly:3' (every 3 weeks)")
    add_parser.add_argument("-p", "--priority", choices=["low", "normal", "high"], default="normal", help="Priority")
    add_parser.add_argument("-D", "--description", help="Task description")
    add_parser.add_argument("-t", "--tags", help="Tags (comma separated)")
    add_parser.add_argument("--create-list", action="store_true", help="Create list if not exists")

    complete_parser = subparsers.add_parser("complete", help="Mark task as completed")
    complete_parser.add_argument("title", help="Task title")
    complete_parser.add_argument("-l", "--list", help="List name (if not specified, uses your default list)")

    delete_parser = subparsers.add_parser("delete", help="Delete task")
    delete_parser.add_argument("title", help="Task title")
    delete_parser.add_argument("-l", "--list", help="List name (if not specified, uses your default list)")
    delete_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")

    detail_parser = subparsers.add_parser("detail", help="View task details")
    detail_parser.add_argument("title", help="Task title (supports partial match)")
    detail_parser.add_argument("-l", "--list", help="List name (if not specified, uses your default list)")

    search_parser = subparsers.add_parser("search", help="Search for tasks")
    search_parser.add_argument("keyword", help="Search keyword")

    # Task views
    subparsers.add_parser("today", help="View tasks due today")
    subparsers.add_parser("overdue", help="View overdue tasks")
    
    pending_parser = subparsers.add_parser("pending", help="Show all incomplete tasks")
    pending_parser.add_argument("-g", "--group", action="store_true", help="Group by list")

    subparsers.add_parser("stats", help="Show statistics")

    # Data management
    export_parser = subparsers.add_parser("export", help="Export tasks to JSON file")
    export_parser.add_argument("-o", "--output", default="todo_export.json", help="Output file name")

    # List management (advanced)
    create_list_parser = subparsers.add_parser("create-list", help="Create a new list")
    create_list_parser.add_argument("name", help="List name")

    delete_list_parser = subparsers.add_parser("delete-list", help="Delete list")
    delete_list_parser.add_argument("name", help="List name")
    delete_list_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")

    # Authentication
    login_parser = subparsers.add_parser("login", help="Authentication management")
    login_subparsers = login_parser.add_subparsers(dest="login_action", help="Login operation")
    login_subparsers.add_parser("get", help="Get authentication info (verification code and login link)")
    login_subparsers.add_parser("verify", help="Verify authentication code and complete login")

    subparsers.add_parser("logout", help="Logout and clear cache")

    return parser


def main():
    """Main function"""
    parser = create_parser()
    args = parser.parse_args()

    # If no command provided, show help
    if not args.command:
        parser.print_help()
        return

    # Create client
    client = MicrosoftTodoClient(debug=args.debug)

    # Logout and login commands don't need authentication
    if args.command == "logout":
        cmd_logout(args, client)
        return

    if args.command == "login":
        if not args.login_action:
            print("Please specify login operation: get (get auth info) or verify (verify auth)")
            sys.exit(1)

        try:
            if args.login_action == "get":
                cmd_login_get(args, client)
            elif args.login_action == "verify":
                cmd_login_verify(args, client)
        except Exception as e:
            print(f"❌ Error: {e}")
            if args.verbose:
                import traceback

                traceback.print_exc()
            sys.exit(1)
        return

    # Other commands need authentication
    if not client.authenticate():
        print("\n❌ Not logged in")
        print("\nPlease use the following commands to login:")
        print("  Step 1: Get authentication info")
        print("    ms-todo-sync.py login get")
        print("\n  Step 2: Verify authentication code (login)")
        print("    ms-todo-sync.py login verify")
        sys.exit(1)

    # Execute command
    commands = {
        "lists": cmd_lists,
        "tasks": cmd_tasks,
        "add": cmd_add,
        "complete": cmd_complete,
        "delete": cmd_delete,
        "detail": cmd_detail,
        "search": cmd_search,
        "today": cmd_today,
        "overdue": cmd_overdue,
        "pending": cmd_pending,
        "stats": cmd_stats,
        "export": cmd_export,
        "create-list": cmd_create_list,
        "delete-list": cmd_delete_list,
    }

    if args.command in commands:
        try:
            commands[args.command](args, client)
        except Exception as e:
            print(f"❌ Error: {e}")
            if args.verbose:
                import traceback

                traceback.print_exc()
            sys.exit(1)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
