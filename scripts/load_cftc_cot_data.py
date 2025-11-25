#!/usr/bin/env python3
"""
Load CFTC Disaggregated COT Data into PostgreSQL

This script:
1. Downloads CFTC disaggregated reports (petroleum, natural gas, electricity)
2. Parses the HTML data using cftc_parser
3. Loads parsed data into PostgreSQL database
"""

import sys
import os
from pathlib import Path
from datetime import date, datetime
import psycopg2
from psycopg2.extras import execute_batch, RealDictCursor
import requests
from bs4 import BeautifulSoup

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))
from cftc_parser import CFTCDisaggregatedParser, CommodityData


# CFTC report URLs for target commodity groups
CFTC_REPORTS = {
    'petroleum': 'https://www.cftc.gov/dea/futures/petroleum_lf.htm',
    'natural_gas': 'https://www.cftc.gov/dea/futures/nat_gas_lf.htm',
    'electricity': 'https://www.cftc.gov/dea/futures/electricity_lf.htm',
}


def get_or_create_market(cursor, market_name: str, exchange: str, cftc_code: str, commodity_group: str) -> int:
    """Get or create market record."""
    cursor.execute("""
        INSERT INTO cftc_cot.markets (cftc_code, market_name, exchange, commodity_group)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (cftc_code) DO UPDATE
        SET market_name = EXCLUDED.market_name,
            exchange = EXCLUDED.exchange,
            commodity_group = EXCLUDED.commodity_group,
            updated_at = NOW()
        RETURNING id
    """, (cftc_code, market_name, exchange, commodity_group))
    return cursor.fetchone()[0]


def get_category_id(cursor, category_code: str) -> int:
    """Get trader category ID."""
    cursor.execute("SELECT id FROM cftc_cot.trader_categories WHERE category_code = %s", (category_code,))
    result = cursor.fetchone()
    if result:
        return result[0]
    raise ValueError(f"Category not found: {category_code}")


def get_or_create_report(cursor, report_date: date, report_type: str, format: str, source_url: str = None) -> int:
    """Get or create report record."""
    cursor.execute("""
        INSERT INTO cftc_cot.reports (report_date, report_type, format, source_url)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (report_date, report_type, format) DO UPDATE
        SET source_url = EXCLUDED.source_url,
            updated_at = NOW()
        RETURNING id
    """, (report_date, report_type, format, source_url))
    return cursor.fetchone()[0]


