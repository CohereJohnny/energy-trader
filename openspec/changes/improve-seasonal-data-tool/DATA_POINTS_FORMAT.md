# Data-Points Format Feature

## Overview

Added a third format option `data-points` to the `get_seasonal_data` tool that returns the actual sampled data points without aggregation. This fills the gap between `aggregated` (statistics only) and `raw` (all daily prices).

## Format Options

### 1. `aggregated` (Default)
- Returns aggregated statistics (min, max, avg, std dev, median)
- Grouped by sampling period (month, week, etc.)
- Best for: Quick pattern identification and summary analysis
- Example: 19 lines for monthly aggregated

### 2. `data-points` (New)
- Returns actual sampled data points (the prices used for aggregation)
- CSV format with actual dates and prices
- Best for: Detailed analysis with actual prices but reduced volume
- Example: 53 lines for 5 years of monthly sampling (vs 7,700+ raw)

### 3. `raw` (Backward Compatible)
- Returns all daily prices
- Best for: Complete historical data access
- Example: 7,700+ lines for 5 years

## Use Cases

### When to Use `data-points`:
- Need actual prices at sampled points (e.g., last trading day of each month)
- Want reduced data volume compared to raw format
- Need to see individual data points that make up the aggregated statistics
- Building custom visualizations or analysis
- Verifying aggregated statistics with actual underlying data

### Example Output (Monthly, data-points):

```
Seasonal Data Points: GO M2 Contracts (2020-2024)

Date,Year,Month,Price
2020-01-31,2020,1,510.25
2020-02-28,2020,2,494.50
2020-03-31,2020,3,443.75
...
2024-01-31,2024,1,855.00
2024-02-12,2024,2,918.25
```

### Example Output (Bi-monthly, data-points):

```
Seasonal Data Points: GO M2 Contracts (2020-2024)

Date,Year,Month,Position,Price
2020-01-15,2020,1,mid,558.00
2020-01-31,2020,1,end,510.25
2020-02-14,2020,2,mid,519.50
2020-02-28,2020,2,end,494.50
...
```

## Implementation Details

### Database Layer
- Added `get_seasonal_data_points()` method
- Added `_get_monthly_data_points()`, `_get_bimonthly_data_points()`, `_get_weekly_data_points()`
- Filters by trade date year (not expiration year) for data-points format
- Uses same sampling logic as aggregated format

### Tool Layer
- Updated `get_seasonal_data()` to handle `format="data-points"`
- Formats output as CSV with appropriate columns based on sampling frequency
- Includes year range in header when specified

### Response Size Comparison

For 5 years of data (2020-2024):
- **Aggregated (monthly)**: 19 lines (statistics only)
- **Data-points (monthly)**: 53 lines (actual sampled prices)
- **Raw**: 7,704 lines (all daily prices)

## Benefits

1. **Reduced Volume**: 99%+ smaller than raw format
2. **Actual Prices**: Provides real prices, not just statistics
3. **Flexible Analysis**: Can perform custom calculations on sampled points
4. **Transparency**: Shows exactly which data points were used for aggregation
5. **Chart-Ready**: CSV format easy to import into visualization tools

## Testing

✅ All formats tested and working:
- Monthly data-points: 53 lines for 5 years
- Bi-monthly data-points: 102 lines for 5 years  
- Weekly data-points: Working correctly
- Year filtering: Correctly filters by trade date year
- All sampling frequencies supported

