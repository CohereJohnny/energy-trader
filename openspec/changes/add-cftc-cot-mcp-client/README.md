# Add CFTC COT MCP Client - Change Proposal

## Overview

This change proposal adds a comprehensive MCP client test suite for the CFTC COT MCP server, following the same pattern as the existing `futures-prices-tester` client.

## Change ID

`add-cftc-cot-mcp-client`

## Status

✅ **Proposal Created and Validated**

## Files Created

1. **`proposal.md`** - Why, what changes, and impact
2. **`tasks.md`** - Implementation checklist (6 phases, 30+ tasks)
3. **`specs/mcp-clients/spec.md`** - Requirements and scenarios (10 scenarios)

## Key Requirements

The test suite will validate:

1. **All 4 MCP Tools**:
   - `get_cot_data` - Query COT data with various filters
   - `analyze_positioning_trends` - Analyze trends over time
   - `compare_positioning` - Compare across commodities
   - `get_positioning_extremes` - Find extreme positions

2. **Test Coverage**:
   - All parameter combinations
   - Edge cases (invalid dates, categories, missing data)
   - Citation metadata validation
   - Response format validation
   - Performance benchmarks
   - End-to-end scenarios

3. **Manual Testing**:
   - Interactive testing script
   - MCP Inspector configuration
   - Documentation and guides

## Implementation Phases

1. **Setup & Structure** - Create directory and configuration files
2. **Test Suite Implementation** - Comprehensive automated tests
3. **Manual Testing Tools** - Interactive testing capabilities
4. **MCP Inspector Configuration** - Visual testing setup
5. **Test Runner & Documentation** - Scripts and docs
6. **Integration & Validation** - Final testing and validation

## Next Steps

1. Review and approve the proposal
2. Implement tasks sequentially from `tasks.md`
3. Test with loaded CFTC COT data
4. Validate all scenarios pass

## Related Changes

- `add-cftc-cot-mcp-server` - The MCP server being tested
- `add-futures-price-mcp-server` - Reference implementation pattern

