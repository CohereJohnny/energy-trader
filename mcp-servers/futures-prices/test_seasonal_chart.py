#!/usr/bin/env python3
"""
Test script to generate data for seasonal spread charts.
This simulates what the agent would need to render charts like the examples.
"""

import sys
from collections import defaultdict
from db import get_db

def calculate_averages(data_by_month, years, window_years):
    """Calculate rolling averages for each month."""
    averages = {}
    for month in range(1, 13):
        month_data = []
        for year in sorted(years):
            if year in data_by_month[month]:
                month_data.append((year, data_by_month[month][year]))
        
        # Calculate rolling average
        if len(month_data) >= window_years:
            # Get last N years
            recent_years = sorted([y for y, _ in month_data])[-window_years:]
            recent_prices = [data_by_month[month][y] for y in recent_years]
            avg = sum(recent_prices) / len(recent_prices)
            averages[month] = avg
    
    return averages

def calculate_deviations(data_by_month, averages, year):
    """Calculate deviations from average for a specific year."""
    deviations = {}
    for month in range(1, 13):
        if month in averages and year in data_by_month[month]:
            actual = data_by_month[month][year]
            avg = averages[month]
            deviation = actual - avg
            deviations[month] = deviation
    return deviations

def format_for_charting(data_points, commodity, contract_month_offset):
    """Format data points for seasonal spread charting."""
    # Organize data by month and year
    data_by_month = defaultdict(dict)  # {month: {year: price}}
    years = set()
    
    for point in data_points:
        month = point['month']
        year = point['year']
        price = float(point['settlement_price'])
        data_by_month[month][year] = price
        years.add(year)
    
    # Calculate averages
    years_list = sorted(years)
    avg_5y = calculate_averages(data_by_month, years_list, min(5, len(years_list)))
    avg_15y = calculate_averages(data_by_month, years_list, min(15, len(years_list))) if len(years_list) >= 5 else {}
    
    # Format for CSV output (suitable for charting)
    print("=" * 80)
    print(f"Seasonal Spread Chart Data: {commodity} M{contract_month_offset}")
    print("=" * 80)
    print("\nCSV Format (for charting):")
    print("Month,Year,Price")
    
    # Output individual year series
    for year in sorted(years):
        for month in range(1, 13):
            if year in data_by_month[month]:
                price = data_by_month[month][year]
                print(f"{month},{year},{price:.2f}")
    
    # Output 5-year average
    if avg_5y:
        print("\n5-Year Average:")
        print("Month,Year,Price")
        for month in range(1, 13):
            if month in avg_5y:
                print(f"{month},5y_avg,{avg_5y[month]:.2f}")
    
    # Output 15-year average (if we have enough data)
    if avg_15y:
        print("\n15-Year Average:")
        print("Month,Year,Price")
        for month in range(1, 13):
            if month in avg_15y:
                print(f"{month},15y_avg,{avg_15y[month]:.2f}")
    
    # Output deviations for a specific year (e.g., 2019)
    if 2019 in years:
        deviations_5y = calculate_deviations(data_by_month, avg_5y, 2019)
        if deviations_5y:
            print("\n5-Year Deviation for 2019:")
            print("Month,Year,Deviation")
            for month in range(1, 13):
                if month in deviations_5y:
                    print(f"{month},2019_dev,{deviations_5y[month]:.2f}")
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("Summary:")
    print(f"  Years available: {sorted(years)}")
    print(f"  Total years: {len(years)}")
    print(f"  5-year average available: {bool(avg_5y)}")
    print(f"  15-year average available: {bool(avg_15y)}")
    
    # Show sample data structure
    print("\nSample data structure (first 3 months):")
    for month in range(1, 4):
        if month in data_by_month:
            print(f"  Month {month}:")
            for year in sorted(data_by_month[month].keys())[:3]:
                print(f"    {year}: ${data_by_month[month][year]:.2f}")
            if month in avg_5y:
                print(f"    5y avg: ${avg_5y[month]:.2f}")

def main():
    db = get_db()
    
    # Test 1: GO M2 (Gasoil M2) - similar to the charts shown
    print("\n" + "=" * 80)
    print("TEST 1: GO M2 Seasonal Spread Data")
    print("=" * 80)
    data_points = db.get_seasonal_data_points('GO', 2, 12, 2019, 2024)
    format_for_charting(data_points, 'GO', 2)
    
    # Test 2: BRENT M1 - test with different commodity
    print("\n" + "=" * 80)
    print("TEST 2: BRENT M1 Seasonal Spread Data")
    print("=" * 80)
    data_points = db.get_seasonal_data_points('BRENT', 1, 12, 2019, 2024)
    format_for_charting(data_points, 'BRENT', 1)
    
    # Test 3: Check if we have enough years for 15-year average
    print("\n" + "=" * 80)
    print("TEST 3: Checking Historical Data Range")
    print("=" * 80)
    # Try to get all available years
    data_points_all = db.get_seasonal_data_points('GO', 2, 12, None, None)
    years_all = sorted(set(p['year'] for p in data_points_all))
    print(f"GO M2 - All available years: {years_all}")
    print(f"Total years: {len(years_all)}")
    print(f"Can calculate 5-year average: {len(years_all) >= 5}")
    print(f"Can calculate 15-year average: {len(years_all) >= 15}")

if __name__ == "__main__":
    main()

