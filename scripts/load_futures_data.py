#!/usr/bin/env python3
"""
Load Futures Prices Data into PostgreSQL

This script loads CSV files containing futures prices into the PostgreSQL database.
It handles:
- Parsing contract names using CME Group month codes
- Normalizing data into commodities, contracts, and prices tables
- Handling missing/null prices
- Date parsing
"""

import csv
import sys
import os
from datetime import datetime, date
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_batch
from psycopg2 import sql

# Add scripts directory to path to import month_code_parser
sys.path.insert(0, str(Path(__file__).parent))
from month_code_parser import parse_contract_name, get_cme_code


# Commodity mapping from CSV filename to database code
COMMODITY_MAPPING = {
    'BR_CUR.csv': 'BRENT',
    'WTI_CUR.csv': 'WTI',
    'GO_CUR.csv': 'GO',
    'RB_CUR.csv': 'RBOB',
}


def parse_date(date_str: str) -> date:
    """
    Parse date string in format M/D/YY, M/D/YYYY, or DD-MMM.
    
    Args:
        date_str: Date string (e.g., "1/4/10", "1/4/2010", or "26-Aug")
        
    Returns:
        date object
    """
    # Try DD-MMM format (e.g., "26-Aug")
    if '-' in date_str and len(date_str.split('-')) == 2:
        try:
            day_str, month_str = date_str.split('-')
            day = int(day_str)
            month_abbr = month_str[:3].lower()
            
            month_map = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            
            if month_abbr in month_map:
                # Assume current year for DD-MMM format (or could infer from context)
                # For now, we'll skip these as they're ambiguous without year
                # This is a data quality issue in the CSV
                raise ValueError(f"Ambiguous date format (no year): {date_str}")
        except (ValueError, IndexError):
            pass
    
    # Try M/D/YY or M/D/YYYY format
    try:
        parts = date_str.split('/')
        if len(parts) == 3:
            month, day, year = map(int, parts)
            # Handle 2-digit years (assume 2000s if < 50, else 1900s)
            if year < 100:
                if year < 50:
                    year += 2000
                else:
                    year += 1900
            return date(year, month, day)
    except (ValueError, IndexError):
        pass
    
    raise ValueError(f"Unable to parse date: {date_str}")


def calculate_expiration_date(year: int, month: int) -> date:
    """
    Calculate expiration date (first business day of expiration month).
    For simplicity, we'll use the 1st of the month.
    In production, this might need to account for exchange holidays.
    
    Args:
        year: Expiration year
        month: Expiration month (1-12)
        
    Returns:
        date object
    """
    return date(year, month, 1)


def get_or_create_commodity(cursor, commodity_code: str, name: str, exchange: str) -> int:
    """
    Get commodity ID or create if it doesn't exist.
    
    Returns:
        commodity_id
    """
    cursor.execute(
        "SELECT id FROM futures_prices.commodities WHERE code = %s",
        (commodity_code,)
    )
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    cursor.execute(
        """
        INSERT INTO futures_prices.commodities (code, name, exchange)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (commodity_code, name, exchange)
    )
    return cursor.fetchone()[0]


def get_or_create_contract(cursor, commodity_id: int, expiration_year: int, 
                           expiration_month: int, cme_code: str) -> int:
    """
    Get contract ID or create if it doesn't exist.
    
    Returns:
        contract_id
    """
    cursor.execute(
        """
        SELECT id FROM futures_prices.contracts
        WHERE commodity_id = %s AND expiration_year = %s AND expiration_month = %s
        """,
        (commodity_id, expiration_year, expiration_month)
    )
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    expiration_date = calculate_expiration_date(expiration_year, expiration_month)
    
    cursor.execute(
        """
        INSERT INTO futures_prices.contracts 
        (commodity_id, expiration_year, expiration_month, cme_month_code, expiration_date)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (commodity_id, expiration_year, expiration_month, cme_code, expiration_date)
    )
    return cursor.fetchone()[0]


