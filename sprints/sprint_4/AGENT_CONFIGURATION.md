# AI Agent Configuration Guide

## Overview
This guide walks through configuring a North AI Agent to use the Futures Prices MCP Server.

## Prerequisites

1. **MCP Server Running**: The futures prices MCP server must be running
   ```bash
   cd mcp-servers/futures-prices
   uv run python server.py --transport streamable-http --port 5222
   ```

2. **Database Running**: PostgreSQL database must be running
   ```bash
   docker compose up -d
   # or
   ./scripts/setup_db.sh
   ```

3. **North Platform Access**: Access to North platform for creating/configuring agents

## Configuration Steps

### Step 1: Start the MCP Server

Ensure the MCP server is running and accessible:

```bash
cd mcp-servers/futures-prices
uv run python server.py --transport streamable-http --port 5222
```

The server should display:
```
Starting Futures Prices MCP Server on port 5222...
Server endpoint: http://localhost:5222/mcp
```

### Step 2: Configure MCP Server Connection in North

1. **Navigate to Agent Configuration** in North platform
2. **Add MCP Server**:
   - **Name**: "Futures Prices"
   - **Transport Type**: StreamableHTTP
   - **URL**: `http://localhost:5222/mcp` (or your server URL)
   - **Authentication**: Bearer token (if `MCP_SERVER_SECRET` is set in `.env`)

### Step 3: Add Agent Instructions

1. **Copy agent instructions** from `specs/agent-instructions.md`
2. **Paste into "Custom agent instructions"** field in North platform
3. **Save configuration**

### Step 4: Verify Tool Discovery

1. **Check available tools** in the agent configuration
2. **Verify these 4 tools are available**:
   - `get_front_month_price_tool`
   - `get_front_month_prices_tool`
   - `calculate_price_change_tool`
   - `get_seasonal_data_tool`

### Step 5: Test Basic Tool Invocation

Test that the agent can call tools:

**Test Query**: "What was the front month Brent price on 2025-01-03?"

**Expected Behavior**:
- Agent should call `get_front_month_price_tool` with `commodity="BRENT"` and `date="2025-01-03"`
- Agent should return price with citation metadata
- Citation should appear in the response

## Environment Variables

Ensure these are set in `mcp-servers/futures-prices/.env`:

```bash
# Database connection
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_trader
DB_USER=energy_trader
DB_PASSWORD=your_password

# MCP Server (optional)
MCP_SERVER_SECRET=your_secret_token  # If using authentication
```

## Troubleshooting

### Agent Cannot Connect to MCP Server

1. **Check server is running**: `curl http://localhost:5222/mcp`
2. **Check firewall/network**: Ensure port 5222 is accessible
3. **Check authentication**: If using bearer token, verify it matches

### Tools Not Appearing

1. **Check server logs** for errors
2. **Verify database connection** is working
3. **Check tool registration** in `server.py`

### Tool Calls Failing

1. **Check database is running**: `docker compose ps`
2. **Verify data is loaded**: Query database directly
3. **Check server logs** for error messages

## Next Steps

After configuration is complete, proceed with:
- **Task 3**: End-to-End Query Testing
- **Task 4**: Citation Metadata Validation
- **Task 5**: Error Handling & Edge Cases

