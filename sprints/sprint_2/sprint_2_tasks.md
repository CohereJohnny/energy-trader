# Sprint 2 Tasks

## Goals
Build MCP server with tools for querying futures prices. This sprint implements the MCP server using North MCP Python SDK and exposes 4 tools for querying front month prices.

**OpenSpec Change**: `add-futures-price-mcp-server` (complete)

## Tasks

### 1. MCP Server Setup
- [x] 1.1 Set up Python project structure with North MCP Python SDK
- [x] 1.2 Create project directory structure (`mcp-servers/futures-prices/`)
- [x] 1.3 Install dependencies (North MCP SDK, psycopg2)
- [x] 1.4 Create configuration files (requirements.txt, .env.example)
- [x] 1.5 Set up database connection utilities

**Progress Notes**:
- Created MCP server directory structure
- Created requirements.txt with North MCP SDK and psycopg2
- Created database connection module (`db.py`)
- Created .env.example for configuration

### 2. Database Connection & Query Utilities
- [x] 2.1 Create database connection module
- [x] 2.2 Create query helper functions for front month prices
- [x] 2.3 Implement error handling for database queries
- [x] 2.4 Add connection pooling (if needed)

**Progress Notes**:
- Created `db.py` with Database class
- Implemented get_front_month_price(), get_front_month_prices()
- Implemented get_contract_prices_by_month_offset() for seasonal data
- Added error handling and connection management

### 3. MCP Tool: get_front_month_price
- [x] 3.1 Implement tool for single date lookup
- [x] 3.2 Add input validation (commodity, date)
- [x] 3.3 Format response with citation metadata
- [x] 3.4 Add error handling

**Progress Notes**:
- Implemented in `tools.py`
- Validates commodity codes and date format
- Returns formatted response with citation metadata

### 4. MCP Tool: get_front_month_prices
- [x] 4.1 Implement tool for date range lookup
- [x] 4.2 Add input validation (commodity, start_date, end_date)
- [x] 4.3 Format response with citation metadata
- [x] 4.4 Handle large date ranges efficiently

**Progress Notes**:
- Implemented in `tools.py`
- Validates date ranges and commodity codes
- Returns formatted list with citation metadata

### 5. MCP Tool: calculate_price_change
- [x] 5.1 Implement price change calculation logic
- [x] 5.2 Calculate absolute and percentage change
- [x] 5.3 Format response with citation metadata
- [x] 5.4 Handle edge cases (same dates, missing data)

**Progress Notes**:
- Implemented in `tools.py`
- Calculates absolute and percentage changes
- Handles missing data gracefully

### 6. MCP Tool: get_seasonal_data
- [x] 6.1 Implement seasonal data retrieval (e.g., M2 GOBRs)
- [x] 6.2 Add contract month offset parameter
- [x] 6.3 Format data for charting
- [x] 6.4 Format response with citation metadata

**Progress Notes**:
- Implemented in `tools.py`
- Uses contract month offset to get M1, M2, etc.
- Returns CSV-like format for charting

### 7. Citation Metadata
- [x] 7.1 Implement `_north_metadata` format for all tools
- [x] 7.2 Include title, source, timestamp in citations
- [x] 7.3 Test citation format matches North MCP specification

**Progress Notes**:
- Created `citations.py` module
- All tools return responses with `_north_metadata`
- Includes title, url, author_name, last_updated

### 8. Server Configuration
- [x] 8.1 Configure StreamableHTTP transport
- [x] 8.2 Set up server startup script
- [x] 8.3 Add environment variable configuration
- [x] 8.4 Create server entry point

**Progress Notes**:
- Created `server.py` with NorthMCPServer
- Configured StreamableHTTP transport (default)
- Added command-line arguments for port and debug
- All 4 tools registered with @mcp.tool() decorator

### 9. Error Handling & Validation
- [x] 9.1 Add comprehensive error handling
- [x] 9.2 Validate all input parameters
- [x] 9.3 Return meaningful error messages
- [x] 9.4 Log errors appropriately

**Progress Notes**:
- All tools include input validation
- Error handling for database connections, invalid dates, missing data
- Clear error messages returned to users

### 10. Documentation
- [x] 10.1 Document MCP server setup
- [x] 10.2 Document available tools and parameters
- [x] 10.3 Create README for MCP server
- [x] 10.4 Document citation metadata format

**Progress Notes**:
- Created comprehensive README.md
- Documented all 4 tools with parameters and examples
- Created setup.sh script for easy installation
- Created pyproject.toml for uv package management
- Setup script tested and working

## Sprint Review

### Demo Readiness
✅ **MCP Server Implementation Complete**
- All 4 MCP tools implemented and verified
- Citation metadata included in all responses
- Server configured with StreamableHTTP transport
- Virtual environment setup with uv
- Dependencies installed successfully
- **Verification tests: 7/7 passed** ✅
  - Database connection working
  - All 4 tools return correct data
  - Citation metadata format correct
  - Error handling working
  - All commodities (BRENT, WTI, GO, RBOB) supported

### Gaps/Issues
- None identified - ready for Sprint 3 testing

### Next Steps
- **Sprint 3**: Build MCP client for end-to-end testing
- Test all tools with sample queries
- Validate citation metadata format
- Performance testing

