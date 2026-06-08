#!/usr/bin/env python3
"""
Academic Research Hub - Multi-Source Academic Paper Search

Search and retrieve academic papers from arXiv, PubMed, Semantic Scholar, and more.
Download PDFs, extract citations, and generate bibliographies.

Requires: pip install arxiv scholarly pubmed-parser semanticscholar requests
"""

import argparse
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum

# Import handlers
try:
    import arxiv
except ImportError:
    arxiv = None

try:
    from semanticscholar import SemanticScholar
except ImportError:
    SemanticScholar = None

try:
    from Bio import Entrez
except ImportError:
    Entrez = None

import requests


class Source(Enum):
    """Available research sources"""
    ARXIV = "arxiv"
    PUBMED = "pubmed"
    SEMANTIC = "semantic"


class OutputFormat(Enum):
    """Available output formats"""
    TEXT = "text"
    JSON = "json"
    BIBTEX = "bibtex"
    RIS = "ris"
    MARKDOWN = "markdown"


def check_dependencies(source: Source):
    """Check if required dependencies are installed"""
    if source == Source.ARXIV and arxiv is None:
        print("Error: arxiv library not installed", file=sys.stderr)
        print("Install with: pip install arxiv", file=sys.stderr)
        sys.exit(1)
    
    if source == Source.SEMANTIC and SemanticScholar is None:
        print("Error: semanticscholar library not installed", file=sys.stderr)
        print("Install with: pip install semanticscholar", file=sys.stderr)
        sys.exit(1)
    
    if source == Source.PUBMED and Entrez is None:
        print("Error: biopython library not installed", file=sys.stderr)
        print("Install with: pip install biopython", file=sys.stderr)
        sys.exit(1)


# ============================================================================
# arXiv Search Functions
# ============================================================================

def search_arxiv(
    query: str,
    max_results: int = 10,
    category: Optional[str] = None,
    author: Optional[str] = None,
    year: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: str = "relevance"
) -> List[Dict[str, Any]]:
    """Search arXiv repository"""
    
    # Build query
    search_query = query
    
    if category:
        search_query = f"cat:{category} AND {query}"
    
    if author:
        search_query = f"{search_query} AND au:{author}"
    
    # Determine sort order
    sort_order = arxiv.SortCriterion.Relevance
    if sort_by == "date":
        sort_order = arxiv.SortCriterion.SubmittedDate
    
    try:
        search = arxiv.Search(
            query=search_query,
            max_results=max_results,
            sort_by=sort_order
        )
        
        results = []
        for paper in search.results():
            # Filter by date if specified
            pub_date = paper.published.date()
            
            if year and pub_date.year != year:
                continue
            
            if start_date:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                if pub_date < start:
                    continue
            
            if end_date:
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                if pub_date > end:
                    continue
            
            results.append({
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "published": paper.published.strftime("%Y-%m-%d"),
                "updated": paper.updated.strftime("%Y-%m-%d"),
                "arxiv_id": paper.entry_id.split("/")[-1],
                "categories": paper.categories,
                "abstract": paper.summary,
                "pdf_url": paper.pdf_url,
                "doi": paper.doi,
                "primary_category": paper.primary_category,
                "comment": paper.comment,
                "journal_ref": paper.journal_ref
            })
        
        return results
    
    except Exception as e:
        print(f"Error searching arXiv: {e}", file=sys.stderr)
        return []


