#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hide command — Anonymize text (Phase 1 of HaS workflow).

Internal workflow per chunk:
    NER → Hide (with or without mapping) → Model-Pair → composite check
    → Model-Split if needed → mapping self-check
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from ..chunker import DEFAULT_MAX_CHUNK_TOKENS, take_chunk
from ..client import ContextOverflowError, HaSClient
from ..pair import compute_pair_mapping
from ..server_runtime import DEFAULT_CONTEXT_PER_SLOT
from ..mapping import (
    TAG_PATTERN,
    find_composite_entries,
    find_tags,
    merge_mappings,
    normalize_mapping_dict,
    parse_json_tolerant,
)
from ..parallel import DEFAULT_MAX_PARALLEL_REQUESTS, resolve_parallel_workers
from ..prompts import (
    build_hide_with_messages,
    build_hide_without_messages,
    build_ner_messages,
    build_pair_messages,
    build_split_messages,
)
from ..validation import normalize_entity_map


@dataclass(frozen=True)
class HideDocument:
    """Plaintext input for batch anonymization."""

    source: str
    text: str


def estimate_hide_batch_request_count(documents: List[HideDocument]) -> int:
    """Estimate how many hide workers will actually need the model."""
    return sum(1 for document in documents if document.text and document.text.strip())


def _warn(message: str) -> None:
    """Emit a non-fatal warning to stderr."""
    if os.environ.get("HAS_TEXT_VERBOSE") == "1":
        print(f"Warning: {message}", file=sys.stderr)


def _clone_hide_client(client: HaSClient) -> HaSClient:
    """Create a fresh client per worker to avoid sharing HTTP sessions."""
    client_cls = client.__class__
    try:
        return client_cls(client.base_url)
    except TypeError:
        return HaSClient(client.base_url)


_HIDE_OVERHEAD = 200
# Pair call fixed overhead: pair prompt (~30) + pair mapping output (~200)
_PAIR_OVERHEAD = 230
# Anonymized output is roughly 1.05x the input (entity names become tags)
_OUTPUT_RATIO = 1.05
_MIN_CHUNK_TOKENS = 100
# Retry parameters for context overflow recovery
_RETRY_SHRINK_FACTOR = 0.75   # shrink chunk to 75% on overflow
_MAX_OVERFLOW_RETRIES = 2     # retry up to 2 times per chunk position


def _compute_chunk_budget(
    count_tokens,
    max_chunk_tokens: int,
    mapping: Optional[Dict[str, List[str]]],
    context_window: int = DEFAULT_CONTEXT_PER_SLOT,
) -> int:
    """Shrink the text budget as the carried mapping grows.

    The Hide call is a 3-turn conversation where the source text appears as
    input (T1-user) and the anonymized output (~1.05x input) appears as
    T2-assistant.  The accumulated mapping is injected once in T2-user.

    Context constraint for Hide:
        T*(1 + α) + F_hide + M  ≤  context_window
        T  ≤  (context_window - F_hide - M) / (1 + α)

    Model-Pair imposes a fixed ceiling (independent of mapping):
        T*(1 + α) + F_pair  ≤  context_window
        T  ≤  (context_window - F_pair) / (1 + α)
    """
    # Pair ceiling (fixed, does not depend on mapping)
    pair_limit = int((context_window - _PAIR_OVERHEAD) / (1 + _OUTPUT_RATIO))

    if not mapping:
        hide_limit = int((context_window - _HIDE_OVERHEAD) / (1 + _OUTPUT_RATIO))
        return min(max_chunk_tokens, hide_limit, pair_limit)

    mapping_json = json.dumps(mapping, ensure_ascii=False, separators=(",", ":"))
    mapping_tokens = count_tokens(mapping_json)

    # Hide constraint: text appears ~2x, mapping appears 1x
    hide_limit = int((context_window - _HIDE_OVERHEAD - mapping_tokens) / (1 + _OUTPUT_RATIO))

    budget = min(max_chunk_tokens, hide_limit, pair_limit)
    if budget < _MIN_CHUNK_TOKENS:
        raise RuntimeError(
            "Accumulated mapping no longer leaves room for more text chunks "
            f"({len(mapping)} entries, ~{mapping_tokens} mapping tokens, "
            f"derived budget {hide_limit}). "
            "Split the document or reduce the carried mapping."
        )
    return budget


