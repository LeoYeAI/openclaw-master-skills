#!/usr/bin/env python3
"""Search and inspect consulting reports from iResearch and QuestMobile.

This script provides four subcommands:

- list: fetch the latest iResearch free reports
- search: search iResearch first, then QuestMobile as a secondary source
- detail: fetch a report detail page from either source and extract evidence
- answer: answer a question conservatively using one report's public evidence
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import datetime
import json
import re
import sys
from dataclasses import asdict, dataclass
from html import unescape
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

IRESEARCH_API_URL = "https://www.iresearch.com.cn/api/products/GetReportList"
IRESEARCH_DEFAULT_LAST_ID = ""
IRESEARCH_DEFAULT_PAGE_SIZE = 100
IRESEARCH_MAX_BATCH_SIZE = 50
SEARCH_DEFAULT_PAGES = 8
SEARCH_DEFAULT_LIMIT = 20
SEARCH_AUTO_MAX_PAGES = 20
SEARCH_AUTO_PAGE_STEP = 2
QUESTMOBILE_LIST_URL = "https://www.questmobile.com.cn/research/reports/"
QUESTMOBILE_ARTICLE_LIST_URL = (
    "https://www.questmobile.com.cn/api/v2/report/article-list"
)
IRESEARCH_SOURCE = "iresearch"
QUESTMOBILE_SOURCE = "questmobile"
SOURCE_PRIORITY = {
    IRESEARCH_SOURCE: 0,
    QUESTMOBILE_SOURCE: 1,
}
JSON_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.iresearch.com.cn/report.shtml",
}
HTML_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


@dataclass(slots=True)
class ReportSummary:
    """Summary metadata for a report source item."""

    source: str
    report_id: str
    news_id: int
    title: str
    summary: str
    industry: str
    author: str
    published_at: str
    views: int
    keywords: list[str]
    price: int | None
    detail_url: str
    online_read_url: str | None


@dataclass(slots=True)
class ReportDetail:
    """Structured information extracted from a report detail page."""

    source: str
    report_id: str
    news_id: int
    title: str
    author: str | None
    published_at: str | None
    industry: str | None
    report_type: str | None
    page_count: int | None
    chart_count: int | None
    price: str | None
    detail_url: str
    online_read_url: str | None
    summary: str
    interpretation: str
    evidence_boundary: str
    outline_sections: list[str]
    catalog: str
    chart_catalog: str
    viewer_images: list[str]
    keywords: list[str]


@dataclass(slots=True)
class ReportAnswer:
    """Grounded answer generated from public report evidence."""

    source: str
    report_id: str
    title: str
    question: str
    answer: str
    evidence: list[str]
    evidence_boundary: str
    report_link: str
    online_read_url: str | None
    verification_links: list[str]


def clean_text(value: str) -> str:
    """Normalize HTML-decoded text."""
    value = unescape(value).replace("\u3000", " ").replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def html_to_text(fragment: str) -> str:
    """Convert a small HTML fragment into newline-preserving plain text."""
    fragment = unescape(fragment)
    fragment = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.IGNORECASE)
    fragment = re.sub(r"</p\s*>", "\n", fragment, flags=re.IGNORECASE)
    fragment = re.sub(r"</h[1-6]\s*>", "\n", fragment, flags=re.IGNORECASE)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    lines = [clean_text(line) for line in fragment.splitlines()]
    return "\n".join(line for line in lines if line)


def first_sentences(text: str, limit: int = 2) -> str:
    """Return the first few sentences from a block of text."""
    normalized = clean_text(text)
    if not normalized:
        return ""
    parts = [
        part.strip()
        for part in re.split(r"(?<=[。！？!?；;])", normalized)
        if part.strip()
    ]
    if not parts:
        return normalized
    return "".join(parts[:limit]).strip()


def extract_outline_sections(catalog: str, limit: int = 8) -> list[str]:
    """Extract structured outline lines from a public catalog block."""
    sections: list[str] = []
    for line in [clean_text(item) for item in catalog.splitlines() if clean_text(item)]:
        if line in {"报告摘要", "目录"}:
            continue
        if not re.match(r"^([0-9]+(\.[0-9]+)*|[一二三四五六七八九十]+)[\s、.]", line):
            continue
        if line not in sections:
            sections.append(line)
        if len(sections) >= limit:
            break
    return sections


def summarize_outline_sections(outline_sections: list[str], limit: int = 4) -> str:
    """Summarize the first few outline sections for natural-language output."""
    selected = [clean_text(item) for item in outline_sections if clean_text(item)][
        :limit
    ]
    return "；".join(selected)


def chart_catalog_lines(chart_catalog: str) -> list[str]:
    """Split a chart catalog block into clean individual lines."""
    return [clean_text(item) for item in chart_catalog.splitlines() if clean_text(item)]


def select_relevant_lines(query: str, lines: list[str], limit: int = 4) -> list[str]:
    """Pick the most query-relevant public lines while preserving deterministic output."""
    if not lines:
        return []

    query_text = clean_text(query).lower()
    query_tokens = [token.lower() for token in tokenize(query) if clean_text(token)]
    scored: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        line_lower = line.lower()
        score = 0
        if query_text and query_text in line_lower:
            score += 10
        for token in query_tokens:
            if token and token in line_lower:
                score += 3
        scored.append((score, index, line))

    relevant = [item for item in scored if item[0] > 0]
    if relevant:
        relevant.sort(key=lambda item: (-item[0], item[1]))
        return [item[2] for item in relevant[:limit]]
    return lines[:limit]


def contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    """Return whether any pattern appears in normalized text."""
    normalized = clean_text(text).lower()
    return any(pattern.lower() in normalized for pattern in patterns)


def build_interpretation(
    source: str,
    title: str,
    summary: str,
    outline_sections: list[str],
    chart_catalog: str,
    keywords: list[str],
) -> str:
    """Build a conservative interpretation grounded in public detail evidence."""
    intro = first_sentences(summary, limit=2)
    outline_summary = summarize_outline_sections(outline_sections, limit=4)
    parts: list[str] = []

    if intro:
        parts.append(f"从公开简介看，这份报告的核心内容是：{intro}")
    elif title:
        parts.append(f"从标题看，这份报告聚焦于“{title}”相关议题。")

    if outline_summary:
        parts.append(f"从公开目录看，内容重点覆盖：{outline_summary}。")

    if keywords:
        parts.append("公开关键词包括：" + "、".join(keywords[:6]) + "。")

    if chart_catalog:
        parts.append(
            "图表目录也显示，报告包含一定的数据图表支撑，但具体数值仍需回看原页。"
        )

    if not parts:
        parts.append(
            f"当前这份 {source} 报告公开可见的信息有限，因此解读需要保持保守。"
        )

    return " ".join(parts).strip()


def build_report_answer(report: ReportDetail, question: str) -> ReportAnswer:
    """Answer a user question conservatively using only public report evidence."""
    normalized_question = clean_text(question)
    outline_lines = [
        clean_text(item) for item in report.outline_sections if clean_text(item)
    ]
    chart_lines = chart_catalog_lines(report.chart_catalog)
    relevant_outline = select_relevant_lines(
        normalized_question, outline_lines, limit=5
    )
    relevant_charts = select_relevant_lines(normalized_question, chart_lines, limit=4)
    intro = first_sentences(report.summary, limit=2)

    evidence: list[str] = []
    if intro:
        evidence.append(f"报告简介：{intro}")
    if relevant_outline:
        evidence.append("公开目录：" + "；".join(relevant_outline))
    if relevant_charts:
        evidence.append("图表目录：" + "；".join(relevant_charts))
    elif report.chart_catalog:
        evidence.append("图表目录：公开页面显示该报告包含图表目录。")

    if contains_any(
        normalized_question,
        ("发布时间", "什么时候", "哪年", "日期", "何时发布", "发布于"),
    ):
        answer = f"这份报告公开页面标注的发布时间是 {report.published_at or '未标注'}。"
    elif contains_any(
        normalized_question,
        ("作者", "谁写", "来源", "机构", "发布方", "哪家"),
    ):
        answer = f"这份报告公开页面显示的作者或发布机构是 {report.author or '未标注'}，来源为 {report.source}。"
    elif contains_any(
        normalized_question,
        ("链接", "地址", "在线阅读", "原文", "pdf", "报告链接", "怎么看"),
    ):
        online_read = report.online_read_url or "当前未提供在线阅读链接"
        answer = f"报告详情页链接是 {report.detail_url}。在线阅读入口是 {online_read}。"
    elif contains_any(
        normalized_question,
        ("目录", "章节", "结构", "分几部分", "覆盖哪些", "包含哪些部分"),
    ):
        if relevant_outline:
            answer = (
                "从公开目录看，这份报告主要覆盖：" + "；".join(relevant_outline) + "。"
            )
        elif report.catalog:
            answer = (
                "公开页面可以确认这份报告包含目录结构，但当前未提取出稳定的章节摘要。"
            )
        else:
            answer = "当前公开页面没有暴露足够稳定的目录结构，暂时只能确认它存在详情页与摘要信息。"
    elif contains_any(
        normalized_question,
        (
            "图表",
            "数据",
            "案例",
            "指标",
            "多少",
            "几%",
            "规模",
            "增速",
            "渗透率",
            "份额",
            "排名",
            "数值",
        ),
    ):
        if relevant_charts:
            answer = (
                "公开页面能确认这份报告包含与该问题相关的数据图表线索，例如："
                + "；".join(relevant_charts)
                + "。但脚本当前不对页面图片做 OCR，所以还不能直接给出精确数值，仍需回到在线阅读页或 viewer_images 做人工核验。"
            )
        elif report.chart_catalog:
            answer = (
                "公开页面能确认这份报告含有图表目录，说明报告内部存在数据图表支撑。"
                "不过当前可见证据不足以直接回答具体数值问题，仍需回看原始页面。"
            )
        else:
            answer = (
                "当前公开简介和目录不足以支持精确数据回答。"
                "如果你要的是具体数值、比例或排名，需要回到原报告页面逐页核验。"
            )
    elif contains_any(
        normalized_question,
        ("适合谁", "面向谁", "谁应该看", "适合哪些人", "受众", "读者"),
    ):
        focus_terms = [term for term in [report.industry, *report.keywords[:3]] if term]
        focus_text = "、".join(focus_terms) if focus_terms else report.title
        answer = f"从标题、行业和公开目录看，这份报告更适合关注 {focus_text} 的研究、战略、产品、市场或投资相关人员阅读。"
    elif contains_any(
        normalized_question,
        (
            "讲什么",
            "主要讲",
            "说什么",
            "核心观点",
            "总结",
            "摘要",
            "核心内容",
            "怎么看",
        ),
    ):
        answer = report.interpretation
    else:
        answer_parts: list[str] = []
        if intro:
            answer_parts.append(f"基于公开简介，目前能确认的是：{intro}")
        if relevant_outline:
            answer_parts.append(
                "从公开目录看，相关内容主要落在：" + "；".join(relevant_outline) + "。"
            )
        elif outline_lines:
            answer_parts.append(
                "从公开目录看，报告整体覆盖：" + "；".join(outline_lines[:4]) + "。"
            )
        if relevant_charts and contains_any(
            normalized_question, ("数据", "图表", "证据")
        ):
            answer_parts.append(
                "相关图表线索包括：" + "；".join(relevant_charts) + "。"
            )
        if not answer_parts:
            answer_parts.append(
                "当前公开页面能支持的回答有限，暂时只能确认该报告的标题、基础元数据和部分目录结构。"
            )
        answer_parts.append("如需精确页内结论，请回到在线阅读页继续核验。")
        answer = " ".join(answer_parts)

    verification_links = report.viewer_images[:5] if report.viewer_images else []
    if not evidence:
        evidence.append("当前答案主要来自公开详情页的基础元数据。")

    return ReportAnswer(
        source=report.source,
        report_id=report.report_id,
        title=report.title,
        question=normalized_question,
        answer=answer,
        evidence=evidence,
        evidence_boundary=report.evidence_boundary,
        report_link=report.detail_url,
        online_read_url=report.online_read_url,
        verification_links=verification_links,
    )


def build_evidence_boundary(source: str, has_viewer_images: bool) -> str:
    """Explain what the current interpretation is grounded on."""
    if source == IRESEARCH_SOURCE:
        if has_viewer_images:
            return (
                "当前解读主要基于公开的报告简介、meta description、目录、图表目录，以及在线浏览页暴露的页面图片链接。"
                "脚本当前不会对页面图片做 OCR，因此涉及具体页内数据或精确表述时，仍应回到 viewer_images 对应页面进行人工核验。"
            )
        return (
            "当前解读主要基于公开的报告简介、meta description、目录和图表目录。"
            "在没有进一步检查页面图片的情况下，结论应限制在这些公开可见部分能够支持的范围内。"
        )
    return (
        "当前解读主要基于公开的导语、元数据区块、标题结构以及页面中暴露的图片。"
        "它应被视为基于公开页面的解读，而不是对完整报告正文的逐页通读。"
    )


def decode_html(data: bytes) -> str:
    """Decode HTML pages for both supported sources."""
    for encoding in ("utf-8", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="ignore")


def fetch_bytes(url: str, headers: dict[str, str]) -> bytes:
    """Fetch a URL and return raw bytes."""
    request = Request(url, headers=headers)
    with urlopen(request, timeout=20) as response:
        return response.read()


def fetch_json(url: str) -> dict[str, Any]:
    """Fetch JSON from the iResearch list API."""
    return json.loads(fetch_bytes(url, JSON_HEADERS).decode("utf-8"))


def fetch_html(url: str) -> str:
    """Fetch and decode an HTML page."""
    return decode_html(fetch_bytes(url, HTML_HEADERS))


def build_iresearch_list_url(
    last_id: str,
    page_size: int,
    fee: int = 0,
    date: str = "",
) -> str:
    """Build the iResearch list API URL."""
    query = urlencode(
        {
            "fee": fee,
            "date": date,
            "lastId": last_id,
            "pageSize": page_size,
        }
    )
    return f"{IRESEARCH_API_URL}?{query}"


def build_iresearch_viewer_url(news_id: int) -> str:
    """Return the iResearch online reader URL for a report."""
    return f"https://report.iresearch.cn/report_pdf.aspx?id={news_id}"


def build_questmobile_detail_url(news_id: int) -> str:
    """Return the QuestMobile detail URL for a report."""
    return f"https://www.questmobile.com.cn/research/report/{news_id}"


def normalize_report_link(url: str | None) -> str:
    """Normalize and validate a public report link."""
    value = clean_text(url or "")
    if not value:
        return ""
    if value.startswith("//"):
        return f"https:{value}"
    if value.startswith("http://") or value.startswith("https://"):
        return value
    return ""


def require_report_link(url: str | None) -> str:
    """Require a valid public report link and raise when it is missing."""
    normalized = normalize_report_link(url)
    if not normalized:
        raise ValueError("Report link is required and cannot be empty")
    return normalized


def build_questmobile_list_url(
    page_no: int,
    page_size: int,
    industry_id: int = -1,
    label_id: int = -1,
    version: int = 0,
) -> str:
    """Return the QuestMobile paginated article-list endpoint URL."""
    query = urlencode(
        {
            "version": version,
            "pageSize": page_size,
            "pageNo": page_no,
            "industryId": industry_id,
            "labelId": label_id,
        }
    )
    return f"{QUESTMOBILE_ARTICLE_LIST_URL}?{query}"


def tokenize(query: str) -> list[str]:
    """Split a search query into ranking tokens."""
    base_tokens = [
        clean_text(value) for value in re.split(r"[\s,，、/]+", query) if value.strip()
    ]
    if not base_tokens:
        return [clean_text(query)]

    tokens: list[str] = []
    for token in base_tokens:
        if token and token not in tokens:
            tokens.append(token)
        for segment in re.findall(r"[A-Za-z0-9]+|[\u4e00-\u9fff]+", token):
            normalized_segment = clean_text(segment)
            if normalized_segment and normalized_segment not in tokens:
                tokens.append(normalized_segment)
    return tokens


def extract_years(text: str) -> list[int]:
    """Extract distinct 4-digit years from text in appearance order."""
    years: list[int] = []
    for match in re.findall(r"(?<!\d)((?:19|20)\d{2})(?!\d)", clean_text(text)):
        year = int(match)
        if year not in years:
            years.append(year)
    return years


def non_year_query_tokens(query: str) -> list[str]:
    """Return non-year ranking tokens from a query."""
    query_year_tokens = {str(year) for year in extract_years(query)}
    return [
        token for token in tokenize(query) if token.lower() not in query_year_tokens
    ]


def has_strong_title_topic_match(results: list[dict[str, Any]], query: str) -> bool:
    """Return whether at least one result title strongly matches the non-year topic tokens."""
    topic_tokens = [clean_text(token).lower() for token in non_year_query_tokens(query)]
    if not topic_tokens:
        return True
    for item in results:
        title = clean_text(str(item.get("title") or "")).lower()
        if title and all(token in title for token in topic_tokens):
            return True
    return False


def score_report(query: str, report: ReportSummary) -> int:
    """Compute a simple lexical relevance score for a report."""
    query_text = clean_text(query).lower()
    query_years = {str(year) for year in extract_years(query)}
    title = report.title.lower()
    summary = report.summary.lower()
    industry = report.industry.lower()
    keyword_blob = " ".join(keyword.lower() for keyword in report.keywords)
    score = 0
    if query_text and query_text in title:
        score += 40
    if query_text and query_text in summary:
        score += 20
    if query_text and query_text in keyword_blob:
        score += 12
    for token in tokenize(query):
        token_lower = token.lower()
        is_year_token = token_lower in query_years
        title_weight = 4 if is_year_token else 12
        keyword_weight = 3 if is_year_token else 7
        industry_weight = 2 if is_year_token else 6
        summary_weight = 2 if is_year_token else 4
        if token_lower in title:
            score += title_weight
        if token_lower in keyword_blob:
            score += keyword_weight
        if token_lower in industry:
            score += industry_weight
        if token_lower in summary:
            score += summary_weight
    if score > 0:
        score += min(report.views // 5000, 8)
    return score


def published_at_sort_key(value: str) -> tuple[int, int, int, int, int, int]:
    """Convert a published_at string into a descending-friendly datetime tuple."""
    normalized = clean_text(value)
    if not normalized:
        return (0, 0, 0, 0, 0, 0)

    for fmt in ("%Y/%m/%d %H:%M:%S", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(normalized, fmt)
        except ValueError:
            continue
        return (
            parsed.year,
            parsed.month,
            parsed.day,
            parsed.hour,
            parsed.minute,
            parsed.second,
        )

    numbers = [int(part) for part in re.findall(r"\d+", normalized)]
    padded = (numbers + [0, 0, 0, 0, 0, 0])[:6]
    return tuple(padded)  # type: ignore[return-value]


def parse_cli_datetime(value: str) -> tuple[int, int, int, int, int, int]:
    """Parse a CLI date or datetime string into a sortable tuple."""
    normalized = clean_text(value)
    if not normalized:
        raise ValueError("Date value cannot be empty")

    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
        try:
            parsed = datetime.strptime(normalized, fmt)
        except ValueError:
            continue
        return (
            parsed.year,
            parsed.month,
            parsed.day,
            parsed.hour,
            parsed.minute,
            parsed.second,
        )
    raise ValueError(
        "Unsupported date format. Use YYYY-MM-DD, YYYY/MM/DD, YYYY-MM-DD HH:MM:SS, or YYYY/MM/DD HH:MM:SS"
    )


def should_include_report(
    published_at: str,
    since: tuple[int, int, int, int, int, int] | None,
) -> bool:
    """Return whether a report passes the optional since-date filter."""
    if since is None:
        return True
    return published_at_sort_key(published_at) >= since


def extract_match(pattern: str, html: str) -> str | None:
    """Return the first cleaned regex capture from HTML."""
    match = re.search(pattern, html, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        return None
    return clean_text(match.group(1))


def extract_all_matches(pattern: str, html: str) -> list[str]:
    """Return all cleaned regex captures from HTML."""
    matches = re.findall(pattern, html, flags=re.DOTALL | re.IGNORECASE)
    cleaned: list[str] = []
    for match in matches:
        raw_value = match if isinstance(match, str) else match[0]
        value = clean_text(html_to_text(raw_value))
        if value and value not in cleaned:
            cleaned.append(value)
    return cleaned


def extract_iresearch_section(html: str, heading: str) -> str:
    """Extract a section block delimited by iResearch `<h3>` headings."""
    pattern = rf"<h3>\s*{re.escape(heading)}\s*</h3>\s*<p>(.*?)</p>"
    match = re.search(pattern, html, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        return ""
    return html_to_text(match.group(1))


def report_from_iresearch_item(item: dict[str, Any]) -> ReportSummary:
    """Map an iResearch list API item into a typed report summary."""
    news_id = int(item["NewsId"])
    return ReportSummary(
        source=IRESEARCH_SOURCE,
        report_id=item["Id"],
        news_id=news_id,
        title=clean_text(item.get("Title") or item.get("sTitle") or ""),
        summary=clean_text(item.get("Content") or ""),
        industry=clean_text(item.get("industry") or ""),
        author=clean_text(item.get("Author") or ""),
        published_at=clean_text(item.get("Uptime") or ""),
        views=int(item.get("views") or 0),
        keywords=[clean_text(value) for value in item.get("Keyword") or [] if value],
        price=int(item.get("Price") or 0),
        detail_url=normalize_report_link(item.get("VisitUrl")),
        online_read_url=build_iresearch_viewer_url(news_id),
    )


def list_iresearch_reports(
    pages: int,
    page_size: int,
    last_id: str = IRESEARCH_DEFAULT_LAST_ID,
    fee: int = 0,
    date: str = "",
) -> list[ReportSummary]:
    """Fetch multiple pages of the iResearch free report feed.

    The public API conceptually uses large page sizes, but the live endpoint
    currently fails at 100 items in a single request. To keep a logical
    page-size of 100 while remaining compatible, the script transparently
    splits large fetches into multiple 50-item backend requests.
    """
    reports: list[ReportSummary] = []
    seen_ids: set[str] = set()
    cursor = last_id
    remaining_items = max(0, pages * page_size)

    while remaining_items > 0:
        request_page_size = min(IRESEARCH_MAX_BATCH_SIZE, remaining_items)
        payload = fetch_json(
            build_iresearch_list_url(
                cursor,
                request_page_size,
                fee=fee,
                date=date,
            )
        )
        if payload.get("Status") != "success":
            raise RuntimeError(f"Unexpected API status: {payload.get('Status')!r}")
        batch = [report_from_iresearch_item(item) for item in payload.get("List") or []]
        if not batch:
            break
        for report in batch:
            if not report.detail_url:
                continue
            if report.report_id in seen_ids:
                continue
            reports.append(report)
            seen_ids.add(report.report_id)
        cursor = batch[-1].report_id
        remaining_items -= len(batch)
        if len(batch) < request_page_size:
            break
    return reports


def parse_questmobile_card_keywords(value: str) -> list[str]:
    """Normalize the QuestMobile card keyword blob into a list."""
    return [
        clean_text(keyword)
        for keyword in re.split(r"[、|]", value.replace(" ", ""))
        if clean_text(keyword)
    ]


def report_from_questmobile_item(item: dict[str, Any]) -> ReportSummary:
    """Map a QuestMobile article-list item into a typed report summary."""
    news_id = int(item["id"])
    industry_list = [
        clean_text(value) for value in item.get("industryList") or [] if value
    ]
    label_list = [clean_text(value) for value in item.get("labelList") or [] if value]
    return ReportSummary(
        source=QUESTMOBILE_SOURCE,
        report_id=f"qm.{news_id}",
        news_id=news_id,
        title=clean_text(item.get("title") or ""),
        summary=clean_text(item.get("introduction") or item.get("content") or ""),
        industry=" | ".join(industry_list),
        author="QuestMobile 研究院",
        published_at=clean_text(item.get("publishTime") or ""),
        views=0,
        keywords=label_list,
        price=None,
        detail_url=build_questmobile_detail_url(news_id),
        online_read_url=build_questmobile_detail_url(news_id),
    )


def list_questmobile_reports(
    pages: int,
    page_size: int,
    industry_id: int = -1,
    label_id: int = -1,
) -> list[ReportSummary]:
    """Fetch paginated public QuestMobile reports from the article-list API."""
    reports: list[ReportSummary] = []
    seen_ids: set[int] = set()
    total_pages: int | None = None
    for page_no in range(1, pages + 1):
        payload = fetch_json(
            build_questmobile_list_url(
                page_no=page_no,
                page_size=page_size,
                industry_id=industry_id,
                label_id=label_id,
            )
        )
        if int(payload.get("code") or 0) != 100200:
            raise RuntimeError(
                f"Unexpected QuestMobile API status: {payload.get('code')!r}"
            )
        batch = [
            report_from_questmobile_item(item) for item in payload.get("data") or []
        ]
        if not batch:
            break
        for report in batch:
            if not report.detail_url:
                continue
            if report.news_id in seen_ids:
                continue
            reports.append(report)
            seen_ids.add(report.news_id)
        total_pages = int(payload.get("totalPage") or 0) or total_pages
        if total_pages is not None and page_no >= total_pages:
            break
    return reports


def build_scored_results(
    query: str,
    reports: list[ReportSummary],
    normalized_industry: str,
    since_filter: tuple[int, int, int, int, int, int] | None,
) -> list[dict[str, Any]]:
    """Filter and score report summaries into serializable search results."""
    scored_results: list[dict[str, Any]] = []
    for report in reports:
        if normalized_industry and normalized_industry not in report.industry.lower():
            continue
        if not should_include_report(report.published_at, since_filter):
            continue
        score = score_report(query, report)
        if score <= 0:
            continue
        result = asdict(report)
        result["score"] = score
        result["source_priority"] = SOURCE_PRIORITY[report.source]
        scored_results.append(result)
    return scored_results


def sort_scored_results(
    scored_results: list[dict[str, Any]],
    query: str,
    sort_by: str,
    sort_order: str,
) -> list[dict[str, Any]]:
    """Sort scored results within a source by the configured strategy."""

    def recency_key(item: dict[str, Any]) -> tuple[int, int, int, int, int, int]:
        return published_at_sort_key(item["published_at"])

    def relevance_key(item: dict[str, Any]) -> int:
        return int(item["score"])

    def views_key(item: dict[str, Any]) -> int:
        return int(item["views"])

    query_years = extract_years(query)

    def title_year_key(item: dict[str, Any]) -> tuple[int, int]:
        title_years = extract_years(str(item.get("title") or ""))
        matched_years = [year for year in title_years if year in query_years]
        return (
            max(matched_years, default=0),
            max(title_years, default=0),
        )

    reverse_sort = sort_order == "desc"
    sorted_results = list(scored_results)
    if query_years:
        sorted_results.sort(
            key=lambda item: (
                title_year_key(item),
                relevance_key(item),
                recency_key(item),
            ),
            reverse=True,
        )
        return sorted_results

    if sort_by == "recency":
        sorted_results.sort(
            key=lambda item: (
                recency_key(item),
                relevance_key(item),
                views_key(item),
            ),
            reverse=reverse_sort,
        )
    else:
        sorted_results.sort(
            key=lambda item: (
                relevance_key(item),
                recency_key(item),
                views_key(item),
            ),
            reverse=reverse_sort,
        )
    return sorted_results


def search_reports(
    query: str,
    pages: int,
    page_size: int,
    limit: int,
    industry: str | None = None,
    include_questmobile: bool = True,
    sort_by: str = "recency",
    sort_order: str = "desc",
    since: str | None = None,
) -> list[dict[str, Any]]:
    """Search reports, always ordering iResearch ahead of QuestMobile."""
    if limit <= 0:
        return []

    normalized_industry = clean_text(industry or "").lower()
    since_filter = parse_cli_datetime(since) if since else None

    iresearch_reports = list_iresearch_reports(pages=pages, page_size=page_size)
    iresearch_results = build_scored_results(
        query,
        iresearch_reports,
        normalized_industry,
        since_filter,
    )
    fetched_pages = pages
    last_cursor = iresearch_reports[-1].report_id if iresearch_reports else ""

    query_has_years = bool(extract_years(query))
    query_has_topic_tokens = bool(non_year_query_tokens(query))

    while iresearch_reports and fetched_pages < SEARCH_AUTO_MAX_PAGES:
        enough_results = len(iresearch_results) >= limit
        enough_topic_precision = not (
            query_has_years
            and query_has_topic_tokens
            and not has_strong_title_topic_match(iresearch_results, query)
        )
        if enough_results and enough_topic_precision:
            break

        extra_pages = min(SEARCH_AUTO_PAGE_STEP, SEARCH_AUTO_MAX_PAGES - fetched_pages)
        extra_reports = list_iresearch_reports(
            pages=extra_pages,
            page_size=page_size,
            last_id=last_cursor,
        )
        if not extra_reports:
            break
        iresearch_results.extend(
            build_scored_results(
                query,
                extra_reports,
                normalized_industry,
                since_filter,
            )
        )
        iresearch_reports = extra_reports
        last_cursor = extra_reports[-1].report_id
        fetched_pages += extra_pages
        if len(extra_reports) < extra_pages * page_size:
            break

    iresearch_results = sort_scored_results(
        iresearch_results,
        query,
        sort_by,
        sort_order,
    )

    if not include_questmobile or len(iresearch_results) >= limit:
        return iresearch_results[:limit]

    questmobile_results = sort_scored_results(
        build_scored_results(
            query,
            list_questmobile_reports(pages=pages, page_size=page_size),
            normalized_industry,
            since_filter,
        ),
        query,
        sort_by,
        sort_order,
    )

    if not iresearch_results:
        return questmobile_results[:limit]

    if len(iresearch_results) >= limit:
        return iresearch_results[:limit]

    remaining_slots = max(0, limit - len(iresearch_results))
    return iresearch_results + questmobile_results[:remaining_slots]


def group_reports_by_source(
    reports: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Group search results by source using the configured source priority."""
    grouped: dict[str, list[dict[str, Any]]] = {
        IRESEARCH_SOURCE: [],
        QUESTMOBILE_SOURCE: [],
    }
    for report in reports:
        grouped.setdefault(report["source"], []).append(report)
    return {
        source: grouped[source]
        for source in sorted(grouped, key=lambda source: SOURCE_PRIORITY[source])
    }


