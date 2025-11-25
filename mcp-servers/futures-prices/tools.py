"""
MCP tool implementations for futures prices.
"""

from datetime import date, datetime
from typing import Dict, Any, List, Optional
from db import get_db
from citations import create_citation_metadata, format_price_response


def get_front_month_price(commodity: str, trade_date: str) -> Dict[str, Any]:
    """
    Get front month settlement price for a commodity on a specific date.
    
    Args:
        commodity: Commodity code (BRENT, WTI, GO, RBOB)
        trade_date: Date in YYYY-MM-DD format
        
    Returns:
        Formatted response with price data and citation metadata
    """
    try:
        # Parse date
        trade_date_obj = datetime.strptime(trade_date, '%Y-%m-%d').date()
        
        # Validate commodity
        valid_commodities = ['BRENT', 'WTI', 'GO', 'RBOB']
        commodity_upper = commodity.upper()
        if commodity_upper not in valid_commodities:
            return format_price_response(
                f"Error: Invalid commodity '{commodity}'. Valid options: {', '.join(valid_commodities)}",
                create_citation_metadata("Futures Prices Error")
            )
        
        # Query database
        db = get_db()
        result = db.get_front_month_price(commodity_upper, trade_date_obj)
        
        if not result:
            return format_price_response(
                f"No front month price found for {commodity_upper} on {trade_date}",
                create_citation_metadata(f"{commodity_upper} Front Month Price")
            )
        
        # Format response
        price = result['settlement_price']
        expiration = result['expiration_date']
        contract_info = f"{result['expiration_year']}-{result['expiration_month']:02d}"
        
        text = (
            f"Front month {commodity_upper} settlement price on {trade_date}: ${price:.2f}\n"
            f"Contract: {contract_info} (expires {expiration})"
        )
        
        return format_price_response(
            text,
            create_citation_metadata(
                f"{commodity_upper} Front Month Price - {trade_date}",
                f"https://energy-trader.local/futures-prices/{commodity_upper.lower()}/{trade_date}"
            )
        )
        
    except ValueError as e:
        return format_price_response(
            f"Error: Invalid date format '{trade_date}'. Expected YYYY-MM-DD format.",
            create_citation_metadata("Futures Prices Error")
        )
    except Exception as e:
        return format_price_response(
            f"Error retrieving price: {str(e)}",
            create_citation_metadata("Futures Prices Error")
        )


