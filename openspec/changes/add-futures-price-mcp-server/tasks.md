## 1. Database Schema Design
- [ ] 1.1 Design normalized schema for futures contracts and prices
- [ ] 1.2 Create schema migration script (futures_prices schema)
- [ ] 1.3 Create tables: commodities, contracts, prices
- [ ] 1.4 Add indexes for efficient date/commodity queries

## 2. Data Loading
- [ ] 2.1 Implement CME Group month code parser (F=Jan, G=Feb, H=Mar, J=Apr, K=May, M=Jun, N=Jul, Q=Aug, U=Sep, V=Oct, X=Nov, Z=Dec)
- [ ] 2.2 Create script to parse CSV files and extract contract metadata (commodity, year, month from contract names)
- [ ] 2.3 Create script to normalize and load data into PostgreSQL with month code conversion
- [ ] 2.4 Validate data integrity after loading
- [ ] 2.5 Handle edge cases (missing dates, null prices, invalid month codes)

## 3. Front Month Logic
- [ ] 3.1 Implement front month detection algorithm (nearest expiring contract with price)
- [ ] 3.2 Create database function/view for front month price lookup
- [ ] 3.3 Handle contract expiration and rollover logic

## 4. MCP Server Implementation
- [ ] 4.1 Set up Python project structure with North MCP Python SDK
- [ ] 4.2 Implement database connection and query utilities
- [ ] 4.3 Create MCP tool: `get_front_month_price` (single date)
- [ ] 4.4 Create MCP tool: `get_front_month_prices` (date range)
- [ ] 4.5 Create MCP tool: `calculate_price_change` (between two dates)
- [ ] 4.6 Create MCP tool: `get_seasonal_data` (for charting, e.g., M2 GOBRs)
- [ ] 4.7 Add citation metadata to all tool responses
- [ ] 4.8 Configure StreamableHTTP transport
- [ ] 4.9 Add error handling and validation

## 5. Testing
- [ ] 5.1 Create MCP client for testing
- [ ] 5.2 Test all MCP tools with sample queries
- [ ] 5.3 Test citation metadata format
- [ ] 5.4 Test edge cases (missing data, invalid dates)

## 6. Documentation
- [ ] 6.1 Document database schema
- [ ] 6.2 Document MCP server setup and configuration
- [ ] 6.3 Document available tools and their parameters

