#!/usr/bin/env python3
"""Validate HypoGeniC task configs and the skill's plan-only run policy."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

if __package__:
    from ._common import (
        MAX_CONFIG_BYTES,
        MAX_JSON_BYTES,
        CliError,
        checked_input_file,
        emit_error,
        emit_json,
        load_structured_document,
        named_env_presence,
        validate_run_config,
        validate_task_config,
    )
else:
    from _common import (  # type: ignore
        MAX_CONFIG_BYTES,
        MAX_JSON_BYTES,
        CliError,
        checked_input_file,
        emit_error,
        emit_json,
        load_structured_document,
        named_env_presence,
        validate_run_config,
        validate_task_config,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate strict local HypoGeniC configuration without importing "
            "HypoGeniC, loading .env, enumerating the environment, or calling a model."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser(
        "run",
        help="Validate the skill-local provider/budget/run policy",
    )
    run.add_argument("--input", required=True, help="Local .json/.yaml run policy")
    run.add_argument("--root", default=".", help="Existing local I/O boundary")
    run.add_argument(
        "--check-env",
        action="store_true",
        help="Check only the validated provider-specific variable name; never print its value",
    )
    run.add_argument(
        "--check-paths",
        action="store_true",
        help="Require task_config and dataset_manifest to exist inside root",
    )

    task = subparsers.add_parser(
        "task",
        help="Validate the pinned source's task-config surface",
    )
    task.add_argument("--input", required=True, help="Local .json/.yaml task config")
    task.add_argument("--root", default=".", help="Existing local I/O boundary")
    task.add_argument(
        "--check-data-files",
        action="store_true",
        help="Require train/validation/test and optional OOD JSON beside the task config",
    )
    return parser


def _run_policy(args: argparse.Namespace) -> int:
    document = load_structured_document(
        args.input,
        root=args.root,
        max_bytes=MAX_CONFIG_BYTES,
    )
    config = validate_run_config(document)
    if args.check_paths:
        checked_input_file(
            config["data"]["task_config"],
            root=args.root,
            suffixes={".json", ".yaml", ".yml"},
            max_bytes=MAX_CONFIG_BYTES,
        )
        checked_input_file(
            config["data"]["dataset_manifest"],
            root=args.root,
            suffixes={".json"},
            max_bytes=MAX_CONFIG_BYTES,
        )
    environment = (
        named_env_presence(config)
        if args.check_env
        else {
            "checked": False,
            "name": config["provider"]["credential_env"],
            "value_included": False,
        }
    )
    emit_json(
        {
            "ok": True,
            "schema": "hypogenic-local-run-policy",
            "schema_version": config["schema_version"],
            "provider": {
                "type": config["provider"]["type"],
                "model": config["provider"]["model"],
                "data_destination": config["provider"]["data_destination"],
                "local_model_path_configured": (
                    config["provider"]["local_model_path"] is not None
                ),
            },
            "credential_environment": environment,
            "paths_checked": bool(args.check_paths),
            "external_calls_authorized": False,
            "requires_separate_confirmation": True,
            "send_test_split": False,
            "redacted_logging_required": True,
            "network_access": False,
            "model_called": False,
            "secret_values_included": False,
        }
    )
    return 0


def _task_config(args: argparse.Namespace) -> int:
    config_path = checked_input_file(
        args.input,
        root=args.root,
        suffixes={".json", ".yaml", ".yml"},
        max_bytes=MAX_CONFIG_BYTES,
    )
    document = load_structured_document(
        args.input,
        root=args.root,
        max_bytes=MAX_CONFIG_BYTES,
    )
    config = validate_task_config(document)
    checked: list[str] = []
    if args.check_data_files:
        for key in (
            "train_data_path",
            "val_data_path",
            "test_data_path",
            "ood_data_path",
        ):
            if config.get(key) is None:
                continue
            checked_input_file(
                config[key],
                root=config_path.parent,
                suffixes={".json"},
                max_bytes=MAX_JSON_BYTES,
            )
            checked.append(key)
    emit_json(
        {
            "ok": True,
            "schema": "hypogenic-upstream-task-config",
            "task_name": config["task_name"],
            "label_name": config["label_name"],
            "prompt_template_keys": config["prompt_template_keys"],
            "prompt_text_interpreted": False,
            "data_files_checked": checked,
            "split_paths_distinct": True,
            "network_access": False,
            "model_called": False,
            "secret_values_included": False,
        }
    )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "run":
            return _run_policy(args)
        return _task_config(args)
    except (CliError, OSError) as error:
        return emit_error(error)


if __name__ == "__main__":
    raise SystemExit(main())
