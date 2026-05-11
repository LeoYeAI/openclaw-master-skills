#!/bin/bash

# Test Auto-Routing Feature
# Tests various query types to verify routing works correctly

# Load from environment or .env file
if [ -f .env ]; then
  source .env
fi

# Check required keys
if [ -z "$SERPER_API_KEY" ]; then
  echo "Error: SERPER_API_KEY not set. Copy .env.example to .env and add your keys."
  exit 1
fi

echo "Testing auto-routing..."
python3 scripts/search.py -q "buy iPhone 15 price" --auto
python3 scripts/search.py -q "how does quantum computing work" --auto  
python3 scripts/search.py -q "companies like Stripe" --auto