# ======================================================================
# Mapping self-check
# ======================================================================

def _mapping_self_check(
    anonymized_text: str,
    mapping: Dict[str, List[str]],
) -> bool:
    """Check if the mapping covers all tags in the anonymized text.

    Returns True if all tags in the text have corresponding mapping entries.
    """
    text_tags = set(find_tags(anonymized_text))
    if not text_tags:
        return True

    # Expand composite keys to individual tags
    mapped_tags = set()
    for key in mapping:
        for m in TAG_PATTERN.finditer(key):
            mapped_tags.add(m.group(0))

    # Check that all text tags are covered
    missing = text_tags - mapped_tags
    if missing:
        return False

    # Check all values are non-empty
    for key, values in mapping.items():
        if not values:
            return False

    return True


# ======================================================================
# Composite tag handling
# ======================================================================

def _handle_composite_tags(
    client: HaSClient,
    mapping: Dict[str, List[str]],
) -> Dict[str, List[str]]:
    """If mapping has composite keys, split them using Model-Split.

    Returns mapping with composite keys replaced by atomic keys.
    """
    atomic, composite = find_composite_entries(mapping)

    if not composite:
        return mapping

    # Build input for Model-Split
    composite_list = [{k: v} for k, v in composite.items()]

    messages = build_split_messages(composite_list)
    raw_output = client.chat(messages)
    split_result = parse_json_tolerant(raw_output)

    normalized_split: Dict[str, List[str]] = {}

    try:
        if isinstance(split_result, dict):
            normalized_split = normalize_mapping_dict(split_result)
        elif isinstance(split_result, list):
            merged_split: Dict[str, Any] = {}
            for item in split_result:
                if not isinstance(item, dict):
                    raise ValueError("Model-Split returned a non-object entry")
                merged_split.update(item)
            normalized_split = normalize_mapping_dict(merged_split)
        else:
            raise ValueError("Model-Split did not return valid JSON")
    except ValueError as exc:
        _warn(f"Model-Split failed; keeping composite mapping entries intact ({exc})")
        return mapping

    merged = dict(atomic)
    merged.update(normalized_split)

    for composite_key, values in composite.items():
        component_tags = [m.group(0) for m in TAG_PATTERN.finditer(composite_key)]
        if not component_tags or not all(tag in merged for tag in component_tags):
            merged[composite_key] = values

    return merged


# ======================================================================
# Tool-Pair mapping extraction (diff-based, no model call)
# ======================================================================

def _tool_pair(
    original_text: str,
    anonymized_text: str,
) -> Optional[Dict[str, List[str]]]:
    """Extract mapping via diff alignment.  Returns None if self-check fails."""
    result = compute_pair_mapping(original_text, anonymized_text)
    if not result.self_check.get("pass"):
        return None
    return result.normalized_mapping


# ======================================================================
# Model-Pair mapping extraction
# ======================================================================

def _model_pair(
    client: HaSClient,
    original_text: str,
    anonymized_text: str,
) -> Dict[str, List[str]]:
    """Extract mapping via the model and reject incomplete results."""
    pair_messages = build_pair_messages(original_text, anonymized_text)
    raw_output = client.chat(pair_messages)
    pair_result = parse_json_tolerant(raw_output)
    if not isinstance(pair_result, dict):
        raise RuntimeError("Model-Pair did not return a JSON object")

    try:
        mapping = normalize_mapping_dict(pair_result)
    except ValueError as exc:
        raise RuntimeError(f"Model-Pair returned invalid mapping ({exc})") from exc

    mapping = _handle_composite_tags(client, mapping)
    if not _mapping_self_check(anonymized_text, mapping):
        raise RuntimeError("Model-Pair mapping did not cover all tags in anonymized text")

    return mapping


