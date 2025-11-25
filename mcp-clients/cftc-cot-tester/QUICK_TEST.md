# Quick Test Guide

Quick start guide for testing CFTC COT MCP Server.

## Prerequisites

1. CFTC COT data loaded in database:
   ```bash
   cd ../../scripts
   python3 load_cftc_cot_data.py --report petroleum
   ```

2. Virtual environment set up:
   ```bash
   ./setup.sh
   source .venv/bin/activate
   ```

## Quick Test

Run the comprehensive test suite:

```bash
./run_tests.sh
```

Expected output:
- Tests for all 4 tools
- Parameter validation
- Edge case handling
- Citation metadata checks
- Performance benchmarks

## Manual Testing

For interactive testing:

```bash
python3 manual_test.py
```

Select option 5 to run example tests with predefined parameters.

## MCP Inspector

For visual testing:

1. Start MCP server:
   ```bash
   cd ../../mcp-servers/cftc-cot
   python server.py --port 5223
   ```

2. Use MCP Inspector with `mcp_inspector_config.json`

## Example Queries

### get_cot_data
```python
get_cot_data(
    commodity="Petroleum and Products",
    trader_category="MANAGED_MONEY"
)
```

### analyze_positioning_trends
```python
analyze_positioning_trends(
    commodity="Petroleum and Products",
    start_date="2025-07-01",
    end_date="2025-10-07",
    trader_category="MANAGED_MONEY"
)
```

### compare_positioning
```python
compare_positioning(
    commodities="Petroleum and Products, Natural Gas and Products",
    report_date="2025-10-07",
    trader_category="MANAGED_MONEY"
)
```

### get_positioning_extremes
```python
get_positioning_extremes(
    commodity="Petroleum and Products",
    trader_category="MANAGED_MONEY",
    lookback_days=365,
    metric="long"
)
```

