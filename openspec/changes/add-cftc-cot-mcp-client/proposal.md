## Why
The CFTC COT MCP server needs comprehensive end-to-end testing to validate all 4 tools (`get_cot_data`, `analyze_positioning_trends`, `compare_positioning`, `get_positioning_extremes`) work correctly with real data, handle edge cases properly, and return properly formatted responses with citation metadata. Currently, there is no automated way to test the CFTC COT MCP server tools, making it difficult to validate functionality, catch regressions, and ensure data quality.

## What Changes
- **BREAKING**: None (new testing capability)
- Create MCP client test suite for CFTC COT MCP server (`mcp-clients/cftc-cot-tester/`)
- Implement comprehensive test suite covering:
  - All 4 MCP tools with various parameter combinations
  - Edge cases (missing data, invalid dates, invalid categories)
  - Citation metadata validation
  - Response format validation
  - Performance benchmarks
  - End-to-end scenarios (e.g., "Analyze Managed Money positioning trends in Petroleum over 3 months")
- Create manual testing script for interactive tool testing
- Add MCP Inspector configuration for visual testing
- Create test runner script and documentation
- Follow same pattern as `mcp-clients/futures-prices-tester/` for consistency

## Impact
- Affected specs: New capability `mcp-clients` (or extension of existing testing capability)
- Affected code:
  - New MCP client implementation (`mcp-clients/cftc-cot-tester/`)
  - Test suite and manual testing scripts
- Dependencies: 
  - Existing CFTC COT MCP server (`mcp-servers/cftc-cot/`)
  - CFTC COT data loaded in PostgreSQL database
  - Python testing libraries (pytest or similar)

