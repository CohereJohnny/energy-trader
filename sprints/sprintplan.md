# Sprint Plan - Energy Trader

High-level plan for development sprints.

## Sprint Overview

This project uses a sprint-based development approach to build the Energy Trader AI Agent system incrementally.

## Sprint Goals

### Sprint 1: Foundation & Data Infrastructure
**Goal**: Set up database infrastructure and load historical futures prices data

**Key Deliverables**:
- PostgreSQL database setup with containerized instance
- Database schema for futures prices (commodities, contracts, prices tables)
- Data loading scripts for CSV files (BRENT, WTI, GASOIL, RBOB)
- CME Group month code parsing implementation
- Data validation and integrity checks

**OpenSpec Change**: `add-futures-price-mcp-server` (partial - database and data loading)

### Sprint 2: MCP Server Implementation
**Goal**: Build MCP server with tools for querying futures prices

**Key Deliverables**:
- MCP server using North MCP Python SDK
- Front month price lookup logic
- Four MCP tools:
  - `get_front_month_price`
  - `get_front_month_prices`
  - `calculate_price_change`
  - `get_seasonal_data`
- Citation metadata implementation

**OpenSpec Change**: `add-futures-price-mcp-server` (complete)

### Sprint 3: MCP Client & End-to-End Testing
**Goal**: Build MCP client for comprehensive end-to-end testing of the MCP server

**Key Deliverables**:
- MCP client implementation for testing futures prices MCP server
- Test suite covering all MCP tools
- End-to-end test scenarios for natural language queries:
  - "What was the change in front month Brent price between January 3rd 2025 and March 31st 2025?"
  - "What was the front month Brent Settlement yesterday?"
  - "Display a seasonal chart of M2 GOBRs"
- Citation metadata validation
- Performance testing
- Error handling validation
- Test documentation

**OpenSpec Change**: Testing and validation for `add-futures-price-mcp-server`

### Sprint 4: AI Agent Integration
**Goal**: Integrate MCP server with AI agent and test end-to-end queries

**Key Deliverables**:
- AI agent configuration to use futures prices MCP server
- End-to-end testing of natural language queries with AI agent
- Performance optimization
- Error handling improvements
- User acceptance testing

### Future Sprints
- Additional data sources (EIA, IEA, CFTC)
- Advanced analytics and charting
- Position tracking capabilities
- Market sentiment analysis

## Sprint Cadence
- Sprint duration: 1-2 weeks (to be determined)
- Sprint planning: Beginning of each sprint
- Sprint review: End of each sprint

