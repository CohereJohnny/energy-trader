# How to Add More Tests to CFTC COT Test Suite

## Quick Guide

### 1. View Current Test Results

After running tests, view the report:
```bash
cat TEST_REPORT.md
```

Or open it in your editor to see:
- Test summary (passed/failed counts)
- Test results grouped by tool
- Failed test details
- Execution time

### 2. Review Coverage Gaps

Check `TEST_COVERAGE.md` for:
- Current coverage analysis
- Missing test areas
- Priority recommendations

### 3. Add New Tests

#### Option A: Add to Existing Test Function

Edit `test_suite.py` and add test cases to an existing function:

```python
def test_get_cot_data_additional_cases(results: TestResults):
    """Test additional get_cot_data scenarios."""
    print("\n" + "=" * 60)
    print("Testing get_cot_data - Additional Cases")
    print("=" * 60)
    
    # Test with only commodity (no category, no date)
    test_name = "get_cot_data with only commodity"
    try:
        result = get_cot_data(commodity="Petroleum and Products")
        if validate_response_structure(result, results, test_name):
            results.add_test(test_name, True, "✓ Works with only commodity")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
    
    # Add more test cases...
```

Then add the function call to `main()`:
```python
def main():
    # ... existing tests ...
    test_get_cot_data_additional_cases(results)
```

#### Option B: Create New Test Function

Create a completely new test function:

```python
def test_get_cot_data_single_day_range(results: TestResults):
    """Test get_cot_data with single day scenarios."""
    print("\n" + "=" * 60)
    print("Testing get_cot_data - Single Day Range")
    print("=" * 60)
    
    test_name = "get_cot_data with same start/end date"
    try:
        result = get_cot_data(
            commodity="Petroleum and Products",
            report_date="2025-10-07"
        )
        # Validate and add test result
        if validate_response_structure(result, results, test_name):
            results.add_test(test_name, True, "✓ Handles single day")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
```

#### Option C: Extend Edge Case Testing

Add more edge cases to existing edge case functions:

```python
def test_get_cot_data_edge_cases(results: TestResults):
    # ... existing edge cases ...
    
    # Add new edge case
    test_name = "get_cot_data with future date"
    try:
        future_date = (date.today() + timedelta(days=365)).strftime('%Y-%m-%d')
        result = get_cot_data(report_date=future_date)
        if 'Error' in result['text'] or 'No COT data found' in result['text']:
            results.add_test(test_name, True, "✓ Handles future date")
        else:
            results.add_test(test_name, False, "Should handle future date")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
```

### 4. Test Your New Tests

Run the test suite to verify new tests work:
```bash
./run_tests.sh
# Or:
python3 test_suite.py
```

Check the updated `TEST_REPORT.md` to see your new tests.

### 5. Validate Test Results

Ensure new tests:
- ✅ Actually test something meaningful
- ✅ Pass when data is available
- ✅ Handle missing data gracefully
- ✅ Provide clear error messages
- ✅ Are included in TEST_REPORT.md

## Example: Adding Response Content Validation

Here's a complete example of adding a new test category:

```python
def test_response_content_validation(results: TestResults):
    """Validate actual response content, not just structure."""
    print("\n" + "=" * 60)
    print("Testing Response Content Validation")
    print("=" * 60)
    
    test_name = "get_cot_data response contains expected fields"
    try:
        result = get_cot_data(
            commodity="Petroleum and Products",
            trader_category="MANAGED_MONEY"
        )
        
        if not validate_response_structure(result, results, test_name):
            return
        
        if 'Error' in result['text']:
            results.add_test(test_name, True, "✓ Handles missing data")
            return
        
        # Validate content
        text = result['text']
        has_market = 'Market:' in text or 'market' in text.lower()
        has_positions = 'Long:' in text or 'Short:' in text
        has_percentages = '%' in text
        has_date = 'Report Date:' in text or '202' in text
        
        if has_market and has_positions:
            results.add_test(test_name, True, "✓ Response contains expected content")
        else:
            results.add_test(test_name, False, 
                f"Missing content: market={has_market}, positions={has_positions}")
            
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
```

Then add to `main()`:
```python
test_response_content_validation(results)
```

## Priority Test Areas

Based on `TEST_COVERAGE.md`, prioritize:

### High Priority
1. **Response Content Validation** - Verify actual data values
2. **Date Range Edge Cases** - Single day, large ranges, missing periods
3. **Error Handling** - Database errors, invalid data
4. **Real-World Scenarios** - Actual trader use cases

### Medium Priority
1. **Parameter Combinations** - All valid combinations
2. **Data Validation** - Calculations, formatting
3. **Performance** - Load testing, concurrent queries

### Low Priority
1. **Extreme Edge Cases** - Very old dates, very large ranges
2. **Stress Testing** - Maximum data volumes

## Test Template

Use this template for new tests:

```python
def test_your_new_test(results: TestResults):
    """Description of what this test validates."""
    print("\n" + "=" * 60)
    print("Testing Your New Test")
    print("=" * 60)
    
    test_name = "Descriptive test name"
    try:
        # Setup
        # ... prepare test data ...
        
        # Execute
        result = some_tool_call(...)
        
        # Validate structure
        if not validate_response_structure(result, results, test_name):
            return
        
        # Handle errors
        if 'Error' in result['text']:
            if 'expected error condition' in result['text']:
                results.add_test(test_name, True, "✓ Handles error correctly")
            else:
                results.add_test(test_name, False, result['text'])
            return
        
        # Validate content/behavior
        # ... check specific conditions ...
        
        # Success
        results.add_test(test_name, True, "✓ Test passed")
        
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
```

## Running Specific Tests

To test a specific function during development:

```python
# At the bottom of test_suite.py, temporarily:
if __name__ == '__main__':
    results = TestResults()
    results.start_time = time.time()
    
    # Run only your new test
    test_your_new_test(results)
    
    results.end_time = time.time()
    results.print_summary()
    results.generate_report()
```

## Best Practices

1. **One Assertion Per Test**: Each test should validate one thing
2. **Clear Test Names**: Use descriptive names that explain what's being tested
3. **Handle Missing Data**: Tests should work even if data isn't loaded
4. **Validate Structure First**: Always check response structure before content
5. **Provide Context**: Include helpful messages in test results
6. **Group Related Tests**: Keep related tests in the same function
7. **Update Coverage Doc**: Update `TEST_COVERAGE.md` as you add tests

## Checking Coverage Progress

After adding tests:
1. Run test suite: `./run_tests.sh`
2. Review `TEST_REPORT.md` for new tests
3. Update `TEST_COVERAGE.md` to mark covered areas
4. Verify coverage improvements

## Questions?

- See `TEST_COVERAGE.md` for detailed coverage analysis
- See `README.md` for general testing information
- See `MANUAL_TESTING.md` for manual testing guidance

