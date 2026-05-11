#!/usr/bin/env bash
# Setup virtual environment for Options Spread Conviction Engine
# This isolates dependencies to avoid system conflicts (numba/numpy)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$HOME/.openclaw/venvs/options-spread-conviction-engine"

echo "📊 Setting up Options Spread Conviction Engine..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is required but not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# Activate and install dependencies
echo "Installing dependencies (this may take a minute)..."
source "$VENV_DIR/bin/activate"

# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install numpy first (required by pandas_ta)
echo "Installing numpy..."
pip install numpy

# Install pandas and yfinance
echo "Installing pandas and yfinance..."
pip install pandas yfinance

# Install pandas_ta without numba (Python 3.14+ compatibility)
echo "Installing pandas_ta (pure Python mode, numba not available for Python 3.14)..."
NUMBA_DISABLE_JIT=1 pip install pandas_ta --no-deps
pip install scipy tqdm  # Required dependencies

echo "✅ Setup complete!"
echo ""
echo "Virtual environment: $VENV_DIR"
echo "Python: $(which python3)"
echo ""
echo "Test with: conviction-engine AAPL"