# ======================================================================
# Single-chunk hide
# ======================================================================

def _hide_single_chunk(
    client: HaSClient,
    text: str,
    types: List[str],
    existing_mapping: Optional[Dict[str, List[str]]] = None,
    tool_pair: bool = True,
    context_window: int = DEFAULT_CONTEXT_PER_SLOT,
) -> Tuple[str, Dict[str, List[str]]]:
    """Anonymize a single text chunk.

    Args:
        tool_pair: If True, try diff-based pair extraction first (faster,
            no model call).  Falls back to Model-Pair when self-check fails.

    Returns:
        (anonymized_text, mapping)
    """
    # Step 1: NER
    ner_messages = build_ner_messages(text, types)
    ner_output = client.chat(ner_messages)
    ner_result = normalize_entity_map(
        parse_json_tolerant(ner_output),
        context="NER output",
    )
    has_entities = any(ner_result.values())

    if not has_entities:
        # No entities found, return original text unchanged
        return text, existing_mapping or {}

    # Step 2: Hide
    # Use ner_output as-is (the raw model output string) for the assistant turn
    if existing_mapping:
        # Subsequent chunk: use hide_with
        messages = build_hide_with_messages(text, types, ner_output, existing_mapping)
    else:
        # First chunk: use hide_without
        messages = build_hide_without_messages(text, types, ner_output)

    anonymized_text = client.chat(messages)

    # Step 3: Pair — extract mapping
    chunk_mapping = None
    if tool_pair:
        chunk_mapping = _tool_pair(text, anonymized_text)
        if chunk_mapping is not None:
            # Tool-Pair succeeded; still need to split composites if any
            chunk_mapping = _handle_composite_tags(client, chunk_mapping)
            if not _mapping_self_check(anonymized_text, chunk_mapping):
                _warn("Tool-Pair mapping failed self-check after composite split, "
                      "falling back to Model-Pair")
                chunk_mapping = None
            else:
                _warn("Tool-Pair succeeded (skipped Model-Pair)")
        else:
            _warn("Tool-Pair self-check failed, falling back to Model-Pair")

    if chunk_mapping is None:
        chunk_mapping = _model_pair(client, text, anonymized_text)

    # Merge with existing mapping
    if existing_mapping:
        merged = merge_mappings(existing_mapping, chunk_mapping)
    else:
        merged = chunk_mapping

    return anonymized_text, merged


# ======================================================================
# Public entry point
# ======================================================================

