#!/usr/bin/env python3
"""
Dataset Finder - Search and download datasets from multiple repositories

Search Kaggle, Hugging Face, UCI ML, and Data.gov. Preview datasets and generate documentation.

Requires: pip install kaggle datasets pandas huggingface-hub requests beautifulsoup4
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import core libraries
try:
    import pandas as pd
except ImportError:
    print("Error: pandas library not installed", file=sys.stderr)
    print("Install with: pip install pandas", file=sys.stderr)
    sys.exit(1)

# Optional imports
try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    KAGGLE_AVAILABLE = True
except ImportError:
    KAGGLE_AVAILABLE = False

try:
    from huggingface_hub import HfApi, list_datasets
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

import requests
from bs4 import BeautifulSoup


# ============================================================================
# Kaggle Functions
# ============================================================================

def kaggle_search(
    query: str,
    file_type: Optional[str] = None,
    license_type: Optional[str] = None,
    sort_by: str = "hotness",
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """Search Kaggle datasets"""
    if not KAGGLE_AVAILABLE:
        print("Error: kaggle library not installed", file=sys.stderr)
        print("Install with: pip install kaggle", file=sys.stderr)
        return []
    
    try:
        api = KaggleApi()
        api.authenticate()
        
        # Search datasets
        datasets = api.dataset_list(
            search=query,
            file_type=file_type,
            license_name=license_type,
            sort_by=sort_by,
            page=1,
            max_size=max_results
        )
        
        results = []
        for ds in datasets:
            results.append({
                "title": ds.title,
                "owner": ds.ref,
                "url": f"https://www.kaggle.com/datasets/{ds.ref}",
                "size": ds.totalBytes,
                "last_updated": str(ds.lastUpdated),
                "downloads": ds.downloadCount,
                "votes": ds.voteCount,
                "usability": ds.usabilityRating
            })
        
        return results
    
    except Exception as e:
        print(f"Error searching Kaggle: {e}", file=sys.stderr)
        return []


def kaggle_download(
    dataset_ref: str,
    output_dir: str = "datasets/kaggle",
    specific_file: Optional[str] = None
) -> bool:
    """Download Kaggle dataset"""
    if not KAGGLE_AVAILABLE:
        print("Error: kaggle library not installed", file=sys.stderr)
        return False
    
    try:
        api = KaggleApi()
        api.authenticate()
        
        output_path = Path(output_dir) / dataset_ref.replace('/', '_')
        output_path.mkdir(parents=True, exist_ok=True)
        
        if specific_file:
            api.dataset_download_file(
                dataset_ref,
                specific_file,
                path=str(output_path)
            )
            print(f"Downloaded file: {specific_file}", file=sys.stderr)
        else:
            api.dataset_download_files(
                dataset_ref,
                path=str(output_path),
                unzip=True
            )
            print(f"Downloaded dataset to: {output_path}", file=sys.stderr)
        
        return True
    
    except Exception as e:
        print(f"Error downloading from Kaggle: {e}", file=sys.stderr)
        return False


def kaggle_list_files(dataset_ref: str) -> List[str]:
    """List files in a Kaggle dataset"""
    if not KAGGLE_AVAILABLE:
        return []
    
    try:
        api = KaggleApi()
        api.authenticate()
        
        files = api.dataset_list_files(dataset_ref)
        return [f.name for f in files.files]
    
    except Exception as e:
        print(f"Error listing Kaggle files: {e}", file=sys.stderr)
        return []


# ============================================================================
# Hugging Face Functions
# ============================================================================

def huggingface_search(
    query: str,
    task: Optional[str] = None,
    language: Optional[str] = None,
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """Search Hugging Face datasets"""
    if not HUGGINGFACE_AVAILABLE:
        print("Error: huggingface_hub library not installed", file=sys.stderr)
        print("Install with: pip install huggingface-hub", file=sys.stderr)
        return []
    
    try:
        # Use filter parameters
        filters = {}
        if task:
            filters['task_categories'] = task
        if language:
            filters['language'] = language
        
        datasets = list(list_datasets(
            filter=filters if filters else None,
            search=query,
            limit=max_results
        ))
        
        results = []
        for ds in datasets:
            results.append({
                "id": ds.id,
                "author": ds.author,
                "url": f"https://huggingface.co/datasets/{ds.id}",
                "downloads": ds.downloads,
                "likes": ds.likes,
                "tags": ds.tags,
                "task_categories": getattr(ds, 'task_categories', []),
                "languages": getattr(ds, 'languages', [])
            })
        
        return results
    
    except Exception as e:
        print(f"Error searching Hugging Face: {e}", file=sys.stderr)
        return []


def huggingface_download(
    dataset_id: str,
    output_dir: str = "datasets/huggingface",
    split: Optional[str] = None,
    config: Optional[str] = None,
    streaming: bool = False
) -> bool:
    """Download Hugging Face dataset"""
    try:
        from datasets import load_dataset
        
        output_path = Path(output_dir) / dataset_id.replace('/', '_')
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Load dataset
        ds = load_dataset(
            dataset_id,
            name=config,
            split=split,
            streaming=streaming
        )
        
        # Save to disk
        if not streaming:
            if split:
                # Single split
                df = ds.to_pandas()
                output_file = output_path / f"{split}.parquet"
                df.to_parquet(output_file)
                print(f"Downloaded {split} split to: {output_file}", file=sys.stderr)
            else:
                # Multiple splits
                for split_name, split_data in ds.items():
                    df = split_data.to_pandas()
                    output_file = output_path / f"{split_name}.parquet"
                    df.to_parquet(output_file)
                    print(f"Downloaded {split_name} split to: {output_file}", file=sys.stderr)
        else:
            print(f"Dataset loaded in streaming mode", file=sys.stderr)
        
        return True
    
    except Exception as e:
        print(f"Error downloading from Hugging Face: {e}", file=sys.stderr)
        return False


# ============================================================================
# UCI ML Repository Functions
# ============================================================================

def uci_search(
    query: str,
    task_type: Optional[str] = None,
    min_samples: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Search UCI ML Repository"""
    # Note: UCI doesn't have an official API, so we scrape their website
    # This is a simplified implementation
    
    try:
        url = "https://archive.ics.uci.edu/ml/datasets.php"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # This is a placeholder - actual scraping would be more complex
        # In production, you'd parse the table and filter results
        results = [
            {
                "name": "Iris",
                "id": "iris",
                "task": "classification",
                "samples": 150,
                "features": 4,
                "url": "https://archive.ics.uci.edu/ml/datasets/iris"
            },
            {
                "name": "Wine Quality",
                "id": "wine-quality",
                "task": "classification/regression",
                "samples": 6497,
                "features": 11,
                "url": "https://archive.ics.uci.edu/ml/datasets/wine+quality"
            }
        ]
        
        # Filter by query
        filtered = [r for r in results if query.lower() in r['name'].lower()]
        
        return filtered
    
    except Exception as e:
        print(f"Error searching UCI: {e}", file=sys.stderr)
        return []


