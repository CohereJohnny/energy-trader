#!/usr/bin/env python3
"""
Interactive manual testing script for CFTC COT MCP Server tools.

This script provides an interactive menu for testing MCP tools manually.
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
    get_positioning_extremes,
    get_loaded_data_status
)


def print_separator():
    """Print separator line."""
    print("\n" + "=" * 80 + "\n")


def print_result(result: Dict[str, Any]):
    """Pretty print tool result."""
    print_separator()
    print("RESULT:")
    print_separator()
    print(result['text'])
    print_separator()
    
    if '_north_metadata' in result:
        print("Citation Metadata:")
        metadata = result['_north_metadata']
        print(f"  Title: {metadata.get('title', 'N/A')}")
        print(f"  URL: {metadata.get('url', 'N/A')}")
        print(f"  Author: {metadata.get('author_name', 'N/A')}")
        print(f"  Last Updated: {metadata.get('last_updated', 'N/A')}")
        print_separator()


def test_get_cot_data():
    """Test get_cot_data tool."""
    print("\n=== Test get_cot_data ===")
    
    print("\nParameters (press Enter to skip optional parameters):")
    commodity = input("  Commodity (Petroleum and Products, Natural Gas and Products, Electricity): ").strip() or None
    report_date = input("  Report Date (YYYY-MM-DD, or leave empty for latest): ").strip() or None
    trader_category = input("  Trader Category (PRODUCER, SWAP, MANAGED_MONEY, OTHER_REPORTABLE, NONREPORTABLE): ").strip() or None
    position_type = input("  Position Type (all, old, other) [default: all]: ").strip() or 'all'
    
    try:
        result = get_cot_data(
            commodity=commodity,
            report_date=report_date,
            trader_category=trader_category,
            position_type=position_type
        )
        print_result(result)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_analyze_positioning_trends():
    """Test analyze_positioning_trends tool."""
    print("\n=== Test analyze_positioning_trends ===")
    
    print("\nParameters:")
    commodity = input("  Commodity (required): ").strip()
    if not commodity:
        print("✗ Commodity is required")
        return
    
    start_date = input("  Start Date (YYYY-MM-DD): ").strip()
    if not start_date:
        print("✗ Start date is required")
        return
    
    end_date = input("  End Date (YYYY-MM-DD): ").strip()
    if not end_date:
        print("✗ End date is required")
        return
    
    trader_category = input("  Trader Category (required): ").strip()
    if not trader_category:
        print("✗ Trader category is required")
        return
    
    try:
        result = analyze_positioning_trends(
            commodity=commodity,
            start_date=start_date,
            end_date=end_date,
            trader_category=trader_category
        )
        print_result(result)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_compare_positioning():
    """Test compare_positioning tool."""
    print("\n=== Test compare_positioning ===")
    
    print("\nParameters:")
    commodities = input("  Commodities (comma-separated, e.g., 'Petroleum and Products, Natural Gas and Products'): ").strip()
    if not commodities:
        print("✗ Commodities are required")
        return
    
    report_date = input("  Report Date (YYYY-MM-DD): ").strip()
    if not report_date:
        print("✗ Report date is required")
        return
    
    trader_category = input("  Trader Category (required): ").strip()
    if not trader_category:
        print("✗ Trader category is required")
        return
    
    try:
        result = compare_positioning(
            commodities=commodities,
            report_date=report_date,
            trader_category=trader_category
        )
        print_result(result)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_get_positioning_extremes():
    """Test get_positioning_extremes tool."""
    print("\n=== Test get_positioning_extremes ===")
    
    print("\nParameters:")
    commodity = input("  Commodity (required): ").strip()
    if not commodity:
        print("✗ Commodity is required")
        return
    
    trader_category = input("  Trader Category (required): ").strip()
    if not trader_category:
        print("✗ Trader category is required")
        return
    
    lookback_days = input("  Lookback Days [default: 365]: ").strip()
    lookback_days = int(lookback_days) if lookback_days else 365
    
    metric = input("  Metric (long, short, net, pct_long, pct_short) [default: long]: ").strip() or 'long'
    
    try:
        result = get_positioning_extremes(
            commodity=commodity,
            trader_category=trader_category,
            lookback_days=lookback_days,
            metric=metric
        )
        print_result(result)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_get_loaded_data_status():
    """Test get_loaded_data_status tool."""
    print("\n=== Test get_loaded_data_status ===")
    
    print("\nParameters (press Enter to skip optional parameters):")
    commodity = input("  Commodity (optional): ").strip() or None
    start_date = input("  Start Date (YYYY-MM-DD, optional): ").strip() or None
    end_date = input("  End Date (YYYY-MM-DD, optional): ").strip() or None
    status = input("  Status (pending, downloading, parsing, loading, completed, failed, optional): ").strip() or None
    identify_gaps_input = input("  Identify gaps in data? (y/n) [default: n]: ").strip().lower()
    identify_gaps = identify_gaps_input == 'y'
    
    try:
        result = get_loaded_data_status(
            commodity=commodity,
            start_date=start_date,
            end_date=end_date,
            status=status,
            identify_gaps=identify_gaps
        )
        print_result(result)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def show_menu():
    """Show main menu."""
    print("\n" + "=" * 80)
    print("CFTC COT MCP Server - Manual Testing")
    print("=" * 80)
    print("\nSelect a tool to test:")
    print("  1. get_cot_data")
    print("  2. analyze_positioning_trends")
    print("  3. compare_positioning")
    print("  4. get_positioning_extremes")
    print("  5. get_loaded_data_status")
    print("  6. Run all tools with example parameters")
    print("  0. Exit")
    print()


def run_examples():
    """Run all tools with example parameters."""
    print("\n=== Running Example Tests ===")
    
    # Example 1: get_cot_data
    print("\n1. get_cot_data example:")
    print("   Parameters: commodity='Petroleum and Products', trader_category='MANAGED_MONEY'")
    try:
        result = get_cot_data(
            commodity="Petroleum and Products",
            trader_category="MANAGED_MONEY"
        )
        print_result(result)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Example 2: analyze_positioning_trends
    print("\n2. analyze_positioning_trends example:")
    end_date = date.today()
    start_date = end_date - timedelta(days=90)
    print(f"   Parameters: commodity='Petroleum and Products', start_date='{start_date}', end_date='{end_date}', trader_category='MANAGED_MONEY'")
    try:
        result = analyze_positioning_trends(
            commodity="Petroleum and Products",
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            trader_category="MANAGED_MONEY"
        )
        print_result(result)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Example 3: compare_positioning
    print("\n3. compare_positioning example:")
    print("   Parameters: commodities='Petroleum and Products, Natural Gas and Products', report_date='2025-10-07', trader_category='MANAGED_MONEY'")
    try:
        result = compare_positioning(
            commodities="Petroleum and Products, Natural Gas and Products",
            report_date="2025-10-07",
            trader_category="MANAGED_MONEY"
        )
        print_result(result)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Example 4: get_positioning_extremes
    print("\n4. get_positioning_extremes example:")
    print("   Parameters: commodity='Petroleum and Products', trader_category='MANAGED_MONEY', lookback_days=365, metric='long'")
    try:
        result = get_positioning_extremes(
            commodity="Petroleum and Products",
            trader_category="MANAGED_MONEY",
            lookback_days=365,
            metric="long"
        )
        print_result(result)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Example 5: get_loaded_data_status
    print("\n5. get_loaded_data_status example:")
    print("   Parameters: identify_gaps=True")
    try:
        result = get_loaded_data_status(
            identify_gaps=True
        )
        print_result(result)
    except Exception as e:
        print(f"   ✗ Error: {e}")


def main():
    """Main interactive loop."""
    while True:
        show_menu()
        choice = input("Enter choice: ").strip()
        
        if choice == '0':
            print("\nExiting...")
            break
        elif choice == '1':
            test_get_cot_data()
        elif choice == '2':
            test_analyze_positioning_trends()
        elif choice == '3':
            test_compare_positioning()
        elif choice == '4':
            test_get_positioning_extremes()
        elif choice == '5':
            test_get_loaded_data_status()
        elif choice == '6':
            run_examples()
        else:
            print("\n✗ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == '__main__':
    main()

