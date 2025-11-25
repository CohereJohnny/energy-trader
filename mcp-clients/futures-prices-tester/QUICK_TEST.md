# Quick Manual Testing Guide

## Start Manual Testing

### Step 1: Verify Database is Running
```bash
docker compose ps postgres
# Should show: Up X hours (healthy)
```

### Step 2: Run Interactive Test Script
```bash
cd mcp-clients/futures-prices-tester
uv run python manual_test.py
```

### Step 3: Follow the Menu

The script will show a menu:
```
============================================================
SELECT TEST:
============================================================
1. get_front_month_price (single date)
2. get_front_month_prices (date range)
3. calculate_price_change
4. get_seasonal_data
5. End-to-end scenarios
6. Exit
============================================================
```

## Quick Test Examples

### Test 1: Get BRENT Price for Specific Date
1. Select option `1`
2. Commodity: `BRENT` (or press Enter for default)
3. Date: `2010-01-04` (or press Enter for default)
4. Review the response and citation metadata

### Test 2: Get Price Range
1. Select option `2`
2. Commodity: `BRENT`
3. Start date: `2025-01-01`
4. End date: `2025-01-31`
5. Review the list of prices

### Test 3: Calculate Price Change
1. Select option `3`
2. Commodity: `BRENT`
3. Start date: `2025-01-03`
4. End date: `2025-03-31`
5. Review the price change calculation

### Test 4: Seasonal Data (M2 GOBRs)
1. Select option `4`
2. Commodity: `GO`
3. Month offset: `2` (for M2)
4. Review the CSV-like data output

### Test 5: End-to-End Scenarios
1. Select option `5`
2. Choose scenario 1, 2, 3, or `all`
3. Review the results

## What to Check

For each test, verify:
- ✅ Response contains expected data
- ✅ Citation metadata (`_north_metadata`) is present
- ✅ Citation has all fields: `title`, `url`, `author_name`, `last_updated`
- ✅ Timestamp ends with `Z` (UTC format)
- ✅ Error messages are clear (if testing invalid inputs)

## Tips

- Use default values (press Enter) for quick testing
- Try edge cases: invalid commodities, future dates, invalid date ranges
- Check the citation metadata format matches North MCP specification
- Test all 4 commodities: BRENT, WTI, GO, RBOB

