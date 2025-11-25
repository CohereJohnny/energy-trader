# Seasonal Data Tool Improvement - Research Summary

## Problem Statement

The current `get_seasonal_data` tool returns **30,000+ lines** of raw daily price data, which is:
- Too large for AI agents to process efficiently
- Difficult for traders to interpret without aggregation
- Not aligned with how traders actually use seasonal data

## Research Findings: How Traders Use Seasonal Data

### 1. Pattern Identification
Traders analyze historical data to identify **recurring patterns** during specific periods:
- Example: Crude oil prices typically rise in summer due to increased driving demand
- Example: Heating oil prices spike in winter months
- Traders look for patterns that appear in **>70% of years** to ensure reliability

### 2. Aggregated Statistics, Not Raw Data
Traders need:
- **Monthly averages** to compare same periods across years
- **Min/Max ranges** to understand volatility
- **Standard deviation** to assess consistency of patterns
- **Year-over-year comparisons** for trend analysis

### 3. Focused Time Windows
- Traders typically analyze **5-10 years** of historical data
- Too much data (30+ years) can obscure recent trends
- Date range filtering is essential for focused analysis

### 4. Actionable Insights
Traders want:
- **Pattern detection**: "January prices are typically X% higher than December"
- **Volatility indicators**: Which months show highest/lowest price swings
- **Trend identification**: Are patterns strengthening or weakening over time

### 5. Strategic Planning
- Enter positions **a few weeks before** typical seasonal moves
- Use seasonal patterns to inform **risk management**
- Combine with fundamental analysis (supply/demand, weather, etc.)

## Proposed Solution

### Default Behavior: Aggregated Statistics
Instead of returning 30k+ lines of raw data, return:
- **Monthly aggregated statistics** (12 months × ~50 lines = ~600 lines)
- **Pattern insights** highlighting significant differences
- **Summary statistics** (count, avg, min, max, std dev, median)

### Key Features

1. **Monthly Aggregation by Expiration Month**
   - Group prices by expiration month (1-12)
   - Calculate statistics per month across all years
   - Enables month-to-month comparisons

2. **Date Range Filtering**
   - Optional `start_year` and `end_year` parameters
   - Default: all available years
   - Allows focusing on recent trends vs historical patterns

3. **Pattern Detection**
   - Compare consecutive months
   - Highlight differences > 5%
   - Format as natural language insights

4. **Backward Compatibility**
   - `format="raw"` parameter for users who need daily data
   - Maintains existing functionality for edge cases

## Expected Impact

### Response Size Reduction
- **Before**: 30,000+ lines (all daily prices)
- **After**: ~500 lines (aggregated statistics + insights)
- **Reduction**: 98%+ smaller responses

### Improved Usability
- Traders get actionable insights immediately
- AI agents can process summaries more effectively
- Clear pattern identification without manual analysis

### Better Alignment with Trader Needs
- Provides statistics traders actually use
- Enables quick decision-making
- Supports strategic planning

## Example Output (Aggregated Format)

```
Seasonal Analysis: GO M2 Contracts (2020-2024)

Monthly Statistics:
Month  | Count | Avg    | Min    | Max    | Std Dev | Median
-------|-------|--------|--------|--------|---------|--------
Jan    | 1,234 | 650.25 | 580.00 | 720.50 | 35.20   | 645.00
Feb    | 1,198 | 655.30 | 590.00 | 730.00 | 38.10   | 650.00
...

Seasonal Patterns Detected:
- January prices are typically 7.2% higher than December prices
- February shows highest volatility (std dev: 38.10)
- Summer months (Jun-Aug) average 5% lower than winter months
```

## Next Steps

1. **Review proposal** - Validate approach aligns with trader needs
2. **Approve design** - Confirm technical decisions
3. **Implement** - Build aggregation functions and update tool
4. **Test** - Validate accuracy and response size reduction
5. **Deploy** - Update agent instructions and documentation

