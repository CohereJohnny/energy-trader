# Scripts Directory

Utility scripts for data processing and database operations.

## Database Management Scripts

### setup_db.sh
Start the containerized PostgreSQL database.

```bash
./scripts/setup_db.sh
```

This script will:
- Create `.env` file if it doesn't exist
- Start PostgreSQL container
- Wait for database to be ready
- Verify connection

### stop_db.sh
Stop the PostgreSQL container.

```bash
./scripts/stop_db.sh
```

### reset_db.sh
Remove the PostgreSQL container and all data volumes (WARNING: deletes all data).

```bash
./scripts/reset_db.sh
```

## month_code_parser.py

CME Group month code parser for futures contracts.

**Usage:**
```bash
python scripts/month_code_parser.py
```

**Functions:**
- `parse_contract_name(contract_name)` - Parse contract name like 'BRENT_2011F'
- `get_cme_code(month)` - Get CME code for month number (1-12)
- `get_month_number(cme_code)` - Get month number for CME code

**Example:**
```python
from scripts.month_code_parser import parse_contract_name

result = parse_contract_name('BRENT_2011F')
# Returns: {'commodity': 'BRENT', 'year': 2011, 'month': 1, 'cme_code': 'F'}
```

## load_futures_data.py

Loads CSV files containing futures prices into PostgreSQL database.

**Usage:**
```bash
# Set environment variables (optional)
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=energy_trader
export DB_USER=postgres
export DB_PASSWORD=postgres

# Run loader
python scripts/load_futures_data.py
```

**Features:**
- Parses contract names from CSV column headers
- Handles CME Group month codes
- Normalizes data into commodities, contracts, and prices tables
- Handles missing/null prices gracefully
- Batch inserts for performance
- Uses ON CONFLICT for idempotent loading

**Requirements:**
- Database migration must be run first
- CSV files must be in `data/` directory
- psycopg2-binary Python package

