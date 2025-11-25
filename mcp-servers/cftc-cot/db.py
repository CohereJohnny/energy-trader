"""
Database connection and query utilities for CFTC COT data.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta


class Database:
    """Database connection and query handler for CFTC COT data."""
    
    def __init__(self):
        """Initialize database connection."""
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'energy_trader'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres'),
            )
        except psycopg2.Error as e:
            raise ConnectionError(f"Failed to connect to database: {e}")
    
    def get_cot_data(
        self,
        commodity: Optional[str] = None,
        report_date: Optional[date] = None,
        trader_category: Optional[str] = None,
        position_type: str = 'all'
    ) -> List[Dict[str, Any]]:
        """
        Get COT data for specified criteria.
        
        Args:
            commodity: Commodity group (Petroleum and Products, Natural Gas and Products, Electricity)
            report_date: Report date (if None, returns latest)
            trader_category: Trader category code (PRODUCER, SWAP, MANAGED_MONEY, OTHER_REPORTABLE, NONREPORTABLE)
            position_type: Position type ('all', 'old', 'other')
            
        Returns:
            List of position data dictionaries
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT 
                    r.report_date,
                    m.market_name,
                    m.exchange,
                    m.cftc_code,
                    m.commodity_group,
                    tc.category_name,
                    tc.category_code,
                    p.position_type,
                    p.long_positions,
                    p.short_positions,
                    p.spreading_positions,
                    oi.open_interest,
                    ch.change_long,
                    ch.change_short,
                    ch.change_spreading,
                    ch.change_open_interest,
                    pct.pct_long,
                    pct.pct_short,
                    pct.pct_spreading,
                    tc_counts.num_traders_long,
                    tc_counts.num_traders_short,
                    tc_counts.num_traders_spreading
                FROM cftc_cot.positions p
                JOIN cftc_cot.reports r ON p.report_id = r.id
                JOIN cftc_cot.markets m ON p.market_id = m.id
                JOIN cftc_cot.trader_categories tc ON p.category_id = tc.id
                LEFT JOIN cftc_cot.open_interest oi ON oi.report_id = r.id AND oi.market_id = m.id AND oi.position_type = p.position_type
                LEFT JOIN cftc_cot.changes ch ON ch.report_id = r.id AND ch.market_id = m.id AND ch.category_id = tc.id
                LEFT JOIN cftc_cot.percentages pct ON pct.report_id = r.id AND pct.market_id = m.id AND pct.category_id = tc.id AND pct.position_type = p.position_type
                LEFT JOIN cftc_cot.trader_counts tc_counts ON tc_counts.report_id = r.id AND tc_counts.market_id = m.id AND tc_counts.category_id = tc.id AND tc_counts.position_type = p.position_type
                WHERE 1=1
            """
            params = []
            
            if report_date:
                query += " AND r.report_date = %s"
                params.append(report_date)
            else:
                # Get latest report date
                query += " AND r.report_date = (SELECT MAX(report_date) FROM cftc_cot.reports)"
            
            if commodity:
                query += " AND m.commodity_group = %s"
                params.append(commodity)
            
            if trader_category:
                query += " AND tc.category_code = %s"
                params.append(trader_category.upper())
            
            if position_type:
                query += " AND p.position_type = %s"
                params.append(position_type)
            
            query += " ORDER BY r.report_date DESC, m.market_name, tc.category_code"
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def analyze_positioning_trends(
        self,
        commodity: str,
        start_date: date,
        end_date: date,
        trader_category: str
    ) -> List[Dict[str, Any]]:
        """
        Analyze positioning trends for a commodity and trader category over time.
        
        Args:
            commodity: Commodity group
            start_date: Start date
            end_date: End date
            trader_category: Trader category code
            
        Returns:
            List of trend data dictionaries
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    r.report_date,
                    m.market_name,
                    m.cftc_code,
                    tc.category_name,
                    p.long_positions,
                    p.short_positions,
                    p.spreading_positions,
                    oi.open_interest,
                    pct.pct_long,
                    pct.pct_short,
                    pct.pct_spreading,
                    ch.change_long,
                    ch.change_short,
                    ch.change_spreading
                FROM cftc_cot.positions p
                JOIN cftc_cot.reports r ON p.report_id = r.id
                JOIN cftc_cot.markets m ON p.market_id = m.id
                JOIN cftc_cot.trader_categories tc ON p.category_id = tc.id
                LEFT JOIN cftc_cot.open_interest oi ON oi.report_id = r.id AND oi.market_id = m.id AND oi.position_type = p.position_type
                LEFT JOIN cftc_cot.percentages pct ON pct.report_id = r.id AND pct.market_id = m.id AND pct.category_id = tc.id AND pct.position_type = p.position_type
                LEFT JOIN cftc_cot.changes ch ON ch.report_id = r.id AND ch.market_id = m.id AND ch.category_id = tc.id
                WHERE m.commodity_group = %s
                    AND r.report_date BETWEEN %s AND %s
                    AND tc.category_code = %s
                    AND p.position_type = 'all'
                ORDER BY r.report_date ASC, m.market_name
            """, (commodity, start_date, end_date, trader_category.upper()))
            return cursor.fetchall()
    
    def compare_positioning(
        self,
        commodities: List[str],
        report_date: date,
        trader_category: str
    ) -> List[Dict[str, Any]]:
        """
        Compare positioning across multiple commodities on a given date.
        
        Args:
            commodities: List of commodity groups
            report_date: Report date
            trader_category: Trader category code
            
        Returns:
            List of comparison data dictionaries
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            placeholders = ','.join(['%s'] * len(commodities))
            cursor.execute(f"""
                SELECT 
                    m.commodity_group,
                    m.market_name,
                    m.cftc_code,
                    tc.category_name,
                    p.long_positions,
                    p.short_positions,
                    p.spreading_positions,
                    oi.open_interest,
                    pct.pct_long,
                    pct.pct_short,
                    pct.pct_spreading
                FROM cftc_cot.positions p
                JOIN cftc_cot.reports r ON p.report_id = r.id
                JOIN cftc_cot.markets m ON p.market_id = m.id
                JOIN cftc_cot.trader_categories tc ON p.category_id = tc.id
                LEFT JOIN cftc_cot.open_interest oi ON oi.report_id = r.id AND oi.market_id = m.id AND oi.position_type = p.position_type
                LEFT JOIN cftc_cot.percentages pct ON pct.report_id = r.id AND pct.market_id = m.id AND pct.category_id = tc.id AND pct.position_type = p.position_type
                WHERE r.report_date = %s
                    AND m.commodity_group IN ({placeholders})
                    AND tc.category_code = %s
                    AND p.position_type = 'all'
                ORDER BY m.commodity_group, m.market_name
            """, [report_date] + commodities + [trader_category.upper()])
            return cursor.fetchall()
    
    def get_positioning_extremes(
        self,
        commodity: str,
        trader_category: str,
        lookback_days: int = 365,
        metric: str = 'long'
    ) -> List[Dict[str, Any]]:
        """
        Get positioning extremes for a commodity and trader category.
        
        Args:
            commodity: Commodity group
            trader_category: Trader category code
            lookback_days: Number of days to look back
            metric: Metric to find extremes for ('long', 'short', 'net', 'pct_long', 'pct_short')
            
        Returns:
            List of extreme positioning data dictionaries
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cutoff_date = date.today() - timedelta(days=lookback_days)
            
            # Build query based on metric
            if metric == 'long':
                order_by = "p.long_positions DESC"
                select_metric = "p.long_positions AS metric_value"
            elif metric == 'short':
                order_by = "p.short_positions DESC"
                select_metric = "p.short_positions AS metric_value"
            elif metric == 'net':
                order_by = "(p.long_positions - COALESCE(p.short_positions, 0)) DESC"
                select_metric = "(p.long_positions - COALESCE(p.short_positions, 0)) AS metric_value"
            elif metric == 'pct_long':
                order_by = "pct.pct_long DESC"
                select_metric = "pct.pct_long AS metric_value"
            elif metric == 'pct_short':
                order_by = "pct.pct_short DESC"
                select_metric = "pct.pct_short AS metric_value"
            else:
                order_by = "p.long_positions DESC"
                select_metric = "p.long_positions AS metric_value"
            
            cursor.execute(f"""
                SELECT 
                    r.report_date,
                    m.market_name,
                    m.cftc_code,
                    tc.category_name,
                    p.long_positions,
                    p.short_positions,
                    p.spreading_positions,
                    oi.open_interest,
                    pct.pct_long,
                    pct.pct_short,
                    pct.pct_spreading,
                    {select_metric}
                FROM cftc_cot.positions p
                JOIN cftc_cot.reports r ON p.report_id = r.id
                JOIN cftc_cot.markets m ON p.market_id = m.id
                JOIN cftc_cot.trader_categories tc ON p.category_id = tc.id
                LEFT JOIN cftc_cot.open_interest oi ON oi.report_id = r.id AND oi.market_id = m.id AND oi.position_type = p.position_type
                LEFT JOIN cftc_cot.percentages pct ON pct.report_id = r.id AND pct.market_id = m.id AND pct.category_id = tc.id AND pct.position_type = p.position_type
                WHERE m.commodity_group = %s
                    AND r.report_date >= %s
                    AND tc.category_code = %s
                    AND p.position_type = 'all'
                ORDER BY {order_by}
                LIMIT 10
            """, (commodity, cutoff_date, trader_category.upper()))
            return cursor.fetchall()
    
    def get_latest_report_date(self) -> Optional[date]:
        """Get the latest report date in the database."""
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT MAX(report_date) FROM cftc_cot.reports")
            result = cursor.fetchone()
            return result[0] if result and result[0] else None
    
    def get_loaded_reports(
        self,
        commodity: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of loaded reports with optional filters.
        
        Args:
            commodity: Commodity group filter (optional)
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            
        Returns:
            List of report dictionaries with metadata
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT DISTINCT
                    r.report_date,
                    r.report_type,
                    r.format,
                    r.source_url,
                    COUNT(DISTINCT m.id) as market_count,
                    COUNT(DISTINCT m.commodity_group) as commodity_group_count,
                    STRING_AGG(DISTINCT m.commodity_group, ', ' ORDER BY m.commodity_group) as commodity_groups
                FROM cftc_cot.reports r
                LEFT JOIN cftc_cot.positions p ON p.report_id = r.id
                LEFT JOIN cftc_cot.markets m ON p.market_id = m.id
                WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND r.report_date >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND r.report_date <= %s"
                params.append(end_date)
            
            query += " GROUP BY r.id, r.report_date, r.report_type, r.format, r.source_url"
            
            if commodity:
                query += " HAVING STRING_AGG(DISTINCT m.commodity_group, ', ') LIKE %s"
                params.append(f"%{commodity}%")
            
            query += " ORDER BY r.report_date DESC"
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def get_loading_status(
        self,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get loading status from loading_log table.
        
        Args:
            status: Filter by status ('pending', 'downloading', 'parsing', 'loading', 'completed', 'failed')
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            
        Returns:
            List of loading log entries
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT 
                    report_date,
                    report_type,
                    format,
                    status,
                    started_at,
                    completed_at,
                    records_loaded,
                    error_message,
                    created_at,
                    updated_at
                FROM cftc_cot.loading_log
                WHERE 1=1
            """
            params = []
            
            if status:
                query += " AND status = %s"
                params.append(status)
            
            if start_date:
                query += " AND report_date >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND report_date <= %s"
                params.append(end_date)
            
            query += " ORDER BY report_date DESC, created_at DESC"
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def get_data_coverage(self) -> Dict[str, Any]:
        """
        Get data coverage statistics.
        
        Returns:
            Dictionary with coverage statistics
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get overall statistics
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT r.id) as total_reports,
                    MIN(r.report_date) as earliest_date,
                    MAX(r.report_date) as latest_date,
                    COUNT(DISTINCT m.commodity_group) as commodity_groups_count,
                    COUNT(DISTINCT m.id) as markets_count,
                    STRING_AGG(DISTINCT m.commodity_group, ', ' ORDER BY m.commodity_group) as commodity_groups
                FROM cftc_cot.reports r
                LEFT JOIN cftc_cot.positions p ON p.report_id = r.id
                LEFT JOIN cftc_cot.markets m ON p.market_id = m.id
            """)
            coverage = cursor.fetchone()
            
            # Handle case where no data exists
            if not coverage:
                return {
                    'total_reports': 0,
                    'earliest_date': None,
                    'latest_date': None,
                    'commodity_groups_count': 0,
                    'markets_count': 0,
                    'commodity_groups': None,
                    'loading_status_counts': {},
                    'commodity_statistics': []
                }
            
            # Get loading status counts
            cursor.execute("""
                SELECT 
                    status,
                    COUNT(*) as count
                FROM cftc_cot.loading_log
                GROUP BY status
            """)
            status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Get commodity-specific counts
            cursor.execute("""
                SELECT 
                    m.commodity_group,
                    COUNT(DISTINCT r.id) as report_count,
                    MIN(r.report_date) as earliest_date,
                    MAX(r.report_date) as latest_date
                FROM cftc_cot.reports r
                JOIN cftc_cot.positions p ON p.report_id = r.id
                JOIN cftc_cot.markets m ON p.market_id = m.id
                WHERE m.commodity_group IS NOT NULL
                GROUP BY m.commodity_group
                ORDER BY m.commodity_group
            """)
            commodity_stats = cursor.fetchall()
            
            return {
                'total_reports': coverage.get('total_reports', 0) or 0,
                'earliest_date': coverage.get('earliest_date'),
                'latest_date': coverage.get('latest_date'),
                'commodity_groups_count': coverage.get('commodity_groups_count', 0) or 0,
                'markets_count': coverage.get('markets_count', 0) or 0,
                'commodity_groups': coverage.get('commodity_groups'),
                'loading_status_counts': status_counts,
                'commodity_statistics': commodity_stats
            }
    
    def get_missing_reports(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Identify missing reports (gaps in expected weekly reports).
        
        Args:
            start_date: Start date for analysis (defaults to earliest loaded report)
            end_date: End date for analysis (defaults to today)
            
        Returns:
            List of missing report dates
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get date range
            if not start_date:
                cursor.execute("SELECT MIN(report_date) as min_date FROM cftc_cot.reports")
                result = cursor.fetchone()
                if result and result.get('min_date'):
                    start_date = result['min_date']
                else:
                    start_date = date.today() - timedelta(days=365)
            
            if not end_date:
                end_date = date.today()
            
            # Get all loaded report dates
            cursor.execute("""
                SELECT DISTINCT report_date
                FROM cftc_cot.reports
                WHERE report_date BETWEEN %s AND %s
                ORDER BY report_date
            """, (start_date, end_date))
            loaded_dates = {row['report_date'] for row in cursor.fetchall()}
            
            # Generate expected weekly dates (CFTC reports are typically released on Fridays)
            # Reports are dated as of the previous Tuesday
            expected_dates = []
            current_date = start_date
            
            # Find the first Tuesday before or on start_date
            days_until_tuesday = (current_date.weekday() - 1) % 7
            if days_until_tuesday > 0:
                current_date = current_date - timedelta(days=days_until_tuesday)
            
            # Generate expected report dates (every Tuesday)
            while current_date <= end_date:
                expected_dates.append(current_date)
                current_date += timedelta(days=7)
            
            # Find missing dates
            missing_dates = [d for d in expected_dates if d not in loaded_dates]
            
            # Format as list of dictionaries
            return [{'report_date': d, 'status': 'missing'} for d in missing_dates]
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


# Global database instance
_db_instance = None

def get_db() -> Database:
    """Get or create database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance

