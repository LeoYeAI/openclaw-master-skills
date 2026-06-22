#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""seek command — Restore anonymized text (Phase 3 of HaS workflow).

Internal workflow:
    Check for tags → Language detection → Tool-Seek or Model-Seek
    → Self-check → Model-Seek fallback
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import os
from pathlib import Path
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..chunker import (
    DEFAULT_MAX_CHUNK_TOKENS,
    _FALLBACK_BOUNDARIES,
    _SENTENCE_BOUNDARIES,
)
from ..client import HaSClient
from ..lang import is_same_language
from ..mapping import (
    TAG_PATTERN,
    find_composite_entries,
    has_tags,
    normalize_mapping_dict,
    parse_json_tolerant,
)
from ..parallel import DEFAULT_MAX_PARALLEL_REQUESTS, resolve_parallel_workers
from ..prompts import build_seek_messages, build_split_messages




@dataclass(frozen=True)
class _KeyOccurrence:
    key: str
    start: int
    end: int


@dataclass(frozen=True)
class _SeekChunk:
    text: str
    index: int
    start_char: int
    end_char: int
    mapping: Dict[str, List[str]]
    needs_model: bool
    prompt_token_count: int


@dataclass(frozen=True)
class SeekDocument:
    """Plaintext input for batch restoration."""

    source: str
    text: str


def _warn(message: str) -> None:
    if os.environ.get("HAS_TEXT_VERBOSE") == "1":
        print(f"Warning: {message}", file=sys.stderr)


def _clone_seek_client(client: HaSClient) -> HaSClient:
    """Create a fresh client per worker to avoid sharing HTTP sessions."""
    client_cls = client.__class__
    try:
        return client_cls(client.base_url)
    except TypeError:
        return HaSClient(client.base_url)


# ======================================================================
# Tool-Seek: deterministic string replacement
# ======================================================================


def _tool_seek(text: str, mapping: Dict[str, List[str]]) -> str:
    """Restore text by replacing tags with original values.

    Uses the first value in each tag's value array.
    """
    restored = text
    # Replace longer composite tags first so unresolved composite mappings can
    # still restore correctly.
    for tag, values in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
        if values:
            restored = restored.replace(tag, str(values[0]))
    return restored


# ======================================================================
# Seek self-check
# ======================================================================


def _seek_self_check(restored_text: str) -> bool:
    """Check if the restored text still contains unreplaced tags.

    Returns True if no tags remain (success).
    """
    return not has_tags(restored_text)


def _should_try_tool_seek(
    text: str,
    mapping: Dict[str, List[str]],
    original_text: Optional[str] = None,
) -> bool:
    """Return whether deterministic seek is likely sufficient."""
    if original_text:
        return is_same_language(original_text, text)

    entity_sample = " ".join(val for vals in mapping.values() for val in vals[:2])
    if not entity_sample.strip():
        return True
    return is_same_language(entity_sample, text)


def restore_without_model(
    text: str,
    mapping: Dict[str, List[str]],
    original_text: Optional[str] = None,
) -> Optional[str]:
    """Restore text without llama-server when deterministic replacement succeeds."""
    if not has_tags(text):
        return text

    if not _should_try_tool_seek(text, mapping, original_text=original_text):
        return None

    restored = _tool_seek(text, mapping)
    if _seek_self_check(restored):
        return restored
    return None