def run_hide(
    client: HaSClient,
    text: str,
    types: List[str],
    existing_mapping: Optional[Dict[str, List[str]]] = None,
    max_chunk_tokens: int = DEFAULT_MAX_CHUNK_TOKENS,
    progress_label: Optional[str] = None,
    tool_pair: bool = True,
    context_window: int = DEFAULT_CONTEXT_PER_SLOT,
) -> Dict[str, Any]:
    """Anonymize text with automatic chunking and mapping accumulation.

    This is the main entry point for the hide command.
    Implements the full Phase 1 workflow from the HaS flowchart.

    Args:
        client: HaSClient connected to llama-server.
        text: Text to anonymize.
        types: Entity types to anonymize, e.g. ["人名", "地址"].
        existing_mapping: Optional pre-existing mapping for cross-document consistency.
        max_chunk_tokens: Maximum tokens per chunk.

    Returns:
        {
            "text": "anonymized text...",
            "mapping": {"<tag>": ["original_value"], ...},
            "chunks": N  # number of chunks processed (if > 1)
        }
    """
    if not text or not text.strip():
        return {"text": "", "mapping": existing_mapping or {}}

    accumulated_mapping = dict(existing_mapping) if existing_mapping else {}
    anonymized_parts: List[str] = []
    remaining_text = text
    chunk_count = 0

    while remaining_text:
        chunk_budget = _compute_chunk_budget(
            client.count_tokens,
            max_chunk_tokens,
            accumulated_mapping if accumulated_mapping else None,
            context_window=context_window,
        )
        chunk = take_chunk(
            remaining_text,
            client.count_tokens,
            chunk_budget,
            index=chunk_count,
        )
        if chunk is None:
            break

        next_remaining = remaining_text[len(chunk.text):]
        if chunk_count > 0 or next_remaining:
            prefix = f"{progress_label}: " if progress_label else ""
            if os.environ.get("HAS_TEXT_VERBOSE") == "1":
                print(
                    f"{prefix}Processing chunk {chunk_count + 1} "
                    f"({chunk.token_count} tokens, {len(chunk.text)} chars; "
                    f"text budget {chunk_budget})...",
                    file=sys.stderr,
                )

        # Retry with shrunk chunk on context overflow
        current_chunk_text = chunk.text
        current_budget = chunk_budget
        for attempt in range(_MAX_OVERFLOW_RETRIES + 1):
            try:
                anonymized_text, accumulated_mapping = _hide_single_chunk(
                    client,
                    current_chunk_text,
                    types,
                    existing_mapping=accumulated_mapping if accumulated_mapping else None,
                    tool_pair=tool_pair,
                    context_window=context_window,
                )
                break
            except ContextOverflowError:
                if attempt >= _MAX_OVERFLOW_RETRIES:
                    raise
                current_budget = int(current_budget * _RETRY_SHRINK_FACTOR)
                if current_budget < _MIN_CHUNK_TOKENS:
                    raise
                _warn(
                    f"Context overflow on chunk {chunk_count + 1}, "
                    f"retrying with reduced budget {current_budget}"
                )
                retry_chunk = take_chunk(
                    remaining_text,
                    client.count_tokens,
                    current_budget,
                    index=chunk_count,
                )
                if retry_chunk is None:
                    raise
                current_chunk_text = retry_chunk.text

        anonymized_parts.append(anonymized_text)
        remaining_text = remaining_text[len(current_chunk_text):]
        chunk_count += 1

    result = {
        "text": "".join(anonymized_parts),
        "mapping": accumulated_mapping,
    }

    if chunk_count > 1:
        result["chunks"] = chunk_count

    return result


def run_hide_batch(
    client: HaSClient,
    documents: List[HideDocument],
    types: List[str],
    existing_mapping: Optional[Dict[str, List[str]]] = None,
    max_chunk_tokens: int = DEFAULT_MAX_CHUNK_TOKENS,
    max_parallel_requests: int = DEFAULT_MAX_PARALLEL_REQUESTS,
    tool_pair: bool = True,
    context_window: int = DEFAULT_CONTEXT_PER_SLOT,
) -> Dict[str, Any]:
    """Anonymize multiple plaintext documents with independent per-file mappings."""
    if max_parallel_requests < 1:
        raise ValueError("max_parallel_requests must be >= 1")

    if not documents:
        return {"results": [], "count": 0}

    results: List[Optional[Dict[str, Any]]] = [None] * len(documents)

    def _process(index: int, document: HideDocument) -> Dict[str, Any]:
        hidden = run_hide(
            _clone_hide_client(client),
            document.text,
            types,
            existing_mapping=existing_mapping,
            max_chunk_tokens=max_chunk_tokens,
            progress_label=Path(document.source).name,
            tool_pair=tool_pair,
            context_window=context_window,
        )
        hidden["file"] = document.source
        return hidden

    if len(documents) == 1 or max_parallel_requests == 1:
        for index, document in enumerate(documents):
            results[index] = _process(index, document)
    else:
        max_workers = resolve_parallel_workers(len(documents), max_parallel_requests)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(_process, index, document): index
                for index, document in enumerate(documents)
            }
            try:
                for future in as_completed(futures):
                    index = futures[future]
                    results[index] = future.result()
            except BaseException:
                for future in futures:
                    future.cancel()
                raise

    materialized = [result for result in results if result is not None]
    return {"results": materialized, "count": len(materialized)}


