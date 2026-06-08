#!/usr/bin/env python3
"""
TimeDoctor CLI Tool for OpenClaw
Complete command-line interface to TimeDoctor API
Author: JehadurRE (Jehadur Rahman Emran)
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import httpx

BASE_URL = "https://api2.timedoctor.com"


class TimeDoctorClient:
    """Simple TimeDoctor API client."""
    
    def __init__(self, token: str, company_id: Optional[str] = None):
        self.token = token
        self.company_id = company_id
        self.headers = {
            "Authorization": f"JWT {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    
    def get(self, path: str, params: dict = None) -> dict:
        """Make GET request."""
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{BASE_URL}{path}",
                headers=self.headers,
                params=params or {}
            )
            response.raise_for_status()
            return response.json()


# Authentication & Authorization
def login(email: str, password: str) -> dict:
    """Login with email/password to get JWT token."""
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            f"{BASE_URL}/api/1.0/login",
            headers={"Content-Type": "application/json"},
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        return response.json()


def get_authorization(client: TimeDoctorClient) -> dict:
    """Get authorization info and available companies."""
    return client.get("/api/1.0/authorization")


def get_companies(client: TimeDoctorClient) -> dict:
    """List all companies."""
    return client.get("/api/1.0/companies")


def get_company(client: TimeDoctorClient, company_id: str) -> dict:
    """Get specific company details."""
    return client.get(f"/api/1.0/companies/{company_id}")


# User Management
def get_users(client: TimeDoctorClient, company_id: str, page: int = 1, 
              limit: int = 100, deleted: bool = False, show_hidden: bool = False) -> dict:
    """List users in a company."""
    params = {
        "company": company_id,
        "page": page,
        "limit": limit,
        "deleted": str(deleted).lower(),
        "show-hidden": str(show_hidden).lower(),
    }
    return client.get("/api/1.1/users", params=params)


def get_user(client: TimeDoctorClient, company_id: str, user_id: str) -> dict:
    """Get specific user details."""
    params = {"company": company_id}
    return client.get(f"/api/1.1/users/{user_id}", params=params)


def get_managed_users(client: TimeDoctorClient, company_id: str, user_id: str) -> dict:
    """Get users managed by a manager."""
    params = {"company": company_id}
    return client.get(f"/api/1.0/users/{user_id}/managed", params=params)


# Activity & Worklog
def get_activity_worklog(client: TimeDoctorClient, company_id: str, from_date: str,
                         to_date: str, user_ids: str = None, task_ids: str = None,
                         project_ids: str = None, sort: str = "date", 
                         page: int = 1, limit: int = 100) -> dict:
    """Get detailed work activity log."""
    params = {
        "company": company_id,
        "from": from_date,
        "to": to_date,
        "sort": sort,
        "page": page,
        "limit": limit,
    }
    if user_ids:
        params["user"] = user_ids
    if task_ids:
        params["task"] = task_ids
    if project_ids:
        params["project"] = project_ids
    return client.get("/api/1.0/activity/worklog", params=params)


def get_activity_timeuse_stats(client: TimeDoctorClient, company_id: str,
                                from_date: str, to_date: str, user_ids: str = None) -> dict:
    """Get time usage statistics."""
    params = {
        "company": company_id,
        "from": from_date,
        "to": to_date,
    }
    if user_ids:
        params["user"] = user_ids
    return client.get("/api/1.0/activity/timeuse/stats", params=params)


def get_disconnectivity(client: TimeDoctorClient, company_id: str, from_date: str,
                        to_date: str, user_ids: str = None) -> dict:
    """Get disconnectivity periods."""
    params = {
        "company": company_id,
        "from": from_date,
        "to": to_date,
    }
    if user_ids:
        params["user"] = user_ids
    return client.get("/api/1.0/activity/disconnectivity", params=params)


# Statistics
def get_stats_total(client: TimeDoctorClient, company_id: str, from_date: str,
                    to_date: str, user_ids: str = None, group_ids: str = None,
                    project_ids: str = None, task_ids: str = None, sort: str = "total",
                    page: int = 1, limit: int = 100) -> dict:
    """Get aggregated total statistics."""
    params = {
        "company": company_id,
        "from": from_date,
        "to": to_date,
        "sort": sort,
        "page": page,
        "limit": limit,
    }
    if user_ids:
        params["user"] = user_ids
    if group_ids:
        params["tag"] = group_ids
    if project_ids:
        params["project"] = project_ids
    if task_ids:
        params["task"] = task_ids
    return client.get("/api/1.1/stats/total", params=params)


def get_stats_category(client: TimeDoctorClient, company_id: str, from_date: str,
                       to_date: str, user_ids: str = None, category_score: int = None) -> dict:
    """Get statistics by productivity category."""
    params = {
        "company": company_id,
        "from": from_date,
        "to": to_date,
    }
    if user_ids:
        params["user"] = user_ids
    if category_score is not None:
        params["category-score"] = category_score
    return client.get("/api/1.1/stats/category", params=params)


def get_stats_summary(client: TimeDoctorClient, company_id: str, from_date: str,
                      to_date: str, user_ids: str = None, resolution: str = "day") -> dict:
    """Get summary statistics over time."""
    params = {
        "company": company_id,
        "from": from_date,
        "to": to_date,
        "resolution": resolution,
    }
    if user_ids:
        params["user"] = user_ids
    return client.get("/api/1.1/stats/summary", params=params)


def get_stats_work_life(client: TimeDoctorClient, company_id: str, from_date: str,
                        to_date: str, user_ids: str = None) -> dict:
    """Get work-life balance statistics."""
    params = {
        "company": company_id,
        "from": from_date,
        "to": to_date,
    }
    if user_ids:
        params["user"] = user_ids
    return client.get("/api/1.1/stats/work-life", params=params)


def get_stats_shift(client: TimeDoctorClient, company_id: str, from_date: str,
                    to_date: str, user_ids: str = None) -> dict:
    """Get shift-related statistics."""
    params = {
        "company": company_id,
        "from": from_date,
        "to": to_date,
    }
    if user_ids:
        params["user"] = user_ids
    return client.get("/api/1.1/stats/shift", params=params)


def get_stats_outliers(client: TimeDoctorClient, company_id: str, from_date: str,
                       to_date: str, user_ids: str = None) -> dict:
    """Get outlier statistics."""
    params = {
        "company": company_id,
        "from": from_date,
        "to": to_date,
    }
    if user_ids:
        params["user"] = user_ids
    return client.get("/api/1.1/stats/outliers", params=params)


# Timesheet Stats
def get_timesheet_total(client: TimeDoctorClient, company_id: str, from_date: str,
                        to_date: str, user_ids: str = None) -> dict:
    """Get timesheet total statistics."""
    params = {
        "company": company_id,
        "from": from_date,
        "to": to_date,
    }
    if user_ids:
        params["user"] = user_ids
    return client.get("/api/1.1/stats/timesheet/total", params=params)


def get_timesheet_summary(client: TimeDoctorClient, company_id: str, from_date: str,
                          to_date: str, user_ids: str = None, resolution: str = "day") -> dict:
    """Get timesheet summary statistics."""
    params = {
        "company": company_id,
        "from": from_date,
        "to": to_date,
        "resolution": resolution,
    }
    if user_ids:
        params["user"] = user_ids
    return client.get("/api/1.1/stats/timesheet/summary", params=params)


# Projects & Tasks
def get_projects(client: TimeDoctorClient, company_id: str, page: int = 1,
                 limit: int = 100, deleted: bool = False) -> dict:
    """List projects."""
    params = {
        "company": company_id,
        "page": page,
        "limit": limit,
        "deleted": str(deleted).lower(),
    }
    return client.get("/api/1.1/projects", params=params)


def get_project(client: TimeDoctorClient, company_id: str, project_id: str) -> dict:
    """Get specific project details."""
    params = {"company": company_id}
    return client.get(f"/api/1.0/projects/{project_id}", params=params)


def get_tasks(client: TimeDoctorClient, company_id: str, project_id: str = None,
              user_id: str = None, status: str = None, page: int = 1, limit: int = 100) -> dict:
    """List tasks."""
    params = {
        "company": company_id,
        "page": page,
        "limit": limit,
    }
    if project_id:
        params["project"] = project_id
    if user_id:
        params["user"] = user_id
    if status:
        params["status"] = status
    return client.get("/api/1.1/tasks", params=params)


def get_task(client: TimeDoctorClient, company_id: str, task_id: str) -> dict:
    """Get specific task details."""
    params = {"company": company_id}
    return client.get(f"/api/1.0/tasks/{task_id}", params=params)


# Groups (Tags)
def get_groups(client: TimeDoctorClient, company_id: str) -> dict:
    """Get all groups/tags."""
    params = {"company": company_id}
    return client.get("/api/1.0/tags", params=params)


def get_group(client: TimeDoctorClient, company_id: str, group_id: str) -> dict:
    """Get specific group details."""
    params = {"company": company_id}
    return client.get(f"/api/1.0/tags/{group_id}", params=params)


# Work Schedules
def get_work_schedules(client: TimeDoctorClient, company_id: str) -> dict:
    """Get all work schedules."""
    params = {"company": company_id}
    return client.get("/api/1.0/work-schedules", params=params)


def get_work_schedule(client: TimeDoctorClient, company_id: str, schedule_id: str) -> dict:
    """Get specific work schedule details."""
    params = {"company": company_id}
    return client.get(f"/api/1.0/work-schedules/{schedule_id}", params=params)


def get_work_schedule_issues(client: TimeDoctorClient, company_id: str, from_date: str,
                              to_date: str, user_ids: str = None) -> dict:
    """Get work schedule issues."""
    params = {
        "company": company_id,
        "from": from_date,
        "to": to_date,
    }
    if user_ids:
        params["user"] = user_ids
    return client.get("/api/1.0/work-schedules/issues", params=params)


def get_leave_stats(client: TimeDoctorClient, company_id: str, from_date: str,
                    to_date: str, user_ids: str = None) -> dict:
    """Get leave/time-off statistics."""
    params = {
        "company": company_id,
        "from": from_date,
        "to": to_date,
    }
    if user_ids:
        params["user"] = user_ids
    return client.get("/api/1.0/work-schedules/stats", params=params)


# Payroll
def get_users_payroll(client: TimeDoctorClient, company_id: str, user_ids: str = None) -> dict:
    """Get payroll information for users."""
    params = {"company": company_id}
    if user_ids:
        params["user"] = user_ids
    return client.get("/api/1.0/users/payroll", params=params)


def get_company_payroll_settings(client: TimeDoctorClient, company_id: str) -> dict:
    """Get company-wide payroll settings."""
    params = {"company": company_id}
    return client.get("/api/1.0/companies/payroll", params=params)


# Files (Screenshots)
def get_files(client: TimeDoctorClient, company_id: str, from_date: str, to_date: str,
              user_ids: str = None, file_type: str = "screenshot", 
              page: int = 1, limit: int = 100) -> dict:
    """Get screenshot/screencast files."""
    params = {
        "company": company_id,
        "from": from_date,
        "to": to_date,
        "type": file_type,
        "page": page,
        "limit": limit,
    }
    if user_ids:
        params["user"] = user_ids
    return client.get("/api/1.0/files", params=params)


# Categories (Productivity Ratings)
def get_categories(client: TimeDoctorClient, company_id: str) -> dict:
    """Get productivity categories."""
    params = {"company": company_id}
    return client.get("/api/1.0/categories", params=params)


def get_unrated_categories_count(client: TimeDoctorClient, company_id: str) -> dict:
    """Get count of unrated apps/websites."""
    params = {"company": company_id}
    return client.get("/api/1.0/categories/unrated-count", params=params)


# Convenience Functions
def get_today_worklog(client: TimeDoctorClient, company_id: str, user_ids: str = None) -> dict:
    """Get today's worklog."""
    today = datetime.now(timezone.utc).date()
    from_date = f"{today}T00:00:00Z"
    to_date = f"{today + timedelta(days=1)}T00:00:00Z"
    return get_activity_worklog(client, company_id, from_date, to_date, user_ids)