def _normalize_seek_mapping(
    client: HaSClient,
    text: str,
    mapping: Dict[str, List[str]],
) -> Dict[str, List[str]]:
    """Split composite mappings that no longer appear literally in the text."""
    atomic, composite = find_composite_entries(mapping)
    if not composite:
        return mapping

    preserved = {key: values for key, values in composite.items() if key in text}
    unresolved = {key: values for key, values in composite.items() if key not in text}
    if not unresolved:
        return mapping

    messages = build_split_messages([{key: values} for key, values in unresolved.items()])
    raw_output = client.chat(messages)
    split_result = parse_json_tolerant(raw_output)

    try:
        if isinstance(split_result, dict):
            normalized_split = normalize_mapping_dict(split_result)
        elif isinstance(split_result, list):
            merged: Dict[str, Any] = {}
            for item in split_result:
                if not isinstance(item, dict):
                    raise ValueError("Model-Split returned a non-object entry")
                merged.update(item)
            normalized_split = normalize_mapping_dict(merged)
        else:
            raise ValueError("Model-Split did not return valid JSON")
    except ValueError as exc:
        _warn(
            "Model-Split failed while preparing seek mapping; "
            f"falling back to original composite mappings ({exc})"
        )
        return mapping

    merged_mapping: Dict[str, List[str]] = {}
    merged_mapping.update(atomic)
    merged_mapping.update(normalized_split)
    merged_mapping.update(preserved)

    for key, values in unresolved.items():
        if key not in merged_mapping:
            merged_mapping[key] = values

    return merged_mapping


def _find_key_occurrences(text: str, mapping: Dict[str, List[str]]) -> List[_KeyOccurrence]:
    occurrences: List[_KeyOccurrence] = []
    for key in mapping:
        start = 0
        while True:
            index = text.find(key, start)
            if index < 0:
                break
            occurrences.append(_KeyOccurrence(key=key, start=index, end=index + len(key)))
            start = index + 1
    occurrences.sort(key=lambda item: (item.start, -(item.end - item.start), item.key))
    return occurrences


def _has_uncovered_tags(text: str, occurrences: List[_KeyOccurrence]) -> bool:
    for match in TAG_PATTERN.finditer(text):
        tag_start = match.start()
        tag_end = match.end()
        if not any(item.start <= tag_start and item.end >= tag_end for item in occurrences):
            return True
    return False


def _is_safe_split(pos: int, occurrences: List[_KeyOccurrence]) -> bool:
    return all(not (item.start < pos < item.end) for item in occurrences)


def _local_mapping_for_prefix(
    mapping: Dict[str, List[str]],
    occurrences: List[_KeyOccurrence],
    end_pos: int,
) -> Dict[str, List[str]]:
    included = {item.key for item in occurrences if item.end <= end_pos}
    return {key: values for key, values in mapping.items() if key in included}


def _count_seek_prompt_tokens(
    count_tokens,
    text: str,
    mapping: Dict[str, List[str]],
) -> int:
    if not has_tags(text):
        return 0
    messages = build_seek_messages(mapping, text)
    return count_tokens(messages[0]["content"])


def _plan_seek_chunks_from_mapping(
    text: str,
    mapping: Dict[str, List[str]],
    count_tokens: Callable[[str], int],
    max_chunk_tokens: int,
) -> List[_SeekChunk]:
    occurrences = _find_key_occurrences(text, mapping)

    if _has_uncovered_tags(text, occurrences):
        prompt_tokens = _count_seek_prompt_tokens(count_tokens, text, mapping)
        if prompt_tokens <= max_chunk_tokens:
            return [
                _SeekChunk(
                    text=text,
                    index=0,
                    start_char=0,
                    end_char=len(text),
                    mapping=mapping,
                    needs_model=True,
                    prompt_token_count=prompt_tokens,
                )
            ]
        raise RuntimeError(
            "Cross-language seek could not be chunked safely because some tags are not "
            "covered by mapping keys. This usually means the translated text mutated a "
            "tag or still depends on unresolved composite mappings."
        )

    chunks: List[_SeekChunk] = []
    offset = 0
    index = 0

    while offset < len(text):
        remaining_text = text[offset:]
        remaining_occurrences = [
            _KeyOccurrence(
                key=item.key,
                start=item.start - offset,
                end=item.end - offset,
            )
            for item in occurrences
            if item.end > offset
        ]

        if not remaining_occurrences:
            chunks.append(
                _SeekChunk(
                    text=remaining_text,
                    index=index,
                    start_char=offset,
                    end_char=len(text),
                    mapping={},
                    needs_model=False,
                    prompt_token_count=0,
                )
            )
            break

        first_occurrence = remaining_occurrences[0]
        if first_occurrence.start > 0:
            passthrough = remaining_text[:first_occurrence.start]
            chunks.append(
                _SeekChunk(
                    text=passthrough,
                    index=index,
                    start_char=offset,
                    end_char=offset + len(passthrough),
                    mapping={},
                    needs_model=False,
                    prompt_token_count=0,
                )
            )
            offset += len(passthrough)
            index += 1
            continue

        chunk = _take_seek_chunk(
            remaining_text,
            mapping,
            remaining_occurrences,
            count_tokens,
            max_chunk_tokens,
            index=index,
            start_char=offset,
        )
        chunks.append(chunk)
        offset += len(chunk.text)
        index += 1

    return chunks


