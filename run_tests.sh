#!/usr/bin/env bash

# Sierra SDK Test Runner
# Runs comprehensive test suite with coverage

set -e

echo "🧪 Sierra SDK Test Suite"
echo "========================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing..."
    pip install pytest pytest-cov pytest-mock
fi

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -q pytest pytest-cov pytest-mock httpx requests dnspython beautifulsoup4

echo ""
echo "${YELLOW}Running tests...${NC}"
echo ""

# Run tests with coverage
pytest tests/ \
    -v \
    --cov=sierra \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-branch \
    --tb=short \
    "$@"

# Show summary
echo ""
echo "${GREEN}✅ Tests complete!${NC}"
echo ""
echo "📊 Coverage report generated in: htmlcov/index.html"
echo ""
echo "To view coverage:"
echo "  open htmlcov/index.html"
echo ""
