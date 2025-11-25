# CFTC COT MCP Server

MCP server for querying CFTC Commitment of Traders (COT) data.

## Features

This MCP server provides access to CFTC Disaggregated Commitment of Traders data for:
- Petroleum and Products
- Natural Gas and Products
- Electricity

## Tools

### 1. `get_cot_data`
Get CFTC COT data for specified criteria.

**Parameters:**
- `commodity` (optional): Commodity group
- `report_date` (optional): Report date in YYYY-MM-DD format (defaults to latest)
- `trader_category` (optional): Trader category (PRODUCER, SWAP, MANAGED_MONEY, OTHER_REPORTABLE, NONREPORTABLE)
- `position_type` (optional): Position type ('all', 'old', 'other') - defaults to 'all'

**Example:**
```python
get_cot_data(
    commodity="Petroleum and Products",
    report_date="2025-10-07",
    trader_category="MANAGED_MONEY"
)
```

### 2. `analyze_positioning_trends`
Analyze positioning trends for a commodity and trader category over time.

**Parameters:**
- `commodity`: Commodity group
- `start_date`: Start date in YYYY-MM-DD format
- `end_date`: End date in YYYY-MM-DD format
- `trader_category`: Trader category

**Example:**
```python
analyze_positioning_trends(
    commodity="Petroleum and Products",
    start_date="2025-01-01",
    end_date="2025-10-07",
    trader_category="MANAGED_MONEY"
)
```

### 3. `compare_positioning`
Compare positioning across multiple commodities on a given date.

**Parameters:**
- `commodities`: Comma-separated list of commodity groups
- `report_date`: Report date in YYYY-MM-DD format
- `trader_category`: Trader category

**Example:**
```python
compare_positioning(
    commodities="Petroleum and Products, Natural Gas and Products",
    report_date="2025-10-07",
    trader_category="MANAGED_MONEY"
)
```

### 4. `get_positioning_extremes`
Get positioning extremes for a commodity and trader category.

**Parameters:**
- `commodity`: Commodity group
- `trader_category`: Trader category
- `lookback_days` (optional): Number of days to look back (default: 365)
- `metric` (optional): Metric to find extremes for ('long', 'short', 'net', 'pct_long', 'pct_short') - defaults to 'long'

**Example:**
```python
get_positioning_extremes(
    commodity="Petroleum and Products",
    trader_category="MANAGED_MONEY",
    lookback_days=365,
    metric="long"
)
```

### 5. `get_loaded_data_status`
Query what CFTC COT data has been loaded and processed from the CFTC website.

**Parameters:**
- `commodity` (optional): Filter by commodity group
- `start_date` (optional): Start date filter in YYYY-MM-DD format
- `end_date` (optional): End date filter in YYYY-MM-DD format
- `status` (optional): Filter by loading status ('pending', 'downloading', 'parsing', 'loading', 'completed', 'failed')
- `identify_gaps` (optional): Whether to identify missing reports (default: False)

**Example:**
```python
get_loaded_data_status(
    commodity="Petroleum and Products",
    start_date="2025-01-01",
    end_date="2025-03-31",
    identify_gaps=True
)
```

**Returns:**
- Overall coverage statistics (total reports, date range, commodity groups, markets)
- Loading status counts
- Commodity-specific statistics
- Filtered list of loaded reports (if filters provided)
- Loading log entries (if status filter provided)
- Missing reports (if identify_gaps=True)

## CLI Tool

A command-line script is available for querying loaded data status locally:

```bash
python scripts/query_cftc_loaded_data.py [options]
```

### CLI Options

- `--summary`: Show summary statistics
- `--reports`: List loaded reports
- `--commodity COMMODITY`: Filter by commodity group
- `--start-date YYYY-MM-DD`: Start date filter
- `--end-date YYYY-MM-DD`: End date filter
- `--status STATUS`: Filter by loading status ('pending', 'downloading', 'parsing', 'loading', 'completed', 'failed')
- `--missing`: Identify missing reports
- `--json`: Output in JSON format
- `--limit N`: Limit number of results shown (default: 50)

### CLI Examples

```bash
# Show summary statistics
python scripts/query_cftc_loaded_data.py --summary

# List all loaded reports
python scripts/query_cftc_loaded_data.py --reports

# Filter by commodity
python scripts/query_cftc_loaded_data.py --commodity "Petroleum and Products"

# Filter by date range
python scripts/query_cftc_loaded_data.py --start-date 2025-01-01 --end-date 2025-03-31

# Show failed loading attempts
python scripts/query_cftc_loaded_data.py --status failed

# Find missing reports
python scripts/query_cftc_loaded_data.py --missing

# JSON output for automation
python scripts/query_cftc_loaded_data.py --summary --json
```

## Setup

1. **Install dependencies:**
   ```bash
   ./setup.sh
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database settings
   ```

3. **Start the server:**
   ```bash
   source .venv/bin/activate
   python server.py
   ```

## Database Requirements

The server requires a PostgreSQL database with the `cftc_cot` schema. See `database/migrations/002_create_cftc_cot_schema.sql` for the schema definition.

## Data Loading

Before using the server, load CFTC COT data using:
```bash
python scripts/load_cftc_cot_data.py --report petroleum
```

## Citation Metadata

All tool responses include citation metadata (`_north_metadata`) pointing to CFTC as the data source.

