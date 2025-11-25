# CFTC COT MCP Server Test Report

**Generated**: 2025-11-24 18:35:48

## Summary

- **Total Tests**: 34
- **Passed**: 34
- **Failed**: 0
- **Duration**: 0.21 seconds

## Test Results

### get_cot_data

- ✅ PASS: **get_cot_data with all parameters**
  - ✓ Response valid with all parameters
- ✅ PASS: **get_cot_data without report_date (latest)**
  - ✓ Returns latest report date
- ✅ PASS: **get_cot_data with PRODUCER**
  - ✓ PRODUCER category works
- ✅ PASS: **get_cot_data with SWAP**
  - ✓ SWAP category works
- ✅ PASS: **get_cot_data with MANAGED_MONEY**
  - ✓ MANAGED_MONEY category works
- ✅ PASS: **get_cot_data with OTHER_REPORTABLE**
  - ✓ OTHER_REPORTABLE category works
- ✅ PASS: **get_cot_data with NONREPORTABLE**
  - ✓ NONREPORTABLE category works
- ✅ PASS: **get_cot_data with Petroleum and Products**
  - ✓ Petroleum and Products works
- ✅ PASS: **get_cot_data with Natural Gas and Products**
  - ✓ Natural Gas and Products works
- ✅ PASS: **get_cot_data with Electricity**
  - ✓ Electricity works
- ✅ PASS: **get_cot_data with invalid date format**
  - ✓ Handles invalid date format
- ✅ PASS: **get_cot_data with invalid trader category**
  - ✓ Handles invalid category
- ✅ PASS: **get_cot_data with only commodity**
  - ✓ Works with only commodity
- ✅ PASS: **get_cot_data with only trader_category**
  - ✓ Works with only trader_category
- ✅ PASS: **get_cot_data with only report_date**
  - ✓ Works with only report_date
- ✅ PASS: **get_cot_data with commodity + report_date**
  - ✓ Works with commodity + report_date
- ✅ PASS: **get_cot_data performance (< 2 seconds)**
  - ✓ Query completed in 0.01s
- ✅ PASS: **get_cot_data response contains expected content**
  - ✓ Contains expected content (market, positions, date)

### analyze_positioning_trends

- ✅ PASS: **analyze_positioning_trends with valid parameters**
  - ✓ Returns trend analysis
- ✅ PASS: **analyze_positioning_trends with invalid date ordering**
  - ✓ Handles invalid date ordering
- ✅ PASS: **analyze_positioning_trends with single day range**
  - ✓ Handles single day range
- ✅ PASS: **analyze_positioning_trends response contains expected content**
  - ✓ Contains trend analysis content

### compare_positioning

- ✅ PASS: **compare_positioning with multiple commodities**
  - ✓ Returns comparison data
- ✅ PASS: **compare_positioning with single commodity**
  - ✓ Works with single commodity

### get_positioning_extremes

- ✅ PASS: **get_positioning_extremes with metric=long**
  - ✓ Returns extremes for long
- ✅ PASS: **get_positioning_extremes with metric=short**
  - ✓ Returns extremes for short
- ✅ PASS: **get_positioning_extremes with metric=net**
  - ✓ Returns extremes for net
- ✅ PASS: **get_positioning_extremes with metric=pct_long**
  - ✓ Returns extremes for pct_long
- ✅ PASS: **get_positioning_extremes with metric=pct_short**
  - ✓ Returns extremes for pct_short
- ✅ PASS: **get_positioning_extremes with invalid metric**
  - ✓ Handles invalid metric
- ✅ PASS: **get_positioning_extremes with lookback=1 day**
  - ✓ Works with 1 day lookback
- ✅ PASS: **get_positioning_extremes with lookback=1 week**
  - ✓ Works with 1 week lookback
- ✅ PASS: **get_positioning_extremes with lookback=1 month**
  - ✓ Works with 1 month lookback

### End-to-End

- ✅ PASS: **End-to-end: Analyze trends then compare**
  - ✓ End-to-end workflow successful
