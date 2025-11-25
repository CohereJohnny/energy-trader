# Data Sampling Strategy for Seasonal Data Tool

## Overview

The `get_seasonal_data` tool now supports configurable data point granularity via the `points_per_year` parameter. This document details the sampling strategies for each option.

## Sampling Options

### 12/year (Monthly - Default)

**Purpose**: Monthly aggregation for seasonal pattern analysis

**Sampling Method**:
- Select **last trading day** of each calendar month
- Group by expiration month (1-12)
- Aggregate statistics across all years

**Example**:
- January contracts: Use last trading day of January for each year
- February contracts: Use last trading day of February for each year
- etc.

**Output Structure**:
```
Month  | Count | Avg    | Min    | Max    | Std Dev | Median
-------|-------|--------|--------|--------|---------|--------
Jan    | 15    | 650.25 | 580.00 | 720.50 | 35.20   | 645.00
Feb    | 15    | 655.30 | 590.00 | 730.00 | 38.10   | 650.00
...
```

**Use Case**: Standard seasonal analysis, identifying month-to-month patterns

**Response Size**: ~12-15 rows per expiration month (depending on years analyzed)

---

### 24/year (Bi-monthly)

**Purpose**: Higher frequency analysis for intra-month volatility

**Sampling Method**:
- Select **two dates per month**:
  1. **Mid-month**: ~15th of month (or nearest trading day)
  2. **End-of-month**: Last trading day of month
- Group by expiration month (1-12) and position (mid/end)

**Example**:
- January contracts: Separate stats for mid-January and end-January
- February contracts: Separate stats for mid-February and end-February
- etc.

**Output Structure**:
```
Month  | Position | Count | Avg    | Min    | Max    | Std Dev | Median
-------|----------|-------|--------|--------|--------|---------|--------
Jan    | mid      | 15    | 645.00 | 575.00 | 715.00 | 32.50   | 640.00
Jan    | end      | 15    | 655.50 | 585.00 | 725.00 | 37.80   | 650.00
Feb    | mid      | 15    | 650.00 | 590.00 | 720.00 | 35.20   | 645.00
Feb    | end      | 15    | 660.50 | 595.00 | 735.00 | 40.10   | 655.00
...
```

**Use Case**: Analyzing intra-month price movements, identifying mid-month vs end-of-month patterns

**Response Size**: ~24-30 rows per expiration month (depending on years analyzed)

**Implementation Notes**:
- Use `DATE_PART('day', trade_date)` to identify mid-month dates
- Handle weekends/holidays by selecting nearest trading day
- Consider using `ABS(EXTRACT(DAY FROM trade_date) - 15)` to find closest to 15th

---

### 52/year (Weekly)

**Purpose**: Weekly granularity for detailed trend analysis

**Sampling Method**:
- Select **consistent day of week** (prefer Friday close, or first trading day of week)
- Group by week number (1-52) and expiration month
- Handle year boundaries consistently

**Example**:
- January contracts: All Friday prices → aggregate by week number
- February contracts: All Friday prices → aggregate by week number
- etc.

**Output Structure**:
```
Month  | Week | Count | Avg    | Min    | Max    | Std Dev | Median
-------|------|-------|--------|--------|--------|---------|--------
Jan    | 1    | 15    | 640.00 | 570.00 | 710.00 | 30.00   | 635.00
Jan    | 2    | 15    | 645.00 | 575.00 | 715.00 | 32.50   | 640.00
Jan    | 3    | 15    | 650.00 | 580.00 | 720.00 | 35.00   | 645.00
...
```

**Use Case**: Weekly trend analysis, identifying short-term patterns within months

**Response Size**: ~52-65 rows per expiration month (depending on years analyzed)

**Implementation Notes**:
- Use `EXTRACT(WEEK FROM trade_date)` for week number
- Use `EXTRACT(DOW FROM trade_date)` to filter by day of week (0=Sunday, 5=Friday)
- Handle week 53 (leap years) consistently
- Consider ISO week numbering for consistency

---

## SQL Implementation Patterns

### Pattern 1: Last Trading Day of Month (12/year)

```sql
WITH monthly_last_days AS (
  SELECT 
    c.expiration_month,
    p.trade_date,
    p.settlement_price,
    ROW_NUMBER() OVER (
      PARTITION BY c.expiration_year, c.expiration_month 
      ORDER BY p.trade_date DESC
    ) as rn
  FROM futures_prices.prices p
  JOIN futures_prices.contracts c ON p.contract_id = c.id
  WHERE c.commodity_id = ? 
    AND c.expiration_year BETWEEN ? AND ?
    AND p.settlement_price IS NOT NULL
)
SELECT 
  expiration_month,
  COUNT(*) as count,
  AVG(settlement_price) as avg_price,
  MIN(settlement_price) as min_price,
  MAX(settlement_price) as max_price,
  STDDEV(settlement_price) as std_dev,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY settlement_price) as median
FROM monthly_last_days
WHERE rn = 1
GROUP BY expiration_month
ORDER BY expiration_month
```

