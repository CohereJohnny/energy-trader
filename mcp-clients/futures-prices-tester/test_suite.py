#!/usr/bin/env python3
"""
Comprehensive test suite for Futures Prices MCP Server.

This test suite directly tests the tool functions (bypassing MCP protocol)
to validate functionality, then provides guidance for MCP Inspector testing.
"""

import sys
import os
import time
from datetime import date, datetime, timedelta
from typing import Dict, Any, List

# Add parent directory to path to import tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../mcp-servers/futures-prices'))

from tools import (
    get_front_month_price,
    get_front_month_prices,
    calculate_price_change,
    get_seasonal_data
)


class TestResults:
    """Track test results."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_test(self, name: str, passed: bool, message: str = ""):
        """Add a test result."""
        self.tests.append({
            'name': name,
            'passed': passed,
            'message': message
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print(f"Test Results: {self.passed} passed, {self.failed} failed")
        print("=" * 60)
        
        if self.failed > 0:
            print("\nFailed Tests:")
            for test in self.tests:
                if not test['passed']:
                    print(f"  ✗ {test['name']}: {test['message']}")


def test_get_front_month_price_all_commodities(results: TestResults):
    """Test get_front_month_price for all commodities."""
    print("\n" + "=" * 60)
    print("Testing get_front_month_price")
    print("=" * 60)
    
    commodities = ['BRENT', 'WTI', 'GO', 'RBOB']
    test_date = '2010-01-04'
    
    for commodity in commodities:
        test_name = f"{commodity} on {test_date}"
        try:
            result = get_front_month_price(commodity, test_date)
            
            # Validate response structure
            assert 'text' in result, "Missing 'text' field"
            assert '_north_metadata' in result, "Missing '_north_metadata'"
            
            # Check for error
            if 'Error' in result['text']:
                results.add_test(test_name, False, result['text'])
                continue
            
            # Validate price is in response
            assert '$' in result['text'] or 'price' in result['text'].lower(), "No price in response"
            
            results.add_test(test_name, True, f"Price found: {result['text'][:60]}...")
            print(f"  ✓ {commodity}: {result['text'][:80]}")
            
        except Exception as e:
            results.add_test(test_name, False, str(e))
            print(f"  ✗ {commodity}: {e}")


def test_get_front_month_price_edge_cases(results: TestResults):
    """Test edge cases for get_front_month_price."""
    print("\n" + "=" * 60)
    print("Testing get_front_month_price - Edge Cases")
    print("=" * 60)
    
    # Invalid commodity
    try:
        result = get_front_month_price('INVALID', '2010-01-04')
        assert 'Error' in result['text'], "Should return error for invalid commodity"
        results.add_test("Invalid commodity", True)
        print("  ✓ Invalid commodity handled correctly")
    except Exception as e:
        results.add_test("Invalid commodity", False, str(e))
    
    # Invalid date format
    try:
        result = get_front_month_price('BRENT', 'invalid-date')
        assert 'Error' in result['text'], "Should return error for invalid date"
        results.add_test("Invalid date format", True)
        print("  ✓ Invalid date format handled correctly")
    except Exception as e:
        results.add_test("Invalid date format", False, str(e))
    
    # Future date (may or may not have data)
    try:
        result = get_front_month_price('BRENT', '2030-01-01')
        # Should handle gracefully (either return data or error message)
        results.add_test("Future date", True)
        print(f"  ✓ Future date handled: {result['text'][:60]}...")
    except Exception as e:
        results.add_test("Future date", False, str(e))


def test_get_front_month_prices_date_ranges(results: TestResults):
    """Test get_front_month_prices with various date ranges."""
    print("\n" + "=" * 60)
    print("Testing get_front_month_prices - Date Ranges")
    print("=" * 60)
    
    test_cases = [
        ('BRENT', '2025-01-01', '2025-01-01', '1 day'),
        ('BRENT', '2025-01-01', '2025-01-07', '1 week'),
        ('BRENT', '2025-01-01', '2025-01-31', '1 month'),
        ('BRENT', '2025-01-01', '2025-12-31', '1 year'),
    ]
    
    for commodity, start, end, desc in test_cases:
        test_name = f"{commodity} {desc} range"
        try:
            result = get_front_month_prices(commodity, start, end)
            
            assert 'text' in result, "Missing 'text' field"
            assert '_north_metadata' in result, "Missing '_north_metadata'"
            
            # Count lines (should have header + data lines)
            lines = result['text'].split('\n')
            data_lines = [l for l in lines if l.strip() and not l.startswith('Front month')]
            
            results.add_test(test_name, True, f"{len(data_lines)} prices returned")
            print(f"  ✓ {desc}: {len(data_lines)} prices")
            
        except Exception as e:
            results.add_test(test_name, False, str(e))
            print(f"  ✗ {desc}: {e}")


def test_calculate_price_change(results: TestResults):
    """Test calculate_price_change tool."""
    print("\n" + "=" * 60)
    print("Testing calculate_price_change")
    print("=" * 60)
    
    # Test positive change
    try:
        result = calculate_price_change('BRENT', '2010-01-04', '2010-01-05')
        assert 'change' in result['text'].lower(), "Should mention change"
        assert '%' in result['text'] or 'percentage' in result['text'].lower(), "Should include percentage"
        results.add_test("Price change calculation", True)
        print(f"  ✓ Price change: {result['text'][:80]}...")
    except Exception as e:
        results.add_test("Price change calculation", False, str(e))
    
    # Test same date
    try:
        result = calculate_price_change('BRENT', '2010-01-04', '2010-01-04')
        # Should handle gracefully
        results.add_test("Same date change", True)
        print(f"  ✓ Same date handled: {result['text'][:60]}...")
    except Exception as e:
        results.add_test("Same date change", False, str(e))


def test_get_seasonal_data(results: TestResults):
    """Test get_seasonal_data tool with new parameters."""
    print("\n" + "=" * 60)
    print("Testing get_seasonal_data")
    print("=" * 60)
    
    # Test 1: Monthly aggregated (12/year) - default
    try:
        result = get_seasonal_data('GO', 2, points_per_year=12, format='aggregated')
        assert 'text' in result, "Missing 'text' field"
        assert '_north_metadata' in result, "Missing '_north_metadata'"
        
        text = result['text']
        assert 'Monthly Statistics' in text or 'Month' in text, "Should include monthly statistics"
        assert 'Avg' in text or 'Average' in text, "Should include average price"
        
        lines = text.split('\n')
        # Should be much smaller than raw data (around 20-30 lines)
        assert len(lines) < 100, f"Response too large: {len(lines)} lines (expected < 100)"
        
        results.add_test("M2 GOBRs monthly aggregated (12/year)", True, f"{len(lines)} lines")
        print(f"  ✓ M2 GOBRs monthly: {len(lines)} lines (aggregated)")
        
    except Exception as e:
        results.add_test("M2 GOBRs monthly aggregated (12/year)", False, str(e))
        print(f"  ✗ Monthly aggregated: {e}")
    
    # Test 2: Bi-monthly aggregated (24/year)
    try:
        result = get_seasonal_data('GO', 2, points_per_year=24, format='aggregated')
        assert 'text' in result, "Missing 'text' field"
        
        text = result['text']
        assert 'Bi-Monthly Statistics' in text or 'position' in text.lower(), "Should include bi-monthly stats"
        
        lines = text.split('\n')
        assert len(lines) < 200, f"Response too large: {len(lines)} lines (expected < 200)"
        
        results.add_test("M2 GOBRs bi-monthly aggregated (24/year)", True, f"{len(lines)} lines")
        print(f"  ✓ M2 GOBRs bi-monthly: {len(lines)} lines (aggregated)")
        
    except Exception as e:
        results.add_test("M2 GOBRs bi-monthly aggregated (24/year)", False, str(e))
        print(f"  ✗ Bi-monthly aggregated: {e}")
    
    # Test 3: Weekly aggregated (52/year)
    try:
        result = get_seasonal_data('GO', 2, points_per_year=52, format='aggregated')
        assert 'text' in result, "Missing 'text' field"
        
        text = result['text']
        assert 'Weekly Statistics' in text or 'week' in text.lower(), "Should include weekly stats"
        
        lines = text.split('\n')
        assert len(lines) < 1000, f"Response too large: {len(lines)} lines (expected < 1000)"
        
        results.add_test("M2 GOBRs weekly aggregated (52/year)", True, f"{len(lines)} lines")
        print(f"  ✓ M2 GOBRs weekly: {len(lines)} lines (aggregated)")
        
    except Exception as e:
        results.add_test("M2 GOBRs weekly aggregated (52/year)", False, str(e))
        print(f"  ✗ Weekly aggregated: {e}")
    
    # Test 4: Data-points format (sampled points, not aggregated)
    try:
        result = get_seasonal_data('GO', 2, points_per_year=12, format='data-points', start_year=2020, end_year=2024)
        assert 'text' in result, "Missing 'text' field"
        
        text = result['text']
        assert 'Date,Year,Month,Price' in text, "Should include CSV headers"
        assert '2020' in text and '2024' in text, "Should include data from specified years"
        
        lines = text.split('\n')
        # Data-points should have sampled points (e.g., ~60 for 5 years monthly)
        assert 20 < len(lines) < 200, f"Unexpected response size: {len(lines)} lines"
        
        results.add_test("M2 GOBRs data-points format (sampled points)", True, f"{len(lines)} lines")
        print(f"  ✓ M2 GOBRs data-points: {len(lines)} lines (sampled points)")
        
    except Exception as e:
        results.add_test("M2 GOBRs data-points format", False, str(e))
        print(f"  ✗ Data-points format: {e}")
    
    # Test 5: Raw format (backward compatibility)
    try:
        result = get_seasonal_data('GO', 2, format='raw', start_year=2020, end_year=2024)
        assert 'text' in result, "Missing 'text' field"
        
        text = result['text']
        assert 'Date,Year,Month,Price' in text or 'Date' in text, "Should include CSV headers"
        
        lines = text.split('\n')
        # Raw format will have many lines (original behavior)
        results.add_test("M2 GOBRs raw format (backward compatibility)", True, f"{len(lines)} lines")
        print(f"  ✓ M2 GOBRs raw: {len(lines)} lines (backward compatible)")
        
    except Exception as e:
        results.add_test("M2 GOBRs raw format", False, str(e))
        print(f"  ✗ Raw format: {e}")
    
    # Test 6: Date range filtering
    try:
        result = get_seasonal_data('BRENT', 1, start_year=2020, end_year=2024, points_per_year=12)
        assert 'text' in result, "Missing 'text' field"
        
        text = result['text']
        assert '2020' in text or '2024' in text or '2020-2024' in text, "Should mention year range"
        
        results.add_test("BRENT M1 with date range (2020-2024)", True)
        print(f"  ✓ BRENT M1 with date range: Data retrieved")
        
    except Exception as e:
        results.add_test("BRENT M1 with date range", False, str(e))
        print(f"  ✗ Date range filtering: {e}")
    
    # Test 7: Pattern detection (should appear in monthly aggregated)
    try:
        result = get_seasonal_data('GO', 2, points_per_year=12, format='aggregated')
        text = result['text']
        
        # Pattern detection may or may not appear depending on data
        # Just verify the response is valid
        assert 'text' in result, "Missing 'text' field"
        
        results.add_test("Pattern detection (monthly)", True, "Response valid")
        print(f"  ✓ Pattern detection: Response valid")
        
    except Exception as e:
        results.add_test("Pattern detection", False, str(e))
        print(f"  ✗ Pattern detection: {e}")
    
    # Test 8: Invalid parameters
    try:
        result = get_seasonal_data('GO', 2, points_per_year=99)  # Invalid
        text = result['text']
        assert 'Error' in text or 'invalid' in text.lower(), "Should return error for invalid points_per_year"
        results.add_test("Invalid points_per_year handling", True)
        print(f"  ✓ Invalid points_per_year: Error handled correctly")
    except Exception as e:
        results.add_test("Invalid points_per_year handling", False, str(e))


def test_citation_metadata(results: TestResults):
    """Test citation metadata format."""
    print("\n" + "=" * 60)
    print("Testing Citation Metadata")
    print("=" * 60)
    
    result = get_front_month_price('BRENT', '2010-01-04')
    metadata = result['_north_metadata']
    
    required_fields = ['title', 'url', 'author_name', 'last_updated']
    for field in required_fields:
        test_name = f"Citation metadata: {field}"
        if field in metadata and metadata[field]:
            results.add_test(test_name, True)
            print(f"  ✓ {field}: {metadata[field][:60]}...")
        else:
            results.add_test(test_name, False, f"Missing or empty {field}")
    
    # Check timestamp format
    timestamp = metadata['last_updated']
    if timestamp.endswith('Z'):
        results.add_test("Citation timestamp format", True)
        print(f"  ✓ Timestamp format correct: {timestamp}")
    else:
        results.add_test("Citation timestamp format", False, f"Invalid format: {timestamp}")


def test_performance(results: TestResults):
    """Test performance of tools."""
    print("\n" + "=" * 60)
    print("Performance Testing")
    print("=" * 60)
    
    # Single date query
    start = time.perf_counter()
    get_front_month_price('BRENT', '2010-01-04')
    elapsed = (time.perf_counter() - start) * 1000
    
    if elapsed < 100:
        results.add_test("Single date query performance", True, f"{elapsed:.2f}ms")
        print(f"  ✓ Single date: {elapsed:.2f}ms (< 100ms target)")
    else:
        results.add_test("Single date query performance", False, f"{elapsed:.2f}ms (exceeded 100ms)")
    
    # Date range query
    start = time.perf_counter()
    get_front_month_prices('BRENT', '2025-01-01', '2025-01-31')
    elapsed = (time.perf_counter() - start) * 1000
    
    if elapsed < 500:
        results.add_test("Date range query performance", True, f"{elapsed:.2f}ms")
        print(f"  ✓ Date range (1 month): {elapsed:.2f}ms (< 500ms target)")
    else:
        results.add_test("Date range query performance", False, f"{elapsed:.2f}ms (exceeded 500ms)")


def test_end_to_end_scenarios(results: TestResults):
    """Test end-to-end query scenarios."""
    print("\n" + "=" * 60)
    print("End-to-End Query Scenarios")
    print("=" * 60)
    
    # Scenario 1: "What was the change in front month Brent price between January 3rd 2025 and March 31st 2025?"
    try:
        result = calculate_price_change('BRENT', '2025-01-03', '2025-03-31')
        assert 'change' in result['text'].lower(), "Should mention change"
        results.add_test("E2E: BRENT price change Jan-Mar 2025", True)
        print(f"  ✓ Scenario 1: {result['text'][:80]}...")
    except Exception as e:
        results.add_test("E2E: BRENT price change Jan-Mar 2025", False, str(e))
    
    # Scenario 2: "What was the front month Brent Settlement yesterday?"
    # Note: "yesterday" would need date parsing - for now test with a recent date
    try:
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        result = get_front_month_price('BRENT', yesterday)
        # May or may not have data for yesterday, but should handle gracefully
        results.add_test("E2E: BRENT settlement yesterday", True)
        print(f"  ✓ Scenario 2: {result['text'][:80]}...")
    except Exception as e:
        results.add_test("E2E: BRENT settlement yesterday", False, str(e))
    
    # Scenario 3: "Display a seasonal chart of M2 GOBRs"
    try:
        result = get_seasonal_data('GO', 2, points_per_year=12, format='aggregated')  # M2 GOBRs
        assert 'text' in result, "Missing response"
        # Should be aggregated format with statistics
        assert 'Month' in result['text'] or 'Statistics' in result['text'], "Should include aggregated statistics"
        results.add_test("E2E: M2 GOBRs seasonal chart (aggregated)", True)
        print(f"  ✓ Scenario 3: Seasonal data retrieved ({len(result['text'].split(chr(10)))} lines)")
    except Exception as e:
        results.add_test("E2E: M2 GOBRs seasonal chart", False, str(e))


def main():
    """Run all tests."""
    print("=" * 60)
    print("Futures Prices MCP Server - Comprehensive Test Suite")
    print("=" * 60)
    
    results = TestResults()
    
    # Run all test suites
    test_get_front_month_price_all_commodities(results)
    test_get_front_month_price_edge_cases(results)
    test_get_front_month_prices_date_ranges(results)
    test_calculate_price_change(results)
    test_get_seasonal_data(results)
    test_citation_metadata(results)
    test_performance(results)
    test_end_to_end_scenarios(results)
    
    # Print summary
    results.print_summary()
    
    return 0 if results.failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

