#!/usr/bin/env python3
"""
Additional test coverage for CFTC COT MCP Server.

This file contains additional tests to improve coverage as outlined in TEST_COVERAGE.md.
These tests can be integrated into the main test_suite.py or run separately.
"""

import sys
import os
from datetime import date, timedelta
from typing import Dict, Any

# Add parent directory to path to import tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../mcp-servers/cftc-cot'))

from tools import (
    get_cot_data,
    analyze_positioning_trends,
    compare_positioning,
    get_positioning_extremes
)


def validate_response_structure(result: Dict[str, Any]) -> bool:
    """Validate response has required structure."""
    return 'text' in result and '_north_metadata' in result


def test_get_cot_data_parameter_combinations():
    """Test get_cot_data with various parameter combinations."""
    print("\n" + "=" * 60)
    print("Testing get_cot_data - Parameter Combinations")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Only commodity
    try:
        result = get_cot_data(commodity="Petroleum and Products")
        if validate_response_structure(result):
            print("  ✓ Only commodity parameter")
            tests_passed += 1
        else:
            print("  ✗ Only commodity parameter - invalid structure")
            tests_failed += 1
    except Exception as e:
        print(f"  ✗ Only commodity parameter - Exception: {e}")
        tests_failed += 1
    
    # Test 2: Only trader_category
    try:
        result = get_cot_data(trader_category="MANAGED_MONEY")
        if validate_response_structure(result):
            print("  ✓ Only trader_category parameter")
            tests_passed += 1
        else:
            print("  ✗ Only trader_category parameter - invalid structure")
            tests_failed += 1
    except Exception as e:
        print(f"  ✗ Only trader_category parameter - Exception: {e}")
        tests_failed += 1
    
    # Test 3: Only report_date
    try:
        result = get_cot_data(report_date="2025-10-07")
        if validate_response_structure(result):
            print("  ✓ Only report_date parameter")
            tests_passed += 1
        else:
            print("  ✗ Only report_date parameter - invalid structure")
            tests_failed += 1
    except Exception as e:
        print(f"  ✗ Only report_date parameter - Exception: {e}")
        tests_failed += 1
    
    # Test 4: Commodity + report_date (no category)
    try:
        result = get_cot_data(
            commodity="Petroleum and Products",
            report_date="2025-10-07"
        )
        if validate_response_structure(result):
            print("  ✓ Commodity + report_date")
            tests_passed += 1
        else:
            print("  ✗ Commodity + report_date - invalid structure")
            tests_failed += 1
    except Exception as e:
        print(f"  ✗ Commodity + report_date - Exception: {e}")
        tests_failed += 1
    
    # Test 5: Commodity + category (no date)
    try:
        result = get_cot_data(
            commodity="Petroleum and Products",
            trader_category="MANAGED_MONEY"
        )
        if validate_response_structure(result):
            print("  ✓ Commodity + category")
            tests_passed += 1
        else:
            print("  ✗ Commodity + category - invalid structure")
            tests_failed += 1
    except Exception as e:
        print(f"  ✗ Commodity + category - Exception: {e}")
        tests_failed += 1
    
    print(f"\n  Results: {tests_passed} passed, {tests_failed} failed")
    return tests_passed, tests_failed


def test_analyze_positioning_trends_date_ranges():
    """Test analyze_positioning_trends with various date ranges."""
    print("\n" + "=" * 60)
    print("Testing analyze_positioning_trends - Date Ranges")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Single day range
    try:
        result = analyze_positioning_trends(
            commodity="Petroleum and Products",
            start_date="2025-10-07",
            end_date="2025-10-07",
            trader_category="MANAGED_MONEY"
        )
        if validate_response_structure(result):
            print("  ✓ Single day range")
            tests_passed += 1
        else:
            print("  ✗ Single day range - invalid structure")
            tests_failed += 1
    except Exception as e:
        print(f"  ✗ Single day range - Exception: {e}")
        tests_failed += 1
    
    # Test 2: Large date range (1 year)
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        result = analyze_positioning_trends(
            commodity="Petroleum and Products",
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            trader_category="MANAGED_MONEY"
        )
        if validate_response_structure(result):
            print("  ✓ Large date range (1 year)")
            tests_passed += 1
        else:
            print("  ✗ Large date range - invalid structure")
            tests_failed += 1
    except Exception as e:
        print(f"  ✗ Large date range - Exception: {e}")
        tests_failed += 1
    
    print(f"\n  Results: {tests_passed} passed, {tests_failed} failed")
    return tests_passed, tests_failed


