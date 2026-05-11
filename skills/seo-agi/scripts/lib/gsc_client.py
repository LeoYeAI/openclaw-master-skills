"""
Google Search Console API client for SEO-AGI.
Pulls query performance data, cannibalization detection, and indexing status.
"""

import json
from typing import Optional
from pathlib import Path


class GSCClient:
    """Client for Google Search Console API."""

    def __init__(self, credentials_path: str = None, oauth_creds: dict = None):
        """
        Initialize GSC client.

        Args:
            credentials_path: Path to service account JSON file
            oauth_creds: Dict with client_id, client_secret, refresh_token
        """
        self.credentials_path = credentials_path
        self.oauth_creds = oauth_creds
        self._service = None

    def _get_service(self):
        """Lazy-initialize the GSC API service."""
        if self._service is not None:
            return self._service

        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError:
            raise RuntimeError(
                "GSC requires google-auth and google-api-python-client. "
                "Install with: pip install google-auth google-api-python-client"
            )

        if self.credentials_path:
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
            )
        else:
            raise RuntimeError(
                "OAuth2 flow not yet implemented. Use a service account."
            )

        self._service = build("searchconsole", "v1", credentials=creds)
        return self._service

    def query_performance(
        self,
        site_url: str,
        keyword: str = None,
        days: int = 90,
        min_impressions: int = 10,
        row_limit: int = 100,
    ) -> list[dict]:
        """
        Pull query performance data from GSC.

        Args:
            site_url: The GSC property URL (e.g., "https://example.com")
            keyword: Optional keyword filter (partial match)
            days: Lookback period in days
            min_impressions: Minimum impressions threshold
            row_limit: Max rows to return

        Returns:
            List of dicts with query, page, clicks, impressions, ctr, position
        """
        from datetime import datetime, timedelta

        service = self._get_service()

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        request_body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query", "page"],
            "rowLimit": row_limit,
            "dimensionFilterGroups": [],
        }

        if keyword:
            request_body["dimensionFilterGroups"].append(
                {
                    "filters": [
                        {
                            "dimension": "query",
                            "operator": "contains",
                            "expression": keyword,
                        }
                    ]
                }
            )

        response = (
            service.searchanalytics()
            .query(siteUrl=site_url, body=request_body)
            .execute()
        )

        rows = response.get("rows", [])
        results = []

        for row in rows:
            impressions = row.get("impressions", 0)
            if impressions < min_impressions:
                continue

            results.append(
                {
                    "query": row["keys"][0],
                    "page": row["keys"][1],
                    "clicks": row.get("clicks", 0),
                    "impressions": impressions,
                    "ctr": round(row.get("ctr", 0) * 100, 2),
                    "position": round(row.get("position", 0), 1),
                }
            )

        return sorted(results, key=lambda x: x["impressions"], reverse=True)

    def detect_cannibalization(
        self,
        site_url: str,
        keyword: str,
        days: int = 90,
    ) -> list[dict]:
        """
        Detect keyword cannibalization: multiple pages ranking for same query.

        Returns:
            List of queries where 2+ pages from the site appear,
            sorted by total impressions.
        """
        results = self.query_performance(
            site_url=site_url,
            keyword=keyword,
            days=days,
            min_impressions=5,
            row_limit=500,
        )

        # Group by query
        query_pages = {}
        for row in results:
            q = row["query"]
            if q not in query_pages:
                query_pages[q] = []
            query_pages[q].append(row)

        # Find queries with multiple pages
        cannibalized = []
        for query, pages in query_pages.items():
            if len(pages) > 1:
                cannibalized.append(
                    {
                        "query": query,
                        "page_count": len(pages),
                        "pages": sorted(
                            pages, key=lambda x: x["position"]
                        ),
                        "total_impressions": sum(
                            p["impressions"] for p in pages
                        ),
                    }
                )

        return sorted(
            cannibalized,
            key=lambda x: x["total_impressions"],
            reverse=True,
        )
