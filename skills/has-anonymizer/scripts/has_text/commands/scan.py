#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan command — Identify sensitive entities in text (NER only, no anonymization)."""

from __future__ import annotations

import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from ..chunker import chunk_text
from ..client import HaSClient
from ..mapping import parse_json_tolerant
from ..parallel import DEFAULT_MAX_PARALLEL_REQUESTS, resolve_parallel_workers
from ..prompts import build_ner_messages
from ..validation import normalize_entity_map

# scan only produces a small JSON entity list (no full-text rewrite),
# so chunks can be larger than the 3000 default used by hide/seek.
DEFAULT_SCAN_MAX_CHUNK_TOKENS = 5000


@dataclass(frozen=True)
class ScanDocument:
    """Plaintext input for batch scanning."""

    source: str
    text: str


@dataclass(frozen=True)
class _ScanTask:
    document_index: int
    chunk_index: int
    text: str


def _scan_single_chunk(
    client: HaSClient,
    chunk_text_str: str,
    types: List[str],
    chunk_index: int,
) -> Dict[str, List[str]]:
    """Run NER for a single chunk."""
    messages = build_ner_messages(chunk_text_str, types)
    raw_output = client.chat(messages)
    return normalize_entity_map(
        parse_json_tolerant(raw_output),
        context=f"NER output for chunk {chunk_index + 1}",
    )


def _clone_scan_client(client: HaSClient) -> HaSClient:
    """Create a fresh client per worker to avoid sharing HTTP sessions."""
    client_cls = client.__class__
    try:
        return client_cls(client.base_url)
    except TypeError:
        return HaSClient(client.base_url)


def _merge_entities(chunk_results: List[Dict[str, List[str]]]) -> Dict[str, List[str]]:
    """Merge chunk results while preserving the first-seen order."""
    merged_entities: Dict[str, List[str]] = {}

    for ner_result in chunk_results:
        for entity_type, entities in ner_result.items():
            if entity_type not in merged_entities:
                merged_entities[entity_type] = []
            for entity in entities:
                entity_str = str(entity).strip()
                if entity_str and entity_str not in merged_entities[entity_type]:
                    merged_entities[entity_type].append(entity_str)

    return merged_entities


def estimate_scan_request_count(
    text: str,
    max_chunk_tokens: int = DEFAULT_SCAN_MAX_CHUNK_TOKENS,
    *,
    count_tokens: Callable[[str], int],
) -> int:
    """Estimate how many model requests scan will issue for one text."""
    if not text or not text.strip():
        return 0
    return len(chunk_text(text, count_tokens, max_chunk_tokens))


def estimate_scan_batch_request_count(
    documents: List[ScanDocument],
    max_chunk_tokens: int = DEFAULT_SCAN_MAX_CHUNK_TOKENS,
    *,
    count_tokens: Callable[[str], int],
) -> int:
    """Estimate total scan requests across a batch of documents."""
    return sum(
        estimate_scan_request_count(
            document.text,
            max_chunk_tokens=max_chunk_tokens,
            count_tokens=count_tokens,
        )
        for document in documents
    )


def run_scan(
    client: HaSClient,
    text: str,
    types: List[str],
    max_chunk_tokens: int = DEFAULT_SCAN_MAX_CHUNK_TOKENS,
    max_parallel_requests: int = DEFAULT_MAX_PARALLEL_REQUESTS,
) -> Dict[str, List[str]]:
    """Scan text for sensitive entities.

    For short text, runs a single NER call.
    For long text, chunks and merges NER results.

    Returns:
        {"entities": {"人名": ["张三", "李四"], "地址": ["北京"], ...}}
    """
    if max_parallel_requests < 1:
        raise ValueError("max_parallel_requests must be >= 1")

    chunks = chunk_text(text, client.count_tokens, max_chunk_tokens)
    if not chunks:
        return {"entities": {}}

    if len(chunks) == 1 or max_parallel_requests == 1:
        chunk_results = [
            _scan_single_chunk(client, chunk.text, types, chunk.index)
            for chunk in chunks
        ]
        return {"entities": _merge_entities(chunk_results)}

    max_workers = resolve_parallel_workers(len(chunks), max_parallel_requests)
    chunk_results: List[Optional[Dict[str, List[str]]]] = [None] * len(chunks)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _scan_single_chunk,
                _clone_scan_client(client),
                chunk.text,
                types,
                chunk.index,
            ): chunk.index
            for chunk in chunks
        }

        try:
            for future in as_completed(futures):
                chunk_index = futures[future]
                chunk_results[chunk_index] = future.result()
        except BaseException:
            for future in futures:
                future.cancel()
            raise

    # Merge in original chunk order so first-seen semantics remain stable.
    return {"entities": _merge_entities([result for result in chunk_results if result is not None])}


