"""Document ingestion for RAG (ADR-009)."""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from palaia.store import Store

# Supported text extensions
TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".rst", ".text"}
HTML_EXTENSIONS = {".html", ".htm"}
PDF_EXTENSIONS = {".pdf"}
SUPPORTED_EXTENSIONS = TEXT_EXTENSIONS | HTML_EXTENSIONS | PDF_EXTENSIONS

# Optional PDF support
try:
    import pdfplumber

    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# Minimum chunk length (words) to store
MIN_CHUNK_WORDS = 10


class _HTMLTextExtractor(HTMLParser):
    """Extract visible text from HTML."""

    def __init__(self):
        super().__init__()
        self._result: list[str] = []
        self._skip = False
        self._skip_tags = {"script", "style", "head", "meta", "link"}
        self._title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in self._skip_tags:
            self._skip = True
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag in self._skip_tags:
            self._skip = False
        if tag == "title":
            self._in_title = False
        if tag in ("p", "div", "br", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr"):
            self._result.append("\n")

    def handle_data(self, data):
        if self._in_title:
            self._title += data
        if not self._skip:
            self._result.append(data)

    def get_text(self) -> str:
        return "".join(self._result).strip()

    def get_title(self) -> str:
        return self._title.strip()


@dataclass
class IngestResult:
    """Result of a document ingestion."""

    source: str
    total_chunks: int
    stored_chunks: int
    skipped_chunks: int
    project: str | None
    entry_ids: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0


@dataclass
class _PageChunk:
    """Internal: text from a specific page (for PDFs)."""

    text: str
    page: int | None = None


class DocumentIngestor:
    """Ingest documents into Palaia as chunked, searchable entries."""

    def __init__(self, store: Store, config: dict | None = None):
        self.store = store
        self.config = config or store.config

    def ingest(
        self,
        source: str,
        project: str | None = None,
        scope: str = "private",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        tags: list[str] | None = None,
        dry_run: bool = False,
    ) -> IngestResult:
        """Ingest a file, URL, or directory into the store.

        Args:
            source: File path, URL, or directory path.
            project: Palaia project name (recommended).
            scope: Scope for stored entries.
            chunk_size: Target words per chunk.
            chunk_overlap: Overlap words between chunks.
            tags: Additional tags for entries.
            dry_run: If True, don't actually store anything.

        Returns:
            IngestResult with statistics.
        """
        start = time.monotonic()
        source_path = Path(source) if not self._is_url(source) else None

        # Directory: recurse
        if source_path and source_path.is_dir():
            return self._ingest_directory(source_path, project, scope, chunk_size, chunk_overlap, tags, dry_run, start)

        # Single source
        pages, title = self._read_source(source)
        all_tags = ["rag", "ingested"] + (tags or [])
        now = datetime.now(timezone.utc).isoformat()

        # Chunk each page
        chunks: list[tuple[str, int | None]] = []  # (chunk_text, page_number)
        for page in pages:
            page_chunks = self._chunk_text(page.text, chunk_size, chunk_overlap)
            for c in page_chunks:
                chunks.append((c, page.page))

        total_chunks = len(chunks)
        stored = 0
        skipped = 0
        entry_ids: list[str] = []

        source_display = os.path.basename(source) if source_path else source

        for idx, (chunk_text, page_num) in enumerate(chunks):
            # Skip too-short chunks
            if len(chunk_text.split()) < MIN_CHUNK_WORDS:
                skipped += 1
                continue

            if dry_run:
                stored += 1
                continue

            # Build frontmatter fields for source attribution
            extra_tags = list(all_tags)
            # We store via store.write but need custom frontmatter, so write raw
            entry_id = self._store_chunk(
                chunk_text=chunk_text,
                scope=scope,
                project=project,
                tags=extra_tags,
                source=source_display,
                source_page=page_num,
                chunk_index=idx,
                chunk_total=total_chunks,
                ingested_at=now,
                title=title,
            )
            entry_ids.append(entry_id)
            stored += 1

        elapsed = time.monotonic() - start
        return IngestResult(
            source=source,
            total_chunks=total_chunks,
            stored_chunks=stored,
            skipped_chunks=skipped,
            project=project,
            entry_ids=entry_ids,
            duration_seconds=round(elapsed, 2),
        )

    def _ingest_directory(
        self,
        directory: Path,
        project: str | None,
        scope: str,
        chunk_size: int,
        chunk_overlap: int,
        tags: list[str] | None,
        dry_run: bool,
        start: float,
    ) -> IngestResult:
        """Ingest all supported files in a directory."""
        total_chunks = 0
        stored_chunks = 0
        skipped_chunks = 0
        entry_ids: list[str] = []

        for fpath in sorted(directory.rglob("*")):
            if not fpath.is_file():
                continue
            if fpath.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            result = self.ingest(str(fpath), project, scope, chunk_size, chunk_overlap, tags, dry_run)
            total_chunks += result.total_chunks
            stored_chunks += result.stored_chunks
            skipped_chunks += result.skipped_chunks
            entry_ids.extend(result.entry_ids)

        elapsed = time.monotonic() - start
        return IngestResult(
            source=str(directory),
            total_chunks=total_chunks,
            stored_chunks=stored_chunks,
            skipped_chunks=skipped_chunks,
            project=project,
            entry_ids=entry_ids,
            duration_seconds=round(elapsed, 2),
        )

    def _store_chunk(
        self,
        chunk_text: str,
        scope: str,
        project: str | None,
        tags: list[str],
        source: str,
        source_page: int | None,
        chunk_index: int,
        chunk_total: int,
        ingested_at: str,
        title: str | None,
    ) -> str:
        """Store a single chunk as a Palaia entry with RAG frontmatter."""
        import uuid

        from palaia.entry import _to_yaml_simple, content_hash

        body = chunk_text
        h = content_hash(body)

        # Check dedup
        existing = self.store._find_by_hash(h)
        if existing:
            return existing

        now = datetime.now(timezone.utc).isoformat()
        meta = {
            "id": str(uuid.uuid4()),
            "scope": scope,
            "created": now,
            "accessed": now,
            "access_count": 1,
            "decay_score": 1.0,
            "content_hash": h,
            "tags": tags,
            "source": source,
            "chunk_index": chunk_index,
            "chunk_total": chunk_total,
            "ingested_at": ingested_at,
        }
        if project:
            meta["project"] = project
        if title:
            meta["title"] = f"{title} (chunk {chunk_index + 1}/{chunk_total})"
        if source_page is not None:
            meta["source_page"] = source_page

        fm = _to_yaml_simple(meta)
        entry_text = f"---\n{fm}\n---\n\n{body}\n"
        entry_id = meta["id"]
        target = f"hot/{entry_id}.md"

        with self.store.lock:
            from palaia.wal import WALEntry

            wal_entry = WALEntry(
                operation="write",
                target=target,
                payload_hash=h,
                payload=entry_text,
            )
            self.store.wal.log(wal_entry)
            self.store.write_raw(target, entry_text)
            self.store.wal.commit(wal_entry)

        self.store.embedding_cache.invalidate(entry_id)
        return entry_id

    def _read_source(self, source: str) -> tuple[list[_PageChunk], str]:
        """Read a source and return list of page chunks and a title.

        Returns:
            (pages, title) where pages is a list of _PageChunk.
        """
        if self._is_url(source):
            return self._read_url(source)

        path = Path(source)
        ext = path.suffix.lower()

        if ext in TEXT_EXTENSIONS:
            text = path.read_text(encoding="utf-8")
            title = path.stem
            return [_PageChunk(text=text)], title

        if ext in HTML_EXTENSIONS:
            text = path.read_text(encoding="utf-8")
            extractor = _HTMLTextExtractor()
            extractor.feed(text)
            title = extractor.get_title() or path.stem
            return [_PageChunk(text=extractor.get_text())], title

        if ext in PDF_EXTENSIONS:
            return self._read_pdf(path)

        raise ValueError(f"Unsupported file format: {ext}")

    def _read_url(self, url: str) -> tuple[list[_PageChunk], str]:
        """Fetch URL and extract text."""
        with urlopen(url) as resp:  # noqa: S310
            content_type = resp.headers.get("Content-Type", "")
            data = resp.read().decode("utf-8", errors="replace")

        if "html" in content_type or data.strip().startswith("<"):
            extractor = _HTMLTextExtractor()
            extractor.feed(data)
            title = extractor.get_title() or urlparse(url).path.split("/")[-1] or url
            return [_PageChunk(text=extractor.get_text())], title

        # Plain text
        title = urlparse(url).path.split("/")[-1] or url
        return [_PageChunk(text=data)], title

    def _read_pdf(self, path: Path) -> tuple[list[_PageChunk], str]:
        """Read a PDF file. Requires pdfplumber."""
        if not PDF_SUPPORT:
            raise ImportError(
                "PDF support requires pdfplumber. Install it with: pip install pdfplumber\n"
                "Or: pip install 'palaia[pdf]'"
            )

        pages: list[_PageChunk] = []
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages.append(_PageChunk(text=text, page=i + 1))

        title = path.stem
        return pages, title

    def _chunk_text(self, text: str, size: int, overlap: int) -> list[str]:
        """Split text into chunks of approximately `size` words with `overlap` word overlap.

        Respects sentence boundaries where possible.
        """
        if not text or not text.strip():
            return []

        # Split into sentences
        sentences = self._split_sentences(text)
        if not sentences:
            return []

        chunks: list[str] = []
        current_words: list[str] = []
        current_sentences: list[str] = []

        for sentence in sentences:
            words = sentence.split()
            if not words:
                continue

            # If adding this sentence would exceed size and we have content, start new chunk
            if current_words and len(current_words) + len(words) > size:
                chunks.append(" ".join(current_sentences))

                # Overlap: keep last `overlap` words worth of sentences
                if overlap > 0:
                    overlap_words: list[str] = []
                    overlap_sents: list[str] = []
                    for s in reversed(current_sentences):
                        s_words = s.split()
                        if len(overlap_words) + len(s_words) > overlap and overlap_words:
                            break
                        overlap_words = s_words + overlap_words
                        overlap_sents.insert(0, s)
                    current_sentences = overlap_sents
                    current_words = overlap_words
                else:
                    current_sentences = []
                    current_words = []

            current_sentences.append(sentence)
            current_words.extend(words)

        # Last chunk
        if current_sentences:
            chunks.append(" ".join(current_sentences))

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        # Split on sentence-ending punctuation followed by space or end
        parts = re.split(r"(?<=[.!?])\s+", text)
        return [p.strip() for p in parts if p.strip()]

    @staticmethod
    def _is_url(source: str) -> bool:
        """Check if source looks like a URL."""
        return source.startswith("http://") or source.startswith("https://")


def format_rag_output(query: str, results: list[dict]) -> str:
    """Format search results as RAG context block.

    Args:
        query: The original search query.
        results: Search results from SearchEngine.search().

    Returns:
        Formatted RAG context string.
    """
    lines = [f'[RAG Context for: "{query}"]']

    for r in results:
        lines.append("---")
        # Build source line
        source = r.get("source", "")
        chunk_info = ""
        if "chunk_index" in r and "chunk_total" in r:
            chunk_info = f" (chunk {r['chunk_index'] + 1}/{r['chunk_total']})"
        elif source:
            pass  # just source

        source_line = source + chunk_info if source else r.get("title", r.get("id", "unknown"))
        lines.append(f"Source: {source_line}")
        lines.append(f"Score: {r.get('score', 0)}")
        lines.append("")
        # Full body for RAG (not truncated)
        lines.append(r.get("full_body", r.get("body", "")))
        lines.append("")

    lines.append("---")
    return "\n".join(lines)
