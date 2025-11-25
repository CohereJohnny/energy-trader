## ADDED Requirements

### Requirement: Query Loaded Data Status Tool
The system SHALL provide an MCP tool `get_loaded_data_status` that allows querying what CFTC COT data has been loaded and processed from the CFTC website.

#### Scenario: Query All Loaded Reports
- **WHEN** agent calls `get_loaded_data_status` with no filters
- **THEN** tool returns summary of all loaded reports including:
  - Total number of reports loaded
  - Date range covered (earliest and latest report dates)
  - List of commodity groups available
  - List of unique report dates
- **AND** response includes citation metadata

#### Scenario: Query Loaded Reports by Commodity
- **WHEN** agent calls `get_loaded_data_status` with commodity="Petroleum and Products"
- **THEN** tool returns only reports for that commodity group including:
  - Number of reports for the commodity
  - Date range for the commodity
  - List of markets available for the commodity
- **AND** response includes citation metadata

#### Scenario: Query Loaded Reports by Date Range
- **WHEN** agent calls `get_loaded_data_status` with start_date="2025-01-01" and end_date="2025-03-31"
- **THEN** tool returns reports within the date range including:
  - Number of reports in range
  - List of report dates
  - Commodities available in range
- **AND** response includes citation metadata

#### Scenario: Query Loading Status
- **WHEN** agent calls `get_loaded_data_status` with status="failed"
- **THEN** tool returns reports with failed loading status from loading_log table including:
  - Report dates that failed
  - Error messages
  - Timestamps of failures
- **AND** response includes citation metadata

#### Scenario: Identify Missing Reports
- **WHEN** agent calls `get_loaded_data_status` with identify_gaps=true
- **THEN** tool analyzes expected weekly reports and identifies:
  - Missing report dates (gaps in weekly sequence)
  - Date ranges with missing data
  - Commodities missing for specific dates
- **AND** response includes citation metadata

### Requirement: CLI Tool for Querying Loaded Data
The system SHALL provide a command-line script that allows querying loaded CFTC COT data status locally without using the MCP server.

#### Scenario: Query All Loaded Data via CLI
- **WHEN** user runs `python scripts/query_cftc_loaded_data.py --summary`
- **THEN** script displays summary statistics including:
  - Total reports loaded
  - Date range covered
  - Commodities available
  - Loading status counts (completed, failed, pending)

#### Scenario: Query by Commodity via CLI
- **WHEN** user runs `python scripts/query_cftc_loaded_data.py --commodity "Petroleum and Products"`
- **THEN** script displays table of loaded reports for that commodity with:
  - Report dates
  - Markets available
  - Status (loaded/failed)

#### Scenario: Query by Date Range via CLI
- **WHEN** user runs `python scripts/query_cftc_loaded_data.py --start-date 2025-01-01 --end-date 2025-03-31`
- **THEN** script displays reports in date range with:
  - Report dates
  - Commodities available
  - Status

#### Scenario: Query Missing Reports via CLI
- **WHEN** user runs `python scripts/query_cftc_loaded_data.py --missing`
- **THEN** script identifies and displays:
  - Missing report dates (expected weekly reports not loaded)
  - Date ranges with gaps
  - Commodities missing for specific dates

#### Scenario: JSON Output Format via CLI
- **WHEN** user runs `python scripts/query_cftc_loaded_data.py --json`
- **THEN** script outputs results in JSON format suitable for scripting and automation
- **AND** JSON includes all query results in structured format

## MODIFIED Requirements

### Requirement: Get COT Data Tool
The system SHALL provide an MCP tool `get_cot_data` that retrieves COT data for specified commodities and date ranges.

#### Scenario: Query COT Data by Commodity and Date Range
- **WHEN** agent calls `get_cot_data` with commodity="WTI", start_date="2024-01-01", end_date="2024-01-31"
- **THEN** tool returns COT data for NYMEX Crude Oil (WTI) for all reports in date range
- **AND** response includes trader categories (Producer/Merchant, Swap Dealers, Managed Money, etc.)
- **AND** response includes positions (long, short, spread) and changes from previous week
- **AND** response includes citation metadata with CFTC source URL and report date
- **AND** tool validates that requested reports exist in database and provides helpful error message if data not loaded

#### Scenario: Query COT Data with Trader Category Filter
- **WHEN** agent calls `get_cot_data` with commodity="RBOB", trader_category="Managed Money"
- **THEN** tool returns only Managed Money positions for NYMEX Gasoline
- **AND** response includes long, short, spread positions and changes
- **AND** tool validates that requested commodity and date data exists in database

