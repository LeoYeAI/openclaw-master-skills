"""
PDF processing module

Handles PDF parsing, OCR, table extraction, and PDF generation
"""

from fa_advisor.pdf.parser import PDFParser
from fa_advisor.pdf.financial_parser import FinancialStatementParser
from fa_advisor.pdf.generator import PDFGenerator
from fa_advisor.pdf.ocr import OCRService

__all__ = [
    "PDFParser",
    "FinancialStatementParser",
    "PDFGenerator",
    "OCRService",
]