def extract_iresearch_viewer_images(news_id: int) -> list[str]:
    """Extract image URLs from the iResearch online reader page."""
    html = fetch_html(build_iresearch_viewer_url(news_id))
    matches = re.findall(
        rf"https://pic\.iresearch\.cn/rimgs/{news_id}/\d+\.jpg",
        html,
        flags=re.IGNORECASE,
    )
    images: list[str] = []
    for match in matches:
        if match not in images:
            images.append(match)
    return images


def resolve_iresearch_summary(
    identifier: str,
    pages: int,
    page_size: int,
    last_id: str,
) -> ReportSummary:
    """Resolve an iResearch identifier into a report summary."""
    if identifier.startswith("http://") or identifier.startswith("https://"):
        news_id_match = re.search(r"/(\d+)\.shtml", identifier)
        news_id = int(news_id_match.group(1)) if news_id_match else None
        if news_id is not None:
            for report in list_iresearch_reports(
                pages=pages,
                page_size=page_size,
                last_id=last_id,
            ):
                if report.news_id == news_id or report.detail_url == identifier:
                    return report
        raise ValueError(
            "Could not resolve the iResearch report URL from the current feed window"
        )

    reports = list_iresearch_reports(pages=pages, page_size=page_size, last_id=last_id)
    for report in reports:
        if report.report_id == identifier:
            return report
        if str(report.news_id) == identifier:
            return report
    raise ValueError(f"Could not find iResearch report identifier: {identifier}")


