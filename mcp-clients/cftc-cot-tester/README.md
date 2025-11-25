# CFTC COT MCP Client Tester

MCP client and test suite for end-to-end testing of the CFTC COT MCP Server.

## Overview

This directory contains:
- Comprehensive test suite for validating all CFTC COT MCP tools
- Manual testing script for interactive tool testing
- MCP Inspector configuration for visual testing
- Performance and error handling tests
- End-to-end scenario tests

## Setup

### Prerequisites

- Python 3.10+
- `uv` package manager (recommended) or `pip`
- CFTC COT MCP server running (see `mcp-servers/cftc-cot/`)
- CFTC COT data loaded in PostgreSQL database

### Installation

```bash
cd mcp-clients/cftc-cot-tester

# Using uv (recommended)
./setup.sh

# Or using pip
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running Tests

### Comprehensive Test Suite

This tests the tool functions directly (bypassing MCP protocol):

```bash
./run_tests.sh
# Or directly:
python3 test_suite.py
```

This will test:
- All 4 CFTC COT tools (`get_cot_data`, `analyze_positioning_trends`, `compare_positioning`, `get_positioning_extremes`)
- All parameter combinations
- All commodity groups (Petroleum, Natural Gas, Electricity)
- All trader categories (PRODUCER, SWAP, MANAGED_MONEY, OTHER_REPORTABLE, NONREPORTABLE)
- Edge cases (invalid dates, categories, missing data)
- Citation metadata format
- Performance benchmarks
- End-to-end scenarios

### Manual Testing

For interactive testing:

```bash
python3 manual_test.py
```

This provides an interactive menu to:
- Test individual tools with custom parameters
- See formatted results
- Run example tests with predefined parameters

### MCP Inspector Testing

For visual testing via MCP Inspector:

1. Ensure MCP server is running:
   ```bash
   cd ../../mcp-servers/cftc-cot
   python server.py --port 5223
   ```

2. Use MCP Inspector with `mcp_inspector_config.json`:
   - The config file is already set up for the CFTC COT server
   - Connect to the server and test tools interactively

## Test Coverage

### Tool Tests

1. **get_cot_data**:
   - With all parameters
   - With latest report date (no date specified)
   - With specific commodity groups
   - With all trader categories
   - With all position types (all, old, other)
   - Edge cases (invalid dates, categories)

2. **analyze_positioning_trends**:
   - Valid date ranges
   - Different commodity groups
   - Different trader categories
   - Edge cases (invalid dates, date ordering)

3. **compare_positioning**:
   - Multiple commodities comparison
   - Different trader categories
   - Edge cases (invalid commodities, dates)

4. **get_positioning_extremes**:
   - Different metrics (long, short, net, pct_long, pct_short)
   - Different lookback periods
   - Different commodity groups and trader categories
   - Edge cases (invalid metric, lookback)

### Validation

All tests validate:
- Response structure (text, _north_metadata)
- Citation metadata format (title, url, author_name, last_updated)
- CFTC source attribution
- Error handling and messages
- Performance (query response times)

## Test Results

### Viewing Results

After running tests, results are available in:

1. **Console Output**: Summary printed to terminal
   - Shows test execution progress
   - Displays final summary (passed/failed counts, duration)

2. **TEST_REPORT.md**: Detailed markdown report (auto-generated)
   - Test summary (passed/failed counts, duration)
   - Test results grouped by tool category
   - Failed test details (if any)
   - Individual test status and messages

```bash
# View test report
cat TEST_REPORT.md

# Or open in editor
code TEST_REPORT.md
```

3. **TEST_RESULTS_SUMMARY.md**: High-level summary
   - Current test status
   - Coverage breakdown
   - Performance metrics
   - Data status

### Current Test Status

**Latest Results**: 34 tests, 100% passing, 0.21 seconds

See `TEST_REPORT.md` for detailed results after running tests.

### Expected Test Results

When CFTC COT data is loaded:
- All tool tests should pass
- Responses should contain COT data
- Citation metadata should reference CFTC
- TEST_REPORT.md will show ✅ PASS for most tests

When no data is loaded:
- Tests should handle missing data gracefully
- Error messages should be informative
- Citation metadata should still be present
- TEST_REPORT.md will show ⚠️ warnings for missing data (not failures)

### Test Coverage

See `TEST_COVERAGE.md` for:
- Current test coverage analysis
- Areas needing additional tests
- Recommendations for improving coverage
- Priority list for new tests

## Troubleshooting

### "No COT data found" errors

Ensure CFTC COT data is loaded:
```bash
cd ../../scripts
python3 load_cftc_cot_data.py --report petroleum
```

### Database connection errors

Check database configuration in `.env` file:
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

### Import errors

Ensure virtual environment is activated:
```bash
source .venv/bin/activate
```

Or install dependencies:
```bash
pip install -r requirements.txt
```

## Files

- `test_suite.py` - Comprehensive automated test suite
- `manual_test.py` - Interactive manual testing script
- `mcp_inspector_config.json` - MCP Inspector configuration
- `run_tests.sh` - Test runner script
- `setup.sh` - Setup script
- `README.md` - This file

## Related

- CFTC COT MCP Server: `../../mcp-servers/cftc-cot/`
- Data Loader: `../../scripts/load_cftc_cot_data.py`
- Database Schema: `../../database/migrations/002_create_cftc_cot_schema.sql`