# ======================================================================
# CLI handler
# ======================================================================


def cmd_hide(args: argparse.Namespace) -> None:
    """Execute the hide (anonymize) command."""
    from ..cli_utils import (
        FALLBACK_CONTEXT_PER_SLOT,
        absolute_path,
        collect_text_documents,
        fatal,
        load_mapping_file,
        output,
        parse_types,
        read_text,
        required_slots,
        resolve_single_output_path,
        write_text_output,
    )
    from ..client import DEFAULT_SERVER
    from ..mapping import save_mapping
    from ..server_runtime import DEFAULT_CONTEXT_PER_SLOT, acquire_server

    types = parse_types(args.type)
    dir_path = getattr(args, "dir", None)

    if dir_path and args.mapping:
        fatal(
            "invalid_mapping_usage",
            "hide --dir does not support --mapping; batch hide always writes per-file mappings.",
        )
    if dir_path and args.output:
        fatal(
            "invalid_output_usage",
            "hide --dir does not support --output; use --output-dir instead.",
        )
    if dir_path and args.mapping_output:
        fatal(
            "invalid_output_usage",
            "hide --dir does not support --mapping-output; use --mapping-dir instead.",
        )
    if not dir_path and args.output_dir:
        fatal(
            "invalid_output_usage",
            "hide without --dir does not support --output-dir; use --output instead.",
        )
    if not dir_path and args.mapping_dir:
        fatal(
            "invalid_output_usage",
            "hide without --dir does not support --mapping-dir; use --mapping-output instead.",
        )
    if not dir_path and not args.mapping_output:
        fatal(
            "missing_mapping_output",
            "Single-file hide requires --mapping-output so the mapping is not emitted inline.",
        )

    existing_mapping = None
    existing_mapping_path: Optional[Path] = None
    if args.mapping:
        existing_mapping = load_mapping_file(args.mapping)
        existing_mapping_path = Path(args.mapping)

    t0 = time.time()
    if dir_path:
        raw_documents, skipped = collect_text_documents(dir_path)
        documents = [
            HideDocument(source=item["file"], text=item["text"])
            for item in raw_documents
        ]
        _required = required_slots(
            estimate_hide_batch_request_count(documents),
            args.max_parallel_requests,
        )

        if documents and _required > 0:
            with acquire_server(
                DEFAULT_SERVER,
                required_slots=_required,
            ) as lease:
                client = lease.create_client()
                batch_result = run_hide_batch(
                    client,
                    documents,
                    types,
                    existing_mapping=existing_mapping,
                    max_chunk_tokens=args.max_chunk_tokens,
                    max_parallel_requests=args.max_parallel_requests,
                    tool_pair=args.tool_pair,
                )
        elif documents:
            batch_result = {
                "results": [
                    {
                        "file": document.source,
                        "text": document.text,
                        "mapping": dict(existing_mapping) if existing_mapping else {},
                    }
                    for document in documents
                ],
                "count": len(documents),
            }
        else:
            batch_result = {"results": [], "count": 0}

        output_dir = Path(args.output_dir or str(Path(dir_path) / ".has" / "anonymized"))
        mapping_dir = Path(args.mapping_dir or str(output_dir / "mappings"))
        manifest_results: List[Dict[str, Any]] = []

        for item in batch_result["results"]:
            source_path = Path(str(item["file"]))
            output_path = output_dir / source_path.name
            mapping_path = mapping_dir / f"{source_path.name}.mapping.json"
            if output_path.resolve() == source_path.resolve():
                fatal("refusing_overwrite", f"Refusing to overwrite source file: {source_path}")

            write_text_output(output_path, str(item["text"]))
            mapping_path.parent.mkdir(parents=True, exist_ok=True)
            save_mapping(item["mapping"], str(mapping_path))

            manifest_item: Dict[str, Any] = {
                "file": absolute_path(source_path),
                "output": absolute_path(output_path),
                "mapping_output": absolute_path(mapping_path),
            }
            if "chunks" in item:
                manifest_item["chunks"] = item["chunks"]
            manifest_results.append(manifest_item)

        result = {"results": manifest_results, "count": len(manifest_results)}
        if skipped:
            result["skipped"] = skipped
            result["skipped_count"] = len(skipped)
    else:
        source_path = Path(args.file) if args.file else None
        output_path = resolve_single_output_path(args.output, input_path=source_path)
        mapping_output_path = resolve_single_output_path(
            args.mapping_output,
            input_path=source_path,
            input_label="input file",
        )
        if mapping_output_path is None:
            fatal(
                "missing_mapping_output",
                "Single-file hide requires --mapping-output so the mapping is not emitted inline.",
            )
        if output_path is not None and output_path.resolve(strict=False) == mapping_output_path.resolve(strict=False):
            fatal(
                "invalid_output_usage",
                "hide output and mapping output must be different paths.",
            )
        if existing_mapping_path is not None:
            resolved_mapping_input = existing_mapping_path.resolve(strict=False)
            if output_path is not None and output_path.resolve(strict=False) == resolved_mapping_input:
                fatal(
                    "refusing_overwrite",
                    "--output must not overwrite the input --mapping file.",
                )
            if mapping_output_path.resolve(strict=False) == resolved_mapping_input:
                fatal(
                    "refusing_overwrite",
                    "--mapping-output must not overwrite the input --mapping file. "
                    "Use a different path for the updated mapping.",
                )

        text = read_text(args)
        if text.strip():
            context_per_slot = DEFAULT_CONTEXT_PER_SLOT
            for _attempt in range(2):
                try:
                    with acquire_server(
                        DEFAULT_SERVER,
                        required_slots=1,
                        context_per_slot=context_per_slot,
                    ) as lease:
                        client = lease.create_client()
                        result = run_hide(
                            client,
                            text,
                            types,
                            existing_mapping=existing_mapping,
                            max_chunk_tokens=args.max_chunk_tokens,
                            tool_pair=args.tool_pair,
                            context_window=context_per_slot,
                        )
                    break
                except RuntimeError as exc:
                    if (
                        context_per_slot < FALLBACK_CONTEXT_PER_SLOT
                        and "no longer leaves room" in str(exc)
                    ):
                        context_per_slot = FALLBACK_CONTEXT_PER_SLOT
                        if os.environ.get("HAS_TEXT_VERBOSE") == "1":
                            print(
                                f"Mapping overflow at {DEFAULT_CONTEXT_PER_SLOT} context; "
                                f"retrying with {FALLBACK_CONTEXT_PER_SLOT}...",
                                file=sys.stderr,
                            )
                        continue
                    raise
        else:
            result = {"text": "", "mapping": dict(existing_mapping) if existing_mapping else {}}

        mapping_output_path.parent.mkdir(parents=True, exist_ok=True)
        save_mapping(result["mapping"], str(mapping_output_path))
        if output_path is not None:
            write_text_output(output_path, str(result["text"]))
            single_result: Dict[str, Any] = {
                "output": absolute_path(output_path),
                "mapping_output": absolute_path(mapping_output_path),
            }
        else:
            single_result = {
                "text": str(result["text"]),
                "mapping_output": absolute_path(mapping_output_path),
            }
        if "chunks" in result:
            single_result["chunks"] = result["chunks"]
        result = single_result
    elapsed_ms = round((time.time() - t0) * 1000)
    output(
        "hide",
        result,
        timing=args.timing,
        elapsed_ms=elapsed_ms,
    )