def fetch_iresearch_detail(
    identifier: str,
    pages: int,
    page_size: int,
    last_id: str,
    include_images: bool,
) -> ReportDetail:
    """Fetch detail information for an iResearch report."""
    summary = resolve_iresearch_summary(
        identifier,
        pages=pages,
        page_size=page_size,
        last_id=last_id,
    )
    detail_url = require_report_link(summary.detail_url)
    html = fetch_html(detail_url)
    meta_summary = extract_match(r'<meta name="description" content="([^"]+)"', html)
    source_block = extract_match(r"来源：\s*([^<]+?)\s+\d{4}/\d{1,2}/\d{1,2}", html)
    published_at = extract_match(
        r"来源：\s*[^<]+?\s+(\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}:\d{2})",
        html,
    )
    industry = extract_match(r"所属行业：</span><em>(.*?)</em>", html)
    report_type = extract_match(r"报告类型：</span><em>(.*?)</em>", html)
    page_count_text = extract_match(r"页数：</span><em>(.*?)</em>", html)
    chart_count_text = extract_match(r"图表：</span><em>(.*?)</em>", html)
    price = extract_match(r'<li class="price">(.*?)</li>', html)
    online_read_path = extract_match(
        r'href="([^"]*report_pdf\.aspx\?id=\d+)"[^>]*>\s*在线浏览',
        html,
    )
    online_read_url = None
    if online_read_path:
        online_read_url = (
            online_read_path
            if online_read_path.startswith("http")
            else f"https://report.iresearch.cn{online_read_path}"
        )
    viewer_images = (
        extract_iresearch_viewer_images(summary.news_id) if include_images else []
    )
    public_summary = (
        extract_iresearch_section(html, "报告简介") or meta_summary or summary.summary
    )
    catalog = extract_iresearch_section(html, "目录")
    chart_catalog = extract_iresearch_section(html, "图表目录")
    outline_sections = extract_outline_sections(catalog)
    return ReportDetail(
        source=IRESEARCH_SOURCE,
        report_id=summary.report_id,
        news_id=summary.news_id,
        title=summary.title,
        author=source_block or summary.author,
        published_at=published_at or summary.published_at,
        industry=industry or summary.industry,
        report_type=report_type,
        page_count=int(page_count_text)
        if page_count_text and page_count_text.isdigit()
        else None,
        chart_count=int(chart_count_text)
        if chart_count_text and chart_count_text.isdigit()
        else None,
        price=price,
        detail_url=detail_url,
        online_read_url=online_read_url or summary.online_read_url,
        summary=public_summary,
        interpretation=build_interpretation(
            IRESEARCH_SOURCE,
            summary.title,
            public_summary,
            outline_sections,
            chart_catalog,
            summary.keywords,
        ),
        evidence_boundary=build_evidence_boundary(
            IRESEARCH_SOURCE,
            has_viewer_images=bool(viewer_images),
        ),
        outline_sections=outline_sections,
        catalog=catalog,
        chart_catalog=chart_catalog,
        viewer_images=viewer_images,
        keywords=summary.keywords,
    )


