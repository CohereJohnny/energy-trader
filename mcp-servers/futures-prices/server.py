#!/usr/bin/env python3
"""
Futures Prices MCP Server

MCP server for querying historical and current futures prices.
"""

import os
import sys
import argparse
from dotenv import load_dotenv
try:
    from north_mcp_python_sdk import NorthMCPServer
except ImportError:
    print("Error: north-mcp-python-sdk not installed. Install with:")
    print("  pip install git+ssh://git@github.com/cohere-ai/north-mcp-python-sdk.git")
    sys.exit(1)
from tools import (
    get_front_month_price,
    get_front_month_prices,
    calculate_price_change,
    get_seasonal_data
)

# Load environment variables
load_dotenv()


def create_server(port: int = 5222, host: str = '127.0.0.1', debug: bool = False):
    """Create and configure MCP server."""
    
    # Get server secret from environment (optional)
    server_secret = os.getenv('MCP_SERVER_SECRET', None)
    
    # Create server
    mcp = NorthMCPServer(
        name="Futures Prices",
        port=port,
        host=host,
        server_secret=server_secret,
        debug=debug
    )
    
    # Register tools
    @mcp.tool()
    def get_front_month_price_tool(commodity: str, date: str) -> dict:
        """
        Get the front month settlement price for a commodity on a specific date.
        
        Args:
            commodity: Commodity code (BRENT, WTI, GO, RBOB)
            date: Date in YYYY-MM-DD format (e.g., "2025-01-03")
            
        Returns:
            Front month price with citation metadata
        """
        return get_front_month_price(commodity, date)
    
    @mcp.tool()
    def get_front_month_prices_tool(commodity: str, start_date: str, end_date: str) -> dict:
        """
        Get front month prices for a commodity over a date range.
        
        Args:
            commodity: Commodity code (BRENT, WTI, GO, RBOB)
            start_date: Start date in YYYY-MM-DD format (e.g., "2025-01-03")
            end_date: End date in YYYY-MM-DD format (e.g., "2025-03-31")
            
        Returns:
            Front month prices with citation metadata
        """
        return get_front_month_prices(commodity, start_date, end_date)
    
    @mcp.tool()
    def calculate_price_change_tool(commodity: str, start_date: str, end_date: str) -> dict:
        """
        Calculate the price change between two dates.
        
        Args:
            commodity: Commodity code (BRENT, WTI, GO, RBOB)
            start_date: Start date in YYYY-MM-DD format (e.g., "2025-01-03")
            end_date: End date in YYYY-MM-DD format (e.g., "2025-03-31")
            
        Returns:
            Price change calculation with citation metadata
        """
        return calculate_price_change(commodity, start_date, end_date)
    
    @mcp.tool()
    def get_seasonal_data_tool(
        commodity: str,
        contract_month_offset: int,
        start_year: int = None,
        end_year: int = None,
        points_per_year: int = 12,
        format: str = "aggregated"
    ) -> dict:
        """
        Get seasonal data for a specific contract month offset with configurable sampling frequency.

        Args:
            commodity: Commodity code (BRENT, WTI, GO, RBOB)
            contract_month_offset: Month offset (1=M1, 2=M2, etc.)
            start_year: Optional start year filter (by expiration year)
            end_year: Optional end year filter (by expiration year)
            points_per_year: Sampling frequency (12=monthly default, 24=bi-monthly, 52=weekly)
            format: Output format ("aggregated" default, "data-points" for sampled points, "raw" for all daily prices)

        Returns:
            Seasonal data with aggregated statistics, sampled data points, or raw prices, with citation metadata
        """
        return get_seasonal_data(
            commodity, contract_month_offset, start_year, end_year, points_per_year, format
        )
    
    return mcp


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Futures Prices MCP Server')
    parser.add_argument(
        '--transport',
        choices=['streamable-http', 'stdio'],
        default='streamable-http',
        help='Transport type (default: streamable-http)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5222,
        help='Port for streamable-http transport (default: 5222)'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Server host (default: 127.0.0.1, use 0.0.0.0 for all interfaces)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    # Create server
    server = create_server(port=args.port, host=args.host, debug=args.debug)
    
    # Start server
    if args.transport == 'streamable-http':
        print(f"Starting Futures Prices MCP Server on {args.host}:{args.port}...")
        print(f"Server endpoint: http://{args.host}:{args.port}/mcp")
        server.run(transport='streamable-http')
    else:
        print("Starting Futures Prices MCP Server (stdio transport)...")
        server.run(transport='stdio')


if __name__ == '__main__':
    main()

