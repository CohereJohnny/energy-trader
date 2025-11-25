#!/bin/bash
# Test runner script for CFTC COT MCP Client Tester

set -e

echo "🧪 Running CFTC COT MCP Server Test Suite"
echo "=========================================="

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run test suite
echo ""
echo "Running comprehensive test suite..."
python3 test_suite.py

echo ""
echo "✅ Tests complete!"
echo ""
echo "📊 Test Report: See TEST_REPORT.md for detailed results"
echo ""
echo "For manual testing, run: python3 manual_test.py"
echo "For MCP Inspector testing, use: mcp_inspector_config.json"
echo "For coverage analysis, see: TEST_COVERAGE.md"

