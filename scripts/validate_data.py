#!/usr/bin/env python3
"""
Data integrity validation script.
"""

import os
import psycopg2
import csv
from pathlib import Path

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'energy_trader'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
}


def validate_data_integrity():
    """Validate data integrity after loading."""
    print("Data Integrity Validation\n")
    print("=" * 60)
    
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        # Check commodities
        cursor.execute("SELECT code, name FROM futures_prices.commodities ORDER BY code")
        commodities = cursor.fetchall()
        print(f"\n✓ Commodities: {len(commodities)}")
        for code, name in commodities:
            print(f"  - {code}: {name}")
        
        # Check contracts per commodity
        print(f"\n✓ Contracts per commodity:")
        cursor.execute("""
            SELECT c.code, COUNT(DISTINCT ct.id) as contract_count
            FROM futures_prices.commodities c
            LEFT JOIN futures_prices.contracts ct ON c.id = ct.commodity_id
            GROUP BY c.code
            ORDER BY c.code
        """)
        for code, count in cursor.fetchall():
            print(f"  - {code}: {count} contracts")
        
        # Check prices per commodity
        print(f"\n✓ Prices per commodity:")
        cursor.execute("""
            SELECT c.code, COUNT(p.id) as price_count,
                   MIN(p.trade_date) as earliest_date,
                   MAX(p.trade_date) as latest_date
            FROM futures_prices.commodities c
            JOIN futures_prices.contracts ct ON c.id = ct.commodity_id
            JOIN futures_prices.prices p ON ct.id = p.contract_id
            GROUP BY c.code
            ORDER BY c.code
        """)
        total_prices = 0
        for code, count, earliest, latest in cursor.fetchall():
            total_prices += count
            print(f"  - {code}: {count:,} prices ({earliest} to {latest})")
        
        print(f"\n✓ Total prices: {total_prices:,}")
        
        # Check for NULL prices
        cursor.execute("SELECT COUNT(*) FROM futures_prices.prices WHERE settlement_price IS NULL")
        null_count = cursor.fetchone()[0]
        print(f"✓ NULL prices: {null_count:,} (expected - some contracts may not have prices on all dates)")
        
        # Check date coverage
        cursor.execute("""
            SELECT COUNT(DISTINCT trade_date) as unique_dates
            FROM futures_prices.prices
        """)
        unique_dates = cursor.fetchone()[0]
        print(f"✓ Unique trading dates: {unique_dates}")
        
        # Validate front month prices exist
        cursor.execute("""
            SELECT COUNT(*) FROM futures_prices.front_month_prices
        """)
        front_month_count = cursor.fetchone()[0]
        print(f"✓ Front month price records: {front_month_count:,}")
        
        print("\n" + "=" * 60)
        print("\n✓ Data integrity validation complete!")
        
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    validate_data_integrity()

