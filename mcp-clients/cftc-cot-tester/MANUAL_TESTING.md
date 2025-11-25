# Manual Testing Guide

Detailed guide for manual testing of CFTC COT MCP Server tools.

## Starting Manual Testing

```bash
python3 manual_test.py
```

## Tool Testing

### 1. get_cot_data

**Purpose**: Query COT data with flexible filtering

**Parameters**:
- `commodity` (optional): Petroleum and Products, Natural Gas and Products, Electricity
- `report_date` (optional): YYYY-MM-DD format, or leave empty for latest
- `trader_category` (optional): PRODUCER, SWAP, MANAGED_MONEY, OTHER_REPORTABLE, NONREPORTABLE
- `position_type` (optional): all, old, other (default: all)

**Example**:
```
Commodity: Petroleum and Products
Report Date: (leave empty for latest)
Trader Category: MANAGED_MONEY
Position Type: all
```

**Expected Result**:
- COT data for specified criteria
- Report date (latest if not specified)
- Positions, percentages, changes
- Citation metadata

### 2. analyze_positioning_trends

**Purpose**: Analyze positioning trends over time

**Parameters**:
- `commodity` (required): Commodity group
- `start_date` (required): YYYY-MM-DD format
- `end_date` (required): YYYY-MM-DD format
- `trader_category` (required): Trader category

**Example**:
```
Commodity: Petroleum and Products
Start Date: 2025-07-01
End Date: 2025-10-07
Trader Category: MANAGED_MONEY
```

**Expected Result**:
- Trend analysis showing start/end values
- Changes in positions (absolute and percentage)
- Citation metadata

### 3. compare_positioning

**Purpose**: Compare positioning across commodities

**Parameters**:
- `commodities` (required): Comma-separated list
- `report_date` (required): YYYY-MM-DD format
- `trader_category` (required): Trader category

**Example**:
```
Commodities: Petroleum and Products, Natural Gas and Products
Report Date: 2025-10-07
Trader Category: MANAGED_MONEY
```

**Expected Result**:
- Tabular comparison
- Long, Short, % Long, % Short for each commodity
- Citation metadata

### 4. get_positioning_extremes

**Purpose**: Find extreme positioning values

**Parameters**:
- `commodity` (required): Commodity group
- `trader_category` (required): Trader category
- `lookback_days` (optional): Days to look back (default: 365)
- `metric` (optional): long, short, net, pct_long, pct_short (default: long)

**Example**:
```
Commodity: Petroleum and Products
Trader Category: MANAGED_MONEY
Lookback Days: 365
Metric: long
```

**Expected Result**:
- Top 10 extreme positions
- Dates and values for each extreme
- Citation metadata

## Running Example Tests

Select option 5 in the menu to run all tools with example parameters. This is useful for:
- Quick validation that all tools work
- Seeing example outputs
- Testing with real data

## Interpreting Results

### Successful Response

- Contains `text` field with formatted data
- Contains `_north_metadata` with citation information
- Data is relevant to query parameters
- Citation points to CFTC source

### Error Response

- Contains `text` field with error message
- Error message is descriptive and helpful
- Still contains `_north_metadata`
- Error explains what went wrong

### Missing Data Response

- May return "No COT data found" message
- This is expected if data isn't loaded
- Response still includes citation metadata
- Not an error - just no data available

## Tips

1. **Start with latest data**: Use option 1 without specifying report_date to get latest data
2. **Use example tests**: Option 5 runs all tools with sensible defaults
3. **Check citation metadata**: Always verify CFTC attribution
4. **Test edge cases**: Try invalid dates, categories to test error handling
5. **Compare results**: Test same query with different parameters to verify consistency

## Troubleshooting

### "No COT data found"

Load data first:
```bash
cd ../../scripts
python3 load_cftc_cot_data.py --report petroleum
```

### Import errors

Ensure you're in the virtual environment:
```bash
source .venv/bin/activate
```

### Database errors

Check database is running and `.env` is configured correctly.

