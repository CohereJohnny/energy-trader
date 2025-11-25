## 1. Research & Design
- [x] 1.1 Research trader use cases for seasonal data analysis
- [ ] 1.2 Design aggregated statistics format and structure
- [ ] 1.3 Design date range filtering approach
- [ ] 1.4 Design pattern detection algorithms
- [ ] 1.5 Review design with user

## 2. Database Layer Updates
- [x] 2.1 Design sampling logic for 12/year (monthly), 24/year (bi-monthly), 52/year (weekly)
- [x] 2.2 Add aggregation query function for monthly statistics (12/year)
- [x] 2.3 Add sampling query function for bi-monthly statistics (24/year)
- [x] 2.4 Add sampling query function for weekly statistics (52/year)
- [x] 2.5 Update `get_contract_prices_by_month_offset` to support date filtering and sampling
- [x] 2.6 Add query function for pattern detection (implemented in tools.py)
- [x] 2.7 Optimize queries for efficient sampling (use window functions, pre-filtering)
- [ ] 2.8 Test aggregation and sampling queries with sample data

## 3. Tool Implementation
- [x] 3.1 Update `get_seasonal_data` function signature (add `start_year`, `end_year`, `format`, `points_per_year` parameters)
- [x] 3.2 Implement sampling logic for 12/year (monthly)
- [x] 3.3 Implement sampling logic for 24/year (bi-monthly: mid-month and end-of-month)
- [x] 3.4 Implement sampling logic for 52/year (weekly)
- [x] 3.5 Implement aggregated statistics calculation for each sampling frequency
- [x] 3.6 Implement pattern detection logic
- [x] 3.7 Implement format selection (aggregated, data-points, raw)
- [x] 3.8 Update response formatting for aggregated output (handle different granularities)
- [x] 3.9 Implement data-points format (sampled points without aggregation)
- [x] 3.10 Maintain backward compatibility for raw data format

## 4. Testing
- [x] 4.1 Test monthly sampling (12/year) accuracy
- [x] 4.2 Test bi-monthly sampling (24/year) accuracy
- [x] 4.3 Test weekly sampling (52/year) accuracy
- [x] 4.4 Test aggregated statistics accuracy for each sampling frequency
- [x] 4.5 Test date range filtering with different sampling frequencies
- [x] 4.6 Test pattern detection with different sampling frequencies
- [x] 4.7 Test all output formats (aggregated, data-points, raw)
- [x] 4.8 Validate response size reduction for each sampling frequency
- [x] 4.9 Test edge cases (single year, no data, invalid points_per_year, etc.)
- [x] 4.10 Validate sampling consistency (same parameters return same results)

**Test Results**:
- ✅ Monthly (12/year): 19 lines (98% reduction from 30k+)
- ✅ Bi-monthly (24/year): 31 lines (97% reduction)
- ✅ Weekly (52/year): 77 lines (95% reduction)
- ✅ Data-points format: Returns sampled points (e.g., 53 lines for 5 years monthly)
- ✅ Raw format: Backward compatible, returns original CSV format
- ✅ Date range filtering: Working correctly
- ✅ Invalid parameters: Handled gracefully
- ✅ All statistics calculated correctly (count, avg, min, max, std_dev, median)

## 5. Documentation
- [ ] 5.1 Update tool documentation with new parameters
- [ ] 5.2 Update agent instructions with new tool behavior
- [ ] 5.3 Document aggregation methodology
- [ ] 5.4 Add examples of aggregated output

