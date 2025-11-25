#!/bin/bash
# Setup script for Futures Prices MCP Server

set -e

echo "🚀 Setting up Futures Prices MCP Server..."

# Check if uv is installed
if command -v uv &> /dev/null; then
    echo "✓ Using uv package manager"
    
    # Create virtual environment and install dependencies
    echo "📦 Installing dependencies with uv..."
    uv sync
    
    # Install North MCP SDK into the virtual environment
    echo "📦 Installing North MCP Python SDK..."
    uv pip install --python .venv/bin/python git+ssh://git@github.com/cohere-ai/north-mcp-python-sdk.git
    
    echo ""
    echo "✓ Setup complete!"
    echo ""
    echo "To activate the virtual environment:"
    echo "  source .venv/bin/activate"
    echo ""
    echo "To run the server:"
    echo "  python server.py"
    
elif command -v python3 &> /dev/null; then
    echo "⚠️  uv not found, using pip instead"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate and install
    echo "📦 Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    
    echo ""
    echo "✓ Setup complete!"
    echo ""
    echo "To activate the virtual environment:"
    echo "  source venv/bin/activate"
    echo ""
    echo "To run the server:"
    echo "  python server.py"
else
    echo "❌ Error: Neither uv nor python3 found"
    echo "Please install Python 3.11+ or uv"
    exit 1
fi

