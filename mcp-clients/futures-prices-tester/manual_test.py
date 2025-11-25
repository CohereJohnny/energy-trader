#!/usr/bin/env python3
"""
Interactive manual testing script for Futures Prices MCP Server.

This script allows you to manually test each tool with custom inputs.
"""

import sys
import os
from datetime import date, datetime, timedelta

# Add parent directory to path to import tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../mcp-servers/futures-prices'))

from tools import (
    get_front_month_price,
    get_front_month_prices,
    calculate_price_change,
    get_seasonal_data
)


def print_response(result: dict):
    """Pretty print tool response."""
    print("\n" + "=" * 60)
    print("RESPONSE:")
    print("=" * 60)
    print(result['text'])
    print("\n" + "-" * 60)
    print("CITATION METADATA:")
    print("-" * 60)
    metadata = result['_north_metadata']
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    print("=" * 60 + "\n")


def test_get_front_month_price():
    """Test get_front_month_price tool."""
    print("\n" + "=" * 60)
    print("TEST: get_front_month_price")
    print("=" * 60)
    
    commodity = input("Enter commodity (BRENT, WTI, GO, RBOB) [BRENT]: ").strip() or "BRENT"
    test_date = input("Enter date (YYYY-MM-DD) [2010-01-04]: ").strip() or "2010-01-04"
    
    print(f"\nCalling get_front_month_price('{commodity}', '{test_date}')...")
    result = get_front_month_price(commodity, test_date)
    print_response(result)


def test_get_front_month_prices():
    """Test get_front_month_prices tool."""
    print("\n" + "=" * 60)
    print("TEST: get_front_month_prices")
    print("=" * 60)
    
    commodity = input("Enter commodity (BRENT, WTI, GO, RBOB) [BRENT]: ").strip() or "BRENT"
    start_date = input("Enter start date (YYYY-MM-DD) [2025-01-01]: ").strip() or "2025-01-01"
    end_date = input("Enter end date (YYYY-MM-DD) [2025-01-31]: ").strip() or "2025-01-31"
    
    print(f"\nCalling get_front_month_prices('{commodity}', '{start_date}', '{end_date}')...")
    result = get_front_month_prices(commodity, start_date, end_date)
    print_response(result)
    
    # Show summary
    lines = result['text'].split('\n')
    data_lines = [l for l in lines if l.strip() and '$' in l]
    print(f"Summary: {len(data_lines)} prices returned")


def test_calculate_price_change():
    """Test calculate_price_change tool."""
    print("\n" + "=" * 60)
    print("TEST: calculate_price_change")
    print("=" * 60)
    
    commodity = input("Enter commodity (BRENT, WTI, GO, RBOB) [BRENT]: ").strip() or "BRENT"
    start_date = input("Enter start date (YYYY-MM-DD) [2025-01-03]: ").strip() or "2025-01-03"
    end_date = input("Enter end date (YYYY-MM-DD) [2025-03-31]: ").strip() or "2025-03-31"
    
    print(f"\nCalling calculate_price_change('{commodity}', '{start_date}', '{end_date}')...")
    result = calculate_price_change(commodity, start_date, end_date)
    print_response(result)


def test_get_seasonal_data():
    """Test get_seasonal_data tool."""
    print("\n" + "=" * 60)
    print("TEST: get_seasonal_data")
    print("=" * 60)
    
    commodity = input("Enter commodity (BRENT, WTI, GO, RBOB) [GO]: ").strip() or "GO"
    month_offset = input("Enter contract month offset (1=M1, 2=M2, etc.) [2]: ").strip() or "2"
    
    try:
        month_offset = int(month_offset)
    except ValueError:
        print("Invalid month offset, using 2")
        month_offset = 2
    
    # New parameters
    print("\nSampling frequency options:")
    print("  12 = Monthly (default, 1 per month)")
    print("  24 = Bi-monthly (2 per month: mid and end)")
    print("  52 = Weekly (1 per week)")
    points_per_year_input = input("Enter points_per_year [12]: ").strip() or "12"
    
    try:
        points_per_year = int(points_per_year_input)
        if points_per_year not in [12, 24, 52]:
            print("Invalid points_per_year, using 12")
            points_per_year = 12
    except ValueError:
        print("Invalid points_per_year, using 12")
        points_per_year = 12
    
    format_input = input("Enter format (aggregated/data-points/raw) [aggregated]: ").strip() or "aggregated"
    if format_input not in ["aggregated", "raw", "data-points"]:
        print("Invalid format, using aggregated")
        format_input = "aggregated"
    
    start_year_input = input("Enter start_year (optional, press Enter to skip): ").strip()
    start_year = int(start_year_input) if start_year_input else None
    
    end_year_input = input("Enter end_year (optional, press Enter to skip): ").strip()
    end_year = int(end_year_input) if end_year_input else None
    
    print(f"\nCalling get_seasonal_data('{commodity}', {month_offset}, start_year={start_year}, end_year={end_year}, points_per_year={points_per_year}, format='{format_input}')...")
    result = get_seasonal_data(
        commodity, month_offset, start_year, end_year, points_per_year, format_input
    )
    
    # Show response
    lines = result['text'].split('\n')
    print("\n" + "=" * 60)
    print("RESPONSE:")
    print("=" * 60)
    
    # For aggregated format, show full response (it's already concise)
    # For raw format, show first 20 lines
    if format_input == "raw" and len(lines) > 20:
        for line in lines[:20]:
            print(line)
        print(f"... ({len(lines) - 20} more lines)")
    else:
        for line in lines:
            print(line)
    
    print("\n" + "-" * 60)
    print("CITATION METADATA:")
    print("-" * 60)
    metadata = result['_north_metadata']
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    print("=" * 60)
    print(f"\nTotal lines: {len(lines)}")
    print("=" * 60 + "\n")


