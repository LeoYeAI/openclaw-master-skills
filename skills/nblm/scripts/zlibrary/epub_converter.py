#!/usr/bin/env python3
"""
EPUB conversion utilities for Z-Library downloads.
Uses BeautifulSoup for HTML parsing.
"""

import re
from pathlib import Path


def count_words(text: str) -> int:
    """Count combined Chinese characters and English words."""
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
    return chinese_chars + english_words


def split_markdown_file(file_path: Path, max_words: int = 350000) -> list[Path]:
    """Split a large Markdown file into smaller parts."""
    content = file_path.read_text(encoding="utf-8")
    chapters = re.split(r'\n(?=#{1,3}\s)', content)

    chunks = []
    current_chunk = ""
    current_words = 0

    for chapter in chapters:
        chapter_words = count_words(chapter)

        if chapter_words > max_words:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
                current_words = 0

            paragraphs = chapter.split('\n\n')
            temp_chunk = ""
            temp_words = 0

            for para in paragraphs:
                para_words = count_words(para)
                if temp_words + para_words > max_words and temp_chunk:
                    chunks.append(temp_chunk)
                    temp_chunk = para + "\n\n"
                    temp_words = para_words
                else:
                    temp_chunk += para + "\n\n"
                    temp_words += para_words

            if temp_chunk:
                current_chunk = temp_chunk
                current_words = temp_words

        elif current_words + chapter_words > max_words:
            chunks.append(current_chunk)
            current_chunk = chapter + "\n\n"
            current_words = chapter_words
        else:
            current_chunk += chapter + "\n\n"
            current_words += chapter_words

    if current_chunk:
        chunks.append(current_chunk)

    chunk_files = []
    stem = file_path.stem
    for i, chunk in enumerate(chunks, 1):
        chunk_file = file_path.parent / f"{stem}_part{i}.md"
        chunk_file.write_text(chunk, encoding="utf-8")
        chunk_files.append(chunk_file)

    return chunk_files


def html_to_markdown(soup) -> str:
    """Convert BeautifulSoup object to Markdown."""
    markdown_parts = []

    def process_element(element):
        if element.name is None:
            text = str(element).strip()
            return text if text else ""

        if element.name in ['script', 'style', 'nav', 'footer', 'svg']:
            return ""

        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element.name[1])
            text = element.get_text().strip()
            return f"\n\n{'#' * level} {text}\n\n" if text else ""

        if element.name == 'p':
            text = element.get_text().strip()
            return f"\n\n{text}\n\n" if text else ""

        if element.name in ['b', 'strong']:
            text = element.get_text().strip()
            return f"**{text}**" if text else ""

        if element.name in ['i', 'em']:
            text = element.get_text().strip()
            return f"*{text}*" if text else ""

        if element.name == 'code':
            text = element.get_text().strip()
            return f"`{text}`" if text else ""

        if element.name == 'a':
            href = element.get('href', '')
            text = element.get_text().strip()
            if href and text:
                return f"[{text}]({href})"
            return text

        if element.name == 'ul':
            items = element.find_all('li', recursive=False)
            result = "\n\n"
            for li in items:
                text = li.get_text().strip()
                if text:
                    result += f"- {text}\n"
            return result + "\n"

        if element.name == 'ol':
            items = element.find_all('li', recursive=False)
            result = "\n\n"
            for i, li in enumerate(items, 1):
                text = li.get_text().strip()
                if text:
                    result += f"{i}. {text}\n"
            return result + "\n"

        if element.name == 'br':
            return "\n"

        if element.contents:
            result = ""
            for child in element.contents:
                result += process_element(child)
            return result

        return ""

    body = soup.find('body')
    markdown = process_element(body) if body else process_element(soup)

    markdown = re.sub(r'\n{4,}', '\n\n\n', markdown)
    markdown = re.sub(r' +', ' ', markdown)
    return markdown.strip()


def epub_to_markdown(epub_path: Path, output_path: Path) -> Path:
    """Convert EPUB to Markdown file."""
    from ebooklib import epub
    from bs4 import BeautifulSoup

    book = epub.read_epub(str(epub_path))

    title = book.get_metadata('DC', 'title')
    title_text = title[0][0] if title else "Unknown Title"
    author = book.get_metadata('DC', 'creator')
    author_text = author[0][0] if author else "Unknown Author"

    markdown_content = f"# {title_text}\n\n"
    markdown_content += f"**Author:** {author_text}\n\n"
    markdown_content += "---\n\n"

    for item in book.get_items():
        if item.get_type() == 9:  # ITEM_DOCUMENT
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            chapter_md = html_to_markdown(soup)
            if len(chapter_md.strip()) > 100:
                markdown_content += chapter_md
                markdown_content += "\n\n---\n\n"

    output_path = Path(str(output_path).replace('.txt', '.md'))
    output_path.write_text(markdown_content, encoding="utf-8")
    return output_path


def convert_epub_to_markdown(epub_path: Path, output_path: Path, max_words: int = 350000) -> list[Path]:
    """Convert EPUB to Markdown, splitting when over max_words."""
    markdown_path = epub_to_markdown(epub_path, output_path)
    word_count = count_words(markdown_path.read_text(encoding="utf-8"))
    if word_count > max_words:
        return split_markdown_file(markdown_path, max_words=max_words)
    return [markdown_path]