def _candidate_positions(text: str, occurrences: List[_KeyOccurrence], search_end: int) -> List[int]:
    positions = set()

    for pattern in (_SENTENCE_BOUNDARIES, _FALLBACK_BOUNDARIES):
        for match in pattern.finditer(text[:search_end]):
            positions.add(match.start())

    for item in occurrences:
        if 0 < item.start <= search_end:
            positions.add(item.start)
        if 0 < item.end <= search_end:
            positions.add(item.end)

    safe_positions = [
        pos
        for pos in positions
        if 0 < pos < len(text) and _is_safe_split(pos, occurrences)
    ]
    return sorted(safe_positions, reverse=True)


def _take_seek_chunk(
    text: str,
    mapping: Dict[str, List[str]],
    occurrences: List[_KeyOccurrence],
    count_tokens,
    max_tokens: int,
    *,
    index: int,
    start_char: int,
) -> _SeekChunk:
    """Take the next seek chunk without splitting mapping keys across boundaries."""
    if not text:
        raise RuntimeError("Cannot plan an empty seek chunk")

    full_mapping = _local_mapping_for_prefix(mapping, occurrences, len(text))
    full_prompt_tokens = _count_seek_prompt_tokens(count_tokens, text, full_mapping)
    if full_prompt_tokens <= max_tokens:
        return _SeekChunk(
            text=text,
            index=index,
            start_char=start_char,
            end_char=start_char + len(text),
            mapping=full_mapping,
            needs_model=has_tags(text),
            prompt_token_count=full_prompt_tokens,
        )

    chars_per_token = len(text) / max(full_prompt_tokens, 1)
    estimated_chars = max(1, int(max_tokens * chars_per_token))
    search_end = min(estimated_chars + 50, len(text))

    for split_pos in _candidate_positions(text, occurrences, search_end):
        local_mapping = _local_mapping_for_prefix(mapping, occurrences, split_pos)
        chunk_text = text[:split_pos]
        prompt_tokens = _count_seek_prompt_tokens(count_tokens, chunk_text, local_mapping)
        if prompt_tokens <= max_tokens:
            return _SeekChunk(
                text=chunk_text,
                index=index,
                start_char=start_char,
                end_char=start_char + split_pos,
                mapping=local_mapping,
                needs_model=has_tags(chunk_text),
                prompt_token_count=prompt_tokens,
            )

    hard_cut = min(estimated_chars, len(text) - 1)
    while hard_cut > 0 and not _is_safe_split(hard_cut, occurrences):
        hard_cut -= 1

    if hard_cut > 0:
        local_mapping = _local_mapping_for_prefix(mapping, occurrences, hard_cut)
        chunk_text = text[:hard_cut]
        prompt_tokens = _count_seek_prompt_tokens(count_tokens, chunk_text, local_mapping)
        if prompt_tokens <= max_tokens:
            return _SeekChunk(
                text=chunk_text,
                index=index,
                start_char=start_char,
                end_char=start_char + hard_cut,
                mapping=local_mapping,
                needs_model=has_tags(chunk_text),
                prompt_token_count=prompt_tokens,
            )

    first_complete = min((item.end for item in occurrences), default=0)
    if first_complete > 0:
        local_mapping = _local_mapping_for_prefix(mapping, occurrences, first_complete)
        chunk_text = text[:first_complete]
        prompt_tokens = _count_seek_prompt_tokens(count_tokens, chunk_text, local_mapping)
        if prompt_tokens <= max_tokens:
            return _SeekChunk(
                text=chunk_text,
                index=index,
                start_char=start_char,
                end_char=start_char + first_complete,
                mapping=local_mapping,
                needs_model=has_tags(chunk_text),
                prompt_token_count=prompt_tokens,
            )

    raise RuntimeError(
        "A single seek chunk cannot fit in the model budget, even after splitting at "
        "safe key boundaries. Increase --max-chunk-tokens or reduce the mapping size."
    )


