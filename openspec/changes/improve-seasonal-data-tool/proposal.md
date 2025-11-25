## Why
The current `get_seasonal_data` tool returns excessive raw data (30,000+ lines of daily prices) that is difficult for traders to interpret and inefficient for AI agents to process. Traders need aggregated seasonal statistics (monthly averages, min/max, patterns) rather than raw daily price data to identify recurring patterns and inform trading strategies. The tool should provide actionable insights, not just data dumps.

## What Changes
- **MODIFIED**: `get_seasonal_data` tool behavior - default to aggregated statistics instead of raw data
- **ADDED**: Date range filtering parameters (`start_year`, `end_year`) to limit data scope
- **ADDED**: Output format options (`aggregated`, `data-points`, `raw`) to support different use cases:
  - `aggregated` (default): Returns aggregated statistics (min, max, avg, std dev, median)
  - `data-points`: Returns actual sampled data points (e.g., last trading day of each month) without aggregation
  - `raw`: Returns all daily prices (backward compatible)
- **ADDED**: Data point granularity parameter (`points_per_year`) to control sampling frequency:
  - `12` (default): 1 data point per month (monthly aggregation)
  - `24`: 2 data points per month (mid-month and end-of-month)
  - `52`: Weekly sampling (1 data point per week)
- **ADDED**: Monthly aggregation statistics (min, max, average, standard deviation) grouped by expiration month
- **ADDED**: Pattern detection insights (e.g., "January prices typically X% higher than December")
- **ADDED**: Data sampling logic for mid-month and weekly intervals
- **MODIFIED**: Database query function to support aggregation, filtering, and sampling
- **MODIFIED**: Tool response format to include summary statistics and insights

## Impact
- Affected specs: `futures-prices` capability
- Affected code:
  - `mcp-servers/futures-prices/tools.py` - `get_seasonal_data` function
  - `mcp-servers/futures-prices/db.py` - `get_contract_prices_by_month_offset` function
  - Database queries for aggregated statistics
- Dependencies: None (uses existing database schema)
- Breaking changes: Default behavior changes from raw data to aggregated statistics (backward compatible via `format` parameter)

