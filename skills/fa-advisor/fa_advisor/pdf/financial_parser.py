"""
Financial Statement Parser - Extract structured financial data from PDFs
"""

import logging
import re
from pathlib import Path
from typing import Optional, Dict, List
import pandas as pd
import camelot

from fa_advisor.types.models import FinancialStatementData, PDFExtractionResult

logger = logging.getLogger(__name__)


class FinancialStatementParser:
    """
    Specialized parser for financial statements

    Capabilities:
    - Income statement extraction
    - Balance sheet extraction
    - Cash flow statement extraction
    - Key metrics identification
    """

    def __init__(self):
        # Common financial terms to look for
        self.revenue_keywords = [
            'revenue', 'sales', 'income', 'turnover',
            '营收', '收入', '销售额'
        ]
        self.expense_keywords = [
            'expense', 'cost', 'expenditure', 'cogs',
            '费用', '成本', '支出'
        ]
        self.profit_keywords = [
            'profit', 'net income', 'earnings',
            '利润', '净利润', '净收入'
        ]

    async def parse_financial_pdf(
        self,
        pdf_path: str | Path,
        statement_type: str = 'auto'  # auto, income, balance, cashflow
    ) -> PDFExtractionResult:
        """
        Parse financial statement PDF

        Args:
            pdf_path: Path to financial PDF
            statement_type: Type of statement to parse

        Returns:
            PDFExtractionResult with financial_data populated
        """
        try:
            pdf_path = Path(pdf_path)

            # Extract tables using camelot (best for financial tables)
            tables = camelot.read_pdf(str(pdf_path), pages='all', flavor='lattice')

            if len(tables) == 0:
                # Try stream mode if lattice fails
                tables = camelot.read_pdf(str(pdf_path), pages='all', flavor='stream')

            if len(tables) == 0:
                return PDFExtractionResult(
                    success=False,
                    error="No tables found in PDF"
                )

            # Convert tables to pandas DataFrames
            dfs = [table.df for table in tables]

            # Extract financial data
            financial_data = self._extract_financial_data(dfs, statement_type)

            return PDFExtractionResult(
                success=True,
                tables=[df.values.tolist() for df in dfs],
                financial_data=financial_data
            )

        except Exception as e:
            logger.error(f"Error parsing financial PDF: {e}")
            return PDFExtractionResult(
                success=False,
                error=str(e)
            )

    def _extract_financial_data(
        self,
        dataframes: List[pd.DataFrame],
        statement_type: str
    ) -> FinancialStatementData:
        """Extract structured financial data from dataframes"""

        financial_data = FinancialStatementData()

        for df in dataframes:
            # Clean dataframe
            df = self._clean_dataframe(df)

            # Try to extract revenue
            revenue = self._find_metric(df, self.revenue_keywords)
            if revenue:
                financial_data.revenue = revenue

            # Try to extract expenses
            expenses = self._find_metric(df, self.expense_keywords)
            if expenses:
                financial_data.expenses = expenses

            # Try to extract profit
            profit = self._find_metric(df, self.profit_keywords)
            if profit:
                financial_data.profit = profit

            # Store raw table for further analysis
            if financial_data.raw_tables is None:
                financial_data.raw_tables = []
            financial_data.raw_tables.append(df.values.tolist())

        return financial_data

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize dataframe"""
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')

        # Strip whitespace from string columns
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()

        return df

    def _find_metric(
        self,
        df: pd.DataFrame,
        keywords: List[str]
    ) -> Optional[float]:
        """
        Find a financial metric in dataframe using keywords

        Returns the first numeric value found in rows containing keywords
        """
        for _, row in df.iterrows():
            row_text = ' '.join(str(cell).lower() for cell in row)

            # Check if any keyword is in this row
            if any(keyword.lower() in row_text for keyword in keywords):
                # Look for numeric values in this row
                for cell in row:
                    value = self._extract_number(str(cell))
                    if value is not None and value != 0:
                        return value

        return None

    def _extract_number(self, text: str) -> Optional[float]:
        """
        Extract number from text

        Handles formats like:
        - 1,234,567
        - $1,234,567
        - (1,234,567) [negative]
        - 1.23M, 1.23B
        """
        try:
            # Remove common currency symbols and whitespace
            text = re.sub(r'[$¥€£,\s]', '', text)

            # Handle parentheses as negative
            is_negative = False
            if '(' in text and ')' in text:
                text = text.replace('(', '').replace(')', '')
                is_negative = True

            # Handle M/B suffixes
            multiplier = 1
            if text.endswith('M') or text.endswith('m'):
                multiplier = 1_000_000
                text = text[:-1]
            elif text.endswith('B') or text.endswith('b'):
                multiplier = 1_000_000_000
                text = text[:-1]
            elif text.endswith('K') or text.endswith('k'):
                multiplier = 1_000
                text = text[:-1]

            # Try to parse as float
            number = float(text) * multiplier

            return -number if is_negative else number

        except (ValueError, AttributeError):
            return None

    def extract_metrics_summary(
        self,
        pdf_path: str | Path
    ) -> Dict[str, Optional[float]]:
        """
        Extract key financial metrics summary

        Returns:
            Dict with keys: revenue, expenses, profit, margin, growth
        """
        import asyncio
        result = asyncio.run(self.parse_financial_pdf(pdf_path))

        summary = {
            'revenue': None,
            'expenses': None,
            'profit': None,
            'margin': None,
            'growth': None
        }

        if result.success and result.financial_data:
            data = result.financial_data
            summary['revenue'] = data.revenue
            summary['expenses'] = data.expenses
            summary['profit'] = data.profit

            # Calculate margin if we have revenue and profit
            if data.revenue and data.profit:
                summary['margin'] = (data.profit / data.revenue) * 100

        return summary
