#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Standalone pair mapping helper.

This script contains a self-sufficient implementation of the pair generation
algorithm used by the TagID batch pipeline.  It does not rely on the rest of the
project package and can therefore be executed independently via
``python share/pair_core.py``.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union

# ---------------------------------------------------------------------------
# Token models and constants (mirrors tagid.tag_mapping)
# ---------------------------------------------------------------------------

TAG_PATTERN = re.compile(r"<([^<>\[\]]+)\[(\d+)\]\.([^<>\[\].]+)\.([^<>\[\].]+)>")
CONJ_JUNK_SET: Set[str] = {"及", "和", "与", "到", "的"}


@dataclass(frozen=True)
class TagToken:
    text: str

    def __str__(self) -> str:
        return self.text


@dataclass(frozen=True)
class SpanToken:
    text: str
    kind: str

    def __str__(self) -> str:
        return self.text


Token = Union[str, TagToken, SpanToken]


# ---------------------------------------------------------------------------
# Text normalisation and tokenisation helpers
# ---------------------------------------------------------------------------


def normalize_plain_text(s: str) -> str:
    if s is None:
        return s
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("\ufeff", "")
    s = s.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "")
    s = unicodedata.normalize("NFC", s)
    return s


def _tokenize_plain_text_with_spans(s: str, *, include_quote_delims: bool = True) -> List[Token]:
    s = normalize_plain_text(s) or ""

    email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,24}")
    url_re = re.compile(r"https?://[^\s\u3000<>\"'）】>)\u4E00-\u9FFF]+", re.IGNORECASE)
    trail_puncts = set(list(".,!?:;)]}")) | set(list("，。！？：；）】】、》”’"))

    tokens: List[Token] = []
    i = 0
    n = len(s)

    def append_span(text: str, kind: str) -> None:
        if text:
            tokens.append(SpanToken(text=text, kind=kind))

    while i < n:
        ch = s[i]

        m = email_re.match(s, i)
        if m:
            span = m.group(0)
            end = m.end()
            while span and span[-1] in trail_puncts:
                end -= 1
                span = span[:-1]
            if span:
                append_span(span, 'email')
                i = end
                continue

        m = url_re.match(s, i)
        if m:
            span = m.group(0)
            end = m.end()
            while span and span[-1] in trail_puncts:
                end -= 1
                span = span[:-1]
            if span:
                append_span(span, 'url')
                i = end
                continue

        if ch == '《':
            j = s.find('》', i + 1)
            if j != -1 and (j - i) <= 200:
                if include_quote_delims:
                    append_span(s[i:j + 1], 'quote')
                else:
                    tokens.append('《')
                    inner = s[i + 1:j]
                    if inner:
                        append_span(inner, 'quote')
                    tokens.append('》')
                i = j + 1
                continue

        tokens.append(ch)
        i += 1

    return tokens


def tokenize_input_text(s: str, *, include_quote_delims: bool = True) -> List[Token]:
    return _tokenize_plain_text_with_spans(s, include_quote_delims=include_quote_delims)


def tokenize_hide_with_tags(hide: str, *, include_quote_delims: bool = True) -> List[Token]:
    tokens: List[Token] = []
    last = 0
    for m in TAG_PATTERN.finditer(hide):
        start, end = m.span()
        if start > last:
            plain = hide[last:start]
            tokens.extend(_tokenize_plain_text_with_spans(plain, include_quote_delims=include_quote_delims))
        tokens.append(TagToken(m.group(0)))
        last = end
    if last < len(hide):
        tail = hide[last:]
        tokens.extend(_tokenize_plain_text_with_spans(tail, include_quote_delims=include_quote_delims))
    return tokens


def render_tokens(tokens: Sequence[Token]) -> str:
    out_parts: List[str] = []
    for t in tokens:
        out_parts.append(str(t))
    return "".join(out_parts)


# ---------------------------------------------------------------------------
# Diff-based entity/tag pairing helpers
# ---------------------------------------------------------------------------


def _is_whitespace_str(t: Token) -> bool:
    return isinstance(t, str) and t.isspace()


