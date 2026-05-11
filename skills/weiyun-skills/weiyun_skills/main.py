"""Weiyun Skills CLI - command line interface for Weiyun management."""

import sys
import json
import argparse

from weiyun_skills.client import WeiyunClient
from weiyun_skills.utils import format_size

try:
    from tabulate import tabulate
except ImportError:
    tabulate = None


def _print_json(data: dict) -> None:
    """Pretty print JSON data."""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _print_table(headers: list, rows: list) -> None:
    """Print data as a formatted table."""
    if tabulate:
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        # Fallback: simple table output
        print("\t".join(headers))
        print("-" * (len(headers) * 20))
        for row in rows:
            print("\t".join(str(c) for c in row))


def cmd_list(client: WeiyunClient, args) -> None:
    """Handle 'list' command."""
    result = client.list_files(
        remote_path=args.path,
        sort_by=getattr(args, "sort", "name"),
        sort_order=getattr(args, "order", "asc"),
    )
    if not result["success"]:
        print(f"[ERROR] {result['message']}")
        return

    files = result["data"]["files"]
    if not files:
        print(f"(empty directory: {args.path})")
        return

    headers = ["Type", "Name", "Size", "Updated"]
    rows = []
    for f in files:
        icon = "📁" if f["type"] == "folder" else "📄"
        rows.append([icon, f["name"], f["size_str"], f["updated_at"]])
    _print_table(headers, rows)
    print(f"\nTotal: {result['data']['total']} items")


def cmd_upload(client: WeiyunClient, args) -> None:
    """Handle 'upload' command."""
    print(f"[*] Uploading {args.local} -> {args.remote}")
    result = client.upload_file(
        args.local, args.remote,
        overwrite=getattr(args, "overwrite", False)
    )
    if result["success"]:
        d = result["data"]
        print(f"[✓] Uploaded: {d['name']} ({format_size(d['size'])})")
        print(f"    Path: {d['remote_path']}")
        print(f"    MD5:  {d['md5']}")
    else:
        print(f"[✗] Upload failed: {result['message']}")


def cmd_download(client: WeiyunClient, args) -> None:
    """Handle 'download' command."""
    print(f"[*] Downloading {args.remote} -> {args.local}")
    result = client.download_file(
        args.remote, args.local,
        overwrite=getattr(args, "overwrite", False)
    )
    if result["success"]:
        d = result["data"]
        print(f"[✓] Downloaded: {d['local_path']} ({format_size(d['size'])})")
        print(f"    MD5:  {d['md5']}")
        print(f"    Time: {d['elapsed']}s")
    else:
        print(f"[✗] Download failed: {result['message']}")


def cmd_delete(client: WeiyunClient, args) -> None:
    """Handle 'delete' command."""
    permanent = getattr(args, "permanent", False)
    action = "Permanently deleting" if permanent else "Deleting"
    print(f"[*] {action} {args.path}")
    result = client.delete_file(args.path, permanent=permanent)
    if result["success"]:
        d = result["data"]
        msg = "permanently deleted" if d["is_permanent"] else "moved to recycle bin"
        print(f"[✓] {d['deleted_path']} {msg}")
    else:
        print(f"[✗] Delete failed: {result['message']}")


def cmd_move(client: WeiyunClient, args) -> None:
    """Handle 'move' command."""
    print(f"[*] Moving {args.source} -> {args.target}")
    result = client.move_file(args.source, args.target)
    if result["success"]:
        d = result["data"]
        print(f"[✓] Moved to: {d['target_path']}")
    else:
        print(f"[✗] Move failed: {result['message']}")


def cmd_copy(client: WeiyunClient, args) -> None:
    """Handle 'copy' command."""
    print(f"[*] Copying {args.source} -> {args.target}")
    result = client.copy_file(args.source, args.target)
    if result["success"]:
        d = result["data"]
        print(f"[✓] Copied to: {d['target_path']}")
    else:
        print(f"[✗] Copy failed: {result['message']}")


def cmd_rename(client: WeiyunClient, args) -> None:
    """Handle 'rename' command."""
    print(f"[*] Renaming {args.path} -> {args.name}")
    result = client.rename_file(args.path, args.name)
    if result["success"]:
        d = result["data"]
        print(f"[✓] Renamed: {d['old_path']} -> {d['new_path']}")
    else:
        print(f"[✗] Rename failed: {result['message']}")


def cmd_mkdir(client: WeiyunClient, args) -> None:
    """Handle 'mkdir' command."""
    print(f"[*] Creating folder: {args.path}")
    result = client.create_folder(args.path)
    if result["success"]:
        print(f"[✓] Created: {result['data']['path']}")
    else:
        print(f"[✗] Create failed: {result['message']}")


