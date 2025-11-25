#!/usr/bin/env python3
"""
Query CFTC COT Loaded Data Status

CLI tool for querying what CFTC COT data has been loaded and processed from the CFTC website.
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import date, datetime, timedelta

# Add mcp-servers directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-servers" / "cftc-cot"))
from db import get_db


def format_date(d) -> str:
    """Format date or datetime as string."""
    if d is None:
        return "N/A"
    if isinstance(d, datetime):
        return d.date().isoformat()
    if isinstance(d, date):
        return d.isoformat()
    return str(d)


def print_summary(coverage: dict):
    """Print summary statistics."""
    print("=" * 60)
    print("CFTC COT Data Coverage Summary")
    print("=" * 60)
    print()
    print(f"Total Reports: {coverage['total_reports']}")
    print(f"Date Range: {format_date(coverage['earliest_date'])} to {format_date(coverage['latest_date'])}")
    print(f"Commodity Groups: {coverage['commodity_groups_count']}")
    if coverage['commodity_groups']:
        print(f"  - {coverage['commodity_groups']}")
    print(f"Markets: {coverage['markets_count']}")
    print()
    
    if coverage['loading_status_counts']:
        print("Loading Status:")
        for status, count in sorted(coverage['loading_status_counts'].items()):
            print(f"  {status}: {count}")
        print()
    
    if coverage['commodity_statistics']:
        print("Commodity Statistics:")
        for stat in coverage['commodity_statistics']:
            print(f"  {stat['commodity_group']}:")
            print(f"    Reports: {stat['report_count']}")
            print(f"    Date Range: {format_date(stat['earliest_date'])} to {format_date(stat['latest_date'])}")
        print()


def print_reports(reports: list, limit: int = None):
    """Print reports table."""
    if not reports:
        print("No reports found matching filters.")
        return
    
    if limit:
        reports = reports[:limit]
    
    print(f"Loaded Reports ({len(reports)} shown):")
    print()
    print(f"{'Date':<12} {'Type':<30} {'Format':<10} {'Markets':<10} {'Commodities'}")
    print("-" * 100)
    
    for report in reports:
        commodity_groups = report['commodity_groups'] or 'N/A'
        if len(commodity_groups) > 50:
            commodity_groups = commodity_groups[:47] + "..."
        print(
            f"{report['report_date']:<12} "
            f"{report['report_type']:<30} "
            f"{report['format']:<10} "
            f"{report['market_count']:<10} "
            f"{commodity_groups}"
        )


def print_loading_status(logs: list, limit: int = None):
    """Print loading status table."""
    if not logs:
        print("No loading log entries found matching filters.")
        return
    
    if limit:
        logs = logs[:limit]
    
    print(f"Loading Log Entries ({len(logs)} shown):")
    print()
    print(f"{'Date':<12} {'Type':<30} {'Status':<15} {'Records':<10} {'Started':<20} {'Error'}")
    print("-" * 120)
    
    for log in logs:
        error_msg = (log['error_message'] or '')[:30] if log['error_message'] else ''
        if len(error_msg) > 30:
            error_msg = error_msg[:27] + "..."
        started = log['started_at']
        if started:
            if isinstance(started, datetime):
                started = started.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(started, date):
                started = started.isoformat()
            else:
                started = str(started)
        else:
            started = 'N/A'
        print(
            f"{log['report_date']:<12} "
            f"{log['report_type']:<30} "
            f"{log['status']:<15} "
            f"{log['records_loaded'] or 0:<10} "
            f"{str(started):<20} "
            f"{error_msg}"
        )


def print_missing_reports(missing: list):
    """Print missing reports."""
    if not missing:
        print("No missing reports detected in the specified date range.")
        return
    
    print(f"Missing Reports ({len(missing)} gaps detected):")
    print()
    
    if len(missing) <= 50:
        for m in missing:
            print(f"  {m['report_date']}")
    else:
        print(f"  {missing[0]['report_date']} (first missing)")
        print(f"  ... {len(missing) - 2} more missing dates ...")
        print(f"  {missing[-1]['report_date']} (last missing)")
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Query CFTC COT loaded data status',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show summary statistics
  python query_cftc_loaded_data.py --summary
  
  # List all loaded reports
  python query_cftc_loaded_data.py --reports
  
  # Filter by commodity
  python query_cftc_loaded_data.py --commodity "Petroleum and Products"
  
  # Filter by date range
  python query_cftc_loaded_data.py --start-date 2025-01-01 --end-date 2025-03-31
  
  # Show failed loading attempts
  python query_cftc_loaded_data.py --status failed
  
  # Find missing reports
  python query_cftc_loaded_data.py --missing
  
  # JSON output
  python query_cftc_loaded_data.py --summary --json
        """
    )
    
    parser.add_argument('--summary', action='store_true', help='Show summary statistics')
    parser.add_argument('--reports', action='store_true', help='List loaded reports')
    parser.add_argument('--commodity', type=str, help='Filter by commodity group')
    parser.add_argument('--start-date', type=str, help='Start date filter (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date filter (YYYY-MM-DD)')
    parser.add_argument('--status', type=str, choices=['pending', 'downloading', 'parsing', 'loading', 'completed', 'failed'],
                       help='Filter by loading status')
    parser.add_argument('--missing', action='store_true', help='Identify missing reports')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--limit', type=int, default=50, help='Limit number of results shown (default: 50)')
    
    args = parser.parse_args()
    
    # If no specific action, default to summary
    if not any([args.summary, args.reports, args.status, args.missing]):
        args.summary = True
    
    try:
        db = get_db()
        
        # Parse dates
        start_date_obj = None
        end_date_obj = None
        
        if args.start_date:
            try:
                start_date_obj = datetime.strptime(args.start_date, '%Y-%m-%d').date()
            except ValueError:
                print(f"Error: Invalid start-date format '{args.start_date}'. Expected YYYY-MM-DD format.")
                sys.exit(1)
        
        if args.end_date:
            try:
                end_date_obj = datetime.strptime(args.end_date, '%Y-%m-%d').date()
            except ValueError:
                print(f"Error: Invalid end-date format '{args.end_date}'. Expected YYYY-MM-DD format.")
                sys.exit(1)
        
        # Collect results
        results = {}
        
        if args.summary:
            coverage = db.get_data_coverage()
            results['coverage'] = {
                'total_reports': coverage['total_reports'],
                'earliest_date': format_date(coverage['earliest_date']),
                'latest_date': format_date(coverage['latest_date']),
                'commodity_groups_count': coverage['commodity_groups_count'],
                'markets_count': coverage['markets_count'],
                'commodity_groups': coverage['commodity_groups'],
                'loading_status_counts': coverage['loading_status_counts'],
                'commodity_statistics': [
                    {
                        'commodity_group': s['commodity_group'],
                        'report_count': s['report_count'],
                        'earliest_date': format_date(s['earliest_date']),
                        'latest_date': format_date(s['latest_date'])
                    }
                    for s in coverage['commodity_statistics']
                ]
            }
            
            if not args.json:
                print_summary(coverage)
        
        if args.reports:
            reports = db.get_loaded_reports(
                commodity=args.commodity,
                start_date=start_date_obj,
                end_date=end_date_obj
            )
            results['reports'] = [
                {
                    'report_date': format_date(r['report_date']),
                    'report_type': r['report_type'],
                    'format': r['format'],
                    'source_url': r['source_url'],
                    'market_count': r['market_count'],
                    'commodity_group_count': r['commodity_group_count'],
                    'commodity_groups': r['commodity_groups']
                }
                for r in reports
            ]
            
            if not args.json:
                print()
                print_reports(reports, limit=args.limit)
                if len(reports) > args.limit:
                    print(f"\n... and {len(reports) - args.limit} more reports (use --limit to show more)")
        
        if args.status:
            logs = db.get_loading_status(
                status=args.status,
                start_date=start_date_obj,
                end_date=end_date_obj
            )
            results['loading_status'] = [
                {
                    'report_date': format_date(l['report_date']),
                    'report_type': l['report_type'],
                    'format': l['format'],
                    'status': l['status'],
                    'started_at': format_date(l['started_at']),
                    'completed_at': format_date(l['completed_at']),
                    'records_loaded': l['records_loaded'],
                    'error_message': l['error_message']
                }
                for l in logs
            ]
            
            if not args.json:
                print()
                print_loading_status(logs, limit=args.limit)
                if len(logs) > args.limit:
                    print(f"\n... and {len(logs) - args.limit} more entries (use --limit to show more)")
        
        if args.missing:
            missing = db.get_missing_reports(
                start_date=start_date_obj,
                end_date=end_date_obj
            )
            results['missing_reports'] = [
                {
                    'report_date': format_date(m['report_date']),
                    'status': m['status']
                }
                for m in missing
            ]
            
            if not args.json:
                print()
                print_missing_reports(missing)
        
        # Output JSON if requested
        if args.json:
            print(json.dumps(results, indent=2))
        
        db.close()
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