def _find_adjacent_composite_group(insert_tokens: Sequence[Token], *, allowed_mid_tokens: Optional[Set[str]] = None) -> Optional[Tuple[int, int]]:
    n = len(insert_tokens)
    allowed_mid_tokens = allowed_mid_tokens or set()
    i = 0
    while i < n and not isinstance(insert_tokens[i], TagToken):
        i += 1
    if i >= n:
        return None
    start = i
    has_tag = False
    while i < n:
        t = insert_tokens[i]
        if isinstance(t, TagToken):
            has_tag = True
            i += 1
            continue
        if _is_whitespace_str(t):
            i += 1
            continue
        if isinstance(t, str) and t in allowed_mid_tokens:
            i += 1
            continue
        break
    end = i
    if not has_tag:
        return None
    return (start, end)


def extract_entity_tag_pairs(
    src_tokens: Sequence[Token],
    dst_tokens: Sequence[Token],
    *,
    isjunk=None,
    allowed_mid_tokens: Optional[Set[str]] = None,
) -> Tuple[List[Tuple[str, str]], Set[str]]:
    opcodes = difflib.SequenceMatcher(isjunk, a=src_tokens, b=dst_tokens, autojunk=False).get_opcodes()
    pairs: List[Tuple[str, str]] = []
    used_mid_tokens: Set[str] = set()

    def render_range(tokens: Sequence[Token], start: int, end: int) -> str:
        return render_tokens(tokens[start:end])

    def lcp(a: str, b: str) -> str:
        n = min(len(a), len(b))
        k = 0
        while k < n and a[k] == b[k]:
            k += 1
        return a[:k]

    def lcsuf(a: str, b: str) -> str:
        na, nb = len(a), len(b)
        k = 0
        while k < na and k < nb and a[na - 1 - k] == b[nb - 1 - k]:
            k += 1
        return a[na - k:] if k > 0 else ""

    def _inside_quote(tokens: Sequence[Token], start_idx: int, end_idx: int) -> bool:
        li = start_idx - 1
        left_q = -1
        while li >= 0:
            t = tokens[li]
            if isinstance(t, str) and t == '《':
                left_q = li
                break
            if isinstance(t, str) and t == '》':
                break
            li -= 1
        if left_q == -1:
            return False
        ri = end_idx
        right_q = -1
        n2 = len(tokens)
        while ri < n2:
            t = tokens[ri]
            if isinstance(t, str) and t == '》':
                right_q = ri
                break
            if isinstance(t, str) and t == '《':
                break
            ri += 1
        return right_q != -1 and left_q < start_idx and end_idx <= right_q

    def _render_skip_tags(tokens: Sequence[Token]) -> str:
        parts: List[str] = []
        for t in tokens:
            if isinstance(t, TagToken):
                continue
            parts.append(str(t))
        return "".join(parts)

    def _first_plain_prefix(tokens: Sequence[Token]) -> str:
        buf: List[str] = []
        i = 0
        n = len(tokens)
        while i < n and isinstance(tokens[i], str) and tokens[i].isspace():
            i += 1
        while i < n:
            t = tokens[i]
            if isinstance(t, TagToken):
                break
            s = str(t)
            if s and not s.isspace():
                buf.append(s)
                i += 1
                continue
            if s.isspace():
                buf.append(s)
                i += 1
                continue
            i += 1
        return "".join(buf)

    def _suffix_overlap_with_right_prefix(a: str, right: str) -> int:
        a = a or ''
        right = right or ''
        max_k = min(len(a), len(right))
        k = max_k
        while k > 0:
            if a.endswith(right[:k]):
                return k
            k -= 1
        return 0

    for idx, (tag, i1, i2, j1, j2) in enumerate(opcodes):
        if tag == "replace":
            del_tokens = src_tokens[i1:i2]
            ins_tokens = dst_tokens[j1:j2]
            grp = _find_adjacent_composite_group(ins_tokens, allowed_mid_tokens=allowed_mid_tokens)
            if grp is None:
                continue
            entity = render_range(del_tokens, 0, len(del_tokens))
            g0, g1 = grp
            comp = render_range(ins_tokens, g0, g1)
            left_ctx = render_range(ins_tokens, 0, g0)
            right_ctx = render_range(ins_tokens, g1, len(ins_tokens))
            pre = lcp(entity, left_ctx)
            suf = lcsuf(entity, right_ctx)
            if pre:
                entity = entity[len(pre):]
            if suf and len(entity) > len(suf):
                entity = entity[:len(entity) - len(suf)]
            try:
                abs_g0 = j1 + g0
                abs_g1 = j1 + g1
                if _inside_quote(dst_tokens, abs_g0, abs_g1):
                    first_plain = _first_plain_prefix(ins_tokens[g1:])
                    if first_plain:
                        pos = entity.rfind(first_plain)
                        if pos != -1:
                            entity = entity[:pos]
                    if entity:
                        right_ctx_plain = _render_skip_tags(ins_tokens[g1:])
                        overlap = _suffix_overlap_with_right_prefix(entity, right_ctx_plain)
                        if overlap and len(entity) > overlap:
                            entity = entity[:-overlap]
            except Exception:
                pass
            entity = entity.strip()
            if not entity:
                entity = render_range(del_tokens, 0, len(del_tokens))
            if allowed_mid_tokens:
                for tt in ins_tokens[g0:g1]:
                    if isinstance(tt, str) and tt in allowed_mid_tokens:
                        used_mid_tokens.add(tt)
            pairs.append((entity, comp))
        elif tag == "insert":
            if idx == 0:
                continue
            prev = opcodes[idx - 1]
            if prev[0] != "delete":
                continue
            del_tokens = src_tokens[prev[1]:prev[2]]
            ins_tokens = dst_tokens[j1:j2]
            grp = _find_adjacent_composite_group(ins_tokens, allowed_mid_tokens=allowed_mid_tokens)
            if grp is None:
                continue
            entity = render_range(del_tokens, 0, len(del_tokens))
            g0, g1 = grp
            comp = render_range(ins_tokens, g0, g1)
            left_ctx = render_range(ins_tokens, 0, g0)
            right_ctx = render_range(ins_tokens, g1, len(ins_tokens))
            pre = lcp(entity, left_ctx)
            suf = lcsuf(entity, right_ctx)
            if pre:
                entity = entity[len(pre):]
            if suf and len(entity) > len(suf):
                entity = entity[:len(entity) - len(suf)]
            try:
                abs_g0 = j1 + g0
                abs_g1 = j1 + g1
                if _inside_quote(dst_tokens, abs_g0, abs_g1):
                    first_plain = _first_plain_prefix(ins_tokens[g1:])
                    if first_plain:
                        pos = entity.rfind(first_plain)
                        if pos != -1:
                            entity = entity[:pos]
                    if entity:
                        right_ctx_plain = _render_skip_tags(ins_tokens[g1:])
                        overlap = _suffix_overlap_with_right_prefix(entity, right_ctx_plain)
                        if overlap and len(entity) > overlap:
                            entity = entity[:-overlap]
            except Exception:
                pass
            entity = entity.strip()
            if not entity:
                entity = render_range(del_tokens, 0, len(del_tokens))
            if allowed_mid_tokens:
                for tt in ins_tokens[g0:g1]:
                    if isinstance(tt, str) and tt in allowed_mid_tokens:
                        used_mid_tokens.add(tt)
            pairs.append((entity, comp))

    return pairs, used_mid_tokens


