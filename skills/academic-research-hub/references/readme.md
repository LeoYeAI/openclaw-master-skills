# Academic Research Hub

A powerful OpenClaw skill for searching and retrieving academic papers from multiple sources.

## Features

✅ **Multi-Source Search**
- arXiv (physics, CS, math, biology, finance, stats)
- PubMed (biomedical & life sciences)
- Semantic Scholar (CS & interdisciplinary)

✅ **Advanced Filtering**
- Date ranges
- Author names
- Categories/fields
- Citation counts
- Publication types

✅ **Multiple Output Formats**
- Plain text (human-readable)
- JSON (structured data)
- BibTeX (LaTeX citations)
- RIS (reference managers)
- Markdown (documentation)

✅ **PDF Download**
- Download papers from arXiv
- Batch download support
- Organized file naming

✅ **Citation Management**
- Extract citations
- Generate bibliographies
- Export to reference managers

## Installation

### Prerequisites

1. Install [OpenClawCLI](https://clawhub.ai/) for Windows or MacOS

2. Install Python dependencies:

```bash
# Standard installation
pip install -r requirements.txt

# Or install individually
pip install arxiv scholarly biopython semanticscholar requests
```

**Using Virtual Environment (Recommended):**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

⚠️ **Never use `--break-system-packages`** - use virtual environments instead!

## Quick Start

### Basic Searches

```bash
# Search arXiv
python scripts/research.py arxiv "quantum computing"

# Search PubMed
python scripts/research.py pubmed "cancer immunotherapy"

# Search Semantic Scholar
python scripts/research.py semantic "machine learning"
```

### Advanced Usage

```bash
# Filter by date
python scripts/research.py arxiv "neural networks" --year 2023

# Download papers
python scripts/research.py arxiv "transformers" --download --max-results 5

# Generate BibTeX citations
python scripts/research.py arxiv "deep learning" --format bibtex --output refs.bib

# Highly cited papers
python scripts/research.py semantic "reinforcement learning" --min-citations 500
```

## Usage Examples

### Literature Review Workflow

```bash
# Step 1: Search multiple sources
python scripts/research.py arxiv "graph neural networks" --max-results 20 --format json --output arxiv_gnn.json
python scripts/research.py semantic "graph neural networks" --max-results 20 --format json --output semantic_gnn.json

# Step 2: Download key papers
python scripts/research.py arxiv "graph neural networks" --download --max-results 10 --output-dir papers/gnn/

# Step 3: Generate bibliography
python scripts/research.py arxiv "graph neural networks" --format bibtex --output gnn_refs.bib
```

### Tracking Recent Research

```bash
# This year's papers
python scripts/research.py arxiv "large language models" --year 2024 --sort-by date

# Last 3 months in biomedicine
python scripts/research.py pubmed "gene editing" --start-date 2024-01-01 --end-date 2024-03-31
```

### Building Reference Library

```bash
# Create organized structure
mkdir -p references/{papers,citations}

# Download papers by topic
python scripts/research.py arxiv "computer vision" --download --max-results 15 --output-dir references/papers/cv/

# Generate citations
python scripts/research.py arxiv "computer vision" --format bibtex --output references/citations/cv.bib
```

## Command Reference

```bash
python scripts/research.py <source> "<query>" [OPTIONS]

SOURCES:
  arxiv              Search arXiv repository
  pubmed             Search PubMed database
  semantic           Search Semantic Scholar

OPTIONS:
  -n, --max-results  Maximum results (default: 10)
  -f, --format       Output format (text|json|bibtex|ris|markdown)
  -o, --output       Save to file
  --sort-by          Sort by (relevance|date|citations)
  
FILTERS:
  --year            Specific year (YYYY)
  --start-date      Start date (YYYY-MM-DD)
  --end-date        End date (YYYY-MM-DD)
  --author          Author name
  --min-citations   Minimum citations (Semantic Scholar)
  --category        arXiv category (e.g., cs.AI)
  --publication-type PubMed publication type
  
DOWNLOAD:
  --download        Download PDFs (arXiv only)
  --output-dir      Download directory (default: downloads/)
```

## Output Formats

### Text (Default)
Human-readable format with all metadata

### JSON
```json
{
  "title": "Paper Title",
  "authors": ["Author 1", "Author 2"],
  "published": "2024-01-15",
  "abstract": "...",
  "pdf_url": "https://..."
}
```

### BibTeX
```bibtex
@article{author2024title,
  title={Paper Title},
  author={Author, First and Author, Second},
  year={2024},
  ...
}
```

### RIS
```
TY  - JOUR
TI  - Paper Title
AU  - Author, First
PY  - 2024
...
```

### Markdown
Formatted documentation with headers and links

## Data Sources

### arXiv
- **Best for:** Physics, CS, math, quantitative fields
- **Coverage:** 2M+ preprints since 1991
- **PDF Download:** ✅ Yes
- **Full Text:** ✅ Yes

### PubMed
- **Best for:** Biomedical, life sciences, medicine
- **Coverage:** 35M+ citations
- **PDF Download:** ❌ Links only
- **Full Text:** Sometimes (via PMC)

### Semantic Scholar
- **Best for:** CS, interdisciplinary research
- **Coverage:** 200M+ papers
- **PDF Download:** ✅ When available
- **Full Text:** ✅ When open access

## Best Practices

### Search Strategy
1. Start with broad terms
2. Use multiple sources for comprehensive coverage
3. Apply date filters for recent research
4. Filter by citations for influential papers

### Download Guidelines
1. Respect rate limits
2. Only download papers you need
3. Check licensing before redistribution
4. Use organized directory structures

### Citation Management
1. Export citations as you search
2. Use BibTeX for LaTeX documents
3. Use RIS for reference managers
4. Keep abstracts for later review

## Troubleshooting

### "Library not installed"
```bash
pip install arxiv scholarly biopython semanticscholar requests
```

### "Rate limit exceeded"
- Wait a few minutes
- Reduce max-results
- Space out requests

### "Download failed"
- Check internet connection
- Some papers may not have PDFs
- Try individual downloads

### "No results found"
- Try broader search terms
- Remove restrictive filters
- Check spelling

## Limitations

- Not all papers have downloadable PDFs
- Some content requires institutional access
- Rate limits apply to prevent abuse
- Citation counts may be outdated
- Google Scholar not included (no API)

## Support

- Documentation: See SKILL.md
- Issues: Check troubleshooting section
- Dependencies: See requirements.txt
- Updates: Check OpenClawCLI updates

## License

Proprietary - See LICENSE.txt

## Credits

Built for OpenClaw using:
- [arxiv](https://pypi.org/project/arxiv/) - arXiv API wrapper
- [scholarly](https://pypi.org/project/scholarly/) - Google Scholar scraper
- [biopython](https://biopython.org/) - PubMed access
- [semanticscholar](https://pypi.org/project/semanticscholar/) - Semantic Scholar API