### Pattern 2: Mid-Month and End-of-Month (24/year)

```sql
WITH monthly_samples AS (
  SELECT 
    c.expiration_month,
    p.trade_date,
    p.settlement_price,
    CASE 
      WHEN ABS(EXTRACT(DAY FROM p.trade_date) - 15) <= 3 
        AND EXTRACT(DAY FROM p.trade_date) <= 18
      THEN 'mid'
      ELSE 'end'
    END as position,
    CASE 
      WHEN ABS(EXTRACT(DAY FROM p.trade_date) - 15) <= 3 
        AND EXTRACT(DAY FROM p.trade_date) <= 18
      THEN ROW_NUMBER() OVER (
        PARTITION BY c.expiration_year, c.expiration_month 
        ORDER BY ABS(EXTRACT(DAY FROM p.trade_date) - 15)
      )
      ELSE ROW_NUMBER() OVER (
        PARTITION BY c.expiration_year, c.expiration_month 
        ORDER BY p.trade_date DESC
      )
    END as rn
  FROM futures_prices.prices p
  JOIN futures_prices.contracts c ON p.contract_id = c.id
  WHERE c.commodity_id = ? 
    AND c.expiration_year BETWEEN ? AND ?
    AND p.settlement_price IS NOT NULL
)
SELECT 
  expiration_month,
  position,
  COUNT(*) as count,
  AVG(settlement_price) as avg_price,
  MIN(settlement_price) as min_price,
  MAX(settlement_price) as max_price,
  STDDEV(settlement_price) as std_dev,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY settlement_price) as median
FROM monthly_samples
WHERE rn = 1
GROUP BY expiration_month, position
ORDER BY expiration_month, position
```

### Pattern 3: Weekly Sampling (52/year)

```sql
WITH weekly_samples AS (
  SELECT 
    c.expiration_month,
    EXTRACT(WEEK FROM p.trade_date) as week_number,
    p.trade_date,
    p.settlement_price,
    ROW_NUMBER() OVER (
      PARTITION BY c.expiration_year, c.expiration_month, EXTRACT(WEEK FROM p.trade_date)
      ORDER BY CASE WHEN EXTRACT(DOW FROM p.trade_date) = 5 THEN 0 ELSE 1 END,  -- Prefer Friday
               p.trade_date DESC
    ) as rn
  FROM futures_prices.prices p
  JOIN futures_prices.contracts c ON p.contract_id = c.id
  WHERE c.commodity_id = ? 
    AND c.expiration_year BETWEEN ? AND ?
    AND p.settlement_price IS NOT NULL
)
SELECT 
  expiration_month,
  week_number,
  COUNT(*) as count,
  AVG(settlement_price) as avg_price,
  MIN(settlement_price) as min_price,
  MAX(settlement_price) as max_price,
  STDDEV(settlement_price) as std_dev,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY settlement_price) as median
FROM weekly_samples
WHERE rn = 1
GROUP BY expiration_month, week_number
ORDER BY expiration_month, week_number
```

## Performance Optimization

### Indexing Requirements

Ensure these indexes exist:
```sql
CREATE INDEX idx_prices_trade_date ON futures_prices.prices(trade_date);
CREATE INDEX idx_prices_contract_trade_date ON futures_prices.prices(contract_id, trade_date);
CREATE INDEX idx_contracts_expiration ON futures_prices.contracts(expiration_year, expiration_month);
```

### Query Optimization Tips

1. **Pre-filter early**: Filter by commodity and date range before window functions
2. **Use appropriate indexes**: Ensure indexes support the query patterns
3. **Limit window function scope**: Partition only by necessary columns
4. **Consider materialized views**: For frequently accessed patterns, cache results

### Expected Performance

- **12/year**: < 100ms for 10 years of data
- **24/year**: < 150ms for 10 years of data  
- **52/year**: < 300ms for 10 years of data

## Response Size Estimates

For 10 years of data:
- **12/year**: ~12 rows (one per month)
- **24/year**: ~24 rows (two per month)
- **52/year**: ~52 rows (one per week)

Each row includes: month, count, avg, min, max, std_dev, median

Total response size (including headers and formatting):
- **12/year**: ~200-300 lines
- **24/year**: ~400-600 lines
- **52/year**: ~800-1200 lines

All significantly smaller than current 30,000+ lines!

