## Context

The CFTC (Commodity Futures Trading Commission) publishes weekly Commitment of Traders (COT) reports that provide a breakdown of open interest and trader positions. These reports are critical for energy traders to understand market positioning and sentiment.

### CFTC COT Report Types

1. **Legacy Reports**: Categorize traders as Commercial and Non-Commercial
2. **Disaggregated Reports**: More detailed breakdown including:
   - Producer/Merchant/Processor/User
   - Swap Dealers
   - Managed Money
   - Other Reportables
3. **Traders in Financial Futures (TFF)**: Focus on financial contracts

### Report Formats

- **Short Format**: Basic position data
- **Long Format**: Includes concentration data (positions held by largest traders)
- **Available Formats**: CSV, XML, TSV, RDF, RSS via CFTC PRE API

### Petroleum Commodities in COT Reports

The disaggregated petroleum report (https://www.cftc.gov/dea/futures/petroleum_lf.htm) includes:
- NYMEX Crude Oil (WTI)
- NYMEX Gasoline (RBOB)
- NYMEX Heating Oil
- ICE Brent Crude Oil
- ICE Gas Oil

### Data Structure

Each report contains:
- Report date (weekly, released Fridays)
- Market/Commodity name
- Open Interest (total contracts)
- Trader categories with:
  - Long positions
  - Short positions
  - Spread positions
  - Changes from previous week
- Concentration data (long format only)

## Goals / Non-Goals

### Goals
- Provide programmatic access to CFTC COT data via MCP tools
- Structure data for efficient querying and RAG applications
- Support disaggregated reports (more detailed than legacy)
- Enable analysis of trader positioning trends
- Store historical data for trend analysis
- Support petroleum commodities (WTI, RBOB, Heating Oil, Brent, Gas Oil)

### Non-Goals
- Real-time data updates (weekly reports are sufficient)
- All CFTC commodities (focus on petroleum initially)
- Financial futures (TFF reports) - focus on physical commodities
- Web scraping if CFTC API is available (prefer API access)

## Decisions

### Decision 1: Data Source - Direct Downloads vs Web Scraping
**What**: Use CFTC Public Reporting Environment (PRE) web interface for direct data downloads (CSV/XML formats).

**Why**:
- CFTC does not provide a public API, but offers downloadable data files
- PRE interface allows downloading reports in structured formats (CSV, XML, TSV)
- More reliable than parsing HTML pages
- Can programmatically construct download URLs based on report dates and types
- Files are well-structured and consistent

**Alternatives considered**:
- CFTC API: Not available - CFTC does not provide a public API
- HTML scraping: Rejected - less reliable, harder to maintain, more fragile
- Third-party APIs (e.g., ICE Data Services): Considered but rejected - requires subscription/licensing, adds cost
- Manual downloads: Rejected - not scalable

**Implementation Note**: 
- CFTC PRE allows downloading data files via URLs that can be programmatically constructed
- Example: `https://www.cftc.gov/files/dea/history/futures_disaggregated_short_YYYYMMDD.zip`
- Files contain CSV/XML data that can be parsed programmatically

### Decision 2: Database Schema Design
**What**: Normalized schema with separate tables for reports, markets, positions, and trader categories.

**Schema Structure**:
```
cftc_cot schema:
- reports: report_date, report_type (disaggregated/legacy), format (short/long)
- markets: market_code, market_name, exchange, commodity_type
- trader_categories: category_code, category_name, category_type
- positions: report_id, market_id, category_id, long_positions, short_positions, 
            spread_positions, changes_from_prev_week, open_interest
- concentration: report_id, market_id, category_id, num_traders, pct_long, pct_short
```

**Why**:
- Normalized structure enables efficient querying
- Supports multiple report types and formats
- Allows historical trend analysis
- Flexible for adding new trader categories

**Alternatives considered**:
- Single denormalized table: Rejected - too much duplication, harder to query
- JSONB column: Considered but rejected - less queryable, harder to index

### Decision 3: Data Format for RAG
**What**: Generate structured JSON documents for each report with hierarchical structure.

**JSON Structure**:
```json
{
  "report_date": "2024-01-09",
  "report_type": "disaggregated",
  "format": "long",
  "markets": [
    {
      "market_code": "CL",
      "market_name": "Crude Oil",
      "exchange": "NYMEX",
      "open_interest": 1234567,
      "trader_categories": [
        {
          "category": "Producer/Merchant/Processor/User",
          "long": 123456,
          "short": 234567,
          "spread": 34567,
          "change": 1234,
          "concentration": {
            "num_traders": 45,
            "pct_long": 12.5,
            "pct_short": 18.9
          }
        }
      ]
    }
  ]
}
```

**Why**:
- Hierarchical structure matches report organization
- Easy to parse for RAG applications
- Preserves relationships between markets and trader categories
- Can be stored as JSONB in PostgreSQL for flexible querying

### Decision 4: MCP Tools Design
**What**: Provide focused tools for common trader queries.

**Tools**:
1. `get_cot_data`: Get COT data for specific commodity and date range
2. `analyze_positioning_trends`: Analyze positioning trends over time
3. `compare_positioning`: Compare positioning across commodities or dates
4. `get_positioning_extremes`: Identify extreme positioning (high long/short ratios)

**Why**:
- Focused tools are easier to use than generic query tool
- Each tool serves specific trader use case
- Can combine tools for complex analysis

**Alternatives considered**:
- Single generic query tool: Rejected - too complex, harder to use
- More granular tools: Considered but rejected - too many tools, harder to maintain

### Decision 5: Data Ingestion Strategy
**What**: Weekly batch ingestion with incremental updates.

**Process**:
1. Check for new reports (released Fridays)
2. Fetch report data from CFTC API
3. Parse and validate data
4. Store in database
5. Generate structured JSON for RAG

**Why**:
- Weekly reports don't require real-time updates
- Batch processing is simpler and more reliable
- Can handle historical data backfill
- Incremental updates avoid duplicates

## Implementation Plan

### Phase 1: Database Schema
1. Design normalized schema for COT data
2. Create migration scripts
3. Add indexes for common queries

### Phase 2: Data Ingestion
1. Implement CFTC data download client (construct download URLs programmatically)
2. Download report files (CSV/XML) from CFTC PRE
3. Parse CSV/XML report formats
4. Validate and transform data
5. Store in database

### Phase 3: MCP Server
1. Create MCP server structure
2. Implement database queries
3. Build MCP tools
4. Add citation metadata

### Phase 4: Testing & Validation
1. Test data ingestion with sample reports
2. Validate MCP tools with test client
3. Test RAG JSON generation
4. Performance testing

## Risks/Trade-offs

### Risk: CFTC Data Download URL Changes
**Mitigation**: Monitor CFTC website for URL structure changes. Implement robust URL construction with error handling. Cache historical data to reduce dependency on live downloads. Consider fallback to HTML parsing if download URLs change.

### Risk: Data Format Changes
**Mitigation**: Version data schema, implement robust parsing with error handling, monitor CFTC for format changes.

### Trade-off: Data Freshness vs. Reliability
**Decision**: Prefer reliability - weekly batch updates are sufficient for COT analysis. Real-time updates not critical.

### Trade-off: Storage vs. Query Performance
**Decision**: Normalized schema for query performance. Can add materialized views for common queries if needed.

