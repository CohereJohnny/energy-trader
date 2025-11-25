"""
MCP tool implementations for CFTC COT data.
"""

from datetime import date, datetime
from typing import Dict, Any, List, Optional
from db import get_db
from citations import create_citation_metadata, format_cot_response


def get_cot_data(
    commodity: Optional[str] = None,
    report_date: Optional[str] = None,
    trader_category: Optional[str] = None,
    position_type: str = 'all'
) -> Dict[str, Any]:
    """
    Get CFTC Commitment of Traders (COT) data.
    
    Args:
        commodity: Commodity group (Petroleum and Products, Natural Gas and Products, Electricity)
        report_date: Report date in YYYY-MM-DD format (if None, returns latest)
        trader_category: Trader category (PRODUCER, SWAP, MANAGED_MONEY, OTHER_REPORTABLE, NONREPORTABLE)
        position_type: Position type ('all' for Futures+Options, 'old' for Futures only, 'other' for Options only)
        
    Returns:
        Formatted response with COT data and citation metadata
    """
    try:
        db = get_db()
        
        # Parse date if provided
        report_date_obj = None
        if report_date:
            try:
                report_date_obj = datetime.strptime(report_date, '%Y-%m-%d').date()
            except ValueError:
                return format_cot_response(
                    f"Error: Invalid date format '{report_date}'. Expected YYYY-MM-DD format.",
                    create_citation_metadata("CFTC COT Data Error")
                )
        
        # Validate trader category if provided
        valid_categories = ['PRODUCER', 'SWAP', 'MANAGED_MONEY', 'OTHER_REPORTABLE', 'NONREPORTABLE']
        if trader_category and trader_category.upper() not in valid_categories:
            return format_cot_response(
                f"Error: Invalid trader category '{trader_category}'. Valid options: {', '.join(valid_categories)}",
                create_citation_metadata("CFTC COT Data Error")
            )
        
        # Query database
        results = db.get_cot_data(
            commodity=commodity,
            report_date=report_date_obj,
            trader_category=trader_category.upper() if trader_category else None,
            position_type=position_type
        )
        
        if not results:
            date_str = report_date if report_date else "latest"
            return format_cot_response(
                f"No COT data found for commodity={commodity or 'all'}, date={date_str}, category={trader_category or 'all'}",
                create_citation_metadata("CFTC COT Data")
            )
        
        # Format response
        lines = []
        lines.append(f"CFTC Commitment of Traders Data")
        if report_date_obj:
            lines.append(f"Report Date: {report_date_obj}")
        else:
            lines.append(f"Report Date: {results[0]['report_date']} (latest)")
        lines.append("")
        
        # Group by market
        current_market = None
        for row in results:
            if current_market != row['market_name']:
                if current_market is not None:
                    lines.append("")
                current_market = row['market_name']
                lines.append(f"Market: {row['market_name']} ({row['cftc_code']})")
                lines.append(f"Exchange: {row['exchange']}")
                lines.append(f"Commodity Group: {row['commodity_group']}")
                if row['open_interest']:
                    lines.append(f"Open Interest: {row['open_interest']:,}")
                lines.append("")
            
            lines.append(f"  {row['category_name']}:")
            if row['long_positions'] is not None:
                lines.append(f"    Long: {row['long_positions']:,}")
            if row['short_positions'] is not None:
                lines.append(f"    Short: {row['short_positions']:,}")
            if row['spreading_positions'] is not None:
                lines.append(f"    Spreading: {row['spreading_positions']:,}")
            if row['pct_long'] is not None:
                lines.append(f"    % Long: {row['pct_long']:.2f}%")
            if row['pct_short'] is not None:
                lines.append(f"    % Short: {row['pct_short']:.2f}%")
            if row['change_long'] is not None or row['change_short'] is not None:
                changes = []
                if row['change_long'] is not None:
                    changes.append(f"Long: {row['change_long']:+,}")
                if row['change_short'] is not None:
                    changes.append(f"Short: {row['change_short']:+,}")
                if changes:
                    lines.append(f"    Changes: {', '.join(changes)}")
            lines.append("")
        
        text = "\n".join(lines)
        
        return format_cot_response(
            text,
            create_citation_metadata(
                f"CFTC COT Data - {results[0]['report_date']}",
                "https://www.cftc.gov/dea/futures/petroleum_lf.htm"
            )
        )
        
    except Exception as e:
        return format_cot_response(
            f"Error retrieving COT data: {str(e)}",
            create_citation_metadata("CFTC COT Data Error")
        )


