# Futures Prices MCP Client Tester

MCP client and test suite for end-to-end testing of the Futures Prices MCP Server.

## Overview

This directory contains:
- Test suite for validating all MCP tools
- MCP Inspector configuration for interactive testing
- Performance and error handling tests
- End-to-end scenario tests

## Setup

### Prerequisites

- Python 3.11+
- `uv` package manager (recommended) or `pip`
- MCP server running (see `mcp-servers/futures-prices/`)

### Installation

```bash
cd mcp-clients/futures-prices-tester

# Using uv (recommended)
uv sync

# Or using pip
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running Tests

### Direct Tool Testing (Bypasses MCP Protocol)

This tests the tool functions directly:

```bash
uv run python test_suite.py
```

This will test:
- All 4 commodities (BRENT, WTI, GO, RBOB)
- All 4 MCP tools
- Edge cases and error handling
- Citation metadata format
- Performance benchmarks
- End-to-end scenarios

### Using MCP Inspector (Interactive Testing)

The MCP Inspector provides a visual interface for testing MCP servers.

#### Setup

1. Install MCP Inspector:
```bash
npx @modelcontextprotocol/inspector
```

2. Start the MCP server in another terminal:
```bash
cd ../../mcp-servers/futures-prices
uv run python server.py --port 5222
```

3. Configure MCP Inspector:
   - Transport Type: **Streamable HTTP**
   - URL: `http://localhost:5222/mcp`
   - Authentication: Bearer token (if server requires it)

4. Connect and test tools interactively

#### Testing with MCP Inspector

1. **List Tools**: Click "List Tools" to see all available tools
2. **Test get_front_month_price**:
   - Tool: `get_front_month_price_tool`
   - Arguments: `{"commodity": "BRENT", "date": "2025-01-03"}`
3. **Test get_front_month_prices**:
   - Tool: `get_front_month_prices_tool`
   - Arguments: `{"commodity": "BRENT", "start_date": "2025-01-03", "end_date": "2025-03-31"}`
4. **Test calculate_price_change**:
   - Tool: `calculate_price_change_tool`
   - Arguments: `{"commodity": "BRENT", "start_date": "2025-01-03", "end_date": "2025-03-31"}`
5. **Test get_seasonal_data**:
   - Tool: `get_seasonal_data_tool`
   - Arguments: `{"commodity": "GO", "contract_month_offset": 2}`

## Test Scenarios

### Scenario 1: Price Change Query
**Query**: "What was the change in front month Brent price between January 3rd 2025 and March 31st 2025?"

**Tool Call**:
```json
{
  "name": "calculate_price_change_tool",
  "arguments": {
    "commodity": "BRENT",
    "start_date": "2025-01-03",
    "end_date": "2025-03-31"
  }
}
```

### Scenario 2: Yesterday's Settlement
**Query**: "What was the front month Brent Settlement yesterday?"

**Tool Call**:
```json
{
  "name": "get_front_month_price_tool",
  "arguments": {
    "commodity": "BRENT",
    "date": "2025-11-19"  // Replace with actual yesterday's date
  }
}
```

### Scenario 3: Seasonal Chart
**Query**: "Display a seasonal chart of M2 GOBRs"

**Tool Call**:
```json
{
  "name": "get_seasonal_data_tool",
  "arguments": {
    "commodity": "GO",
    "contract_month_offset": 2
  }
}
```

## Expected Results

### Citation Metadata Format

All tool responses should include:
```json
{
  "text": "...",
  "_north_metadata": {
    "title": "...",
    "url": "...",
    "author_name": "Energy Trader Database",
    "last_updated": "2025-11-20T..."
  }
}
```

### Performance Targets

- Single date query: < 100ms
- Date range query (1 month): < 500ms
- Date range query (1 year): < 2000ms

## Troubleshooting

### Server Not Running
- Ensure MCP server is running: `cd ../../mcp-servers/futures-prices && uv run python server.py`
- Check server logs for errors

### Connection Errors
- Verify server URL: `http://localhost:5222/mcp`
- Check firewall settings
- Verify database is running: `docker compose ps`

### Authentication Errors
- Check if server requires authentication
- Verify bearer token in `.env` file

