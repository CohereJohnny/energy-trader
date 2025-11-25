## Why
Energy traders need access to CFTC Commitment of Traders (COT) reports to analyze market positioning, identify trends in trader behavior, and make informed trading decisions. Currently, COT data is only available through CFTC's web interface or manual downloads, making it difficult for AI agents to query and analyze this critical market positioning data. We need an MCP server that can retrieve, parse, and structure CFTC COT data (particularly disaggregated reports for petroleum commodities) into a queryable format suitable for retrieval-augmented generation (RAG) and analysis.

## What Changes
- **BREAKING**: None (new capability)
- Create new MCP server `cftc-cot` using North MCP Python SDK
- Design database schema for storing CFTC COT report data (disaggregated futures and options format)
- Implement data ingestion pipeline to fetch and parse CFTC COT reports (CSV/XML formats from CFTC PRE downloads)
- Parse disaggregated COT reports for:
  - **Petroleum and Products**: Crude Oil (WTI, Brent), Gasoline (RBOB), Heating Oil, Gas Oil
  - **Natural Gas and Products**: Natural Gas, Propane
  - **Electricity**: Electricity futures
- Structure data into normalized JSON format for efficient querying and RAG
- Implement MCP tools for:
  - Querying COT data by commodity, date range, and trader category
  - Analyzing trader positioning trends (commercial vs. non-commercial, managed money, etc.)
  - Comparing positioning across commodities or time periods
  - Generating insights on market sentiment and positioning extremes
- Include citation metadata in all tool responses following North MCP citations pattern
- Store historical COT data in PostgreSQL database (new schema: `cftc_cot`)
- Focus on Disaggregated Futures and Options reports only (not Legacy or TFF reports)

## Impact
- Affected specs: New capability `cftc-cot`
- Affected code:
  - New MCP server implementation (`mcp-servers/cftc-cot/`)
  - Database schema and migration scripts (`database/migrations/`)
  - Data ingestion scripts (`scripts/ingest_cftc_cot.py`)
- Dependencies: 
  - CFTC Public Reporting Environment (PRE) web interface for data downloads (CSV/XML formats)
  - PostgreSQL database (existing containerized instance)
  - North MCP Python SDK
  - Python libraries for data parsing (pandas, requests, zipfile for downloaded archives)

