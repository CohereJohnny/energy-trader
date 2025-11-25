## 1. Setup & Structure
- [ ] 1.1 Create `mcp-clients/cftc-cot-tester/` directory structure
- [ ] 1.2 Create `pyproject.toml` and `requirements.txt` with dependencies
- [ ] 1.3 Create `setup.sh` script for environment setup
- [ ] 1.4 Create `.env.example` for configuration
- [ ] 1.5 Create `README.md` with setup and usage instructions

## 2. Test Suite Implementation
- [ ] 2.1 Create `test_suite.py` with comprehensive test cases:
  - [ ] 2.1.1 Test `get_cot_data` tool:
    - [ ] With all parameters (commodity, report_date, trader_category, position_type)
    - [ ] With latest report date (no date specified)
    - [ ] With specific commodity groups (Petroleum, Natural Gas, Electricity)
    - [ ] With all trader categories (PRODUCER, SWAP, MANAGED_MONEY, OTHER_REPORTABLE, NONREPORTABLE)
    - [ ] With all position types (all, old, other)
    - [ ] Edge cases (invalid dates, invalid categories, no data found)
  - [ ] 2.1.2 Test `analyze_positioning_trends` tool:
    - [ ] Valid date ranges
    - [ ] Different commodity groups
    - [ ] Different trader categories
    - [ ] Edge cases (invalid dates, date ordering, no data)
  - [ ] 2.1.3 Test `compare_positioning` tool:
    - [ ] Multiple commodities comparison
    - [ ] Different trader categories
    - [ ] Edge cases (invalid commodities, invalid date, no data)
  - [ ] 2.1.4 Test `get_positioning_extremes` tool:
    - [ ] Different metrics (long, short, net, pct_long, pct_short)
    - [ ] Different lookback periods
    - [ ] Different commodity groups and trader categories
    - [ ] Edge cases (invalid metric, invalid lookback, no data)
- [ ] 2.2 Add response validation:
  - [ ] Validate response structure (text, _north_metadata)
  - [ ] Validate citation metadata format
  - [ ] Validate data content (non-empty, correct format)
- [ ] 2.3 Add performance benchmarks:
  - [ ] Measure query response times
  - [ ] Test with large date ranges
  - [ ] Test concurrent queries

## 3. Manual Testing Tools
- [ ] 3.1 Create `manual_test.py` for interactive testing:
  - [ ] Interactive menu for selecting tools
  - [ ] Parameter input prompts
  - [ ] Pretty-printed results
  - [ ] Error handling and retry options
- [ ] 3.2 Create `QUICK_TEST.md` with quick start guide
- [ ] 3.3 Create `MANUAL_TESTING.md` with detailed manual testing instructions

## 4. MCP Inspector Configuration
- [ ] 4.1 Create `mcp_inspector_config.json` for MCP Inspector tool
- [ ] 4.2 Configure server connection settings
- [ ] 4.3 Document MCP Inspector usage

## 5. Test Runner & Documentation
- [ ] 5.1 Create `run_tests.sh` script for easy test execution
- [ ] 5.2 Create `TEST_REPORT.md` template for documenting test results
- [ ] 5.3 Update `README.md` with:
  - [ ] Setup instructions
  - [ ] Test execution guide
  - [ ] Expected test results
  - [ ] Troubleshooting guide

## 6. Integration & Validation
- [ ] 6.1 Verify all tests pass with loaded CFTC COT data
- [ ] 6.2 Validate citation metadata in all tool responses
- [ ] 6.3 Test error handling and edge cases
- [ ] 6.4 Document any known limitations or issues