def compute_mappings_and_self_check_from_tokens(
    src_tokens: Sequence[Token],
    dst_tokens: Sequence[Token],
    hide_s: str,
) -> Tuple["OrderedDict[str, List[str]]", dict, Optional[Any], Optional[Set[str]], Optional[str], Set[str], List[dict]]:
    def _extract_conj_between_tags(tokens: Sequence[Token], conj_set: Set[str]) -> Set[str]:
        selected: Set[str] = set()
        n = len(tokens)
        for idx, t in enumerate(tokens):
            if not (isinstance(t, str) and t in conj_set):
                continue
            li = idx - 1
            while li >= 0 and not isinstance(tokens[li], TagToken):
                li -= 1
            ri = idx + 1
            while ri < n and not isinstance(tokens[ri], TagToken):
                ri += 1
            if li >= 0 and ri < n:
                selected.add(t)
        return selected

    contextual_allowed: Set[str] = _extract_conj_between_tags(dst_tokens, CONJ_JUNK_SET)

    def _mk_isjunk(allowed: Set[str]):
        return (lambda tok: isinstance(tok, str) and tok in allowed) if allowed else None

    strategies: List[Tuple[str, Optional[Any], Optional[Set[str]]]] = [("default", None, None)]
    if contextual_allowed:
        strategies.append(("fallback:contextual-conj", _mk_isjunk(contextual_allowed), contextual_allowed))
        for tok in sorted(list(contextual_allowed)):
            single = {tok}
            strategies.append((f"fallback:contextual-one:{tok}", _mk_isjunk(single), single))

    best_result = None
    best_missing = None

    attempts_summary: List[dict] = []
    default_self_check: Optional[dict] = None
    chosen_isjunk = None
    chosen_allowed = None
    chosen_label = None
    chosen_used_mid_tokens: Set[str] = set()

    for label, sjunk, allowed in strategies:
        pairs, used_mids = extract_entity_tag_pairs(src_tokens, dst_tokens, isjunk=sjunk, allowed_mid_tokens=allowed)
        mappings: "OrderedDict[str, List[str]]" = OrderedDict()
        for entity, tag in pairs:
            arr = mappings.setdefault(tag, [])
            if entity not in arr:
                arr.append(entity)

        hide_tag_set = {m.group(0) for m in TAG_PATTERN.finditer(hide_s)}
        expanded_tags: List[str] = []
        for composite in mappings.keys():
            expanded_tags.extend([m.group(0) for m in TAG_PATTERN.finditer(composite)])
        mapped_tag_set = set(expanded_tags)
        all_values_non_empty = all(len(v) > 0 for v in mappings.values()) if len(mappings) > 0 else True

        set_equal = (hide_tag_set == mapped_tag_set)
        pass_flag = set_equal and all_values_non_empty

        missing_tags = sorted(list(hide_tag_set - mapped_tag_set))
        extra_tags = sorted(list(mapped_tag_set - hide_tag_set))

        self_check: Dict[str, Any] = {
            "pass": pass_flag,
            "summary": {
                "hide_tag_set_count": len(hide_tag_set),
                "mapped_tag_set_count": len(mapped_tag_set),
                "all_values_non_empty": all_values_non_empty,
                "set_equal": set_equal,
            },
            "missing": {
                "count": len(missing_tags),
                "tags": missing_tags[:50],
            },
            "extra": {
                "count": len(extra_tags),
                "tags": extra_tags[:50],
            },
        }

        attempts_summary.append({
            "label": label,
            "pass": pass_flag,
            "missing_count": len(missing_tags),
            "extra_count": len(extra_tags),
        })
        if label == "default":
            default_self_check = self_check

        if pass_flag:
            best_result = (mappings, self_check, sjunk, allowed, label, used_mids)
            chosen_isjunk, chosen_allowed, chosen_label = sjunk, allowed, label
            chosen_used_mid_tokens = used_mids
            break
        miss_count = len(missing_tags)
        if best_missing is None or miss_count < best_missing:
            best_missing = miss_count
            best_result = (mappings, self_check, sjunk, allowed, label, used_mids)
            chosen_isjunk, chosen_allowed, chosen_label = sjunk, allowed, label
            chosen_used_mid_tokens = used_mids

    mappings, self_check, _, _, _, _ = best_result

    if chosen_label is not None:
        used_fallback = (chosen_label != "default")
        strat_obj = {
            "chosen": chosen_label,
            "used_fallback": used_fallback,
            "chosen_isjunk": None if chosen_isjunk is None else "conj_junk",
            "allowed_mid_tokens": None if chosen_allowed is None else sorted(list(chosen_allowed)),
            "used_mid_tokens": sorted(list(chosen_used_mid_tokens)) if chosen_used_mid_tokens else [],
        }
        if used_fallback and default_self_check is not None and not default_self_check.get("pass") and self_check.get("pass"):
            fallback_obj = {
                "used": True,
                "recovered_from": {
                    "missing_count": default_self_check["missing"]["count"],
                    "extra_count": default_self_check["extra"]["count"],
                    "missing_tags_example": default_self_check["missing"]["tags"],
                    "extra_tags_example": default_self_check["extra"]["tags"],
                },
                "recovered_to": {
                    "missing_count": self_check["missing"]["count"],
                    "extra_count": self_check["extra"]["count"],
                },
                "chosen_strategy": chosen_label,
            }
        else:
            fallback_obj = {"used": False}
        self_check["strategy"] = {"chosen": strat_obj["chosen"], "used_fallback": strat_obj["used_fallback"]}

    return mappings, self_check, chosen_isjunk, chosen_allowed, chosen_label, chosen_used_mid_tokens, attempts_summary


