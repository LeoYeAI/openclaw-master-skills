#!/usr/bin/env python3
"""
AI Rankings Leaderboard Query Tool
Fetches model rankings, model IDs, and pricing from OpenRouter and Pinchbench
"""

import sys
import json
import argparse
from urllib.request import urlopen, Request
from datetime import datetime

# OpenRouter API endpoints (no auth needed for public data)
OPENROUTER_MODELS_API = "https://openrouter.ai/api/v1/models"
OPENROUTER_RANKINGS_URL = "https://openrouter.ai/rankings"
PINCHBENCH_URL = "https://pinchbench.com/"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json'
}


def fetch_json(url):
    """Fetch JSON data from API"""
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def get_all_models():
    """Get all models from OpenRouter API"""
    print("Fetching models from OpenRouter API...")
    data = fetch_json(OPENROUTER_MODELS_API)
    
    if not data or 'data' not in data:
        print("Failed to fetch models from API")
        return []
    
    models = []
    for model in data['data']:
        models.append({
            'id': model.get('id', ''),
            'name': model.get('name', model.get('id', '')),
            'provider': model.get('id', '').split('/')[0] if '/' in model.get('id', '') else 'unknown',
            'context_length': model.get('context_length', 0),
            'pricing': {
                'input': model.get('pricing', {}).get('prompt', '0'),
                'output': model.get('pricing', {}).get('completion', '0')
            },
            'top_provider': model.get('top_provider', {}),
            'per_request_limits': model.get('per_request_limits', {}),
            'architecture': model.get('architecture', {})
        })
    
    return models


def get_free_models():
    """Get free models from OpenRouter"""
    models = get_all_models()
    free_models = []
    
    for m in models:
        input_price = float(m['pricing']['input'] or 0)
        output_price = float(m['pricing']['output'] or 0)
        
        if input_price == 0 and output_price == 0:
            free_models.append(m)
    
    return free_models


def search_models(query):
    """Search models by name or ID"""
    models = get_all_models()
    query_lower = query.lower()
    
    results = []
    for m in models:
        if query_lower in m['id'].lower() or query_lower in m['name'].lower():
            results.append(m)
    
    return results


def format_pricing(price_str):
    """Format pricing string"""
    if not price_str:
        return "$0"
    try:
        price = float(price_str)
        if price == 0:
            return "FREE"
        return f"${price * 1000000:.2f}/M"
    except:
        return price_str


def print_models_table(models, title="Models"):
    """Print models in table format"""
    if not models:
        print(f"No {title.lower()} found")
        return
    
    print("=" * 80)
    print(f"    {title}")
    print("=" * 80)
    print()
    
    for i, m in enumerate(models[:20], 1):  # Limit to 20 for readability
        print(f"{i}. {m['name']}")
        print(f"   Model ID: {m['id']}")
        print(f"   Context: {m['context_length']:,} tokens" if m['context_length'] else "   Context: N/A")
        
        input_price = format_pricing(m['pricing']['input'])
        output_price = format_pricing(m['pricing']['output'])
        print(f"   Pricing: Input {input_price} | Output {output_price}")
        print()
    
    if len(models) > 20:
        print(f"... and {len(models) - 20} more models")
    
    print("=" * 80)
    print(f"Total: {len(models)} models")
    print(f"Query time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


def print_model_detail(model):
    """Print detailed model info"""
    print("=" * 60)
    print(f"    {model['name']}")
    print("=" * 60)
    print()
    print(f"Model ID: {model['id']}")
    print(f"Provider: {model['provider']}")
    print(f"Context Length: {model['context_length']:,} tokens" if model['context_length'] else "Context Length: N/A")
    print()
    
    input_price = format_pricing(model['pricing']['input'])
    output_price = format_pricing(model['pricing']['output'])
    print(f"Pricing:")
    print(f"  Input:  {input_price}")
    print(f"  Output: {output_price}")
    print()
    
    # Architecture info
    arch = model.get('architecture', {})
    if arch:
        print("Architecture:")
        if arch.get('modality'):
            print(f"  Modality: {arch.get('modality')}")
        if arch.get('tokenizer'):
            print(f"  Tokenizer: {arch.get('tokenizer')}")
    
    print()
    print("=" * 60)
    print("API Usage Example (for reference only, this script does not require API key):")
    print("=" * 60)
    print(f'''
curl https://openrouter.ai/api/v1/chat/completions \\
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{model['id']}",
    "messages": [{{"role": "user", "content": "Hello"}}]
  }}'
''')


def main():
    parser = argparse.ArgumentParser(description='AI Rankings Leaderboard Query Tool')
    parser.add_argument('--free', action='store_true', help='List free models only')
    parser.add_argument('--search', '-s', type=str, help='Search models by name or ID')
    parser.add_argument('--id', type=str, help='Get model by exact ID')
    parser.add_argument('--all', action='store_true', help='List all models')
    parser.add_argument('--limit', '-l', type=int, default=20, help='Limit number of results')
    args = parser.parse_args()
    
    if args.id:
        # Get specific model by ID
        models = get_all_models()
        model = next((m for m in models if m['id'] == args.id), None)
        if model:
            print_model_detail(model)
        else:
            print(f"Model not found: {args.id}")
            print("Try --search to find similar models")
    
    elif args.search:
        # Search models
        results = search_models(args.search)
        print_models_table(results, f"Search Results for '{args.search}'")
    
    elif args.free:
        # List free models
        free = get_free_models()
        print_models_table(free, "Free Models on OpenRouter")
    
    elif args.all:
        # List all models
        models = get_all_models()
        print_models_table(models[:args.limit], "All Models on OpenRouter")
    
    else:
        # Default: show help
        parser.print_help()
        print()
        print("Examples:")
        print("  python3 query_leaderboard.py --free              # List free models")
        print("  python3 query_leaderboard.py -s gpt              # Search for GPT models")
        print("  python3 query_leaderboard.py -s glm              # Search for GLM models")
        print("  python3 query_leaderboard.py --id openai/gpt-4o  # Get specific model info")


if __name__ == "__main__":
    main()
