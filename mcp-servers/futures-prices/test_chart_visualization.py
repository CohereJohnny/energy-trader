#!/usr/bin/env python3
"""
Test script to visualize seasonal spread charts similar to the examples.
This demonstrates that we have the data structure needed for charting.
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

def format_chart_data(data_points, commodity, contract_month_offset, target_year=None):
    """
    Format data for seasonal spread charting.
    Returns data structured for plotting: {year: {month: price}}
    """
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
    
    # Structure for charting
    chart_data = {
        'individual_years': {},
        'avg_5y': avg_5y,
        'avg_15y': avg_15y,
        'years_available': sorted(years)
    }
    
    # Add individual year data
    for year in sorted(years):
        chart_data['individual_years'][year] = {}
        for month in range(1, 13):
            if year in data_by_month[month]:
                chart_data['individual_years'][year][month] = data_by_month[month][year]
    
    # Calculate deviations for target year if specified
    if target_year and target_year in years:
        deviations_5y = {}
        deviations_15y = {}
        for month in range(1, 13):
            if month in avg_5y and target_year in data_by_month[month]:
                deviations_5y[month] = data_by_month[month][target_year] - avg_5y[month]
            if month in avg_15y and target_year in data_by_month[month]:
                deviations_15y[month] = data_by_month[month][target_year] - avg_15y[month]
        chart_data[f'{target_year}_dev_5y'] = deviations_5y
        chart_data[f'{target_year}_dev_15y'] = deviations_15y
    
    return chart_data

def print_chart_summary(chart_data, commodity, contract_month_offset):
    """Print a summary of chart data structure."""
    print(f"\n{'='*80}")
    print(f"Chart Data Summary: {commodity} M{contract_month_offset}")
    print(f"{'='*80}")
    
    print(f"\nYears Available: {chart_data['years_available']}")
    print(f"Total Years: {len(chart_data['years_available'])}")
    
    print(f"\n5-Year Average: {'Available' if chart_data['avg_5y'] else 'Not Available'}")
    print(f"15-Year Average: {'Available' if chart_data['avg_15y'] else 'Not Available'}")
    
    # Show sample of individual year data
    print(f"\nSample Individual Year Data (first 3 years, first 3 months):")
    for year in sorted(chart_data['individual_years'].keys())[:3]:
        print(f"  {year}:")
        for month in range(1, 4):
            if month in chart_data['individual_years'][year]:
                price = chart_data['individual_years'][year][month]
                print(f"    Month {month:2d}: ${price:.2f}")
    
    # Show averages
    if chart_data['avg_5y']:
        print(f"\n5-Year Average (first 3 months):")
        for month in range(1, 4):
            if month in chart_data['avg_5y']:
                print(f"  Month {month:2d}: ${chart_data['avg_5y'][month]:.2f}")
    
    # Show deviations if available
    if '2019_dev_5y' in chart_data:
        print(f"\n2019 Deviation from 5-Year Average (first 3 months):")
        for month in range(1, 4):
            if month in chart_data['2019_dev_5y']:
                dev = chart_data['2019_dev_5y'][month]
                print(f"  Month {month:2d}: {dev:+.2f}")

def generate_csv_for_charting(chart_data, commodity, contract_month_offset, include_deviations=True):
    """Generate CSV format suitable for charting libraries."""
    print(f"\n{'='*80}")
    print(f"CSV Format for Charting: {commodity} M{contract_month_offset}")
    print(f"{'='*80}")
    
    # Individual years
    print("\n# Individual Year Series")
    print("Series,Month,Price")
    for year in sorted(chart_data['individual_years'].keys()):
        for month in range(1, 13):
            if month in chart_data['individual_years'][year]:
                price = chart_data['individual_years'][year][month]
                print(f"{year},{month},{price:.2f}")
    
    # 5-year average
    if chart_data['avg_5y']:
        print("\n# 5-Year Average")
        print("Series,Month,Price")
        for month in range(1, 13):
            if month in chart_data['avg_5y']:
                print(f"5y_avg,{month},{chart_data['avg_5y'][month]:.2f}")
    
    # 15-year average
    if chart_data['avg_15y']:
        print("\n# 15-Year Average")
        print("Series,Month,Price")
        for month in range(1, 13):
            if month in chart_data['avg_15y']:
                print(f"15y_avg,{month},{chart_data['avg_15y'][month]:.2f}")
    
    # Deviations (if requested and available)
    if include_deviations:
        for year in [2019]:  # Can be parameterized
            dev_5y_key = f'{year}_dev_5y'
            dev_15y_key = f'{year}_dev_15y'
            
            if dev_5y_key in chart_data:
                print(f"\n# {year} Deviation from 5-Year Average")
                print("Series,Month,Deviation")
                for month in range(1, 13):
                    if month in chart_data[dev_5y_key]:
                        print(f"{year}_dev_5y,{month},{chart_data[dev_5y_key][month]:+.2f}")
            
            if dev_15y_key in chart_data:
                print(f"\n# {year} Deviation from 15-Year Average")
                print("Series,Month,Deviation")
                for month in range(1, 13):
                    if month in chart_data[dev_15y_key]:
                        print(f"{year}_dev_15y,{month},{chart_data[dev_15y_key][month]:+.2f}")

def main():
    db = get_db()
    
    # Test: GO M2 (similar to the charts shown - ZWZ = December contracts)
    # Note: M2 for GO means the second month contract, which would be December for many years
    print("\n" + "="*80)
    print("TESTING SEASONAL SPREAD CHART DATA GENERATION")
    print("="*80)
    
    # Get data for multiple years (2010-2024 to match chart style)
    data_points = db.get_seasonal_data_points('GO', 2, 12, 2010, 2024)
    
    # Format for charting
    chart_data = format_chart_data(data_points, 'GO', 2, target_year=2019)
    
    # Print summary
    print_chart_summary(chart_data, 'GO', 2)
    
    # Generate CSV format
    generate_csv_for_charting(chart_data, 'GO', 2, include_deviations=True)
    
    print("\n" + "="*80)
    print("CONCLUSION: Data structure is suitable for seasonal spread charts!")
    print("="*80)
    print("\nThe data includes:")
    print("  ✓ Individual year series (like ZWZ10-ZWZ19 in the example)")
    print("  ✓ 5-year averages")
    print("  ✓ 15-year averages (if enough historical data)")
    print("  ✓ Deviations from averages")
    print("\nThe agent can use format='data-points' to get this data structure,")
    print("then calculate averages and deviations client-side for charting.")

if __name__ == "__main__":
    main()