def load_commodity_data(cursor, report_id: int, commodity: CommodityData, commodity_group: str):
    """Load a single commodity's data into database."""
    if not commodity.cftc_code or not commodity.open_interest:
        return  # Skip if missing required data
    
    # Get or create market
    market_id = get_or_create_market(
        cursor,
        commodity.market_name,
        commodity.exchange,
        commodity.cftc_code,
        commodity_group
    )
    
    # Load Open Interest
    for position_type in ['all', 'old', 'other']:
        positions = getattr(commodity, f'positions_{position_type}', None)
        if positions:
            cursor.execute("""
                INSERT INTO cftc_cot.open_interest (report_id, market_id, position_type, open_interest)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (report_id, market_id, position_type) DO UPDATE
                SET open_interest = EXCLUDED.open_interest
            """, (report_id, market_id, position_type, commodity.open_interest))
    
    # Load positions
    category_mapping = {
        'PRODUCER': 'producer',
        'SWAP': 'swap',
        'MANAGED_MONEY': 'managed_money',
        'OTHER_REPORTABLE': 'other',
        'NONREPORTABLE': 'nonreportable'
    }
    
    for position_type in ['all', 'old', 'other']:
        positions = getattr(commodity, f'positions_{position_type}', None)
        if not positions:
            continue
        
        # Producer/Merchant
        if positions.producer_long is not None or positions.producer_short is not None:
            category_id = get_category_id(cursor, 'PRODUCER')
            cursor.execute("""
                INSERT INTO cftc_cot.positions (report_id, market_id, category_id, position_type, long_positions, short_positions)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (report_id, market_id, category_id, position_type) DO UPDATE
                SET long_positions = EXCLUDED.long_positions,
                    short_positions = EXCLUDED.short_positions,
                    updated_at = NOW()
            """, (report_id, market_id, category_id, position_type, positions.producer_long, positions.producer_short))
        
        # Swap Dealers
        if positions.swap_long is not None or positions.swap_short is not None or positions.swap_spreading is not None:
            category_id = get_category_id(cursor, 'SWAP')
            cursor.execute("""
                INSERT INTO cftc_cot.positions (report_id, market_id, category_id, position_type, long_positions, short_positions, spreading_positions)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (report_id, market_id, category_id, position_type) DO UPDATE
                SET long_positions = EXCLUDED.long_positions,
                    short_positions = EXCLUDED.short_positions,
                    spreading_positions = EXCLUDED.spreading_positions,
                    updated_at = NOW()
            """, (report_id, market_id, category_id, position_type, positions.swap_long, positions.swap_short, positions.swap_spreading))
        
        # Managed Money
        if positions.managed_money_long is not None or positions.managed_money_short is not None or positions.managed_money_spreading is not None:
            category_id = get_category_id(cursor, 'MANAGED_MONEY')
            cursor.execute("""
                INSERT INTO cftc_cot.positions (report_id, market_id, category_id, position_type, long_positions, short_positions, spreading_positions)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (report_id, market_id, category_id, position_type) DO UPDATE
                SET long_positions = EXCLUDED.long_positions,
                    short_positions = EXCLUDED.short_positions,
                    spreading_positions = EXCLUDED.spreading_positions,
                    updated_at = NOW()
            """, (report_id, market_id, category_id, position_type, positions.managed_money_long, positions.managed_money_short, positions.managed_money_spreading))
        
        # Other Reportables
        if positions.other_long is not None or positions.other_short is not None or positions.other_spreading is not None:
            category_id = get_category_id(cursor, 'OTHER_REPORTABLE')
            cursor.execute("""
                INSERT INTO cftc_cot.positions (report_id, market_id, category_id, position_type, long_positions, short_positions, spreading_positions)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (report_id, market_id, category_id, position_type) DO UPDATE
                SET long_positions = EXCLUDED.long_positions,
                    short_positions = EXCLUDED.short_positions,
                    spreading_positions = EXCLUDED.spreading_positions,
                    updated_at = NOW()
            """, (report_id, market_id, category_id, position_type, positions.other_long, positions.other_short, positions.other_spreading))
        
        # Nonreportable
        if positions.nonreportable_long is not None or positions.nonreportable_short is not None:
            category_id = get_category_id(cursor, 'NONREPORTABLE')
            cursor.execute("""
                INSERT INTO cftc_cot.positions (report_id, market_id, category_id, position_type, long_positions, short_positions)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (report_id, market_id, category_id, position_type) DO UPDATE
                SET long_positions = EXCLUDED.long_positions,
                    short_positions = EXCLUDED.short_positions,
                    updated_at = NOW()
            """, (report_id, market_id, category_id, position_type, positions.nonreportable_long, positions.nonreportable_short))
    
    # Load changes
    if commodity.changes:
        ch = commodity.changes
        # Changes use same structure - map accordingly
        if ch.producer_long is not None:  # This is actually change in Open Interest
            # Load changes for each category
            for category_code, attr_prefix in [('PRODUCER', 'producer'), ('SWAP', 'swap'), ('MANAGED_MONEY', 'managed_money'), ('OTHER_REPORTABLE', 'other')]:
                category_id = get_category_id(cursor, category_code)
                long_attr = f'{attr_prefix}_long'
                short_attr = f'{attr_prefix}_short'
                spread_attr = f'{attr_prefix}_spreading'
                
                change_long = getattr(ch, long_attr, None)
                change_short = getattr(ch, short_attr, None)
                change_spread = getattr(ch, spread_attr, None) if hasattr(ch, spread_attr) else None
                
                if change_long is not None or change_short is not None:
                    cursor.execute("""
                        INSERT INTO cftc_cot.changes (report_id, market_id, category_id, change_open_interest, change_long, change_short, change_spreading)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (report_id, market_id, category_id) DO UPDATE
                        SET change_open_interest = EXCLUDED.change_open_interest,
                            change_long = EXCLUDED.change_long,
                            change_short = EXCLUDED.change_short,
                            change_spreading = EXCLUDED.change_spreading
                    """, (report_id, market_id, category_id, ch.producer_long if category_code == 'PRODUCER' else None, change_long, change_short, change_spread))
    
    # Load percentages
    if commodity.percentages_all:
        pct = commodity.percentages_all
        for position_type in ['all', 'old', 'other']:
            pct_data = getattr(commodity, f'percentages_{position_type}', None) or pct if position_type == 'all' else None
            if not pct_data:
                continue
            
            # Load percentages for each category
            for category_code, attr_prefix in [('PRODUCER', 'producer'), ('SWAP', 'swap'), ('MANAGED_MONEY', 'managed_money'), ('OTHER_REPORTABLE', 'other'), ('NONREPORTABLE', 'nonreportable')]:
                category_id = get_category_id(cursor, category_code)
                long_attr = f'{attr_prefix}_long'
                short_attr = f'{attr_prefix}_short'
                spread_attr = f'{attr_prefix}_spreading' if category_code != 'NONREPORTABLE' else None
                
                pct_long = getattr(pct_data, long_attr, None)
                pct_short = getattr(pct_data, short_attr, None)
                pct_spread = getattr(pct_data, spread_attr, None) if spread_attr else None
                
                if pct_long is not None or pct_short is not None:
                    cursor.execute("""
                        INSERT INTO cftc_cot.percentages (report_id, market_id, category_id, position_type, pct_long, pct_short, pct_spreading)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (report_id, market_id, category_id, position_type) DO UPDATE
                        SET pct_long = EXCLUDED.pct_long,
                            pct_short = EXCLUDED.pct_short,
                            pct_spreading = EXCLUDED.pct_spreading
                    """, (report_id, market_id, category_id, position_type, pct_long, pct_short, pct_spread))
    
    # Load trader counts
    if commodity.trader_counts_all:
        tc = commodity.trader_counts_all
        for position_type in ['all', 'old', 'other']:
            tc_data = getattr(commodity, f'trader_counts_{position_type}', None) or tc if position_type == 'all' else None
            if not tc_data:
                continue
            
            # Load trader counts for each category
            for category_code, attr_prefix in [('PRODUCER', 'producer'), ('SWAP', 'swap'), ('MANAGED_MONEY', 'managed_money'), ('OTHER_REPORTABLE', 'other')]:
                category_id = get_category_id(cursor, category_code)
                long_attr = f'{attr_prefix}_long'
                short_attr = f'{attr_prefix}_short'
                spread_attr = f'{attr_prefix}_spreading'
                
                num_long = getattr(tc_data, long_attr, None)
                num_short = getattr(tc_data, short_attr, None)
                num_spread = getattr(tc_data, spread_attr, None)
                
                if num_long is not None or num_short is not None:
                    cursor.execute("""
                        INSERT INTO cftc_cot.trader_counts (report_id, market_id, category_id, position_type, num_traders_long, num_traders_short, num_traders_spreading)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (report_id, market_id, category_id, position_type) DO UPDATE
                        SET num_traders_long = EXCLUDED.num_traders_long,
                            num_traders_short = EXCLUDED.num_traders_short,
                            num_traders_spreading = EXCLUDED.num_traders_spreading
                    """, (report_id, market_id, category_id, position_type, num_long, num_short, num_spread))
    
    # Load concentration
    if commodity.concentration_gross_4_long is not None:
        for position_type in ['all', 'old', 'other']:
            # Only 'all' has concentration data typically
            if position_type == 'all':
                cursor.execute("""
                    INSERT INTO cftc_cot.concentration (
                        report_id, market_id, position_type,
                        gross_4_long, gross_4_short, gross_8_long, gross_8_short,
                        net_4_long, net_4_short, net_8_long, net_8_short
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (report_id, market_id, position_type) DO UPDATE
                    SET gross_4_long = EXCLUDED.gross_4_long,
                        gross_4_short = EXCLUDED.gross_4_short,
                        gross_8_long = EXCLUDED.gross_8_long,
                        gross_8_short = EXCLUDED.gross_8_short,
                        net_4_long = EXCLUDED.net_4_long,
                        net_4_short = EXCLUDED.net_4_short,
                        net_8_long = EXCLUDED.net_8_long,
                        net_8_short = EXCLUDED.net_8_short
                """, (
                    report_id, market_id, position_type,
                    commodity.concentration_gross_4_long,
                    commodity.concentration_gross_4_short,
                    commodity.concentration_gross_8_long,
                    commodity.concentration_gross_8_short,
                    commodity.concentration_net_4_long,
                    commodity.concentration_net_4_short,
                    commodity.concentration_net_8_long,
                    commodity.concentration_net_8_short
                ))