def resolve_questmobile_identifier(identifier: str) -> int:
    """Resolve a QuestMobile identifier into a numeric report id."""
    if identifier.startswith("qm."):
        return int(identifier.split(".", maxsplit=1)[1])
    if identifier.startswith("qm:"):
        return int(identifier.split(":", maxsplit=1)[1])
    if "questmobile.com.cn/research/report/" in identifier:
        match = re.search(r"/research/report/(\d+)", identifier)
        if match:
            return int(match.group(1))
    raise ValueError("Could not resolve the QuestMobile identifier")


def extract_questmobile_metadata(
    html: str,
) -> tuple[str | None, list[str], str | None, str | None]:
    """Extract industry, keywords, published date, and author from QuestMobile."""
    industry_fragment = extract_match(
        r"行业：(.+?)</div></div><div[^>]*class=\"other\"", html
    )
    keywords_fragment = extract_match(
        r"关键词：</strong>(.+?)</div></div><div[^>]*class=\"dataAndsource\"", html
    )
    published_at = extract_match(
        r"<span[^>]*>(\d{4}-\d{2}-\d{2})</span></div><div[^>]*class=\"source\"", html
    )
    author = extract_match(r"class=\"source\">来源：([^<]+)</div>", html)

    industry = None
    if industry_fragment:
        industry = clean_text(html_to_text(industry_fragment)).replace("|", " | ")

    keywords: list[str] = []
    if keywords_fragment:
        keywords = extract_all_matches(r"<span>(.*?)</span>", keywords_fragment)
        if not keywords:
            keywords = [clean_text(html_to_text(keywords_fragment))]

    return industry, keywords, published_at, author


