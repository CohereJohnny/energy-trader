# CFTC COT Data Insights and Analysis

## Overview

This document provides insights into CFTC Commitment of Traders (COT) data structure, how to ingest it, and how to structure it for useful trader insights and RAG applications.

## CFTC COT Report Structure

### Report Types

1. **Legacy Reports**: Simple Commercial vs. Non-Commercial categorization
2. **Disaggregated Reports** (Recommended): More detailed breakdown:
   - **Producer/Merchant/Processor/User**: Physical market participants
   - **Swap Dealers**: Financial intermediaries
   - **Managed Money**: Hedge funds, CTAs, commodity pools
   - **Other Reportables**: Other large traders
3. **Traders in Financial Futures (TFF)**: For financial contracts

### Report Formats

- **Short Format**: Basic position data
- **Long Format**: Includes concentration data (positions held by largest traders) - **More useful for analysis**

### Data Availability

- **Frequency**: Weekly reports (released Fridays at 3:30 PM ET)
- **Coverage**: Markets with 20+ traders holding reportable positions
- **Historical Data**: Available back to ~2006 for disaggregated reports
- **Access Methods**:
  - CFTC Public Reporting Environment (PRE) web interface
  - Direct downloads via PRE (CSV, XML, TSV formats)
  - **Note**: CFTC does not provide a public API, but data files can be downloaded programmatically by constructing download URLs

## Petroleum Commodities in COT Reports

The disaggregated petroleum report includes:

| Commodity | Exchange | Market Code | Description |
|-----------|----------|-------------|-------------|
| Crude Oil | NYMEX | CL | West Texas Intermediate (WTI) |
| Gasoline | NYMEX | RB | Reformulated Blendstock (RBOB) |
| Heating Oil | NYMEX | HO | Distillate fuel oil |
| Brent Crude | ICE | BZ | ICE Brent Crude Oil |
| Gas Oil | ICE | G | ICE Gas Oil |

## Data Structure Analysis

### Key Data Points Per Report

For each commodity and trader category, reports include:

1. **Open Interest**: Total number of contracts outstanding
2. **Long Positions**: Number of long contracts
3. **Short Positions**: Number of short contracts
4. **Spread Positions**: Number of spread positions
5. **Changes**: Week-over-week changes in positions
6. **Concentration** (Long Format):
   - Number of traders
   - Percentage of long positions held by largest traders
   - Percentage of short positions held by largest traders

### Example Data Structure

```
Report Date: 2024-01-09
Market: NYMEX Crude Oil (CL)

Trader Category: Managed Money
- Long Positions: 234,567
- Short Positions: 45,678
- Spread Positions: 12,345
- Changes: +5,432 (long), -1,234 (short)
- Concentration: 45 traders, 12.5% long, 18.9% short

Trader Category: Producer/Merchant/Processor/User
- Long Positions: 123,456
- Short Positions: 345,678
- ...
```

## Useful Insights for Traders

### 1. Market Sentiment Analysis

**Managed Money Positioning**:
- High long positions → Bullish sentiment
- High short positions → Bearish sentiment
- Rapid changes → Momentum shifts

**Commercial Positioning**:
- Producers hedging (short) → Expecting price declines
- Users hedging (long) → Expecting price increases

### 2. Extreme Positioning Detection

**When to Watch**:
- Managed Money long positions > 80th percentile → Potential reversal risk
- Commercial short positions at extremes → Strong hedging pressure
- Large week-over-week changes → Momentum acceleration

### 3. Spread Analysis

**Calendar Spreads**:
- High spread positions → Market structure concerns
- Changes in spread positions → Term structure shifts

### 4. Concentration Analysis

**High Concentration**:
- Few traders holding large positions → Increased volatility risk
- Low concentration → More distributed, stable market

## Proposed Database Schema

### Normalized Structure

```sql
-- Reports table
reports (
  id SERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  report_type VARCHAR(20) NOT NULL, -- 'disaggregated', 'legacy'
  format VARCHAR(10) NOT NULL, -- 'short', 'long'
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(report_date, report_type, format)
);

-- Markets table
markets (
  id SERIAL PRIMARY KEY,
  market_code VARCHAR(10) NOT NULL UNIQUE, -- 'CL', 'RB', 'BZ', etc.
  market_name VARCHAR(100) NOT NULL,
  exchange VARCHAR(20) NOT NULL, -- 'NYMEX', 'ICE'
  commodity_type VARCHAR(50), -- 'Crude Oil', 'Gasoline', etc.
  created_at TIMESTAMP DEFAULT NOW()
);

-- Trader categories table
trader_categories (
  id SERIAL PRIMARY KEY,
  category_code VARCHAR(50) NOT NULL UNIQUE,
  category_name VARCHAR(100) NOT NULL,
  category_type VARCHAR(20), -- 'commercial', 'non-commercial'
  created_at TIMESTAMP DEFAULT NOW()
);

-- Positions table
positions (
  id SERIAL PRIMARY KEY,
  report_id INTEGER REFERENCES reports(id),
  market_id INTEGER REFERENCES markets(id),
  category_id INTEGER REFERENCES trader_categories(id),
  open_interest BIGINT,
  long_positions BIGINT,
  short_positions BIGINT,
  spread_positions BIGINT,
  change_long INTEGER, -- week-over-week change
  change_short INTEGER,
  change_spread INTEGER,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(report_id, market_id, category_id)
);

-- Concentration table (long format only)
concentration (
  id SERIAL PRIMARY KEY,
  report_id INTEGER REFERENCES reports(id),
  market_id INTEGER REFERENCES markets(id),
  category_id INTEGER REFERENCES trader_categories(id),
  num_traders INTEGER,
  pct_long DECIMAL(5,2), -- percentage of long positions
  pct_short DECIMAL(5,2), -- percentage of short positions
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(report_id, market_id, category_id)
);
```

