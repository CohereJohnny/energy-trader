#!/bin/bash
# Run CFTC Parser Tests

set -e

echo "🧪 Running CFTC Parser Tests"
echo "=============================="

# Activate virtual environment
source scripts/.venv/bin/activate

# Install test dependencies if needed
pip install pytest pytest-cov --quiet

# Run tests with coverage
echo ""
echo "Running unit tests..."
python3 -m pytest scripts/test_cftc_parser.py -v --cov=scripts/cftc_parser --cov-report=term-missing

echo ""
echo "✅ Tests complete!"