def extract_questmobile_catalog(body_html: str) -> str:
    """Extract top-level section headings from QuestMobile detail content."""
    headings = [
        heading
        for heading in extract_all_matches(r"<h3[^>]*>(.*?)</h3>", body_html)
        if re.match(r"^[一二三四五六七八九十]+、", heading)
    ]
    return "\n".join(headings)


def extract_questmobile_chart_catalog(body_html: str) -> str:
    """Extract lower-level narrative headings from QuestMobile detail content."""
    headings = [
        heading
        for heading in extract_all_matches(r"<h4[^>]*>(.*?)</h4>", body_html)
        if heading and not heading.startswith("http") and len(heading) <= 120
    ]
    return "\n".join(headings)


def extract_questmobile_images(body_html: str) -> list[str]:
    """Extract QuestMobile report image URLs from the article body."""
    matches = re.findall(
        r"https://ws\.questmobile\.cn/report/article/images/[A-Za-z0-9]+\.png",
        body_html,
        flags=re.IGNORECASE,
    )
    images: list[str] = []
    for match in matches:
        if match not in images:
            images.append(match)
    return images


def fetch_questmobile_detail(identifier: str, include_images: bool) -> ReportDetail:
    """Fetch detail information for a QuestMobile report."""
    news_id = resolve_questmobile_identifier(identifier)
    detail_url = build_questmobile_detail_url(news_id)
    html = fetch_html(detail_url)
    title = (
        extract_match(r"<h1[^>]*>(.*?)</h1>", html) or f"QuestMobile Report {news_id}"
    )
    meta_summary = extract_match(r'<meta name="description" content="([^"]+)"', html)
    industry, keywords, published_at, author = extract_questmobile_metadata(html)
    intro = extract_match(r"class=\"daoyu\">(.*?)</div><div[^>]*innerhtml=", html)
    body_anchor = html.find("<h1")
    body_html = html[body_anchor:] if body_anchor != -1 else html
    body_html = re.sub(r'\sinnerhtml="[^"]*"', "", body_html)
    chart_catalog = extract_questmobile_chart_catalog(body_html)
    summary_text = intro or meta_summary or ""
    outline_sections = extract_questmobile_catalog(body_html).splitlines()
    return ReportDetail(
        source=QUESTMOBILE_SOURCE,
        report_id=f"qm.{news_id}",
        news_id=news_id,
        title=title,
        author=author or "QuestMobile 研究院",
        published_at=published_at,
        industry=industry,
        report_type="Public report page",
        page_count=None,
        chart_count=None,
        price=None,
        detail_url=detail_url,
        online_read_url=detail_url,
        summary=summary_text,
        interpretation=build_interpretation(
            QUESTMOBILE_SOURCE,
            title,
            summary_text,
            [clean_text(item) for item in outline_sections if clean_text(item)],
            chart_catalog,
            keywords,
        ),
        evidence_boundary=build_evidence_boundary(
            QUESTMOBILE_SOURCE,
            has_viewer_images=include_images,
        ),
        outline_sections=[
            clean_text(item) for item in outline_sections if clean_text(item)
        ],
        catalog=extract_questmobile_catalog(body_html),
        chart_catalog=chart_catalog,
        viewer_images=extract_questmobile_images(body_html) if include_images else [],
        keywords=keywords,
    )