def analyze_positioning_trends(
    commodity: str,
    start_date: str,
    end_date: str,
    trader_category: str
) -> Dict[str, Any]:
    """
    Analyze positioning trends for a commodity and trader category over time.
    
    Args:
        commodity: Commodity group (Petroleum and Products, Natural Gas and Products, Electricity)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        trader_category: Trader category (PRODUCER, SWAP, MANAGED_MONEY, OTHER_REPORTABLE, NONREPORTABLE)
        
    Returns:
        Formatted response with trend analysis and citation metadata
    """
    try:
        # Parse dates
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError as e:
            return format_cot_response(
                f"Error: Invalid date format. Expected YYYY-MM-DD format. {str(e)}",
                create_citation_metadata("CFTC COT Data Error")
            )
        
        if start_date_obj > end_date_obj:
            return format_cot_response(
                "Error: Start date must be before end date.",
                create_citation_metadata("CFTC COT Data Error")
            )
        
        # Validate trader category
        valid_categories = ['PRODUCER', 'SWAP', 'MANAGED_MONEY', 'OTHER_REPORTABLE', 'NONREPORTABLE']
        if trader_category.upper() not in valid_categories:
            return format_cot_response(
                f"Error: Invalid trader category '{trader_category}'. Valid options: {', '.join(valid_categories)}",
                create_citation_metadata("CFTC COT Data Error")
            )
        
        # Query database
        db = get_db()
        results = db.analyze_positioning_trends(
            commodity=commodity,
            start_date=start_date_obj,
            end_date=end_date_obj,
            trader_category=trader_category.upper()
        )
        
        if not results:
            return format_cot_response(
                f"No positioning data found for {commodity}, {trader_category} from {start_date} to {end_date}",
                create_citation_metadata("CFTC COT Data")
            )
        
        # Analyze trends
        lines = []
        lines.append(f"Positioning Trends Analysis")
        lines.append(f"Commodity: {commodity}")
        lines.append(f"Trader Category: {results[0]['category_name']}")
        lines.append(f"Period: {start_date} to {end_date}")
        lines.append("")
        
        # Group by market
        markets = {}
        for row in results:
            market_name = row['market_name']
            if market_name not in markets:
                markets[market_name] = []
            markets[market_name].append(row)
        
        for market_name, market_data in markets.items():
            lines.append(f"Market: {market_name} ({market_data[0]['cftc_code']})")
            lines.append("")
            
            # Calculate changes
            first = market_data[0]
            last = market_data[-1]
            
            if first['long_positions'] is not None and last['long_positions'] is not None:
                long_change = last['long_positions'] - first['long_positions']
                long_pct_change = (long_change / first['long_positions'] * 100) if first['long_positions'] > 0 else 0
                lines.append(f"  Long Positions:")
                lines.append(f"    Start: {first['long_positions']:,} ({start_date})")
                lines.append(f"    End: {last['long_positions']:,} ({end_date})")
                lines.append(f"    Change: {long_change:+,} ({long_pct_change:+.2f}%)")
                lines.append("")
            
            if first['short_positions'] is not None and last['short_positions'] is not None:
                short_change = last['short_positions'] - first['short_positions']
                short_pct_change = (short_change / first['short_positions'] * 100) if first['short_positions'] > 0 else 0
                lines.append(f"  Short Positions:")
                lines.append(f"    Start: {first['short_positions']:,} ({start_date})")
                lines.append(f"    End: {last['short_positions']:,} ({end_date})")
                lines.append(f"    Change: {short_change:+,} ({short_pct_change:+.2f}%)")
                lines.append("")
            
            if first['pct_long'] is not None and last['pct_long'] is not None:
                pct_change = last['pct_long'] - first['pct_long']
                lines.append(f"  % of Open Interest (Long):")
                lines.append(f"    Start: {first['pct_long']:.2f}%")
                lines.append(f"    End: {last['pct_long']:.2f}%")
                lines.append(f"    Change: {pct_change:+.2f}%")
                lines.append("")
        
        text = "\n".join(lines)
        
        return format_cot_response(
            text,
            create_citation_metadata(
                f"CFTC COT Positioning Trends - {commodity}",
                "https://www.cftc.gov/dea/futures/petroleum_lf.htm"
            )
        )
        
    except Exception as e:
        return format_cot_response(
            f"Error analyzing positioning trends: {str(e)}",
            create_citation_metadata("CFTC COT Data Error")
        )


