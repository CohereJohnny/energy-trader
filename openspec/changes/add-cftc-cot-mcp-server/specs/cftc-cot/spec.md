## ADDED Requirements

### Requirement: CFTC COT Database Schema
The system SHALL store CFTC Commitment of Traders report data in a normalized PostgreSQL schema (`cftc_cot`) with tables for reports, markets, trader categories, positions, and concentration data.

#### Scenario: Schema Creation
- **WHEN** database migration is executed
- **THEN** the `cftc_cot` schema is created with tables: `reports`, `markets`, `trader_categories`, `positions`, `concentration`
- **AND** appropriate indexes are created for common queries (report_date, market_code, category)

### Requirement: CFTC COT Data Ingestion
The system SHALL provide a data ingestion pipeline that fetches CFTC COT reports (disaggregated format) from CFTC API or web interface, parses the data, and stores it in the database.

#### Scenario: Successful Data Ingestion
- **WHEN** ingestion script is run with a date range and commodity filter
- **THEN** COT reports are fetched from CFTC source
- **AND** report data is parsed (CSV/XML format)
- **AND** data is validated and stored in database
- **AND** duplicate reports are handled (ON CONFLICT)

#### Scenario: Data Ingestion Error Handling
- **WHEN** ingestion encounters invalid or missing data
- **THEN** errors are logged with details
- **AND** valid data is still processed
- **AND** invalid records are skipped with warnings

### Requirement: Get COT Data Tool
The system SHALL provide an MCP tool `get_cot_data` that retrieves COT data for specified commodities and date ranges.

#### Scenario: Query COT Data by Commodity and Date Range
- **WHEN** agent calls `get_cot_data` with commodity="WTI", start_date="2024-01-01", end_date="2024-01-31"
- **THEN** tool returns COT data for NYMEX Crude Oil (WTI) for all reports in date range
- **AND** response includes trader categories (Producer/Merchant, Swap Dealers, Managed Money, etc.)
- **AND** response includes positions (long, short, spread) and changes from previous week
- **AND** response includes citation metadata with CFTC source URL and report date

#### Scenario: Query COT Data with Trader Category Filter
- **WHEN** agent calls `get_cot_data` with commodity="RBOB", trader_category="Managed Money"
- **THEN** tool returns only Managed Money positions for NYMEX Gasoline
- **AND** response includes long, short, spread positions and changes

### Requirement: Analyze Positioning Trends Tool
The system SHALL provide an MCP tool `analyze_positioning_trends` that analyzes trader positioning trends over time.

#### Scenario: Analyze Trends Over Date Range
- **WHEN** agent calls `analyze_positioning_trends` with commodity="BRENT", start_date="2024-01-01", end_date="2024-03-31", category="Managed Money"
- **THEN** tool returns trend analysis showing:
  - Changes in long/short positions over time
  - Net positioning (long - short) trends
  - Percentage changes week-over-week
  - Identification of significant trend changes
- **AND** response includes citation metadata

### Requirement: Compare Positioning Tool
The system SHALL provide an MCP tool `compare_positioning` that compares trader positioning across commodities or time periods.

#### Scenario: Compare Across Commodities
- **WHEN** agent calls `compare_positioning` with commodities=["WTI", "BRENT"], date="2024-01-09", category="Managed Money"
- **THEN** tool returns comparison showing:
  - Long/short positions for each commodity
  - Net positioning comparison
  - Percentage differences
- **AND** response includes citation metadata

#### Scenario: Compare Across Time Periods
- **WHEN** agent calls `compare_positioning` with commodity="RBOB", dates=["2024-01-09", "2024-03-12"], category="Producer/Merchant"
- **THEN** tool returns comparison showing changes in positioning between the two dates
- **AND** response includes percentage changes and direction (increased/decreased)

### Requirement: Get Positioning Extremes Tool
The system SHALL provide an MCP tool `get_positioning_extremes` that identifies extreme positioning (high long/short ratios, record positions, etc.).

#### Scenario: Identify Extreme Long Positioning
- **WHEN** agent calls `get_positioning_extremes` with commodity="WTI", category="Managed Money", extreme_type="long"
- **THEN** tool returns dates and values where Managed Money long positions were at extremes (top 10% of historical range)
- **AND** response includes comparison to historical average
- **AND** response includes citation metadata

### Requirement: Structured JSON for RAG
The system SHALL generate structured JSON documents from COT data suitable for retrieval-augmented generation applications.

#### Scenario: Generate RAG JSON
- **WHEN** COT data is retrieved from database
- **THEN** system generates JSON with hierarchical structure:
  - Report metadata (date, type, format)
  - Markets array with market details
  - Trader categories with positions and concentration data
- **AND** JSON is formatted for efficient RAG querying
- **AND** JSON includes all relevant fields (positions, changes, open interest)

### Requirement: Citation Metadata
All MCP tool responses SHALL include citation metadata following North MCP citations pattern.

#### Scenario: Citation Metadata in Response
- **WHEN** any COT tool returns data
- **THEN** response includes `_north_metadata` field with:
  - `title`: "CFTC Commitment of Traders Report"
  - `url`: CFTC report URL or source page
  - `author_name`: "Commodity Futures Trading Commission"
  - `last_updated`: Report date timestamp
- **AND** metadata is properly formatted for North UI display

### Requirement: Petroleum Commodities Support
The system SHALL support petroleum commodities from CFTC COT reports: NYMEX Crude Oil (WTI), NYMEX Gasoline (RBOB), NYMEX Heating Oil, ICE Brent Crude Oil, ICE Gas Oil.

#### Scenario: Query Multiple Petroleum Commodities
- **WHEN** agent queries COT data for petroleum commodities
- **THEN** system correctly maps commodity codes to CFTC market codes:
  - "WTI" → NYMEX Crude Oil (CL)
  - "RBOB" → NYMEX Gasoline (RB)
  - "BRENT" → ICE Brent Crude Oil
  - "GO" → ICE Gas Oil
- **AND** data is retrieved and formatted correctly

### Requirement: Historical Data Storage
The system SHALL store historical COT report data to enable trend analysis and historical comparisons.

#### Scenario: Historical Data Query
- **WHEN** agent queries COT data with date range spanning multiple years
- **THEN** system retrieves all available historical reports in date range
- **AND** data is returned in chronological order
- **AND** missing data (holidays, data gaps) is handled gracefully