## Structured JSON for RAG

### Hierarchical JSON Structure

```json
{
  "report_metadata": {
    "report_date": "2024-01-09",
    "report_type": "disaggregated",
    "format": "long",
    "source": "CFTC",
    "source_url": "https://www.cftc.gov/dea/futures/petroleum_lf.htm"
  },
  "markets": [
    {
      "market_code": "CL",
      "market_name": "Crude Oil",
      "exchange": "NYMEX",
      "commodity_type": "Crude Oil",
      "open_interest": 1234567,
      "trader_categories": [
        {
          "category_code": "MM",
          "category_name": "Managed Money",
          "positions": {
            "long": 234567,
            "short": 45678,
            "spread": 12345,
            "net": 188889
          },
          "changes": {
            "long": 5432,
            "short": -1234,
            "spread": 234
          },
          "concentration": {
            "num_traders": 45,
            "pct_long": 12.5,
            "pct_short": 18.9
          }
        },
        {
          "category_code": "PMPU",
          "category_name": "Producer/Merchant/Processor/User",
          "positions": {
            "long": 123456,
            "short": 345678,
            "spread": 0,
            "net": -222222
          },
          "changes": {
            "long": -2345,
            "short": 5678,
            "spread": 0
          },
          "concentration": {
            "num_traders": 78,
            "pct_long": 8.5,
            "pct_short": 22.3
          }
        }
      ]
    }
  ]
}
```

### Benefits of This Structure

1. **Hierarchical Organization**: Matches report structure naturally
2. **Queryable**: Can query by market, category, date
3. **RAG-Friendly**: Easy to chunk and embed for semantic search
4. **Complete**: Includes all relevant data points
5. **Metadata**: Includes source information for citations

## MCP Tool Use Cases

### 1. Get COT Data
**Use Case**: "What were Managed Money positions in WTI last week?"
- Query by commodity, date, trader category
- Returns positions and changes

### 2. Analyze Positioning Trends
**Use Case**: "How has Managed Money positioning in Brent changed over the past 3 months?"
- Analyze trends over time
- Identify significant changes
- Calculate percentage changes

### 3. Compare Positioning
**Use Case**: "Compare Managed Money positioning in WTI vs. Brent"
- Compare across commodities
- Compare across time periods
- Highlight differences

### 4. Get Positioning Extremes
**Use Case**: "When was Managed Money most long WTI in the past year?"
- Identify extreme positioning
- Compare to historical averages
- Flag potential reversal risks

## Data Ingestion Strategy

### Weekly Batch Process

1. **Check for New Reports**: Query CFTC API for latest report date
2. **Fetch Report Data**: Download CSV/XML format
3. **Parse Data**: Extract markets, categories, positions
4. **Validate**: Check data integrity and completeness
5. **Store**: Insert into database with conflict handling
6. **Generate JSON**: Create structured JSON for RAG storage

### Historical Backfill

- Fetch historical reports from CFTC API
- Process in batches (e.g., monthly)
- Handle missing or incomplete data gracefully

## Implementation Considerations

### CFTC Data Access

- **PRE Downloads**: Primary method - download data files (CSV/XML) from CFTC PRE
- **URL Construction**: Download URLs can be programmatically constructed based on report date and type
- **Example Pattern**: `https://www.cftc.gov/files/dea/history/futures_disaggregated_short_YYYYMMDD.zip`
- **No Authentication**: Public data, no API key required
- **Rate Limits**: Be respectful of CFTC servers; implement reasonable delays between requests
- **Fallback**: HTML parsing if download URL patterns change

### Data Quality

- **Validation**: Check for missing or invalid data
- **Normalization**: Handle different report formats consistently
- **Error Handling**: Log errors, continue processing valid data

### Performance

- **Indexing**: Index on report_date, market_code, category for fast queries
- **Caching**: Cache frequently accessed data
- **Batch Processing**: Process multiple reports efficiently

## Next Steps

1. **Research CFTC API**: Determine exact API endpoints and access methods
2. **Sample Data**: Download sample reports to understand exact format
3. **Schema Refinement**: Adjust schema based on actual data structure
4. **Tool Design**: Refine MCP tools based on trader feedback
5. **RAG Integration**: Test JSON structure with RAG system

