# Sprint 3 Test Plan

Test cases for Sprint 3 deliverables - MCP Client & End-to-End Testing.

## MCP Client Setup Tests
- [ ] Client successfully connects to MCP server
- [ ] StreamableHTTP transport works correctly
- [ ] Authentication handled properly (if required)
- [ ] Client can list available tools
- [ ] Client can invoke tools

## get_front_month_price Tests
- [ ] Returns correct price for BRENT on valid date
- [ ] Returns correct price for WTI on valid date
- [ ] Returns correct price for GASOIL on valid date
- [ ] Returns correct price for RBOB on valid date
- [ ] Handles missing data gracefully
- [ ] Handles invalid date format
- [ ] Handles date outside data range
- [ ] Handles invalid commodity name
- [ ] Citation metadata present and correct format

## get_front_month_prices Tests
- [ ] Returns correct prices for BRENT date range
- [ ] Returns correct prices for WTI date range
- [ ] Handles 1-day range
- [ ] Handles 1-week range
- [ ] Handles 1-month range
- [ ] Handles 1-year range
- [ ] Handles invalid date range (start > end)
- [ ] Handles dates outside data range
- [ ] Citation metadata present and correct format

## calculate_price_change Tests
- [ ] Calculates correct absolute change
- [ ] Calculates correct percentage change
- [ ] Handles positive price changes
- [ ] Handles negative price changes
- [ ] Handles zero change
- [ ] Handles same start and end date
- [ ] Handles invalid date range
- [ ] Citation metadata present and correct format

## get_seasonal_data Tests
- [ ] Returns seasonal data for GASOIL M2
- [ ] Returns seasonal data for other commodities
- [ ] Handles different contract month offsets (M1, M2, M3)
- [ ] Data format suitable for charting
- [ ] Handles invalid month offset
- [ ] Citation metadata present and correct format

## End-to-End Query Scenarios
- [ ] Query: "What was the change in front month Brent price between January 3rd 2025 and March 31st 2025?"
  - Correctly parses dates
  - Returns correct price change
  - Includes proper citations
- [ ] Query: "What was the front month Brent Settlement yesterday?"
  - Correctly identifies "yesterday"
  - Returns correct settlement price
  - Includes proper citations
- [ ] Query: "Display a seasonal chart of M2 GOBRs"
  - Correctly identifies M2 GOBRs (GASOIL, second month)
  - Returns seasonal data
  - Data format suitable for charting
  - Includes proper citations

## Performance Tests
- [ ] Single tool invocation completes in < 500ms
- [ ] Date range queries complete in < 2s for 1-year range
- [ ] Handles 10 concurrent requests without errors
- [ ] Handles 50 concurrent requests (may degrade gracefully)

## Error Handling Tests
- [ ] Invalid commodity name returns appropriate error
- [ ] Invalid date format returns appropriate error
- [ ] Date outside data range returns appropriate error
- [ ] Server errors handled gracefully
- [ ] Network timeouts handled gracefully
- [ ] Connection failures handled gracefully

## Citation Metadata Tests
- [ ] All tool responses include `_north_metadata`
- [ ] Metadata includes title
- [ ] Metadata includes source URL or identifier
- [ ] Metadata includes timestamp
- [ ] Metadata format matches North MCP specification

