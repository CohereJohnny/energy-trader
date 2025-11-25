# Seasonal Spread Chart Data Capabilities

## Overview

The `get_seasonal_data` tool with `format="data-points"` provides all the data necessary to render seasonal spread charts similar to the examples shown (ZWZ spreads, 5y/15y averages, deviations).

## Data Structure

When using `format="data-points"` with `points_per_year=12` (monthly), the tool returns:

```python
[
    {'year': 2019, 'month': 1, 'trade_date': date(2019, 1, 31), 'settlement_price': Decimal('584.50')},
    {'year': 2019, 'month': 2, 'trade_date': date(2019, 2, 28), 'settlement_price': Decimal('599.25')},
    ...
    {'year': 2024, 'month': 1, 'trade_date': date(2024, 1, 31), 'settlement_price': Decimal('855.00')},
    ...
]
```

## Chart Requirements Met

### ✅ Individual Year Series
- **Example**: ZWZ10, ZWZ11, ..., ZWZ19 (10 different years)
- **Our Data**: We have 15+ years (2010-2024) of monthly data points
- **Format**: Each year can be plotted as a separate line series

### ✅ 5-Year Average
- **Example**: Red "5y" line showing rolling 5-year average
- **Our Data**: Can calculate 5-year rolling average for each month
- **Calculation**: Average of last 5 years' prices for each month (Jan-Dec)

### ✅ 15-Year Average
- **Example**: Green "15y" line showing rolling 15-year average
- **Our Data**: We have 15+ years, so can calculate 15-year average
- **Calculation**: Average of last 15 years' prices for each month

### ✅ Deviations from Average
- **Example**: Greyed-out "5y Dev" and "15y Dev" lines
- **Our Data**: Can calculate deviations for any year vs. averages
- **Calculation**: `deviation = actual_price - average_price` for each month

## Data Availability

### Historical Range
- **GO M2**: 2010-2024 (15 years) ✅
- **BRENT M1**: 2010-2024 (15 years) ✅
- **WTI M1**: 2010-2024 (15 years) ✅
- **RBOB M1**: 2010-2024 (15 years) ✅

### Sampling Frequency
- **Monthly (12/year)**: Default, one data point per month (last trading day)
- **Bi-monthly (24/year)**: Two points per month (mid-month ~15th and end-of-month)
- **Weekly (52/year)**: One point per week (prefer Friday)

## Chart Rendering Process

### Step 1: Get Data Points
```python
# Agent calls tool
result = get_seasonal_data(
    commodity='GO',
    contract_month_offset=2,  # M2
    start_year=2010,
    end_year=2024,
    points_per_year=12,  # Monthly
    format='data-points'
)
```

### Step 2: Organize by Year and Month
```python
# Structure: {year: {month: price}}
data_by_year = {}
for point in result['data']:
    year = point['year']
    month = point['month']
    price = float(point['settlement_price'])
    if year not in data_by_year:
        data_by_year[year] = {}
    data_by_year[year][month] = price
```

### Step 3: Calculate Averages
```python
# 5-year average for each month
avg_5y = {}
for month in range(1, 13):
    recent_years = sorted(data_by_year.keys())[-5:]
    prices = [data_by_year[y][month] for y in recent_years if month in data_by_year[y]]
    avg_5y[month] = sum(prices) / len(prices) if prices else None

# 15-year average (if enough data)
avg_15y = {}
if len(data_by_year) >= 15:
    for month in range(1, 13):
        recent_years = sorted(data_by_year.keys())[-15:]
        prices = [data_by_year[y][month] for y in recent_years if month in data_by_year[y]]
        avg_15y[month] = sum(prices) / len(prices) if prices else None
```

### Step 4: Calculate Deviations (Optional)
```python
# Deviation for specific year (e.g., 2019)
deviations_5y = {}
for month in range(1, 13):
    if month in avg_5y and 2019 in data_by_year and month in data_by_year[2019]:
        deviations_5y[month] = data_by_year[2019][month] - avg_5y[month]
```

### Step 5: Format for Charting Library
```python
# CSV format for charting
# Series,Month,Price
for year in sorted(data_by_year.keys()):
    for month in range(1, 13):
        if month in data_by_year[year]:
            print(f"{year},{month},{data_by_year[year][month]:.2f}")

# Averages
for month in range(1, 13):
    if month in avg_5y:
        print(f"5y_avg,{month},{avg_5y[month]:.2f}")
    if month in avg_15y:
        print(f"15y_avg,{month},{avg_15y[month]:.2f}")

# Deviations
for month in range(1, 13):
    if month in deviations_5y:
        print(f"2019_dev_5y,{month},{deviations_5y[month]:+.2f}")
```

## Example Output

### Individual Year Series (like ZWZ10-ZWZ19)
```
Series,Month,Price
2010,1,697.00
2010,2,731.75
...
2019,1,584.50
2019,2,599.25
...
```

### 5-Year Average
```
Series,Month,Price
5y_avg,1,653.40
5y_avg,2,684.40
...
```

### 15-Year Average
```
Series,Month,Price
15y_avg,1,648.04
15y_avg,2,661.54
...
```

### Deviations
```
Series,Month,Deviation
2019_dev_5y,1,-71.90
2019_dev_5y,2,-91.90
...
```

## Testing

Run the test scripts to verify data structure:

```bash
# Test data structure
cd mcp-servers/futures-prices
uv run python3 test_seasonal_chart.py

# Test chart visualization format
uv run python3 test_chart_visualization.py
```

## Agent Instructions

The agent should:
1. Use `format="data-points"` when user asks for charts/visualizations
2. Use `points_per_year=12` for monthly seasonal charts (default)
3. Calculate averages and deviations client-side from the data points
4. Format data as CSV for charting libraries (matplotlib, plotly, etc.)

## Limitations

- **No built-in average calculation**: The tool returns raw data points; averages must be calculated client-side
- **No deviation calculation**: Deviations must be calculated client-side
- **Year filtering**: Use `start_year` and `end_year` to limit the date range

## Future Enhancements

Potential improvements:
1. Add `include_averages=True` parameter to automatically calculate and return averages
2. Add `include_deviations=True` parameter to calculate deviations for a specific year
3. Add `average_window` parameter (5, 10, 15 years) to specify which average to calculate

