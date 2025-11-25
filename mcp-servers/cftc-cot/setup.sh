#!/bin/bash
# Setup script for CFTC COT MCP Server

set -e

echo "🚀 Setting up CFTC COT MCP Server..."

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
echo "  1. Copy .env.example to .env and configure database settings"
echo "  2. Start the server: python server.py"
echo "  3. Or run with custom port: python server.py --port 5223"