def fetch_report_detail(
    identifier: str,
    pages: int,
    page_size: int,
    last_id: str,
    include_images: bool,
) -> ReportDetail:
    """Fetch detail information for a report from either source."""
    if identifier.startswith("qm.") or identifier.startswith("qm:"):
        return fetch_questmobile_detail(identifier, include_images=include_images)
    if "questmobile.com.cn/research/report/" in identifier:
        return fetch_questmobile_detail(identifier, include_images=include_images)
    return fetch_iresearch_detail(
        identifier,
        pages=pages,
        page_size=page_size,
        last_id=last_id,
        include_images=include_images,
    )


def with_report_link(payload: dict[str, Any]) -> dict[str, Any]:
    """Add a stable report_link field to a serialized report payload."""
    enriched = dict(payload)
    enriched["report_link"] = require_report_link(enriched.get("detail_url"))
    return enriched


def render_report_list_markdown(
    reports: list[dict[str, Any]],
    sort_by: str | None = None,
    sort_order: str | None = None,
    since: str | None = None,
) -> str:
    """Render report summaries as Markdown."""
    lines = ["# Report Search Results", ""]
    if sort_by and sort_order:
        lines.append(f"- Sort: {sort_by} ({sort_order})")
    if since:
        lines.append(f"- Since: {since}")
    if len(lines) > 2:
        lines.append("")
    for index, report in enumerate(reports, start=1):
        lines.extend(
            [
                f"## {index}. {report['title']}",
                f"- Source: {report['source']}",
                f"- Report ID: {report['report_id']}",
                f"- News ID: {report['news_id']}",
                f"- Industry: {report['industry'] or 'Unknown'}",
                f"- Published: {report['published_at'] or 'Unknown'}",
                f"- Views: {report['views']}",
                f"- Score: {report.get('score', 0)}",
                f"- Keywords: {', '.join(report['keywords']) if report['keywords'] else 'None'}",
                f"- Report Link: {report['report_link']}",
                f"- Detail URL: {report['detail_url']}",
                f"- Online Read: {report['online_read_url'] or 'N/A'}",
                f"- Summary: {report['summary']}",
                "",
            ]
        )
    return "\n".join(lines).strip()


