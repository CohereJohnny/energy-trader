# Manual Testing Guide

This guide helps you manually test the Futures Prices MCP Server interactively.

## Prerequisites

1. **Database Running**: Ensure PostgreSQL container is running
   ```bash
   docker compose ps postgres
   # If not running:
   docker compose up -d postgres
   ```

2. **Dependencies Installed**: Test client dependencies installed
   ```bash
   cd mcp-clients/futures-prices-tester
   uv sync
   ```

## Quick Start

### Option 1: Interactive Test Script (Recommended)

Run the interactive test script:

```bash
cd mcp-clients/futures-prices-tester
uv run python manual_test.py
```

This provides a menu-driven interface to test each tool with custom inputs.

### Option 2: Direct Tool Testing

You can also test tools directly in Python:

```bash
cd mcp-clients/futures-prices-tester
uv run python
```

Then in Python:
```python
import sys
sys.path.insert(0, '../../mcp-servers/futures-prices')
from tools import get_front_month_price

result = get_front_month_price('BRENT', '2010-01-04')
print(result['text'])
print(result['_north_metadata'])
```

## Test Scenarios

### Scenario 1: Single Date Price Lookup

**Test**: Get front month BRENT price for a specific date

```python
from tools import get_front_month_price

result = get_front_month_price('BRENT', '2010-01-04')
print(result['text'])
# Expected: "Front month BRENT settlement price on 2010-01-04: $85.87..."
```

**Try different dates**:
- `'2010-01-04'` - Historical data
- `'2025-01-03'` - Recent data
- `'2030-01-01'` - Future date (should handle gracefully)

**Try different commodities**:
- `'BRENT'`, `'WTI'`, `'GO'`, `'RBOB'`

### Scenario 2: Date Range Price Lookup

**Test**: Get front month prices for a date range

```python
from tools import get_front_month_prices

result = get_front_month_prices('BRENT', '2025-01-01', '2025-01-31')
print(result['text'])
# Expected: List of prices for each date in range
```

**Try different ranges**:
- 1 day: `'2025-01-01'` to `'2025-01-01'`
- 1 week: `'2025-01-01'` to `'2025-01-07'`
- 1 month: `'2025-01-01'` to `'2025-01-31'`
- 1 year: `'2025-01-01'` to `'2025-12-31'`

### Scenario 3: Price Change Calculation

**Test**: Calculate price change between two dates

```python
from tools import calculate_price_change

result = calculate_price_change('BRENT', '2025-01-03', '2025-03-31')
print(result['text'])
# Expected: Price change with absolute and percentage values
```

**Try different scenarios**:
- Positive change: `'2010-01-04'` to `'2010-01-05'`
- Negative change: Find dates where price decreased
- Same date: `'2010-01-04'` to `'2010-01-04'`

### Scenario 4: Seasonal Data

**Test**: Get seasonal data for M2 GOBRs

```python
from tools import get_seasonal_data

result = get_seasonal_data('GO', 2)  # M2 GOBRs
print(result['text'][:500])  # First 500 chars
# Expected: CSV-like format with Date, Year, Month, Price columns
```

**Try different month offsets**:
- M1: `get_seasonal_data('BRENT', 1)`
- M2: `get_seasonal_data('BRENT', 2)`
- M3: `get_seasonal_data('BRENT', 3)`

## End-to-End Query Testing

### Query 1: "What was the change in front month Brent price between January 3rd 2025 and March 31st 2025?"

```python
from tools import calculate_price_change

result = calculate_price_change('BRENT', '2025-01-03', '2025-03-31')
print(result['text'])
print("\nCitation:", result['_north_metadata'])
```

### Query 2: "What was the front month Brent Settlement yesterday?"

```python
from datetime import datetime, timedelta
from tools import get_front_month_price

yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
result = get_front_month_price('BRENT', yesterday)
print(result['text'])
```

### Query 3: "Display a seasonal chart of M2 GOBRs"

```python
from tools import get_seasonal_data

result = get_seasonal_data('GO', 2)  # M2 GOBRs
# Save to file for charting
with open('m2_gobrs_data.csv', 'w') as f:
    f.write(result['text'])
print(f"Data saved to m2_gobrs_data.csv ({len(result['text'].split(chr(10)))} lines)")
```

## Validating Responses

### Check Citation Metadata

Every response should have:
```python
assert '_north_metadata' in result
metadata = result['_north_metadata']
assert 'title' in metadata
assert 'url' in metadata
assert 'author_name' in metadata
assert 'last_updated' in metadata
assert metadata['last_updated'].endswith('Z')  # UTC timestamp
```

### Check Response Format

- `get_front_month_price`: Should contain price and contract info
- `get_front_month_prices`: Should list multiple dates with prices
- `calculate_price_change`: Should show start price, end price, absolute change, percentage change
- `get_seasonal_data`: Should be CSV-like format with headers

## Troubleshooting

### Database Connection Error
```bash
# Check if database is running
docker compose ps postgres

# Check database connection
docker compose exec postgres psql -U postgres -d energy_trader -c "SELECT COUNT(*) FROM futures_prices.prices;"
```

### Import Errors
```bash
# Make sure you're in the right directory
cd mcp-clients/futures-prices-tester

# Install dependencies
uv sync
```

### No Data Returned
- Check if date is within data range (2010-01-04 to 2025-11-05)
- Check if date is a trading day (weekends/holidays may not have data)
- Verify commodity code is correct (BRENT, WTI, GO, RBOB)

## Next Steps

After manual testing:
1. Verify all tools work as expected
2. Check citation metadata format
3. Test edge cases (invalid inputs, missing data)
4. Proceed to Sprint 4: AI Agent Integration