def test_end_to_end_scenarios():
    """Test end-to-end scenarios."""
    print("\n" + "=" * 60)
    print("END-TO-END SCENARIOS")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "Price Change Query",
            "description": "What was the change in front month Brent price between January 3rd 2025 and March 31st 2025?",
            "tool": "calculate_price_change",
            "args": {"commodity": "BRENT", "start_date": "2025-01-03", "end_date": "2025-03-31"}
        },
        {
            "name": "Yesterday's Settlement",
            "description": "What was the front month Brent Settlement yesterday?",
            "tool": "get_front_month_price",
            "args": {"commodity": "BRENT", "trade_date": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')}
        },
        {
            "name": "Seasonal Chart Data (Monthly)",
            "description": "Display a seasonal chart of M2 GOBRs (monthly aggregated)",
            "tool": "get_seasonal_data",
            "args": {"commodity": "GO", "contract_month_offset": 2, "points_per_year": 12, "format": "aggregated"}
        },
        {
            "name": "Seasonal Chart Data (Bi-monthly)",
            "description": "Display a seasonal chart of M2 GOBRs (bi-monthly aggregated)",
            "tool": "get_seasonal_data",
            "args": {"commodity": "GO", "contract_month_offset": 2, "points_per_year": 24, "format": "aggregated"}
        },
        {
            "name": "Seasonal Chart Data (Raw)",
            "description": "Display raw seasonal data for M2 GOBRs",
            "tool": "get_seasonal_data",
            "args": {"commodity": "GO", "contract_month_offset": 2, "format": "raw"}
        }
    ]
    
    print("\nAvailable scenarios:")
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']}: {scenario['description']}")
    
    choice = input(f"\nSelect scenario (1-{len(scenarios)}) or 'all': ").strip().lower()
    
    if choice == 'all':
        for scenario in scenarios:
            print(f"\n{'='*60}")
            print(f"SCENARIO: {scenario['name']}")
            print(f"Query: {scenario['description']}")
            print("="*60)
            
            if scenario['tool'] == 'get_front_month_price':
                result = get_front_month_price(**scenario['args'])
            elif scenario['tool'] == 'calculate_price_change':
                result = calculate_price_change(**scenario['args'])
            elif scenario['tool'] == 'get_seasonal_data':
                result = get_seasonal_data(**scenario['args'])
            
            print_response(result)
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(scenarios):
                scenario = scenarios[idx]
                print(f"\n{'='*60}")
                print(f"SCENARIO: {scenario['name']}")
                print(f"Query: {scenario['description']}")
                print("="*60)
                
                if scenario['tool'] == 'get_front_month_price':
                    result = get_front_month_price(**scenario['args'])
                elif scenario['tool'] == 'calculate_price_change':
                    result = calculate_price_change(**scenario['args'])
                elif scenario['tool'] == 'get_seasonal_data':
                    result = get_seasonal_data(**scenario['args'])
                
                print_response(result)
            else:
                print("Invalid choice")
        except ValueError:
            print("Invalid choice")


def main():
    """Main interactive menu."""
    print("=" * 60)
    print("Futures Prices MCP Server - Manual Testing")
    print("=" * 60)
    print("\nThis script allows you to manually test each MCP tool.")
    print("Make sure the database is running (docker compose ps)")
    print()
    
    while True:
        print("\n" + "=" * 60)
        print("SELECT TEST:")
        print("=" * 60)
        print("1. get_front_month_price (single date)")
        print("2. get_front_month_prices (date range)")
        print("3. calculate_price_change")
        print("4. get_seasonal_data")
        print("5. End-to-end scenarios")
        print("6. Exit")
        print("=" * 60)
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        try:
            if choice == '1':
                test_get_front_month_price()
            elif choice == '2':
                test_get_front_month_prices()
            elif choice == '3':
                test_calculate_price_change()
            elif choice == '4':
                test_get_seasonal_data()
            elif choice == '5':
                test_end_to_end_scenarios()
            elif choice == '6':
                print("\nExiting...")
                break
            else:
                print("Invalid choice. Please enter 1-6.")
        except KeyboardInterrupt:
            print("\n\nInterrupted. Exiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()