def _plan_seek_chunks(
    client: HaSClient,
    text: str,
    mapping: Dict[str, List[str]],
    max_chunk_tokens: int,
) -> List[_SeekChunk]:
    normalized_mapping = _normalize_seek_mapping(client, text, mapping)
    return _plan_seek_chunks_from_mapping(
        text,
        normalized_mapping,
        client.count_tokens,
        max_chunk_tokens,
    )


def _run_model_seek_chunk(
    client: HaSClient,
    text: str,
    mapping: Dict[str, List[str]],
) -> str:
    for attempt in range(2):
        messages = build_seek_messages(mapping, text)
        restored = client.chat(messages)

        if has_tags(restored) and mapping:
            restored = _tool_seek(restored, mapping)

        if _seek_self_check(restored):
            return restored

        if attempt == 0:
            _warn("Model-Seek left unresolved tags; retrying once with the original chunk")

    raise RuntimeError("Model-Seek left unresolved tags after one retry")


def _execute_seek_chunks(
    client: HaSClient,
    chunks: List[_SeekChunk],
    max_parallel_requests: int = DEFAULT_MAX_PARALLEL_REQUESTS,
) -> str:
    outputs = [""] * len(chunks)
    model_chunks = [chunk for chunk in chunks if chunk.needs_model]

    if not model_chunks:
        return "".join(chunk.text for chunk in chunks)

    can_parallelize = isinstance(client, HaSClient) and len(model_chunks) > 1
    max_workers = resolve_parallel_workers(len(model_chunks), max_parallel_requests)

    if can_parallelize and max_workers > 1:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                (
                    chunk.index,
                    executor.submit(
                        _run_model_seek_chunk,
                        _clone_seek_client(client),
                        chunk.text,
                        chunk.mapping,
                    ),
                )
                for chunk in model_chunks
            ]
            try:
                for index, future in futures:
                    outputs[index] = future.result()
            except BaseException:
                for _, future in futures:
                    future.cancel()
                raise
    else:
        for chunk in model_chunks:
            outputs[chunk.index] = _run_model_seek_chunk(client, chunk.text, chunk.mapping)

    for chunk in chunks:
        if not chunk.needs_model:
            outputs[chunk.index] = chunk.text

    return "".join(outputs)


def estimate_seek_model_request_count(
    text: str,
    mapping: Dict[str, List[str]],
    max_chunk_tokens: int = DEFAULT_MAX_CHUNK_TOKENS,
    *,
    count_tokens: Callable[[str], int],
    original_text: Optional[str] = None,
) -> int:
    """Estimate how many model-backed seek requests a text will need."""
    restored = restore_without_model(text, mapping, original_text=original_text)
    if restored is not None or not has_tags(text):
        return 0

    chunks = _plan_seek_chunks_from_mapping(
        text,
        mapping,
        count_tokens,
        max_chunk_tokens,
    )
    return sum(1 for chunk in chunks if chunk.needs_model)


def estimate_seek_batch_model_request_count(
    documents: List[SeekDocument],
    mapping: Dict[str, List[str]],
    max_chunk_tokens: int = DEFAULT_MAX_CHUNK_TOKENS,
    *,
    count_tokens: Callable[[str], int],
) -> int:
    """Estimate total model-backed seek requests across a batch."""
    return sum(
        estimate_seek_model_request_count(
            document.text,
            mapping,
            max_chunk_tokens=max_chunk_tokens,
            count_tokens=count_tokens,
        )
        for document in documents
    )


def run_seek_batch(
    client: HaSClient,
    documents: List[SeekDocument],
    mapping: Dict[str, List[str]],
    max_chunk_tokens: int = DEFAULT_MAX_CHUNK_TOKENS,
    max_parallel_requests: int = DEFAULT_MAX_PARALLEL_REQUESTS,
) -> Dict[str, Any]:
    """Restore multiple texts with a shared global pool for model-backed chunks."""
    if max_parallel_requests < 1:
        raise ValueError("max_parallel_requests must be >= 1")

    if not documents:
        return {"results": [], "count": 0}

    chunk_plans: List[List[_SeekChunk]] = []
    outputs: List[List[str]] = []
    tasks: List[Tuple[int, _SeekChunk]] = []

    for document_index, document in enumerate(documents):
        chunks = _plan_seek_chunks(client, document.text, mapping, max_chunk_tokens)
        chunk_plans.append(chunks)
        outputs.append([""] * len(chunks))
        for chunk in chunks:
            if chunk.needs_model:
                tasks.append((document_index, chunk))

    can_parallelize = isinstance(client, HaSClient) and len(tasks) > 1
    max_workers = resolve_parallel_workers(len(tasks), max_parallel_requests) if tasks else 0

    if can_parallelize and max_workers > 1:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                (
                    document_index,
                    chunk.index,
                    executor.submit(
                        _run_model_seek_chunk,
                        _clone_seek_client(client),
                        chunk.text,
                        chunk.mapping,
                    ),
                )
                for document_index, chunk in tasks
            ]
            try:
                for document_index, chunk_index, future in futures:
                    outputs[document_index][chunk_index] = future.result()
            except BaseException:
                for _, _, future in futures:
                    future.cancel()
                raise
    else:
        for document_index, chunk in tasks:
            outputs[document_index][chunk.index] = _run_model_seek_chunk(
                client,
                chunk.text,
                chunk.mapping,
            )

    results: List[Dict[str, Any]] = []
    for document_index, document in enumerate(documents):
        chunks = chunk_plans[document_index]
        for chunk in chunks:
            if not chunk.needs_model:
                outputs[document_index][chunk.index] = chunk.text

        restored_text = "".join(outputs[document_index])
        result: Dict[str, Any] = {"file": document.source, "text": restored_text}
        if len(chunks) > 1:
            result["chunks"] = len(chunks)
        results.append(result)

    return {"results": results, "count": len(results)}


# ======================================================================
# Public entry point
# ======================================================================


