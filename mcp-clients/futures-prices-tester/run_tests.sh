#!/bin/bash
# Quick test runner script

set -e

echo "🧪 Running Futures Prices MCP Server Test Suite..."
echo ""

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Setting up virtual environment..."
    uv sync
fi

# Run tests
echo "🚀 Running tests..."
uv run python test_suite.py

echo ""
echo "✅ Test suite complete!"

