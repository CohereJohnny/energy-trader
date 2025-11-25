## 1. Database Layer
- [x] 1.1 Add `get_loaded_reports()` method to `db.py` to query loaded reports from `reports` table
- [x] 1.2 Add `get_loading_status()` method to `db.py` to query `loading_log` table for loading status
- [x] 1.3 Add `get_data_coverage()` method to `db.py` to return coverage statistics (date range, commodity counts, etc.)
- [x] 1.4 Add `get_missing_reports()` method to `db.py` to identify gaps in expected weekly reports

## 2. MCP Tool
- [x] 2.1 Add `get_loaded_data_status` tool function to `tools.py`
- [x] 2.2 Implement tool parameters: `commodity` (optional), `start_date` (optional), `end_date` (optional), `status` (optional)
- [x] 2.3 Format tool response with human-readable summary and structured data
- [x] 2.4 Add citation metadata to tool response
- [x] 2.5 Register tool in `server.py`

## 3. CLI Script
- [x] 3.1 Create `scripts/query_cftc_loaded_data.py` CLI script
- [x] 3.2 Implement command-line arguments for filtering (commodity, date range, status)
- [x] 3.3 Add multiple output formats (human-readable table, JSON)
- [x] 3.4 Add summary statistics command
- [x] 3.5 Add missing reports detection command
- [x] 3.6 Add proper error handling and user-friendly messages

## 4. Documentation
- [x] 4.1 Update MCP server README with new tool documentation
- [x] 4.2 Add CLI script usage examples to README
- [x] 4.3 Document query examples and use cases