def load_csv_file(cursor, csv_path: Path, commodity_code: str, commodity_name: str, exchange: str):
    """
    Load a single CSV file into the database.
    
    Args:
        cursor: Database cursor
        csv_path: Path to CSV file
        commodity_code: Commodity code (BRENT, WTI, GO, RBOB)
        commodity_name: Full commodity name
        exchange: Exchange name (ICE, NYMEX)
    """
    print(f"Loading {csv_path.name}...")
    
    # Get or create commodity
    commodity_id = get_or_create_commodity(cursor, commodity_code, commodity_name, exchange)
    
    # Read CSV file
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header row
        
        # First column is date, rest are contract columns
        date_col_idx = 0
        contract_columns = header[1:]  # Skip first empty column if present
        
        # Parse contract metadata from column headers
        contract_info = {}
        for col_idx, col_name in enumerate(contract_columns):
            if not col_name or col_name.strip() == '':
                continue
            
            try:
                parsed = parse_contract_name(col_name)
                contract_info[col_idx + 1] = parsed  # +1 because date is column 0
            except ValueError as e:
                print(f"Warning: Skipping invalid contract column '{col_name}': {e}")
                continue
        
        # Process data rows
        prices_to_insert = []
        contracts_created = 0
        rows_processed = 0
        
        for row_idx, row in enumerate(reader, start=2):  # Start at 2 because header is row 1
            if not row or len(row) == 0:
                continue
            
            # Parse trade date
            try:
                trade_date = parse_date(row[date_col_idx])
            except (ValueError, IndexError) as e:
                print(f"Warning: Skipping row {row_idx} - invalid date: {e}")
                continue
            
            # Process each contract column
            for col_idx, contract_data in contract_info.items():
                if col_idx >= len(row):
                    continue
                
                price_str = row[col_idx].strip()
                if not price_str or price_str == '':
                    continue  # Skip empty prices (NULL)
                
                try:
                    price = float(price_str)
                except ValueError:
                    print(f"Warning: Invalid price '{price_str}' for contract {contract_data['commodity']}_{contract_data['year']}{contract_data['cme_code']} on {trade_date}")
                    continue
                
                # Get or create contract
                contract_id = get_or_create_contract(
                    cursor,
                    commodity_id,
                    contract_data['year'],
                    contract_data['month'],
                    contract_data['cme_code']
                )
                
                if contract_id not in [c[0] for c in prices_to_insert if len(c) > 0]:
                    contracts_created += 1
                
                # Add price to batch insert list
                prices_to_insert.append((contract_id, trade_date, price))
            
            rows_processed += 1
            if rows_processed % 1000 == 0:
                print(f"  Processed {rows_processed} rows...")
        
        # Batch insert prices
        print(f"  Inserting {len(prices_to_insert)} prices...")
        execute_batch(
            cursor,
            """
            INSERT INTO futures_prices.prices (contract_id, trade_date, settlement_price)
            VALUES (%s, %s, %s)
            ON CONFLICT (contract_id, trade_date) DO UPDATE
            SET settlement_price = EXCLUDED.settlement_price,
                updated_at = NOW()
            """,
            prices_to_insert,
            page_size=1000
        )
        
        print(f"  ✓ Loaded {len(prices_to_insert)} prices from {rows_processed} rows")
        print(f"  ✓ Created/updated {len(contract_info)} contracts")


def main():
    """Main function to load all CSV files."""
    # Database connection parameters (update as needed)
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'energy_trader'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
    }
    
    # Data directory
    data_dir = Path(__file__).parent.parent / 'data'
    
    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        sys.exit(1)
    
    # Connect to database
    try:
        conn = psycopg2.connect(**db_config)
        conn.autocommit = False
        cursor = conn.cursor()
        print("Connected to database")
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)
    
    try:
        # Load each CSV file
        csv_files = {
            'BR_CUR.csv': ('BRENT', 'Brent Crude Oil', 'ICE'),
            'WTI_CUR.csv': ('WTI', 'West Texas Intermediate', 'NYMEX'),
            'GO_CUR.csv': ('GO', 'Gas Oil', 'ICE'),
            'RB_CUR.csv': ('RBOB', 'Reformulated Blendstock for Oxygenate Blending', 'NYMEX'),
        }
        
        for filename, (code, name, exchange) in csv_files.items():
            csv_path = data_dir / filename
            if csv_path.exists():
                load_csv_file(cursor, csv_path, code, name, exchange)
                conn.commit()
            else:
                print(f"Warning: File not found: {csv_path}")
        
        print("\n✓ Data loading complete!")
        
    except Exception as e:
        conn.rollback()
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()

