#!/usr/bin/env python3
import argparse
import json
import re
from typing import Iterable, List

STOPWORDS = {
    "的", "了", "和", "是", "在", "就", "都", "而", "及", "与", "着", "或", "被", "把", "让",
    "我们", "你们", "他们", "这个", "那个", "一个", "一些", "没有", "不是", "真的", "感觉",
    "the", "a", "an", "and", "or", "of", "to", "for", "in", "on", "with", "from", "by", "is",
}


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def dedupe(items: Iterable[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        item = clean(item)
        key = item.casefold()
        if item and key not in seen:
            seen.add(key)
            out.append(item)
    return out


def extract_tokens(text: str) -> List[str]:
    text = clean(text)
    if not text:
        return []
    cjk_chunks = re.findall(r"[\u4e00-\u9fffA-Za-z0-9#@_.:-]{2,}", text)
    tokens = []
    for chunk in cjk_chunks:
        parts = re.split(r"[^\u4e00-\u9fffA-Za-z0-9#@_.:-]+", chunk)
        for part in parts:
            part = clean(part)
            if len(part) >= 2 and part.casefold() not in STOPWORDS:
                tokens.append(part)
    return dedupe(tokens)


def extract_dates(text: str) -> List[str]:
    patterns = [
        r"20\d{2}(?:[-/.年]\d{1,2})(?:[-/.月]\d{1,2}[日号]?)?",
        r"\d{1,2}月\d{1,2}[日号]?",
        r"近\d+[天日周月年]",
    ]
    dates = []
    for pattern in patterns:
        dates.extend(match.group(0) for match in re.finditer(pattern, text))
    return dedupe(dates)


def extract_hashtags(text: str) -> List[str]:
    return dedupe(re.findall(r"[#＃][^#＃\s]{2,30}", text))


def quote_candidates(title: str, snippet: str, max_quotes: int) -> List[str]:
    candidates = []
    for source in [title, snippet]:
        source = clean(source)
        if not source:
            continue
        clauses = re.split(r"[。！？!?.；;，,、]\s*", source)
        for clause in clauses:
            clause = clean(clause)
            if 6 <= len(clause) <= 20:
                candidates.append(f'"{clause}"')
    return dedupe(candidates)[:max_quotes]


def build_queries(entity: str, title: str, snippet: str, extracted_text: str, context: List[str], limit: int) -> List[str]:
    text_pool = " ".join([entity, title, snippet, extracted_text, *context])
    tokens = extract_tokens(text_pool)
    hashtags = extract_hashtags(text_pool)
    quotes = quote_candidates(title, snippet or extracted_text, max_quotes=4)
    dates = extract_dates(text_pool)

    strong_tokens = [t for t in tokens if len(t) >= 2][:12]
    context_terms = dedupe(context + hashtags + dates)[:8]

    queries = []

    if entity:
        queries.extend([
            f'{entity} 小红书',
            f'site:xiaohongshu.com {entity}',
            f'site:www.xiaohongshu.com {entity}',
        ])

    for quote in quotes:
        queries.append(quote)
        if entity:
            queries.append(f'{entity} {quote}')
        queries.append(f'site:xiaohongshu.com {quote}')

    for token in strong_tokens[:8]:
        if entity and token.casefold() != entity.casefold():
            queries.append(f'{entity} {token}')
            queries.append(f'{entity} 小红书 {token}')
        if not entity or token.casefold() != entity.casefold():
            queries.append(token)

    for term in context_terms:
        if entity:
            queries.append(f'{entity} {term}')
            queries.append(f'{entity} 小红书 {term}')
        for quote in quotes[:2]:
            queries.append(f'{quote} {term}')

    for token in strong_tokens[:6]:
        queries.append(f'site:xiaohongshu.com {token}')
        queries.append(f'site:www.xiaohongshu.com {token}')

    return dedupe(queries)[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description='Build recovery-oriented search queries from partial RedNote snippets, titles, OCR text, or subtitle fragments.')
    parser.add_argument('--entity', default='', help='Main subject/entity if known')
    parser.add_argument('--title', default='', help='Visible title or page title')
    parser.add_argument('--snippet', default='', help='Search snippet or short visible description')
    parser.add_argument('--text', default='', help='OCR / subtitle / extracted visible text fragment')
    parser.add_argument('--context', action='append', default=[], help='Extra context tokens such as city, product, hashtag, date; repeatable or comma-separated')
    parser.add_argument('--limit', type=int, default=20, help='Maximum number of recovery queries')
    parser.add_argument('--json', action='store_true', help='Emit JSON instead of markdown')
    args = parser.parse_args()

    context = []
    for value in args.context:
        for item in value.split(','):
            item = clean(item)
            if item:
                context.append(item)

    queries = build_queries(args.entity, args.title, args.snippet, args.text, dedupe(context), args.limit)
    payload = {
        'entity': clean(args.entity),
        'title': clean(args.title),
        'snippet': clean(args.snippet),
        'text': clean(args.text),
        'context': dedupe(context),
        'queries': queries,
        'notes': [
            'Use quoted clauses first to recover reposts or mirrors.',
            'Then pivot on distinctive names, prices, dates, hashtags, or subtitle fragments.',
            'Treat recovered pages as original, relay, or commentary separately in the claim log.',
        ],
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print('# Recovery query set')
    print()
    if payload['entity']:
        print(f"- Entity: {payload['entity']}")
    if payload['title']:
        print(f"- Title: {payload['title']}")
    if payload['snippet']:
        print(f"- Snippet: {payload['snippet']}")
    if payload['text']:
        print(f"- Extracted text: {payload['text']}")
    if payload['context']:
        print(f"- Context: {', '.join(payload['context'])}")
    print()
    print('## Queries')
    for i, query in enumerate(payload['queries'], start=1):
        print(f'{i}. {query}')
    print()
    print('## Recovery notes')
    for note in payload['notes']:
        print(f'- {note}')


if __name__ == '__main__':
    main()