def compare_positioning(
    commodities: str,
    report_date: str,
    trader_category: str
) -> Dict[str, Any]:
    """
    Compare positioning across multiple commodities on a given date.
    
    Args:
        commodities: Comma-separated list of commodity groups
        report_date: Report date in YYYY-MM-DD format
        trader_category: Trader category (PRODUCER, SWAP, MANAGED_MONEY, OTHER_REPORTABLE, NONREPORTABLE)
        
    Returns:
        Formatted response with comparison data and citation metadata
    """
    try:
        # Parse date
        try:
            report_date_obj = datetime.strptime(report_date, '%Y-%m-%d').date()
        except ValueError:
            return format_cot_response(
                f"Error: Invalid date format '{report_date}'. Expected YYYY-MM-DD format.",
                create_citation_metadata("CFTC COT Data Error")
            )
        
        # Parse commodities
        commodity_list = [c.strip() for c in commodities.split(',')]
        
        # Validate trader category
        valid_categories = ['PRODUCER', 'SWAP', 'MANAGED_MONEY', 'OTHER_REPORTABLE', 'NONREPORTABLE']
        if trader_category.upper() not in valid_categories:
            return format_cot_response(
                f"Error: Invalid trader category '{trader_category}'. Valid options: {', '.join(valid_categories)}",
                create_citation_metadata("CFTC COT Data Error")
            )
        
        # Query database
        db = get_db()
        results = db.compare_positioning(
            commodities=commodity_list,
            report_date=report_date_obj,
            trader_category=trader_category.upper()
        )
        
        if not results:
            return format_cot_response(
                f"No positioning data found for commodities={commodities}, date={report_date}, category={trader_category}",
                create_citation_metadata("CFTC COT Data")
            )
        
        # Format comparison
        lines = []
        lines.append(f"Positioning Comparison")
        lines.append(f"Report Date: {report_date}")
        lines.append(f"Trader Category: {results[0]['category_name']}")
        lines.append(f"Commodities: {', '.join(commodity_list)}")
        lines.append("")
        lines.append(f"{'Commodity':<30} {'Market':<40} {'Long':>12} {'Short':>12} {'% Long':>10} {'% Short':>10}")
        lines.append("-" * 120)
        
        for row in results:
            market_name = row['market_name'][:38]  # Truncate if too long
            long_str = f"{row['long_positions']:,}" if row['long_positions'] is not None else "N/A"
            short_str = f"{row['short_positions']:,}" if row['short_positions'] is not None else "N/A"
            pct_long_str = f"{row['pct_long']:.2f}%" if row['pct_long'] is not None else "N/A"
            pct_short_str = f"{row['pct_short']:.2f}%" if row['pct_short'] is not None else "N/A"
            
            lines.append(f"{row['commodity_group']:<30} {market_name:<40} {long_str:>12} {short_str:>12} {pct_long_str:>10} {pct_short_str:>10}")
        
        text = "\n".join(lines)
        
        return format_cot_response(
            text,
            create_citation_metadata(
                f"CFTC COT Positioning Comparison - {report_date}",
                "https://www.cftc.gov/dea/futures/petroleum_lf.htm"
            )
        )
        
    except Exception as e:
        return format_cot_response(
            f"Error comparing positioning: {str(e)}",
            create_citation_metadata("CFTC COT Data Error")
        )