def run_seek(
    client: HaSClient,
    text: str,
    mapping: Dict[str, List[str]],
    original_text: Optional[str] = None,
    max_chunk_tokens: int = DEFAULT_MAX_CHUNK_TOKENS,
    max_parallel_requests: int = DEFAULT_MAX_PARALLEL_REQUESTS,
) -> Dict[str, Any]:
    """Restore anonymized text to its original form.

    Implements the Phase 3 workflow:
    1. Check if text contains tags
    2. If same language → Tool-Seek (deterministic) → self-check
    3. If different language or self-check fails → Model-Seek (model-based)

    Language detection is automatic: compares the language of the input text
    against the language of the mapping values (which represent the original
    entities). If they differ (e.g., text was translated), Model-Seek is used.

    Args:
        client: HaSClient connected to llama-server.
        text: Text containing anonymized tags to restore.
        mapping: Mapping dictionary {tag: [original_values]}.
        original_text: Optional original text for language comparison.
                       If not provided, uses mapping values for detection.
        max_chunk_tokens: Maximum tokens per model-backed seek chunk.
        max_parallel_requests: Maximum model-backed seek chunks to run in parallel.

    Returns:
        {"text": "restored original text..."}
    """
    if max_parallel_requests < 1:
        raise ValueError("max_parallel_requests must be >= 1")

    restored = restore_without_model(text, mapping, original_text=original_text)
    if restored is not None:
        return {"text": restored}

    if not has_tags(text):
        return {"text": text}

    if _should_try_tool_seek(text, mapping, original_text=original_text):
        if os.environ.get("HAS_TEXT_VERBOSE") == "1":
            print(
                "Tool-Seek self-check failed, falling back to Model-Seek...",
                file=sys.stderr,
            )

    chunks = _plan_seek_chunks(client, text, mapping, max_chunk_tokens)
    restored_text = _execute_seek_chunks(
        client,
        chunks,
        max_parallel_requests=max_parallel_requests,
    )
    if not _seek_self_check(restored_text):
        raise RuntimeError("Seek output still contains unresolved tags after model retry")
    result = {"text": restored_text}
    if len(chunks) > 1:
        result["chunks"] = len(chunks)
    return result


# ======================================================================
# CLI handler
# ======================================================================


