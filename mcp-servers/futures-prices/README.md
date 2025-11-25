# Futures Prices MCP Server

MCP server for querying historical and current futures prices for energy commodities (BRENT, WTI, GASOIL, RBOB).

## Overview

This MCP server provides tools for:
- Getting front month prices for specific dates
- Getting front month prices for date ranges
- Calculating price changes between dates
- Retrieving seasonal data for charting

## Setup

### Prerequisites

- Python 3.11+
- `uv` package manager (recommended) or `pip`
- PostgreSQL database (containerized via Docker Compose)
- North MCP Python SDK

### Installation with uv (Recommended)

```bash
# Navigate to MCP server directory
cd mcp-servers/futures-prices

# Create virtual environment and install dependencies
uv sync

# Install North MCP SDK from GitHub
uv pip install git+ssh://git@github.com/cohere-ai/north-mcp-python-sdk.git

# Activate virtual environment (if needed)
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

### Installation with pip (Alternative)

```bash
# Navigate to MCP server directory
cd mcp-servers/futures-prices

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Quick Setup

Run the setup script:
```bash
./setup.sh
```

This will:
- Create a virtual environment (using `uv` if available, otherwise `pip`)
- Install all dependencies
- Install North MCP Python SDK

### Configuration

Set environment variables:
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=energy_trader
export DB_USER=postgres
export DB_PASSWORD=postgres
```

Or create `.env` file in the `mcp-servers/futures-prices/` directory:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_trader
DB_USER=postgres
DB_PASSWORD=postgres
```

### Running the Server

```bash
python server.py
```

Or with transport specification:
```bash
python server.py --transport streamable-http
```

## Available Tools

### get_front_month_price
Get the front month settlement price for a commodity on a specific date.

**Parameters:**
- `commodity` (string): Commodity code (BRENT, WTI, GO, RBOB)
- `date` (string): Date in YYYY-MM-DD format

**Example:**
```json
{
  "commodity": "BRENT",
  "date": "2025-01-03"
}
```

### get_front_month_prices
Get front month prices for a commodity over a date range.

**Parameters:**
- `commodity` (string): Commodity code (BRENT, WTI, GO, RBOB)
- `start_date` (string): Start date in YYYY-MM-DD format
- `end_date` (string): End date in YYYY-MM-DD format

### calculate_price_change
Calculate the price change between two dates.

**Parameters:**
- `commodity` (string): Commodity code (BRENT, WTI, GO, RBOB)
- `start_date` (string): Start date in YYYY-MM-DD format
- `end_date` (string): End date in YYYY-MM-DD format

### get_seasonal_data
Get seasonal data for a specific contract month (e.g., M2 GOBRs).

**Parameters:**
- `commodity` (string): Commodity code (BRENT, WTI, GO, RBOB)
- `contract_month_offset` (integer): Month offset (1=M1, 2=M2, etc.)

## Citation Metadata

All tool responses include `_north_metadata` fields for proper citation display in the North UI:

```json
{
  "text": "Result content",
  "_north_metadata": {
    "title": "Front Month Brent Price",
    "url": "https://example.com/source",
    "author_name": "Energy Trader Database",
    "last_updated": "2025-01-20T12:00:00Z"
  }
}
```

## Development

### Project Structure

```
mcp-servers/futures-prices/
├── server.py              # Main server entry point
├── db.py                  # Database connection and queries
├── tools.py               # MCP tool implementations
├── citations.py           # Citation metadata helpers
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Testing

See Sprint 3 for MCP client testing.