def render_grouped_report_list_markdown(
    grouped_reports: dict[str, list[dict[str, Any]]],
    sort_by: str | None = None,
    sort_order: str | None = None,
    since: str | None = None,
) -> str:
    """Render search results grouped by source with iResearch first."""
    lines = ["# Report Search Results", ""]
    if sort_by and sort_order:
        lines.append(f"- Sort: {sort_by} ({sort_order})")
    if since:
        lines.append(f"- Since: {since}")
    if len(lines) > 2:
        lines.append("")
    section_titles = {
        IRESEARCH_SOURCE: "iResearch Reports",
        QUESTMOBILE_SOURCE: "QuestMobile Reports",
    }
    for source in sorted(grouped_reports, key=lambda source: SOURCE_PRIORITY[source]):
        reports = grouped_reports[source]
        if not reports:
            continue
        lines.extend([f"## {section_titles.get(source, source.title())}", ""])
        for index, report in enumerate(reports, start=1):
            lines.extend(
                [
                    f"### {index}. {report['title']}",
                    f"- Report ID: {report['report_id']}",
                    f"- News ID: {report['news_id']}",
                    f"- Industry: {report['industry'] or 'Unknown'}",
                    f"- Published: {report['published_at'] or 'Unknown'}",
                    f"- Views: {report['views']}",
                    f"- Score: {report.get('score', 0)}",
                    f"- Keywords: {', '.join(report['keywords']) if report['keywords'] else 'None'}",
                    f"- Report Link: {report['report_link']}",
                    f"- Detail URL: {report['detail_url']}",
                    f"- Online Read: {report['online_read_url'] or 'N/A'}",
                    f"- Summary: {report['summary']}",
                    "",
                ]
            )
    return "\n".join(lines).strip()


def render_report_detail_markdown(report: ReportDetail) -> str:
    """Render a report detail object as Markdown."""
    lines = [
        f"# {report.title}",
        "",
        f"- Source: {report.source}",
        f"- Report ID: {report.report_id}",
        f"- News ID: {report.news_id}",
        f"- Author: {report.author or 'Unknown'}",
        f"- Published: {report.published_at or 'Unknown'}",
        f"- Industry: {report.industry or 'Unknown'}",
        f"- Report Type: {report.report_type or 'Unknown'}",
        f"- Page Count: {report.page_count if report.page_count is not None else 'Unknown'}",
        f"- Chart Count: {report.chart_count if report.chart_count is not None else 'Unknown'}",
        f"- Price: {report.price or 'Unknown'}",
        f"- Report Link: {report.detail_url}",
        f"- Detail URL: {report.detail_url}",
        f"- Online Read: {report.online_read_url or 'N/A'}",
        f"- Keywords: {', '.join(report.keywords) if report.keywords else 'None'}",
        "",
        "## Summary",
        report.summary or "",
        "",
        "## Interpretation",
        report.interpretation or "",
        "",
        "## Evidence Boundary",
        report.evidence_boundary or "",
        "",
        "## Outline Sections",
        "\n".join(report.outline_sections) if report.outline_sections else "",
        "",
        "## Catalog",
        report.catalog or "",
        "",
        "## Chart Catalog",
        report.chart_catalog or "",
    ]
    if report.viewer_images:
        lines.extend(["", "## Viewer Images", *report.viewer_images])
    return "\n".join(lines).strip()


def render_report_answer_markdown(report_answer: ReportAnswer) -> str:
    """Render a grounded report answer as Markdown."""
    lines = [
        f"# {report_answer.title}",
        "",
        f"- Source: {report_answer.source}",
        f"- Report ID: {report_answer.report_id}",
        f"- Question: {report_answer.question}",
        f"- Report Link: {report_answer.report_link}",
        f"- Online Read: {report_answer.online_read_url or 'N/A'}",
        "",
        "## Answer",
        report_answer.answer,
        "",
        "## Evidence",
        *(f"- {item}" for item in report_answer.evidence),
        "",
        "## Evidence Boundary",
        report_answer.evidence_boundary,
    ]
    if report_answer.verification_links:
        lines.extend(["", "## Verification Links", *report_answer.verification_links])
    return "\n".join(lines).strip()


