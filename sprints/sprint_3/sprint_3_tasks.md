# Sprint 3 Tasks

## Goals
Build MCP client for comprehensive end-to-end testing of the futures prices MCP server. This sprint focuses on validating all MCP tools work correctly and handle edge cases properly.

**OpenSpec Change**: Testing and validation for `add-futures-price-mcp-server`

## Tasks

### 1. MCP Client Setup
- [ ] 1.1 Set up MCP client project structure
- [ ] 1.2 Configure client to connect to MCP server (StreamableHTTP transport)
- [ ] 1.3 Implement authentication handling (if required)
- [ ] 1.4 Create client utilities for tool invocation

**Progress Notes**:
- 

### 2. Tool Testing - get_front_month_price
- [ ] 2.1 Test single date lookup for BRENT
- [ ] 2.2 Test single date lookup for WTI
- [ ] 2.3 Test single date lookup for GASOIL
- [ ] 2.4 Test single date lookup for RBOB
- [ ] 2.5 Test edge cases (missing data, invalid dates, future dates)
- [ ] 2.6 Validate citation metadata format

**Progress Notes**:
- 

### 3. Tool Testing - get_front_month_prices
- [ ] 3.1 Test date range lookup for BRENT
- [ ] 3.2 Test date range lookup for WTI
- [ ] 3.3 Test various date ranges (1 day, 1 week, 1 month, 1 year)
- [ ] 3.4 Test edge cases (invalid ranges, dates outside data range)
- [ ] 3.5 Validate citation metadata format

**Progress Notes**:
- 

### 4. Tool Testing - calculate_price_change
- [ ] 4.1 Test price change calculation for BRENT
- [ ] 4.2 Test price change calculation for WTI
- [ ] 4.3 Validate absolute change calculation
- [ ] 4.4 Validate percentage change calculation
- [ ] 4.5 Test edge cases (same date, negative changes, zero changes)
- [ ] 4.6 Validate citation metadata format

**Progress Notes**:
- 

### 5. Tool Testing - get_seasonal_data
- [ ] 5.1 Test seasonal data for GASOIL M2 (second month contract)
- [ ] 5.2 Test seasonal data for other commodities
- [ ] 5.3 Test various contract month offsets (M1, M2, M3, etc.)
- [ ] 5.4 Validate data format suitable for charting
- [ ] 5.5 Validate citation metadata format

**Progress Notes**:
- 

### 6. End-to-End Query Scenarios
- [ ] 6.1 Test: "What was the change in front month Brent price between January 3rd 2025 and March 31st 2025?"
- [ ] 6.2 Test: "What was the front month Brent Settlement yesterday?"
- [ ] 6.3 Test: "Display a seasonal chart of M2 GOBRs"
- [ ] 6.4 Test additional natural language query variations
- [ ] 6.5 Document query patterns and expected responses

**Progress Notes**:
- 

### 7. Performance & Error Handling
- [ ] 7.1 Performance testing (response times for all tools)
- [ ] 7.2 Load testing (multiple concurrent requests)
- [ ] 7.3 Error handling validation (invalid inputs, server errors)
- [ ] 7.4 Timeout handling
- [ ] 7.5 Network error handling

**Progress Notes**:
- 

### 8. Test Documentation
- [ ] 8.1 Document test scenarios and results
- [ ] 8.2 Create test report
- [ ] 8.3 Document any issues found
- [ ] 8.4 Update MCP server documentation based on test findings

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