def get_front_month_prices(commodity: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Get front month prices for a commodity over a date range.
    
    Args:
        commodity: Commodity code (BRENT, WTI, GO, RBOB)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Formatted response with price data and citation metadata
    """
    try:
        # Parse dates
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_date_obj > end_date_obj:
            return format_price_response(
                f"Error: Start date ({start_date}) must be before or equal to end date ({end_date})",
                create_citation_metadata("Futures Prices Error")
            )
        
        # Validate commodity
        valid_commodities = ['BRENT', 'WTI', 'GO', 'RBOB']
        commodity_upper = commodity.upper()
        if commodity_upper not in valid_commodities:
            return format_price_response(
                f"Error: Invalid commodity '{commodity}'. Valid options: {', '.join(valid_commodities)}",
                create_citation_metadata("Futures Prices Error")
            )
        
        # Query database
        db = get_db()
        results = db.get_front_month_prices(commodity_upper, start_date_obj, end_date_obj)
        
        if not results:
            return format_price_response(
                f"No front month prices found for {commodity_upper} between {start_date} and {end_date}",
                create_citation_metadata(f"{commodity_upper} Front Month Prices")
            )
        
        # Format response
        lines = [f"Front month {commodity_upper} prices from {start_date} to {end_date}:\n"]
        for row in results:
            price = row['settlement_price']
            trade_date = row['trade_date']
            lines.append(f"{trade_date}: ${price:.2f}")
        
        text = "\n".join(lines)
        
        return format_price_response(
            text,
            create_citation_metadata(
                f"{commodity_upper} Front Month Prices - {start_date} to {end_date}",
                f"https://energy-trader.local/futures-prices/{commodity_upper.lower()}/{start_date}/{end_date}"
            )
        )
        
    except ValueError as e:
        return format_price_response(
            f"Error: Invalid date format. Expected YYYY-MM-DD format.",
            create_citation_metadata("Futures Prices Error")
        )
    except Exception as e:
        return format_price_response(
            f"Error retrieving prices: {str(e)}",
            create_citation_metadata("Futures Prices Error")
        )


def calculate_price_change(commodity: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Calculate price change between two dates.
    
    Args:
        commodity: Commodity code (BRENT, WTI, GO, RBOB)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Formatted response with price change data and citation metadata
    """
    try:
        # Parse dates
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_date_obj > end_date_obj:
            return format_price_response(
                f"Error: Start date ({start_date}) must be before or equal to end date ({end_date})",
                create_citation_metadata("Futures Prices Error")
            )
        
        # Validate commodity
        valid_commodities = ['BRENT', 'WTI', 'GO', 'RBOB']
        commodity_upper = commodity.upper()
        if commodity_upper not in valid_commodities:
            return format_price_response(
                f"Error: Invalid commodity '{commodity}'. Valid options: {', '.join(valid_commodities)}",
                create_citation_metadata("Futures Prices Error")
            )
        
        # Get prices for both dates
        db = get_db()
        start_price_data = db.get_front_month_price(commodity_upper, start_date_obj)
        end_price_data = db.get_front_month_price(commodity_upper, end_date_obj)
        
        if not start_price_data:
            return format_price_response(
                f"No front month price found for {commodity_upper} on {start_date}",
                create_citation_metadata("Futures Prices Error")
            )
        
        if not end_price_data:
            return format_price_response(
                f"No front month price found for {commodity_upper} on {end_date}",
                create_citation_metadata("Futures Prices Error")
            )
        
        start_price = float(start_price_data['settlement_price'])
        end_price = float(end_price_data['settlement_price'])
        
        # Calculate changes
        absolute_change = end_price - start_price
        percentage_change = (absolute_change / start_price) * 100
        
        direction = "increased" if absolute_change > 0 else "decreased" if absolute_change < 0 else "unchanged"
        
        text = (
            f"{commodity_upper} front month price change from {start_date} to {end_date}:\n"
            f"Start price: ${start_price:.2f}\n"
            f"End price: ${end_price:.2f}\n"
            f"Absolute change: ${absolute_change:+.2f} ({direction})\n"
            f"Percentage change: {percentage_change:+.2f}%"
        )
        
        return format_price_response(
            text,
            create_citation_metadata(
                f"{commodity_upper} Price Change - {start_date} to {end_date}",
                f"https://energy-trader.local/futures-prices/{commodity_upper.lower()}/change/{start_date}/{end_date}"
            )
        )
        
    except ValueError as e:
        return format_price_response(
            f"Error: Invalid date format. Expected YYYY-MM-DD format.",
            create_citation_metadata("Futures Prices Error")
        )
    except Exception as e:
        return format_price_response(
            f"Error calculating price change: {str(e)}",
            create_citation_metadata("Futures Prices Error")
        )


def get_seasonal_data(
    commodity: str,
    contract_month_offset: int,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    points_per_year: int = 12,
    format: str = "aggregated"
) -> Dict[str, Any]:
    """
    Get seasonal data for a specific contract month offset with configurable sampling frequency.
    
    Args:
        commodity: Commodity code (BRENT, WTI, GO, RBOB)
        contract_month_offset: Month offset (1=M1, 2=M2, etc.)
        start_year: Optional start year filter (by expiration year)
        end_year: Optional end year filter (by expiration year)
        points_per_year: Sampling frequency (12=monthly default, 24=bi-monthly, 52=weekly)
        format: Output format ("aggregated" default, "raw" for all daily prices)
        
    Returns:
        Formatted response with seasonal data and citation metadata
    """
    try:
        # Validate commodity
        valid_commodities = ['BRENT', 'WTI', 'GO', 'RBOB']
        commodity_upper = commodity.upper()
        if commodity_upper not in valid_commodities:
            return format_price_response(
                f"Error: Invalid commodity '{commodity}'. Valid options: {', '.join(valid_commodities)}",
                create_citation_metadata("Futures Prices Error")
            )
        
        # Validate month offset
        if contract_month_offset < 1 or contract_month_offset > 12:
            return format_price_response(
                f"Error: Contract month offset must be between 1 and 12, got {contract_month_offset}",
                create_citation_metadata("Futures Prices Error")
            )
        
        # Validate points_per_year
        if points_per_year not in [12, 24, 52]:
            return format_price_response(
                f"Error: points_per_year must be 12, 24, or 52, got {points_per_year}",
                create_citation_metadata("Futures Prices Error")
            )
        
        # Validate format
        if format not in ["aggregated", "raw", "data-points"]:
            return format_price_response(
                f"Error: format must be 'aggregated', 'raw', or 'data-points', got '{format}'",
                create_citation_metadata("Futures Prices Error")
            )
        
        db = get_db()
        
        # Handle data-points format (sampled points, not aggregated)
        if format == "data-points":
            results = db.get_seasonal_data_points(
                commodity_upper, contract_month_offset, points_per_year, start_year, end_year
            )
            
            if not results:
                return format_price_response(
                    f"No seasonal data found for {commodity_upper} M{contract_month_offset}",
                    create_citation_metadata(f"{commodity_upper} Seasonal Data")
                )
            
            # Format response as CSV-like data points
            lines = [f"Seasonal Data Points: {commodity_upper} M{contract_month_offset} Contracts"]
            if start_year or end_year:
                year_range = f" ({start_year or 'all'}-{end_year or 'all'})"
                lines[0] += year_range
            lines[0] += "\n"
            
            # Determine sampling description
            if points_per_year == 12:
                sampling_desc = "Monthly (last trading day of each month)"
                lines.append("Date,Year,Month,Price")
                for row in results:
                    trade_date = row['trade_date']
                    year = int(row['year'])
                    month = int(row['month'])
                    price = float(row['settlement_price'])
                    lines.append(f"{trade_date},{year},{month},{price:.2f}")
            elif points_per_year == 24:
                sampling_desc = "Bi-monthly (mid-month ~15th and end-of-month)"
                lines.append("Date,Year,Month,Position,Price")
                for row in results:
                    trade_date = row['trade_date']
                    year = int(row['year'])
                    month = int(row['month'])
                    position = row['position']
                    price = float(row['settlement_price'])
                    lines.append(f"{trade_date},{year},{month},{position},{price:.2f}")
            else:  # 52/year
                sampling_desc = "Weekly (consistent day of week, prefer Friday)"
                lines.append("Date,Year,Month,Week,Price")
                for row in results:
                    trade_date = row['trade_date']
                    year = int(row['year'])
                    month = int(row['month'])
                    week = int(row['week_number'])
                    price = float(row['settlement_price'])
                    lines.append(f"{trade_date},{year},{month},{week},{price:.2f}")
            
            text = "\n".join(lines)
            
            return format_price_response(
                text,
                create_citation_metadata(
                    f"{commodity_upper} M{contract_month_offset} Seasonal Data Points ({sampling_desc})",
                    f"https://energy-trader.local/futures-prices/{commodity_upper.lower()}/seasonal/m{contract_month_offset}"
                )
            )
        
        # Handle raw format (backward compatibility)
        if format == "raw":
            results = db.get_contract_prices_by_month_offset(
                commodity_upper, contract_month_offset, start_year, end_year
            )
            
            if not results:
                return format_price_response(
                    f"No seasonal data found for {commodity_upper} M{contract_month_offset}",
                    create_citation_metadata(f"{commodity_upper} Seasonal Data")
                )
            
            # Format response for charting (CSV-like format)
            lines = [f"Seasonal data for {commodity_upper} M{contract_month_offset} contract:\n"]
            lines.append("Date,Year,Month,Price")
            
            for row in results:
                trade_date = row['trade_date']
                year = row['expiration_year']
                month = row['expiration_month']
                price = row['settlement_price']
                lines.append(f"{trade_date},{year},{month},{price:.2f}")
            
            text = "\n".join(lines)
            
            return format_price_response(
                text,
                create_citation_metadata(
                    f"{commodity_upper} M{contract_month_offset} Seasonal Data",
                    f"https://energy-trader.local/futures-prices/{commodity_upper.lower()}/seasonal/m{contract_month_offset}"
                )
            )
        
        # Handle aggregated format (new default)
        results = db.get_seasonal_data_aggregated(
            commodity_upper, contract_month_offset, points_per_year, start_year, end_year
        )
        
        if not results:
            return format_price_response(
                f"No seasonal data found for {commodity_upper} M{contract_month_offset}",
                create_citation_metadata(f"{commodity_upper} Seasonal Data")
            )
        
        # Format aggregated response
        lines = [f"Seasonal Analysis: {commodity_upper} M{contract_month_offset} Contracts"]
        if start_year or end_year:
            year_range = f" ({start_year or 'all'}-{end_year or 'all'})"
            lines[0] += year_range
        lines[0] += "\n"
        
        # Determine sampling description
        if points_per_year == 12:
            sampling_desc = "Monthly (last trading day of each month)"
        elif points_per_year == 24:
            sampling_desc = "Bi-monthly (mid-month ~15th and end-of-month)"
        else:
            sampling_desc = "Weekly (consistent day of week, prefer Friday)"
        
        lines.append(f"Sampling: {sampling_desc}\n")
        
        # Format statistics table
        if points_per_year == 12:
            # Monthly format
            lines.append("Monthly Statistics:")
            lines.append("Month  | Count | Avg    | Min    | Max    | Std Dev | Median")
            lines.append("-------|-------|--------|--------|--------|---------|--------")
            
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            for row in results:
                month_num = int(row['expiration_month'])
                month_name = month_names[month_num - 1]
                count = row['count']
                avg_price = float(row['avg_price']) if row['avg_price'] else 0.0
                min_price = float(row['min_price']) if row['min_price'] else 0.0
                max_price = float(row['max_price']) if row['max_price'] else 0.0
                std_dev = float(row['std_dev']) if row['std_dev'] else 0.0
                median = float(row['median']) if row['median'] else 0.0
                
                lines.append(
                    f"{month_name:6} | {count:5} | {avg_price:6.2f} | {min_price:6.2f} | "
                    f"{max_price:6.2f} | {std_dev:7.2f} | {median:6.2f}"
                )
        
        elif points_per_year == 24:
            # Bi-monthly format
            lines.append("Bi-Monthly Statistics:")
            lines.append("Month  | Position | Count | Avg    | Min    | Max    | Std Dev | Median")
            lines.append("-------|----------|-------|--------|--------|--------|---------|--------")
            
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            for row in results:
                month_num = int(row['expiration_month'])
                month_name = month_names[month_num - 1]
                position = row['position']
                count = row['count']
                avg_price = float(row['avg_price']) if row['avg_price'] else 0.0
                min_price = float(row['min_price']) if row['min_price'] else 0.0
                max_price = float(row['max_price']) if row['max_price'] else 0.0
                std_dev = float(row['std_dev']) if row['std_dev'] else 0.0
                median = float(row['median']) if row['median'] else 0.0
                
                lines.append(
                    f"{month_name:6} | {position:8} | {count:5} | {avg_price:6.2f} | "
                    f"{min_price:6.2f} | {max_price:6.2f} | {std_dev:7.2f} | {median:6.2f}"
                )
        
        else:  # 52/year
            # Weekly format
            lines.append("Weekly Statistics:")
            lines.append("Month  | Week | Count | Avg    | Min    | Max    | Std Dev | Median")
            lines.append("-------|------|-------|--------|--------|--------|---------|--------")
            
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            for row in results:
                month_num = int(row['expiration_month'])
                month_name = month_names[month_num - 1]
                week_number = int(row['week_number'])
                count = row['count']
                avg_price = float(row['avg_price']) if row['avg_price'] else 0.0
                min_price = float(row['min_price']) if row['min_price'] else 0.0
                max_price = float(row['max_price']) if row['max_price'] else 0.0
                std_dev = float(row['std_dev']) if row['std_dev'] else 0.0
                median = float(row['median']) if row['median'] else 0.0
                
                lines.append(
                    f"{month_name:6} | {week_number:4} | {count:5} | {avg_price:6.2f} | "
                    f"{min_price:6.2f} | {max_price:6.2f} | {std_dev:7.2f} | {median:6.2f}"
                )
        
        # Add pattern detection for monthly data (12/year)
        if points_per_year == 12 and len(results) >= 2:
            patterns = _detect_seasonal_patterns(results)
            if patterns:
                lines.append("\nSeasonal Patterns Detected:")
                for pattern in patterns:
                    lines.append(f"- {pattern}")
        
        text = "\n".join(lines)
        
        return format_price_response(
            text,
            create_citation_metadata(
                f"{commodity_upper} M{contract_month_offset} Seasonal Data ({sampling_desc})",
                f"https://energy-trader.local/futures-prices/{commodity_upper.lower()}/seasonal/m{contract_month_offset}"
            )
        )
        
    except ValueError as e:
        return format_price_response(
            f"Error: {str(e)}",
            create_citation_metadata("Futures Prices Error")
        )
    except Exception as e:
        return format_price_response(
            f"Error retrieving seasonal data: {str(e)}",
            create_citation_metadata("Futures Prices Error")
        )


def _detect_seasonal_patterns(results: List[Dict[str, Any]], threshold: float = 5.0) -> List[str]:
    """
    Detect significant seasonal patterns from aggregated monthly statistics.
    
    Args:
        results: List of aggregated statistics, ordered by expiration_month
        threshold: Minimum percentage difference to consider significant (default: 5%)
        
    Returns:
        List of pattern descriptions
    """
    patterns = []
    
    if len(results) < 2:
        return patterns
    
    # Sort by month to ensure correct order
    sorted_results = sorted(results, key=lambda x: int(x['expiration_month']))
    
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    # Compare consecutive months
    for i in range(len(sorted_results) - 1):
        current = sorted_results[i]
        next_month = sorted_results[i + 1]
        
        current_avg = float(current['avg_price']) if current['avg_price'] else 0.0
        next_avg = float(next_month['avg_price']) if next_month['avg_price'] else 0.0
        
        if current_avg > 0:
            pct_change = ((next_avg - current_avg) / current_avg) * 100
            
            if abs(pct_change) >= threshold:
                current_month_name = month_names[int(current['expiration_month']) - 1]
                next_month_name = month_names[int(next_month['expiration_month']) - 1]
                
                direction = "higher" if pct_change > 0 else "lower"
                patterns.append(
                    f"{next_month_name} prices are typically {abs(pct_change):.1f}% {direction} "
                    f"than {current_month_name} prices"
                )
    
    # Also compare first and last month (yearly cycle)
    if len(sorted_results) >= 12:
        first = sorted_results[0]
        last = sorted_results[-1]
        
        first_avg = float(first['avg_price']) if first['avg_price'] else 0.0
        last_avg = float(last['avg_price']) if last['avg_price'] else 0.0
        
        if first_avg > 0:
            pct_change = ((last_avg - first_avg) / first_avg) * 100
            
            if abs(pct_change) >= threshold:
                first_month_name = month_names[int(first['expiration_month']) - 1]
                last_month_name = month_names[int(last['expiration_month']) - 1]
                
                direction = "higher" if pct_change > 0 else "lower"
                patterns.append(
                    f"{last_month_name} prices are typically {abs(pct_change):.1f}% {direction} "
                    f"than {first_month_name} prices (yearly cycle)"
                )
    
    return patterns