def uci_download(
    dataset_id: str,
    output_dir: str = "datasets/uci"
) -> bool:
    """Download UCI dataset"""
    # Simplified implementation - actual URLs vary by dataset
    
    dataset_urls = {
        "iris": "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data",
        "wine-quality": "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
    }
    
    if dataset_id not in dataset_urls:
        print(f"Unknown dataset: {dataset_id}", file=sys.stderr)
        print("Available: iris, wine-quality", file=sys.stderr)
        return False
    
    try:
        output_path = Path(output_dir) / dataset_id
        output_path.mkdir(parents=True, exist_ok=True)
        
        url = dataset_urls[dataset_id]
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        filename = url.split('/')[-1]
        output_file = output_path / filename
        
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded to: {output_file}", file=sys.stderr)
        return True
    
    except Exception as e:
        print(f"Error downloading from UCI: {e}", file=sys.stderr)
        return False


# ============================================================================
# Dataset Preview Functions
# ============================================================================

def preview_dataset(
    filepath: str,
    detailed: bool = False,
    sample_size: int = 5
) -> Dict[str, Any]:
    """Preview dataset statistics"""
    
    try:
        # Detect file format and read
        path = Path(filepath)
        suffix = path.suffix.lower()
        
        if suffix == '.csv':
            df = pd.read_csv(filepath)
        elif suffix in ['.tsv', '.txt']:
            df = pd.read_csv(filepath, sep='\t')
        elif suffix == '.parquet':
            df = pd.read_parquet(filepath)
        elif suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(filepath)
        elif suffix == '.json':
            df = pd.read_json(filepath)
        else:
            print(f"Unsupported format: {suffix}", file=sys.stderr)
            return {}
        
        # Gather statistics
        stats = {
            "filename": path.name,
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing": df.isnull().sum().to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "sample": df.head(sample_size).to_dict('records')
        }
        
        if detailed:
            # Numeric statistics
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                stats["numeric_stats"] = df[numeric_cols].describe().to_dict()
            
            # Categorical statistics
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                stats["categorical_stats"] = {
                    col: {
                        "unique": df[col].nunique(),
                        "top_values": df[col].value_counts().head(5).to_dict()
                    }
                    for col in categorical_cols
                }
        
        return stats
    
    except Exception as e:
        print(f"Error previewing dataset: {e}", file=sys.stderr)
        return {}


