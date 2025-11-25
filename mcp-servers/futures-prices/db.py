"""
Database connection and query utilities for futures prices.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
from datetime import date, datetime


class Database:
    """Database connection and query handler."""
    
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
    
    def get_front_month_price(self, commodity: str, trade_date: date) -> Optional[Dict[str, Any]]:
        """
        Get front month price for a commodity on a specific date.
        
        Args:
            commodity: Commodity code (BRENT, WTI, GO, RBOB)
            trade_date: Trading date
            
        Returns:
            Dictionary with price data or None if not found
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT * FROM futures_prices.get_front_month_price(%s, %s)
                """,
                (commodity.upper(), trade_date)
            )
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def get_front_month_prices(self, commodity: str, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """
        Get front month prices for a commodity over a date range.
        
        Args:
            commodity: Commodity code (BRENT, WTI, GO, RBOB)
            start_date: Start date
            end_date: End date
            
        Returns:
            List of dictionaries with price data
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT * FROM futures_prices.front_month_prices
                WHERE commodity_code = %s
                    AND trade_date >= %s
                    AND trade_date <= %s
                ORDER BY trade_date
                """,
                (commodity.upper(), start_date, end_date)
            )
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    def get_contract_prices_by_month_offset(
        self, 
        commodity: str, 
        month_offset: int,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get prices for a specific contract month offset (e.g., M2 = second month contract).
        
        Args:
            commodity: Commodity code (BRENT, WTI, GO, RBOB)
            month_offset: Month offset (1=M1, 2=M2, etc.)
            start_year: Optional start year filter
            end_year: Optional end year filter
            
        Returns:
            List of dictionaries with price data
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get all contracts for the commodity, ordered by expiration
            # Then filter to the Nth contract for each year
            query = """
                WITH ranked_contracts AS (
                    SELECT 
                        c.id,
                        c.expiration_year,
                        c.expiration_month,
                        ROW_NUMBER() OVER (
                            PARTITION BY c.commodity_id, c.expiration_year 
                            ORDER BY c.expiration_date
                        ) as contract_rank
                    FROM futures_prices.contracts c
                    JOIN futures_prices.commodities com ON c.commodity_id = com.id
                    WHERE com.code = %s
                )
                SELECT 
                    p.trade_date,
                    c.expiration_year,
                    c.expiration_month,
                    p.settlement_price
                FROM futures_prices.prices p
                JOIN ranked_contracts rc ON p.contract_id = rc.id
                JOIN futures_prices.contracts c ON p.contract_id = c.id
                WHERE rc.contract_rank = %s
                    AND p.settlement_price IS NOT NULL
            """
            params = [commodity.upper(), month_offset]
            
            if start_year:
                query += " AND c.expiration_year >= %s"
                params.append(start_year)
            
            if end_year:
                query += " AND c.expiration_year <= %s"
                params.append(end_year)
            
            query += " ORDER BY p.trade_date, c.expiration_year"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    def get_seasonal_data_aggregated(
        self,
        commodity: str,
        month_offset: int,
        points_per_year: int = 12,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get aggregated seasonal data for a contract month offset with configurable sampling frequency.
        
        Args:
            commodity: Commodity code (BRENT, WTI, GO, RBOB)
            month_offset: Month offset (1=M1, 2=M2, etc.)
            points_per_year: Sampling frequency (12=monthly, 24=bi-monthly, 52=weekly)
            start_year: Optional start year filter
            end_year: Optional end year filter
            
        Returns:
            List of dictionaries with aggregated statistics
        """
        if points_per_year == 12:
            return self._get_monthly_aggregated(commodity, month_offset, start_year, end_year)
        elif points_per_year == 24:
            return self._get_bimonthly_aggregated(commodity, month_offset, start_year, end_year)
        elif points_per_year == 52:
            return self._get_weekly_aggregated(commodity, month_offset, start_year, end_year)
        else:
            raise ValueError(f"Invalid points_per_year: {points_per_year}. Must be 12, 24, or 52.")
    
    def get_seasonal_data_points(
        self,
        commodity: str,
        month_offset: int,
        points_per_year: int = 12,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get sampled data points (not aggregated) for a contract month offset.
        
        Args:
            commodity: Commodity code (BRENT, WTI, GO, RBOB)
            month_offset: Month offset (1=M1, 2=M2, etc.)
            points_per_year: Sampling frequency (12=monthly, 24=bi-monthly, 52=weekly)
            start_year: Optional start year filter (by expiration year)
            end_year: Optional end year filter (by expiration year)
            
        Returns:
            List of dictionaries with sampled data points (trade_date, price, etc.)
        """
        if points_per_year == 12:
            return self._get_monthly_data_points(commodity, month_offset, start_year, end_year)
        elif points_per_year == 24:
            return self._get_bimonthly_data_points(commodity, month_offset, start_year, end_year)
        elif points_per_year == 52:
            return self._get_weekly_data_points(commodity, month_offset, start_year, end_year)
        else:
            raise ValueError(f"Invalid points_per_year: {points_per_year}. Must be 12, 24, or 52.")
    
    def _get_monthly_aggregated(
        self,
        commodity: str,
        month_offset: int,
        start_year: Optional[int],
        end_year: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Get monthly aggregated statistics (12/year - last trading day of each month)."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                WITH ranked_contracts AS (
                    SELECT 
                        c.id,
                        c.expiration_year,
                        c.expiration_month,
                        ROW_NUMBER() OVER (
                            PARTITION BY c.commodity_id, c.expiration_year 
                            ORDER BY c.expiration_date
                        ) as contract_rank
                    FROM futures_prices.contracts c
                    JOIN futures_prices.commodities com ON c.commodity_id = com.id
                    WHERE com.code = %s
            """
            params = [commodity.upper()]
            
            if start_year:
                query += " AND c.expiration_year >= %s"
                params.append(start_year)
            
            if end_year:
                query += " AND c.expiration_year <= %s"
                params.append(end_year)
            
            query += """
                ),
                monthly_last_days AS (
                    SELECT 
                        EXTRACT(MONTH FROM p.trade_date)::integer as trade_month,
                        p.trade_date,
                        p.settlement_price,
                        ROW_NUMBER() OVER (
                            PARTITION BY EXTRACT(YEAR FROM p.trade_date), EXTRACT(MONTH FROM p.trade_date)
                            ORDER BY p.trade_date DESC
                        ) as rn
                    FROM futures_prices.prices p
                    JOIN ranked_contracts rc ON p.contract_id = rc.id
                    WHERE rc.contract_rank = %s
                        AND p.settlement_price IS NOT NULL
                )
                SELECT 
                    trade_month as expiration_month,
                    COUNT(*) as count,
                    ROUND(AVG(settlement_price)::numeric, 2) as avg_price,
                    ROUND(MIN(settlement_price)::numeric, 2) as min_price,
                    ROUND(MAX(settlement_price)::numeric, 2) as max_price,
                    ROUND(STDDEV(settlement_price)::numeric, 2) as std_dev,
                    ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY settlement_price))::numeric, 2) as median
                FROM monthly_last_days
                WHERE rn = 1
                GROUP BY trade_month 
                ORDER BY trade_month
            """
            params.append(month_offset)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    def _get_bimonthly_aggregated(
        self,
        commodity: str,
        month_offset: int,
        start_year: Optional[int],
        end_year: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Get bi-monthly aggregated statistics (24/year - mid-month and end-of-month)."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                WITH ranked_contracts AS (
                    SELECT 
                        c.id,
                        c.expiration_year,
                        c.expiration_month,
                        ROW_NUMBER() OVER (
                            PARTITION BY c.commodity_id, c.expiration_year 
                            ORDER BY c.expiration_date
                        ) as contract_rank
                    FROM futures_prices.contracts c
                    JOIN futures_prices.commodities com ON c.commodity_id = com.id
                    WHERE com.code = %s
            """
            params = [commodity.upper()]
            
            if start_year:
                query += " AND c.expiration_year >= %s"
                params.append(start_year)
            
            if end_year:
                query += " AND c.expiration_year <= %s"
                params.append(end_year)
            
            query += """
                ),
                monthly_samples AS (
                    SELECT 
                        EXTRACT(MONTH FROM p.trade_date)::integer as trade_month,
                        p.trade_date,
                        p.settlement_price,
                        CASE 
                            WHEN ABS(EXTRACT(DAY FROM p.trade_date) - 15) <= 3 
                                AND EXTRACT(DAY FROM p.trade_date) <= 18
                            THEN 'mid'
                            ELSE 'end'
                        END as position,
                        CASE 
                            WHEN ABS(EXTRACT(DAY FROM p.trade_date) - 15) <= 3 
                                AND EXTRACT(DAY FROM p.trade_date) <= 18
                            THEN ROW_NUMBER() OVER (
                                PARTITION BY EXTRACT(YEAR FROM p.trade_date), EXTRACT(MONTH FROM p.trade_date)
                                ORDER BY ABS(EXTRACT(DAY FROM p.trade_date) - 15)
                            )
                            ELSE ROW_NUMBER() OVER (
                                PARTITION BY EXTRACT(YEAR FROM p.trade_date), EXTRACT(MONTH FROM p.trade_date)
                                ORDER BY p.trade_date DESC
                            )
                        END as rn
                    FROM futures_prices.prices p
                    JOIN ranked_contracts rc ON p.contract_id = rc.id
                    WHERE rc.contract_rank = %s
                        AND p.settlement_price IS NOT NULL
                )
                SELECT 
                    trade_month as expiration_month,
                    position,
                    COUNT(*) as count,
                    ROUND(AVG(settlement_price)::numeric, 2) as avg_price,
                    ROUND(MIN(settlement_price)::numeric, 2) as min_price,
                    ROUND(MAX(settlement_price)::numeric, 2) as max_price,
                    ROUND(STDDEV(settlement_price)::numeric, 2) as std_dev,
                    ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY settlement_price))::numeric, 2) as median
                FROM monthly_samples
                WHERE rn = 1
                GROUP BY trade_month, position 
                ORDER BY trade_month, position
            """
            params.append(month_offset)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    def _get_weekly_aggregated(
        self,
        commodity: str,
        month_offset: int,
        start_year: Optional[int],
        end_year: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Get weekly aggregated statistics (52/year - consistent day of week, prefer Friday)."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                WITH ranked_contracts AS (
                    SELECT 
                        c.id,
                        c.expiration_year,
                        c.expiration_month,
                        ROW_NUMBER() OVER (
                            PARTITION BY c.commodity_id, c.expiration_year 
                            ORDER BY c.expiration_date
                        ) as contract_rank
                    FROM futures_prices.contracts c
                    JOIN futures_prices.commodities com ON c.commodity_id = com.id
                    WHERE com.code = %s
            """
            params = [commodity.upper()]
            
            if start_year:
                query += " AND c.expiration_year >= %s"
                params.append(start_year)
            
            if end_year:
                query += " AND c.expiration_year <= %s"
                params.append(end_year)
            
            query += """
                ),
                weekly_samples AS (
                    SELECT 
                        EXTRACT(MONTH FROM p.trade_date)::integer as trade_month,
                        EXTRACT(WEEK FROM p.trade_date)::integer as week_number,
                        p.trade_date,
                        p.settlement_price,
                        ROW_NUMBER() OVER (
                            PARTITION BY EXTRACT(YEAR FROM p.trade_date), EXTRACT(MONTH FROM p.trade_date), EXTRACT(WEEK FROM p.trade_date)
                            ORDER BY CASE WHEN EXTRACT(DOW FROM p.trade_date) = 5 THEN 0 ELSE 1 END,
                                     p.trade_date DESC
                        ) as rn
                    FROM futures_prices.prices p
                    JOIN ranked_contracts rc ON p.contract_id = rc.id
                    WHERE rc.contract_rank = %s
                        AND p.settlement_price IS NOT NULL
                )
                SELECT 
                    trade_month as expiration_month,
                    week_number,
                    COUNT(*) as count,
                    ROUND(AVG(settlement_price)::numeric, 2) as avg_price,
                    ROUND(MIN(settlement_price)::numeric, 2) as min_price,
                    ROUND(MAX(settlement_price)::numeric, 2) as max_price,
                    ROUND(STDDEV(settlement_price)::numeric, 2) as std_dev,
                    ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY settlement_price))::numeric, 2) as median
                FROM weekly_samples
                WHERE rn = 1
                GROUP BY trade_month, week_number 
                ORDER BY trade_month, week_number
            """
            params.append(month_offset)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    def _get_monthly_data_points(
        self,
        commodity: str,
        month_offset: int,
        start_year: Optional[int],
        end_year: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Get monthly sampled data points (12/year - last trading day of each month)."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                WITH ranked_contracts AS (
                    SELECT 
                        c.id,
                        c.expiration_year,
                        c.expiration_month,
                        ROW_NUMBER() OVER (
                            PARTITION BY c.commodity_id, c.expiration_year 
                            ORDER BY c.expiration_date
                        ) as contract_rank
                    FROM futures_prices.contracts c
                    JOIN futures_prices.commodities com ON c.commodity_id = com.id
                    WHERE com.code = %s
            """
            params = [commodity.upper()]
            
            if start_year:
                query += " AND c.expiration_year >= %s"
                params.append(start_year)
            
            if end_year:
                query += " AND c.expiration_year <= %s"
                params.append(end_year)
            
            query += """
                ),
                monthly_last_days AS (
                    SELECT 
                        EXTRACT(MONTH FROM p.trade_date)::integer as trade_month,
                        EXTRACT(YEAR FROM p.trade_date)::integer as trade_year,
                        p.trade_date,
                        p.settlement_price,
                        ROW_NUMBER() OVER (
                            PARTITION BY EXTRACT(YEAR FROM p.trade_date), EXTRACT(MONTH FROM p.trade_date)
                            ORDER BY p.trade_date DESC
                        ) as rn
                    FROM futures_prices.prices p
                    JOIN ranked_contracts rc ON p.contract_id = rc.id
                    WHERE rc.contract_rank = %s
                        AND p.settlement_price IS NOT NULL
            """
            params.append(month_offset)
            
            # Filter by trade date year (not expiration year) for data points
            if start_year:
                query += " AND EXTRACT(YEAR FROM p.trade_date) >= %s"
                params.append(start_year)
            
            if end_year:
                query += " AND EXTRACT(YEAR FROM p.trade_date) <= %s"
                params.append(end_year)
            
            query += """
                )
                SELECT 
                    trade_year as year,
                    trade_month as month,
                    trade_date,
                    settlement_price
                FROM monthly_last_days
                WHERE rn = 1
                ORDER BY trade_date
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    def _get_bimonthly_data_points(
        self,
        commodity: str,
        month_offset: int,
        start_year: Optional[int],
        end_year: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Get bi-monthly sampled data points (24/year - mid-month and end-of-month)."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                WITH ranked_contracts AS (
                    SELECT 
                        c.id,
                        c.expiration_year,
                        c.expiration_month,
                        ROW_NUMBER() OVER (
                            PARTITION BY c.commodity_id, c.expiration_year 
                            ORDER BY c.expiration_date
                        ) as contract_rank
                    FROM futures_prices.contracts c
                    JOIN futures_prices.commodities com ON c.commodity_id = com.id
                    WHERE com.code = %s
            """
            params = [commodity.upper()]
            
            if start_year:
                query += " AND c.expiration_year >= %s"
                params.append(start_year)
            
            if end_year:
                query += " AND c.expiration_year <= %s"
                params.append(end_year)
            
            query += """
                ),
                monthly_samples AS (
                    SELECT 
                        EXTRACT(MONTH FROM p.trade_date)::integer as trade_month,
                        EXTRACT(YEAR FROM p.trade_date)::integer as trade_year,
                        p.trade_date,
                        p.settlement_price,
                        CASE 
                            WHEN ABS(EXTRACT(DAY FROM p.trade_date) - 15) <= 3 
                                AND EXTRACT(DAY FROM p.trade_date) <= 18
                            THEN 'mid'
                            ELSE 'end'
                        END as position,
                        CASE 
                            WHEN ABS(EXTRACT(DAY FROM p.trade_date) - 15) <= 3 
                                AND EXTRACT(DAY FROM p.trade_date) <= 18
                            THEN ROW_NUMBER() OVER (
                                PARTITION BY EXTRACT(YEAR FROM p.trade_date), EXTRACT(MONTH FROM p.trade_date)
                                ORDER BY ABS(EXTRACT(DAY FROM p.trade_date) - 15)
                            )
                            ELSE ROW_NUMBER() OVER (
                                PARTITION BY EXTRACT(YEAR FROM p.trade_date), EXTRACT(MONTH FROM p.trade_date)
                                ORDER BY p.trade_date DESC
                            )
                        END as rn
                    FROM futures_prices.prices p
                    JOIN ranked_contracts rc ON p.contract_id = rc.id
                    WHERE rc.contract_rank = %s
                        AND p.settlement_price IS NOT NULL
            """
            params.append(month_offset)
            
            # Filter by trade date year (not expiration year) for data points
            if start_year:
                query += " AND EXTRACT(YEAR FROM p.trade_date) >= %s"
                params.append(start_year)
            
            if end_year:
                query += " AND EXTRACT(YEAR FROM p.trade_date) <= %s"
                params.append(end_year)
            
            query += """
                )
                SELECT 
                    trade_year as year,
                    trade_month as month,
                    position,
                    trade_date,
                    settlement_price
                FROM monthly_samples
                WHERE rn = 1
                ORDER BY trade_date
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    def _get_weekly_data_points(
        self,
        commodity: str,
        month_offset: int,
        start_year: Optional[int],
        end_year: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Get weekly sampled data points (52/year - consistent day of week, prefer Friday)."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                WITH ranked_contracts AS (
                    SELECT 
                        c.id,
                        c.expiration_year,
                        c.expiration_month,
                        ROW_NUMBER() OVER (
                            PARTITION BY c.commodity_id, c.expiration_year 
                            ORDER BY c.expiration_date
                        ) as contract_rank
                    FROM futures_prices.contracts c
                    JOIN futures_prices.commodities com ON c.commodity_id = com.id
                    WHERE com.code = %s
            """
            params = [commodity.upper()]
            
            if start_year:
                query += " AND c.expiration_year >= %s"
                params.append(start_year)
            
            if end_year:
                query += " AND c.expiration_year <= %s"
                params.append(end_year)
            
            query += """
                ),
                weekly_samples AS (
                    SELECT 
                        EXTRACT(MONTH FROM p.trade_date)::integer as trade_month,
                        EXTRACT(YEAR FROM p.trade_date)::integer as trade_year,
                        EXTRACT(WEEK FROM p.trade_date)::integer as week_number,
                        p.trade_date,
                        p.settlement_price,
                        ROW_NUMBER() OVER (
                            PARTITION BY EXTRACT(YEAR FROM p.trade_date), EXTRACT(MONTH FROM p.trade_date), EXTRACT(WEEK FROM p.trade_date)
                            ORDER BY CASE WHEN EXTRACT(DOW FROM p.trade_date) = 5 THEN 0 ELSE 1 END,
                                     p.trade_date DESC
                        ) as rn
                    FROM futures_prices.prices p
                    JOIN ranked_contracts rc ON p.contract_id = rc.id
                    WHERE rc.contract_rank = %s
                        AND p.settlement_price IS NOT NULL
            """
            params.append(month_offset)
            
            # Filter by trade date year (not expiration year) for data points
            if start_year:
                query += " AND EXTRACT(YEAR FROM p.trade_date) >= %s"
                params.append(start_year)
            
            if end_year:
                query += " AND EXTRACT(YEAR FROM p.trade_date) <= %s"
                params.append(end_year)
            
            query += """
                )
                SELECT 
                    trade_year as year,
                    trade_month as month,
                    week_number,
                    trade_date,
                    settlement_price
                FROM weekly_samples
                WHERE rn = 1
                ORDER BY trade_date
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


# Global database instance
_db_instance: Optional[Database] = None


def get_db() -> Database:
    """Get or create database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance

