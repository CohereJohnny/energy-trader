## ADDED Requirements

### Requirement: CFTC COT MCP Client Test Suite
The system SHALL provide a comprehensive test suite for validating the CFTC COT MCP server tools, including automated tests, manual testing capabilities, and performance benchmarks.

#### Scenario: Test get_cot_data tool with all parameters
- **WHEN** the test suite calls `get_cot_data` with commodity="Petroleum and Products", report_date="2025-10-07", trader_category="MANAGED_MONEY", position_type="all"
- **THEN** the tool returns a valid response with text content and citation metadata
- **AND** the response contains COT data for the specified criteria
- **AND** the citation metadata includes CFTC as the source

#### Scenario: Test get_cot_data with latest report date
- **WHEN** the test suite calls `get_cot_data` without specifying a report_date
- **THEN** the tool returns data for the latest available report date
- **AND** the response includes the report date used

#### Scenario: Test analyze_positioning_trends with date range
- **WHEN** the test suite calls `analyze_positioning_trends` with commodity="Petroleum and Products", start_date="2025-07-01", end_date="2025-10-07", trader_category="MANAGED_MONEY"
- **THEN** the tool returns trend analysis showing start/end values and changes
- **AND** the response includes percentage changes for long and short positions
- **AND** the response includes citation metadata

#### Scenario: Test compare_positioning across commodities
- **WHEN** the test suite calls `compare_positioning` with commodities="Petroleum and Products, Natural Gas and Products", report_date="2025-10-07", trader_category="MANAGED_MONEY"
- **THEN** the tool returns a tabular comparison of positioning across commodities
- **AND** the response includes Long, Short, % Long, % Short for each commodity
- **AND** the response includes citation metadata

#### Scenario: Test get_positioning_extremes with different metrics
- **WHEN** the test suite calls `get_positioning_extremes` with commodity="Petroleum and Products", trader_category="MANAGED_MONEY", lookback_days=365, metric="long"
- **THEN** the tool returns top 10 extreme positions sorted by the specified metric
- **AND** the response includes dates and values for each extreme
- **AND** the response includes citation metadata

#### Scenario: Test error handling for invalid parameters
- **WHEN** the test suite calls a tool with invalid parameters (e.g., invalid date format, invalid trader category)
- **THEN** the tool returns an error message in the response text
- **AND** the error message is user-friendly and descriptive
- **AND** the response still includes citation metadata

#### Scenario: Test citation metadata format
- **WHEN** any tool returns a response
- **THEN** the response includes `_north_metadata` field
- **AND** the metadata includes title, url, author_name, and last_updated fields
- **AND** the author_name is "CFTC - Commodity Futures Trading Commission"
- **AND** the url points to CFTC source

#### Scenario: Manual testing with interactive script
- **WHEN** a user runs `manual_test.py`
- **THEN** the script presents an interactive menu for selecting tools
- **AND** the script prompts for required parameters
- **AND** the script displays formatted results
- **AND** the script handles errors gracefully

#### Scenario: Performance benchmark testing
- **WHEN** the test suite runs performance benchmarks
- **THEN** query response times are measured and reported
- **AND** tests with large date ranges complete within acceptable time limits
- **AND** performance metrics are documented

#### Scenario: End-to-end scenario testing
- **WHEN** the test suite runs end-to-end scenarios (e.g., "Analyze Managed Money positioning trends in Petroleum over 3 months")
- **THEN** multiple tools are called in sequence
- **AND** results from one tool can inform parameters for subsequent tools
- **AND** the complete workflow executes successfully