def get_positioning_extremes(
    commodity: str,
    trader_category: str,
    lookback_days: int = 365,
    metric: str = 'long'
) -> Dict[str, Any]:
    """
    Get positioning extremes for a commodity and trader category.
    
    Args:
        commodity: Commodity group (Petroleum and Products, Natural Gas and Products, Electricity)
        trader_category: Trader category (PRODUCER, SWAP, MANAGED_MONEY, OTHER_REPORTABLE, NONREPORTABLE)
        lookback_days: Number of days to look back (default: 365)
        metric: Metric to find extremes for ('long', 'short', 'net', 'pct_long', 'pct_short')
        
    Returns:
        Formatted response with extreme positioning data and citation metadata
    """
    try:
        # Validate trader category
        valid_categories = ['PRODUCER', 'SWAP', 'MANAGED_MONEY', 'OTHER_REPORTABLE', 'NONREPORTABLE']
        if trader_category.upper() not in valid_categories:
            return format_cot_response(
                f"Error: Invalid trader category '{trader_category}'. Valid options: {', '.join(valid_categories)}",
                create_citation_metadata("CFTC COT Data Error")
            )
        
        # Validate metric
        valid_metrics = ['long', 'short', 'net', 'pct_long', 'pct_short']
        if metric.lower() not in valid_metrics:
            return format_cot_response(
                f"Error: Invalid metric '{metric}'. Valid options: {', '.join(valid_metrics)}",
                create_citation_metadata("CFTC COT Data Error")
            )
        
        # Query database
        db = get_db()
        results = db.get_positioning_extremes(
            commodity=commodity,
            trader_category=trader_category.upper(),
            lookback_days=lookback_days,
            metric=metric.lower()
        )
        
        if not results:
            return format_cot_response(
                f"No positioning extremes found for {commodity}, {trader_category} over the past {lookback_days} days",
                create_citation_metadata("CFTC COT Data")
            )
        
        # Format extremes
        lines = []
        lines.append(f"Positioning Extremes")
        lines.append(f"Commodity: {commodity}")
        lines.append(f"Trader Category: {results[0]['category_name']}")
        lines.append(f"Metric: {metric.upper()}")
        lines.append(f"Lookback Period: {lookback_days} days")
        lines.append("")
        lines.append("Top 10 Extreme Positions:")
        lines.append("")
        
        for i, row in enumerate(results, 1):
            lines.append(f"{i}. {row['market_name']} ({row['cftc_code']})")
            lines.append(f"   Date: {row['report_date']}")
            if row['long_positions'] is not None:
                lines.append(f"   Long: {row['long_positions']:,}")
            if row['short_positions'] is not None:
                lines.append(f"   Short: {row['short_positions']:,}")
            if row['pct_long'] is not None:
                lines.append(f"   % Long: {row['pct_long']:.2f}%")
            if row['pct_short'] is not None:
                lines.append(f"   % Short: {row['pct_short']:.2f}%")
            if 'metric_value' in row and row['metric_value'] is not None:
                lines.append(f"   {metric.upper()} Value: {row['metric_value']:,}" if isinstance(row['metric_value'], (int, float)) and row['metric_value'] < 1000 else f"   {metric.upper()} Value: {row['metric_value']:.2f}")
            lines.append("")
        
        text = "\n".join(lines)
        
        return format_cot_response(
            text,
            create_citation_metadata(
                f"CFTC COT Positioning Extremes - {commodity}",
                "https://www.cftc.gov/dea/futures/petroleum_lf.htm"
            )
        )
        
    except Exception as e:
        return format_cot_response(
            f"Error retrieving positioning extremes: {str(e)}",
            create_citation_metadata("CFTC COT Data Error")
        )


