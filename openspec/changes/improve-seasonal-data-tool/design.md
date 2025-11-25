## Context
The `get_seasonal_data` tool currently returns all daily prices for a contract month offset across all years (30,000+ lines). This is:
- Too much data for AI agents to process efficiently
- Difficult for traders to interpret without aggregation
- Not aligned with how traders actually use seasonal data (looking for patterns, not raw data)

Traders use seasonal data to:
- Identify recurring patterns (e.g., "January prices are typically 5% higher than December")
- Compare same periods across different years
- Make trading decisions based on historical averages and ranges
- Understand volatility patterns by month

## Goals / Non-Goals

### Goals
- Reduce response size from 30k+ lines to < 500 lines for typical use cases
- Provide aggregated statistics (min, max, average, std dev) by expiration month
- Enable date range filtering to focus on relevant periods
- Detect and highlight significant seasonal patterns
- Maintain backward compatibility for users who need raw data

### Non-Goals
- Real-time visualization (that's a frontend concern)
- Complex statistical analysis beyond basic aggregations
- Multi-commodity comparisons (single commodity focus)
- Predictive modeling (just historical analysis)

## Decisions

### Decision 1: Default to Aggregated Statistics
**What**: Default behavior returns monthly aggregated statistics instead of raw daily prices.

**Why**: 
- Traders need patterns, not raw data
- Reduces response size by 99%+
- More actionable insights
- AI agents can process summaries more effectively

**Alternatives considered**:
- Keep raw as default, add aggregated option: Rejected - aggregated is the primary use case
- Always return both: Rejected - doubles response size unnecessarily

### Decision 2: Configurable Data Point Granularity
**What**: Add `points_per_year` parameter to control sampling frequency:
- `12` (default): 1 data point per month (monthly aggregation)
- `24`: 2 data points per month (mid-month ~15th and end-of-month)
- `52`: Weekly sampling (1 data point per week)

**Why**:
- Provides flexibility for different analysis needs
- Monthly (12/year) is sufficient for most seasonal pattern analysis
- Higher frequency (24/year, 52/year) useful for intra-month volatility analysis
- Balances detail vs. response size

**Sampling Strategy**:
- **12/year (monthly)**: Use last trading day of each month, aggregate by expiration month
- **24/year (bi-monthly)**: Use ~15th of month (or nearest trading day) and last trading day of month
- **52/year (weekly)**: Use same day of week each week (e.g., Friday close), or first trading day of each week

**Statistics to include** (per sampling period):
- Count: Number of data points
- Average: Mean price for the period
- Min: Lowest price observed
- Max: Highest price observed
- Std Dev: Standard deviation (volatility indicator)
- Median: Middle value (less affected by outliers)

**Alternatives considered**:
- Fixed monthly only: Rejected - traders may need higher frequency for some analysis
- Daily sampling: Rejected - defeats purpose of reducing data volume
- User-defined intervals: Rejected - too complex, standard options are sufficient

### Decision 3: Date Range Filtering
**What**: Add optional `start_year` and `end_year` parameters to limit data scope.

**Why**:
- Traders typically analyze 5-10 years of data
- Reduces data volume further
- Allows focusing on recent trends vs historical patterns
- Default: all available years (maintains current behavior)

**Alternatives considered**:
- Date range by trade date: Rejected - expiration year is more meaningful for seasonal analysis
- Fixed window (e.g., last 5 years): Rejected - traders need flexibility

### Decision 4: Pattern Detection
**What**: Identify and highlight significant seasonal patterns (e.g., "January prices are typically X% higher than December").

**Why**:
- Provides actionable insights
- Helps traders quickly identify opportunities
- Reduces need for manual analysis

**Pattern detection approach**:
- Compare average prices between consecutive months
- Calculate percentage differences
- Highlight differences > 5% (configurable threshold)
- Format as natural language insights

**Alternatives considered**:
- Complex statistical tests: Rejected - too complex, may overfit
- No pattern detection: Rejected - misses opportunity to add value

### Decision 5: Format Parameter Options
**What**: Add `format` parameter with three options:
- `aggregated` (default): Returns aggregated statistics
- `data-points`: Returns actual sampled data points without aggregation
- `raw`: Returns all daily prices (backward compatible)

**Why**:
- `aggregated`: Provides summary statistics for quick analysis
- `data-points`: Provides actual prices at sampled points for detailed analysis without full raw data
- `raw`: Maintains backward compatibility for users who need all daily prices
- Clear API design with distinct use cases

**Data-points Format Details**:
- Returns the actual sampled prices (e.g., last trading day of each month)
- CSV format similar to raw, but only includes sampled points
- Much smaller than raw (e.g., 60 lines for 5 years monthly vs 7,000+ raw)
- Useful when traders want actual prices but don't need every single day

**Alternatives considered**:
- Separate tool for raw data: Rejected - unnecessary complexity
- Always return both: Rejected - doubles response size
- Only aggregated and raw: Rejected - data-points fills important middle ground

## Risks / Trade-offs

### Risk: Loss of Daily Granularity
**Mitigation**: Provide `format=raw` option for users who need daily data.

### Risk: Aggregation May Hide Important Patterns
**Mitigation**: Include min/max ranges and std dev to show volatility. Pattern detection highlights significant differences.

### Risk: Performance Impact of Aggregation
**Mitigation**: Use efficient SQL aggregation (database-side) rather than Python-side processing.

### Trade-off: Simplicity vs Flexibility
**Decision**: Default to simple aggregated view, allow raw data via parameter. Keeps common case simple while supporting advanced use cases.

## Implementation Plan

### Phase 1: Database Aggregation Function
1. Create SQL function for monthly aggregation
2. Add date range filtering support
3. Test with sample queries

### Phase 2: Pattern Detection Logic
1. Implement month-to-month comparison
2. Calculate percentage differences
3. Format insights as natural language

### Phase 3: Tool Updates
1. Update function signature
2. Implement format selection
3. Update response formatting
4. Maintain backward compatibility

### Phase 4: Testing & Validation
1. Validate aggregation accuracy
2. Test response size reduction
3. Verify pattern detection
4. Test edge cases

### Decision 6: Data Sampling and Optimization
**What**: Implement efficient sampling logic that selects representative data points based on `points_per_year` parameter.

**Sampling Implementation Details**:

**12/year (Monthly - Default)**:
- Select last trading day of each calendar month
- Group by expiration month (1-12)
- For each expiration month, aggregate across all years
- Example: All January contracts → aggregate all last-trading-day prices for January across years

**24/year (Bi-monthly)**:
- Select two dates per month:
  1. Mid-month: ~15th of month (or nearest trading day if 15th is weekend/holiday)
  2. End-of-month: Last trading day of month
- Group by expiration month (1-12) and position (mid/end)
- Example: January contracts → separate stats for mid-January and end-January

**52/year (Weekly)**:
- Select consistent day of week (prefer Friday close, or first trading day of week)
- Group by week number (1-52) and expiration month
- Handle year boundaries consistently (week 1 = first week of year)
- Example: All Friday prices for January contracts → aggregate by week number

**SQL Optimization Strategy**:
1. **Pre-filtering**: Filter by date range and commodity before sampling
2. **Window Functions**: Use ROW_NUMBER() or RANK() to identify last trading day of month
3. **Date Functions**: Use DATE_TRUNC() and DATE_PART() for efficient date grouping
4. **Index Usage**: Leverage existing indexes on trade_date and expiration_date
5. **Aggregation**: Perform aggregation in SQL, not Python

**Example Query Pattern (12/year)**:
```sql
WITH monthly_samples AS (
  SELECT 
    expiration_month,
    trade_date,
    settlement_price,
    ROW_NUMBER() OVER (
      PARTITION BY expiration_year, expiration_month 
      ORDER BY trade_date DESC
    ) as rn
  FROM prices p
  JOIN contracts c ON p.contract_id = c.id
  WHERE ... -- filters
)
SELECT 
  expiration_month,
  COUNT(*) as count,
  AVG(settlement_price) as avg_price,
  MIN(settlement_price) as min_price,
  MAX(settlement_price) as max_price,
  STDDEV(settlement_price) as std_dev,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY settlement_price) as median
FROM monthly_samples
WHERE rn = 1  -- Only last trading day of each month
GROUP BY expiration_month
ORDER BY expiration_month
```

**Performance Considerations**:
- **Indexing**: Ensure indexes on (trade_date, contract_id) and (expiration_year, expiration_month)
- **Query Planning**: Use EXPLAIN ANALYZE to verify efficient execution plans
- **Caching**: Consider caching common queries (e.g., last 5 years, monthly aggregation)
- **Materialized Views**: For very frequent queries, consider materialized views with refresh strategy

**Why**:
- Reduces data volume while maintaining representative samples
- Enables efficient database-side processing (faster than Python)
- Provides consistent, reproducible results
- Leverages database optimization capabilities

**Alternatives considered**:
- Client-side sampling: Rejected - inefficient, processes too much data, slower
- Random sampling: Rejected - not reproducible, may miss important dates
- Fixed date sampling: Preferred - consistent and predictable
- Python-side aggregation: Rejected - slower, processes unnecessary data

## Open Questions
- Should we include year-over-year comparisons? (e.g., "2024 January vs 2023 January")
- What threshold should trigger pattern detection? (Currently: 5%)
- For 24/year sampling, should we use exact 15th or nearest trading day? (Recommend: nearest trading day)
- For 52/year sampling, should we use same day of week or first trading day of week? (Recommend: same day of week, e.g., Friday)

