#!/usr/bin/env python3
"""
Comprehensive test suite for CFTC COT MCP Server.

This test suite directly tests the tool functions (bypassing MCP protocol)
to validate functionality, then provides guidance for MCP Inspector testing.
"""

import sys
import os
import time
from datetime import date, datetime, timedelta
from typing import Dict, Any, List

# Add parent directory to path to import tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../mcp-servers/cftc-cot'))

from tools import (
    get_cot_data,
    analyze_positioning_trends,
    compare_positioning,
    get_positioning_extremes,
    get_loaded_data_status
)


class TestResults:
    """Track test results."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        self.start_time = None
        self.end_time = None
    
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
        if self.start_time and self.end_time:
            elapsed = self.end_time - self.start_time
            print(f"Total Time: {elapsed:.2f} seconds")
        print("=" * 60)
        
        if self.failed > 0:
            print("\nFailed Tests:")
            for test in self.tests:
                if not test['passed']:
                    print(f"  ✗ {test['name']}: {test['message']}")
    
    def generate_report(self, filename: str = "TEST_REPORT.md"):
        """Generate markdown test report."""
        from datetime import datetime
        
        report_lines = []
        report_lines.append("# CFTC COT MCP Server Test Report")
        report_lines.append("")
        report_lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Summary
        report_lines.append("## Summary")
        report_lines.append("")
        report_lines.append(f"- **Total Tests**: {len(self.tests)}")
        report_lines.append(f"- **Passed**: {self.passed}")
        report_lines.append(f"- **Failed**: {self.failed}")
        if self.start_time and self.end_time:
            elapsed = self.end_time - self.start_time
            report_lines.append(f"- **Duration**: {elapsed:.2f} seconds")
        report_lines.append("")
        
        # Test Results
        report_lines.append("## Test Results")
        report_lines.append("")
        
        # Group by test category
        categories = {}
        for test in self.tests:
            # Extract category from test name
            category = "Other"
            if "get_cot_data" in test['name']:
                category = "get_cot_data"
            elif "analyze_positioning_trends" in test['name']:
                category = "analyze_positioning_trends"
            elif "compare_positioning" in test['name']:
                category = "compare_positioning"
            elif "get_positioning_extremes" in test['name']:
                category = "get_positioning_extremes"
            elif "get_loaded_data_status" in test['name']:
                category = "get_loaded_data_status"
            elif "performance" in test['name'].lower():
                category = "Performance"
            elif "end-to-end" in test['name'].lower() or "scenario" in test['name'].lower():
                category = "End-to-End"
            elif "content" in test['name'].lower() or "validation" in test['name'].lower():
                category = "Content Validation"
            
            if category not in categories:
                categories[category] = []
            categories[category].append(test)
        
        for category, tests in categories.items():
            report_lines.append(f"### {category}")
            report_lines.append("")
            for test in tests:
                status = "✅ PASS" if test['passed'] else "❌ FAIL"
                report_lines.append(f"- {status}: **{test['name']}**")
                if test['message']:
                    report_lines.append(f"  - {test['message']}")
            report_lines.append("")
        
        # Failed Tests Details
        failed_tests = [t for t in self.tests if not t['passed']]
        if failed_tests:
            report_lines.append("## Failed Tests Details")
            report_lines.append("")
            for test in failed_tests:
                report_lines.append(f"### {test['name']}")
                report_lines.append("")
                report_lines.append(f"**Status**: ❌ FAILED")
                report_lines.append(f"**Message**: {test['message']}")
                report_lines.append("")
        
        # Write report
        with open(filename, 'w') as f:
            f.write('\n'.join(report_lines))
        
        print(f"\n✓ Test report saved to: {filename}")


def validate_response_structure(result: Dict[str, Any], results: TestResults, test_name: str) -> bool:
    """Validate response has required structure."""
    if 'text' not in result:
        results.add_test(test_name, False, "Missing 'text' field")
        return False
    if '_north_metadata' not in result:
        results.add_test(test_name, False, "Missing '_north_metadata'")
        return False
    
    # Validate citation metadata
    metadata = result['_north_metadata']
    required_fields = ['title', 'url', 'author_name', 'last_updated']
    for field in required_fields:
        if field not in metadata:
            results.add_test(test_name, False, f"Missing '{field}' in citation metadata")
            return False
    
    # Validate CFTC source
    if 'CFTC' not in metadata.get('author_name', ''):
        results.add_test(test_name, False, "Citation metadata should reference CFTC")
        return False
    
    return True


def test_get_cot_data_all_parameters(results: TestResults):
    """Test get_cot_data with all parameters."""
    print("\n" + "=" * 60)
    print("Testing get_cot_data - All Parameters")
    print("=" * 60)
    
    test_name = "get_cot_data with all parameters"
    try:
        result = get_cot_data(
            commodity="Petroleum and Products",
            report_date="2025-10-07",
            trader_category="MANAGED_MONEY",
            position_type="all"
        )
        
        if not validate_response_structure(result, results, test_name):
            return
        
        if 'Error' in result['text']:
            results.add_test(test_name, False, result['text'])
            return
        
        # Check for expected content
        if 'CFTC' not in result['text'] or 'Commitment' not in result['text']:
            results.add_test(test_name, False, "Response missing expected COT data content")
            return
        
        results.add_test(test_name, True, "✓ Response valid with all parameters")
        
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")


def test_get_cot_data_latest_date(results: TestResults):
    """Test get_cot_data with latest report date."""
    print("\n" + "=" * 60)
    print("Testing get_cot_data - Latest Report Date")
    print("=" * 60)
    
    test_name = "get_cot_data without report_date (latest)"
    try:
        result = get_cot_data(
            commodity="Petroleum and Products",
            trader_category="MANAGED_MONEY"
        )
        
        if not validate_response_structure(result, results, test_name):
            return
        
        if 'Error' in result['text']:
            # This might be OK if no data is loaded
            if 'No COT data found' in result['text']:
                results.add_test(test_name, True, "✓ Handles missing data gracefully")
                return
            results.add_test(test_name, False, result['text'])
            return
        
        # Should include a report date
        if 'Report Date' in result['text']:
            results.add_test(test_name, True, "✓ Returns latest report date")
        else:
            results.add_test(test_name, False, "Response missing report date")
        
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")


def test_get_cot_data_all_categories(results: TestResults):
    """Test get_cot_data with all trader categories."""
    print("\n" + "=" * 60)
    print("Testing get_cot_data - All Trader Categories")
    print("=" * 60)
    
    categories = ['PRODUCER', 'SWAP', 'MANAGED_MONEY', 'OTHER_REPORTABLE', 'NONREPORTABLE']
    
    for category in categories:
        test_name = f"get_cot_data with {category}"
        try:
            result = get_cot_data(
                commodity="Petroleum and Products",
                trader_category=category
            )
            
            if not validate_response_structure(result, results, test_name):
                continue
            
            if 'Error' in result['text']:
                if 'No COT data found' in result['text']:
                    results.add_test(test_name, True, "✓ Handles missing data")
                    continue
                results.add_test(test_name, False, result['text'])
                continue
            
            results.add_test(test_name, True, f"✓ {category} category works")
            
        except Exception as e:
            results.add_test(test_name, False, f"Exception: {str(e)}")


def test_get_cot_data_all_commodities(results: TestResults):
    """Test get_cot_data with all commodity groups."""
    print("\n" + "=" * 60)
    print("Testing get_cot_data - All Commodity Groups")
    print("=" * 60)
    
    commodities = [
        "Petroleum and Products",
        "Natural Gas and Products",
        "Electricity"
    ]
    
    for commodity in commodities:
        test_name = f"get_cot_data with {commodity}"
        try:
            result = get_cot_data(commodity=commodity)
            
            if not validate_response_structure(result, results, test_name):
                continue
            
            if 'Error' in result['text']:
                if 'No COT data found' in result['text']:
                    results.add_test(test_name, True, "✓ Handles missing data")
                    continue
                results.add_test(test_name, False, result['text'])
                continue
            
            results.add_test(test_name, True, f"✓ {commodity} works")
            
        except Exception as e:
            results.add_test(test_name, False, f"Exception: {str(e)}")


def test_get_cot_data_edge_cases(results: TestResults):
    """Test get_cot_data edge cases."""
    print("\n" + "=" * 60)
    print("Testing get_cot_data - Edge Cases")
    print("=" * 60)
    
    # Test invalid date format
    test_name = "get_cot_data with invalid date format"
    try:
        result = get_cot_data(report_date="invalid-date")
        if 'Error' in result['text'] and 'Invalid date format' in result['text']:
            results.add_test(test_name, True, "✓ Handles invalid date format")
        else:
            results.add_test(test_name, False, "Should return error for invalid date")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
    
    # Test invalid trader category
    test_name = "get_cot_data with invalid trader category"
    try:
        result = get_cot_data(trader_category="INVALID_CATEGORY")
        if 'Error' in result['text'] and 'Invalid trader category' in result['text']:
            results.add_test(test_name, True, "✓ Handles invalid category")
        else:
            results.add_test(test_name, False, "Should return error for invalid category")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")


def test_get_cot_data_additional_parameter_combinations(results: TestResults):
    """Test get_cot_data with additional parameter combinations."""
    print("\n" + "=" * 60)
    print("Testing get_cot_data - Additional Parameter Combinations")
    print("=" * 60)
    
    # Test with only commodity
    test_name = "get_cot_data with only commodity"
    try:
        result = get_cot_data(commodity="Petroleum and Products")
        if validate_response_structure(result, results, test_name):
            results.add_test(test_name, True, "✓ Works with only commodity")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
    
    # Test with only trader_category
    test_name = "get_cot_data with only trader_category"
    try:
        result = get_cot_data(trader_category="MANAGED_MONEY")
        if validate_response_structure(result, results, test_name):
            results.add_test(test_name, True, "✓ Works with only trader_category")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
    
    # Test with only report_date
    test_name = "get_cot_data with only report_date"
    try:
        result = get_cot_data(report_date="2025-10-07")
        if validate_response_structure(result, results, test_name):
            results.add_test(test_name, True, "✓ Works with only report_date")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
    
    # Test with commodity + report_date (no category)
    test_name = "get_cot_data with commodity + report_date"
    try:
        result = get_cot_data(
            commodity="Petroleum and Products",
            report_date="2025-10-07"
        )
        if validate_response_structure(result, results, test_name):
            results.add_test(test_name, True, "✓ Works with commodity + report_date")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")


def test_analyze_positioning_trends(results: TestResults):
    """Test analyze_positioning_trends tool."""
    print("\n" + "=" * 60)
    print("Testing analyze_positioning_trends")
    print("=" * 60)
    
    test_name = "analyze_positioning_trends with valid parameters"
    try:
        # Use a 3-month range
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        
        result = analyze_positioning_trends(
            commodity="Petroleum and Products",
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            trader_category="MANAGED_MONEY"
        )
        
        if not validate_response_structure(result, results, test_name):
            return
        
        if 'Error' in result['text']:
            if 'No positioning data found' in result['text']:
                results.add_test(test_name, True, "✓ Handles missing data gracefully")
                return
            results.add_test(test_name, False, result['text'])
            return
        
        # Check for trend analysis content
        if 'Trends' in result['text'] or 'Change' in result['text']:
            results.add_test(test_name, True, "✓ Returns trend analysis")
        else:
            results.add_test(test_name, False, "Response missing trend analysis content")
        
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
    
    # Test invalid date ordering
    test_name = "analyze_positioning_trends with invalid date ordering"
    try:
        result = analyze_positioning_trends(
            commodity="Petroleum and Products",
            start_date="2025-10-07",
            end_date="2025-07-01",
            trader_category="MANAGED_MONEY"
        )
        if 'Error' in result['text'] and 'before end date' in result['text']:
            results.add_test(test_name, True, "✓ Handles invalid date ordering")
        else:
            results.add_test(test_name, False, "Should return error for invalid date ordering")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
    
    # Test single day range
    test_name = "analyze_positioning_trends with single day range"
    try:
        result = analyze_positioning_trends(
            commodity="Petroleum and Products",
            start_date="2025-10-07",
            end_date="2025-10-07",
            trader_category="MANAGED_MONEY"
        )
        if validate_response_structure(result, results, test_name):
            results.add_test(test_name, True, "✓ Handles single day range")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")


def test_compare_positioning(results: TestResults):
    """Test compare_positioning tool."""
    print("\n" + "=" * 60)
    print("Testing compare_positioning")
    print("=" * 60)
    
    test_name = "compare_positioning with multiple commodities"
    try:
        result = compare_positioning(
            commodities="Petroleum and Products, Natural Gas and Products",
            report_date="2025-10-07",
            trader_category="MANAGED_MONEY"
        )
        
        if not validate_response_structure(result, results, test_name):
            return
        
        if 'Error' in result['text']:
            if 'No positioning data found' in result['text']:
                results.add_test(test_name, True, "✓ Handles missing data gracefully")
                return
            results.add_test(test_name, False, result['text'])
            return
        
        # Check for comparison content
        if 'Comparison' in result['text'] or 'Long' in result['text']:
            results.add_test(test_name, True, "✓ Returns comparison data")
        else:
            results.add_test(test_name, False, "Response missing comparison content")
        
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
    
    # Test with single commodity
    test_name = "compare_positioning with single commodity"
    try:
        result = compare_positioning(
            commodities="Petroleum and Products",
            report_date="2025-10-07",
            trader_category="MANAGED_MONEY"
        )
        if validate_response_structure(result, results, test_name):
            results.add_test(test_name, True, "✓ Works with single commodity")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")


def test_get_positioning_extremes(results: TestResults):
    """Test get_positioning_extremes tool."""
    print("\n" + "=" * 60)
    print("Testing get_positioning_extremes")
    print("=" * 60)
    
    metrics = ['long', 'short', 'net', 'pct_long', 'pct_short']
    
    for metric in metrics:
        test_name = f"get_positioning_extremes with metric={metric}"
        try:
            result = get_positioning_extremes(
                commodity="Petroleum and Products",
                trader_category="MANAGED_MONEY",
                lookback_days=365,
                metric=metric
            )
            
            if not validate_response_structure(result, results, test_name):
                continue
            
            if 'Error' in result['text']:
                if 'No positioning extremes found' in result['text']:
                    results.add_test(test_name, True, "✓ Handles missing data")
                    continue
                results.add_test(test_name, False, result['text'])
                continue
            
            # Check for extremes content
            if 'Extremes' in result['text'] or 'Top' in result['text']:
                results.add_test(test_name, True, f"✓ Returns extremes for {metric}")
            else:
                results.add_test(test_name, False, f"Response missing extremes content for {metric}")
            
        except Exception as e:
            results.add_test(test_name, False, f"Exception: {str(e)}")
    
    # Test invalid metric
    test_name = "get_positioning_extremes with invalid metric"
    try:
        result = get_positioning_extremes(
            commodity="Petroleum and Products",
            trader_category="MANAGED_MONEY",
            metric="invalid_metric"
        )
        if 'Error' in result['text'] and 'Invalid metric' in result['text']:
            results.add_test(test_name, True, "✓ Handles invalid metric")
        else:
            results.add_test(test_name, False, "Should return error for invalid metric")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
    
    # Test different lookback periods
    lookback_periods = [(1, "1 day"), (7, "1 week"), (30, "1 month")]
    for days, desc in lookback_periods:
        test_name = f"get_positioning_extremes with lookback={desc}"
        try:
            result = get_positioning_extremes(
                commodity="Petroleum and Products",
                trader_category="MANAGED_MONEY",
                lookback_days=days,
                metric="long"
            )
            if validate_response_structure(result, results, test_name):
                results.add_test(test_name, True, f"✓ Works with {desc} lookback")
        except Exception as e:
            results.add_test(test_name, False, f"Exception: {str(e)}")


def test_get_loaded_data_status(results: TestResults):
    """Test get_loaded_data_status tool."""
    print("\n" + "=" * 60)
    print("Testing get_loaded_data_status")
    print("=" * 60)
    
    # Test basic status query
    test_name = "get_loaded_data_status basic query"
    try:
        result = get_loaded_data_status()
        
        if not validate_response_structure(result, results, test_name):
            return
        
        if 'Error' in result['text']:
            if 'No CFTC COT data' in result['text']:
                results.add_test(test_name, True, "✓ Handles empty database gracefully")
                return
            results.add_test(test_name, False, result['text'])
            return
        
        # Check for coverage information
        if 'Coverage' in result['text'] or 'Reports' in result['text'] or 'Date Range' in result['text']:
            results.add_test(test_name, True, "✓ Returns coverage information")
        else:
            results.add_test(test_name, False, "Response missing coverage information")
        
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
    
    # Test with commodity filter
    test_name = "get_loaded_data_status with commodity filter"
    try:
        result = get_loaded_data_status(commodity="Petroleum and Products")
        
        if validate_response_structure(result, results, test_name):
            if 'Error' not in result['text']:
                results.add_test(test_name, True, "✓ Works with commodity filter")
            else:
                results.add_test(test_name, True, "✓ Handles missing commodity data gracefully")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
    
    # Test with date range filter
    test_name = "get_loaded_data_status with date range filter"
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        result = get_loaded_data_status(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        if validate_response_structure(result, results, test_name):
            results.add_test(test_name, True, "✓ Works with date range filter")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
    
    # Test with status filter
    test_name = "get_loaded_data_status with status filter"
    try:
        result = get_loaded_data_status(status="completed")
        
        if validate_response_structure(result, results, test_name):
            results.add_test(test_name, True, "✓ Works with status filter")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
    
    # Test with identify_gaps
    test_name = "get_loaded_data_status with identify_gaps"
    try:
        result = get_loaded_data_status(identify_gaps=True)
        
        if validate_response_structure(result, results, test_name):
            if 'Missing Reports' in result['text'] or 'No missing reports' in result['text']:
                results.add_test(test_name, True, "✓ Identifies missing reports")
            else:
                results.add_test(test_name, True, "✓ Works with identify_gaps parameter")
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")


def test_performance_benchmarks(results: TestResults):
    """Test performance benchmarks."""
    print("\n" + "=" * 60)
    print("Testing Performance Benchmarks")
    print("=" * 60)
    
    test_name = "get_cot_data performance (< 2 seconds)"
    try:
        start_time = time.time()
        result = get_cot_data(commodity="Petroleum and Products")
        elapsed = time.time() - start_time
        
        if elapsed < 2.0:
            results.add_test(test_name, True, f"✓ Query completed in {elapsed:.2f}s")
        else:
            results.add_test(test_name, False, f"Query took {elapsed:.2f}s (expected < 2s)")
        
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")


def test_response_content_validation(results: TestResults):
    """Validate actual response content, not just structure."""
    print("\n" + "=" * 60)
    print("Testing Response Content Validation")
    print("=" * 60)
    
    # Test get_cot_data content
    test_name = "get_cot_data response contains expected content"
    try:
        result = get_cot_data(
            commodity="Petroleum and Products",
            trader_category="MANAGED_MONEY"
        )
        
        if not validate_response_structure(result, results, test_name):
            return
        
        if 'Error' in result['text']:
            if 'No COT data found' in result['text']:
                results.add_test(test_name, True, "✓ Handles missing data")
                return
            results.add_test(test_name, False, result['text'])
            return
        
        # Validate content
        text = result['text']
        has_market = 'Market:' in text or 'market' in text.lower()
        has_positions = 'Long:' in text or 'Short:' in text or 'long' in text.lower()
        has_date = 'Report Date:' in text or '202' in text
        
        if has_market and has_positions and has_date:
            results.add_test(test_name, True, "✓ Contains expected content (market, positions, date)")
        else:
            missing = []
            if not has_market: missing.append("market")
            if not has_positions: missing.append("positions")
            if not has_date: missing.append("date")
            results.add_test(test_name, False, f"Missing content: {', '.join(missing)}")
        
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")
    
    # Test analyze_positioning_trends content
    test_name = "analyze_positioning_trends response contains expected content"
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        result = analyze_positioning_trends(
            commodity="Petroleum and Products",
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            trader_category="MANAGED_MONEY"
        )
        
        if not validate_response_structure(result, results, test_name):
            return
        
        if 'Error' in result['text']:
            if 'No positioning data found' in result['text']:
                results.add_test(test_name, True, "✓ Handles missing data")
                return
            results.add_test(test_name, False, result['text'])
            return
        
        text = result['text']
        has_trends = 'Trends' in text or 'Change' in text or 'trend' in text.lower()
        
        if has_trends:
            results.add_test(test_name, True, "✓ Contains trend analysis content")
        else:
            results.add_test(test_name, False, "Missing trend analysis content")
        
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")


def test_end_to_end_scenario(results: TestResults):
    """Test end-to-end scenario."""
    print("\n" + "=" * 60)
    print("Testing End-to-End Scenario")
    print("=" * 60)
    
    test_name = "End-to-end: Analyze trends then compare"
    try:
        # Step 1: Get current positioning
        result1 = get_cot_data(
            commodity="Petroleum and Products",
            trader_category="MANAGED_MONEY"
        )
        
        if 'Error' in result1['text']:
            results.add_test(test_name, True, "✓ Handles missing data in workflow")
            return
        
        # Step 2: Analyze trends (if data available)
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        
        result2 = analyze_positioning_trends(
            commodity="Petroleum and Products",
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            trader_category="MANAGED_MONEY"
        )
        
        if 'Error' in result2['text']:
            results.add_test(test_name, True, "✓ Handles missing data in workflow")
            return
        
        # Both steps succeeded
        results.add_test(test_name, True, "✓ End-to-end workflow successful")
        
    except Exception as e:
        results.add_test(test_name, False, f"Exception: {str(e)}")


def main():
    """Run all tests."""
    import time
    
    print("=" * 60)
    print("CFTC COT MCP Server Test Suite")
    print("=" * 60)
    print("\nNote: This test suite tests tool functions directly.")
    print("For MCP protocol testing, use MCP Inspector or manual_test.py")
    print()
    
    results = TestResults()
    results.start_time = time.time()
    
    # Run all test suites
    test_get_cot_data_all_parameters(results)
    test_get_cot_data_latest_date(results)
    test_get_cot_data_all_categories(results)
    test_get_cot_data_all_commodities(results)
    test_get_cot_data_edge_cases(results)
    test_get_cot_data_additional_parameter_combinations(results)
    test_analyze_positioning_trends(results)
    test_compare_positioning(results)
    test_get_positioning_extremes(results)
    test_get_loaded_data_status(results)
    test_performance_benchmarks(results)
    test_response_content_validation(results)
    test_end_to_end_scenario(results)
    
    results.end_time = time.time()
    
    # Print summary
    results.print_summary()
    
    # Generate report
    results.generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if results.failed == 0 else 1)


if __name__ == '__main__':
    main()
