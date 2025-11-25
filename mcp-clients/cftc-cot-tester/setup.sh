#!/bin/bash
# Setup script for CFTC COT MCP Client Tester

set -e

echo "🚀 Setting up CFTC COT MCP Client Tester..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create virtual environment and install dependencies
echo "📦 Creating virtual environment and installing dependencies..."
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and configure settings if needed"
echo "  2. Ensure CFTC COT MCP server is running (port 5223)"
echo "  3. Ensure CFTC COT data is loaded in database"
echo "  4. Run tests: python test_suite.py"
echo "  5. Or run manual tests: python manual_test.py"

