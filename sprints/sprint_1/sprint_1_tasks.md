# Sprint 1 Tasks

## Goals
Set up database infrastructure and load historical futures prices data. This sprint focuses on the foundation needed for the MCP server implementation in Sprint 2.

**OpenSpec Change**: `add-futures-price-mcp-server` (partial - database and data loading components)

## Tasks

### 1. Database Schema Design
- [x] 1.1 Design normalized schema for futures contracts and prices
- [x] 1.2 Create schema migration script (futures_prices schema)
- [x] 1.3 Create tables: commodities, contracts, prices
- [x] 1.4 Add indexes for efficient date/commodity queries
- [x] 1.5 Set up containerized PostgreSQL with Docker Compose

**Progress Notes**:
- Created schema design document (`database/schema.md`)
- Created migration script (`database/migrations/001_create_futures_prices_schema.sql`)
- Includes commodities, contracts, and prices tables
- Added indexes for performance
- Created front_month_prices view and get_front_month_price() function
- Initial commodities inserted (BRENT, WTI, GO, RBOB)
- Created Docker Compose configuration (`docker-compose.yml`)
- Created `.env.example` for environment variables
- Migrations auto-run on container startup

### 2. Data Loading
- [x] 2.1 Implement CME Group month code parser (F=Jan, G=Feb, H=Mar, J=Apr, K=May, M=Jun, N=Jul, Q=Aug, U=Sep, V=Oct, X=Nov, Z=Dec)
- [x] 2.2 Create script to parse CSV files and extract contract metadata (commodity, year, month from contract names)
- [x] 2.3 Create script to normalize and load data into PostgreSQL with month code conversion
- [x] 2.4 Validate data integrity after loading
- [x] 2.5 Handle edge cases (missing dates, null prices, invalid month codes)

**Progress Notes**:
- Created month code parser (`scripts/month_code_parser.py`) - tested and working
- Created data loading script (`scripts/load_futures_data.py`)
- Script handles contract name parsing, date parsing, null prices
- Uses batch inserts for performance
- Includes ON CONFLICT handling for idempotent loading
- Created data validation script (`scripts/validate_data.py`)
- All data validated successfully

### 3. Front Month Logic (Foundation)
- [x] 3.1 Design front month detection algorithm (nearest expiring contract with price)
- [x] 3.2 Create database function/view for front month price lookup
- [x] 3.3 Document contract expiration and rollover logic

**Progress Notes**:
- Front month detection algorithm designed: nearest expiring contract with valid price on trade date
- Created `front_month_prices` view in migration script
- Created `get_front_month_price()` function for single date lookups
- Algorithm: Find contracts where expiration_date >= trade_date, filter to those with prices, order by expiration_date ASC, take first
- Contract expiration uses first day of expiration month (can be enhanced later for exchange holidays)

### 4. Testing & Validation
- [x] 4.1 Test data loading with all CSV files (BRENT, WTI, GASOIL, RBOB)
- [x] 4.2 Verify month code parsing accuracy
- [x] 4.3 Validate front month detection logic
- [x] 4.4 Performance testing for queries

**Progress Notes**:
- Successfully loaded all 4 CSV files:
  - BRENT: 281,565 prices, 204 contracts
  - WTI: 423,509 prices, 204 contracts
  - GASOIL: 249,231 prices, 204 contracts
  - RBOB: 167,700 prices, 204 contracts
- Total: 1,122,005 price records loaded
- Date range: 2010-01-04 to 2025-11-05
- Fixed date parsing to handle edge cases (skipped ambiguous "26-Aug" format)
- Fixed front_month_prices view schema qualification
- Front month function tested and working
- Created performance test script (`scripts/test_performance.py`)
- Performance verified via EXPLAIN ANALYZE:
  - Single date queries: ~10ms (well under 100ms target) ✓
  - Date range queries (3 months): ~70ms (well under 500ms target) ✓
- All performance targets met

## Sprint Review

### Demo Readiness
✅ **Database Infrastructure Complete**
- Containerized PostgreSQL running
- Schema created with all tables, indexes, views, and functions
- 1.1M+ price records loaded successfully
- Front month detection working correctly
- Performance targets met

### Gaps/Issues
- Minor: One ambiguous date format ("26-Aug") in GO_CUR.csv skipped (data quality issue in source)
- Resolved: Front month view schema qualification fixed
- Resolved: Docker Compose version warning fixed

### Next Steps
- **Sprint 2**: Build MCP server with tools for querying futures prices
- Implement 4 MCP tools: get_front_month_price, get_front_month_prices, calculate_price_change, get_seasonal_data
- Add citation metadata to all tool responses