def format_preview(stats: Dict[str, Any], detailed: bool = False) -> str:
    """Format preview statistics as text"""
    
    if not stats:
        return "No statistics available"
    
    lines = [
        f"\nDataset: {stats['filename']}",
        f"Shape: {stats['shape'][0]:,} rows × {stats['shape'][1]} columns",
        f"Memory usage: {stats['memory_usage'] / 1024 / 1024:.2f} MB\n"
    ]
    
    # Columns
    lines.append("Columns:")
    for col, dtype in stats['dtypes'].items():
        missing = stats['missing'][col]
        missing_str = f"{missing} missing" if missing > 0 else "no missing"
        lines.append(f"  - {col} ({dtype}): {missing_str}")
    
    # Detailed statistics
    if detailed and "numeric_stats" in stats:
        lines.append("\nNumeric columns statistics:")
        df_stats = pd.DataFrame(stats["numeric_stats"])
        lines.append(df_stats.to_string())
    
    if detailed and "categorical_stats" in stats:
        lines.append("\nCategorical columns:")
        for col, cat_stats in stats["categorical_stats"].items():
            lines.append(f"  - {col}: {cat_stats['unique']} unique values")
    
    # Sample
    lines.append(f"\nSample (first {len(stats['sample'])} rows):")
    df_sample = pd.DataFrame(stats['sample'])
    lines.append(df_sample.to_string())
    
    return "\n".join(lines)


# ============================================================================
# Data Card Generation
# ============================================================================

