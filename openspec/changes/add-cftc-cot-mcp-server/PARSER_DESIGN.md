# CFTC Disaggregated COT Parser Design

## Overview

The parser will handle fixed-width format CFTC Disaggregated COT reports from HTML pages. The parser must be robust, handle edge cases, and provide clear error messages.

## Parser Architecture

### Components

1. **HTML Extractor**: Extract `<pre>` content from HTML
2. **Block Parser**: Identify and parse commodity blocks
3. **Header Parser**: Extract market/exchange/code/date
4. **Position Parser**: Parse position rows (All/Old/Other)
5. **Change Parser**: Parse week-over-week changes
6. **Percentage Parser**: Parse percentage data
7. **Trader Count Parser**: Parse trader counts
8. **Concentration Parser**: Parse concentration data
9. **Data Validator**: Validate parsed data integrity

### Error Handling Strategy

- **Graceful Degradation**: Continue parsing other commodities if one fails
- **Detailed Logging**: Log all parsing errors with context
- **Validation**: Validate data types, ranges, and relationships
- **Missing Data**: Handle missing values (represented as ".", "0", or empty)
- **Format Variations**: Handle slight variations in column positions

## Test Strategy

### Test Categories

1. **Unit Tests**: Test each parser component independently
2. **Integration Tests**: Test full parsing pipeline
3. **Edge Case Tests**: Test malformed data, missing fields, etc.
4. **Real Data Tests**: Test with actual CFTC data samples
5. **Regression Tests**: Test with historical data variations

### Test Coverage Goals

- **Line Coverage**: > 95%
- **Branch Coverage**: > 90%
- **Edge Cases**: 100% of identified edge cases
- **Error Paths**: All error handling paths tested

## Test Cases

### 1. HTML Extraction Tests
- ✅ Extract `<pre>` content from valid HTML
- ✅ Handle missing `<pre>` tag
- ✅ Handle malformed HTML
- ✅ Handle empty HTML
- ✅ Handle encoding issues

### 2. Block Identification Tests
- ✅ Identify commodity blocks correctly
- ✅ Handle missing commodity headers
- ✅ Handle malformed headers
- ✅ Handle multiple commodities
- ✅ Handle empty blocks

### 3. Header Parsing Tests
- ✅ Parse market name correctly
- ✅ Parse exchange name correctly
- ✅ Parse CFTC code correctly
- ✅ Parse report date correctly
- ✅ Handle missing header fields
- ✅ Handle malformed dates
- ✅ Handle various date formats

### 4. Position Parsing Tests
- ✅ Parse "All" row (Futures + Options)
- ✅ Parse "Old" row (Futures only)
- ✅ Parse "Other" row (Options only)
- ✅ Handle missing position rows
- ✅ Handle malformed position rows
- ✅ Parse all trader categories:
  - Producer/Merchant (Long, Short)
  - Swap Dealers (Long, Short, Spreading)
  - Managed Money (Long, Short, Spreading)
  - Other Reportables (Long, Short, Spreading)
  - Nonreportable (Long, Short)
- ✅ Handle missing values (".", "0", empty)
- ✅ Handle negative values
- ✅ Handle values with commas
- ✅ Validate position relationships (e.g., Long + Short + Spread ≤ Open Interest)

### 5. Change Parsing Tests
- ✅ Parse week-over-week changes
- ✅ Handle missing change row
- ✅ Handle negative changes
- ✅ Handle zero changes
- ✅ Validate change calculations

### 6. Percentage Parsing Tests
- ✅ Parse percentage values
- ✅ Handle missing percentage row
- ✅ Validate percentage ranges (0-100%)
- ✅ Handle decimal percentages
- ✅ Validate percentage sums

### 7. Trader Count Parsing Tests
- ✅ Parse trader counts for each category
- ✅ Handle missing trader count row
- ✅ Handle missing values (".")
- ✅ Validate counts are non-negative integers

### 8. Concentration Parsing Tests
- ✅ Parse concentration percentages
- ✅ Parse by Gross Position (4 or less, 8 or less)
- ✅ Parse by Net Position (4 or less, 8 or less)
- ✅ Handle missing concentration section
- ✅ Validate concentration ranges

### 9. Data Validation Tests
- ✅ Validate Open Interest > 0
- ✅ Validate positions are non-negative
- ✅ Validate position relationships
- ✅ Validate percentages sum correctly
- ✅ Validate date formats
- ✅ Validate CFTC codes

### 10. Integration Tests
- ✅ Parse complete commodity block
- ✅ Parse multiple commodities
- ✅ Parse full report
- ✅ Handle mixed valid/invalid commodities
- ✅ Preserve data relationships

### 11. Edge Case Tests
- ✅ Empty report
- ✅ Report with only headers
- ✅ Report with missing sections
- ✅ Report with extra whitespace
- ✅ Report with special characters in names
- ✅ Report with very large numbers
- ✅ Report with zero Open Interest
- ✅ Report with all zeros
- ✅ Report with missing trader categories

### 12. Real Data Tests
- ✅ Parse actual CFTC petroleum_lf.htm data
- ✅ Validate against known values
- ✅ Test with multiple report dates
- ✅ Test with different commodity types

## Parser Implementation Plan

### Phase 1: Core Parser Structure
1. Create parser module structure
2. Implement HTML extractor
3. Implement block identifier
4. Create base parser class

### Phase 2: Individual Parsers
1. Header parser
2. Position parser
3. Change parser
4. Percentage parser
5. Trader count parser
6. Concentration parser

### Phase 3: Integration
1. Combine parsers into full pipeline
2. Add error handling
3. Add logging
4. Add data validation

### Phase 4: Testing
1. Create test fixtures
2. Write unit tests
3. Write integration tests
4. Write edge case tests
5. Achieve >95% coverage

### Phase 5: Refinement
1. Fix bugs found in testing
2. Optimize performance
3. Add documentation
4. Final validation

## Test Fixtures

### Fixture Types

1. **Minimal Valid Block**: Smallest valid commodity block
2. **Complete Block**: Full commodity block with all sections
3. **Multiple Commodities**: Report with multiple commodities
4. **Edge Cases**: Various edge case scenarios
5. **Real Data**: Actual CFTC data samples
6. **Malformed Data**: Intentionally malformed data for error testing

## Error Reporting

### Error Types

1. **Parsing Errors**: Failed to parse specific field
2. **Validation Errors**: Data failed validation checks
3. **Format Errors**: Unexpected format encountered
4. **Missing Data Errors**: Required data missing

### Error Messages

- Include line number
- Include context (surrounding lines)
- Include expected vs. actual values
- Include recovery action taken

## Performance Considerations

- Parse in streaming fashion (don't load entire file into memory)
- Use efficient string operations
- Cache parsed results when possible
- Optimize regex patterns

## Maintainability

- Clear separation of concerns
- Well-documented code
- Type hints for all functions
- Comprehensive docstrings
- Clear variable names

