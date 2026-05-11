"""Weiyun API client - core module for interacting with Weiyun services."""

import os
import json
import time
import hashlib
import requests
from typing import Optional

from weiyun_skills.login import load_cookies, DEFAULT_COOKIES_PATH
from weiyun_skills.utils import (
    format_size,
    get_file_md5,
    parse_cookies_str,
    get_timestamp,
    ensure_dir,
    build_response,
)

# Weiyun API base URLs
API_BASE = "https://www.weiyun.com"
DISK_API = f"{API_BASE}/webapp/json/weiyunQdiskClient"


class WeiyunClient:
    """Tencent Weiyun API client.

    Supports file management, sharing, and space operations.
    Authentication via saved cookies file or direct cookies string.

    Usage:
        # Auto-load cookies from cookies.json
        client = WeiyunClient()

        # Or pass cookies string directly
        client = WeiyunClient(cookies_str="uin=xxx; skey=xxx; ...")
    """

    def __init__(self, cookies_str: str = None,
                 cookies_path: str = DEFAULT_COOKIES_PATH):
        """Initialize Weiyun client.

        Args:
            cookies_str: Optional cookies string. If not provided,
                         will try to load from cookies_path.
            cookies_path: Path to cookies JSON file.
        """
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.weiyun.com/",
            "Content-Type": "application/json",
        })

        if cookies_str:
            cookies_dict = parse_cookies_str(cookies_str)
            self.session.cookies.update(cookies_dict)
        else:
            cookies_data = load_cookies(cookies_path)
            if cookies_data.get("cookies_dict"):
                self.session.cookies.update(cookies_data["cookies_dict"])
            elif cookies_data.get("cookies_str"):
                cookies_dict = parse_cookies_str(cookies_data["cookies_str"])
                self.session.cookies.update(cookies_dict)

    def _api_request(self, cmd: str, body: dict = None) -> dict:
        """Make an API request to Weiyun.

        Args:
            cmd: API command name.
            body: Request body data.

        Returns:
            API response as dict.
        """
        url = f"{DISK_API}/{cmd}"
        payload = {
            "req_header": {
                "cmd": cmd,
                "main_v": 12,
                "sub_v": 1,
            },
            "req_body": body or {},
        }
        try:
            resp = self.session.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if data.get("rsp_header", {}).get("retcode") == 0:
                return build_response(True, data=data.get("rsp_body", {}))
            else:
                msg = data.get("rsp_header", {}).get("retmsg", "Unknown error")
                return build_response(False, message=msg,
                                      error_code="API_ERROR")
        except requests.RequestException as e:
            return build_response(False, message=str(e),
                                  error_code="NETWORK_ERROR")
        except (json.JSONDecodeError, KeyError) as e:
            return build_response(False, message=f"Invalid response: {e}",
                                  error_code="API_ERROR")

    # ==================== File Management ====================

    def list_files(self, remote_path: str = "/", sort_by: str = "name",
                   sort_order: str = "asc", page: int = 1,
                   page_size: int = 100) -> dict:
        """List files and folders in a directory.

        Args:
            remote_path: Remote directory path.
            sort_by: Sort field - 'name', 'size', or 'time'.
            sort_order: Sort order - 'asc' or 'desc'.
            page: Page number.
            page_size: Items per page.

        Returns:
            Response dict with file list.
        """
        sort_map = {"name": 1, "size": 2, "time": 3}
        order_map = {"asc": 1, "desc": 2}

        body = {
            "path": remote_path,
            "sort_type": sort_map.get(sort_by, 1),
            "sort_order": order_map.get(sort_order, 1),
            "start": (page - 1) * page_size,
            "count": page_size,
        }
        result = self._api_request("DiskDirFileBatchList", body)
        if not result["success"]:
            return result

        # Format file list
        raw_files = result["data"].get("file_list", [])
        raw_dirs = result["data"].get("dir_list", [])
        files = []

        for d in raw_dirs:
            files.append({
                "file_id": d.get("dir_key", ""),
                "name": d.get("dir_name", ""),
                "type": "folder",
                "size": 0,
                "size_str": "-",
                "path": d.get("dir_path", ""),
                "updated_at": d.get("modify_time", ""),
            })

        for f in raw_files:
            size = f.get("file_size", 0)
            files.append({
                "file_id": f.get("file_id", ""),
                "name": f.get("file_name", ""),
                "type": "file",
                "size": size,
                "size_str": format_size(size),
                "path": f.get("file_path", ""),
                "updated_at": f.get("modify_time", ""),
            })

        total = result["data"].get("total_count",
                                    len(raw_files) + len(raw_dirs))
        return build_response(True, data={
            "files": files,
            "total": total,
        })

    def upload_file(self, local_path: str, remote_path: str,
                    overwrite: bool = False) -> dict:
        """Upload a local file to Weiyun.

        Args:
            local_path: Path to local file.
            remote_path: Target path on Weiyun.
            overwrite: Whether to overwrite existing file.

        Returns:
            Response dict with upload result.
        """
        if not os.path.isfile(local_path):
            return build_response(False,
                                  message=f"Local file not found: {local_path}",
                                  error_code="FILE_NOT_FOUND")

        file_size = os.path.getsize(local_path)
        file_name = os.path.basename(local_path)
        file_md5 = get_file_md5(local_path)

        # Split remote_path into directory and filename
        remote_dir = os.path.dirname(remote_path)
        if not remote_dir:
            remote_dir = "/"

        body = {
            "dir_path": remote_dir,
            "file_name": file_name,
            "file_size": file_size,
            "file_md5": file_md5,
            "overwrite": overwrite,
        }

        # Request upload URL
        result = self._api_request("DiskFileUpload", body)
        if not result["success"]:
            return result

        upload_url = result["data"].get("upload_url", "")
        if upload_url:
            try:
                with open(local_path, "rb") as f:
                    upload_resp = self.session.put(upload_url, data=f,
                                                   timeout=300)
                    if upload_resp.status_code not in (200, 201):
                        return build_response(
                            False,
                            message=f"Upload failed: HTTP {upload_resp.status_code}",
                            error_code="NETWORK_ERROR"
                        )
            except requests.RequestException as e:
                return build_response(False, message=f"Upload error: {e}",
                                      error_code="NETWORK_ERROR")

        return build_response(True, data={
            "file_id": result["data"].get("file_id", ""),
            "name": file_name,
            "size": file_size,
            "remote_path": remote_path,
            "md5": file_md5,
            "uploaded_at": get_timestamp(),
        })

    def download_file(self, remote_path: str, local_path: str,
                      overwrite: bool = False) -> dict:
        """Download a file from Weiyun to local.

        Args:
            remote_path: Remote file path on Weiyun.
            local_path: Local destination path.
            overwrite: Whether to overwrite local file.

        Returns:
            Response dict with download result.
        """
        if os.path.exists(local_path) and not overwrite:
            return build_response(
                False,
                message=f"Local file already exists: {local_path}",
                error_code="DUPLICATE_NAME"
            )

        # Request download URL
        body = {"file_path": remote_path}
        result = self._api_request("DiskFileDownload", body)
        if not result["success"]:
            return result

        download_url = result["data"].get("download_url", "")
        if not download_url:
            return build_response(False, message="No download URL returned",
                                  error_code="API_ERROR")

        ensure_dir(local_path)
        start_time = time.time()
        try:
            resp = self.session.get(download_url, stream=True, timeout=300)
            resp.raise_for_status()
            with open(local_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        except requests.RequestException as e:
            return build_response(False, message=f"Download error: {e}",
                                  error_code="NETWORK_ERROR")

        elapsed = round(time.time() - start_time, 2)
        file_size = os.path.getsize(local_path)
        file_md5 = get_file_md5(local_path)

        return build_response(True, data={
            "local_path": local_path,
            "size": file_size,
            "md5": file_md5,
            "elapsed": elapsed,
        })

    def delete_file(self, remote_path: str,
                    permanent: bool = False) -> dict:
        """Delete a file or folder on Weiyun.

        Args:
            remote_path: Path to delete.
            permanent: If True, permanently delete (skip recycle bin).

        Returns:
            Response dict with deletion result.
        """
        body = {
            "file_path": remote_path,
            "permanent": permanent,
        }
        result = self._api_request("DiskFileDelete", body)
        if not result["success"]:
            return result

        return build_response(True, data={
            "deleted_path": remote_path,
            "is_permanent": permanent,
            "deleted_at": get_timestamp(),
        })

    def move_file(self, source_path: str, target_path: str) -> dict:
        """Move a file or folder to another directory.

        Args:
            source_path: Source file/folder path.
            target_path: Target directory path.

        Returns:
            Response dict with move result.
        """
        body = {
            "src_path": source_path,
            "dst_path": target_path,
        }
        result = self._api_request("DiskFileMove", body)
        if not result["success"]:
            return result

        file_name = os.path.basename(source_path)
        new_path = os.path.join(target_path, file_name)
        return build_response(True, data={
            "source_path": source_path,
            "target_path": new_path,
        })

    def copy_file(self, source_path: str, target_path: str) -> dict:
        """Copy a file or folder to another directory.

        Args:
            source_path: Source file/folder path.
            target_path: Target directory path.

        Returns:
            Response dict with copy result.
        """
        body = {
            "src_path": source_path,
            "dst_path": target_path,
        }
        result = self._api_request("DiskFileCopy", body)
        if not result["success"]:
            return result

        file_name = os.path.basename(source_path)
        new_path = os.path.join(target_path, file_name)
        return build_response(True, data={
            "source_path": source_path,
            "target_path": new_path,
            "new_file_id": result["data"].get("file_id", ""),
        })

    def rename_file(self, remote_path: str, new_name: str) -> dict:
        """Rename a file or folder.

        Args:
            remote_path: Current file path.
            new_name: New name (without path).

        Returns:
            Response dict with rename result.
        """
        body = {
            "file_path": remote_path,
            "new_name": new_name,
        }
        result = self._api_request("DiskFileRename", body)
        if not result["success"]:
            return result

        parent_dir = os.path.dirname(remote_path)
        new_path = os.path.join(parent_dir, new_name)
        return build_response(True, data={
            "old_path": remote_path,
            "new_path": new_path,
        })

    def create_folder(self, remote_path: str) -> dict:
        """Create a folder on Weiyun.

        Args:
            remote_path: Folder path to create.

        Returns:
            Response dict with folder creation result.
        """
        body = {"dir_path": remote_path}
        result = self._api_request("DiskDirCreate", body)
        if not result["success"]:
            return result

        return build_response(True, data={
            "folder_id": result["data"].get("dir_key", ""),
            "path": remote_path,
            "created_at": get_timestamp(),
        })

    def search_files(self, keyword: str, file_type: str = "all",
                     page: int = 1, page_size: int = 50) -> dict:
        """Search files by keyword.

        Args:
            keyword: Search keyword.
            file_type: Type filter - 'all', 'document', 'image', 'video', 'audio'.
            page: Page number.
            page_size: Items per page.

        Returns:
            Response dict with search results.
        """
        type_map = {"all": 0, "document": 1, "image": 2, "video": 3, "audio": 4}
        body = {
            "keyword": keyword,
            "search_type": type_map.get(file_type, 0),
            "start": (page - 1) * page_size,
            "count": page_size,
        }
        result = self._api_request("DiskFileSearch", body)
        if not result["success"]:
            return result

        raw_files = result["data"].get("file_list", [])
        results = []
        for f in raw_files:
            size = f.get("file_size", 0)
            results.append({
                "file_id": f.get("file_id", ""),
                "name": f.get("file_name", ""),
                "type": "file",
                "size_str": format_size(size),
                "path": f.get("file_path", ""),
            })

        return build_response(True, data={
            "results": results,
            "total": result["data"].get("total_count", len(results)),
        })

    # ==================== Share Management ====================

    def create_share(self, remote_path: str, expire_days: int = 0,
                     password: str = None) -> dict:
        """Create a share link for a file or folder.

        Args:
            remote_path: Path to share.
            expire_days: Expiry in days (0 = permanent).
            password: Optional 4-char password.

        Returns:
            Response dict with share link info.
        """
        body = {
            "file_path": remote_path,
            "expire_days": expire_days,
        }
        if password:
            body["password"] = password

        result = self._api_request("DiskShareCreate", body)
        if not result["success"]:
            return result

        return build_response(True, data={
            "share_id": result["data"].get("share_id", ""),
            "share_url": result["data"].get("share_url", ""),
            "password": password or "",
            "expire_at": result["data"].get("expire_time", ""),
            "created_at": get_timestamp(),
        })

    def cancel_share(self, share_id: str) -> dict:
        """Cancel an existing share.

        Args:
            share_id: Share ID to cancel.

        Returns:
            Response dict with cancellation result.
        """
        body = {"share_id": share_id}
        result = self._api_request("DiskShareCancel", body)
        if not result["success"]:
            return result

        return build_response(True, data={
            "share_id": share_id,
            "cancelled_at": get_timestamp(),
        })

    def list_shares(self, status: str = "all", page: int = 1,
                    page_size: int = 20) -> dict:
        """List all share links.

        Args:
            status: Filter by status - 'all', 'active', 'expired'.
            page: Page number.
            page_size: Items per page.

        Returns:
            Response dict with share list.
        """
        status_map = {"all": 0, "active": 1, "expired": 2}
        body = {
            "status": status_map.get(status, 0),
            "start": (page - 1) * page_size,
            "count": page_size,
        }
        result = self._api_request("DiskShareList", body)
        if not result["success"]:
            return result

        raw_shares = result["data"].get("share_list", [])
        shares = []
        for s in raw_shares:
            shares.append({
                "share_id": s.get("share_id", ""),
                "share_url": s.get("share_url", ""),
                "file_name": s.get("file_name", ""),
                "status": s.get("status", ""),
                "view_count": s.get("view_count", 0),
                "download_count": s.get("download_count", 0),
                "created_at": s.get("create_time", ""),
                "expire_at": s.get("expire_time", ""),
            })

        return build_response(True, data={
            "shares": shares,
            "total": result["data"].get("total_count", len(shares)),
        })

    # ==================== Space Management ====================

    def get_space_info(self) -> dict:
        """Get storage space usage information.

        Returns:
            Response dict with space info.
        """
        result = self._api_request("DiskSpaceQuery", {})
        if not result["success"]:
            return result

        total = result["data"].get("total_space", 0)
        used = result["data"].get("used_space", 0)
        free = max(0, total - used)
        percent = round((used / total * 100), 1) if total > 0 else 0

        return build_response(True, data={
            "total_space": total,
            "total_space_str": format_size(total),
            "used_space": used,
            "used_space_str": format_size(used),
            "free_space": free,
            "free_space_str": format_size(free),
            "usage_percent": percent,
            "file_count": result["data"].get("file_count", 0),
            "folder_count": result["data"].get("dir_count", 0),
        })

    def get_recycle_bin(self, page: int = 1, page_size: int = 50) -> dict:
        """Get files in recycle bin.

        Args:
            page: Page number.
            page_size: Items per page.

        Returns:
            Response dict with recycle bin contents.
        """
        body = {
            "start": (page - 1) * page_size,
            "count": page_size,
        }
        result = self._api_request("DiskRecycleList", body)
        if not result["success"]:
            return result

        raw_files = result["data"].get("file_list", [])
        files = []
        total_size = 0
        for f in raw_files:
            size = f.get("file_size", 0)
            total_size += size
            files.append({
                "file_id": f.get("file_id", ""),
                "name": f.get("file_name", ""),
                "size_str": format_size(size),
                "original_path": f.get("original_path", ""),
                "deleted_at": f.get("delete_time", ""),
            })

        return build_response(True, data={
            "files": files,
            "total": result["data"].get("total_count", len(files)),
            "total_size_str": format_size(total_size),
        })

    def restore_file(self, file_id: str) -> dict:
        """Restore a file from recycle bin.

        Args:
            file_id: File ID in recycle bin.

        Returns:
            Response dict with restoration result.
        """
        body = {"file_id": file_id}
        result = self._api_request("DiskRecycleRestore", body)
        if not result["success"]:
            return result

        return build_response(True, data={
            "file_id": file_id,
            "restored_path": result["data"].get("restore_path", ""),
            "restored_at": get_timestamp(),
        })

    def clear_recycle_bin(self, confirm: bool = False) -> dict:
        """Clear all files in recycle bin. This action is irreversible!

        Args:
            confirm: Must be True to execute.

        Returns:
            Response dict with clear result.
        """
        if not confirm:
            return build_response(
                False,
                message="Must set confirm=True to clear recycle bin",
                error_code="INVALID_PARAM"
            )

        result = self._api_request("DiskRecycleClear", {})
        if not result["success"]:
            return result

        return build_response(True, data={
            "deleted_count": result["data"].get("delete_count", 0),
            "freed_space_str": format_size(
                result["data"].get("freed_space", 0)
            ),
            "cleared_at": get_timestamp(),
        })
