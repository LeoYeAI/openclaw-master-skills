#!/usr/bin/env python3
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

CLAIM_LOG_TEMPLATE = {
    'claims': [],
    'evidence': [],
}


def load_json(path: str) -> Dict[str, Any]:
    if path == '-':
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding='utf-8'))


def dump_json(data: Dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def normalize(data: Dict[str, Any]) -> Dict[str, Any]:
    claims = data.get('claims') or []
    evidence = data.get('evidence') or []

    normalized_claims: List[Dict[str, Any]] = []
    for idx, claim in enumerate(claims, start=1):
        item = dict(claim)
        item.setdefault('claim_id', f'c{idx}')
        item.setdefault('claim_text', '')
        item.setdefault('claim_type', 'fact')
        theme = item.get('theme', [])
        if isinstance(theme, str):
            theme = [theme] if theme else []
        item['theme'] = theme
        item.setdefault('entity', '')
        item.setdefault('time_scope', '')
        item.setdefault('geography', '')
        item.setdefault('status', 'unresolved')
        item.setdefault('confidence', 'low')
        item.setdefault('notes', '')
        normalized_claims.append(item)

    claim_ids = {claim['claim_id'] for claim in normalized_claims}
    normalized_evidence: List[Dict[str, Any]] = []
    for idx, evidence_item in enumerate(evidence, start=1):
        item = dict(evidence_item)
        item.setdefault('evidence_id', f'e{idx}')
        item.setdefault('claim_id', '')
        if item['claim_id'] and item['claim_id'] not in claim_ids:
            claim_ids.add(item['claim_id'])
            normalized_claims.append({
                'claim_id': item['claim_id'],
                'claim_text': '',
                'claim_type': 'fact',
                'theme': [],
                'entity': '',
                'time_scope': '',
                'geography': '',
                'status': 'unresolved',
                'confidence': 'low',
                'notes': 'Auto-created because evidence referenced a missing claim_id',
            })
        item.setdefault('source_url', '')
        item.setdefault('source_class', 'community')
        item.setdefault('modality', 'text-page')
        item.setdefault('access_level', 'fetched page')
        item.setdefault('visible_date', '')
        item.setdefault('extract', '')
        item.setdefault('summary', '')
        item['credibility'] = int(item.get('credibility', 0) or 0)
        item['score'] = int(item.get('score', 0) or 0)
        item.setdefault('supports', 'contextual-only')
        normalized_evidence.append(item)

    return {'claims': normalized_claims, 'evidence': normalized_evidence}


def summary(data: Dict[str, Any]) -> Dict[str, Any]:
    claims = data.get('claims', [])
    evidence = data.get('evidence', [])
    evidence_by_claim = defaultdict(list)
    for item in evidence:
        evidence_by_claim[item.get('claim_id', '')].append(item)

    source_classes = Counter(item.get('source_class', 'unknown') for item in evidence)
    modalities = Counter(item.get('modality', 'unknown') for item in evidence)
    access_levels = Counter(item.get('access_level', 'unknown') for item in evidence)
    statuses = Counter(item.get('status', 'unresolved') for item in claims)

    claim_summaries = []
    for claim in claims:
        claim_id = claim['claim_id']
        linked = evidence_by_claim.get(claim_id, [])
        credibility_values = [item['credibility'] for item in linked]
        score_values = [item['score'] for item in linked]
        support_counts = Counter(item.get('supports', 'contextual-only') for item in linked)
        claim_summaries.append({
            'claim_id': claim_id,
            'claim_text': claim.get('claim_text', ''),
            'status': claim.get('status', 'unresolved'),
            'confidence': claim.get('confidence', 'low'),
            'evidence_count': len(linked),
            'max_credibility': max(credibility_values) if credibility_values else 0,
            'avg_credibility': round(sum(credibility_values) / len(credibility_values), 2) if credibility_values else 0,
            'avg_score': round(sum(score_values) / len(score_values), 2) if score_values else 0,
            'support_mix': dict(support_counts),
        })

    return {
        'claim_count': len(claims),
        'evidence_count': len(evidence),
        'status_counts': dict(statuses),
        'source_class_counts': dict(source_classes),
        'modality_counts': dict(modalities),
        'access_level_counts': dict(access_levels),
        'claims': claim_summaries,
    }


def init_template() -> Dict[str, Any]:
    return CLAIM_LOG_TEMPLATE


def main() -> None:
    parser = argparse.ArgumentParser(description='Normalize and summarize RedNote structured claim logs.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    subparsers.add_parser('init', help='Print an empty claim log template')

    normalize_parser = subparsers.add_parser('normalize', help='Normalize a claim log JSON file')
    normalize_parser.add_argument('path', help='Path to claim log JSON, or - for stdin')

    summary_parser = subparsers.add_parser('summary', help='Summarize a claim log JSON file')
    summary_parser.add_argument('path', help='Path to claim log JSON, or - for stdin')
    summary_parser.add_argument('--markdown', action='store_true', help='Emit markdown instead of JSON')

    args = parser.parse_args()

    if args.command == 'init':
        dump_json(init_template())
        return

    data = normalize(load_json(args.path))

    if args.command == 'normalize':
        dump_json(data)
        return

    result = summary(data)
    if not args.markdown:
        dump_json(result)
        return

    print('# Claim log summary')
    print()
    print(f"- Claims: {result['claim_count']}")
    print(f"- Evidence items: {result['evidence_count']}")
    print(f"- Status counts: {json.dumps(result['status_counts'], ensure_ascii=False)}")
    print(f"- Source classes: {json.dumps(result['source_class_counts'], ensure_ascii=False)}")
    print(f"- Modalities: {json.dumps(result['modality_counts'], ensure_ascii=False)}")
    print(f"- Access levels: {json.dumps(result['access_level_counts'], ensure_ascii=False)}")
    print()
    print('## Claim-level view')
    for item in result['claims']:
        text = item['claim_text'] or '(blank claim text)'
        print(f"- {item['claim_id']} | status={item['status']} | confidence={item['confidence']} | evidence={item['evidence_count']} | max_cred={item['max_credibility']} | avg_cred={item['avg_credibility']} | avg_score={item['avg_score']} | {text}")


if __name__ == '__main__':
    main()
