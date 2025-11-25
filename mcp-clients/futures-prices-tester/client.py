#!/usr/bin/env python3
"""
MCP Client for testing Futures Prices MCP Server.

This client connects to the MCP server and tests all available tools.
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MCPClient:
    """Client for interacting with MCP server."""
    
    def __init__(self, server_url: Optional[str] = None, bearer_token: Optional[str] = None):
        """
        Initialize MCP client.
        
        Args:
            server_url: MCP server URL (defaults to MCP_SERVER_URL env var)
            bearer_token: Bearer token for authentication (optional)
        """
        self.server_url = server_url or os.getenv('MCP_SERVER_URL', 'http://localhost:5222/mcp')
        self.bearer_token = bearer_token or os.getenv('MCP_BEARER_TOKEN')
        self.session = requests.Session()
        
        if self.bearer_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.bearer_token}'
            })
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools from the MCP server."""
        # Note: Actual MCP protocol may differ - this is a simplified version
        # In production, you'd use the actual MCP SDK client
        response = self.session.post(
            f"{self.server_url}/tools/list",
            json={}
        )
        response.raise_for_status()
        return response.json()
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool response
        """
        # Note: Actual MCP protocol may differ - this is a simplified version
        response = self.session.post(
            f"{self.server_url}/tools/call",
            json={
                "name": tool_name,
                "arguments": arguments
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_front_month_price(self, commodity: str, date: str) -> Dict[str, Any]:
        """Call get_front_month_price tool."""
        return self.call_tool("get_front_month_price_tool", {
            "commodity": commodity,
            "date": date
        })
    
    def get_front_month_prices(self, commodity: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Call get_front_month_prices tool."""
        return self.call_tool("get_front_month_prices_tool", {
            "commodity": commodity,
            "start_date": start_date,
            "end_date": end_date
        })
    
    def calculate_price_change(self, commodity: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Call calculate_price_change tool."""
        return self.call_tool("calculate_price_change_tool", {
            "commodity": commodity,
            "start_date": start_date,
            "end_date": end_date
        })
    
    def get_seasonal_data(self, commodity: str, contract_month_offset: int) -> Dict[str, Any]:
        """Call get_seasonal_data tool."""
        return self.call_tool("get_seasonal_data_tool", {
            "commodity": commodity,
            "contract_month_offset": contract_month_offset
        })


def main():
    """Test the MCP client."""
    print("MCP Client for Futures Prices Server")
    print("=" * 60)
    
    client = MCPClient()
    
    # Test connection
    print("\n1. Testing server connection...")
    try:
        # This is a placeholder - actual MCP protocol may differ
        print(f"   Server URL: {client.server_url}")
        print("   ✓ Client initialized")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        return
    
    print("\nNote: This is a basic client structure.")
    print("For full MCP protocol support, use the MCP Inspector or North MCP SDK client.")


if __name__ == '__main__':
    main()

