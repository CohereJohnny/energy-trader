## Why
The AI agent needs to query historical and current futures prices for energy commodities (BRENT, WTI, GASOIL, RBOB) to answer questions like "What was the front month Brent price on a given date?" or "What was the change in front month Brent price between two dates?". Currently, this data exists only in CSV files that need to be loaded into a PostgreSQL database and exposed via an MCP server with proper citations.

## What Changes
- **BREAKING**: None (new capability)
- Set up containerized PostgreSQL database using Docker Compose
- Create PostgreSQL schema for storing normalized futures prices data
- Parse contract names using CME Group month codes (https://www.cmegroup.com/month-codes.html) from CSV column headers
- Load CSV data (BR_CUR.csv, WTI_CUR.csv, GO_CUR.csv, RB_CUR.csv) into PostgreSQL with proper month code interpretation
- Build MCP server using North MCP Python SDK to query front month prices
- Implement MCP tools for:
  - Getting front month price for a specific commodity and date
  - Getting front month prices for a date range
  - Calculating price changes between dates
  - Getting seasonal data for charting (e.g., M2 GOBRs)
- Include citation metadata in all tool responses following North MCP citations pattern

## Impact
- Affected specs: New capability `futures-prices`
- Affected code: 
  - New MCP server implementation
  - Database schema and migration scripts
  - Data loading scripts
- Dependencies: Docker, PostgreSQL database (containerized), North MCP Python SDK

