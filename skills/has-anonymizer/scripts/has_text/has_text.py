#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""has-text — CLI tool for text anonymization and restoration.

Usage:
    has-text hide --type "person name" --type "address" --text "..." --mapping-output mapping.json
    has-text restore --mapping mapping.json --text "..."
    has-text scan --type "person name" --type "address" --text "..."

See `has-text <command> --help` for details.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

from .chunker import DEFAULT_MAX_CHUNK_TOKENS
from .cli_utils import (
    CLIError,
    StructuredArgumentParser,
    emit_json,
    error_payload,
    parallel_default,
)


# ======================================================================
# Argument parser
# ======================================================================

def build_parser() -> argparse.ArgumentParser:
    prog_name = os.environ.get("HAS_CLI_PROG", "has-text")
    global_options = argparse.ArgumentParser(add_help=False)
    global_options.add_argument(
        "--timing",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Include elapsed_ms in the JSON output",
    )
    global_options.add_argument(
        "--verbose",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Emit runtime status and progress messages to stderr",
    )
    parser = StructuredArgumentParser(
        parents=[global_options],
        prog=prog_name,
        description="HaS Text — Text anonymization and restoration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            f'  {prog_name} hide --type "person name" --type "address" --text "张三住在北京市朝阳区" --mapping-output mapping.json\n'
            f'  {prog_name} hide --type "person name" --file document.txt --mapping-output mapping.json\n'
            f'  {prog_name} hide --type "person name" --dir docs/ --output-dir .has/anonymized/\n'
            f'  {prog_name} restore --mapping mapping.json --text "<person name[1].personal.name> lives in ..."\n'
            f"  {prog_name} restore --dir .has/anonymized/ --output-dir .has/restored/\n"
            f"  {prog_name} restore --dir .has/anonymized/ --mapping-dir exported-mappings/ --output-dir .has/restored/\n"
            f'  {prog_name} scan --type "person name" --type "phone number" --file report.txt\n'
            f'  {prog_name} scan --type "person name" --type "phone number" --dir reports/\n'
            f'  cat doc.txt | {prog_name} hide --type "person name" --mapping-output mapping.json\n'
        ),
    )

    env_parallel = parallel_default()
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        parser_class=StructuredArgumentParser,
    )

    # --- hide ---
    hide_parser = subparsers.add_parser(
        "hide",
        parents=[global_options],
        help="Anonymize text (replace entities with privacy tags)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    hide_parser.add_argument(
        "--type",
        action="append",
        required=True,
        help="Entity type to anonymize; repeat the flag to add more types",
    )
    hide_input_group = hide_parser.add_mutually_exclusive_group()
    hide_input_group.add_argument("--text", help="Text to anonymize")
    hide_input_group.add_argument("--file", help="Read text from file")
    hide_input_group.add_argument(
        "--dir",
        help="Anonymize the immediate plaintext files in a directory (non-recursive)",
    )
    hide_parser.add_argument(
        "--output-dir",
        help="Batch output directory for anonymized files (default: .has/anonymized/ under the input directory)",
    )
    hide_parser.add_argument(
        "--output",
        help="Single-file output path for anonymized text",
    )
    hide_parser.add_argument(
        "--mapping-dir",
        help="Batch output directory for per-file mapping JSON files (default: mappings/ under the output directory)",
    )
    hide_parser.add_argument(
        "--mapping-output",
        help="Single-file output path for the generated mapping JSON",
    )
    hide_parser.add_argument(
        "--mapping",
        help="Single-file only: existing mapping JSON file path (for incremental anonymization)",
    )
    hide_parser.add_argument(
        "--max-chunk-tokens",
        type=int,
        default=DEFAULT_MAX_CHUNK_TOKENS,
        help=f"Max tokens per chunk (default: {DEFAULT_MAX_CHUNK_TOKENS})",
    )
    hide_parser.add_argument(
        "--max-parallel-requests",
        type=int,
        dest="max_parallel_requests",
        default=env_parallel,
        help=(
            "Max files to anonymize in parallel when hide uses --dir "
            f"(env: HAS_TEXT_MAX_PARALLEL_REQUESTS, default: {env_parallel})"
        ),
    )
    hide_parser.add_argument(
        "--no-tool-pair",
        action="store_false",
        dest="tool_pair",
        default=True,
        help="Disable diff-based pair extraction; always use Model-Pair (slower but more robust)",
    )

    from .commands.hide import cmd_hide

    hide_parser.set_defaults(func=cmd_hide)

    # --- restore ---
    restore_parser = subparsers.add_parser(
        "restore",
        parents=[global_options],
        help="Restore anonymized text to original form",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    restore_parser.add_argument(
        "--mapping",
        help=(
            "Single-file only: mapping JSON file path. "
            "restore --dir always uses per-file mappings from <dir>/mappings/ or --mapping-dir."
        ),
    )
    restore_input_group = restore_parser.add_mutually_exclusive_group()
    restore_input_group.add_argument("--text", help="Anonymized text to restore")
    restore_input_group.add_argument("--file", help="Read anonymized text from file")
    restore_input_group.add_argument(
        "--dir",
        help="Restore the immediate plaintext files in a directory (non-recursive)",
    )
    restore_parser.add_argument(
        "--mapping-dir",
        help=(
            "Batch mapping directory for per-file mapping JSON files "
            "(default: mappings/ under the input directory)"
        ),
    )
    restore_parser.add_argument(
        "--output-dir",
        help="Batch output directory for restored files (default: sibling of input under .has/, or .has/restored/)",
    )
    restore_parser.add_argument(
        "--output",
        help="Single-file output path for restored text",
    )
    restore_parser.add_argument(
        "--max-chunk-tokens",
        type=int,
        default=DEFAULT_MAX_CHUNK_TOKENS,
        help=f"Max tokens per chunk when restore uses the model (default: {DEFAULT_MAX_CHUNK_TOKENS})",
    )
    restore_parser.add_argument(
        "--max-parallel-requests",
        type=int,
        dest="max_parallel_requests",
        default=env_parallel,
        help=(
            "Max model-backed restore chunks to run in parallel "
            f"(env: HAS_TEXT_MAX_PARALLEL_REQUESTS, default: {env_parallel})"
        ),
    )

    from .commands.seek import cmd_restore

    restore_parser.set_defaults(func=cmd_restore)

    # --- scan ---
    scan_parser = subparsers.add_parser(
        "scan",
        parents=[global_options],
        help="Scan text for sensitive entities (NER only, no anonymization)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    scan_parser.add_argument(
        "--type",
        action="append",
        required=True,
        help="Entity type to scan for; repeat the flag to add more types",
    )
    scan_input_group = scan_parser.add_mutually_exclusive_group()
    scan_input_group.add_argument("--text", help="Text to scan")
    scan_input_group.add_argument("--file", help="Read text from file")
    scan_input_group.add_argument(
        "--dir",
        help="Scan the immediate plaintext files in a directory (non-recursive)",
    )
    from .commands.scan import DEFAULT_SCAN_MAX_CHUNK_TOKENS

    scan_parser.add_argument(
        "--max-chunk-tokens",
        type=int,
        default=DEFAULT_SCAN_MAX_CHUNK_TOKENS,
        help=f"Max tokens per chunk (default: {DEFAULT_SCAN_MAX_CHUNK_TOKENS})",
    )
    scan_parser.add_argument(
        "--max-parallel-requests",
        type=int,
        dest="max_parallel_requests",
        default=env_parallel,
        help=(
            "Max scan chunks to run in parallel "
            f"(env: HAS_TEXT_MAX_PARALLEL_REQUESTS, default: {env_parallel})"
        ),
    )

    from .commands.scan import cmd_scan

    scan_parser.set_defaults(func=cmd_scan)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args: Optional[argparse.Namespace] = None
    try:
        args = parser.parse_args(argv)
        args.timing = getattr(args, "timing", False)
        args.verbose = getattr(args, "verbose", False)
        if not args.command:
            from .cli_utils import fatal

            fatal("missing_command", "Choose a subcommand: scan, hide, or restore.")
        if args.verbose:
            os.environ["HAS_TEXT_VERBOSE"] = "1"
        else:
            os.environ.pop("HAS_TEXT_VERBOSE", None)
        args.func(args)
    except CLIError as exc:
        emit_json(error_payload(exc.code, exc.message))
        sys.exit(1)
    except (OSError, RuntimeError, ValueError) as exc:
        emit_json(error_payload("runtime_error", str(exc)))
        sys.exit(1)


if __name__ == "__main__":
    main()