def cmd_search(client: WeiyunClient, args) -> None:
    """Handle 'search' command."""
    result = client.search_files(
        keyword=args.keyword,
        file_type=getattr(args, "type", "all"),
    )
    if not result["success"]:
        print(f"[ERROR] {result['message']}")
        return

    results = result["data"]["results"]
    if not results:
        print(f"No files found matching '{args.keyword}'")
        return

    headers = ["Name", "Size", "Path"]
    rows = [[r["name"], r["size_str"], r["path"]] for r in results]
    _print_table(headers, rows)
    print(f"\nFound: {result['data']['total']} items")


def cmd_share(client: WeiyunClient, args) -> None:
    """Handle 'share' command."""
    print(f"[*] Creating share for: {args.path}")
    result = client.create_share(
        args.path,
        expire_days=getattr(args, "expire", 0),
        password=getattr(args, "password", None),
    )
    if result["success"]:
        d = result["data"]
        print(f"[✓] Share created!")
        print(f"    URL:      {d['share_url']}")
        if d.get("password"):
            print(f"    Password: {d['password']}")
        if d.get("expire_at"):
            print(f"    Expires:  {d['expire_at']}")
    else:
        print(f"[✗] Share failed: {result['message']}")


def cmd_unshare(client: WeiyunClient, args) -> None:
    """Handle 'unshare' command."""
    result = client.cancel_share(args.share_id)
    if result["success"]:
        print(f"[✓] Share {args.share_id} cancelled")
    else:
        print(f"[✗] Cancel failed: {result['message']}")


def cmd_shares(client: WeiyunClient, args) -> None:
    """Handle 'shares' command."""
    result = client.list_shares(
        status=getattr(args, "status", "all")
    )
    if not result["success"]:
        print(f"[ERROR] {result['message']}")
        return

    shares = result["data"]["shares"]
    if not shares:
        print("No shares found")
        return

    headers = ["ID", "File", "URL", "Status", "Views", "Downloads", "Expires"]
    rows = []
    for s in shares:
        rows.append([
            s["share_id"], s["file_name"], s["share_url"],
            s["status"], s["view_count"], s["download_count"],
            s["expire_at"],
        ])
    _print_table(headers, rows)
    print(f"\nTotal: {result['data']['total']} shares")


def cmd_space(client: WeiyunClient, args) -> None:
    """Handle 'space' command."""
    result = client.get_space_info()
    if not result["success"]:
        print(f"[ERROR] {result['message']}")
        return

    d = result["data"]
    print("=" * 40)
    print("  Weiyun Space Usage")
    print("=" * 40)
    print(f"  Total:   {d['total_space_str']}")
    print(f"  Used:    {d['used_space_str']} ({d['usage_percent']}%)")
    print(f"  Free:    {d['free_space_str']}")
    print(f"  Files:   {d['file_count']}")
    print(f"  Folders: {d['folder_count']}")
    print("=" * 40)

    # Simple progress bar
    bar_width = 30
    filled = int(bar_width * d["usage_percent"] / 100)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"  [{bar}] {d['usage_percent']}%")


def cmd_recycle(client: WeiyunClient, args) -> None:
    """Handle 'recycle' command."""
    result = client.get_recycle_bin()
    if not result["success"]:
        print(f"[ERROR] {result['message']}")
        return

    files = result["data"]["files"]
    if not files:
        print("Recycle bin is empty")
        return

    headers = ["ID", "Name", "Size", "Original Path", "Deleted At"]
    rows = []
    for f in files:
        rows.append([
            f["file_id"], f["name"], f["size_str"],
            f["original_path"], f["deleted_at"],
        ])
    _print_table(headers, rows)
    print(f"\nTotal: {result['data']['total']} items "
          f"({result['data']['total_size_str']})")


def cmd_restore(client: WeiyunClient, args) -> None:
    """Handle 'restore' command."""
    result = client.restore_file(args.file_id)
    if result["success"]:
        d = result["data"]
        print(f"[✓] Restored to: {d['restored_path']}")
    else:
        print(f"[✗] Restore failed: {result['message']}")