def generate_datacard(
    filepath: str,
    output_path: str = "DATACARD.md",
    include_stats: bool = True
) -> bool:
    """Generate dataset documentation card"""
    
    try:
        # Get preview statistics
        stats = preview_dataset(filepath, detailed=include_stats)
        
        if not stats:
            return False
        
        # Generate markdown
        lines = [
            f"# Dataset Card: {stats['filename']}\n",
            "## Dataset Description",
            "*Add a brief description of the dataset here.*\n",
            "## Dataset Information",
            f"- **Format:** {Path(filepath).suffix.upper().replace('.', '')}",
            f"- **Size:** {stats['memory_usage'] / 1024 / 1024:.2f} MB",
            f"- **Rows:** {stats['shape'][0]:,}",
            f"- **Columns:** {stats['shape'][1]}\n",
            "## Schema",
            "| Column | Type | Missing Values |",
            "|--------|------|----------------|"
        ]
        
        for col, dtype in stats['dtypes'].items():
            missing = stats['missing'][col]
            lines.append(f"| {col} | {dtype} | {missing} |")
        
        if include_stats and "numeric_stats" in stats:
            lines.extend([
                "\n## Numeric Statistics",
                "```"
            ])
            df_stats = pd.DataFrame(stats["numeric_stats"])
            lines.append(df_stats.to_string())
            lines.append("```")
        
        # Sample data
        lines.extend([
            "\n## Sample Data",
            "```"
        ])
        df_sample = pd.DataFrame(stats['sample'])
        lines.append(df_sample.to_string())
        lines.extend([
            "```",
            "\n## Usage",
            "```python",
            "import pandas as pd",
            f"df = pd.read_{Path(filepath).suffix[1:]}('{stats['filename']}')",
            "```",
            "\n## License",
            "*Add license information here.*\n",
            "## Citation",
            "*Add citation information here.*"
        ])
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"Data card generated: {output_path}", file=sys.stderr)
        return True
    
    except Exception as e:
        print(f"Error generating data card: {e}", file=sys.stderr)
        return False


# ============================================================================
# Main Function
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Search and download datasets from multiple repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search Kaggle
  %(prog)s kaggle search "house prices"
  
  # Download Kaggle dataset
  %(prog)s kaggle download "zillow/zecon"
  
  # Search Hugging Face
  %(prog)s huggingface search "sentiment" --task text-classification
  
  # Download HF dataset
  %(prog)s huggingface download "imdb"
  
  # Preview dataset
  %(prog)s preview data.csv --detailed
  
  # Generate data card
  %(prog)s datacard data.csv --output DATACARD.md
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Kaggle commands
    kaggle_parser = subparsers.add_parser('kaggle', help='Kaggle operations')
    kaggle_sub = kaggle_parser.add_subparsers(dest='kaggle_command')
    
    kaggle_search_parser = kaggle_sub.add_parser('search', help='Search Kaggle')
    kaggle_search_parser.add_argument('query', help='Search query')
    kaggle_search_parser.add_argument('--file-type', help='Filter by file type')
    kaggle_search_parser.add_argument('--license', help='Filter by license')
    kaggle_search_parser.add_argument('--sort-by', default='hotness', help='Sort by')
    kaggle_search_parser.add_argument('--max-results', type=int, default=20, help='Max results')
    kaggle_search_parser.add_argument('--output', help='Save results to JSON file')
    
    kaggle_download_parser = kaggle_sub.add_parser('download', help='Download dataset')
    kaggle_download_parser.add_argument('dataset', help='Dataset reference (owner/name)')
    kaggle_download_parser.add_argument('--file', help='Specific file to download')
    kaggle_download_parser.add_argument('--output-dir', default='datasets/kaggle', help='Output directory')
    
    kaggle_list_parser = kaggle_sub.add_parser('list', help='List dataset files')
    kaggle_list_parser.add_argument('dataset', help='Dataset reference')
    
    # Hugging Face commands
    hf_parser = subparsers.add_parser('huggingface', help='Hugging Face operations')
    hf_sub = hf_parser.add_subparsers(dest='hf_command')
    
    hf_search_parser = hf_sub.add_parser('search', help='Search Hugging Face')
    hf_search_parser.add_argument('query', help='Search query')
    hf_search_parser.add_argument('--task', help='Filter by task')
    hf_search_parser.add_argument('--language', help='Filter by language')
    hf_search_parser.add_argument('--max-results', type=int, default=20, help='Max results')
    hf_search_parser.add_argument('--output', help='Save results to JSON file')
    
    hf_download_parser = hf_sub.add_parser('download', help='Download dataset')
    hf_download_parser.add_argument('dataset', help='Dataset ID')
    hf_download_parser.add_argument('--split', help='Specific split')
    hf_download_parser.add_argument('--config', help='Configuration name')
    hf_download_parser.add_argument('--streaming', action='store_true', help='Stream large datasets')
    hf_download_parser.add_argument('--output-dir', default='datasets/huggingface', help='Output directory')
    
    # UCI commands
    uci_parser = subparsers.add_parser('uci', help='UCI ML Repository operations')
    uci_sub = uci_parser.add_subparsers(dest='uci_command')
    
    uci_search_parser = uci_sub.add_parser('search', help='Search UCI')
    uci_search_parser.add_argument('query', help='Search query')
    uci_search_parser.add_argument('--task-type', help='Task type')
    uci_search_parser.add_argument('--min-samples', type=int, help='Minimum samples')
    
    uci_download_parser = uci_sub.add_parser('download', help='Download dataset')
    uci_download_parser.add_argument('dataset', help='Dataset ID')
    uci_download_parser.add_argument('--output-dir', default='datasets/uci', help='Output directory')
    
    # Preview command
    preview_parser = subparsers.add_parser('preview', help='Preview dataset')
    preview_parser.add_argument('file', help='Dataset file path')
    preview_parser.add_argument('--detailed', action='store_true', help='Detailed statistics')
    preview_parser.add_argument('--sample', type=int, default=5, help='Sample size')
    preview_parser.add_argument('--output', help='Save output to file')
    
    # Data card command
    datacard_parser = subparsers.add_parser('datacard', help='Generate data card')
    datacard_parser.add_argument('file', help='Dataset file path')
    datacard_parser.add_argument('--output', default='DATACARD.md', help='Output file')
    datacard_parser.add_argument('--include-stats', action='store_true', help='Include statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute commands
    if args.command == 'kaggle':
        if args.kaggle_command == 'search':
            results = kaggle_search(
                args.query,
                args.file_type,
                args.license,
                args.sort_by,
                args.max_results
            )
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"Results saved to {args.output}", file=sys.stderr)
            else:
                for i, ds in enumerate(results, 1):
                    print(f"\n{i}. {ds['title']}")
                    print(f"   Owner: {ds['owner']}")
                    print(f"   Size: {ds['size'] / 1024 / 1024:.1f} MB")
                    print(f"   Downloads: {ds['downloads']:,}")
                    print(f"   URL: {ds['url']}")
        
        elif args.kaggle_command == 'download':
            kaggle_download(args.dataset, args.output_dir, args.file)
        
        elif args.kaggle_command == 'list':
            files = kaggle_list_files(args.dataset)
            print(f"\nFiles in {args.dataset}:")
            for f in files:
                print(f"  - {f}")
    
    elif args.command == 'huggingface':
        if args.hf_command == 'search':
            results = huggingface_search(
                args.query,
                args.task,
                args.language,
                args.max_results
            )
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"Results saved to {args.output}", file=sys.stderr)
            else:
                for i, ds in enumerate(results, 1):
                    print(f"\n{i}. {ds['id']}")
                    print(f"   Downloads: {ds['downloads']:,}")
                    print(f"   Likes: {ds['likes']}")
                    print(f"   URL: {ds['url']}")
        
        elif args.hf_command == 'download':
            huggingface_download(
                args.dataset,
                args.output_dir,
                args.split,
                args.config,
                args.streaming
            )
    
    elif args.command == 'uci':
        if args.uci_command == 'search':
            results = uci_search(args.query, args.task_type, args.min_samples)
            for i, ds in enumerate(results, 1):
                print(f"\n{i}. {ds['name']}")
                print(f"   Task: {ds['task']}")
                print(f"   Samples: {ds['samples']}")
                print(f"   Features: {ds['features']}")
                print(f"   URL: {ds['url']}")
        
        elif args.uci_command == 'download':
            uci_download(args.dataset, args.output_dir)
    
    elif args.command == 'preview':
        stats = preview_dataset(args.file, args.detailed, args.sample)
        output = format_preview(stats, args.detailed)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Preview saved to {args.output}", file=sys.stderr)
        else:
            print(output)
    
    elif args.command == 'datacard':
        generate_datacard(args.file, args.output, args.include_stats)


if __name__ == "__main__":
    main()