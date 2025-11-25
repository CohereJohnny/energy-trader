## Why
Users need visibility into what CFTC COT data has already been loaded and processed from the CFTC website. Currently, there's no way to query the database to see which reports have been loaded, what date ranges are covered, which commodities are available, or the status of data loading operations. This makes it difficult to:
- Determine if specific reports or date ranges are available before querying
- Identify gaps in loaded data
- Monitor data loading progress and troubleshoot failed loads
- Plan data loading operations

## What Changes
- **BREAKING**: None (new capability)
- Add new MCP tool `get_loaded_data_status` to query what CFTC COT data has been loaded into the database
- Add CLI script/tool (`scripts/query_cftc_loaded_data.py`) for local command-line queries of loaded data status
- Query capabilities include:
  - List all loaded report dates with date range summary
  - Query loaded reports by commodity group
  - Query loaded reports by date range
  - Show loading status (completed, failed, pending) from loading_log table
  - Show data coverage statistics (total reports, date range, commodities covered)
  - Identify missing reports or gaps in data coverage

## Impact
- Affected specs: Modified capability `cftc-cot`
- Affected code:
  - MCP server tools (`mcp-servers/cftc-cot/tools.py`)
  - Database layer (`mcp-servers/cftc-cot/db.py`)
  - New CLI script (`scripts/query_cftc_loaded_data.py`)
- Dependencies: None (uses existing database schema and connection)