def output_payload(
    payload: Any,
    output_format: str,
    render_markdown: Callable[[Any], str] | None = None,
) -> None:
    """Print payload as JSON or Markdown."""
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    if render_markdown is None:
        raise ValueError("Markdown output requires a renderer")
    print(render_markdown(payload))


def warn_if_debug_last_id(last_id: str) -> None:
    """Warn when the deprecated debug-only last_id cursor is used explicitly."""
    if clean_text(last_id):
        print(
            "Warning: --last-id is deprecated for normal usage and should only be used for debugging older iResearch cursor windows.",
            file=sys.stderr,
        )


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser(
        "list",
        help="List the latest iResearch free reports",
    )
    list_parser.add_argument("--pages", type=int, default=1)
    list_parser.add_argument(
        "--page-size", type=int, default=IRESEARCH_DEFAULT_PAGE_SIZE
    )
    list_parser.add_argument(
        "--last-id",
        default=IRESEARCH_DEFAULT_LAST_ID,
        help=argparse.SUPPRESS,
    )
    list_parser.add_argument("--format", choices=("json", "markdown"), default="json")

    search_parser = subparsers.add_parser(
        "search",
        help="Search iResearch first and QuestMobile second",
    )
    search_parser.add_argument("query")
    search_parser.add_argument("--pages", type=int, default=SEARCH_DEFAULT_PAGES)
    search_parser.add_argument(
        "--page-size", type=int, default=IRESEARCH_DEFAULT_PAGE_SIZE
    )
    search_parser.add_argument("--limit", type=int, default=SEARCH_DEFAULT_LIMIT)
    search_parser.add_argument("--industry")
    search_parser.add_argument(
        "--sort-by",
        choices=("recency", "relevance"),
        default="recency",
        help="Sort within each source by recency first or relevance first",
    )
    search_parser.add_argument(
        "--sort-order",
        choices=("desc", "asc"),
        default="desc",
        help="Sort direction within each source; default is descending",
    )
    search_parser.add_argument(
        "--since",
        help="Only include reports published on or after this date",
    )
    search_parser.add_argument(
        "--no-questmobile",
        action="store_true",
        help="Disable QuestMobile as the secondary source",
    )
    search_parser.add_argument(
        "--iresearch-only",
        action="store_true",
        help="Use only iResearch results and disable QuestMobile fallback",
    )
    search_parser.add_argument(
        "--grouped",
        action="store_true",
        help="Group results by source with iResearch first and QuestMobile second",
    )
    search_parser.add_argument("--format", choices=("json", "markdown"), default="json")

    detail_parser = subparsers.add_parser(
        "detail",
        help="Fetch a report detail page from iResearch or QuestMobile",
    )
    detail_parser.add_argument("identifier")
    detail_parser.add_argument("--pages", type=int, default=8)
    detail_parser.add_argument(
        "--page-size", type=int, default=IRESEARCH_DEFAULT_PAGE_SIZE
    )
    detail_parser.add_argument(
        "--last-id",
        default=IRESEARCH_DEFAULT_LAST_ID,
        help=argparse.SUPPRESS,
    )
    detail_parser.add_argument("--include-images", action="store_true")
    detail_parser.add_argument("--format", choices=("json", "markdown"), default="json")

    answer_parser = subparsers.add_parser(
        "answer",
        help="Answer a question using public evidence from one report detail page",
    )
    answer_parser.add_argument("identifier")
    answer_parser.add_argument("question")
    answer_parser.add_argument("--pages", type=int, default=8)
    answer_parser.add_argument(
        "--page-size", type=int, default=IRESEARCH_DEFAULT_PAGE_SIZE
    )
    answer_parser.add_argument(
        "--last-id",
        default=IRESEARCH_DEFAULT_LAST_ID,
        help=argparse.SUPPRESS,
    )
    answer_parser.add_argument("--include-images", action="store_true")
    answer_parser.add_argument("--format", choices=("json", "markdown"), default="json")
    return parser


def main() -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "list":
            warn_if_debug_last_id(args.last_id)
            report_list = [
                with_report_link(asdict(report))
                for report in list_iresearch_reports(
                    pages=args.pages,
                    page_size=args.page_size,
                    last_id=args.last_id,
                )
            ]
            output_payload(
                report_list,
                args.format,
                render_markdown=render_report_list_markdown,
            )
            return 0
        if args.command == "search":
            search_results = [
                with_report_link(report)
                for report in search_reports(
                    query=args.query,
                    pages=args.pages,
                    page_size=args.page_size,
                    limit=args.limit,
                    industry=args.industry,
                    include_questmobile=not (
                        args.no_questmobile or args.iresearch_only
                    ),
                    sort_by=args.sort_by,
                    sort_order=args.sort_order,
                    since=args.since,
                )
            ]
            if args.grouped or args.format == "markdown":
                grouped_results = group_reports_by_source(search_results)
                if args.format == "json":
                    print(json.dumps(grouped_results, ensure_ascii=False, indent=2))
                else:
                    print(
                        render_grouped_report_list_markdown(
                            grouped_results,
                            sort_by=args.sort_by,
                            sort_order=args.sort_order,
                            since=args.since,
                        )
                    )
                return 0
            output_payload(
                search_results,
                args.format,
                render_markdown=lambda reports: render_report_list_markdown(
                    reports,
                    sort_by=args.sort_by,
                    sort_order=args.sort_order,
                    since=args.since,
                ),
            )
            return 0
        if args.command == "detail":
            warn_if_debug_last_id(args.last_id)
            report_detail = fetch_report_detail(
                identifier=args.identifier,
                pages=args.pages,
                page_size=args.page_size,
                last_id=args.last_id,
                include_images=args.include_images,
            )
            if args.format == "json":
                print(
                    json.dumps(
                        with_report_link(asdict(report_detail)),
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            else:
                print(render_report_detail_markdown(report_detail))
            return 0
        if args.command == "answer":
            warn_if_debug_last_id(args.last_id)
            report_detail = fetch_report_detail(
                identifier=args.identifier,
                pages=args.pages,
                page_size=args.page_size,
                last_id=args.last_id,
                include_images=args.include_images,
            )
            report_answer = build_report_answer(report_detail, args.question)
            if args.format == "json":
                print(json.dumps(asdict(report_answer), ensure_ascii=False, indent=2))
            else:
                print(render_report_answer_markdown(report_answer))
            return 0
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
