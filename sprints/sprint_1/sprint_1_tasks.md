# Sprint 1 Tasks

## Goals
Set up database infrastructure and load historical futures prices data. This sprint focuses on the foundation needed for the MCP server implementation in Sprint 2.

**OpenSpec Change**: `add-futures-price-mcp-server` (partial - database and data loading components)

## Tasks

### 1. Database Schema Design
- [ ] 1.1 Design normalized schema for futures contracts and prices
- [ ] 1.2 Create schema migration script (futures_prices schema)
- [ ] 1.3 Create tables: commodities, contracts, prices
- [ ] 1.4 Add indexes for efficient date/commodity queries

**Progress Notes**:
- 

### 2. Data Loading
- [ ] 2.1 Implement CME Group month code parser (F=Jan, G=Feb, H=Mar, J=Apr, K=May, M=Jun, N=Jul, Q=Aug, U=Sep, V=Oct, X=Nov, Z=Dec)
- [ ] 2.2 Create script to parse CSV files and extract contract metadata (commodity, year, month from contract names)
- [ ] 2.3 Create script to normalize and load data into PostgreSQL with month code conversion
- [ ] 2.4 Validate data integrity after loading
- [ ] 2.5 Handle edge cases (missing dates, null prices, invalid month codes)

**Progress Notes**:
- 

### 3. Front Month Logic (Foundation)
- [ ] 3.1 Design front month detection algorithm (nearest expiring contract with price)
- [ ] 3.2 Create database function/view for front month price lookup
- [ ] 3.3 Document contract expiration and rollover logic

**Progress Notes**:
- 

### 4. Testing & Validation
- [ ] 4.1 Test data loading with all CSV files (BRENT, WTI, GASOIL, RBOB)
- [ ] 4.2 Verify month code parsing accuracy
- [ ] 4.3 Validate front month detection logic
- [ ] 4.4 Performance testing for queries

**Progress Notes**:
- 

## Sprint Review
_To be completed at end of sprint_

### Demo Readiness
- 

### Gaps/Issues
- 

### Next Steps
- 

