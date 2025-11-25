## MODIFIED Requirements

### Requirement: Get Seasonal Data
The system SHALL provide seasonal data analysis for futures contracts with aggregated statistics and pattern detection. The tool SHALL support configurable data point granularity, aggregated statistics (default), and raw data formats.

#### Scenario: Get aggregated seasonal statistics (monthly - default)
- **WHEN** the AI agent calls `get_seasonal_data` with commodity="GO", contract_month_offset=2, start_year=2020, end_year=2024
- **THEN** the tool returns aggregated monthly statistics (min, max, average, std dev, median) grouped by expiration month (1-12) for the M2 contract across the specified years, with 12 data points per year (1 per month), response size < 500 lines

#### Scenario: Get bi-monthly seasonal statistics
- **WHEN** the AI agent calls `get_seasonal_data` with commodity="GO", contract_month_offset=2, points_per_year=24
- **THEN** the tool returns aggregated statistics with 24 data points per year (2 per month: mid-month ~15th and end-of-month), grouped by expiration month and position (mid/end)

#### Scenario: Get weekly seasonal statistics
- **WHEN** the AI agent calls `get_seasonal_data` with commodity="GO", contract_month_offset=2, points_per_year=52
- **THEN** the tool returns aggregated statistics with 52 data points per year (1 per week), sampled consistently (e.g., Friday close or first trading day of week)

#### Scenario: Get data-points seasonal data
- **WHEN** the AI agent calls `get_seasonal_data` with commodity="GO", contract_month_offset=2, format="data-points", points_per_year=12
- **THEN** the tool returns actual sampled data points (e.g., last trading day of each month) in CSV format without aggregation

#### Scenario: Get raw seasonal data
- **WHEN** the AI agent calls `get_seasonal_data` with commodity="GO", contract_month_offset=2, format="raw"
- **THEN** the tool returns all daily prices in CSV format (backward compatible behavior)

#### Scenario: Pattern detection in seasonal data
- **WHEN** the tool calculates aggregated statistics
- **THEN** it identifies and highlights significant seasonal patterns (e.g., "January prices are typically X% higher than December") when differences exceed 5%

#### Scenario: Date range filtering
- **WHEN** the AI agent calls `get_seasonal_data` with start_year=2020 and end_year=2024
- **THEN** the tool only includes data from contracts expiring in those years

#### Scenario: Default behavior returns aggregated statistics
- **WHEN** the AI agent calls `get_seasonal_data` without specifying format or points_per_year
- **THEN** the tool returns aggregated monthly statistics (12 points/year) by default, not raw daily prices

## ADDED Requirements

### Requirement: Monthly Aggregation Statistics
The system SHALL calculate and return the following statistics for each expiration month (1-12) when providing aggregated seasonal data:
- Count: Number of price observations
- Average: Mean settlement price
- Minimum: Lowest price observed
- Maximum: Highest price observed
- Standard Deviation: Price volatility measure
- Median: Middle value (less affected by outliers)

#### Scenario: Aggregation calculation
- **WHEN** aggregating prices for January (month 1) contracts across multiple years
- **THEN** the system calculates all six statistics from all January contract prices in the specified date range

### Requirement: Pattern Detection
The system SHALL detect and highlight significant seasonal patterns when differences between consecutive months exceed a threshold (default: 5%).

#### Scenario: Pattern detection
- **WHEN** average January price is 7% higher than average December price
- **THEN** the tool includes an insight: "January prices are typically 7% higher than December prices"

### Requirement: Date Range Filtering
The system SHALL support optional `start_year` and `end_year` parameters to filter seasonal data by contract expiration year.

#### Scenario: Filter by year range
- **WHEN** start_year=2020 and end_year=2024 are provided
- **THEN** only contracts expiring between 2020 and 2024 are included in the analysis

### Requirement: Data Point Granularity
The system SHALL support a `points_per_year` parameter to control sampling frequency:
- `12` (default): 1 data point per month (monthly sampling)
- `24`: 2 data points per month (mid-month ~15th and end-of-month)
- `52`: 1 data point per week (weekly sampling)

#### Scenario: Monthly sampling (12/year)
- **WHEN** points_per_year=12 is specified (or omitted, as default)
- **THEN** the tool samples the last trading day of each month and aggregates by expiration month

#### Scenario: Bi-monthly sampling (24/year)
- **WHEN** points_per_year=24 is specified
- **THEN** the tool samples ~15th of month (or nearest trading day) and last trading day of month, groups by expiration month and position (mid/end)

#### Scenario: Weekly sampling (52/year)
- **WHEN** points_per_year=52 is specified
- **THEN** the tool samples consistent day of week (e.g., Friday close) or first trading day of each week, groups by week number and expiration month

### Requirement: Output Format Selection
The system SHALL support a `format` parameter with options:
- `aggregated` (default): Returns aggregated statistics based on points_per_year sampling
- `data-points`: Returns actual sampled data points without aggregation (e.g., last trading day prices)
- `raw`: Returns all daily prices in CSV format (backward compatible)

#### Scenario: Aggregated format selection
- **WHEN** format="aggregated" is specified (or omitted, as default)
- **THEN** the tool returns aggregated statistics based on points_per_year sampling

#### Scenario: Data-points format selection
- **WHEN** format="data-points" is specified
- **THEN** the tool returns the actual sampled data points (e.g., last trading day of each month) in CSV format, without aggregation

#### Scenario: Raw format selection
- **WHEN** format="raw" is specified
- **THEN** the tool returns all daily prices (backward compatible)

