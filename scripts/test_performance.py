#!/usr/bin/env python3
"""
Performance testing script for database queries.
"""

import time
import os
import psycopg2
from datetime import date, timedelta

# Database connection parameters
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'energy_trader'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
}


def test_single_date_query(conn, commodity='BRENT', test_date='2010-01-04', iterations=100):
    """Test single date front month price lookup."""
    cursor = conn.cursor()
    
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        cursor.execute(
            "SELECT * FROM futures_prices.get_front_month_price(%s, %s)",
            (commodity, test_date)
        )
        cursor.fetchone()
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        times.append(elapsed)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"Single date query ({iterations} iterations):")
    print(f"  Average: {avg_time:.2f}ms")
    print(f"  Min: {min_time:.2f}ms")
    print(f"  Max: {max_time:.2f}ms")
    print(f"  ✓ {'PASS' if avg_time < 100 else 'FAIL'} (< 100ms target)")
    return avg_time < 100


def test_date_range_query(conn, commodity='BRENT', start_date='2025-01-01', end_date='2025-03-31', iterations=10):
    """Test date range front month price lookup."""
    cursor = conn.cursor()
    
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        cursor.execute(
            """
            SELECT * FROM futures_prices.front_month_prices
            WHERE commodity_code = %s
                AND trade_date >= %s
                AND trade_date <= %s
            ORDER BY trade_date
            """,
            (commodity, start_date, end_date)
        )
        cursor.fetchall()
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        times.append(elapsed)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\nDate range query ({iterations} iterations, ~90 days):")
    print(f"  Average: {avg_time:.2f}ms")
    print(f"  Min: {min_time:.2f}ms")
    print(f"  Max: {max_time:.2f}ms")
    print(f"  ✓ {'PASS' if avg_time < 500 else 'FAIL'} (< 500ms target)")
    return avg_time < 500


def test_year_range_query(conn, commodity='BRENT', year=2024, iterations=5):
    """Test full year range query."""
    cursor = conn.cursor()
    
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        cursor.execute(
            """
            SELECT * FROM futures_prices.front_month_prices
            WHERE commodity_code = %s
                AND trade_date >= %s
                AND trade_date <= %s
            ORDER BY trade_date
            """,
            (commodity, start_date, end_date)
        )
        cursor.fetchall()
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        times.append(elapsed)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\nFull year query ({iterations} iterations, ~252 trading days):")
    print(f"  Average: {avg_time:.2f}ms")
    print(f"  Min: {min_time:.2f}ms")
    print(f"  Max: {max_time:.2f}ms")
    print(f"  ✓ {'PASS' if avg_time < 2000 else 'FAIL'} (< 2000ms target)")
    return avg_time < 2000


def main():
    """Run performance tests."""
    print("Performance Testing for Futures Prices Database\n")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(**db_config)
        print("✓ Connected to database\n")
    except psycopg2.Error as e:
        print(f"❌ Error connecting to database: {e}")
        return
    
    results = []
    
    try:
        # Test 1: Single date query
        results.append(test_single_date_query(conn))
        
        # Test 2: Date range query (3 months)
        results.append(test_date_range_query(conn))
        
        # Test 3: Full year query
        results.append(test_year_range_query(conn))
        
        print("\n" + "=" * 60)
        print(f"\nOverall: {'✓ PASS' if all(results) else '✗ FAIL'}")
        print(f"Tests passed: {sum(results)}/{len(results)}")
        
    finally:
        conn.close()


if __name__ == '__main__':
    main()