def cmd_restore(args: argparse.Namespace) -> None:
    """Execute the restore command."""
    from ..cli_utils import (
        absolute_path,
        collect_text_documents,
        default_restore_output_dir,
        default_seek_mapping_dir,
        estimate_tokens_for_planning,
        fatal,
        load_mapping_file,
        output,
        read_text,
        required_slots,
        resolve_single_output_path,
        seek_mapping_path,
        write_text_output,
    )
    from ..client import DEFAULT_SERVER
    from ..mapping import has_tags, load_mapping
    from ..server_runtime import acquire_server

    dir_path = getattr(args, "dir", None)

    t0 = time.time()
    if dir_path:
        if args.mapping:
            fatal(
                "invalid_mapping_usage",
                "restore --dir does not support --mapping; use per-file mappings under <dir>/mappings or --mapping-dir.",
            )
        if args.output:
            fatal(
                "invalid_output_usage",
                "restore --dir does not support --output; use --output-dir instead.",
            )

        raw_documents, skipped = collect_text_documents(dir_path)
        documents = [
            SeekDocument(source=item["file"], text=item["text"])
            for item in raw_documents
        ]
        mapping_dir_arg = getattr(args, "mapping_dir", None)
        mapping_dir = Path(mapping_dir_arg) if mapping_dir_arg else default_seek_mapping_dir(dir_path)

        restored_results: List[Optional[Dict[str, Any]]] = [None] * len(documents)
        pending_documents: List[tuple[int, SeekDocument, Dict[str, List[str]]]] = []
        missing_mappings: List[str] = []

        for index, document in enumerate(documents):
            source_path = Path(document.source)
            document_mapping: Optional[Dict[str, List[str]]] = None

            per_file_mapping_path = seek_mapping_path(mapping_dir, source_path)
            if per_file_mapping_path.is_file():
                document_mapping = load_mapping(str(per_file_mapping_path))
            elif has_tags(document.text):
                missing_mappings.append(str(per_file_mapping_path))
                continue

            if document_mapping is None:
                if has_tags(document.text):
                    fatal(
                        "missing_mapping",
                        "Batch restore requires per-file mappings under "
                        f"{mapping_dir} for files that still contain anonymized tags."
                    )

                restored_results[index] = {"file": document.source, "text": document.text}
                continue

            restored = restore_without_model(document.text, document_mapping)
            if restored is not None:
                restored_results[index] = {"file": document.source, "text": restored}
            else:
                pending_documents.append((index, document, document_mapping))

        if missing_mappings:
            fatal(
                "missing_mapping",
                "Missing per-file mapping JSON for batch restore: "
                + ", ".join(sorted(missing_mappings))
            )

        if pending_documents:
            request_count = 0
            for _, document, document_mapping in pending_documents:
                try:
                    request_count += estimate_seek_model_request_count(
                        document.text,
                        document_mapping,
                        max_chunk_tokens=args.max_chunk_tokens,
                        count_tokens=estimate_tokens_for_planning,
                    )
                except RuntimeError:
                    request_count += 1

            with acquire_server(
                DEFAULT_SERVER,
                required_slots=required_slots(
                    max(request_count, 1),
                    args.max_parallel_requests,
                ),
            ) as lease:
                client = lease.create_client()
                for index, document, document_mapping in pending_documents:
                    item = run_seek(
                        client,
                        document.text,
                        document_mapping,
                        max_chunk_tokens=args.max_chunk_tokens,
                        max_parallel_requests=args.max_parallel_requests,
                    )
                    item["file"] = document.source
                    restored_results[index] = item

        output_dir_path = Path(args.output_dir or str(default_restore_output_dir(dir_path)))
        manifest_results: List[Dict[str, Any]] = []
        for item in restored_results:
            if item is None:
                continue
            source_path = Path(item["file"])
            output_path = output_dir_path / source_path.name
            if output_path.resolve() == source_path.resolve():
                fatal("refusing_overwrite", f"Refusing to overwrite source file: {source_path}")
            write_text_output(output_path, str(item["text"]))

            manifest_item: Dict[str, Any] = {
                "file": absolute_path(source_path),
                "output": absolute_path(output_path),
            }
            if "chunks" in item:
                manifest_item["chunks"] = item["chunks"]
            manifest_results.append(manifest_item)

        result = {"results": manifest_results, "count": len(manifest_results)}
        if skipped:
            result["skipped"] = skipped
            result["skipped_count"] = len(skipped)
    else:
        if args.mapping_dir:
            fatal(
                "invalid_output_usage",
                "restore without --dir does not support --mapping-dir.",
            )
        if args.output_dir:
            fatal(
                "invalid_output_usage",
                "restore without --dir does not support --output-dir; use --output instead.",
            )
        if not args.mapping:
            fatal("missing_mapping", "restore requires --mapping in single-file mode.")

        mapping_path = Path(args.mapping)
        mapping = load_mapping_file(args.mapping)
        source_path = Path(args.file) if args.file else None
        output_path = resolve_single_output_path(args.output, input_path=source_path)
        if output_path is not None and output_path.resolve(strict=False) == mapping_path.resolve(strict=False):
            fatal(
                "invalid_output_usage",
                "restore output must be different from the mapping file.",
            )
        text = read_text(args)
        restored = restore_without_model(text, mapping)
        if restored is not None:
            result = {"text": restored}
        else:
            try:
                request_count = estimate_seek_model_request_count(
                    text,
                    mapping,
                    max_chunk_tokens=args.max_chunk_tokens,
                    count_tokens=estimate_tokens_for_planning,
                )
            except RuntimeError:
                request_count = 1

            with acquire_server(
                DEFAULT_SERVER,
                required_slots=required_slots(request_count, args.max_parallel_requests),
            ) as lease:
                client = lease.create_client()
                result = run_seek(
                    client,
                    text,
                    mapping,
                    max_chunk_tokens=args.max_chunk_tokens,
                    max_parallel_requests=args.max_parallel_requests,
                )
        if output_path is not None:
            write_text_output(output_path, str(result["text"]))
            single_result: Dict[str, Any] = {"output": absolute_path(output_path)}
            if "chunks" in result:
                single_result["chunks"] = result["chunks"]
            result = single_result
    elapsed_ms = round((time.time() - t0) * 1000)

    output(
        "restore",
        result,
        timing=args.timing,
        elapsed_ms=elapsed_ms,
    )