def get_loaded_data_status(
    commodity: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    identify_gaps: bool = False
) -> Dict[str, Any]:
    """
    Get status of loaded CFTC COT data.
    
    Args:
        commodity: Commodity group filter (optional)
        start_date: Start date filter in YYYY-MM-DD format (optional)
        end_date: End date filter in YYYY-MM-DD format (optional)
        status: Loading status filter ('pending', 'downloading', 'parsing', 'loading', 'completed', 'failed') (optional)
        identify_gaps: Whether to identify missing reports (default: False)
        
    Returns:
        Formatted response with loaded data status and citation metadata
    """
    try:
        db = get_db()
        
        # Parse dates if provided
        start_date_obj = None
        end_date_obj = None
        
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                return format_cot_response(
                    f"Error: Invalid start_date format '{start_date}'. Expected YYYY-MM-DD format.",
                    create_citation_metadata("CFTC COT Data Status Error")
                )
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return format_cot_response(
                    f"Error: Invalid end_date format '{end_date}'. Expected YYYY-MM-DD format.",
                    create_citation_metadata("CFTC COT Data Status Error")
                )
        
        lines = []
        lines.append("CFTC COT Loaded Data Status")
        lines.append("=" * 50)
        lines.append("")
        
        # Get coverage statistics
        coverage = db.get_data_coverage()
        
        if coverage['total_reports'] == 0:
            return format_cot_response(
                "No CFTC COT data has been loaded into the database yet.",
                create_citation_metadata("CFTC COT Data Status")
            )
        
        # Overall summary
        lines.append("Overall Coverage:")
        lines.append(f"  Total Reports: {coverage['total_reports']}")
        if coverage['earliest_date']:
            lines.append(f"  Earliest Date: {coverage['earliest_date']}")
        if coverage['latest_date']:
            lines.append(f"  Latest Date: {coverage['latest_date']}")
        lines.append(f"  Commodity Groups: {coverage['commodity_groups_count']}")
        if coverage['commodity_groups']:
            lines.append(f"    - {coverage['commodity_groups']}")
        lines.append(f"  Markets: {coverage['markets_count']}")
        lines.append("")
        
        # Loading status counts
        if coverage['loading_status_counts']:
            lines.append("Loading Status:")
            for status, count in sorted(coverage['loading_status_counts'].items()):
                lines.append(f"  {status}: {count}")
            lines.append("")
        
        # Commodity-specific statistics
        if coverage['commodity_statistics']:
            lines.append("Commodity Statistics:")
            for stat in coverage['commodity_statistics']:
                lines.append(f"  {stat['commodity_group']}:")
                lines.append(f"    Reports: {stat['report_count']}")
                if stat['earliest_date']:
                    lines.append(f"    Date Range: {stat['earliest_date']} to {stat['latest_date']}")
            lines.append("")
        
        # Get loaded reports with filters
        reports = db.get_loaded_reports(
            commodity=commodity,
            start_date=start_date_obj,
            end_date=end_date_obj
        )
        
        if commodity or start_date_obj or end_date_obj:
            lines.append(f"Filtered Reports ({len(reports)} found):")
            if reports:
                lines.append(f"{'Date':<12} {'Type':<30} {'Format':<10} {'Markets':<10} {'Commodities'}")
                lines.append("-" * 100)
                for report in reports[:50]:  # Limit to first 50 for readability
                    commodity_groups = report['commodity_groups'] or 'N/A'
                    if len(commodity_groups) > 30:
                        commodity_groups = commodity_groups[:27] + "..."
                    lines.append(
                        f"{report['report_date']:<12} "
                        f"{report['report_type']:<30} "
                        f"{report['format']:<10} "
                        f"{report['market_count']:<10} "
                        f"{commodity_groups}"
                    )
                if len(reports) > 50:
                    lines.append(f"... and {len(reports) - 50} more reports")
            else:
                lines.append("  No reports found matching filters.")
            lines.append("")
        
        # Get loading status if requested
        if status:
            loading_logs = db.get_loading_status(
                status=status,
                start_date=start_date_obj,
                end_date=end_date_obj
            )
            lines.append(f"Loading Log Entries (status={status}):")
            if loading_logs:
                lines.append(f"{'Date':<12} {'Type':<30} {'Status':<15} {'Records':<10} {'Error'}")
                lines.append("-" * 100)
                for log in loading_logs[:50]:  # Limit to first 50
                    error_msg = (log['error_message'] or '')[:30] if log['error_message'] else ''
                    if len(error_msg) > 30:
                        error_msg = error_msg[:27] + "..."
                    lines.append(
                        f"{log['report_date']:<12} "
                        f"{log['report_type']:<30} "
                        f"{log['status']:<15} "
                        f"{log['records_loaded'] or 0:<10} "
                        f"{error_msg}"
                    )
                if len(loading_logs) > 50:
                    lines.append(f"... and {len(loading_logs) - 50} more entries")
            else:
                lines.append("  No loading log entries found matching filters.")
            lines.append("")
        
        # Identify missing reports if requested
        if identify_gaps:
            missing = db.get_missing_reports(
                start_date=start_date_obj,
                end_date=end_date_obj
            )
            if missing:
                lines.append(f"Missing Reports ({len(missing)} gaps detected):")
                # Group consecutive missing dates
                if len(missing) <= 20:
                    for m in missing:
                        lines.append(f"  {m['report_date']}")
                else:
                    lines.append(f"  {missing[0]['report_date']} (first missing)")
                    lines.append(f"  ... {len(missing) - 2} more missing dates ...")
                    lines.append(f"  {missing[-1]['report_date']} (last missing)")
                lines.append("")
            else:
                lines.append("No missing reports detected in the specified date range.")
                lines.append("")
        
        text = "\n".join(lines)
        
        return format_cot_response(
            text,
            create_citation_metadata(
                "CFTC COT Loaded Data Status",
                "https://www.cftc.gov/dea/futures/petroleum_lf.htm"
            )
        )
        
    except Exception as e:
        return format_cot_response(
            f"Error retrieving loaded data status: {str(e)}",
            create_citation_metadata("CFTC COT Data Status Error")
        )