def test_compare_positioning_combinations():
    """Test compare_positioning with various commodity combinations."""
    print("\n" + "=" * 60)
    print("Testing compare_positioning - Commodity Combinations")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Single commodity
    try:
        result = compare_positioning(
            commodities="Petroleum and Products",
            report_date="2025-10-07",
            trader_category="MANAGED_MONEY"
        )
        if validate_response_structure(result):
            print("  ✓ Single commodity")
            tests_passed += 1
        else:
            print("  ✗ Single commodity - invalid structure")
            tests_failed += 1
    except Exception as e:
        print(f"  ✗ Single commodity - Exception: {e}")
        tests_failed += 1
    
    # Test 2: All three commodity groups
    try:
        result = compare_positioning(
            commodities="Petroleum and Products, Natural Gas and Products, Electricity",
            report_date="2025-10-07",
            trader_category="MANAGED_MONEY"
        )
        if validate_response_structure(result):
            print("  ✓ All three commodity groups")
            tests_passed += 1
        else:
            print("  ✗ All three commodity groups - invalid structure")
            tests_failed += 1
    except Exception as e:
        print(f"  ✗ All three commodity groups - Exception: {e}")
        tests_failed += 1
    
    print(f"\n  Results: {tests_passed} passed, {tests_failed} failed")
    return tests_passed, tests_failed


def test_get_positioning_extremes_lookback_periods():
    """Test get_positioning_extremes with various lookback periods."""
    print("\n" + "=" * 60)
    print("Testing get_positioning_extremes - Lookback Periods")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    lookback_periods = [
        (1, "1 day"),
        (7, "1 week"),
        (30, "1 month"),
        (90, "3 months"),
        (365, "1 year"),
    ]
    
    for days, desc in lookback_periods:
        try:
            result = get_positioning_extremes(
                commodity="Petroleum and Products",
                trader_category="MANAGED_MONEY",
                lookback_days=days,
                metric="long"
            )
            if validate_response_structure(result):
                print(f"  ✓ Lookback {desc} ({days} days)")
                tests_passed += 1
            else:
                print(f"  ✗ Lookback {desc} - invalid structure")
                tests_failed += 1
        except Exception as e:
            print(f"  ✗ Lookback {desc} - Exception: {e}")
            tests_failed += 1
    
    print(f"\n  Results: {tests_passed} passed, {tests_failed} failed")
    return tests_passed, tests_failed


def test_response_content_validation():
    """Validate actual response content, not just structure."""
    print("\n" + "=" * 60)
    print("Testing Response Content Validation")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test get_cot_data content
    try:
        result = get_cot_data(
            commodity="Petroleum and Products",
            trader_category="MANAGED_MONEY"
        )
        
        if not validate_response_structure(result):
            print("  ✗ get_cot_data - invalid structure")
            tests_failed += 1
        else:
            text = result['text']
            has_market = 'Market:' in text or 'market' in text.lower()
            has_positions = 'Long:' in text or 'Short:' in text or 'long' in text.lower()
            has_date = 'Report Date:' in text or '202' in text
            
            if has_market and has_positions and has_date:
                print("  ✓ get_cot_data contains expected content")
                tests_passed += 1
            else:
                print(f"  ✗ get_cot_data missing content: market={has_market}, positions={has_positions}, date={has_date}")
                tests_failed += 1
    except Exception as e:
        print(f"  ✗ get_cot_data content validation - Exception: {e}")
        tests_failed += 1
    
    # Test analyze_positioning_trends content
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        result = analyze_positioning_trends(
            commodity="Petroleum and Products",
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            trader_category="MANAGED_MONEY"
        )
        
        if not validate_response_structure(result):
            print("  ✗ analyze_positioning_trends - invalid structure")
            tests_failed += 1
        else:
            text = result['text']
            has_trends = 'Trends' in text or 'Change' in text or 'trend' in text.lower()
            has_period = start_date.strftime('%Y-%m-%d') in text or end_date.strftime('%Y-%m-%d') in text
            
            if has_trends:
                print("  ✓ analyze_positioning_trends contains expected content")
                tests_passed += 1
            else:
                print(f"  ✗ analyze_positioning_trends missing content: trends={has_trends}")
                tests_failed += 1
    except Exception as e:
        print(f"  ✗ analyze_positioning_trends content validation - Exception: {e}")
        tests_failed += 1
    
    print(f"\n  Results: {tests_passed} passed, {tests_failed} failed")
    return tests_passed, tests_failed


def main():
    """Run additional coverage tests."""
    print("=" * 60)
    print("CFTC COT MCP Server - Additional Coverage Tests")
    print("=" * 60)
    print("\nThese tests cover areas identified in TEST_COVERAGE.md")
    print()
    
    total_passed = 0
    total_failed = 0
    
    # Run test suites
    passed, failed = test_get_cot_data_parameter_combinations()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_analyze_positioning_trends_date_ranges()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_compare_positioning_combinations()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_get_positioning_extremes_lookback_periods()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_response_content_validation()
    total_passed += passed
    total_failed += failed
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Additional Coverage Tests Summary")
    print("=" * 60)
    print(f"Total: {total_passed + total_failed} tests")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print("=" * 60)
    
    return 0 if total_failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