def download_arxiv_papers(papers: List[Dict[str, Any]], output_dir: str):
    """Download arXiv papers as PDFs"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    downloaded = 0
    for paper in papers:
        arxiv_id = paper["arxiv_id"]
        title = paper["title"][:100]  # Truncate long titles
        # Clean filename
        filename = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
        filepath = output_path / f"{arxiv_id}_{filename}.pdf"
        
        try:
            # Download PDF
            pdf_url = paper["pdf_url"]
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            print(f"Downloaded: {filepath.name}", file=sys.stderr)
            downloaded += 1
        
        except Exception as e:
            print(f"Failed to download {arxiv_id}: {e}", file=sys.stderr)
    
    print(f"\nDownloaded {downloaded}/{len(papers)} papers to {output_dir}", file=sys.stderr)


# ============================================================================
# PubMed Search Functions
# ============================================================================

def search_pubmed(
    query: str,
    max_results: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    publication_type: Optional[str] = None,
    author: Optional[str] = None,
    email: str = "user@example.com"  # Required by NCBI
) -> List[Dict[str, Any]]:
    """Search PubMed database"""
    
    # Set email for Entrez (required by NCBI)
    Entrez.email = email
    
    # Build query
    search_query = query
    
    if publication_type:
        search_query = f"{search_query} AND {publication_type}[Publication Type]"
    
    if author:
        search_query = f"{search_query} AND {author}[Author]"
    
    # Add date range
    date_filter = ""
    if start_date and end_date:
        date_filter = f"{start_date}:{end_date}[Date - Publication]"
    elif start_date:
        date_filter = f"{start_date}:3000[Date - Publication]"
    elif end_date:
        date_filter = f"1900:{end_date}[Date - Publication]"
    
    if date_filter:
        search_query = f"{search_query} AND {date_filter}"
    
    try:
        # Search for PMIDs
        handle = Entrez.esearch(db="pubmed", term=search_query, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        
        pmids = record["IdList"]
        
        if not pmids:
            return []
        
        # Fetch details
        handle = Entrez.efetch(db="pubmed", id=pmids, rettype="medline", retmode="text")
        records = handle.read()
        handle.close()
        
        # Parse results (simplified - would need proper MEDLINE parser)
        results = []
        for pmid in pmids:
            # Fetch individual record in XML for easier parsing
            handle = Entrez.efetch(db="pubmed", id=pmid, rettype="abstract", retmode="xml")
            record = Entrez.read(handle)
            handle.close()
            
            article = record["PubmedArticle"][0]["MedlineCitation"]["Article"]
            
            # Extract authors
            authors = []
            if "AuthorList" in article:
                for author in article["AuthorList"]:
                    if "LastName" in author and "Initials" in author:
                        authors.append(f"{author['LastName']} {author['Initials']}")
            
            # Extract abstract
            abstract = ""
            if "Abstract" in article and "AbstractText" in article["Abstract"]:
                abstract = " ".join(str(text) for text in article["Abstract"]["AbstractText"])
            
            # Extract publication date
            pub_date = ""
            if "Journal" in article and "JournalIssue" in article["Journal"]:
                issue = article["Journal"]["JournalIssue"]
                if "PubDate" in issue:
                    date = issue["PubDate"]
                    year = date.get("Year", "")
                    month = date.get("Month", "")
                    day = date.get("Day", "")
                    pub_date = f"{year}-{month}-{day}".strip("-")
            
            # Extract DOI
            doi = ""
            if "ELocationID" in article:
                for eid in article["ELocationID"]:
                    if eid.attributes.get("EIdType") == "doi":
                        doi = str(eid)
            
            results.append({
                "title": str(article.get("ArticleTitle", "No title")),
                "authors": authors,
                "journal": str(article.get("Journal", {}).get("Title", "")),
                "published": pub_date,
                "pmid": pmid,
                "doi": doi,
                "abstract": abstract,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            })
        
        return results
    
    except Exception as e:
        print(f"Error searching PubMed: {e}", file=sys.stderr)
        return []


# ============================================================================
# Semantic Scholar Search Functions
# ============================================================================

def search_semantic(
    query: str,
    max_results: int = 10,
    year: Optional[int] = None,
    min_citations: Optional[int] = None,
    author: Optional[str] = None,
    sort_by: str = "relevance"
) -> List[Dict[str, Any]]:
    """Search Semantic Scholar"""
    
    try:
        sch = SemanticScholar()
        
        # Search papers
        results = sch.search_paper(query, limit=max_results)
        
        papers = []
        for paper in results:
            # Get detailed info
            paper_id = paper.paperId
            details = sch.get_paper(paper_id)
            
            # Filter by year
            if year and details.year != year:
                continue
            
            # Filter by citations
            if min_citations and (details.citationCount or 0) < min_citations:
                continue
            
            # Filter by author
            if author and details.authors:
                author_match = any(
                    author.lower() in a.name.lower()
                    for a in details.authors
                )
                if not author_match:
                    continue
            
            # Extract data
            authors = [a.name for a in details.authors] if details.authors else []
            
            papers.append({
                "title": details.title,
                "authors": authors,
                "published": str(details.year) if details.year else "Unknown",
                "paper_id": details.paperId,
                "citations": details.citationCount or 0,
                "influential_citations": details.influentialCitationCount or 0,
                "fields": [f.name for f in details.fieldsOfStudy] if details.fieldsOfStudy else [],
                "abstract": details.abstract or "",
                "doi": details.doi or "",
                "arxiv_id": details.externalIds.get("ArXiv") if details.externalIds else None,
                "url": details.url or f"https://www.semanticscholar.org/paper/{details.paperId}",
                "pdf_url": details.openAccessPdf.get("url") if details.openAccessPdf else None
            })
        
        # Sort results
        if sort_by == "citations":
            papers.sort(key=lambda p: p["citations"], reverse=True)
        elif sort_by == "date":
            papers.sort(key=lambda p: p["published"], reverse=True)
        
        return papers[:max_results]
    
    except Exception as e:
        print(f"Error searching Semantic Scholar: {e}", file=sys.stderr)
        return []


# ============================================================================
# Output Formatting Functions
# ============================================================================

def format_text(papers: List[Dict[str, Any]], source: Source) -> str:
    """Format results as plain text"""
    if not papers:
        return "No results found."
    
    lines = [f"Search Results: {len(papers)} papers found\n"]
    
    for i, paper in enumerate(papers, 1):
        lines.append(f"\n{i}. {paper['title']}")
        
        if "authors" in paper:
            authors = ", ".join(paper["authors"][:5])
            if len(paper["authors"]) > 5:
                authors += " et al."
            lines.append(f"   Authors: {authors}")
        
        if "published" in paper:
            lines.append(f"   Published: {paper['published']}")
        
        if source == Source.ARXIV:
            lines.append(f"   arXiv ID: {paper.get('arxiv_id', 'N/A')}")
            lines.append(f"   Categories: {', '.join(paper.get('categories', []))}")
        
        elif source == Source.PUBMED:
            lines.append(f"   Journal: {paper.get('journal', 'N/A')}")
            lines.append(f"   PMID: {paper.get('pmid', 'N/A')}")
            if paper.get('doi'):
                lines.append(f"   DOI: {paper['doi']}")
        
        elif source == Source.SEMANTIC:
            lines.append(f"   Paper ID: {paper.get('paper_id', 'N/A')}")
            lines.append(f"   Citations: {paper.get('citations', 0)}")
            if paper.get('fields'):
                lines.append(f"   Fields: {', '.join(paper['fields'])}")
        
        if "abstract" in paper and paper["abstract"]:
            abstract = paper["abstract"][:300]
            if len(paper["abstract"]) > 300:
                abstract += "..."
            lines.append(f"   Abstract: {abstract}")
        
        # Add URLs
        if "pdf_url" in paper and paper["pdf_url"]:
            lines.append(f"   PDF: {paper['pdf_url']}")
        if "url" in paper:
            lines.append(f"   URL: {paper['url']}")
    
    return "\n".join(lines)


def format_json_output(papers: List[Dict[str, Any]]) -> str:
    """Format results as JSON"""
    return json.dumps(papers, indent=2, ensure_ascii=False)


def format_bibtex(papers: List[Dict[str, Any]], source: Source) -> str:
    """Format results as BibTeX"""
    entries = []
    
    for paper in papers:
        # Generate citation key
        first_author = paper.get("authors", ["Unknown"])[0].split()[-1].lower()
        year = paper.get("published", "0000")[:4]
        title_word = paper.get("title", "").split()[0].lower()
        key = f"{first_author}{year}{title_word}"
        
        # Build entry
        entry = f"@article{{{key},\n"
        entry += f"  title={{{paper.get('title', 'No title')}}},\n"
        
        if paper.get("authors"):
            authors = " and ".join(paper["authors"])
            entry += f"  author={{{authors}}},\n"
        
        entry += f"  year={{{year}}},\n"
        
        if source == Source.ARXIV:
            entry += f"  journal={{arXiv preprint}},\n"
            if paper.get("arxiv_id"):
                entry += f"  volume={{arXiv:{paper['arxiv_id']}}},\n"
        
        elif source == Source.PUBMED:
            if paper.get("journal"):
                entry += f"  journal={{{paper['journal']}}},\n"
            if paper.get("pmid"):
                entry += f"  note={{PMID: {paper['pmid']}}},\n"
        
        if paper.get("doi"):
            entry += f"  doi={{{paper['doi']}}},\n"
        
        if paper.get("url"):
            entry += f"  url={{{paper['url']}}},\n"
        
        entry = entry.rstrip(",\n") + "\n}\n"
        entries.append(entry)
    
    return "\n".join(entries)


def format_ris(papers: List[Dict[str, Any]], source: Source) -> str:
    """Format results as RIS"""
    entries = []
    
    for paper in papers:
        entry = "TY  - JOUR\n"
        entry += f"TI  - {paper.get('title', 'No title')}\n"
        
        for author in paper.get("authors", []):
            entry += f"AU  - {author}\n"
        
        year = paper.get("published", "0000")[:4]
        entry += f"PY  - {year}\n"
        
        if paper.get("published"):
            entry += f"DA  - {paper['published']}\n"
        
        if source == Source.ARXIV:
            entry += "JO  - arXiv preprint\n"
            if paper.get("arxiv_id"):
                entry += f"VL  - arXiv:{paper['arxiv_id']}\n"
        
        elif source == Source.PUBMED:
            if paper.get("journal"):
                entry += f"JO  - {paper['journal']}\n"
        
        if paper.get("doi"):
            entry += f"DO  - {paper['doi']}\n"
        
        if paper.get("abstract"):
            entry += f"AB  - {paper['abstract']}\n"
        
        if paper.get("url"):
            entry += f"UR  - {paper['url']}\n"
        
        entry += "ER  -\n\n"
        entries.append(entry)
    
    return "".join(entries)


def format_markdown(papers: List[Dict[str, Any]], source: Source) -> str:
    """Format results as Markdown"""
    if not papers:
        return "# Search Results\n\nNo results found."
    
    lines = [f"# Search Results: {len(papers)} papers found\n"]
    
    for i, paper in enumerate(papers, 1):
        lines.append(f"\n## {i}. {paper['title']}\n")
        
        if paper.get("authors"):
            authors = ", ".join(paper["authors"][:5])
            if len(paper["authors"]) > 5:
                authors += " et al."
            lines.append(f"**Authors:** {authors}\n")
        
        if paper.get("published"):
            lines.append(f"**Published:** {paper['published']}\n")
        
        if source == Source.ARXIV:
            lines.append(f"**arXiv ID:** {paper.get('arxiv_id', 'N/A')}\n")
            lines.append(f"**Categories:** {', '.join(paper.get('categories', []))}\n")
        
        elif source == Source.PUBMED:
            lines.append(f"**Journal:** {paper.get('journal', 'N/A')}\n")
            lines.append(f"**PMID:** {paper.get('pmid', 'N/A')}\n")
            if paper.get("doi"):
                lines.append(f"**DOI:** {paper['doi']}\n")
        
        elif source == Source.SEMANTIC:
            lines.append(f"**Citations:** {paper.get('citations', 0)}\n")
            if paper.get("fields"):
                lines.append(f"**Fields:** {', '.join(paper['fields'])}\n")
        
        if paper.get("abstract"):
            lines.append(f"**Abstract:** {paper['abstract']}\n")
        
        if paper.get("pdf_url"):
            lines.append(f"**PDF:** [Download]({paper['pdf_url']})\n")
        if paper.get("url"):
            lines.append(f"**URL:** {paper['url']}\n")
    
    return "\n".join(lines)


def format_output(papers: List[Dict[str, Any]], format_type: OutputFormat, source: Source) -> str:
    """Format results according to specified format"""
    if format_type == OutputFormat.JSON:
        return format_json_output(papers)
    elif format_type == OutputFormat.BIBTEX:
        return format_bibtex(papers, source)
    elif format_type == OutputFormat.RIS:
        return format_ris(papers, source)
    elif format_type == OutputFormat.MARKDOWN:
        return format_markdown(papers, source)
    else:  # TEXT
        return format_text(papers, source)


# ============================================================================
# Main Function
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Search academic papers from multiple sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search arXiv
  %(prog)s arxiv "quantum computing" --max-results 10
  
  # Search PubMed with date filter
  %(prog)s pubmed "covid vaccine" --start-date 2023-01-01 --end-date 2023-12-31
  
  # Search Semantic Scholar, highly cited papers
  %(prog)s semantic "machine learning" --min-citations 100
  
  # Download arXiv papers
  %(prog)s arxiv "deep learning" --download --max-results 5
  
  # Generate BibTeX citations
  %(prog)s arxiv "transformers" --format bibtex --output refs.bib
        """
    )
    
    # Source selection
    parser.add_argument(
        "source",
        choices=["arxiv", "pubmed", "semantic"],
        help="Research source to search"
    )
    
    # Required arguments
    parser.add_argument(
        "query",
        type=str,
        help="Search query"
    )
    
    # General options
    parser.add_argument(
        "-n", "--max-results",
        type=int,
        default=10,
        help="Maximum number of results (default: 10)"
    )
    
    parser.add_argument(
        "-f", "--format",
        type=str,
        choices=["text", "json", "bibtex", "ris", "markdown"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Save results to file"
    )
    
    parser.add_argument(
        "--sort-by",
        type=str,
        choices=["relevance", "date", "citations"],
        default="relevance",
        help="Sort results by (default: relevance)"
    )
    
    # Filtering options
    parser.add_argument(
        "--year",
        type=int,
        help="Filter by specific year"
    )
    
    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--end-date",
        type=str,
        help="End date (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--author",
        type=str,
        help="Filter by author name"
    )
    
    # arXiv-specific options
    parser.add_argument(
        "--category",
        type=str,
        help="arXiv category (e.g., cs.AI, cs.LG)"
    )
    
    # PubMed-specific options
    parser.add_argument(
        "--publication-type",
        type=str,
        help="PubMed publication type filter"
    )
    
    # Semantic Scholar-specific options
    parser.add_argument(
        "--min-citations",
        type=int,
        help="Minimum citation count"
    )
    
    # Download options
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download paper PDFs (arXiv only)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="downloads",
        help="Directory for downloaded PDFs (default: downloads/)"
    )
    
    args = parser.parse_args()
    
    # Determine source
    source = Source(args.source)
    
    # Check dependencies
    check_dependencies(source)
    
    # Perform search
    papers = []
    
    if source == Source.ARXIV:
        papers = search_arxiv(
            query=args.query,
            max_results=args.max_results,
            category=args.category,
            author=args.author,
            year=args.year,
            start_date=args.start_date,
            end_date=args.end_date,
            sort_by=args.sort_by
        )
        
        if args.download and papers:
            download_arxiv_papers(papers, args.output_dir)
    
    elif source == Source.PUBMED:
        papers = search_pubmed(
            query=args.query,
            max_results=args.max_results,
            start_date=args.start_date,
            end_date=args.end_date,
            publication_type=args.publication_type,
            author=args.author
        )
    
    elif source == Source.SEMANTIC:
        papers = search_semantic(
            query=args.query,
            max_results=args.max_results,
            year=args.year,
            min_citations=args.min_citations,
            author=args.author,
            sort_by=args.sort_by
        )
    
    # Format output
    output_format = OutputFormat(args.format)
    formatted_output = format_output(papers, output_format, source)
    
    # Save or print results
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(formatted_output)
            print(f"Results saved to: {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error saving to file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(formatted_output)


if __name__ == "__main__":
    main()