def cmd_clear_recycle(client: WeiyunClient, args) -> None:
    """Handle 'clear-recycle' command."""
    if not getattr(args, "confirm", False):
        print("[!] This will permanently delete all files in recycle bin!")
        print("    Add --confirm flag to proceed.")
        return

    result = client.clear_recycle_bin(confirm=True)
    if result["success"]:
        d = result["data"]
        print(f"[✓] Recycle bin cleared!")
        print(f"    Deleted: {d['deleted_count']} files")
        print(f"    Freed:   {d['freed_space_str']}")
    else:
        print(f"[✗] Clear failed: {result['message']}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Weiyun Skills - Tencent Weiyun Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m weiyun_skills.main list /
  python -m weiyun_skills.main upload ./file.pdf /docs/
  python -m weiyun_skills.main download /docs/file.pdf ./
  python -m weiyun_skills.main share /docs/file.pdf --expire 7
  python -m weiyun_skills.main space
        """
    )

    parser.add_argument(
        "--cookies", type=str, default=None,
        help="Cookies string (overrides cookies.json)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list
    p_list = subparsers.add_parser("list", help="List files in a directory")
    p_list.add_argument("path", nargs="?", default="/", help="Directory path")
    p_list.add_argument("--sort", choices=["name", "size", "time"], default="name")
    p_list.add_argument("--order", choices=["asc", "desc"], default="asc")

    # upload
    p_upload = subparsers.add_parser("upload", help="Upload a file")
    p_upload.add_argument("local", help="Local file path")
    p_upload.add_argument("remote", help="Remote target path")
    p_upload.add_argument("--overwrite", action="store_true")

    # download
    p_download = subparsers.add_parser("download", help="Download a file")
    p_download.add_argument("remote", help="Remote file path")
    p_download.add_argument("local", help="Local save path")
    p_download.add_argument("--overwrite", action="store_true")

    # delete
    p_delete = subparsers.add_parser("delete", help="Delete a file")
    p_delete.add_argument("path", help="File path to delete")
    p_delete.add_argument("--permanent", action="store_true",
                          help="Permanently delete (skip recycle bin)")

    # move
    p_move = subparsers.add_parser("move", help="Move a file")
    p_move.add_argument("source", help="Source path")
    p_move.add_argument("target", help="Target directory path")

    # copy
    p_copy = subparsers.add_parser("copy", help="Copy a file")
    p_copy.add_argument("source", help="Source path")
    p_copy.add_argument("target", help="Target directory path")

    # rename
    p_rename = subparsers.add_parser("rename", help="Rename a file")
    p_rename.add_argument("path", help="File path")
    p_rename.add_argument("name", help="New name")

    # mkdir
    p_mkdir = subparsers.add_parser("mkdir", help="Create a folder")
    p_mkdir.add_argument("path", help="Folder path")

    # search
    p_search = subparsers.add_parser("search", help="Search files")
    p_search.add_argument("keyword", help="Search keyword")
    p_search.add_argument("--type",
                          choices=["all", "document", "image", "video", "audio"],
                          default="all")

    # share
    p_share = subparsers.add_parser("share", help="Create a share link")
    p_share.add_argument("path", help="File path to share")
    p_share.add_argument("--expire", type=int, default=0,
                         help="Expire in days (0=permanent)")
    p_share.add_argument("--password", type=str, default=None,
                         help="Share password (4 chars)")

    # unshare
    p_unshare = subparsers.add_parser("unshare", help="Cancel a share")
    p_unshare.add_argument("share_id", help="Share ID to cancel")

    # shares
    p_shares = subparsers.add_parser("shares", help="List all shares")
    p_shares.add_argument("--status", choices=["all", "active", "expired"],
                          default="all")

    # space
    subparsers.add_parser("space", help="Show space usage")

    # recycle
    subparsers.add_parser("recycle", help="Show recycle bin")

    # restore
    p_restore = subparsers.add_parser("restore", help="Restore from recycle bin")
    p_restore.add_argument("file_id", help="File ID to restore")

    # clear-recycle
    p_clear = subparsers.add_parser("clear-recycle",
                                     help="Clear recycle bin")
    p_clear.add_argument("--confirm", action="store_true",
                         help="Confirm clear operation")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize client
    client = WeiyunClient(cookies_str=args.cookies)

    # Dispatch command
    commands = {
        "list": cmd_list,
        "upload": cmd_upload,
        "download": cmd_download,
        "delete": cmd_delete,
        "move": cmd_move,
        "copy": cmd_copy,
        "rename": cmd_rename,
        "mkdir": cmd_mkdir,
        "search": cmd_search,
        "share": cmd_share,
        "unshare": cmd_unshare,
        "shares": cmd_shares,
        "space": cmd_space,
        "recycle": cmd_recycle,
        "restore": cmd_restore,
        "clear-recycle": cmd_clear_recycle,
    }

    handler = commands.get(args.command)
    if handler:
        handler(client, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
