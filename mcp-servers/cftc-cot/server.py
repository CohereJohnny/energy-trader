#!/usr/bin/env python3
"""
CFTC COT MCP Server

MCP server for querying CFTC Commitment of Traders (COT) data.
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
    get_cot_data,
    analyze_positioning_trends,
    compare_positioning,
    get_positioning_extremes,
    get_loaded_data_status
)

# Load environment variables
load_dotenv()


def create_server(port: int = 5223, host: str = '127.0.0.1', debug: bool = False):
    """Create and configure MCP server."""
    
    # Get server secret from environment (optional)
    # Treat empty string as None to disable authentication
    server_secret = os.getenv('MCP_SERVER_SECRET', None)
    if server_secret == '':
        server_secret = None
    
    # Create server
    mcp = NorthMCPServer(
        name="CFTC COT",
        port=port,
        host=host,
        server_secret=server_secret,
        debug=debug
    )
    
    # Register tools
    @mcp.tool()
    def get_cot_data_tool(
        commodity: str = None,
        report_date: str = None,
        trader_category: str = None,
        position_type: str = 'all'
    ) -> dict:
        """
        Get CFTC Commitment of Traders (COT) data.
        
        Args:
            commodity: Commodity group (Petroleum and Products, Natural Gas and Products, Electricity)
            report_date: Report date in YYYY-MM-DD format (if None, returns latest)
            trader_category: Trader category (PRODUCER, SWAP, MANAGED_MONEY, OTHER_REPORTABLE, NONREPORTABLE)
            position_type: Position type ('all' for Futures+Options, 'old' for Futures only, 'other' for Options only)
        """
        return get_cot_data(
            commodity=commodity,
            report_date=report_date,
            trader_category=trader_category,
            position_type=position_type
        )
    
    @mcp.tool()
    def analyze_positioning_trends_tool(
        commodity: str,
        start_date: str,
        end_date: str,
        trader_category: str
    ) -> dict:
        """
        Analyze positioning trends for a commodity and trader category over time.
        
        Args:
            commodity: Commodity group (Petroleum and Products, Natural Gas and Products, Electricity)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            trader_category: Trader category (PRODUCER, SWAP, MANAGED_MONEY, OTHER_REPORTABLE, NONREPORTABLE)
        """
        return analyze_positioning_trends(
            commodity=commodity,
            start_date=start_date,
            end_date=end_date,
            trader_category=trader_category
        )
    
    @mcp.tool()
    def compare_positioning_tool(
        commodities: str,
        report_date: str,
        trader_category: str
    ) -> dict:
        """
        Compare positioning across multiple commodities on a given date.
        
        Args:
            commodities: Comma-separated list of commodity groups
            report_date: Report date in YYYY-MM-DD format
            trader_category: Trader category (PRODUCER, SWAP, MANAGED_MONEY, OTHER_REPORTABLE, NONREPORTABLE)
        """
        return compare_positioning(
            commodities=commodities,
            report_date=report_date,
            trader_category=trader_category
        )
    
    @mcp.tool()
    def get_positioning_extremes_tool(
        commodity: str,
        trader_category: str,
        lookback_days: int = 365,
        metric: str = 'long'
    ) -> dict:
        """
        Get positioning extremes for a commodity and trader category.
        
        Args:
            commodity: Commodity group (Petroleum and Products, Natural Gas and Products, Electricity)
            trader_category: Trader category (PRODUCER, SWAP, MANAGED_MONEY, OTHER_REPORTABLE, NONREPORTABLE)
            lookback_days: Number of days to look back (default: 365)
            metric: Metric to find extremes for ('long', 'short', 'net', 'pct_long', 'pct_short')
        """
        return get_positioning_extremes(
            commodity=commodity,
            trader_category=trader_category,
            lookback_days=lookback_days,
            metric=metric
        )
    
    @mcp.tool()
    def get_loaded_data_status_tool(
        commodity: str = None,
        start_date: str = None,
        end_date: str = None,
        status: str = None,
        identify_gaps: bool = False
    ) -> dict:
        """
        Get status of loaded CFTC COT data.
        
        Args:
            commodity: Commodity group filter (optional)
            start_date: Start date filter in YYYY-MM-DD format (optional)
            end_date: End date filter in YYYY-MM-DD format (optional)
            status: Loading status filter ('pending', 'downloading', 'parsing', 'loading', 'completed', 'failed') (optional)
            identify_gaps: Whether to identify missing reports (default: False)
        """
        return get_loaded_data_status(
            commodity=commodity,
            start_date=start_date,
            end_date=end_date,
            status=status,
            identify_gaps=identify_gaps
        )
    
    return mcp


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='CFTC COT MCP Server')
    parser.add_argument(
        '--transport',
        choices=['streamable-http', 'stdio'],
        default='streamable-http',
        help='Transport type (default: streamable-http)'
    )
    parser.add_argument('--port', type=int, default=5223, help='Server port (default: 5223)')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Server host (default: 127.0.0.1, use 0.0.0.0 for all interfaces)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Create server
    server = create_server(port=args.port, host=args.host, debug=args.debug)
    
    # Start server
    if args.transport == 'streamable-http':
        print(f"Starting CFTC COT MCP Server on {args.host}:{args.port}...")
        print(f"Server endpoint: http://{args.host}:{args.port}/mcp")
        server.run(transport='streamable-http')
    else:
        print("Starting CFTC COT MCP Server (stdio transport)...")
        server.run(transport='stdio')


if __name__ == '__main__':
    main()