# ---------------------------------------------------------------------------
# Public helper mirroring tagid.pair_core
# ---------------------------------------------------------------------------


@dataclass
class PairComputationResult:
    mapping: "OrderedDict[str, List[str]]"
    normalized_mapping: Dict[str, List[str]]
    self_check: Dict[str, Any]
    chosen_strategy: Optional[str]
    used_mid_tokens: Sequence[str]
    attempts_summary: List[Dict[str, Any]]


def _normalize_mapping(raw_mapping: Iterable[Tuple[str, Iterable[Any]]]) -> Dict[str, List[str]]:
    normalized: Dict[str, List[str]] = OrderedDict()
    for key, values in raw_mapping:
        key_str = str(key).strip()
        if not key_str:
            continue
        bucket = normalized.setdefault(key_str, [])
        for value in values:
            val_str = str(value).strip()
            if not val_str or val_str in bucket:
                continue
            bucket.append(val_str)
    return normalized


def compute_pair_mapping(
    input_text: str,
    hide_text: str,
    *,
    include_quote_delims: bool = False,
) -> PairComputationResult:
    src_tokens = tokenize_input_text(str(input_text), include_quote_delims=include_quote_delims)
    dst_tokens = tokenize_hide_with_tags(str(hide_text), include_quote_delims=include_quote_delims)

    (
        mappings,
        self_check,
        _chosen_isjunk,
        _chosen_allowed,
        chosen_label,
        chosen_used_mid_tokens,
        attempts_summary,
    ) = compute_mappings_and_self_check_from_tokens(src_tokens, dst_tokens, str(hide_text))

    normalized_mapping = _normalize_mapping(mappings.items())

    return PairComputationResult(
        mapping=mappings,
        normalized_mapping=normalized_mapping,
        self_check=self_check,
        chosen_strategy=chosen_label,
        used_mid_tokens=sorted(list(chosen_used_mid_tokens)) if chosen_used_mid_tokens else [],
        attempts_summary=attempts_summary,
    )


# ---------------------------------------------------------------------------
# CLI wrapper
# ---------------------------------------------------------------------------


def _read_text(value: Optional[str], file_path: Optional[str], field_name: str) -> str:
    if value is not None and file_path is not None:
        raise SystemExit(f"{field_name}: cannot specify both text and file")
    if value is None and file_path is None:
        raise SystemExit(f"{field_name}: provide content via --{field_name} or --{field_name}-file")
    if file_path is not None:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return value or ''


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Generate pair mapping from original text and anonymized hide text",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python pair_core.py --input 'original sentence' --hide '<entity[001].Seg1.Seg2>'\n"
            "  python pair_core.py --input-file input.txt --hide-file hide.txt --dump-self-check\n"
        ),
    )
    parser.add_argument('--input', help='Original input_text content')
    parser.add_argument('--input-file', help='Read original input_text from file')
    parser.add_argument('--hide', help='Hide text content containing tags')
    parser.add_argument('--hide-file', help='Read hide text from file')
    parser.add_argument('--include-quote-delims', action='store_true', help='Include book-title mark delimiters (disabled by default)')
    parser.add_argument('--dump-self-check', action='store_true', help='Dump self-check details to stderr')

    args = parser.parse_args(argv)

    input_text = _read_text(args.input, args.input_file, 'input')
    hide_text = _read_text(args.hide, args.hide_file, 'hide')

    result = compute_pair_mapping(
        input_text=input_text,
        hide_text=hide_text,
        include_quote_delims=args.include_quote_delims,
    )

    json_output = json.dumps(result.normalized_mapping, ensure_ascii=False, separators=(',', ':'))
    print(json_output)

    if args.dump_self_check:
        json.dump(result.self_check, sys.stderr, ensure_ascii=False, indent=2)
        sys.stderr.write('\n')


if __name__ == '__main__':
    main()