def get_this_week_stats(client: TimeDoctorClient, company_id: str, user_ids: str = None) -> dict:
    """Get this week's stats (Monday to today)."""
    today = datetime.now(timezone.utc).date()
    monday = today - timedelta(days=today.weekday())
    from_date = f"{monday}T00:00:00Z"
    to_date = f"{today + timedelta(days=1)}T00:00:00Z"
    return get_stats_total(client, company_id, from_date, to_date, user_ids)


def get_this_month_stats(client: TimeDoctorClient, company_id: str, user_ids: str = None) -> dict:
    """Get this month's stats."""
    today = datetime.now(timezone.utc).date()
    first_of_month = today.replace(day=1)
    from_date = f"{first_of_month}T00:00:00Z"
    to_date = f"{today + timedelta(days=1)}T00:00:00Z"
    return get_stats_total(client, company_id, from_date, to_date, user_ids)


def main():
    parser = argparse.ArgumentParser(description="TimeDoctor CLI Tool")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("--email", help="Email for login")
    parser.add_argument("--password", help="Password for login")
    parser.add_argument("--company-id", help="Company ID")
    parser.add_argument("--user-ids", help="Comma-separated user IDs")
    parser.add_argument("--user-id", help="Single user ID")
    parser.add_argument("--from-date", help="From date (ISO 8601)")
    parser.add_argument("--to-date", help="To date (ISO 8601)")
    parser.add_argument("--project-id", help="Project ID")
    parser.add_argument("--task-id", help="Task ID")
    parser.add_argument("--group-id", help="Group/Tag ID")
    parser.add_argument("--schedule-id", help="Schedule ID")
    parser.add_argument("--category-score", type=int, help="Category score (0,2,3,4)")
    parser.add_argument("--resolution", default="day", help="Time resolution")
    parser.add_argument("--file-type", default="screenshot", help="File type")
    parser.add_argument("--status", help="Task status")
    parser.add_argument("--sort", default="date", help="Sort field")
    parser.add_argument("--page", type=int, default=1, help="Page number")
    parser.add_argument("--limit", type=int, default=100, help="Result limit")
    parser.add_argument("--deleted", action="store_true", help="Include deleted")
    parser.add_argument("--show-hidden", action="store_true", help="Show hidden users")
    
    args = parser.parse_args()
    
    # Execute command
    try:
        cmd = args.command
        
        # Login command (doesn't need token)
        if cmd == "login":
            if not args.email or not args.password:
                raise ValueError("email and password required for login")
            result = login(args.email, args.password)
            print(json.dumps(result, indent=2))
            sys.exit(0)
        
        # All other commands need token
        token = os.environ.get("TIMEDOCTOR_TOKEN")
        if not token:
            print(json.dumps({"error": "TIMEDOCTOR_TOKEN environment variable not set. Use 'login' command first or set the token manually."}))
            sys.exit(1)
        
        company_id = args.company_id or os.environ.get("TIMEDOCTOR_COMPANY_ID")
        client = TimeDoctorClient(token, company_id)
        
        # Authentication & Authorization
        if cmd == "get_authorization":
            result = get_authorization(client)
        elif cmd == "get_companies":
            result = get_companies(client)
        elif cmd == "get_company":
            if not company_id:
                raise ValueError("company_id required")
            result = get_company(client, company_id)
        
        # User Management
        elif cmd == "get_users":
            if not company_id:
                raise ValueError("company_id required")
            result = get_users(client, company_id, args.page, args.limit, args.deleted, args.show_hidden)
        elif cmd == "get_user":
            if not company_id or not args.user_id:
                raise ValueError("company_id and user_id required")
            result = get_user(client, company_id, args.user_id)
        elif cmd == "get_managed_users":
            if not company_id or not args.user_id:
                raise ValueError("company_id and user_id required")
            result = get_managed_users(client, company_id, args.user_id)
        
        # Activity & Worklog
        elif cmd == "get_activity_worklog":
            if not company_id or not args.from_date or not args.to_date:
                raise ValueError("company_id, from_date, and to_date required")
            result = get_activity_worklog(client, company_id, args.from_date, args.to_date,
                                         args.user_ids, None, args.project_id, args.sort, args.page, args.limit)
        elif cmd == "get_activity_timeuse_stats":
            if not company_id or not args.from_date or not args.to_date:
                raise ValueError("company_id, from_date, and to_date required")
            result = get_activity_timeuse_stats(client, company_id, args.from_date, args.to_date, args.user_ids)
        elif cmd == "get_disconnectivity":
            if not company_id or not args.from_date or not args.to_date:
                raise ValueError("company_id, from_date, and to_date required")
            result = get_disconnectivity(client, company_id, args.from_date, args.to_date, args.user_ids)
        elif cmd == "get_today_worklog":
            if not company_id:
                raise ValueError("company_id required")
            result = get_today_worklog(client, company_id, args.user_ids)
        
        # Statistics
        elif cmd == "get_stats_total":
            if not company_id or not args.from_date or not args.to_date:
                raise ValueError("company_id, from_date, and to_date required")
            result = get_stats_total(client, company_id, args.from_date, args.to_date,
                                    args.user_ids, args.group_id, args.project_id, args.task_id,
                                    args.sort, args.page, args.limit)
        elif cmd == "get_stats_category":
            if not company_id or not args.from_date or not args.to_date:
                raise ValueError("company_id, from_date, and to_date required")
            result = get_stats_category(client, company_id, args.from_date, args.to_date,
                                       args.user_ids, args.category_score)
        elif cmd == "get_stats_summary":
            if not company_id or not args.from_date or not args.to_date:
                raise ValueError("company_id, from_date, and to_date required")
            result = get_stats_summary(client, company_id, args.from_date, args.to_date,
                                      args.user_ids, args.resolution)
        elif cmd == "get_stats_work_life":
            if not company_id or not args.from_date or not args.to_date:
                raise ValueError("company_id, from_date, and to_date required")
            result = get_stats_work_life(client, company_id, args.from_date, args.to_date, args.user_ids)
        elif cmd == "get_stats_shift":
            if not company_id or not args.from_date or not args.to_date:
                raise ValueError("company_id, from_date, and to_date required")
            result = get_stats_shift(client, company_id, args.from_date, args.to_date, args.user_ids)
        elif cmd == "get_stats_outliers":
            if not company_id or not args.from_date or not args.to_date:
                raise ValueError("company_id, from_date, and to_date required")
            result = get_stats_outliers(client, company_id, args.from_date, args.to_date, args.user_ids)
        elif cmd == "get_this_week_stats":
            if not company_id:
                raise ValueError("company_id required")
            result = get_this_week_stats(client, company_id, args.user_ids)
        elif cmd == "get_this_month_stats":
            if not company_id:
                raise ValueError("company_id required")
            result = get_this_month_stats(client, company_id, args.user_ids)
        
        # Timesheet Stats
        elif cmd == "get_timesheet_total":
            if not company_id or not args.from_date or not args.to_date:
                raise ValueError("company_id, from_date, and to_date required")
            result = get_timesheet_total(client, company_id, args.from_date, args.to_date, args.user_ids)
        elif cmd == "get_timesheet_summary":
            if not company_id or not args.from_date or not args.to_date:
                raise ValueError("company_id, from_date, and to_date required")
            result = get_timesheet_summary(client, company_id, args.from_date, args.to_date,
                                          args.user_ids, args.resolution)
        
        # Projects & Tasks
        elif cmd == "get_projects":
            if not company_id:
                raise ValueError("company_id required")
            result = get_projects(client, company_id, args.page, args.limit, args.deleted)
        elif cmd == "get_project":
            if not company_id or not args.project_id:
                raise ValueError("company_id and project_id required")
            result = get_project(client, company_id, args.project_id)
        elif cmd == "get_tasks":
            if not company_id:
                raise ValueError("company_id required")
            result = get_tasks(client, company_id, args.project_id, args.user_id,
                              args.status, args.page, args.limit)
        elif cmd == "get_task":
            if not company_id or not args.task_id:
                raise ValueError("company_id and task_id required")
            result = get_task(client, company_id, args.task_id)
        
        # Groups
        elif cmd == "get_groups":
            if not company_id:
                raise ValueError("company_id required")
            result = get_groups(client, company_id)
        elif cmd == "get_group":
            if not company_id or not args.group_id:
                raise ValueError("company_id and group_id required")
            result = get_group(client, company_id, args.group_id)
        
        # Work Schedules
        elif cmd == "get_work_schedules":
            if not company_id:
                raise ValueError("company_id required")
            result = get_work_schedules(client, company_id)
        elif cmd == "get_work_schedule":
            if not company_id or not args.schedule_id:
                raise ValueError("company_id and schedule_id required")
            result = get_work_schedule(client, company_id, args.schedule_id)
        elif cmd == "get_work_schedule_issues":
            if not company_id or not args.from_date or not args.to_date:
                raise ValueError("company_id, from_date, and to_date required")
            result = get_work_schedule_issues(client, company_id, args.from_date, args.to_date, args.user_ids)
        elif cmd == "get_leave_stats":
            if not company_id or not args.from_date or not args.to_date:
                raise ValueError("company_id, from_date, and to_date required")
            result = get_leave_stats(client, company_id, args.from_date, args.to_date, args.user_ids)
        
        # Payroll
        elif cmd == "get_users_payroll":
            if not company_id:
                raise ValueError("company_id required")
            result = get_users_payroll(client, company_id, args.user_ids)
        elif cmd == "get_company_payroll_settings":
            if not company_id:
                raise ValueError("company_id required")
            result = get_company_payroll_settings(client, company_id)
        
        # Files
        elif cmd == "get_files":
            if not company_id or not args.from_date or not args.to_date:
                raise ValueError("company_id, from_date, and to_date required")
            result = get_files(client, company_id, args.from_date, args.to_date,
                              args.user_ids, args.file_type, args.page, args.limit)
        
        # Categories
        elif cmd == "get_categories":
            if not company_id:
                raise ValueError("company_id required")
            result = get_categories(client, company_id)
        elif cmd == "get_unrated_categories_count":
            if not company_id:
                raise ValueError("company_id required")
            result = get_unrated_categories_count(client, company_id)
        
        else:
            print(json.dumps({"error": f"Unknown command: {cmd}"}))
            sys.exit(1)
        
        # Output result as JSON
        print(json.dumps(result, indent=2))
    
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
