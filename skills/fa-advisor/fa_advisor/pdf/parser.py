"""
PDF Parser - Extract text and tables from PDF documents
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict
import pdfplumber
from pypdf import PdfReader

from fa_advisor.types.models import PDFExtractionResult

logger = logging.getLogger(__name__)


class PDFParser:
    """
    PDF parsing service using pdfplumber and pypdf

    Capabilities:
    - Text extraction
    - Table extraction
    - Layout analysis
    - Metadata extraction
    """

    def __init__(self):
        self.supported_formats = ['.pdf']

    async def parse_pdf(
        self,
        pdf_path: str | Path,
        extract_tables: bool = True,
        extract_text: bool = True
    ) -> PDFExtractionResult:
        """
        Parse a PDF file and extract text and tables

        Args:
            pdf_path: Path to PDF file
            extract_tables: Whether to extract tables
            extract_text: Whether to extract text

        Returns:
            PDFExtractionResult with extracted data
        """
        try:
            pdf_path = Path(pdf_path)

            if not pdf_path.exists():
                return PDFExtractionResult(
                    success=False,
                    error=f"PDF file not found: {pdf_path}"
                )

            if pdf_path.suffix.lower() not in self.supported_formats:
                return PDFExtractionResult(
                    success=False,
                    error=f"Unsupported format: {pdf_path.suffix}"
                )

            text = None
            tables = None

            # Use pdfplumber for comprehensive extraction
            with pdfplumber.open(pdf_path) as pdf:
                if extract_text:
                    text = self._extract_text(pdf)

                if extract_tables:
                    tables = self._extract_tables(pdf)

            return PDFExtractionResult(
                success=True,
                text=text,
                tables=tables
            )

        except Exception as e:
            logger.error(f"Error parsing PDF {pdf_path}: {e}")
            return PDFExtractionResult(
                success=False,
                error=str(e)
            )

    def _extract_text(self, pdf: pdfplumber.PDF) -> str:
        """Extract all text from PDF"""
        text_parts = []

        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        return "\n\n".join(text_parts)

    def _extract_tables(self, pdf: pdfplumber.PDF) -> List[List[str]]:
        """Extract all tables from PDF"""
        all_tables = []

        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    # Clean and filter empty rows
                    cleaned_table = [
                        [cell if cell is not None else "" for cell in row]
                        for row in table
                        if any(cell for cell in row)  # Skip empty rows
                    ]
                    if cleaned_table:
                        all_tables.append(cleaned_table)

        return all_tables

    def extract_metadata(self, pdf_path: str | Path) -> Dict:
        """Extract PDF metadata using pypdf"""
        try:
            reader = PdfReader(pdf_path)
            metadata = reader.metadata

            return {
                'title': metadata.get('/Title', ''),
                'author': metadata.get('/Author', ''),
                'subject': metadata.get('/Subject', ''),
                'creator': metadata.get('/Creator', ''),
                'producer': metadata.get('/Producer', ''),
                'creation_date': metadata.get('/CreationDate', ''),
                'num_pages': len(reader.pages)
            }
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {}

    def extract_page(
        self,
        pdf_path: str | Path,
        page_number: int
    ) -> Optional[str]:
        """Extract text from a specific page"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if 0 <= page_number < len(pdf.pages):
                    return pdf.pages[page_number].extract_text()
                else:
                    logger.warning(f"Page {page_number} out of range")
                    return None
        except Exception as e:
            logger.error(f"Error extracting page {page_number}: {e}")
            return None

    def search_text(
        self,
        pdf_path: str | Path,
        search_term: str,
        case_sensitive: bool = False
    ) -> List[Dict]:
        """
        Search for text in PDF and return matches with page numbers

        Returns:
            List of dicts with 'page', 'text', 'context'
        """
        matches = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if not text:
                        continue

                    search_in = text if case_sensitive else text.lower()
                    term = search_term if case_sensitive else search_term.lower()

                    if term in search_in:
                        # Find context around the match
                        lines = text.split('\n')
                        for line in lines:
                            if term in (line if case_sensitive else line.lower()):
                                matches.append({
                                    'page': i + 1,
                                    'text': search_term,
                                    'context': line.strip()
                                })
        except Exception as e:
            logger.error(f"Error searching PDF: {e}")

        return matches