def download_report(url: str) -> str:
    """Download CFTC report HTML."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise Exception(f"Failed to download report from {url}: {e}")


def load_report(report_name: str, commodity_group: str, db_cursor, dry_run: bool = False):
    """Load a single CFTC report."""
    url = CFTC_REPORTS.get(report_name)
    if not url:
        print(f"⚠️  Unknown report: {report_name}")
        return
    
    print(f"\n{'='*80}")
    print(f"Loading {report_name.upper()} report")
    print(f"{'='*80}")
    print(f"URL: {url}")
    
    if dry_run:
        print("  [DRY RUN] Would download and parse report")
        return
    
    # Download report
    print("  Downloading report...")
    try:
        html = download_report(url)
        print(f"  ✓ Downloaded ({len(html)} bytes)")
    except Exception as e:
        print(f"  ✗ Download failed: {e}")
        return
    
    # Parse report
    print("  Parsing report...")
    parser = CFTCDisaggregatedParser(strict=False)
    commodities = parser.parse(html)
    
    if parser.errors:
        print(f"  ⚠️  {len(parser.errors)} parsing errors (non-critical)")
    
    print(f"  ✓ Parsed {len(commodities)} commodities")
    
    if not commodities:
        print("  ⚠️  No commodities parsed")
        return
    
    # Get report date from first commodity
    report_date = commodities[0].report_date
    if not report_date:
        print("  ✗ Could not determine report date")
        return
    
    # Create report record
    report_id = get_or_create_report(
        db_cursor,
        report_date,
        'disaggregated_futures_options',
        'long',
        url
    )
    
    # Load each commodity
    records_loaded = 0
    for commodity in commodities:
        try:
            load_commodity_data(db_cursor, report_id, commodity, commodity_group)
            records_loaded += 1
        except Exception as e:
            print(f"  ✗ Error loading {commodity.market_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"  ✓ Loaded {records_loaded} commodities")
    
    return records_loaded


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Load CFTC COT data into PostgreSQL')
    parser.add_argument('--report', choices=['petroleum', 'natural_gas', 'electricity', 'all'],
                       default='petroleum', help='Report to load')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no database writes)')
    
    args = parser.parse_args()
    
    # Database connection
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'energy_trader'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        conn.autocommit = False
        cursor = conn.cursor()
        print("✓ Connected to database")
    except psycopg2.Error as e:
        print(f"✗ Error connecting to database: {e}")
        sys.exit(1)
    
    try:
        reports_to_load = []
        if args.report == 'all':
            reports_to_load = [
                ('petroleum', 'Petroleum and Products'),
                ('natural_gas', 'Natural Gas and Products'),
                ('electricity', 'Electricity')
            ]
        else:
            commodity_groups = {
                'petroleum': 'Petroleum and Products',
                'natural_gas': 'Natural Gas and Products',
                'electricity': 'Electricity'
            }
            reports_to_load = [(args.report, commodity_groups[args.report])]
        
        total_loaded = 0
        for report_name, commodity_group in reports_to_load:
            loaded = load_report(report_name, commodity_group, cursor, dry_run=args.dry_run)
            if loaded:
                total_loaded += loaded
        
        if not args.dry_run:
            conn.commit()
            print(f"\n✓ Successfully loaded {total_loaded} commodities")
        else:
            print(f"\n[DRY RUN] Would load {total_loaded} commodities")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()