def run_scan_batch(
    client: HaSClient,
    documents: List[ScanDocument],
    types: List[str],
    max_chunk_tokens: int = DEFAULT_SCAN_MAX_CHUNK_TOKENS,
    max_parallel_requests: int = DEFAULT_MAX_PARALLEL_REQUESTS,
) -> Dict[str, Any]:
    """Scan multiple plaintext documents with a shared global request pool."""
    if max_parallel_requests < 1:
        raise ValueError("max_parallel_requests must be >= 1")

    if not documents:
        return {"results": [], "count": 0, "summary": {}}

    chunk_results: List[List[Optional[Dict[str, List[str]]]]] = []
    tasks: List[_ScanTask] = []

    for document_index, document in enumerate(documents):
        chunks = chunk_text(document.text, client.count_tokens, max_chunk_tokens)
        doc_results: List[Optional[Dict[str, List[str]]]] = [None] * len(chunks)
        chunk_results.append(doc_results)
        for chunk in chunks:
            tasks.append(
                _ScanTask(
                    document_index=document_index,
                    chunk_index=chunk.index,
                    text=chunk.text,
                )
            )

    if len(tasks) == 1 or max_parallel_requests == 1:
        for task in tasks:
            chunk_results[task.document_index][task.chunk_index] = _scan_single_chunk(
                client,
                task.text,
                types,
                task.chunk_index,
            )
    elif tasks:
        max_workers = resolve_parallel_workers(len(tasks), max_parallel_requests)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    _scan_single_chunk,
                    _clone_scan_client(client),
                    task.text,
                    types,
                    task.chunk_index,
                ): task
                for task in tasks
            }

            try:
                for future in as_completed(futures):
                    task = futures[future]
                    chunk_results[task.document_index][task.chunk_index] = future.result()
            except BaseException:
                for future in futures:
                    future.cancel()
                raise

    results: List[Dict[str, Any]] = []
    summary: Dict[str, int] = {}

    for document_index, document in enumerate(documents):
        entities = _merge_entities(
            [result for result in chunk_results[document_index] if result is not None]
        )
        results.append({"file": document.source, "entities": entities})
        for entity_type, values in entities.items():
            summary[entity_type] = summary.get(entity_type, 0) + len(values)

    return {
        "results": results,
        "count": len(results),
        "summary": summary,
    }


# ======================================================================
# CLI handler
# ======================================================================


def cmd_scan(args: argparse.Namespace) -> None:
    """Execute the scan (NER) command."""
    from ..cli_utils import (
        collect_text_documents,
        estimate_tokens_for_planning,
        output,
        parse_types,
        read_text,
        required_slots,
    )
    from ..client import DEFAULT_SERVER
    from ..server_runtime import acquire_server

    types = parse_types(args.type)
    dir_path = getattr(args, "dir", None)

    t0 = time.time()
    if dir_path:
        raw_documents, skipped = collect_text_documents(dir_path)
        documents = [
            ScanDocument(source=item["file"], text=item["text"])
            for item in raw_documents
        ]
        request_count = estimate_scan_batch_request_count(
            documents,
            max_chunk_tokens=args.max_chunk_tokens,
            count_tokens=estimate_tokens_for_planning,
        )

        if documents and request_count > 0:
            with acquire_server(
                DEFAULT_SERVER,
                required_slots=required_slots(request_count, args.max_parallel_requests),
            ) as lease:
                client = lease.create_client()
                result = run_scan_batch(
                    client,
                    documents,
                    types,
                    max_chunk_tokens=args.max_chunk_tokens,
                    max_parallel_requests=args.max_parallel_requests,
                )
        elif documents:
            result = {
                "results": [
                    {"file": document.source, "entities": {}}
                    for document in documents
                ],
                "count": len(documents),
                "summary": {},
            }
        else:
            result = {"results": [], "count": 0, "summary": {}}

        if skipped:
            result["skipped"] = skipped
            result["skipped_count"] = len(skipped)
    else:
        text = read_text(args)
        request_count = estimate_scan_request_count(
            text,
            max_chunk_tokens=args.max_chunk_tokens,
            count_tokens=estimate_tokens_for_planning,
        )
        if request_count > 0:
            with acquire_server(
                DEFAULT_SERVER,
                required_slots=required_slots(request_count, args.max_parallel_requests),
            ) as lease:
                client = lease.create_client()
                result = run_scan(
                    client,
                    text,
                    types,
                    max_chunk_tokens=args.max_chunk_tokens,
                    max_parallel_requests=args.max_parallel_requests,
                )
        else:
            result = {"entities": {}}
    elapsed_ms = round((time.time() - t0) * 1000)

    output("scan", result, timing=args.timing, elapsed_ms=elapsed_ms)

